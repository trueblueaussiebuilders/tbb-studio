"""True Blue Builds blueprint engine: drawing helpers + shared frame chrome.

A video spec module provides META, NARRATION, CAPTION and draw_section(ctx, t, tl).
Everything here is shared so each new video only defines its own section drawing.
"""
import math, os, random
import cairo

W, H, FPS = 1080, 1920, 30
# Dark-mode theme: white linework on near-black, electric blue brand accents, orange for "what's happening now"
BG = (0.035, 0.04, 0.05)
WHITE = (0.95, 0.96, 0.98)
BLUE = (0.25, 0.58, 1.0)
ORANGE = (1.0, 0.55, 0.12)
YEL = ORANGE                      # legacy name: active-step highlight
FONT = "DejaVu Sans Mono"
HANDLE = "@TRUEBLUEAUSSIEBUILDERS"
SERIES = "TRUE BLUE AUSSIE BUILDERS"

# Layout bands (keep key info out of the bottom ~20% and the right edge: Reels UI)
DRAW_TOP, DRAW_BOTTOM = 400, 1210   # section drawing area
PANEL_Y = 1298                      # step panel: number, title, then body text (was 1305)
BODY_SIZE, BODY_GAP = 36, 50        # step body text px / line pitch (was 32 / 46: about 11.5pt on a phone, now 13pt)
DRIFT = 0.045                       # slow camera on the 2D section: zooms in over odd steps, back out over even ones
DRIFT_FOCUS = (540, (DRAW_TOP + DRAW_BOTTOM) / 2)
DRIFT_CLIP = (54, 395, 1026, 1234)  # zoomed drawing stays inside the frame border, under the section label, above the ticks


