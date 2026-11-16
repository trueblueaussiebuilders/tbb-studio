"""010 Precast box culvert under a road (infrastructure)."""
import math
from engine.blueprint import *

META = {
    "category": "infrastructure",
    "title": "BOX CULVERT",
    "subtitle": "INFRASTRUCTURE  //  TYPICAL AU METHOD",
    "dwg": "010",
    "drawing": "BOX CULVERT",
    "section_label": "SECTION ALONG CULVERT  (NTS)",
    "hook": ["THE CREEK UNDER", "THIS ROAD RUNS", "THROUGH A BOX."],
    "hook_sub": "HOW A BOX CULVERT GOES IN",
    "cover": ["HOW A CREEK", "GETS UNDER", "THE ROAD."],
    "steps": [
        ("DIVERT & DIG", "The creek is diverted around the site. The ground is dug out to the design level."),
        ("BEDDING", "Crushed rock is spread, compacted and screeded to the exact grade."),
        ("UNITS IN", "Precast box units are craned in one at a time, starting at the downstream end."),
        ("SEAL JOINTS", "Each joint is butted up tight, then sealed and wrapped so soil can't wash in."),
        ("HEADWALLS & APRONS", "Headwalls and wing walls hold the fill back. Aprons and rock stop scour."),
        ("BACKFILL", "Select fill goes in thin layers, compacted evenly on both sides of the box."),
        ("EMBANKMENT", "The fill keeps rising in compacted layers until the box has enough cover."),
        ("ROAD ON TOP", "Pavement layers, a sealed surface, then the guard fence."),
    ],
    "result": "A road over the creek with no bridge. The water flows straight through the box.",
}

NARRATION = {
    "hook": "Many creeks pass under Australian roads through a concrete box. Here's how a box culvert goes in.",
    "steps": [
        "First, the creek is diverted around the work area. Then the ground is dug out to the design level.",
        "Crushed rock bedding is spread and compacted. Then it's screeded to the exact grade.",
        "Precast box units are craned in one at a time. Laying starts at the downstream end.",
        "Each joint is butted up tight. Then it's sealed and wrapped, so soil can't wash in.",
        "Headwalls and wing walls go on each end to hold the fill back. Concrete aprons and rock protection stop the water scouring the bed.",
        "Select fill goes in next. It's placed in thin layers, and compacted evenly on both sides of the box.",
        "The embankment keeps rising in compacted layers, until the box has enough cover.",
        "Finally, the pavement layers and the sealed surface go on. Then the guard fence.",
    ],
    "result": "A road over the creek, with no bridge. The water flows straight through the box.",
    "end": "Follow for more.",
}

