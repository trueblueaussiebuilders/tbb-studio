"""True Blue Builds blueprint engine: drawing helpers + shared frame chrome.

A video spec module provides META, NARRATION, CAPTION and draw_section(ctx, t, tl).
Everything here is shared so each new video only defines its own section drawing.
"""
import math, os, random
import cairo

W, H, FPS = 1080, 1920, 30
BG = (0.06, 0.22, 0.42)
WHITE = (0.93, 0.97, 1.0)
YEL = (1.0, 0.82, 0.30)
FONT = "DejaVu Sans Mono"
HANDLE = "@TRUEBLUEBUILDS"
SERIES = "TRUE BLUE BUILDS"

# Layout bands (keep key info out of the bottom ~20% and the right edge: Reels UI)
DRAW_TOP, DRAW_BOTTOM = 400, 1210   # section drawing area
PANEL_Y = 1305


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


def dim_v(ctx, x, y1, y2, label, p, col=YEL):
    polyline(ctx, [(x, y1), (x, y2)], p, col, 2)
    for y in (y1, y2):
        polyline(ctx, [(x - 14, y), (x + 14, y)], p, col, 2)
        polyline(ctx, [(x - 9, y + 9), (x + 9, y - 9)], p, col, 3)
    ctx.save(); ctx.translate(x - 14, (y1 + y2) / 2); ctx.rotate(-math.pi / 2)
    text(ctx, label, 0, 0, 24, col, alpha=clamp(p * 2 - 1), bold=True, anchor="c"); ctx.restore()


def dim_h(ctx, y, x1, x2, label, p, col=YEL):
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


# ---------------------------------------------------------------- background
_BG = None
def background():
    global _BG
    if _BG is not None: return _BG
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
    c.set_source_rgb(*BG); c.paint()
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1250)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.35)
    c.set_source(g); c.paint()
    for i in range(0, max(W, H), 30):
        major = i % 150 == 0
        c.set_source_rgba(1, 1, 1, 0.11 if major else 0.045); c.set_line_width(1.5 if major else 1)
        if i <= W: c.move_to(i + .5, 0); c.line_to(i + .5, H); c.stroke()
        c.move_to(0, i + .5); c.line_to(W, i + .5); c.stroke()
    c.set_source_rgba(*WHITE, 0.55); c.set_line_width(3); c.rectangle(40, 60, W - 80, H - 120); c.stroke()
    c.set_line_width(1.5); c.rectangle(52, 72, W - 104, H - 144); c.stroke()
    _BG = s
    return s


# ---------------------------------------------------------------- full frame
def draw_frame(spec, tl, t):
    M = spec.META
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(s)
    ctx.set_source_surface(background()); ctx.paint()

    # header
    series = M.get("series", SERIES)
    text(ctx, series, 90, 150, 30, YEL, bold=True, spacing=6, chars=int(len(series) * clamp(t / 1.0)))
    text(ctx, M["title"], 88, 235, 76 if len(M["title"]) <= 19 else 60, WHITE, bold=True,
         chars=int(len(M["title"]) * clamp((t - 0.3) / 1.0)))
    text(ctx, M["subtitle"], 90, 285, 26, WHITE, alpha=0.75 * clamp((t - 0.9) / 0.5))
    polyline(ctx, [(90, 320), (990, 320)], prog(t, 0.2, 1.2), WHITE, 2, 0.6)

    # hook
    if t < tl.hook + 0.4:
        a = clamp(t / 0.3) * (1 - clamp((t - tl.hook + 0.2) / 0.5))
        for i, line in enumerate(M["hook"]):
            k = clamp((t - 0.4 - i * 0.35) / 0.35)
            text(ctx, line, W / 2, 760 + i * 95 + (1 - ease(k)) * 30, 64, WHITE, alpha=a * k, bold=True, anchor="c")
        k = clamp((t - 1.6) / 0.4)
        text(ctx, M["hook_sub"], W / 2, 760 + len(M["hook"]) * 95 + 55, 32, YEL, alpha=a * k, bold=True, anchor="c", spacing=2)

    # section label + the video's own drawing
    text(ctx, M.get("section_label", "SECTION A-A  (NTS)"), 90, 385, 24, WHITE,
         alpha=0.7 * clamp((t - tl.s(1)) / 0.4), bold=True, spacing=2)
    spec.draw_section(ctx, t, tl)

    # step panel
    def panel(num_txt, title, body, t0, t1, last=False):
        if not (t0 <= t < t1 + 0.01): return
        a = clamp((t - t0) / 0.25) * (1 if last else 1 - clamp((t - t1 + 0.2) / 0.2))
        if num_txt: text(ctx, num_txt, 90, PANEL_Y, 28, YEL, alpha=a, bold=True, spacing=4)
        text(ctx, title, 88, PANEL_Y + 68, 54, WHITE, alpha=a, bold=True)
        for i, ln in enumerate(wrap(ctx, body, 32, 880)):
            k = clamp((t - t0 - 0.2 - i * 0.15) / 0.3)
            text(ctx, ln, 90, PANEL_Y + 128 + i * 46, 32, WHITE, alpha=a * k * 0.9)

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
        text(ctx, lab, x, tb + 32, 18, WHITE, alpha=0.55, bold=True, spacing=2)
        text(ctx, val, x, tb + 78, 28, WHITE, alpha=0.8, bold=True)

    # end card
    if t >= tl.end0:
        k = clamp((t - tl.end0) / 0.4)
        ctx.set_source_rgba(*BG, 0.88 * k); ctx.paint()
        k3 = clamp((t - tl.end0 - 1.0) / 0.4)
        text(ctx, HANDLE, W / 2, 760, 34, WHITE, alpha=0.8 * k3, bold=True, anchor="c", spacing=3)
        text(ctx, "FOLLOW FOR MORE BUILDS", W / 2, 860, 50, WHITE, alpha=k, bold=True, anchor="c")
        text(ctx, "HOUSES  //  SCHOOLS  //  BRIDGES", W / 2, 930, 28, WHITE, alpha=0.75 * k, bold=True, anchor="c", spacing=2)
        k2 = clamp((t - tl.end0 - 0.6) / 0.4)
        polyline(ctx, [(W / 2 - 300, 1000), (W / 2 + 300, 1000)], k2, YEL, 2)
        if M.get("next"):
            text(ctx, M["next"], W / 2, 1065, 32, YEL, alpha=k2, bold=True, anchor="c")
    return s