# ---------------------------------------------------------------- maths
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def mix(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))
def prog(t, t0, d): return ease((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)


# ---------------------------------------------------------------- timeline
class Timeline:
    """Scene timing: hook, N steps, result, end card. Durations come from the voiceover."""
    def __init__(self, tim):
        self.tim = tim
        self.n = len(tim["steps"])
        self.hook = tim["hook"]
        self.res0 = self.step_start(self.n + 1)
        self.end0 = self.res0 + tim["result"]
        self.duration = self.end0 + tim["end"]
        self.scenes = [(0, self.hook)] + [(self.step_start(i), self.step_end(i)) for i in range(1, self.n + 1)] \
            + [(self.res0, self.end0), (self.end0, self.duration)]

    def step_start(self, i): return self.hook + sum(self.tim["steps"][:i - 1])   # i = 1..N+1
    def step_end(self, i): return self.step_start(i) + self.tim["steps"][i - 1]
    def s(self, i): return self.step_start(i)

    def col(self, step, t):
        """Newest step's linework glows yellow, then settles to white."""
        if step is None: return WHITE
        return mix(YEL, WHITE, clamp((t - self.step_end(step)) / 0.6))


# ---------------------------------------------------------------- drawing helpers
def font(ctx, size, bold=False):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def text(ctx, s, x, y, size, col, alpha=1.0, bold=False, anchor="l", spacing=0.0, chars=None):
    font(ctx, size, bold)
    if chars is not None: s = s[:chars]
    if spacing:
        widths = [ctx.text_extents(c).x_advance + spacing for c in s]
        total = sum(widths) - spacing if s else 0
    else:
        total = ctx.text_extents(s).x_advance
    if anchor == "c": x -= total / 2
    elif anchor == "r": x -= total
    ctx.set_source_rgba(*col, alpha)
    if spacing:
        for c, w in zip(s, widths):
            ctx.move_to(x, y); ctx.show_text(c); x += w
    else:
        ctx.move_to(x, y); ctx.show_text(s)


def wrap(ctx, s, size, maxw, bold=False):
    font(ctx, size, bold)
    lines, cur = [], ""
    for w in s.split():
        trial = (cur + " " + w).strip()
        if ctx.text_extents(trial).x_advance > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur: lines.append(cur)
    return lines


def polyline(ctx, pts, p, col, width=3.0, alpha=1.0, dash=None):
    """Draw a polyline progressively: p=0 nothing, p=1 complete."""
    if p <= 0: return
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    target = sum(segs) * p
    ctx.set_source_rgba(*col, alpha); ctx.set_line_width(width)
    ctx.set_dash(dash or [])
    ctx.set_line_cap(cairo.LINE_CAP_SQUARE); ctx.set_line_join(cairo.LINE_JOIN_MITER)
    ctx.move_to(*pts[0]); acc = 0
    for i, L in enumerate(segs):
        if acc + L >= target:
            k = (target - acc) / L if L else 1
            ctx.line_to(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)
            break
        ctx.line_to(*pts[i + 1]); acc += L
    ctx.stroke(); ctx.set_dash([])


def rect_pts(x1, y1, x2, y2): return [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]


def clip_rect(ctx, x1, y1, x2, y2):
    """ctx.save() + clip. Caller must ctx.restore()."""
    ctx.save(); ctx.rectangle(x1, y1, x2 - x1, y2 - y1); ctx.clip()


def dot(ctx, x, y, r, col, alpha=1.0):
    ctx.set_source_rgba(*col, alpha); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()


def leader(ctx, p, col, tip, elbow, label, size=24, anchor="l"):
    """Leader line from tip to elbow, then label types on."""
    polyline(ctx, [tip, elbow], clamp(p * 2), col, 2)
    if p > 0: dot(ctx, tip[0], tip[1], 5, col, clamp(p * 4))
    n = int(len(label) * clamp(p * 2 - 1))
    dx = 10 if anchor == "l" else -10
    text(ctx, label, elbow[0] + dx, elbow[1] + 8, size, col, bold=True, anchor=anchor, chars=n)


LABEL_SIZE = 28      # leader labels: 28px bold (was 24px, about 9pt on a phone); plates scale with it


def label(ctx, p, col, tip, elbow, txt, anchor="l", a=1.0, size=None):
    """Shared leader label: leader from `tip` to `elbow`, then the text types on beside the elbow on a dark
    plate (so linework never strikes through it). p = 0..1 draw-on progress, a = overall fade (0..1),
    anchor "l" puts the text right of the elbow, "r" left of it. Specs used to copy their own 24px version;
    new specs should use this one (older specs that define their own keep working unchanged)."""
    if p <= 0 or a <= 0: return
    size = size or LABEL_SIZE
    if a < 1: ctx.push_group()
    polyline(ctx, [tip, elbow], clamp(p * 2), col, 2)
    dot(ctx, tip[0], tip[1], 5, col, clamp(p * 4))
    n = int(len(txt) * clamp(p * 2 - 1))
    if n > 0:
        font(ctx, size, True)
        w = ctx.text_extents(txt[:n]).x_advance
        x = elbow[0] + 10 if anchor == "l" else elbow[0] - 10 - w
        ph = round(size * 1.2)
        ctx.set_source_rgba(*BG, 0.92); ctx.rectangle(x - 6, elbow[1] - ph / 2, w + 12, ph); ctx.fill()
        text(ctx, txt, x, elbow[1] + round(size * 0.36), size, col, bold=True, chars=n)
    if a < 1: ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def gone(t, t0, d=0.5):
    """1 until t0, then fades to 0 over d seconds (for labels that are no longer relevant)."""
    return 1 - clamp((t - t0) / d)


def dim_v(ctx, x, y1, y2, label, p, col=BLUE):
    polyline(ctx, [(x, y1), (x, y2)], p, col, 2)
    for y in (y1, y2):
        polyline(ctx, [(x - 14, y), (x + 14, y)], p, col, 2)
        polyline(ctx, [(x - 9, y + 9), (x + 9, y - 9)], p, col, 3)
    ctx.save(); ctx.translate(x - 14, (y1 + y2) / 2); ctx.rotate(-math.pi / 2)
    text(ctx, label, 0, 0, 24, col, alpha=clamp(p * 2 - 1), bold=True, anchor="c"); ctx.restore()


def dim_h(ctx, y, x1, x2, label, p, col=BLUE):
    polyline(ctx, [(x1, y), (x2, y)], p, col, 2)
    for x in (x1, x2):
        polyline(ctx, [(x, y - 14), (x, y + 14)], p, col, 2)
        polyline(ctx, [(x - 9, y + 9), (x + 9, y - 9)], p, col, 3)
    text(ctx, label, (x1 + x2) / 2, y - 14, 24, col, alpha=clamp(p * 2 - 1), bold=True, anchor="c")


def earth_hatch(ctx, x1, y1, x2, y2, col, alpha=0.35, reveal=1.0):
    clip_rect(ctx, x1, y1, x1 + (x2 - x1) * reveal, y2)
    ctx.set_source_rgba(*col, alpha); ctx.set_line_width(2)
    h = y2 - y1
    for k in range(int(-h) - 40, int(x2 - x1) + 40, 36):
        for j in range(3):
            ctx.move_to(x1 + k + j * 8, y2); ctx.line_to(x1 + k + j * 8 + h, y1)
    ctx.stroke(); ctx.restore()


def gravel(seed, x1, y1, x2, y2, n):
    rng = random.Random(seed)
    return [(rng.uniform(x1, x2), rng.uniform(y1, y2), rng.uniform(2, 4.5)) for _ in range(n)]


def draw_gravel(ctx, pts, col, alpha=0.55):
    ctx.set_source_rgba(*col, alpha); ctx.set_line_width(1.6)
    for x, y, r in pts:
        ctx.new_sub_path(); ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.stroke()


def concrete_points(seed, x1, y1, x2, y2, n, inside=lambda x, y: True):
    rng = random.Random(seed)
    pts = [(rng.uniform(x1, x2), rng.uniform(y1, y2), rng.random()) for _ in range(n)]
    return [p for p in pts if inside(p[0], p[1])]


def draw_concrete(ctx, pts, col, alpha=0.75):
    """Standard concrete section symbol: stipple + aggregate triangles."""
    for x, y, r in pts:
        ctx.set_source_rgba(*col, alpha)
        if r < 0.7:
            ctx.arc(x, y, 1.8, 0, 2 * math.pi); ctx.fill()
        else:
            ctx.move_to(x, y - 5); ctx.line_to(x + 5, y + 4); ctx.line_to(x - 5, y + 4); ctx.close_path()
            ctx.set_line_width(1.5); ctx.stroke()


def stamp(ctx, label, x, y, p, col, fade=0.0, angle=-0.12):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle)
    sc = 1.4 - 0.4 * p; ctx.scale(sc, sc)
    a = p * (1 - 0.65 * fade)
    ctx.set_source_rgba(*col, a); ctx.set_line_width(4)
    ctx.rectangle(-150, -42, 300, 84); ctx.stroke()
    ctx.set_line_width(2); ctx.rectangle(-140, -32, 280, 64); ctx.stroke()
    text(ctx, label, 0, 13, 40, col, alpha=a, bold=True, anchor="c", spacing=3)
    ctx.restore()


