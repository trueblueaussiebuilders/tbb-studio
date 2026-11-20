"""Automatic layout check for videos: catches the problems that used to need a manual look at PNGs.

  python tools/check.py videos/014-curtain-wall            # one or more video folders
  python tools/check.py --queue                            # every queued video not yet posted
  python tools/check.py --queue --out /tmp/check           # also save annotated PNGs of each problem
  python tools/check.py videos/014-curtain-wall --voice    # exact timings from the real voice (slow)

It renders frames across the whole video (and the cover) with the engine instrumented, and reports:
  ERROR  label/text plates that overlap each other, or a line (e.g. another label's leader) drawn over a label
         (for 0.5s or more, so brief cross-fades don't count)
  ERROR  text running off the left/right edge, or key text in the bottom 20% (the Reels caption/UI area)
  ERROR  the 3D model running off the frame, into the header, or into the bottom 20%
  WARN   the 3D model drawn small (hard to read on a phone), or covering on-screen text
  WARN   hook scene longer than 4.5s, video longer than 75s
Exit code 1 if there is any ERROR, so it can gate a commit or a workflow.

Timings: uses <slug>.timings.json from --timings (default: build/ and out/) if present, otherwise --voice, otherwise
an estimate from the narration word counts (good to ~0.5s per scene; fine for layout).
"""
import argparse, importlib.util, json, math, os, re, sys
from multiprocessing import get_context

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import cairo
from engine import blueprint as bp
from engine import three_d as td

SAFE_X0, SAFE_X1 = 60, 1000          # text must stay inside these (frame border at 40/1040; Reels buttons on the right)
BOTTOM = int(bp.H * 0.8)             # 1536: bottom 20% is covered by the caption and Reels UI
HEADER = 330                         # header band (series, title, subtitle, rule)
TITLE_BLOCK = 1630                   # decorative title block at the bottom (allowed under the UI)
HOOK_MAX, DUR_MAX = 4.5, 75.0
MIN_3D = 380                         # px: the model's larger side should be at least this when fully shown
VIS = 0.35                           # alpha above which text counts as visible


# ---------------------------------------------------------------- instrumentation
class Rec:
    def __init__(self, s, box, alpha, kind="text"):
        self.s, self.box, self.alpha, self.kind = s, box, alpha, kind


class Probe:
    """Wraps a cairo.Context: forwards everything, tracks group alpha so faded labels count as faded,
    and notices full-frame overlays (the end card) that hide what's underneath."""
    def __init__(self, ctx, frame):
        object.__setattr__(self, "_c", ctx)
        object.__setattr__(self, "_frame", frame)
        object.__setattr__(self, "_stack", [])
        object.__setattr__(self, "_pending", None)
        object.__setattr__(self, "_rgba", None)

    def __getattr__(self, k): return getattr(self._c, k)
    def __setattr__(self, k, v): setattr(self._c, k, v)

    def _sink(self): return self._stack[-1] if self._stack else self._frame

    def push_group(self, *a):
        self._stack.append([]); return self._c.push_group(*a)

    def pop_group_to_source(self):
        object.__setattr__(self, "_pending", self._stack.pop() if self._stack else [])
        return self._c.pop_group_to_source()

    def set_source_rgba(self, *a):
        object.__setattr__(self, "_rgba", a)
        return self._c.set_source_rgba(*a)

    def set_source_surface(self, *a):
        object.__setattr__(self, "_rgba", None); return self._c.set_source_surface(*a)

    def paint_with_alpha(self, a):
        if self._pending is not None:
            for r in self._pending: r.alpha *= a
            self._sink().extend(self._pending); object.__setattr__(self, "_pending", None)
        return self._c.paint_with_alpha(a)

    def paint(self):
        if self._pending is not None:
            self._sink().extend(self._pending); object.__setattr__(self, "_pending", None)
        elif self._rgba and len(self._rgba) == 4 and not self._stack:
            for r in self._frame: r.alpha *= 1 - self._rgba[3]          # full-frame overlay hides what's below
        return self._c.paint()


_REC = {"on": False, "seq": 0}
_text, _render, _polyline = bp.text, td.render, bp.polyline


