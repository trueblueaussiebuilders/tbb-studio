"""019 Transfer beam (structural)."""
import math
from engine.blueprint import *

META = {
    "category": "structural",
    "title": "TRANSFER BEAM",
    "subtitle": "STRUCTURAL  //  TYPICAL AU METHOD",
    "dwg": "019",
    "drawing": "TRANSFER BEAM",
    "section_label": "ELEVATION ALONG THE BEAM  (NTS)",
    "hook": ["THESE COLUMNS", "DON'T REACH", "THE GROUND."],
    "hook_sub": "HOW A TRANSFER BEAM IS BUILT",
    "cover": ["THESE COLUMNS", "STOP IN", "MID-AIR."],
    "hook_start": 0.55,
    "xray": {"after_step": 5, "upto": 3, "hot": [3]},     # bars + ligatures in, the concrete still a ghost
    "steps": [
        ("WIDE GRID BELOW", "The columns below are spaced wide apart to leave an open space."),
        ("HEAVY PROPS", "Props stand on the floor below. They carry the wet concrete."),
        ("DEEP FORMWORK", "The beam is formed much deeper than a normal floor beam."),
        ("HEAVY BOTTOM BARS", "Big bars go in the bottom of the beam, often in layers."),
        ("LIGATURES", "Closed ligatures wrap the bars. They sit closer near the supports."),
        ("STARTER BARS", "Bars for the columns above are cast in where they will land."),
        ("POUR + VIBRATE", "Concrete is poured and vibrated so it fills around the steel."),
        ("COLUMNS ABOVE", "Upper columns go up on the starters. Props stay until it's allowed."),
    ],
    "result": "The columns above stop on the beam. It carries their load sideways to the columns below.",
}

NARRATION = {
    "hook": "These columns don't reach the ground. A huge beam holds them up.",
    "steps": [
        "On the ground floor, the columns are spaced wide apart. That leaves an open space, like a lobby or a car park entry.",
        "Heavy props go up first. They stand on the floor below and carry the weight of the wet concrete.",
        "Then the formwork. A transfer beam is much deeper than a normal floor beam, so the forms are big and strong.",
        "Large bars go in the bottom of the beam, often in more than one layer. This is where the beam is in tension.",
        "Closed ligatures wrap around the bars. They're placed closer together near the supports, where the shear is highest.",
        "Starter bars for the columns above are cast in, right where those columns will land on the beam.",
        "The concrete is poured, and vibrated as it goes, so it fills every gap around the steel.",
        "The upper columns are built on the starter bars. The props stay in until the engineer says they can come out.",
    ],
    "result": "The columns above stop on the beam. It carries their load sideways, to the columns below, and keeps the space underneath open.",
    "end": "Follow for more.",
}

