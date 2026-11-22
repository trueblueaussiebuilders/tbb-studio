"""015 Timber roof trusses (residential)."""
import math
from engine.blueprint import *

META = {
    "category": "residential",
    "title": "ROOF TRUSSES",
    "subtitle": "RESIDENTIAL  //  TYPICAL AU METHOD",
    "dwg": "015",
    "drawing": "ROOF TRUSSES",
    "section_label": "SECTION THROUGH ROOF  (NTS)",
    "hook": ["YOUR ROOF", "WAS BUILT IN", "A FACTORY."],
    "hook_sub": "HOW ROOF TRUSSES GO UP",
    "cover": ["THE ROOF", "IS MADE IN", "A FACTORY."],
    "xray": {"after_step": 4, "upto": 16, "hot": list(range(4, 17))},   # the rest of the trusses stood up
    "steps": [
        ("FACTORY-MADE", "Each truss is designed by the truss maker and pressed together with steel nail plates."),
        ("CRANE LIFT", "Trusses arrive stacked on a truck. A crane lifts them onto the wall top plates."),
        ("FIRST TRUSS", "The first truss is stood up, set plumb and held with temporary bracing."),
        ("THE REST", "The rest go up at the spacing on the truss layout. Temporary battens hold them in line."),
        ("TIE-DOWNS", "Every truss is fixed to the top plate with steel brackets. They stop wind lifting the roof."),
        ("STRAP BRACING", "Steel straps cross the top chords diagonally. They stop the roof racking sideways."),
        ("ROOF BATTENS", "Battens are screwed across the top chords. The roof sheets or tiles fix to these."),
        ("ROOF ON", "Fascia and gutters go on the truss ends. Then sarking and the sheets or tiles."),
    ],
    "result": "The roof is tied to the walls at every truss, and the walls to the slab. That holds it down in a storm.",
}

NARRATION = {
    "hook": "Most new Australian roofs start in a factory. Then they're tied down.",
    "steps": [
        "Each truss is designed by the truss maker. It's pressed together in a factory, with steel nail plates at every joint.",
        "The trusses arrive stacked on a truck. A crane lifts them up onto the top plates of the wall frames.",
        "The first truss is stood up and set plumb. Then it's held with temporary bracing.",
        "The rest go up one by one, at the spacing on the truss layout. Temporary battens hold them in line.",
        "Every truss is fixed to the top plate with steel tie-down brackets. They stop the wind lifting the roof off.",
        "Steel strap bracing runs diagonally across the top chords. It stops the roof racking over sideways.",
        "Roof battens are screwed across the top chords. The roof sheets or tiles fix to these.",
        "Fascia and gutters go on the truss ends. Then sarking, and the roof sheets or tiles.",
    ],
    "result": "The roof is tied down to the walls at every truss. The walls are tied down to the slab. That's what holds it on in a storm.",
    "end": "Follow for more.",
}