def _polyline_probe(ctx, pts, p, col, width=3.0, alpha=1.0, dash=None):
    _polyline(ctx, pts, p, col, width, alpha, dash)
    if not (_REC["on"] and isinstance(ctx, Probe)) or p <= 0 or alpha <= 0.01: return
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    target, acc, drawn = sum(segs) * min(p, 1.0), 0.0, [pts[0]]
    for i, L in enumerate(segs):                       # same partial-draw rule as blueprint.polyline
        if acc + L >= target:
            k = (target - acc) / L if L else 1
            drawn.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k))
            break
        drawn.append(pts[i + 1]); acc += L
    dev = [ctx.user_to_device(*q) for q in drawn]
    r = Rec("line", None, alpha, "line"); r.pts = dev; r.seq = _seq()
    ctx._sink().append(r)


def _seq():
    _REC["seq"] += 1; return _REC["seq"]


def _text_probe(ctx, s, x, y, size, col, alpha=1.0, bold=False, anchor="l", spacing=0.0, chars=None):
    _text(ctx, s, x, y, size, col, alpha, bold, anchor, spacing, chars)
    if not (_REC["on"] and isinstance(ctx, Probe)): return
    shown = s[:chars] if chars is not None else s
    if not shown.strip() or alpha <= 0.01: return
    bp.font(ctx, size, bold)
    if spacing:
        total = sum(ctx.text_extents(c).x_advance + spacing for c in shown) - spacing
    else:
        total = ctx.text_extents(shown).x_advance
    if anchor == "c": x -= total / 2
    elif anchor == "r": x -= total
    pts = [ctx.user_to_device(px, py) for px, py in ((x, y - 0.74 * size), (x + total, y - 0.74 * size),
                                                     (x, y + 0.2 * size), (x + total, y + 0.2 * size))]
    box = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
    r = Rec(shown, box, alpha); r.seq = _seq()
    ctx._sink().append(r)


def _render_probe(ctx, parts, cam, alpha=1.0, highlight=None, appear=None, ghost=None):
    _render(ctx, parts, cam, alpha=alpha, highlight=highlight, appear=appear, ghost=ghost)
    if not (_REC["on"] and isinstance(ctx, Probe)) or alpha <= 0.01: return
    # silhouette mask: render the model alone onto a transparent layer
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, bp.W, bp.H)
    _render(cairo.Context(surf), parts, cam, alpha=1.0, highlight=highlight, appear=appear, ghost=ghost)
    import numpy as np
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(bp.H, surf.get_stride() // 4, 4)[:, :bp.W, 3]
    ys, xs = np.nonzero(a > 40)
    if len(xs) == 0: return
    r = Rec("3D MODEL", (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), alpha, "3d")
    r.mask = a > 60
    ctx._sink().append(r)


bp.text = _text_probe
bp.polyline = _polyline_probe
td.render = _render_probe
_Context = cairo.Context


class _CairoShim:
    """engine.blueprint calls cairo.Context(surface); hand it a Probe instead."""
    def __getattr__(self, k): return getattr(cairo, k)
    @staticmethod
    def Context(surface):
        return Probe(_Context(surface), _CURRENT)


_CURRENT = []
bp.cairo = _CairoShim()


# ---------------------------------------------------------------- timings
def load_spec(folder):
    s = importlib.util.spec_from_file_location("video_spec_" + os.path.basename(folder.rstrip("/")),
                                               os.path.join(folder, "spec.py"))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)     # specs pick up the probed text()
    return m


def estimate(narr):
    """Rough voice timing from word counts (Kokoro am_puck at 0.95 speaks ~3.8 words/s)."""
    from engine import voice
    cfg = voice._cfg()
    sgap = cfg.get("sentence_gap", 0.4)
    gap = (cfg.get(voice.engine_name(), {}) or {}).get("line_gap", 0.3) if isinstance(cfg.get(voice.engine_name()), dict) else 0.3

    def speech(line, sg):
        sents = [x for x in re.split(r"(?<=[.!?])\s+", line.strip()) if x]
        return len(line.split()) / 3.8 + sg * (len(sents) - 1)
    return {"hook": round(max(2.8, voice.LEAD + speech(narr["hook"], voice.HOOK_SENTENCE_GAP) + min(gap, voice.HOOK_LINE_GAP)), 2),
            "steps": [round(max(3.0, voice.LEAD + speech(s, sgap) + gap), 2) for s in narr["steps"]],
            "result": round(max(3.2, voice.LEAD + speech(narr["result"], sgap) + 0.9), 2),
            "end": round(max(2.8, voice.LEAD + speech(narr["end"], sgap) + 0.8), 2)}


