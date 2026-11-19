"""013 Post-tensioned concrete slab (structural)."""
import math
from engine.blueprint import *

META = {
    "category": "structural",
    "title": "POST-TENSIONED SLAB",
    "subtitle": "STRUCTURAL  //  TYPICAL AU METHOD",
    "dwg": "013",
    "drawing": "PT SLAB",
    "section_label": "SECTION ALONG TENDON  (NTS)",
    "hook": ["THIS FLOOR HAS", "STEEL CABLES", "PULLED TIGHT."],
    "hook_sub": "HOW A PT SLAB IS BUILT",
    "cover": ["THE CABLES", "ARE PULLED", "AFTER THE POUR."],
    "xray": {"after_step": 4, "upto": 12, "hot": [5, 6, 7, 8, 9, 10, 12]},   # tendons + anchors before the pour
    "steps": [
        ("FORMWORK", "A formwork deck goes up on props, with edge forms around the slab."),
        ("BOTTOM BARS", "Bar chairs go down, then the bottom reinforcement. Extra bars go behind each anchor."),
        ("TENDON PROFILE", "Ducts with steel strands are set on chairs. High over the columns, low in the middle of each span."),
        ("ANCHORS", "A live end anchor goes at one edge for the jack. A dead end anchor is cast in at the other."),
        ("TOP BARS", "Top bars over the columns. Then the tendon heights and the steel are checked before the pour."),
        ("THE POUR", "Concrete is pumped in, vibrated and finished. Then it's cured until it's strong enough."),
        ("STRESSING", "A hydraulic jack pulls each tendon tight. How far it stretches is measured and checked."),
        ("GROUT & STRIP", "Ducts are grouted, the tails cut off and the pockets filled. Then the formwork comes out."),
    ],
    "result": "The curved cables push the slab up between the columns. A thinner slab, longer spans and fewer columns.",
}

NARRATION = {
    "hook": "This concrete floor has steel cables inside it, pulled tight after the pour. Here's how a post-tensioned slab is built.",
    "steps": [
        "First, a formwork deck goes up on props. Edge forms go around the slab.",
        "Bar chairs go down, then the bottom reinforcement. Extra bars go in behind each anchor, where the forces are high.",
        "Next, the tendons. Each one is a flat duct with steel strands inside. They're set on chairs, high over the columns, and low in the middle of each span.",
        "A live end anchor goes at one edge. That's where the jack will pull. A dead end anchor is cast in at the other end.",
        "Top bars go in over the columns. Then the tendon heights and the steel are checked before the pour.",
        "Concrete is pumped in, vibrated, and finished. Then it's cured, until it's strong enough to take the load.",
        "Now the stressing. A hydraulic jack pulls each tendon tight. How far it stretches is measured and checked against the design.",
        "The ducts are filled with grout. The tails are cut off, and the pockets are filled. Then the formwork can come out.",
    ],
    "result": "The curved cables push the slab up, between the columns. That means a thinner slab, longer spans, and fewer columns.",
    "end": "Follow for more.",
}