CAPTION = """Most new Australian roofs start in a factory 👇 How timber roof trusses go up on a house.

Typical: the truss fabricator designs each truss and issues a truss layout showing positions, spacings, girder trusses and tie-down details. Trusses are delivered stacked and craned onto the wall top plates. The first truss (often a gable end or girder truss) is stood up, plumbed and temporarily braced, then the rest are stood at the spacing on the layout and held in line with temporary battens. Each truss is tied down to the top plate with the specified brackets or straps, so wind uplift is carried down through the wall frame to the slab. Steel strap bracing goes diagonally across the top chords to stop racking, roof battens are fixed across the top chords, then fascia, gutters, sarking or roof blanket and the roof sheets or tiles.
Never cut or notch a truss without the truss designer's approval.
Typical only. Your engineer's and truss designer's design governs.

#rooftrusses #roofframing #carpentry #housebuild #newhome #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
XL, XR = 170, 910                    # wall outer faces
WT = 12                              # wall frame thickness
PL = 940                             # top of the top plates
HY = 934                             # bottom chord centreline
K = 0.5                              # roof slope (exaggerated, NTS)
OH = 45                              # eave overhang
APEX = (540, HY - (540 - XL) * K)    # (540, 749)
SLAB_T, SLAB_B = 1150, 1192
FACTORY = -260                       # how far up the truss sits in step 1 (in the factory / on the hook)
B1, B2 = (417, HY), (663, HY)        # bottom chord panel points
T1, T2 = (355, HY - (355 - XL) * K), (725, HY - (2 * 540 - 725 - XL) * K)
JOINTS = [(XL, HY), (XR, HY), APEX, B1, B2, T1, T2]
WEBS = [(B1, T1), (B1, APEX), (B2, APEX), (B2, T2)]
EAVE_L, EAVE_R = (XL - OH, HY + OH * K), (XR + OH, HY + OH * K)

# roof plan inset (top right)
IX0, IX1, IY0, IY1 = 640, 960, 470, 630
IRIDGE = (IY0 + IY1) / 2
NTR = 14
ITR = [IX0 + 12 + i * (IX1 - IX0 - 24) / (NTR - 1) for i in range(NTR)]

SLAB_CONC = concrete_points(151, 150, SLAB_T, 930, SLAB_B, 160)


def chord_y(x):
    """Top chord centreline height at x (either side of the apex)."""
    return HY - (min(x, 2 * APEX[0] - x) - XL) * K




def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def arrow(ctx, x0, y0, x1, y1, col, p=1.0, a=1.0, head=12):
    if p <= 0: return
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    polyline(ctx, [(x0, y0), (xe, ye)], 1, col, 3, alpha=a)
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    polyline(ctx, [(xe - ux * head - uy * head * 0.8, ye - uy * head + ux * head * 0.8), (xe, ye),
                   (xe - ux * head + uy * head * 0.8, ye - uy * head - ux * head * 0.8)], 1, col, 3, alpha=a)


def bar(ctx, p0, p1, hw, col, p, width=2.5):
    """A truss member in elevation: dark-filled outline around the centreline p0 -> p1, drawn on by p."""
    if p <= 0: return
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * hw, dx / L * hw
    e = (p0[0] + dx * p, p0[1] + dy * p)
    q = [(p0[0] + nx, p0[1] + ny), (e[0] + nx, e[1] + ny), (e[0] - nx, e[1] - ny), (p0[0] - nx, p0[1] - ny)]
    fill_poly(ctx, q, BG, 1)
    polyline(ctx, q + [q[0]], 1, col, width)


def truss(ctx, t, tl, c, dy=0.0, p=1.0, plates=1.0):
    """One Fink truss in elevation, members drawn on by p, nail plates popping in by `plates`."""
    S = lambda q: (q[0], q[1] + dy)
    bar(ctx, S((XL, HY)), S((XR, HY)), 6, c, clamp(p * 3))
    bar(ctx, S(EAVE_L), S(APEX), 6, c, clamp(p * 3 - 1))
    bar(ctx, S(EAVE_R), S(APEX), 6, c, clamp(p * 3 - 1))
    for i, (a, b) in enumerate(WEBS):
        bar(ctx, S(a), S(b), 4, c, clamp((p * 3 - 2) * 1.4 - i * 0.1), width=2)
    for i, j in enumerate(JOINTS):
        k = clamp(plates * 2.2 - i * 0.2)
        if k <= 0: continue
        x, y = S(j); h = 11 * (1.3 - 0.3 * k)
        ctx.set_source_rgba(*mix(BG, c, 0.35), k); ctx.rectangle(x - h, y - h, 2 * h, 2 * h); ctx.fill()
        ctx.set_source_rgba(*c, k); ctx.set_line_width(1.6); ctx.rectangle(x - h, y - h, 2 * h, 2 * h); ctx.stroke()


def walls(ctx, c, p):
    """Slab, the two wall frames and their double top plates (context)."""
    if p <= 0: return
    polyline(ctx, rect_pts(150, SLAB_T, 930, SLAB_B), p, c, 3)
    draw_concrete(ctx, SLAB_CONC, c, 0.5 * p)
    polyline(ctx, [(60, SLAB_B), (150, SLAB_B)], p, c, 2, alpha=0.7)
    polyline(ctx, [(930, SLAB_B), (1020, SLAB_B)], p, c, 2, alpha=0.7)
    earth_hatch(ctx, 60, SLAB_B, 150, SLAB_B + 16, c, 0.3, reveal=p)
    earth_hatch(ctx, 930, SLAB_B, 1020, SLAB_B + 16, c, 0.3, reveal=p)
    for x0 in (XL, XR - WT):
        polyline(ctx, rect_pts(x0, PL, x0 + WT, SLAB_T), p, c, 2.5)
        polyline(ctx, [(x0, PL + 6), (x0 + WT, PL + 6)], p, c, 1.6)            # double top plate
        polyline(ctx, [(x0, PL + 12), (x0 + WT, PL + 12)], p, c, 1.6)
        polyline(ctx, [(x0, SLAB_T - 6), (x0 + WT, SLAB_T - 6)], p, c, 1.6)    # bottom plate


def bubble(ctx, t, tl, a):
    """Step 5 detail: the heel of the truss, enlarged, with the tie-down bracket and uplift."""
    if a <= 0: return
    s5 = tl.s(5); c5 = tl.col(5, t)
    cx, cy, r = 255, 615, 122
    ctx.push_group()
    # link from the heel to the bubble
    ctx.set_source_rgba(*WHITE, 0.8); ctx.set_line_width(2)
    ctx.arc(XL + 6, HY + 4, 30, 0, 2 * math.pi); ctx.stroke()
    polyline(ctx, [(XL + 6 + 21, HY + 4 - 21), (cx + r * 0.42, cy + r * 0.9)], 1, WHITE, 2, alpha=0.8)
    ctx.set_source_rgba(*BG, 0.96); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()
    ctx.save(); ctx.arc(cx, cy, r - 2, 0, 2 * math.pi); ctx.clip()
    ox, oy, sc = XL + 12, HY + 6, 3.2
    M = lambda x, y: (cx + (x - ox) * sc, cy + (y - oy) * sc)
    # wall frame + double top plate
    polyline(ctx, [M(XL, PL), M(XL, PL + 60)], 1, WHITE, 2.5)
    polyline(ctx, [M(XL + WT, PL), M(XL + WT, PL + 60)], 1, WHITE, 2.5)
    for y in (PL, PL + 6, PL + 12):
        polyline(ctx, [M(XL, y), M(XL + WT, y)], 1, WHITE, 2.5 if y == PL else 1.8)
    # bottom chord + top chord at the heel
    q = [M(XL - 4, HY - 6), M(XL + 60, HY - 6), M(XL + 60, HY + 6), M(XL - 4, HY + 6)]
    fill_poly(ctx, q, BG, 1); polyline(ctx, q + [q[0]], 1, WHITE, 2.5)
    for off in (-6, 6):
        polyline(ctx, [M(XL - 40, HY + 40 * K + off * 1.12), M(XL + 60, HY - 60 * K + off * 1.12)], 1, WHITE, 2.5)
    h = 9                                                                       # nail plate (faint, it's not the star)
    ctx.set_source_rgba(*WHITE, 0.12)
    ctx.rectangle(*M(XL - h, HY - h), 2 * h * sc, 2 * h * sc); ctx.fill()
    ctx.set_source_rgba(*WHITE, 0.6); ctx.set_line_width(1.6); ctx.set_dash([5, 4])
    ctx.rectangle(*M(XL - h, HY - h), 2 * h * sc, 2 * h * sc); ctx.stroke(); ctx.set_dash([])
    # the tie-down bracket: strap over the chord and down onto the plates, nailed off
    pb = prog(t, s5 + 0.9, 0.6)
    if pb > 0:
        x0 = XL + 15
        fill_poly(ctx, rect_pts(*M(x0, HY - 8), *M(x0 + 8, HY - 8 + 30 * pb))[:4], c5, 0.9)
        if pb >= 1:
            for y in (HY - 3, HY + 3, PL + 4, PL + 10, PL + 16):
                dot(ctx, *M(x0 + 4, y), 3.5, BG)
    ctx.restore()
    ctx.set_source_rgba(*WHITE, 0.9); ctx.set_line_width(2.5); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    # wind uplift on the roof: what the brackets resist
    pu = prog(t, s5 + 1.6, 0.5)
    if pu > 0:
        for x in (440, 640):
            arrow(ctx, x, chord_y(x) - 28, x, chord_y(x) - 98, BLUE, p=pu, a=a)
        text(ctx, "UPLIFT", 540, 676, 26, BLUE, alpha=a * clamp(pu * 2 - 1), bold=True, anchor="c", spacing=3)


def inset(ctx, t, tl, a):
    """Roof plan inset: trusses going up along the house, then straps, battens and the roof."""
    if a <= 0: return
    s3, s4, s6, s7, s8 = tl.s(3), tl.s(4), tl.s(6), tl.s(7), tl.s(8)
    ctx.push_group()
    text(ctx, "ROOF PLAN", IX0, IY0 - 18, 22, BLUE, bold=True, spacing=3)
    fill_poly(ctx, rect_pts(IX0, IY0, IX1, IY1)[:4], BG, 0.9)
    polyline(ctx, rect_pts(IX0, IY0, IX1, IY1), 1, WHITE, 2, alpha=0.5, dash=[8, 6])          # eaves line
    polyline(ctx, rect_pts(IX0 + 12, IY0 + 12, IX1 - 12, IY1 - 12), 1, WHITE, 1.6, alpha=0.6)  # walls
    # roof sheets (step 8) sweep along under everything else
    pr = prog(t, s8 + 0.6, 1.6)
    if pr > 0:
        fill_poly(ctx, rect_pts(IX0, IY0, IX0 + (IX1 - IX0) * pr, IY1)[:4], BLUE, 0.22)
    # trusses: the first (step 3) then the rest one by one (step 4)
    for i, x in enumerate(ITR):
        k = prog(t, s3 + 0.3, 0.5) if i == 0 else prog(t, s4 + 0.2 + (i - 1) * 0.17, 0.3)
        if k <= 0: continue
        c = tl.col(3, t) if i == 0 else tl.col(4, t)
        polyline(ctx, [(x, IY0 + 2), (x, IY0 + 2 + (IY1 - IY0 - 4) * k)], 1, c, 3)
    polyline(ctx, [(IX0, IRIDGE), (IX1, IRIDGE)], prog(t, s3 + 0.3, 0.6), WHITE, 1.6, alpha=0.6)
    # temporary braces on the first truss (step 3), temporary battens (step 4)
    pb = prog(t, s3 + 0.9, 0.5) * gone(t, s7, 0.5)
    for y in (IY0 + 40, IY1 - 40):
        polyline(ctx, [(ITR[0], y), (IX0 - 22, y - 26)], pb, ORANGE, 2.5, dash=[6, 5])
    pt = prog(t, s4 + 2.4, 0.6) * gone(t, s7, 0.5)
    for y in (IY0 + 40, IY1 - 40):
        polyline(ctx, [(ITR[0], y), (ITR[-1], y)], pt, tl.col(4, t), 2, dash=[6, 5])
    # strap bracing: an X in each half of each roof plane (step 6)
    c6 = tl.col(6, t); xm = (ITR[0] + ITR[-1]) / 2
    for j, (ya, yb) in enumerate(((IY0 + 12, IRIDGE), (IRIDGE, IY1 - 12))):
        for h, (xa, xb) in enumerate(((ITR[0], xm), (xm, ITR[-1]))):
            k0 = s6 + 0.3 + (j * 2 + h) * 0.25
            polyline(ctx, [(xa, ya), (xb, yb)], prog(t, k0, 0.5), c6, 2.5)
            polyline(ctx, [(xa, yb), (xb, ya)], prog(t, k0 + 0.12, 0.5), c6, 2.5)
    # battens (step 7)
    c7 = tl.col(7, t)
    rows = [y for y in range(IY0 + 10, IY1 - 4, 12) if abs(y - IRIDGE) > 5]
    for i, y in enumerate(rows):
        polyline(ctx, [(IX0 + 4, y), (IX1 - 4, y)], prog(t, s7 + 0.3 + i * 0.08, 0.5), c7, 1.4, alpha=0.8)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    # caption under the inset: what's happening in plan
    cap = [(s3 + 0.6, s4, "FIRST TRUSS + BRACES"), (s4 + 0.4, tl.s(5), "SPACING PER LAYOUT"),
           (s6 + 0.4, s7, "STRAPS CROSS THE ROOF"), (s7 + 0.4, s8, "BATTENS ACROSS"),
           (s8 + 0.6, tl.res0, "SHEETS OR TILES ON")]
    for t0, t1, s in cap:
        k = clamp((t - t0) / 0.3) * gone(t, t1 - 0.1, 0.3) * a
        if k > 0:
            text(ctx, s, IX1, IY1 + 34, 22, WHITE, alpha=0.9 * k, bold=True, anchor="r", spacing=1)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    # context: slab and wall frames, drawn on at the start
    walls(ctx, WHITE, prog(t, s1 + 0.2, 1.0))

    # the truss: made in the factory (up high), lifted, lowered onto the plates
    c = tl.col(3, t) if t >= s3 else tl.col(2, t) if t >= s2 else tl.col(1, t)
    low = prog(t, s2 + 0.5, 1.8)
    sway = 6 * math.sin((t - s2) * 3.2) * (1 - low) if t > s2 else 0
    dy = FACTORY * (1 - low)
    ctx.save(); ctx.translate(sway, 0)
    truss(ctx, t, tl, c, dy=dy, p=prog(t, s1, 1.8), plates=prog(t, s1 + 1.8, 0.8))
    ctx.restore()
    rope = prog(t, s2, 0.4) * gone(t, s2 + 2.6, 0.4)
    if rope > 0:
        hx, hy = APEX[0] + sway, APEX[1] + dy - 70
        polyline(ctx, [(hx, 400), (hx, hy)], 1, WHITE, 2, alpha=rope)
        for q in (T1, T2):
            polyline(ctx, [(hx, hy), (q[0] + sway, q[1] + dy)], 1, WHITE, 1.6, alpha=0.8 * rope)
        polyline(ctx, [(hx, hy - 16), (hx, hy), (hx - 10, hy + 8), (hx - 18, hy)], 1, WHITE, 3, alpha=rope)

    # step 1 labels (the truss is up high)
    a1 = gone(t, s2)
    label(ctx, clamp((t - s1 - 0.9) / 0.8), c, (720, chord_y(720) + FACTORY), (940, 520), "TOP CHORD", anchor="r", a=a1)
    label(ctx, clamp((t - s1 - 1.3) / 0.8), c, (300, HY + FACTORY + 6), (110, 760), "BOTTOM CHORD", a=a1)
    label(ctx, clamp((t - s1 - 2.0) / 0.8), c, (B2[0] + 11, HY + FACTORY + 8), (940, 760), "NAIL PLATES", anchor="r", a=a1)
    # step 2 labels
    label(ctx, clamp((t - s2 - 0.3) / 0.8), WHITE, (APEX[0], 430), (940, 445), "CRANE", anchor="r", a=gone(t, s3))
    label(ctx, clamp((t - s2 - 1.6) / 0.8), tl.col(2, t), (XL + WT, PL + 8), (240, 1010), "TOP PLATE", a=gone(t, s4))

    # 3 temporary brace to the ground
    c3 = tl.col(3, t)
    pb = prog(t, s3 + 0.4, 0.8) * gone(t, s6, 0.5)
    polyline(ctx, [(330, chord_y(330)), (95, SLAB_B)], pb, ORANGE, 3, dash=[12, 8])
    label(ctx, clamp((t - s3 - 0.9) / 0.8), c3, (330, chord_y(330) - 6), (110, 760), "TEMP BRACE", a=gone(t, s5))

    # roof plan inset (steps 3-8)
    inset(ctx, t, tl, prog(t, s3 + 0.1, 0.4) * gone(t, r0, 0.5))

    # 4 temporary battens seen in section: small blocks on the top chords
    c4 = tl.col(4, t)
    pt = prog(t, s4 + 2.4, 0.5) * gone(t, s7, 0.5)
    if pt > 0:
        for x in (290, 790):
            y = chord_y(x) - 12
            fill_poly(ctx, rect_pts(x - 7, y - 6, x + 7, y + 6)[:4], c4, 0.8 * pt)

    # 5 tie-down brackets at both heels + the detail bubble
    c5 = tl.col(5, t)
    pk = prog(t, s5 + 0.9, 0.6)
    if pk > 0:
        for x in (XL + 15, XR - 23):
            fill_poly(ctx, rect_pts(x, HY - 8, x + 8, HY - 8 + 30 * pk)[:4], c5, 0.95)
    ba = prog(t, s5 + 0.1, 0.4) * gone(t, s6, 0.5)
    bubble(ctx, t, tl, ba)
    label(ctx, clamp((t - s5 - 1.0) / 0.8), c5, (255 + 15 * 3.2 - 12 * 3.2 + 12, 615 - 6 * 3.2), (110, 445),
          "TIE-DOWN BRACKET", a=ba)

    # 6 strap bracing over the top chords
    c6 = tl.col(6, t)
    ps = prog(t, s6 + 0.2, 1.2)
    if ps > 0:
        polyline(ctx, [(XL, chord_y(XL) - 9), (APEX[0], APEX[1] - 9), (XR, chord_y(XR) - 9)], ps, c6, 3.5)
    label(ctx, clamp((t - s6 - 0.8) / 0.8), c6, (330, chord_y(330) - 9), (110, 760), "STRAP BRACING", a=gone(t, s8))

    # 7 roof battens along both top chords
    c7 = tl.col(7, t)
    bx = [x for x in range(140, 920, 48) if abs(x - APEX[0]) > 16]
    for i, x in enumerate(bx):
        k = prog(t, s7 + 0.2 + i * 0.07, 0.3)
        if k <= 0: continue
        y = chord_y(x) - 13
        fill_poly(ctx, rect_pts(x - 6, y - 6, x + 6, y + 6)[:4], BG, 1)
        polyline(ctx, rect_pts(x - 6, y - 6, x + 6, y + 6), k, c7, 2)
    label(ctx, clamp((t - s7 - 1.2) / 0.8), c7, (796, chord_y(796) - 19), (940, 760), "ROOF BATTENS", anchor="r",
          a=gone(t, s8))

    # 8 fascia + gutters, then the roof sheets (corrugated line over the battens)
    c8 = tl.col(8, t)
    pf = prog(t, s8, 0.6)
    if pf > 0:
        for sgn, (ex, ey) in ((-1, EAVE_L), (1, EAVE_R)):
            polyline(ctx, rect_pts(ex - 4, ey - 12, ex + 4, ey + 20), pf, c8, 2.5)
            gx = ex + sgn * 6
            polyline(ctx, [(gx, ey - 2), (gx, ey + 22), (gx + sgn * 22, ey + 22), (gx + sgn * 26, ey - 4)], pf, c8, 2.5)
    pr = prog(t, s8 + 0.6, 1.6)
    if pr > 0:
        pts = []
        for i in range(0, 201):
            x = EAVE_L[0] + (EAVE_R[0] - EAVE_L[0]) * i / 200
            pts.append((x, chord_y(x) - 24 + 3 * math.sin(x / 5.0)))
        polyline(ctx, pts, pr, c8, 2.5)
        polyline(ctx, [(EAVE_L[0], chord_y(EAVE_L[0]) - 19), APEX[:1] + (APEX[1] - 19,),
                       (EAVE_R[0], chord_y(EAVE_R[0]) - 19)], pr, c8, 1.4, alpha=0.6, dash=[4, 4])   # sarking
    label(ctx, clamp((t - s8 - 1.0) / 0.8), c8, (700, chord_y(700) - 26), (940, 700), "ROOF SHEETS", anchor="r",
          a=gone(t, r0))
    label(ctx, clamp((t - s8 - 0.3) / 0.8), c8, (EAVE_L[0] - 12, EAVE_L[1] + 20), (240, 1060), "FASCIA + GUTTER",
          a=gone(t, r0))

    # result: wind lifts the roof, the tie-downs carry it down through the walls to the slab
    pu = prog(t, r0, 0.6)
    for x in (300, 780):
        arrow(ctx, x, chord_y(x) - 40, x, chord_y(x) - 120, BLUE, p=pu)
    if pu > 0:
        text(ctx, "WIND UPLIFT", 540, 600, 26, BLUE, alpha=clamp(pu * 2 - 1), bold=True, anchor="c", spacing=3)
    pd = prog(t, r0 + 0.7, 0.8)
    for x in (XL + 34, XR - 34):
        arrow(ctx, x, PL + 20, x, SLAB_T - 14, BLUE, p=pd)
    if pd > 0:
        text(ctx, "TIED DOWN", 540, 1050, 30, BLUE, alpha=clamp(pd * 2 - 1), bold=True, anchor="c", spacing=4)
    dim_h(ctx, 1120, XL, XR, "SPAN", prog(t, r0 + 1.3, 0.6))


# ---------------------------------------------------------------- 3D model (mm): a house frame with the roof going on
def model3d():
    from engine.three_d import box, member, member3d
    P = []; o = 0
    SP, LZ, WH = 9000, 11700, 2400              # span, house length, wall height
    FL = 150                                     # slab top
    TP = FL + WH                                 # top of the top plates
    RISE = 4500 * math.tan(math.radians(22.5))
    OHm = 600
    P.append(box(-1800, SP + 1800, -300, 0, -1800, LZ + 1800, o, "ground")); P[-1].base = True; o += 1
    P.append(box(-100, SP + 100, 0, FL, -100, LZ + 100, o, "concrete")); o += 1
    # wall frames: studs at 600 centres on the long walls, plates, and the two end walls
    for x0 in (0, SP - 90):
        P.append(box(x0, x0 + 90, FL, FL + 45, 0, LZ, o)); P.append(box(x0, x0 + 90, TP - 90, TP, 0, LZ, o))
        for z in range(0, LZ, 600):
            P.append(box(x0, x0 + 90, FL + 45, TP - 90, z, z + 45, o))
    for z0 in (0, LZ - 90):
        P.append(box(90, SP - 90, FL, FL + 45, z0, z0 + 90, o)); P.append(box(90, SP - 90, TP - 90, TP, z0, z0 + 90, o))
        for x in range(600, SP - 300, 600):
            P.append(box(x, x + 45, FL + 45, TP - 90, z0, z0 + 90, o))
    o += 1
    # trusses
    yb = TP + 45
    apex = (SP / 2, yb + RISE)
    eL, eR = (-OHm, yb - OHm * RISE / 4500), (SP + OHm, yb - OHm * RISE / 4500)
    q = lambda x: (x, yb + (min(x, SP - x)) * RISE / 4500)
    zs = [i * 900 for i in range(13)] + [LZ - 45]
    for z in zs:
        z0, z1 = z, z + 45
        P.append(member((0, yb), (SP, yb), 90, z0, z1, o))
        P.append(member(eL, apex, 120, z0, z1, o)); P.append(member(eR, apex, 120, z0, z1, o))
        b1, b2, t1, t2 = (SP / 3, yb), (2 * SP / 3, yb), q(SP / 4), q(3 * SP / 4)
        for a, b in ((b1, t1), (b1, apex), (b2, apex), (b2, t2)):
            P.append(member(a, b, 70, z0 + 5, z1 - 5, o))
        o += 1
    # strap bracing: an X on each roof plane (thin steel straps just above the top chords)
    lift = 70
    for side in (0, 1):
        x_e = 0 if side == 0 else SP
        lo = (x_e, yb + lift); hi = (SP / 2, yb + RISE + lift)
        for za, zb in ((0, LZ / 2), (LZ / 2, LZ)):
            P.append(member3d((lo[0], lo[1], za), (hi[0], hi[1], zb), 60, 8, o, "steel"))
            P.append(member3d((lo[0], lo[1], zb), (hi[0], hi[1], za), 60, 8, o, "steel"))
    o += 1
    # roof battens across the top chords
    for side in (0, 1):
        for k in range(1, 7):
            u = k / 6.6
            x = (SP / 2) * u if side == 0 else SP - (SP / 2) * u
            y = yb + RISE * u + 70
            P.append(box(x - 25, x + 25, y, y + 40, -100, LZ + 100, o))
    o += 1
    # fascia, then roof sheets over the near half (the rest left open to show the frame)
    for x in (eL[0], eR[0]):
        P.append(box(x - 30, x + 30, eL[1] - 120, eL[1] + 80, -100, LZ + 100, o))
    o += 1
    ZR = 5400
    for e in (eL, eR):
        P.append(member((e[0], e[1] + 140), (apex[0], apex[1] + 140), 30, ZR, LZ + 100, o, "steel"))
    o += 1
    cfg = {"target": (SP / 2, 2300, LZ / 2), "yaw": 36, "pitch": 20, "dist": 30000, "scale": 1.4,
           "cy_hook": 1090, "cy_result": 830, "cy_cover": 1000, "cover_scale": 0.95}
    return P, cfg