# ---------------------------------------------------------------- caption
def caption(spec):
    """The Instagram caption. If META["question"] is set (one short, easy-to-answer question), it goes right after
    the first line, so it shows in the feed preview before "... more" and invites a comment. Older specs without
    the field get their CAPTION unchanged."""
    cap = spec.CAPTION.strip("\n")
    q = spec.META.get("question", "").strip()
    if not q: return cap
    first, sep, rest = cap.partition("\n")
    return first + "\n\n" + q + ("\n" + rest if sep else "")


# ---------------------------------------------------------------- background
_BG = None
def background():
    global _BG
    if _BG is not None: return _BG
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
    c.set_source_rgb(*BG); c.paint()
    g = cairo.RadialGradient(W / 2, H * 0.42, 100, W / 2, H * 0.42, 1100)
    g.add_color_stop_rgba(0, *BLUE, 0.10); g.add_color_stop_rgba(1, *BLUE, 0.0)
    c.set_source(g); c.paint()
    for i in range(0, max(W, H), 30):
        major = i % 150 == 0
        c.set_source_rgba(*BLUE, 0.13 if major else 0.055); c.set_line_width(1.5 if major else 1)
        if i <= W: c.move_to(i + .5, 0); c.line_to(i + .5, H); c.stroke()
        c.move_to(0, i + .5); c.line_to(W, i + .5); c.stroke()
    c.set_source_rgba(*WHITE, 0.35); c.set_line_width(3); c.rectangle(40, 60, W - 80, H - 120); c.stroke()
    c.set_line_width(1.5); c.rectangle(52, 72, W - 104, H - 144); c.stroke()
    _BG = s
    return s


# ---------------------------------------------------------------- full frame
_MODEL_CACHE = {}
def _model(spec):
    if not hasattr(spec, "model3d"): return None
    # cached on the spec module itself (an id(spec) key could be reused by a later spec in the same process)
    if getattr(spec, "_model3d_cache", None) is None: spec._model3d_cache = spec.model3d()
    return spec._model3d_cache