CAPTION = """Ever wondered how a creek gets under a country road? 👇 How a precast box culvert goes in.

Typical: creek diverted, foundation excavated, compacted crushed rock bedding screeded to grade, precast box culvert units laid from the downstream end, joints sealed and wrapped, headwalls, wing walls and aprons at each end with rock protection against scour, then select backfill placed in thin compacted layers, evenly on both sides, before the embankment and pavement go on.
Unit size, bedding, cover and backfill all depend on the design and the traffic loads.
Typical only. Your engineer's design governs.

#boxculvert #civilengineering #infrastructure #precastconcrete #roadconstruction #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
GND = 1004                          # natural creek bed
EXC = 1040                          # excavation level
TX0, TX1 = 160, 920                 # excavation edges
BED = 1020                          # top of bedding = underside of units
UX0, UW, NU = 240, 120, 5           # units
UX1 = UX0 + UW * NU
TOPO, TOPI, INV = 900, 916, 1004    # unit top outside, top inside (soffit), invert
HW_TOP = 840                        # headwall top
HW = 28                             # headwall thickness
EMB_TOP = 620                       # top of embankment (subgrade)
BAT = 180                           # batter run (px)
PAVE = 598                          # top of pavement
JOINTS = [UX0 + UW * k for k in range(1, NU)]
EMB = [(UX0 - HW, HW_TOP), (UX0 - HW + BAT, EMB_TOP), (UX1 + HW - BAT, EMB_TOP), (UX1 + HW, HW_TOP)]
ROCKS = [(926 + (k % 5) * 13 + (k // 5) * 6, 996 - (k // 5) * 11, 7 - (k // 5)) for k in range(13)]

CONC_TOP = concrete_points(101, UX0, TOPO, UX1, TOPI, 120, lambda x, y: TOPO + 3 < y < TOPI - 3)
CONC_BOT = concrete_points(102, UX0, INV, UX1, BED, 120, lambda x, y: INV + 3 < y < BED - 3)
CONC_APR = concrete_points(103, TX0, INV, TX1, BED, 70,
                           lambda x, y: INV + 3 < y < BED - 3 and (x < UX0 - 3 or x > UX1 + 3))
CONC_HW = concrete_points(104, UX0 - HW, HW_TOP, UX1 + HW, TOPO, 60,
                          lambda x, y: (UX0 - HW + 3 < x < UX0 - 3 or UX1 + 3 < x < UX1 + HW - 3) and HW_TOP + 3 < y < TOPO - 3)
BED_GRAVEL = gravel(105, TX0 + 4, BED + 4, TX1 - 4, EXC - 4, 150)
PAVE_GRAVEL = gravel(106, UX0 - HW + BAT + 6, PAVE + 6, UX1 + HW - BAT - 6, EMB_TOP - 4, 45)


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


def draw_unit(ctx, x0, c, conc_alpha):
    x1 = x0 + UW
    polyline(ctx, rect_pts(x0, TOPO, x1, TOPI), 1, c, 2.5)            # top slab (cut)
    polyline(ctx, rect_pts(x0, INV, x1, BED), 1, c, 2.5)              # bottom slab (cut)
    for x in (x0, x1):                                                 # unit ends seen across the cell
        polyline(ctx, [(x, TOPI), (x, INV)], 1, c, 1.6, alpha=0.7)
    if conc_alpha > 0:
        ctx.save(); ctx.rectangle(x0, TOPO, UW, BED - TOPO); ctx.clip()
        draw_concrete(ctx, CONC_TOP + CONC_BOT, c, conc_alpha)
        ctx.restore()


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 natural surface, creek diverted, excavation
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 90, EXC, 990, 1110, c, reveal=p)
        earth_hatch(ctx, 90, GND, TX0, EXC, c, reveal=p)
        earth_hatch(ctx, TX1, GND, 990, EXC, c, reveal=p)
        polyline(ctx, [(90, GND), (TX0, GND)], p, c, 3)
        polyline(ctx, [(TX1, GND), (990, GND)], p, c, 3)
        polyline(ctx, [(TX0, GND), (TX1, GND)], p, c, 1.6, alpha=0.6, dash=[10, 8])     # removed ground
        pe = prog(t, s1 + 0.8, 0.8)
        polyline(ctx, [(TX0, GND), (TX0, EXC), (TX1, EXC), (TX1, GND)], pe, c, 3)
    label(ctx, clamp((t - s1 - 1.0) / 0.8), c, (120, GND), (110, 1150), "NATURAL SURFACE")
    label(ctx, clamp((t - s1 - 1.6) / 0.8), c, (560, EXC), (470, 1192), "EXCAVATION", a=gone(t, s2))

    # 2 bedding
    c = tl.col(2, t); p = prog(t, s2, 1.0)
    if p > 0:
        clip_rect(ctx, TX0, BED - 2, TX0 + (TX1 - TX0) * p, EXC + 2)
        draw_gravel(ctx, BED_GRAVEL, c, 0.55)
        ctx.restore()
        polyline(ctx, [(TX0, BED), (TX1, BED)], p, c, 2.5)
    label(ctx, clamp((t - s2 - 1.0) / 0.8), c, (560, 1030), (470, 1192), "BEDDING")

    # 3 precast units, downstream (right) end first
    c = tl.col(3, t)
    for k in range(NU):
        i = NU - 1 - k
        pu = prog(t, s3 + 0.2 + k * 0.38, 0.5)
        if pu <= 0: continue
        ctx.save(); ctx.translate(0, -(1 - pu) * 140)
        ctx.push_group()
        draw_unit(ctx, UX0 + i * UW, c, 0.6)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(pu)
        ctx.restore()
    label(ctx, clamp((t - s3 - 2.4) / 0.8), c, (UX0 + 3.5 * UW, TOPO), (560, 520), "PRECAST UNIT", a=gone(t, s6))

    # 4 joints sealed + wrapped
    c = tl.col(4, t)
    for k, x in enumerate(JOINTS):
        pj = prog(t, s4 + 0.2 + k * 0.25, 0.4)
        if pj <= 0: continue
        polyline(ctx, rect_pts(x - 14, TOPO - 7, x + 14, TOPO), pj, c, 2.5)
        ring = pj * (1 - clamp((t - tl.step_end(4)) / 0.5))
        if ring > 0:
            ctx.set_source_rgba(*ORANGE, ring); ctx.set_line_width(2.5)
            ctx.arc(x, (TOPO + INV) / 2 + 4, 24, 0, 2 * math.pi); ctx.stroke()
    label(ctx, clamp((t - s4 - 1.4) / 0.8), c, (JOINTS[1], TOPO - 6), (110, 482), "SEALED JOINT", a=gone(t, s6))

    # 5 headwalls, aprons with toe walls, rock protection
    c = tl.col(5, t)
    ph = prog(t, s5, 0.8)
    if ph > 0:
        for x0 in (UX0 - HW, UX1):
            ytop = TOPO - (TOPO - HW_TOP) * ph
            ctx.set_source_rgba(*BG, 1); ctx.rectangle(x0, ytop, HW, TOPO - ytop); ctx.fill()
            polyline(ctx, [(x0, TOPO), (x0, ytop), (x0 + HW, ytop), (x0 + HW, TOPO)], 1, c, 2.5)
        if ph >= 1: draw_concrete(ctx, CONC_HW, c, 0.6)
    pa = prog(t, s5 + 0.7, 0.8)
    if pa > 0:
        for (xa, xb, toe) in ((TX0, UX0, TX0), (UX1, TX1, TX1 - 18)):
            ctx.set_source_rgba(*BG, 1); ctx.rectangle(toe, BED, 18, 36); ctx.fill()
            pts = [(xb, INV), (xa, INV), (xa, BED), (xb, BED)] if xa == TX0 else [(xa, INV), (xb, INV), (xb, BED), (xa, BED)]
            polyline(ctx, pts, pa, c, 2.5)
            polyline(ctx, [(toe, BED), (toe, BED + 36), (toe + 18, BED + 36), (toe + 18, BED)], pa, c, 2.5)
        if pa >= 1: draw_concrete(ctx, CONC_APR, c, 0.6)
    for k, (x, y, r) in enumerate(ROCKS):
        pr = prog(t, s5 + 1.4 + k * 0.06, 0.3)
        if pr <= 0: continue
        ctx.set_source_rgba(*BG, 1); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgba(*c, pr); ctx.set_line_width(2); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    label(ctx, clamp((t - s5 - 1.0) / 0.8), c, (UX0 - HW / 2, HW_TOP + 12), (110, 790), "HEADWALL")
    label(ctx, clamp((t - s5 - 1.5) / 0.8), c, (UX1 + 40, INV + 6), (800, 1150), "APRON", anchor="r")
    label(ctx, clamp((t - s5 - 2.0) / 0.8), c, (950, 988), (940, 1192), "ROCK PROTECTION", anchor="r")

    # 6 backfill in thin layers up to headwall height
    c = tl.col(6, t)
    nl = 5
    for k in range(nl):
        pl = prog(t, s6 + 0.2 + k * 0.4, 0.5)
        if pl <= 0: continue
        y = TOPO - (TOPO - HW_TOP) * (k + 1) / nl
        polyline(ctx, [(UX0, y), (UX1, y)], pl, c, 2.5 if k == nl - 1 else 1.4, alpha=1 if k == nl - 1 else 0.6,
                 dash=None if k == nl - 1 else [12, 8])
    label(ctx, clamp((t - s6 - 2.0) / 0.8), c, (680, 870), (560, 520), "COMPACTED LAYERS", a=gone(t, s7 + 1.6))

    # 7 embankment, rising layer by layer
    c = tl.col(7, t)
    pe = prog(t, s7, 2.0)
    if pe > 0:
        ytop = HW_TOP - (HW_TOP - EMB_TOP) * pe
        def xl(y): return EMB[0][0] + (HW_TOP - y) / (HW_TOP - EMB_TOP) * BAT
        def xr(y): return EMB[3][0] - (HW_TOP - y) / (HW_TOP - EMB_TOP) * BAT
        y = HW_TOP - 22
        while y > ytop + 1:
            polyline(ctx, [(xl(y) + 4, y), (xr(y) - 4, y)], 1, c, 1.4, alpha=0.5, dash=[12, 8])
            y -= 22
        polyline(ctx, [(EMB[0][0], HW_TOP), (xl(ytop), ytop)], 1, c, 3)
        polyline(ctx, [(EMB[3][0], HW_TOP), (xr(ytop), ytop)], 1, c, 3)
        polyline(ctx, [(xl(ytop), ytop), (xr(ytop), ytop)], 1, c, 3 if pe >= 1 else 2)
    label(ctx, clamp((t - s7 - 2.0) / 0.8), c, (340, 740), (110, 680), "EMBANKMENT")

    # 8 pavement, seal, guard fence
    c = tl.col(8, t)
    xa, xb = EMB[1][0] + 8, EMB[2][0] - 8
    pp = prog(t, s8, 0.9)
    if pp > 0:
        polyline(ctx, [(xa, EMB_TOP), (xa, PAVE), (xb, PAVE), (xb, EMB_TOP)], pp, c, 2.5)
        clip_rect(ctx, xa, PAVE, xa + (xb - xa) * pp, EMB_TOP)
        draw_gravel(ctx, PAVE_GRAVEL, c, 0.55)
        ctx.restore()
    ps = prog(t, s8 + 0.8, 0.7)
    if ps > 0:
        polyline(ctx, [(xa, PAVE - 3), (xb, PAVE - 3)], ps, c, 4)
    for k, x in enumerate((xa + 14, xb - 14)):
        pg = prog(t, s8 + 1.4 + k * 0.3, 0.5)
        if pg <= 0: continue
        polyline(ctx, [(x, PAVE - 5), (x, PAVE - 5 - 46 * pg)], 1, c, 3)
        if pg >= 1:
            polyline(ctx, rect_pts(x - 12, PAVE - 50, x + 12, PAVE - 36), 1, c, 2.5)
    label(ctx, clamp((t - s8 - 0.9) / 0.8), c, (655, PAVE + 12), (940, 520), "PAVEMENT + SEAL", anchor="r")
    label(ctx, clamp((t - s8 - 2.0) / 0.8), c, (xa + 14, PAVE - 40), (110, 482), "GUARD FENCE")

    # result: flow through the box + cover dimension
    r0 = tl.res0
    pf = prog(t, r0, 0.9)
    if pf > 0:
        y = 978
        polyline(ctx, [(UX0 + 30, y), (UX0 + 30 + (UX1 - UX0 - 60) * pf, y)], 1, BLUE, 3)
        if pf >= 1:
            polyline(ctx, [(UX1 - 50, y - 12), (UX1 - 30, y), (UX1 - 50, y + 12)], 1, BLUE, 3)
        text(ctx, "FLOW", (UX0 + UX1) / 2, 955, 26, BLUE, alpha=clamp(pf * 2 - 1), bold=True, anchor="c", spacing=4)
    dim_v(ctx, 590, PAVE, TOPO, "COVER", prog(t, r0 + 0.5, 0.6))


# ---------------------------------------------------------------- 3D model (mm): twin-cell culvert, headwalls, wings, aprons, backfill
def _wing(a, b, th, ha, hb, order):
    """Wing wall in plan from a to b (x, z), th thick, tapering from height ha down to hb."""
    from engine.three_d import Part
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dz)
    nx, nz = -dz / L * th / 2, dx / L * th / 2
    def end(p, h):
        return [(p[0] - nx, 0, p[1] - nz), (p[0] + nx, 0, p[1] + nz), (p[0] + nx, h, p[1] + nz), (p[0] - nx, h, p[1] - nz)]
    return Part(end(a, ha) + end(b, hb), order, "concrete")


def model3d():
    from engine.three_d import box
    P = []; o = 0
    UL, NUN = 1200, 6                     # unit laying length, number of units per barrel
    L = UL * NUN
    CW, CH, WT = 2400, 1500, 200          # cell clear width / height, wall + slab thickness
    BW = CW + 2 * WT                      # one barrel outside width
    BH = CH + 2 * WT
    GAP = 100
    Z = [0, BW + GAP]                     # two barrels side by side
    ZW = Z[1] + BW                        # total width
    BD = 150                              # bedding
    y0 = BD
    P.append(box(-2900, L + 2900, -300, 0, -2500, ZW + 2500, o, "ground")); P[-1].base = True; o += 1
    P.append(box(-250, L + 250, 0, BD, -300, ZW + 300, o, "brick")); o += 1                       # bedding
    for k in range(NUN):                  # downstream (+X) end first
        x0 = L - (k + 1) * UL
        for z0 in Z:
            P.append(box(x0, x0 + UL, y0, y0 + WT, z0, z0 + BW, o, "concrete"))                       # floor
            P.append(box(x0, x0 + UL, y0 + BH - WT, y0 + BH, z0, z0 + BW, o, "concrete"))             # roof
            P.append(box(x0, x0 + UL, y0 + WT, y0 + BH - WT, z0, z0 + WT, o, "concrete"))             # walls
            P.append(box(x0, x0 + UL, y0 + WT, y0 + BH - WT, z0 + BW - WT, z0 + BW, o, "concrete"))
        o += 1
    for k in range(1, NUN):               # joint wraps on the roof
        x = k * UL
        P.append(box(x - 180, x + 180, y0 + BH, y0 + BH + 25, -60, ZW + 60, o, "steel"))
    o += 1
    HT = y0 + BH + 700                    # headwall top
    for xa, xb, sgn in ((-300, 0, -1), (L, L + 300, 1)):
        P.append(box(xa, xb, y0 + BH, HT, -300, ZW + 300, o, "concrete"))                        # headwall over the opening
        xe = xa if sgn < 0 else xb
        P.append(box(xe + sgn * 2400 if sgn < 0 else xe, xe if sgn < 0 else xe + sgn * 2400,
                     0, y0 + WT, -1700, ZW + 1700, o, "concrete"))                               # apron
        xm = (xa + xb) / 2
        for zs, zd in ((-300, -1), (ZW + 300, 1)):                                               # flared wing walls
            P.append(_wing((xm, zs), (xm + sgn * 2300, zs + zd * 1400), 250, HT, y0 + WT + 200, o))
        o += 1
    for k in range(3):                    # backfill layers both sides (cut back to show the box)
        ya, yb = y0 + k * BH / 3, y0 + (k + 1) * BH / 3
        P.append(box(600, L - 600, ya, yb, -2200 + k * 500, -40, o, "ground"))
        P.append(box(600, L - 600, ya, yb, ZW + 40, ZW + 2200 - k * 500, o, "ground"))
        o += 1
    cfg = {"target": (L / 2, 1300, ZW / 2), "yaw": 50, "pitch": 20, "dist": 30000, "scale": 1.7,
           "cy_hook": 1040, "cy_result": 830, "cy_cover": 1010, "cover_scale": 1.0}
    return P, cfg