def timings(folder, spec, dirs, use_voice):
    slug = os.path.basename(folder.rstrip("/"))
    for d in dirs:
        p = os.path.join(d, f"{slug}.timings.json")
        if os.path.exists(p) and os.path.getmtime(p) >= os.path.getmtime(os.path.join(folder, "spec.py")):
            return json.load(open(p)), "timings file " + p
    if use_voice:
        from engine import voice
        return voice.narrate(spec.NARRATION)[0], "voice"
    return estimate(spec.NARRATION), "estimate"


# ---------------------------------------------------------------- per-frame checks
def _chrome(r, M):
    cy = (r.box[1] + r.box[3]) / 2
    return cy < HEADER or cy > TITLE_BLOCK or r.s == M.get("footnote", "Typical only. Engineer's design governs.")


def _inter(a, b, pad=2):
    w = min(a[2], b[2]) - max(a[0], b[0]) - 2 * pad
    h = min(a[3], b[3]) - max(a[1], b[1]) - 2 * pad
    return w * h if w > 0 and h > 0 else 0


def frame_issues(recs, M, cover=False):
    out = []
    txt = [r for r in recs if r.kind == "text" and r.alpha >= VIS and not _chrome(r, M)]
    models = [r for r in recs if r.kind == "3d"]
    for i, a in enumerate(txt):
        x0, y0, x1, y1 = a.box
        if x1 > SAFE_X1 or x0 < SAFE_X0:
            out.append(("ERROR", "off-edge", f"'{a.s}' runs off the {'right' if x1 > SAFE_X1 else 'left'} edge "
                                             f"(x {x0:.0f}-{x1:.0f})", [a.box]))
        if y1 > BOTTOM and not cover:
            out.append(("ERROR", "bottom-20", f"'{a.s}' is in the bottom 20% (y {y1:.0f} > {BOTTOM})", [a.box]))
        for b in txt[i + 1:]:
            if a.s == b.s and a.box == b.box: continue
            if _inter(a.box, b.box) > 30:
                key = " / ".join(sorted((a.s, b.s)))
                out.append(("ERROR", "overlap", f"text overlaps: {key}", [a.box, b.box]))
    lines = [r for r in recs if r.kind == "line" and r.alpha >= VIS]
    for a in txt:                                      # linework drawn on top of a label strikes through it
        bx0, by0, bx1, by1 = a.box[0] + 3, a.box[1] + 4, a.box[2] - 3, a.box[3] - 3
        for ln in lines:
            if ln.seq < a.seq: continue
            hit = False
            for (x0, y0), (x1, y1) in zip(ln.pts, ln.pts[1:]):
                n = max(2, int(math.dist((x0, y0), (x1, y1)) / 3))
                if any(bx0 < x0 + (x1 - x0) * k / n < bx1 and by0 < y0 + (y1 - y0) * k / n < by1 for k in range(n + 1)):
                    hit = True; break
            if hit:
                out.append(("ERROR", "line-through-text", f"a line is drawn over '{a.s}'", [a.box]))
                break
    for m in models:
        x0, y0, x1, y1 = m.box
        if m.alpha < 0.5: continue
        lim_y1 = 1415 if cover else BOTTOM
        if x0 < 45 or x1 > bp.W - 45 or y0 < HEADER - 10 or y1 > lim_y1:
            out.append(("ERROR", "3d-clip", f"3D model outside the safe area (box {x0},{y0}-{x1},{y1}"
                                            f"{', hits the cover title strip' if cover and y1 > lim_y1 else ''})", [m.box]))
        if m.alpha > 0.9 and max(x1 - x0, y1 - y0) < MIN_3D:
            out.append(("WARN", "3d-small", f"3D model is small ({x1 - x0}x{y1 - y0}px)", [m.box]))
        for a in txt:
            ax0, ay0, ax1, ay1 = [int(v) for v in a.box]
            ax0, ay0 = max(ax0, 0), max(ay0, 0)
            sub = m.mask[ay0:max(ay1, ay0 + 1), ax0:max(ax1, ax0 + 1)]
            if sub.size and sub.mean() > 0.06:
                out.append(("WARN", "3d-over-text", f"3D model covers '{a.s}'", [a.box, m.box]))
    return out


_SPECS = {}


def _render_at(args):
    folder, tim, t = args
    spec = _SPECS.get(folder) or _SPECS.setdefault(folder, load_spec(folder))
    tl = bp.Timeline(tim)
    recs = []
    _CURRENT[:] = []
    globals()["_CURRENT"] = recs
    _REC["on"] = True
    if t is None:
        bp.draw_cover(spec, tl)
    else:
        bp.draw_frame(spec, tl, t)
    _REC["on"] = False
    return t, frame_issues(recs, spec.META, cover=t is None)