def _draw3d(ctx, spec, cy, yaw, alpha=1.0, appear=None, pitch=None, scale_mul=1.0, highlight=None, ghost=None):
    from engine import three_d as td
    parts, cfg = _model(spec)
    cam = td.Camera(cfg["target"], yaw, cfg.get("pitch", 18) if pitch is None else pitch, cfg["dist"],
                    cfg["scale"] * scale_mul, 540, cy)
    td.render(ctx, parts, cam, alpha=alpha, appear=appear, highlight=highlight, ghost=ghost)


def section_zoom(spec, tl, t):
    """Scale for the 2D section at time t: a slow push-in over odd steps and pull-back over even ones, so the
    drawing is always gently moving (no jump at the cuts: each step starts where the last one ended).
    Opt out or tune per spec with META["drift"] = 0 / 0.03. Back to 1.0 by the result."""
    amt = spec.META.get("drift", DRIFT)
    if not amt or t < tl.s(1) or t >= tl.res0: return 1.0
    i = 1
    while i < tl.n and t >= tl.step_end(i): i += 1
    u = ease((t - tl.step_start(i)) / max(tl.tim["steps"][i - 1], 0.1))
    z = u if i % 2 else 1 - u
    if i == tl.n and i % 2: z = 1 - u if u > 0.5 else u           # odd step count: come back by the result
    return 1 + amt * z


def _section(ctx, spec, tl, t):
    """spec.draw_section with the slow camera drift applied."""
    z = section_zoom(spec, tl, t)
    if z == 1.0:
        spec.draw_section(ctx, t, tl); return
    fx, fy = DRIFT_FOCUS
    ctx.save()
    x0, y0, x1, y1 = DRIFT_CLIP
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); ctx.clip()
    ctx.translate(fx, fy); ctx.scale(z, z); ctx.translate(-fx, -fy)
    spec.draw_section(ctx, t, tl)
    ctx.restore()


def xray_window(spec, tl):
    """Mid-video 3D "x-ray" interlude (opt-in via META["xray"]).

    META["xray"] = {"after_step": 4, "upto": 15, "hot": [8, 9, 10]}
      after_step: the interlude fills the last ~2.6s of this step (its drawing is finished by then)
      upto:       model parts with order <= upto are drawn solid (built so far); later ones are faint ghosts
      hot:        part orders drawn with orange edges (what this part of the video is about)
      secs:       optional length (default 2.6); scale: optional 3D size multiplier (default 0.92)
    Returns (t0, t1) or None."""
    cfg = spec.META.get("xray")
    if not cfg or not _model(spec): return None
    k = cfg["after_step"]
    if not 1 <= k <= tl.n: return None
    dur = tl.tim["steps"][k - 1]
    L = min(cfg.get("secs", 2.6), dur - 1.8)
    if L < 1.4: return None
    t1 = tl.step_end(k)
    return (t1 - L, t1)


def _xray_amount(spec, tl, t):
    w = xray_window(spec, tl)
    if not w or not (w[0] <= t < w[1]): return 0.0, w
    return min(ease((t - w[0]) / 0.3), ease((w[1] - t) / 0.3)), w


def replay_window(spec, tl):
    """Build replay in the result: the 3D model rebuilds from the ground up in build order (a quick timelapse
    recap of every step), then keeps orbiting finished. Opt out per spec with META["replay"] = False.
    Returns (t0, t1) or None."""
    if not spec.META.get("replay", True) or not _model(spec): return None
    dur = tl.end0 - tl.res0
    t0 = tl.res0 + 0.45 * dur + 0.15            # just after the 3D shot starts fading in
    return t0, t0 + clamp(0.3 * dur, 1.4, 2.2)


def replay_appear(spec, tl, t):
    """appear(part) for the build replay (None once it's finished, or if the video opts out)."""
    w = replay_window(spec, tl)
    if not w or t >= w[1] + 0.4: return None
    parts = _model(spec)[0]
    n = max(p.order for p in parts) or 1
    step = (w[1] - w[0]) / n                    # each build order lands one after another
    return lambda part: 1.0 if part.base or part.order == 0 else clamp((t - w[0] - (part.order - 1) * step) / 0.4)


END_TEXT_Y = 560                     # end card with the 3D model: text sits where the hook text was


def end_model_on(spec):
    """End card keeps the finished 3D model on screen (opt out with META["end_model"] = False). Old specs with a
    witty sign-off keep the original text-only end card, since their sign-off lines need the middle of the frame."""
    return bool(_model(spec)) and spec.META.get("end_model", not spec.META.get("signoff"))