CAPTION = """These cables are pulled tight after the concrete goes in 👇 How a post-tensioned (PT) slab is built.

Typical: formwork deck on props with edge forms, bar chairs and bottom reinforcement, anti-burst bars behind the anchors, flat ducts with steel strands set to a draped profile (high over the columns, low at midspan) on chairs of set heights, live end and dead end anchorages, top bars over the columns, a pre-pour check of the tendon profile and steel, then the pour. Once the concrete reaches the strength the engineer specifies, each tendon is stressed with a hydraulic jack and the extension is checked against the calculated value. Bonded ducts are then grouted, tails cut and pockets filled before the formwork is stripped.
The draped tendons push up on the slab, so PT floors can be thinner, span further and need fewer columns. Never cut or core into a PT slab without the engineer's approval.
Typical only. Your engineer's design governs.

#posttensioning #ptslab #concrete #structuralengineering #formwork #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS; slab depth exaggerated)
TOS, SOF = 620, 740                  # slab top / soffit
EL, ER = 200, 950                    # slab edges (live end left, dead end right)
COLS = [232, 575, 918]               # column centrelines
CW = 22                              # column half width
FLR = 1100                           # floor below
MID = (TOS + SOF) / 2
HI, LO = TOS + 22, SOF - 22          # tendon high (over columns) / low (midspan)
CTRL = [(EL, MID), (403, LO), (575, HI), (747, LO), (ER, MID)]    # tendon control points
PROPS = [300, 350, 450, 500, 650, 700, 800, 850]
BOT_Y, TOP_Y = SOF - 14, TOS + 14    # bottom / top bar levels
JACK_L = 92                          # jack length (sits left of the live end)


def tendon_y(x):
    """Draped profile: cosine blends between control points (smooth, flat at each high/low point)."""
    for (x0, y0), (x1, y1) in zip(CTRL, CTRL[1:]):
        if x0 <= x <= x1:
            u = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * (1 - math.cos(math.pi * u)) / 2
    return MID


def tendon_pts(x0=EL, x1=ER, n=90):
    return [(x0 + (x1 - x0) * k / n, tendon_y(x0 + (x1 - x0) * k / n)) for k in range(n + 1)]


SLAB_CONC = concrete_points(131, EL, TOS, ER, SOF, 420,
                            lambda x, y: TOS + 4 < y < SOF - 4 and abs(y - tendon_y(x)) > 9)
FLR_CONC = concrete_points(132, 90, FLR, 990, FLR + 38, 120, lambda x, y: FLR + 4 < y < FLR + 34)
POCKET = [(EL, MID - 22), (EL + 16, MID - 14), (EL + 16, MID + 14), (EL, MID + 22)]


def label(ctx, p, col, tip, elbow, txt, anchor="l", a=1.0):
    """Leader + typed label on a dark plate (so linework never strikes through), with an overall fade `a`."""
    if p <= 0 or a <= 0: return
    if a < 1: ctx.push_group()
    polyline(ctx, [tip, elbow], clamp(p * 2), col, 2)
    dot(ctx, tip[0], tip[1], 5, col, clamp(p * 4))
    n = int(len(txt) * clamp(p * 2 - 1))
    if n > 0:
        font(ctx, 24, True)
        w = ctx.text_extents(txt[:n]).x_advance
        x = elbow[0] + 10 if anchor == "l" else elbow[0] - 10 - w
        ctx.set_source_rgba(*BG, 0.92); ctx.rectangle(x - 6, elbow[1] - 14, w + 12, 28); ctx.fill()
        text(ctx, txt, x, elbow[1] + 8, 24, col, bold=True, chars=n)
    if a < 1: ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def gone(t, t0, d=0.5): return 1 - clamp((t - t0) / d)


def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def up_arrow(ctx, x, y0, y1, p, col, a=1.0):
    if p <= 0: return
    yt = y0 + (y1 - y0) * p
    polyline(ctx, [(x, y0), (x, yt)], 1, col, 3, alpha=a)
    polyline(ctx, [(x - 10, yt + 12), (x, yt), (x + 10, yt + 12)], 1, col, 3, alpha=a)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    strip = prog(t, s8 + 1.6, 0.8)            # formwork comes out at the end of step 8

    # floor below + columns (context, there from the start of step 1)
    c = tl.col(1, t); p = prog(t, s1, 0.8)
    if p > 0:
        polyline(ctx, rect_pts(90, FLR, 990, FLR + 38), p, c, 2.5)
        draw_concrete(ctx, FLR_CONC, c, 0.5 * p)
        for x in COLS:
            polyline(ctx, [(x - CW, FLR), (x - CW, SOF), (x + CW, SOF), (x + CW, FLR)], p, c, 2.5)

    # 1 formwork deck on props + edge forms
    fa = 1 - strip
    pd = prog(t, s1 + 0.4, 1.0)
    if pd > 0 and fa > 0:
        xr = EL - 30 + (ER + 60 - EL) * pd
        for x0, x1 in ((EL - 30, COLS[0] - CW), (COLS[0] + CW, COLS[1] - CW), (COLS[1] + CW, COLS[2] - CW),
                       (COLS[2] + CW, ER + 30)):
            if x0 >= xr: continue
            polyline(ctx, rect_pts(x0, SOF, min(x1, xr), SOF + 14), 1, c, 2, alpha=fa)
        for i, x in enumerate(PROPS):
            pp = prog(t, s1 + 0.9 + i * 0.1, 0.4)
            if pp <= 0: continue
            polyline(ctx, [(x, SOF + 14), (x, SOF + 14 + (FLR - SOF - 14) * pp)], 1, c, 2.5, alpha=fa)
            polyline(ctx, [(x - 14, FLR - 4), (x + 14, FLR - 4)], pp, c, 2.5, alpha=fa)
        for x in (EL - 30, ER + 30):                                   # edge forms
            pe = prog(t, s1 + 1.6, 0.5)
            polyline(ctx, rect_pts(x - 6 if x < EL else x - 18, TOS - 16, x + 18 if x < EL else x + 6, SOF), pe, c, 2,
                     alpha=fa)
    label(ctx, clamp((t - s1 - 1.0) / 0.8), c, (176, SOF + 7), (110, 1150), "FORMWORK DECK", a=gone(t, s3))
    label(ctx, clamp((t - s1 - 1.6) / 0.8), c, (PROPS[7], 980), (940, 1150), "PROPS", anchor="r", a=gone(t, s3))
    label(ctx, clamp((t - s1 - 2.2) / 0.8), c, (EL - 24, TOS - 10), (110, 520), "EDGE FORM", a=gone(t, s3))

    # 2 bottom bars on chairs + anti-burst bars behind the anchors
    c = tl.col(2, t)
    pb = prog(t, s2, 1.2)
    if pb > 0:
        polyline(ctx, [(EL + 10, BOT_Y), (ER - 10, BOT_Y)], pb, c, 2.5)
        for x in range(260, 930, 70):
            if EL + 10 + (ER - EL - 20) * pb < x: break
            polyline(ctx, [(x - 6, SOF), (x, BOT_Y + 3), (x + 6, SOF)], 1, c, 1.6, alpha=0.8)    # chair
    pz = prog(t, s2 + 1.3, 0.6)
    if pz > 0:                                                       # burst bars: zig-zag behind each anchor
        for xe, sg in ((EL + 14, 1), (ER - 14, -1)):
            pts = [(xe + sg * (k * 9), MID - 30 if k % 2 else MID + 30) for k in range(7)]
            polyline(ctx, pts, pz, c, 2)
    label(ctx, clamp((t - s2 - 0.8) / 0.8), c, (EL + 40, BOT_Y), (110, 1192), "BOTTOM BARS", a=gone(t, s4))
    label(ctx, clamp((t - s2 - 1.6) / 0.8), c, (ER - 30, MID + 30), (940, 1192), "BURST BARS", anchor="r", a=gone(t, s4))

    # 3 tendon on a draped profile (drawn orange, settles to white), with profile chairs of different heights
    c = tl.col(3, t)
    stressed = prog(t, s7 + 0.5, 1.6)                    # glows orange again while it's stressed
    grout = prog(t, s8, 1.0)
    pt = prog(t, s3, 1.6)
    if pt > 0:
        tcol = mix(c, ORANGE, stressed * (1 - grout))
        for k, xc in enumerate((290, 350, 403, 470, 530, 620, 680, 747, 810, 870)):
            pc = prog(t, s3 + 0.2 + k * 0.08, 0.4)
            if pc > 0:
                polyline(ctx, [(xc, BOT_Y - 2), (xc, BOT_Y - 2 - (BOT_Y - 2 - tendon_y(xc) - 7) * pc)], 1, c, 1.6, alpha=0.7)
        pts = tendon_pts(EL, EL + (ER - EL) * pt)
        polyline(ctx, [(x, y - 6) for x, y in pts], 1, tcol, 2.5)          # flat duct, top and bottom
        polyline(ctx, [(x, y + 6) for x, y in pts], 1, tcol, 2.5)
        if grout > 0:
            ctx.save(); ctx.rectangle(EL, 0, (ER - EL) * grout, H); ctx.clip()
            for dy in (-3, 0, 3):
                polyline(ctx, [(x, y + dy) for x, y in pts], 1, c, 1.4, alpha=0.6)
            ctx.restore()
        else:
            polyline(ctx, pts, 1, tcol, 1.4, alpha=0.8, dash=[10, 6])      # strands inside
    label(ctx, clamp((t - s3 - 1.2) / 0.8), c, (575, HI - 6), (560, 482), "HIGH OVER COLUMN", a=gone(t, s5))
    label(ctx, clamp((t - s3 - 1.8) / 0.8), c, (403, LO + 6), (403, 900), "LOW AT MIDSPAN", a=gone(t, s5))
    label(ctx, clamp((t - s3 - 2.4) / 0.8), c, (870, tendon_y(870) - 6), (940, 445), "DUCT + STRANDS", anchor="r", a=gone(t, s5))

    # 4 anchors: live end (pocket former, jack goes here) and dead end
    c = tl.col(4, t)
    pa = prog(t, s4, 0.6)
    if pa > 0:
        fill_poly(ctx, POCKET, BG, pa)
        polyline(ctx, POCKET, pa, c, 2.5)
        polyline(ctx, [(EL + 16, MID - 30), (EL + 16, MID + 30)], pa, c, 4)            # live end plate
    pe = prog(t, s4 + 0.8, 0.6)
    if pe > 0:
        polyline(ctx, [(ER - 20, MID - 26), (ER - 20, MID + 26)], pe, c, 4)            # dead end plate
        for k in range(3):                                                              # bulb ends of strands
            dot(ctx, ER - 34 + k * 0, MID - 12 + k * 12, 5, c, pe)
    label(ctx, clamp((t - s4 - 0.6) / 0.8), c, (EL + 8, MID - 22), (110, 482), "LIVE END", a=gone(t, s8))
    label(ctx, clamp((t - s4 - 1.4) / 0.8), c, (ER - 20, MID - 26), (940, 520), "DEAD END", anchor="r", a=gone(t, s6))

    # 5 top bars over the middle column + inspection stamp
    c = tl.col(5, t)
    ptb = prog(t, s5, 0.8)
    if ptb > 0:
        polyline(ctx, [(470, TOP_Y), (680, TOP_Y)], ptb, c, 2.5)
        polyline(ctx, [(EL + 10, TOP_Y), (300, TOP_Y)], ptb, c, 2.5)
    label(ctx, clamp((t - s5 - 0.6) / 0.8), c, (670, TOP_Y), (940, 445), "TOP BARS", anchor="r", a=gone(t, s7))
    sa = gone(t, s6 + 0.2, 0.5)
    if sa > 0 and t > s5 + 1.6:
        ctx.push_group(); stamp(ctx, "CHECKED", 740, 930, clamp((t - s5 - 1.6) / 0.35), BLUE)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(sa)

    # 6 the pour (left to right), finished top
    c = tl.col(6, t)
    pc = prog(t, s6, 1.8)
    if pc > 0:
        xr = EL + (ER - EL) * pc
        ctx.save(); ctx.rectangle(EL, TOS, xr - EL, SOF - TOS); ctx.clip()
        draw_concrete(ctx, SLAB_CONC, c, 0.55)
        ctx.restore()
        polyline(ctx, [(EL, TOS), (xr, TOS)], 1, c, 3)
        polyline(ctx, [(EL, SOF), (xr, SOF)], 1, c, 3)
        if pc >= 1:
            polyline(ctx, [(EL, TOS), (EL, SOF)], 1, c, 3)
            polyline(ctx, [(ER, TOS), (ER, SOF)], 1, c, 3)
        if pc < 1:                                                    # pump hose dropping concrete
            polyline(ctx, [(xr, TOS - 120), (xr, TOS - 16)], 1, c, 6)
            for k in range(3):
                dot(ctx, xr - 6 + k * 6, TOS - 8 + (k % 2) * 4, 3, c)
    label(ctx, clamp((t - s6 - 1.0) / 0.8), c, (680, TOS + 30), (940, 560), "CONCRETE", anchor="r", a=gone(t, s7 + 0.4))

    # 7 stressing: jack at the live end pulls the tendon, slab is pushed up between the columns
    c = tl.col(7, t)
    pj = prog(t, s7, 0.5) * gone(t, s8 + 0.4)
    if pj > 0:
        ext = 18 * stressed
        x1 = EL - 2; x0 = x1 - JACK_L
        ctx.push_group()
        fill_poly(ctx, rect_pts(x0 - ext, MID - 26, x1 - 30 - ext, MID + 26), BG, 1)
        polyline(ctx, rect_pts(x0 - ext, MID - 26, x1 - 30 - ext, MID + 26), 1, c, 2.5)          # cylinder
        polyline(ctx, rect_pts(x1 - 30, MID - 14, x1, MID + 14), 1, c, 2.5)                      # nose on the anchor
        if ext > 1: polyline(ctx, rect_pts(x1 - 30 - ext, MID - 8, x1 - 30, MID + 8), 1, c, 2)   # ram
        polyline(ctx, [(x0 - ext - 14, MID), (EL, MID)], 1, ORANGE if stressed < 1 else c, 2)  # strand tail
        ctx.pop_group_to_source(); ctx.paint_with_alpha(pj)
        if 0 < stressed < 1:
            ax = x0 - 10 - ext
            polyline(ctx, [(ax + 40, MID - 50), (ax, MID - 50)], 1, ORANGE, 3)
            polyline(ctx, [(ax + 12, MID - 60), (ax, MID - 50), (ax + 12, MID - 40)], 1, ORANGE, 3)
    label(ctx, clamp((t - s7 - 0.4) / 0.8), c, (EL - 50, MID + 26), (110, 1192), "STRESSING JACK", a=gone(t, s8 + 0.4))
    for k, x in enumerate((403, 747)):
        up_arrow(ctx, x, SOF + 100, SOF + 30, clamp(stressed * 1.4 - k * 0.2), ORANGE, a=gone(t, s8))
    label(ctx, clamp((t - s7 - 1.8) / 0.8), ORANGE, (760, SOF + 90), (940, 900), "PUSHES SLAB UP", anchor="r",
          a=gone(t, s8))

    # 8 grout, cut tail, fill pocket, strip the formwork
    c = tl.col(8, t)
    pf = prog(t, s8 + 0.6, 0.6)
    if pf > 0:
        fill_poly(ctx, POCKET, mix(BG, c, 0.25), pf)
        polyline(ctx, POCKET, pf, c, 2.5)
    label(ctx, clamp((t - s8 - 0.6) / 0.8), c, (870, tendon_y(870)), (940, 445), "GROUTED", anchor="r")
    label(ctx, clamp((t - s8 - 1.0) / 0.8), c, (EL + 8, MID), (110, 482), "POCKET FILLED")
    label(ctx, clamp((t - s8 - 1.8) / 0.8), c, (440, SOF + 4), (440, 900), "FORMWORK OUT", a=gone(t, tl.res0))

    # result: the tendon's upward push between the columns + slab depth
    r0 = tl.res0
    for k, x in enumerate((403, 747)):
        up_arrow(ctx, x, SOF + 110, SOF + 20, prog(t, r0 + k * 0.3, 0.6), BLUE)
    if t >= r0:
        text(ctx, "UPLIFT", 403, SOF + 145, 26, BLUE, alpha=prog(t, r0 + 0.4, 0.4), bold=True, anchor="c", spacing=4)
        text(ctx, "UPLIFT", 747, SOF + 145, 26, BLUE, alpha=prog(t, r0 + 0.7, 0.4), bold=True, anchor="c", spacing=4)
    dim_v(ctx, EL - 40, TOS, SOF, "SLAB", prog(t, r0 + 1.0, 0.6))


# ---------------------------------------------------------------- 3D model (mm): slab on columns, tendons exposed beyond the pour
def model3d():
    from engine.three_d import box, member3d
    P = []; o = 0
    GX, GZ, NX, NZ = 8000, 8000, 3, 2
    LX, LZ = GX * NX, GZ * NZ
    H, T = 3000, 450                                  # floor to soffit, slab (exaggerated so the drape reads)
    P.append(box(-1500, LX + 1500, -300, 0, -1500, LZ + 1500, o, "ground")); P[-1].base = True; o += 1
    for i in range(NX + 1):                           # columns
        for j in range(NZ + 1):
            P.append(box(i * GX - 250, i * GX + 250, 0, H, j * GZ - 250, j * GZ + 250, o, "concrete"))
    o += 1
    for i in range(NX):                               # formwork deck, bay by bay (split so faces sort cleanly)
        for j in range(NZ):
            for a in range(2):
                for b in range(2):
                    x0, z0 = i * GX + a * GX / 2, j * GZ + b * GZ / 2
                    P.append(box(x0 - (300 if i == 0 and a == 0 else 0), x0 + GX / 2 + (300 if i == NX - 1 and a == 1 else 0),
                                 H - 120, H, z0 - (300 if j == 0 and b == 0 else 0),
                                 z0 + GZ / 2 + (300 if j == NZ - 1 and b == 1 else 0), o, "timber"))
        o += 1

    def drape(u):                                     # 0..1 along one span: high at the ends, low in the middle
        return H + T - 90 - (T - 180) * math.sin(math.pi * u)

    def tendon(p_at, n_span, span, order):
        for s in range(n_span):
            for k in range(6):
                u0, u1 = k / 6, (k + 1) / 6
                a = p_at(s * span + u0 * span, drape(u0)); b = p_at(s * span + u1 * span, drape(u1))
                P.append(member3d(a, b, 160, 70, order, "steel"))
    for j in range(NZ + 1):                           # banded tendons along the column lines (X)
        for dz in (-300, 0, 300):
            z = j * GZ + dz
            tendon(lambda x, y, z=z: (x, y, z), NX, GX, o)
        o += 1
    for i in range(int(LX / 1600) + 1):               # distributed tendons the other way (Z)
        x = 400 + i * 1600
        if x > LX - 200: break
        tendon(lambda z, y, x=x: (x, y + 80, z), NZ, GZ, o + i // 5)
    o += 4
    for j in range(NZ + 1):                           # live end anchors along the near edge
        for dz in (-300, 0, 300):
            P.append(box(-320, -180, H + T / 2 - 120, H + T / 2 + 120, j * GZ + dz - 120, j * GZ + dz + 120, o, "steel"))
    o += 1
    xs = [-300, GX / 2, GX, GX * 1.5]                 # concrete poured over the first 1.5 bays, strip by strip
    zs = [-300, GZ / 2, GZ, GZ * 1.5, LZ + 300]
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            P.append(box(xs[i], xs[i + 1], H, H + T, zs[j], zs[j + 1], o, "concrete"))
        o += 1
    cfg = {"target": (LX / 2, 1800, LZ / 2), "yaw": 28, "pitch": 26, "dist": 48000, "scale": 1.5,
           "cy_hook": 1060, "cy_result": 820, "cy_cover": 1000, "cover_scale": 1.0}
    return P, cfg
