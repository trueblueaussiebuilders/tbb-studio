"""006 Removing a load-bearing wall (reno)."""
import math
from engine.blueprint import *

META = {
    "category": "reno",
    "title": "LOAD-BEARING WALL OUT",
    "subtitle": "RENOVATION  //  TYPICAL AU METHOD",
    "dwg": "006",
    "drawing": "LOAD-BEARING WALL",
    "section_label": "ELEVATION  (NTS)",
    "hook": ["THAT WALL IS", "HOLDING UP", "YOUR CEILING."],
    "hook_sub": "HOW A LOAD-BEARING WALL COMES OUT",
    "cover": ["KNOCKING OUT A", "LOAD-BEARING", "WALL?"],
    "steps": [
        ("THE LOAD PATH", "Ceiling joists (and often the roof) bear on the wall. It's carrying weight down to the floor."),
        ("ENGINEER & PERMIT", "An engineer sizes the new beam, posts and footings. A building permit is issued."),
        ("PROP IT", "Adjustable steel props and a timber header take the load either side of the wall."),
        ("WALL OUT", "With the load on the props, the wall is carefully stripped out."),
        ("POSTS & FOOTINGS", "Slab cut and new pad footings poured, then posts stood at each end."),
        ("BEAM IN", "The new beam is lifted onto the posts, under or flush with the ceiling joists."),
        ("FIX & DE-PROP", "Joists fixed to the beam with brackets, then the props come out."),
        ("MAKE GOOD", "Beam lined in, ceiling and floor patched, then painted."),
    ],
    "result": "One open room. The load now runs through the beam and posts, down to new footings.",
}

NARRATION = {
    "hook": "That wall might be holding up your ceiling. Here's how a load-bearing wall comes out.",
    "steps": [
        "The ceiling joists, and often the roof, bear on this wall. It's carrying weight down to the floor.",
        "An engineer sizes a new beam, posts, and footings. Then a building permit is issued.",
        "Adjustable steel props and a timber header take the load on both sides of the wall.",
        "With the load on the props, the wall is carefully stripped out.",
        "The slab is cut, new pad footings are poured, and a post is stood at each end.",
        "The new beam is lifted onto the posts, either below or flush with the ceiling joists.",
        "The joists are fixed to the beam with brackets. Then the props come out.",
        "Finally, the beam is lined in, the ceiling and floor are patched, and it's all painted.",
    ],
    "result": "One open room. The load now runs through the beam and the posts, down to the new footings.",
    "end": "Follow for more.",
}