def end_motion(spec, tl, t):
    """End card camera: the finished model glides from the result shot down to the hook's position and turns back
    to the hook's starting angle, so the Reel's loop back to frame 0 (the same model, half built, same place and
    angle) is nearly seamless. Returns (cy, yaw)."""
    cfg = _model(spec)[1]
    cr, ch = cfg.get("cy_result", 820), cfg.get("cy_hook", 1010)
    u = ease((t - tl.end0) / 0.6)
    w = ease(clamp((t - tl.end0) / max(tl.duration - tl.end0 - 0.15, 0.5)))
    return cr + (ch - cr) * u, cfg["yaw"] + 25 * (1 - w)    # the result orbit ends at yaw + 25


def draw_frame(spec, tl, t):
    M = spec.META
    m3 = _model(spec)
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(s)
    ctx.set_source_surface(background()); ctx.paint()

    # header
    # Instant hook: frame 0 is already a full, readable frame (Reels autoplay starts on it), so the
    # header is on screen from t=0 and only the rule + subtitle animate in.
    series = M.get("series", SERIES)
    text(ctx, series, 90, 150, 30, BLUE, bold=True, spacing=6)
    text(ctx, M["title"], 88, 235, 76 if len(M["title"]) <= 19 else 60, WHITE, bold=True)
    text(ctx, M["subtitle"], 90, 285, 26, WHITE, alpha=0.75 * clamp((t + 0.2) / 0.5))
    polyline(ctx, [(90, 320), (990, 320)], prog(t, 0.0, 0.8), WHITE, 2, 0.6)

    # hook
    if t < tl.hook + 0.4:
        a = 1 - clamp((t - tl.hook + 0.2) / 0.5)
        y0, gap = (470, 82) if m3 else (760, 95)
        last = len(M["hook"]) - 1
        for i, line in enumerate(M["hook"]):
            # first line is fully on screen at t=0; the rest land fast, the punchline last with a pop
            k = 1.0 if i == 0 else clamp((t - 0.15 - (i - 1) * 0.3 - (0.15 if i == last else 0)) / 0.2)
            col = ORANGE if i == last else WHITE
            if i == last and 0 < k:
                pop = 1 + 0.18 * (1 - ease(clamp((t - 0.6 - (last - 1) * 0.3) / 0.25)))
                ctx.save(); ctx.translate(W / 2, y0 + i * gap - 22); ctx.scale(pop, pop)
                text(ctx, line, 0, 22, 64, col, alpha=a * k, bold=True, anchor="c"); ctx.restore()
            else:
                text(ctx, line, W / 2, y0 + i * gap + (1 - ease(k)) * 24, 64, col, alpha=a * k, bold=True, anchor="c")
        k = clamp((t - 1.0) / 0.3)
        text(ctx, M["hook_sub"], W / 2, y0 + len(M["hook"]) * gap + 40, 32, BLUE, alpha=a * k, bold=True, anchor="c", spacing=2)
        if m3:
            parts, cfg = m3
            n = max(p.order for p in parts) + 1
            span = max(tl.hook - 1.0, 1.5)
            # Part-built first frame: frame 0 already shows the first `hook_start` of the build (default half),
            # so the autoplay frame is a recognisable structure, not an empty slab. The rest drops in over the hook.
            f0 = clamp(M.get("hook_start", 0.5), 0.0, 0.95)
            tb = f0 * span + (1 - f0) * t + 0.1
            appear = lambda part: 1.0 if part.order == 0 else clamp((tb - span * part.order / n) / 0.45)
            yaw = cfg["yaw"] + 14 * (t / max(tl.hook, 1))
            _draw3d(ctx, spec, cfg.get("cy_hook", 1010), yaw, alpha=a, appear=appear)

    # section label + the video's own drawing
    kx, xw = _xray_amount(spec, tl, t)
    kr = 0.0                                   # the 3D result shot (fades in ~45% into the result)
    if m3 and t >= tl.res0:
        dur = tl.end0 - tl.res0
        kr = ease((t - tl.res0 - 0.45 * dur) / 0.7)
    text(ctx, M.get("section_label", "SECTION A-A  (NTS)"), 90, 385, 24, WHITE,
         alpha=0.7 * clamp((t - tl.s(1)) / 0.4) * clamp(1 - 2 * max(kx, kr)), bold=True, spacing=2)
    k3 = max(kr, kx)
    if k3 < 1:
        if k3 > 0:
            ctx.push_group(); _section(ctx, spec, tl, t); ctx.pop_group_to_source(); ctx.paint_with_alpha(1 - k3)
        else:
            _section(ctx, spec, tl, t)
    if kx > 0:
        # x-ray interlude: the 3D model so far, current work in orange, the rest as faint ghosts, orbiting
        cfg, xc = m3[1], M["xray"]
        u = (t - xw[0]) / (xw[1] - xw[0])
        hot = set(xc.get("hot", []))
        _draw3d(ctx, spec, cfg.get("cy_result", 820), cfg["yaw"] + 30 - 45 * ease(u), alpha=kx,
                pitch=cfg.get("pitch", 18) + 6, scale_mul=xc.get("scale", 0.92), highlight=lambda p: p.order in hot,
                ghost=lambda p: not p.base and p.order > xc["upto"])
        text(ctx, "3D  //  BUILT SO FAR", 90, 385, 24, BLUE, alpha=0.9 * clamp(2 * kx - 1), bold=True, spacing=2)
    elif k3 > 0 and not (t >= tl.end0 and end_model_on(spec)):   # the end card carries the model on from here
        cfg = m3[1]
        u = (t - tl.res0) / max(tl.end0 - tl.res0, 1)
        _draw3d(ctx, spec, cfg.get("cy_result", 820), cfg["yaw"] - 25 + 50 * u, alpha=k3, appear=replay_appear(spec, tl, t))
        text(ctx, "3D  //  START TO FINISH", 90, 385, 24, BLUE, alpha=0.9 * clamp(2 * kr - 1), bold=True, spacing=2)

    # step panel
    def panel(num_txt, title, body, t0, t1, last=False):
        if not (t0 <= t < t1 + 0.01): return
        a = clamp((t - t0) / 0.25) * (1 if last else 1 - clamp((t - t1 + 0.2) / 0.2))
        if num_txt: text(ctx, num_txt, 90, PANEL_Y, 28, YEL, alpha=a, bold=True, spacing=4)
        text(ctx, title, 88, PANEL_Y + 64, 54, WHITE, alpha=a, bold=True)
        for i, ln in enumerate(wrap(ctx, body, BODY_SIZE, 890)):
            k = clamp((t - t0 - 0.2 - i * 0.15) / 0.3)
            text(ctx, ln, 90, PANEL_Y + 116 + i * BODY_GAP, BODY_SIZE, WHITE, alpha=a * k * 0.92)

    for i, (ttl, body) in enumerate(M["steps"], 1):
        panel(f"STEP {i:02d} / {tl.n:02d}", ttl, body, tl.step_start(i), tl.step_end(i))
    panel("", M.get("result_title", "THE RESULT"), M["result"], tl.res0, tl.end0, last=True)
    if t >= tl.res0:
        text(ctx, M.get("footnote", "Typical only. Engineer's design governs."), 90, 1580, 24, WHITE,
             alpha=0.6 * clamp((t - tl.res0 - 1.2) / 0.5))

    # progress ticks
    if t >= tl.s(1) - 0.2:
        seg = 900 / tl.n
        for i in range(tl.n):
            x = 90 + i * seg
            done = clamp((t - tl.step_start(i + 1)) / tl.tim["steps"][i])
            ctx.set_source_rgba(*WHITE, 0.25); ctx.rectangle(x, 1240, seg - 12, 6); ctx.fill()
            ctx.set_source_rgba(*YEL, 0.95); ctx.rectangle(x, 1240, (seg - 12) * done, 6); ctx.fill()

    # title block (decorative, sits under Reels caption area)
    tb = 1640
    ctx.set_source_rgba(*WHITE, 0.5); ctx.set_line_width(2)
    ctx.rectangle(90, tb, 900, 110); ctx.stroke()
    for x in (520, 700, 850):
        ctx.move_to(x, tb); ctx.line_to(x, tb + 110); ctx.stroke()
    for (x, lab, val) in ((100, SERIES, M.get("drawing", M["title"])[:22]), (530, "SCALE", "NTS"),
                          (710, "DWG", M.get("dwg", "001")), (860, "REV", "A")):
        text(ctx, lab, x, tb + 32, 18, BLUE, alpha=0.8, bold=True, spacing=2)
        text(ctx, val, x, tb + 78, 28, WHITE, alpha=0.8, bold=True)

    # end card: follow (+ the finished 3D model, turning back to the hook's framing for the loop)
    if t >= tl.end0 and end_model_on(spec):
        k = clamp((t - tl.end0) / 0.4)
        ctx.set_source_rgba(*BG, 0.92 * k); ctx.paint()
        cy, yaw = end_motion(spec, tl, t)
        _draw3d(ctx, spec, cy, yaw)                      # same model, same spot and angle as the result's last frame
        kt = clamp((t - tl.end0 - 0.2) / 0.4)
        text(ctx, "FOLLOW FOR MORE", W / 2, END_TEXT_Y + (1 - ease(kt)) * 24, 64, WHITE, alpha=kt, bold=True, anchor="c")
        k2 = clamp((t - tl.end0 - 0.6) / 0.4)
        polyline(ctx, [(W / 2 - 300, END_TEXT_Y + 50), (W / 2 + 300, END_TEXT_Y + 50)], k2, ORANGE, 3)
        k3 = clamp((t - tl.end0 - 0.9) / 0.4)
        text(ctx, HANDLE, W / 2, END_TEXT_Y + 115, 30, BLUE, alpha=k3, bold=True, anchor="c", spacing=3)
    elif t >= tl.end0:                                   # text-only end card (no model, or an old sign-off spec)
        k = clamp((t - tl.end0) / 0.4)
        ctx.set_source_rgba(*BG, 0.92 * k); ctx.paint()
        text(ctx, "FOLLOW FOR MORE", W / 2, 840, 64, WHITE, alpha=k, bold=True, anchor="c")
        k2 = clamp((t - tl.end0 - 0.5) / 0.4)
        polyline(ctx, [(W / 2 - 300, 900), (W / 2 + 300, 900)], k2, ORANGE, 3)
        signoff = M.get("signoff", "").upper()          # optional; new videos end on "Follow for more" only
        for i, ln in enumerate(wrap(ctx, signoff, 38, 860, bold=True)):
            text(ctx, ln, W / 2, 965 + i * 52, 38, ORANGE, alpha=k2, bold=True, anchor="c")
        k3 = clamp((t - tl.end0 - 1.0) / 0.4)
        text(ctx, HANDLE, W / 2, 1130, 30, BLUE, alpha=k3, bold=True, anchor="c", spacing=3)
    return s