def _ranges(times, step):
    times = sorted(times); out = []
    for t in times:
        if out and t - out[-1][1] <= step * 1.01: out[-1][1] = t
        else: out.append([t, t])
    return out


def check(folder, a):
    spec = load_spec(folder)
    slug = os.path.basename(folder.rstrip("/"))
    tim, src = timings(folder, spec, a.timings, a.voice)
    tl = bp.Timeline(tim)
    ts = [round(k * a.step, 3) for k in range(int(tl.end0 / a.step) + 1)] + [None]       # skip the end card
    with get_context("fork").Pool(a.jobs) as pool:
        res = pool.map(_render_at, [(folder, tim, t) for t in ts])
    found = {}
    for t, iss in res:
        for sev, kind, msg, boxes in iss:
            f = found.setdefault((sev, kind, msg), {"times": [], "boxes": boxes})
            f["times"].append(-1 if t is None else t)
    issues = []
    for (sev, kind, msg), f in found.items():
        cov = -1 in f["times"]
        tt = [t for t in f["times"] if t >= 0]
        for r0, r1 in _ranges(tt, a.step):
            if kind in ("overlap", "3d-over-text", "line-through-text") and r1 - r0 < 0.5 - 1e-6: continue  # brief cross-fades are fine
            issues.append((sev, kind, msg, f"t={r0:.2f}-{r1:.2f}s" if r1 > r0 else f"t={r0:.2f}s", (r0 + r1) / 2, f["boxes"]))
        if cov: issues.append((sev, kind, msg, "cover", None, f["boxes"]))
    if tim["hook"] > HOOK_MAX:
        issues.append(("WARN", "hook-long", f"hook scene is {tim['hook']:.1f}s (target under {HOOK_MAX}s): trim the hook "
                       "narration to the punchline", "hook", None, []))
    if tl.duration > DUR_MAX:
        issues.append(("WARN", "long", f"video is {tl.duration:.1f}s (target under {DUR_MAX:.0f}s)", "", None, []))
    issues.sort(key=lambda x: (x[0] != "ERROR", x[4] if x[4] is not None else 1e9))
    errs = sum(1 for i in issues if i[0] == "ERROR")
    print(f"[{slug}] {len(issues)} issue(s), {errs} error(s)  (timings: {src}, {tl.duration:.1f}s, sampled every {a.step}s)")
    for sev, kind, msg, when, _, _ in issues:
        print(f"  {sev:5} {when:16} {msg}")
    if a.out and issues:
        os.makedirs(a.out, exist_ok=True)
        _CURRENT[:] = []
        for n, (sev, kind, msg, when, tmid, boxes) in enumerate(issues):
            if not boxes: continue
            _REC["on"] = False
            s = bp.draw_cover(spec, tl) if tmid is None else bp.draw_frame(spec, tl, tmid)
            c = _Context(s); c.set_source_rgba(1, 0.1, 0.1, 1); c.set_line_width(4)
            for b in boxes:
                c.rectangle(b[0] - 4, b[1] - 4, b[2] - b[0] + 8, b[3] - b[1] + 8); c.stroke()
            p = os.path.join(a.out, f"{slug}_issue{n + 1:02d}_{kind}.png"); s.write_to_png(p)
            print(f"        -> {p}")
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*")
    ap.add_argument("--queue", action="store_true", help="check every queued video not yet posted")
    ap.add_argument("--timings", nargs="*", default=["build", "out"], help="folders to look for <slug>.timings.json")
    ap.add_argument("--voice", action="store_true", help="synthesise the voice for exact timings (slow)")
    ap.add_argument("--step", type=float, default=0.25)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--out", help="save annotated PNGs of each problem here")
    a = ap.parse_args()
    folders = list(a.folders)
    if a.queue:
        read = lambda n: [l.strip() for l in open(os.path.join(ROOT, n)) if l.strip() and not l.startswith("#")] \
            if os.path.exists(os.path.join(ROOT, n)) else []
        posted = {l.split()[0] for l in read("posted.txt")}
        folders += [os.path.join(ROOT, "videos", s) for s in dict.fromkeys(read("queue.txt")) if s not in posted]
    if not folders: ap.error("give video folders or --queue")
    errs = sum(check(f, a) for f in folders)
    print("FAIL" if errs else "OK", f"({errs} error(s) across {len(folders)} video(s))")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