CAPTION = """Knocking out a wall? Check it's not holding your house up first 👇 How a load-bearing wall is removed.

Typical sequence: engineer's design and permit, temporary propping, wall out, new footings and posts, beam in, fix off and de-prop, make good.
Typical only. Always get a structural engineer and a building permit before removing any wall.

#renovation #renovationaustralia #openplan #construction #homereno #builder #structural #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
FLOOR, SLAB_B = 1000, 1050
CEIL = 560
J_TOP = 520
WALL_X0, WALL_X1 = 160, 920
OPEN_X0, OPEN_X1 = 300, 780
TP0, TP1 = 560, 575
BP0, BP1 = 985, 1000
STUDS = list(range(WALL_X0, WALL_X1 - 5, 60))
JOISTS = list(range(130, 935, 60))
BEAM = (268, 575, 812, 640)
POSTS = [(272, 296), (784, 808)]
FOOTINGS = [(250, 318), (762, 830)]
PROPS = [350, 540, 730]

CONC = concrete_points(61, 90, FLOOR, 970, SLAB_B, 240, lambda x, y: FLOOR + 3 < y < SLAB_B - 3)
CONC_F = concrete_points(62, 250, SLAB_B, 830, 1095, 120,
                         lambda x, y: any(a + 3 < x < b - 3 for a, b in FOOTINGS) and y < 1092)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 existing: slab, wall, ceiling joists, load arrows
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 90, SLAB_B, 970, 1100, c, reveal=p)
        polyline(ctx, rect_pts(90, FLOOR, 970, SLAB_B), p, c, 3)
        draw_concrete(ctx, CONC, c, 0.55 * clamp(p * 2 - 1))
        wall_a = 1 - clamp((t - s4 - 0.2) / 1.2)              # middle of the wall disappears in step 4
        polyline(ctx, rect_pts(WALL_X0, BP0, WALL_X0 + (WALL_X1 - WALL_X0) * p, BP1), 1, c, 2.2)
        polyline(ctx, rect_pts(WALL_X0, TP0, WALL_X0 + (WALL_X1 - WALL_X0) * p, TP1), 1, c, 2.2)
        for x in STUDS:
            if x > WALL_X0 + (WALL_X1 - WALL_X0) * p: break
            a = wall_a if OPEN_X0 <= x < OPEN_X1 else 1
            if a > 0: polyline(ctx, rect_pts(x, TP1, x + 10, BP0), 1, c, 2, alpha=a)
        if wall_a < 1:                                         # plates cut out of the opening
            ctx.set_source_rgba(*BG, 1 - wall_a)
            ctx.rectangle(OPEN_X0 + 2, TP0 - 2, OPEN_X1 - OPEN_X0 - 4, TP1 - TP0 + 4); ctx.fill()
            ctx.rectangle(OPEN_X0 + 2, BP0 - 2, OPEN_X1 - OPEN_X0 - 4, BP1 - BP0 + 2); ctx.fill()
        pj = prog(t, s1 + 0.6, 0.8)
        for x in JOISTS:
            if x > 130 + 810 * pj: break
            polyline(ctx, rect_pts(x, J_TOP, x + 14, CEIL), 1, c, 2)
        polyline(ctx, [(110, CEIL), (110 + 840 * pj, CEIL)], 1, c, 2)
        arrows = clamp((t - s1 - 1.0) / 0.5) * (1 - clamp((t - tl.step_end(2)) / 0.5))
        if arrows > 0:
            for x in range(200, 900, 110):
                y = 455 + 8 * math.sin(t * 4 + x)
                polyline(ctx, [(x, y), (x, y + 50)], 1, ORANGE, 3, alpha=arrows)
                polyline(ctx, [(x - 9, y + 38), (x, y + 52), (x + 9, y + 38)], 1, ORANGE, 3, alpha=arrows)
        leader(ctx, clamp((t - s1 - 1.3) / 0.8), c, (480, 540), (110, 445), "CEILING JOISTS")
        lab = 1 - clamp((t - s4) / 0.5)
        leader(ctx, clamp((t - s1 - 1.6) / 0.8) * lab, c, (400, 800), (110, 1150), "EXISTING WALL")

    # 2 engineer's beam outline (dashed)
    c = tl.col(2, t); p = prog(t, s2, 0.9) * (1 - clamp((t - s6) / 0.4))
    if p > 0:
        polyline(ctx, rect_pts(*BEAM), p, c, 2.5, dash=[12, 8])
        for a, b in POSTS:
            polyline(ctx, rect_pts(a, BEAM[3], b, FLOOR), p, c, 2, dash=[10, 7])
        leader(ctx, clamp((t - s2 - 0.9) / 0.8), c, (700, BEAM[1] + 6), (940, 445), "NEW BEAM (ENGINEER)", anchor="r")

    # 3 props + header (in front of the wall, dashed)
    c = tl.col(3, t)
    out = 1 - clamp((t - s7 - 1.0) / 0.6)
    ph = prog(t, s3, 0.6) * out
    if ph > 0:
        polyline(ctx, rect_pts(320, 590, 760, 606), 1, c, 2.5, alpha=ph)
    for i, x in enumerate(PROPS):
        pp = prog(t, s3 + 0.4 + i * 0.25, 0.5) * out
        if pp <= 0: continue
        polyline(ctx, [(x, 606), (x, 606 + (FLOOR - 6 - 606) * pp)], 1, c, 4, alpha=pp)
        polyline(ctx, [(x - 6, 760), (x - 6, FLOOR - 6)], pp, c, 2, alpha=pp)
        polyline(ctx, rect_pts(x - 16, FLOOR - 6, x + 16, FLOOR), pp, c, 2, alpha=pp)
    leader(ctx, clamp((t - s3 - 1.4) / 0.8) * out, c, (PROPS[0], 850), (110, 1192), "ACROW PROP")

    # 5 slab cut, pad footings, posts
    c = tl.col(5, t)
    pf = prog(t, s5, 0.8)
    if pf > 0:
        for a, b in FOOTINGS:
            ctx.set_source_rgba(*BG, pf); ctx.rectangle(a + 1, FLOOR - 1, b - a - 2, 1096 - FLOOR); ctx.fill()
            polyline(ctx, rect_pts(a, FLOOR, b, 1095), pf, c, 2.5)
        draw_concrete(ctx, CONC_F, c, 0.7 * clamp(pf * 2 - 1))
    pp = prog(t, s5 + 0.9, 0.7)
    if pp > 0:
        for a, b in POSTS:
            polyline(ctx, rect_pts(a, FLOOR - (FLOOR - BEAM[3]) * pp, b, FLOOR), 1, c, 3)
        leader(ctx, clamp((t - s5 - 1.2) / 0.8), c, (284, 1070), (110, 1150), "PAD FOOTING")
        leader(ctx, clamp((t - s5 - 1.5) / 0.8), c, (808, 820), (940, 1192), "POST", anchor="r")

    # 6 beam drops in
    c = tl.col(6, t); p = prog(t, s6, 0.8)
    if p > 0:
        ctx.save(); ctx.translate(0, -(1 - p) * 60)
        x0, y0, x1, y1 = BEAM
        polyline(ctx, rect_pts(x0, y0, x1, y1), 1, c, 3, alpha=p)
        for yy in (y0 + 8, y1 - 8):
            polyline(ctx, [(x0, yy), (x1, yy)], 1, c, 1.6, alpha=p)
        ctx.restore()
        leader(ctx, clamp((t - s6 - 0.8) / 0.8), c, (540, 608), (560, 492), "STEEL BEAM")

    # 7 brackets on each joist over the beam
    c = tl.col(7, t)
    for i, x in enumerate([j for j in JOISTS if BEAM[0] < j < BEAM[2] - 10]):
        pb = prog(t, s7 + i * 0.06, 0.3)
        if pb > 0:
            polyline(ctx, [(x - 4, CEIL - 14), (x - 4, CEIL + 13), (x + 18, CEIL + 13), (x + 18, CEIL - 14)], pb, c, 2)

    # 8 make good: bulkhead lining around the beam
    c = tl.col(8, t); p = prog(t, s8, 0.9)
    if p > 0:
        polyline(ctx, [(BEAM[0] - 8, CEIL), (BEAM[0] - 8, BEAM[3] + 8), (BEAM[2] + 8, BEAM[3] + 8), (BEAM[2] + 8, CEIL)], p, c, 2.5)
        for a, b in POSTS:
            polyline(ctx, rect_pts(a - 6, BEAM[3] + 8, b + 6, FLOOR), p, c, 1.5, alpha=0.7)
        leader(ctx, clamp((t - s8 - 0.9) / 0.8), c, (BEAM[2] + 8, 620), (940, 445), "LINED BULKHEAD", anchor="r")

    # result dims
    r0 = tl.res0
    dim_h(ctx, 900, POSTS[0][1], POSTS[1][0], "NEW OPENING", prog(t, r0, 0.6))


# ---------------------------------------------------------------- 3D model (mm): room with the wall replaced by a beam on posts
def model3d():
    from engine.three_d import box
    P = []; o = 0
    P.append(box(-400, 6400, -150, 0, -4200, 3000, o, "concrete")); P[-1].base = True; o += 1
    # outer back wall (bears the far end of the joists)
    P.append(box(0, 6000, 0, 45, -3690, -3600, o)); o += 1
    for x in range(0, 6000, 600):
        P.append(box(x, x + 45, 45, 2355, -3690, -3600, o))
    P.append(box(0, 6000, 2355, 2400, -3690, -3600, o)); o += 1
    # stub walls left either side of the new opening
    for a, b in ((0, 800), (5200, 6000)):
        P.append(box(a, b, 0, 45, -45, 45, o)); P.append(box(a, b, 2355, 2400, -45, 45, o))
        for x in range(a, b, 400):
            P.append(box(x, x + 45, 45, 2355, -45, 45, o))
    o += 1
    for x0 in (850, 5060):                                                     # posts
        P.append(box(x0, x0 + 90, 0, 2100, -45, 45, o, "steel"))
    o += 1
    P.append(box(800, 5200, 2100, 2400, -60, 60, o, "steel")); o += 1          # beam
    for i, x in enumerate(range(0, 6000, 450)):                               # ceiling joists
        P.append(box(x, x + 45, 2400, 2540, -3690, 2400, o + i // 3))
    cfg = {"target": (3000, 1300, -700), "yaw": 28, "pitch": 20, "dist": 15000, "scale": 1.45,
           "cy_hook": 1000, "cy_result": 830, "cy_cover": 1020, "cover_scale": 0.95}
    return P, cfg