# ---------------------------------------------------------------- cover / thumbnail
def draw_cover(spec, tl):
    """Reel cover: big headline + finished drawing + title strip.
    Key content sits inside the centre 1080x1440 so the 3:4 profile-grid crop keeps it."""
    M = spec.META
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(s)
    ctx.set_source_surface(background()); ctx.paint()
    text(ctx, M.get("series", SERIES), W / 2, 300, 30, BLUE, bold=True, anchor="c", spacing=6)
    lines = M.get("cover", M["hook"][:2])
    size = 92 if max(len(l) for l in lines) <= 16 else 74
    for i, line in enumerate(lines):
        text(ctx, line, W / 2, 400 + i * (size + 18), size, ORANGE if i == len(lines) - 1 else WHITE, bold=True, anchor="c")
    # finished drawing (3D hero shot if the video has a model), in the middle band
    if _model(spec):
        cfg = _model(spec)[1]
        _draw3d(ctx, spec, cfg.get("cy_cover", 1000) + (len(lines) - 2) * 40, cfg["yaw"] - 8, scale_mul=cfg.get("cover_scale", 1.0))
    else:
        ctx.save(); ctx.translate(81, 330 + (len(lines) - 2) * 60); ctx.scale(0.85, 0.85)
        spec.draw_section(ctx, tl.end0 - 0.05, tl)
        ctx.restore()
    # title strip
    y = 1420
    ctx.set_source_rgba(*ORANGE, 1); ctx.rectangle(90, y, 900, 120); ctx.fill()
    text(ctx, M["title"], W / 2, y + 62, 56 if len(M["title"]) <= 22 else 46, BG, bold=True, anchor="c")
    text(ctx, "HOW IT'S BUILT  //  STEP BY STEP", W / 2, y + 100, 24, BG, bold=True, anchor="c", spacing=2)
    text(ctx, HANDLE, W / 2, y + 175, 26, BLUE, bold=True, anchor="c", spacing=3)
    return s
