"""017 Shower waterproofing (reno)."""
import math
from engine.blueprint import *

META = {
    "category": "reno",
    "title": "SHOWER WATERPROOFING",
    "subtitle": "RENOVATION  //  TYPICAL AU METHOD",
    "dwg": "017",
    "drawing": "SHOWER WATERPROOFING",
    "section_label": "SECTION THROUGH SHOWER FLOOR  (NTS)",
    "hook": ["THE TILES", "AREN'T THE", "WATERPROOFING."],
    "hook_sub": "HOW A SHOWER IS WATERPROOFED",
    "cover": ["TILES DON'T", "STOP THE", "WATER."],
    "hook_start": 0.55,
    "xray": {"after_step": 6, "upto": 6, "hot": [6]},   # the membrane in 3D, tiles and screen still to come
    "steps": [
        ("WET-AREA SHEETS", "Water-resistant sheets are fixed to the wall frame around the shower."),
        ("PUDDLE FLANGE", "The floor waste gets a flange. The membrane will lap down into it."),
        ("FALL TO WASTE", "A sand and cement screed is laid so water always runs to the waste."),
        ("WATERSTOP ANGLE", "A metal angle across the doorway keeps water inside the bathroom."),
        ("PRIME + CORNERS", "Surfaces are primed. Corners get a bond breaker so the membrane can flex."),
        ("MEMBRANE", "Liquid membrane in two coats: up the walls, across the floor, into the flange."),
        ("CURE + CHECK", "It's left to cure, then checked for gaps before any tile goes on."),
        ("TILES ON", "Tiles are laid over the membrane. Silicone, not grout, goes in the corners."),
    ],
    "result": "Grout lets water through. The membrane underneath catches it and sends it to the waste.",
}

NARRATION = {
    "hook": "The tiles don't keep the water out. Something under them does.",
    "steps": [
        "In Australian bathrooms, the shower walls are lined with water-resistant sheets. They're fixed to the wall frame.",
        "The floor waste gets a puddle flange. The membrane will lap down into it.",
        "A sand and cement screed is laid on the floor. It falls towards the waste, so water always runs to the drain.",
        "A metal waterstop angle goes across the doorway. It keeps water inside the bathroom.",
        "Every surface is primed, so the membrane sticks. The corners get a bond breaker, so the membrane can flex without tearing.",
        "Then the waterproof membrane goes on. Two coats. Up the walls, across the floor, and down into the flange.",
        "The membrane is left to cure. Then it's checked for gaps, before any tile goes on.",
        "Finally, the tiles are laid over the top. The corners get silicone, not grout, because they move.",
    ],
    "result": "Grout lets water through. The membrane underneath catches it, and sends it to the waste.",
    "end": "Follow for more.",
}