CAPTION = """These columns don't reach the ground 👇 How a transfer beam is built.

Typical: a transfer beam (or transfer slab) is used where columns or walls in the floors above don't line up with the column grid below, for example to open up a lobby, shopfront or car park entry under an apartment building. The level below is propped with heavy props or shoring, often back-propped through more than one floor, because a deep beam is very heavy while it's wet. The formwork is built for the full depth of the beam. The reinforcement is dense: large bottom bars (often in layers), top bars, and closed ligatures that are spaced closer together near the supports, where the shear is highest. Starter bars for the columns or walls above are cast in where they land. The concrete is poured and thoroughly vibrated so it fills around the congested steel, then cured. The props stay in until the engineer allows them to be removed.
Beam size, reinforcement, concrete strength and the propping sequence all come from the structural design.
Typical only. Your engineer's design governs.

#transferbeam #structuralengineering #concretestructures #reinforcedconcrete #construction #buildingconstruction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
GL, GSB = 1110, 1135                  # ground slab top / bottom
EARTH_B = 1185
BX0, BX1 = 120, 960                   # transfer beam ends
BT, BB = 640, 780                     # beam top / soffit
SLT = 28                              # transfer level slab thickness (shown past the beam ends)
LOW = [(150, 200), (880, 930)]        # columns below (wide grid)
UP = [380, 700]                       # column centres above (land on the beam)
UW = 22                               # half width of an upper column
UFT, UFB = 455, 477                   # floor above: top / bottom
PROPS = [270, 390, 510, 630, 750]
LIGS = sorted(set([x for x in range(BX0 + 50, 340, 16)] + [x for x in range(340, 740, 34)] +
                  [x for x in range(740, BX1 - 40, 16)]))
BEAM_CONC = concrete_points(191, BX0, BT, BX1, BB, 420, inside=lambda x, y: BX0 + 6 < x < BX1 - 6 and BT + 6 < y < BB - 6)
COL_CONC = concrete_points(192, 150, BB, 930, GL, 260,
                           inside=lambda x, y: any(a + 5 < x < b - 5 for a, b in LOW))
GSLAB_CONC = concrete_points(193, 70, GL, 1010, GSB, 160)


def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def arrow(ctx, x0, y0, x1, y1, col, p=1.0, a=1.0, head=12, width=3):
    if p <= 0: return
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    polyline(ctx, [(x0, y0), (xe, ye)], 1, col, width, alpha=a)
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    polyline(ctx, [(xe - ux * head - uy * head * 0.8, ye - uy * head + ux * head * 0.8), (xe, ye),
                   (xe - ux * head + uy * head * 0.8, ye - uy * head - ux * head * 0.8)], 1, col, width, alpha=a)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    # ---- 1 ground slab, earth, the wide columns below; ghost of what lands on top
    c1 = tl.col(1, t)
    pg = prog(t, s1, 0.8)
    if pg > 0:
        polyline(ctx, [(70, GL), (1010, GL)], pg, WHITE, 3)
        polyline(ctx, [(70, GSB), (1010, GSB)], pg, WHITE, 2, alpha=0.6)
        draw_concrete(ctx, GSLAB_CONC, WHITE, 0.4 * pg)
        earth_hatch(ctx, 70, GSB, 1010, EARTH_B, WHITE, 0.12, reveal=pg)
    for j, (a, b) in enumerate(LOW):
        k = prog(t, s1 + 0.3 + j * 0.3, 0.9)
        if k <= 0: continue
        yt = GL - (GL - BB) * k
        fill_poly(ctx, rect_pts(a, yt, b, GL)[:4], BG, 1)
        polyline(ctx, rect_pts(a, yt, b, GL), 1, c1, 3)
        ctx.save(); ctx.rectangle(a, yt, b - a, GL - yt); ctx.clip()
        draw_concrete(ctx, COL_CONC, c1, 0.6); ctx.restore()
    pd = prog(t, s1 + 1.3, 0.8) * gone(t, s2 + 0.2)
    if pd > 0:
        dim_h(ctx, 1060, LOW[0][1], LOW[1][0], "WIDE OPEN SPAN", pd)
    # ghost: where the beam and the columns above will be
    kg = prog(t, s1 + 1.8, 0.8) * gone(t, s3 + 0.4)
    if kg > 0:
        polyline(ctx, rect_pts(BX0, BT, BX1, BB), 1, BLUE, 2, alpha=0.55 * kg, dash=[10, 8])
        for x in UP:
            polyline(ctx, rect_pts(x - UW, UFB, x + UW, BT), 1, BLUE, 2, alpha=0.55 * kg, dash=[10, 8])
    label(ctx, clamp((t - s1 - 2.0) / 0.8), BLUE, (UP[1], UFB + 40), (UP[1] - 40, 440), "COLUMNS ABOVE", anchor="r",
          a=gone(t, s2 + 0.3))

    # ---- 2 props from the floor below up to the soffit, head bearer across the top
    c2 = tl.col(2, t)
    ap = gone(t, s8 + 2.2, 0.8)                  # props come out late in step 8
    if ap > 0:
        ctx.push_group()
        for i, x in enumerate(PROPS):
            k = prog(t, s2 + 0.2 + i * 0.15, 0.6)
            if k <= 0: continue
            yt = GL - (GL - BB - 22) * k
            polyline(ctx, [(x - 5, GL), (x - 5, yt)], 1, c2, 2.5)
            polyline(ctx, [(x + 5, GL), (x + 5, yt)], 1, c2, 2.5)
            polyline(ctx, [(x - 16, GL - 2), (x + 16, GL - 2)], 1, c2, 3)
            if k >= 1:
                polyline(ctx, [(x - 16, BB + 20), (x + 16, BB + 20)], 1, c2, 3)
                for yy in range(int(BB + 40), GL - 20, 46):
                    dot(ctx, x, yy, 2.5, c2, 0.8)
        kb = prog(t, s2 + 1.2, 0.6)
        polyline(ctx, [(BX0 + 40, BB + 14), (BX1 - 40, BB + 14)], kb, c2, 5)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(ap)
    label(ctx, clamp((t - s2 - 0.9) / 0.8), c2, (PROPS[1] + 5, 900), (PROPS[1] + 70, 930), "HEAVY PROPS",
          a=gone(t, s3 + 0.4))
    label(ctx, clamp((t - s2 - 1.9) / 0.8), c2, (PROPS[3], GL - 4), (PROPS[3] - 40, 1060), "ON THE FLOOR BELOW", anchor="r",
          a=gone(t, s3 + 0.4))

    # ---- 3 formwork: soffit + side form outline (the full depth)
    c3 = tl.col(3, t)
    af = gone(t, s8 + 2.2, 0.8)
    kf = prog(t, s3 + 0.2, 0.9)
    if kf > 0 and af > 0:
        ctx.push_group()
        polyline(ctx, [(BX0 - 10, BB + 8), (BX1 + 10, BB + 8)], kf, c3, 5)
        polyline(ctx, [(BX0 - 10, BB + 8), (BX0 - 10, BT - 10), (BX1 + 10, BT - 10), (BX1 + 10, BB + 8)],
                 prog(t, s3 + 0.8, 1.0), c3, 2.5, dash=[12, 6])
        ctx.pop_group_to_source(); ctx.paint_with_alpha(af * (1 - 0.6 * prog(t, s7 + 0.2, 1.5)))
    kdim = prog(t, s3 + 1.6, 0.6) * gone(t, s4 + 0.3)
    if kdim > 0:
        dim_v(ctx, BX1 - 60, BT, BB, "DEEP", kdim)
    label(ctx, clamp((t - s3 - 0.9) / 0.8), c3, (300, BT - 10), (300, 560), "DEEP BEAM FORMWORK", a=gone(t, s4 + 0.3))
    label(ctx, clamp((t - s3 - 1.8) / 0.8), c3, (640, BB + 8), (640, 960), "SOFFIT FORM", a=gone(t, s4 + 0.3))

    # ---- 4 bottom bars (two layers), top bars
    c4 = tl.col(4, t)
    rows = [(BB - 18, s4 + 0.2, 4.5), (BB - 34, s4 + 0.8, 4.5), (BT + 18, s4 + 1.6, 3)]
    for y, t0, w in rows:
        k = prog(t, t0, 0.8)
        if k <= 0: continue
        col = c4 if t < s7 else WHITE
        polyline(ctx, [(BX0 + 14, y), (BX1 - 14, y)], k, col, w)
    label(ctx, clamp((t - s4 - 0.9) / 0.8), c4, (440, BB - 18), (440, 960), "HEAVY BOTTOM BARS", a=gone(t, s5 + 0.3))
    label(ctx, clamp((t - s4 - 2.0) / 0.8), c4, (660, BT + 18), (660, 560), "TOP BARS", a=gone(t, s5 + 0.3))

    # ---- 5 ligatures: closer near the supports
    c5 = tl.col(5, t)
    for i, x in enumerate(LIGS):
        k = prog(t, s5 + 0.2 + 1.4 * (x - BX0) / (BX1 - BX0), 0.25)
        if k <= 0: continue
        col = c5 if t < s7 else WHITE
        polyline(ctx, [(x, BB - 10), (x, BB - 10 - (BB - BT - 20) * k)], 1, col, 1.8, alpha=0.9)
    label(ctx, clamp((t - s5 - 1.0) / 0.8), c5, (230, BT + 8), (230, 470), "CLOSER NEAR SUPPORTS", a=gone(t, s6 + 0.3))
    label(ctx, clamp((t - s5 - 1.8) / 0.8), c5, (540, BT + 40), (540, 560), "WIDER MID-SPAN", a=gone(t, s6 + 0.3))

    # ---- 6 starter bars for the columns above
    c6 = tl.col(6, t)
    for j, x in enumerate(UP):
        k = prog(t, s6 + 0.2 + j * 0.5, 0.6)
        if k <= 0: continue
        for dx in (-12, 12):
            y0 = BB - 44
            polyline(ctx, [(x + dx, y0), (x + dx, y0 - (y0 - (BT - 90)) * k)], 1, c6 if t < s8 else WHITE, 3.5)
        polyline(ctx, [(x - 24, BB - 44), (x + 24, BB - 44)], k, c6 if t < s8 else WHITE, 3.5)
    label(ctx, clamp((t - s6 - 1.0) / 0.8), c6, (UP[1] + 12, BT - 80), (640, 470), "COLUMN STARTER BARS", anchor="r",
          a=gone(t, s7 + 0.3))

    # ---- 7 pour (left to right) with a poker vibrator at the front
    c7 = tl.col(7, t)
    kp = prog(t, s7 + 0.2, 2.2)
    if kp > 0:
        xe = BX0 + (BX1 - BX0) * kp
        ctx.save(); ctx.rectangle(BX0 - 50, BT - 2, xe - BX0 + 50, BB - BT + 4); ctx.clip()
        fill_poly(ctx, rect_pts(BX0, BT, BX1, BB)[:4], BLUE, 0.10)
        draw_concrete(ctx, BEAM_CONC, c7 if t < s8 else WHITE, 0.7)
        ctx.restore()
        cs = c7 if t < s8 else WHITE
        polyline(ctx, [(BX0, BT), (BX0, BB), (BX1, BB), (BX1, BT), (BX0, BT)], kp, cs, 3)
        # slab at the transfer level, shown past the beam ends
        polyline(ctx, [(70, BT), (BX0, BT)], kp, cs, 3); polyline(ctx, [(70, BT + SLT), (BX0, BT + SLT)], kp, cs, 2)
        kp2 = prog(t, s7 + 2.0, 0.5)
        polyline(ctx, [(BX1, BT), (1010, BT)], kp2, cs, 3); polyline(ctx, [(BX1, BT + SLT), (1010, BT + SLT)], kp2, cs, 2)
        if kp < 1:
            vx = xe - 30
            vy = BB - 30 - 25 * (0.5 + 0.5 * math.sin(t * 9))
            polyline(ctx, [(vx, 520), (vx, vy)], 1, ORANGE, 3)
            polyline(ctx, [(vx - 4, vy), (vx + 4, vy), (vx + 4, vy - 40), (vx - 4, vy - 40), (vx - 4, vy)], 1, ORANGE, 3)
            for d in (-1, 1):
                polyline(ctx, [(vx + d * 10, vy - 10), (vx + d * 18, vy - 4)], 1, ORANGE, 2)
    vx = BX0 + (BX1 - BX0) * clamp(kp) - 30
    label(ctx, clamp((t - s7 - 0.6) / 0.8), ORANGE, (vx, 540), (vx + 60 if vx < 600 else vx - 60, 470),
          "POKER VIBRATOR", anchor="l" if vx < 600 else "r", a=gone(t, s7 + 2.3, 0.3))
    label(ctx, clamp((t - s7 - 1.2) / 0.8), c7, (440, BB - 50), (440, 960), "CONCRETE", a=gone(t, s8 + 0.3))

    # ---- 8 columns above rise on the starters, the floor above, more floors (dashed)
    c8 = tl.col(8, t)
    for j, x in enumerate(UP):
        k = prog(t, s8 + 0.2 + j * 0.4, 0.9)
        if k <= 0: continue
        yt = BT - (BT - UFB) * k
        fill_poly(ctx, rect_pts(x - UW, yt, x + UW, BT)[:4], BG, 1)
        polyline(ctx, rect_pts(x - UW, yt, x + UW, BT), 1, c8, 3)
    kfl = prog(t, s8 + 1.2, 0.9)
    if kfl > 0:
        polyline(ctx, rect_pts(70, UFT, 1010, UFB), kfl, c8, 3)
        for x in UP:
            polyline(ctx, [(x - UW, UFT), (x - UW, 415)], kfl, WHITE, 2, alpha=0.45, dash=[10, 8])
            polyline(ctx, [(x + UW, UFT), (x + UW, 415)], kfl, WHITE, 2, alpha=0.45, dash=[10, 8])
        text(ctx, "FLOORS ABOVE", 540, 433, 26, WHITE, alpha=0.7 * kfl, bold=True, anchor="c", spacing=3)
    label(ctx, clamp((t - s8 - 0.9) / 0.8), c8, (UP[1] + UW, 560), (UP[1] + 60, 560), "UPPER COLUMN", a=gone(t, r0))
    label(ctx, clamp((t - s8 - 2.4) / 0.8), WHITE, (PROPS[2], 1000), (PROPS[2] + 60, 1000), "PROPS OUT WHEN ALLOWED",
          a=gone(t, r0))

    # ---- result: load path from the columns above, sideways through the beam, down the columns below
    pr = prog(t, r0 + 0.2, 0.6)
    if pr > 0:
        for x in UP:
            arrow(ctx, x, 500, x, BT - 8, ORANGE, p=pr, head=12, width=4)
    ps = prog(t, r0 + 0.8, 0.7)
    if ps > 0:
        arrow(ctx, UP[0] - 10, BT + 60, LOW[0][1] + 20, BT + 60, ORANGE, p=ps, head=12, width=4)
        arrow(ctx, UP[1] + 10, BT + 60, LOW[1][0] - 20, BT + 60, ORANGE, p=ps, head=12, width=4)
    pdn = prog(t, r0 + 1.4, 0.6)
    if pdn > 0:
        for a, b in LOW:
            arrow(ctx, (a + b) / 2, BB + 30, (a + b) / 2, GL - 20, ORANGE, p=pdn, head=12, width=4)
    pt = prog(t, r0 + 1.6, 0.5)
    if pt > 0:
        text(ctx, "LOAD GOES SIDEWAYS", 540, 960, 34, ORANGE, alpha=pt, bold=True, anchor="c", spacing=1)
        text(ctx, "OPEN SPACE BELOW", 540, 1030, 34, BLUE, alpha=pt, bold=True, anchor="c", spacing=2)


# ---------------------------------------------------------------- 3D model (mm): two frames of a transfer level
def model3d():
    from engine.three_d import box, member3d
    P = []
    g = box(-3500, 15500, -300, 0, -7500, 7500, 0, "ground"); g.base = True; P.append(g)
    SP = 12000                                  # span between the columns below
    ZS = (-4000, 4000)                          # two grid lines
    YS, YT = 4200, 6000                         # soffit / top of the transfer beam
    for z in ZS:
        for x in (0, SP):                       # 1 columns below (on from frame 0)
            P.append(box(x - 400, x + 400, 0, YS, z - 400, z + 400, 1, "concrete"))
    for z in ZS:                                # 2 bottom bars (2 layers) + top bars (props + forms left out: they come out)
        for y in (YS + 80, YS + 200):
            for dz in (-300, -100, 100, 300):
                P.append(box(-450, SP + 450, y, y + 50, z + dz - 25, z + dz + 25, 2, "steel"))
        for dz in (-300, 300):
            P.append(box(-450, SP + 450, YT - 130, YT - 90, z + dz - 20, z + dz + 20, 2, "steel"))
    for z in ZS:                                # 3 ligatures: closer near the supports
        xs = list(range(-300, 3000, 300)) + list(range(3000, SP - 3000, 600)) + list(range(SP - 3000, SP + 400, 300))
        for x in xs:
            P.append(box(x - 20, x + 20, YS + 50, YT - 60, z - 360, z + 360, 3, "steel"))
    for z in ZS:                                # 4 starter bars where the columns above land
        for x in (4000, 8000):
            for dx in (-150, 150):
                for dz in (-150, 150):
                    P.append(box(x + dx - 25, x + dx + 25, YS + 300, YT + 900, z + dz - 25, z + dz + 25, 4, "steel"))
    for z in ZS:                                # 5 the beam
        P.append(box(-450, SP + 450, YS, YT, z - 450, z + 450, 5, "concrete"))
    for z in ZS:                                # 6 columns above + the floor above
        for x in (4000, 8000):
            P.append(box(x - 250, x + 250, YT, YT + 3000, z - 250, z + 250, 6, "concrete"))
    P.append(box(2500, 9500, YT + 3000, YT + 3250, -5000, 5000, 6, "concrete"))
    cfg = {"target": (6000, 4300, 0), "yaw": -45, "pitch": 18, "dist": 42000, "scale": 1.7,
           "cy_hook": 1060, "cy_result": 820, "cy_cover": 960, "cover_scale": 0.85}
    return P, cfg