CAPTION = """The tiles aren't what keeps the water out 👇 How a shower is waterproofed in an Australian bathroom.

Typical: wet-area plasterboard or fibre cement sheets are fixed to the wall frame. The floor waste gets a puddle flange, and a sand and cement screed is laid to falls towards the waste. A waterstop angle goes across the bathroom doorway. Surfaces are primed, and the wall/floor and wall/wall corners get a bond breaker or flexible sealant so the membrane can move without tearing. A liquid membrane goes on in two coats, up the shower walls, across the floor and down into the puddle flange. Once it has cured and been checked, the tiles go on, with silicone (not grout) in the internal corners.
Membrane type, heights, falls and set-downs depend on the product, the standard and your state. Use a qualified waterproofer and check your local requirements.
Typical only. Your engineer's design and the membrane maker's instructions govern.

#waterproofing #bathroomrenovation #bathroomreno #shower #tiling #renovationaustralia #construction #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
SX0, SX1 = 140, 200                  # wall stud (cut)
SH = 214                             # face of the wet-area sheet
WALL_TOP = 430
SLAB_T, SLAB_B, SLAB_X1 = 1050, 1140, 990
WX = 470                             # floor waste centre
DX = 850                             # doorway: waterstop angle
FALL_W, FALL_D = 950, 960          # screed top at the wall / at the door
FALL_WASTE = 1000                    # screed top at the waste
HALL_T = 922                         # hallway finished floor (step up past the door)
MEM_TOP = 600                        # membrane height on the shower wall (NTS)
TILE_TOP = 455                       # wall tiles go higher than the membrane

SLAB_CONC = concrete_points(171, SX0, SLAB_T, SLAB_X1, SLAB_B, 150)

# plan inset (top right)
IX0, IX1, IY0, IY1 = 610, 960, 470, 700
SHW = (IX0, IY0, IX0 + 165, IY0 + 140)          # shower zone in the corner
PW = ((SHW[0] + SHW[2]) / 2, (SHW[1] + SHW[3]) / 2)


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


def screed_y(x):
    """Top of the screed at x: falls from the wall and from the door down to the waste."""
    if x <= WX: return FALL_W + (FALL_WASTE - FALL_W) * (x - SH) / (WX - SH)
    return FALL_WASTE + (FALL_D - FALL_WASTE) * (x - WX) / (DX - WX)


def screed_line(x0, x1, off=0.0, n=40):
    return [(x0 + (x1 - x0) * i / n, screed_y(x0 + (x1 - x0) * i / n) + off) for i in range(n + 1)]


def membrane_path(off=0.0):
    """Wall (top down), the corner, the floor into the flange, out to the door and up the angle."""
    return ([(SH + 3 + off, MEM_TOP), (SH + 3 + off, FALL_W - 3 - off)] + screed_line(SH + 3, WX - 30, -3 - off, 20)
            + [(WX - 22, FALL_WASTE + 6), (WX + 22, FALL_WASTE + 6)] + screed_line(WX + 30, DX - 4, -3 - off, 20)
            + [(DX - 4 - off, HALL_T + 2)])


def draw_base(ctx, c, p):
    """Slab, wall frame and the hallway floor beyond the door (context)."""
    if p <= 0: return
    polyline(ctx, rect_pts(SX0 - 30, SLAB_T, SLAB_X1, SLAB_B), p, c, 3)
    draw_concrete(ctx, SLAB_CONC, c, 0.45 * p)
    earth_hatch(ctx, SX0 - 30, SLAB_B, SLAB_X1, SLAB_B + 18, c, 0.28, reveal=p)
    polyline(ctx, rect_pts(SX0, WALL_TOP, SX1, SLAB_T), p, c, 2.5)                    # stud
    polyline(ctx, [(SX0, SLAB_T - 14), (SX1, SLAB_T - 14)], p, c, 1.6)               # bottom plate
    polyline(ctx, [(SX0 + 4, WALL_TOP), (SX0 - 8, WALL_TOP - 14), (SX0 + 16, WALL_TOP - 22),
                   (SX1 + 4, WALL_TOP - 10)], p, c, 2, alpha=0.6)                     # break line
    # hallway floor past the door: screed + tile, no fall
    polyline(ctx, rect_pts(DX + 6, HALL_T, SLAB_X1, SLAB_T), p, c, 2, alpha=0.7)
    polyline(ctx, [(DX + 6, HALL_T + 14), (SLAB_X1, HALL_T + 14)], p, c, 1.6, alpha=0.7)


def inset(ctx, t, tl, a):
    """Bathroom plan: shower in the corner, falls to the waste, waterstop at the door, membrane, tiles."""
    if a <= 0: return
    s2, s3, s4, s5, s6, s8 = tl.s(2), tl.s(3), tl.s(4), tl.s(5), tl.s(6), tl.s(8)
    ctx.push_group()
    text(ctx, "BATHROOM PLAN", IX0, IY0 - 18, 22, BLUE, bold=True, spacing=3)
    fill_poly(ctx, rect_pts(IX0, IY0, IX1, IY1)[:4], BG, 0.92)
    # membrane over the whole floor (step 6), tiles over it (step 8)
    pm = prog(t, s6 + 0.4, 1.4)
    if pm > 0:
        fill_poly(ctx, rect_pts(IX0, IY0, IX0 + (IX1 - IX0) * pm, IY1)[:4], BLUE, 0.28)
    pt = prog(t, s8 + 0.3, 1.6)
    if pt > 0:
        ctx.set_source_rgba(*WHITE, 0.35); ctx.set_line_width(1.2)
        for x in range(IX0 + 28, IX1, 28):
            ctx.move_to(x, IY1); ctx.line_to(x, IY1 - (IY1 - IY0) * pt)
        for y in range(IY1 - 28, IY0, -28):
            ctx.move_to(IX0, y); ctx.line_to(IX0 + (IX1 - IX0) * pt, y)
        ctx.stroke()
    # walls: thick on three sides, door opening on the right
    for pts in ([(IX1, IY0 + 80), (IX1, IY0), (IX0, IY0), (IX0, IY1), (IX1, IY1), (IX1, IY0 + 170)],):
        polyline(ctx, pts, 1, WHITE, 5, alpha=0.8)
    polyline(ctx, rect_pts(*SHW), 1, WHITE, 1.6, alpha=0.6, dash=[7, 6])                # shower zone
    # membrane up the shower walls (step 6): thick blue along the two shower walls
    pw = prog(t, s6 + 0.4, 0.8)
    polyline(ctx, [(SHW[2], IY0 + 4), (IX0 + 4, IY0 + 4), (IX0 + 4, SHW[3])], pw, BLUE, 6)
    # floor waste (step 2)
    pf = prog(t, s2 + 0.2, 0.4)
    if pf > 0:
        ctx.set_source_rgba(*tl.col(2, t), pf); ctx.set_line_width(2.5)
        ctx.new_path(); ctx.arc(*PW, 13, 0, 2 * math.pi); ctx.stroke(); dot(ctx, *PW, 5, tl.col(2, t), pf)
    # falls (step 3): arrows from the edges of the shower into the waste, and across the floor
    c3 = tl.col(3, t)
    for i, (x0, y0) in enumerate(((SHW[0] + 18, SHW[1] + 18), (SHW[2] - 14, SHW[1] + 16), (SHW[0] + 16, SHW[3] - 14),
                                  (SHW[2] - 12, SHW[3] - 12))):
        k = prog(t, s3 + 0.3 + i * 0.15, 0.5)
        ux, uy = PW[0] - x0, PW[1] - y0; L = math.hypot(ux, uy)
        arrow(ctx, x0, y0, x0 + ux * (L - 20) / L, y0 + uy * (L - 20) / L, c3, p=k, head=8, width=2.5)
    for i, (x0, y0) in enumerate(((IX1 - 30, IY1 - 40), (IX1 - 60, IY0 + 50))):
        k = prog(t, s3 + 1.0 + i * 0.15, 0.6)
        arrow(ctx, x0, y0, PW[0] + 40, PW[1] + 14 * (1 if i == 0 else -1) + 10, c3, p=k, head=8, width=2.5)
    # waterstop angle across the door (step 4)
    polyline(ctx, [(IX1 - 6, IY0 + 82), (IX1 - 6, IY0 + 168)], prog(t, s4 + 0.3, 0.5), tl.col(4, t), 6)
    # bond breaker in the corners (step 5)
    k5 = prog(t, s5 + 1.6, 0.4)
    for q in ((IX0 + 6, IY0 + 6), (IX0 + 6, IY1 - 6), (IX1 - 6, IY0 + 6), (IX1 - 6, IY1 - 6)):
        dot(ctx, *q, 7, tl.col(5, t), k5)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    cap = [(s3 + 0.5, s4, "FALLS TO THE WASTE"), (s4 + 0.6, s5, "WATERSTOP AT THE DOOR"),
           (s6 + 0.6, tl.s(7), "WHOLE FLOOR + SHOWER WALLS"), (s8 + 0.5, tl.res0, "TILES OVER THE TOP")]
    for t0, t1, s in cap:
        k = clamp((t - t0) / 0.3) * gone(t, t1 - 0.1, 0.3) * a
        if k > 0:
            text(ctx, s, IX1, IY1 + 34, 22, WHITE, alpha=0.9 * k, bold=True, anchor="r", spacing=1)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    draw_base(ctx, WHITE, prog(t, s1, 1.0))

    # 1 wet-area sheet on the stud
    c1 = tl.col(1, t)
    ps = prog(t, s1 + 0.6, 1.0)
    if ps > 0:
        y0 = SLAB_T - (SLAB_T - WALL_TOP) * ps
        fill_poly(ctx, rect_pts(SX1, y0, SH, SLAB_T)[:4], c1, 0.25)
        polyline(ctx, rect_pts(SX1, y0, SH, SLAB_T), 1, c1, 2.5)
    label(ctx, clamp((t - s1 - 0.6) / 0.8), WHITE, (170, 560), (300, 520), "WALL FRAME", a=gone(t, s3))
    label(ctx, clamp((t - s1 - 1.4) / 0.8), c1, (SH - 6, 680), (300, 610), "WET-AREA SHEET", a=gone(t, s3))

    # 2 floor waste + puddle flange
    c2 = tl.col(2, t)
    pw = prog(t, s2, 0.8)
    polyline(ctx, [(WX - 16, SLAB_B + 30), (WX - 16, FALL_WASTE + 8)], pw, c2, 3)
    polyline(ctx, [(WX + 16, SLAB_B + 30), (WX + 16, FALL_WASTE + 8)], pw, c2, 3)
    pf = prog(t, s2 + 0.7, 0.5)
    if pf > 0:
        fill_poly(ctx, rect_pts(WX - 16, FALL_WASTE + 8, WX + 16, SLAB_T)[:4], BG, 1)
        polyline(ctx, [(WX - 16, FALL_WASTE + 18), (WX - 16, FALL_WASTE + 8), (WX - 16 - 34 * pf, FALL_WASTE + 8)], 1, c2, 3)
        polyline(ctx, [(WX + 16, FALL_WASTE + 18), (WX + 16, FALL_WASTE + 8), (WX + 16 + 34 * pf, FALL_WASTE + 8)], 1, c2, 3)
    label(ctx, clamp((t - s2 - 1.0) / 0.8), c2, (WX + 40, FALL_WASTE + 8), (560, 880), "PUDDLE FLANGE", a=gone(t, s3 + 0.3))
    label(ctx, clamp((t - s2 - 0.3) / 0.8), c2, (WX - 16, SLAB_B + 10), (330, 1195), "FLOOR WASTE", anchor="r",
          a=gone(t, s5))

    # 3 screed to falls (fills in from the wall to the door)
    c3 = tl.col(3, t)
    pk = prog(t, s3 + 0.2, 1.4)
    if pk > 0:
        xe = SH + (DX - SH) * pk
        top = screed_line(SH, min(xe, WX - 50), 0, 20) + ([(WX - 50, screed_y(WX - 50))] if xe > WX - 50 else [])
        if xe > WX + 50: top += screed_line(WX + 50, xe, 0, 20)
        ctx.save()
        ctx.rectangle(SH, 880, xe - SH, SLAB_T - 880); ctx.clip()
        for seg in ((SH, WX - 50), (WX + 50, DX)):
            poly = screed_line(seg[0], seg[1], 0, 20) + [(seg[1], SLAB_T), (seg[0], SLAB_T)]
            fill_poly(ctx, poly, BG, 1)
            fill_poly(ctx, poly, c3, 0.12)
            polyline(ctx, screed_line(seg[0], seg[1], 0, 20), 1, c3, 2.5)
        ctx.restore()
        # the waste shows through the screed gap again
        polyline(ctx, [(WX - 50, screed_y(WX - 50)), (WX - 50, FALL_WASTE + 8)], pk, c3, 2)
        polyline(ctx, [(WX + 50, screed_y(WX + 50)), (WX + 50, FALL_WASTE + 8)], pk, c3, 2)
    pa = prog(t, s3 + 1.4, 0.6) * gone(t, s4 + 0.5)
    arrow(ctx, 260, 905, 420, 925, BLUE, p=pa, a=1, head=10)
    arrow(ctx, 780, 905, 560, 925, BLUE, p=pa, a=1, head=10)
    if pa > 0:
        text(ctx, "FALL", 340, 890, 26, BLUE, alpha=clamp(pa * 2 - 1), bold=True, anchor="c", spacing=3)
        text(ctx, "FALL", 670, 890, 26, BLUE, alpha=clamp(pa * 2 - 1), bold=True, anchor="c", spacing=3)
    label(ctx, clamp((t - s3 - 1.0) / 0.8), c3, (650, screed_y(650) + 30), (540, 790), "SCREED", a=gone(t, s5))

    # 4 waterstop angle at the door
    c4 = tl.col(4, t)
    pa4 = prog(t, s4 + 0.3, 0.7)
    polyline(ctx, [(DX - 30, FALL_D), (DX, FALL_D), (DX, HALL_T)], pa4, c4, 4)
    label(ctx, clamp((t - s4 - 0.8) / 0.8), c4, (DX, HALL_T + 6), (960, 800), "WATERSTOP ANGLE", anchor="r",
          a=gone(t, s6))

    # 5 primer (dashed, follows the surfaces) + bond breaker in the corners
    c5 = tl.col(5, t)
    pp = prog(t, s5 + 0.2, 1.4)
    polyline(ctx, membrane_path(0), pp, c5, 2, dash=[6, 6], alpha=0.9 * gone(t, s6 + 1.2))
    kb = prog(t, s5 + 1.7, 0.4)
    if kb > 0:
        for (x, y, sx) in ((SH, FALL_W, 1), (DX, FALL_D, -1)):
            fill_poly(ctx, [(x, y - 18 * kb), (x, y), (x + sx * 18 * kb, y)], c5, 0.95)
    label(ctx, clamp((t - s5 - 0.4) / 0.8), c5, (600, screed_y(600) - 4), (560, 880), "PRIMER", a=gone(t, s6))
    label(ctx, clamp((t - s5 - 1.8) / 0.8), c5, (SH + 6, FALL_W - 8), (300, 800), "BOND BREAKER", a=gone(t, s6))

    # 6 membrane: two coats, the second one heavier
    pm1 = prog(t, s6 + 0.2, 1.3)
    pm2 = prog(t, s6 + 1.6, 1.3)
    polyline(ctx, membrane_path(0), pm1, BLUE, 4, alpha=0.7)
    polyline(ctx, membrane_path(0), pm2, BLUE, 7)
    label(ctx, clamp((t - s6 - 0.8) / 0.8), BLUE, (SH + 4, 700), (300, 700), "MEMBRANE", a=gone(t, s8))
    label(ctx, clamp((t - s6 - 1.9) / 0.8), BLUE, (WX - 20, FALL_WASTE + 4), (300, 800), "INTO THE FLANGE",
          a=gone(t, s7 + 0.3))
    label(ctx, clamp((t - s6 - 2.4) / 0.8), BLUE, (DX - 4, HALL_T + 10), (960, 800), "UP THE ANGLE", anchor="r",
          a=gone(t, s7 + 0.3))

    # 7 cure + check: a scan along the membrane, then a stamp
    ps7 = prog(t, s7 + 0.4, 1.8)
    if 0 < ps7 < 1:
        path = membrane_path(0)
        segs = [math.dist(path[i], path[i + 1]) for i in range(len(path) - 1)]
        target = sum(segs) * ps7; acc = 0
        for i, L in enumerate(segs):
            if acc + L >= target:
                k = (target - acc) / L if L else 0
                x = path[i][0] + (path[i + 1][0] - path[i][0]) * k; y = path[i][1] + (path[i + 1][1] - path[i][1]) * k
                ctx.set_source_rgba(*ORANGE, 0.95); ctx.set_line_width(3)
                ctx.new_path(); ctx.arc(x, y, 26, 0, 2 * math.pi); ctx.stroke()
                break
            acc += L
    ks = gone(t, s8, 0.4)
    if ks > 0:
        ctx.push_group()
        stamp(ctx, "CHECKED", 440, 560, prog(t, s7 + 2.3, 0.35), ORANGE, angle=-0.1)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(ks)

    # 8 tiles: up the wall (higher than the membrane) and across the floor, then silicone in the corner
    c8 = tl.col(8, t)
    pt = prog(t, s8 + 0.2, 1.4)
    if pt > 0:
        n = 0
        for y1 in range(FALL_W - 10, TILE_TOP, -92):
            k = clamp(pt * 9 - n * 0.6); n += 1
            if k <= 0: continue
            y0 = max(y1 - 86, TILE_TOP)
            fill_poly(ctx, rect_pts(SH + 9, y0, SH + 31, y1)[:4], BG, 1)
            polyline(ctx, rect_pts(SH + 9, y0, SH + 31, y1), k, c8, 2.2)
        n = 0
        for seg in ((SH + 36, WX - 54), (WX + 54, DX - 10)):
            x = seg[0]
            while x < seg[1] - 8:
                x2 = min(x + 62, seg[1])
                k = clamp(pt * 9 - n * 0.5); n += 1
                if k > 0:
                    q = [(x, screed_y(x) - 13), (x2, screed_y(x2) - 13), (x2, screed_y(x2) - 33), (x, screed_y(x) - 33)]
                    fill_poly(ctx, q, BG, 1); polyline(ctx, q + [q[0]], k, c8, 2.2)
                x = x2 + 6
        kg = prog(t, s8 + 1.4, 0.4)                                                  # waste grate
        if kg > 0:
            y = FALL_WASTE - 8
            polyline(ctx, [(WX - 50, y), (WX + 50, y)], kg, c8, 3, dash=[8, 5])
    ksi = prog(t, s8 + 1.8, 0.4)
    if ksi > 0:
        dot(ctx, SH + 36, FALL_W - 20, 8, c8, ksi)
    label(ctx, clamp((t - s8 - 0.8) / 0.8), c8, (SH + 31, 520), (300, 520), "TILES", a=gone(t, r0 + 0.2))
    label(ctx, clamp((t - s8 - 1.8) / 0.8), c8, (SH + 40, FALL_W - 24), (300, 840), "SILICONE", a=gone(t, r0 + 0.2))
    label(ctx, clamp((t - s8 - 2.4) / 0.8), BLUE, (SH + 4, 580), (300, 610), "MEMBRANE", a=gone(t, r0 + 0.2))

    # plan inset (steps 2-8)
    inset(ctx, t, tl, prog(t, s2 + 0.1, 0.4) * gone(t, r0, 0.5))

    # result: water gets through a grout joint, hits the membrane and runs down to the waste
    pr = prog(t, r0 + 0.2, 0.6)
    if pr > 0:
        for i, x in enumerate((330, 380)):
            y = 560 + (screed_y(x) - 40 - 560) * clamp(pr * 1.2 - i * 0.2)
            ctx.set_source_rgba(*BLUE, 0.9)
            ctx.move_to(x, y - 22); ctx.curve_to(x + 12, y - 4, x + 12, y + 8, x, y + 8)
            ctx.curve_to(x - 12, y + 8, x - 12, y - 4, x, y - 22); ctx.fill()
        text(ctx, "GROUT LETS WATER IN", 540, 520, 30, BLUE, alpha=clamp(pr * 2 - 1), bold=True, anchor="c", spacing=2)
    pd = prog(t, r0 + 1.0, 0.9)
    if pd > 0:
        arrow(ctx, 260, screed_y(260) - 9, WX - 34, FALL_WASTE - 4, ORANGE, p=pd, head=10)
        arrow(ctx, 760, screed_y(760) - 9, WX + 34, FALL_WASTE - 4, ORANGE, p=pd, head=10)
        arrow(ctx, WX, FALL_WASTE + 20, WX, SLAB_B + 40, ORANGE, p=prog(t, r0 + 1.7, 0.6), head=10)
        text(ctx, "MEMBRANE SENDS IT TO THE WASTE", 540, 600, 30, ORANGE, alpha=clamp(pd * 2 - 1), bold=True,
             anchor="c", spacing=1)


# ---------------------------------------------------------------- 3D model (mm): a bathroom corner with the shower
def model3d():
    from engine.three_d import box
    P = []; o = 0
    LX, LZ, WH = 2400, 2700, 2400            # room size, wall height
    SHX, SHZ = 1000, 1000                    # shower in the back-left corner
    g = box(-500, LX + 500, -250, 0, -500, LZ + 500, o, "ground"); g.base = True; P.append(g); o += 1
    # 1 wall frames on the back (z=0) and left (x=0) walls: plates + studs
    for (horiz, L) in ((True, LX), (False, LZ)):
        def b(a0, a1, y0, y1, d0, d1):
            return box(a0, a1, y0, y1, d0, d1, 1) if horiz else box(d0, d1, y0, y1, a0, a1, 1)
        P.append(b(0, L, 0, 45, -90, 0)); P.append(b(0, L, WH - 45, WH, -90, 0))
        for s in range(0, L, 450):
            P.append(b(s, s + 45, 45, WH - 45, -90, 0))
    o = 2
    # 2 wet-area sheets on both walls
    P.append(box(0, LX, 0, WH, 0, 12, o, "precast")); P.append(box(0, 12, 0, WH, 12, LZ, o, "precast")); o += 1
    # 3 floor waste + puddle flange (the screed goes round it)
    wx, wz = SHX / 2, SHZ / 2
    P.append(box(wx - 50, wx + 50, -250, 40, wz - 50, wz + 50, o, "steel"))
    P.append(box(wx - 110, wx + 110, 30, 40, wz - 110, wz + 110, o, "steel")); o += 1
    # 4 screed (in a few tiles so the falls read as facets): thicker at the edges than at the waste
    for x0, x1 in ((12, wx - 110), (wx - 110, wx + 110), (wx + 110, LX)):
        for z0, z1 in ((12, wz - 110), (wz - 110, wz + 110), (wz + 110, LZ)):
            if x0 == wx - 110 and z0 == wz - 110: continue
            h = 40 if (x1 <= SHX + 200 and z1 <= SHZ + 200) else 55
            P.append(box(x0, x1, 0, h, z0, z1, o, "concrete"))
    o += 1
    # 5 waterstop angle across the doorway (front edge, right part)
    P.append(box(1300, 2300, 0, 75, LZ - 10, LZ, o, "steel")); o += 1
    # 6 membrane: whole floor, up the shower walls, a low upturn on the other walls
    P.append(box(12, LX, 55, 62, 12, LZ - 10, o, "membrane"))
    P.append(box(0, SHX, 0, 1800, 12, 22, o, "membrane")); P.append(box(12, 22, 0, 1800, 12, SHZ, o, "membrane"))
    P.append(box(SHX, LX, 0, 150, 12, 22, o, "membrane")); P.append(box(12, 22, 0, 150, SHZ, LZ - 10, o, "membrane"))
    o += 1
    # 7 tiles: floor (back part only, the front is left open to show the membrane) and shower walls
    T = 300
    for xi in range(0, LX, T):
        for zi in range(0, 1800, T):
            P.append(box(xi + 22 + 3, min(xi + T, LX) + 19, 62, 74, zi + 22 + 3, zi + T + 19, o, "precast"))
    for yi in range(70, 2100, T):
        for si in range(0, SHX, T):
            P.append(box(si + 25, si + T + 22, yi + 3, min(yi + T, 2100), 22, 34, o, "precast"))
            P.append(box(22, 34, yi + 3, min(yi + T, 2100), si + 25, si + T + 22, o, "precast"))
    o += 1
    # 8 frameless screen on the open side of the shower
    P.append(box(SHX + 20, SHX + 32, 74, 2000, 40, SHZ - 100, o, "glass")); o += 1
    cfg = {"target": (LX / 2, 700, LZ / 2), "yaw": -50, "pitch": 30, "dist": 9500, "scale": 1.6,
           "cy_hook": 1140, "cy_result": 830, "cy_cover": 990, "cover_scale": 1.0}
    return P, cfg
