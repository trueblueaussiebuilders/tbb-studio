"""004 Timber wall frame (residential)."""
import math
from engine.blueprint import *

META = {
    "title": "TIMBER WALL FRAME",
    "subtitle": "RESIDENTIAL  //  TYPICAL AU DETAIL",
    "dwg": "004",
    "section_label": "ELEVATION  (NTS)",
    "hook": ["THE SKELETON", "INSIDE EVERY", "AUSSIE HOUSE."],
    "hook_sub": "HOW A TIMBER WALL FRAME GOES UP",
    "cover": ["THE SKELETON", "BEHIND YOUR", "WALLS."],
    "steps": [
        ("SETOUT", "Wall lines chalked out on the slab, plates cut to length."),
        ("PLATES", "Top and bottom plates marked out together, so every stud lines up."),
        ("STUDS", "Studs nailed between the plates at 450 or 600 centres."),
        ("OPENINGS", "Window framed with a lintel over, a sill trimmer under, and jamb studs each side."),
        ("NOGGINGS", "Noggings fixed between the studs to stiffen them up."),
        ("BRACING", "Steel strap bracing tensioned on the diagonal so the wall can't rack."),
        ("STAND & TIE DOWN", "Frame stood, plumbed, and bolted down to the slab."),
        ("ROOF TRUSSES", "Trusses lifted on, sitting on the top plate and tied down."),
    ],
    "result": "Light, strong and quick to build. That's why most Aussie houses are framed in timber.",
    "signoff": "Measure twice, follow once.",
}

NARRATION = {
    "hook": "Every brick house you've ever seen has one of these hiding inside. Here's how a timber wall frame goes up.",
    "steps": [
        "First, the wall lines are chalked out on the slab.",
        "The top and bottom plates are marked out together, so every stud lines up.",
        "Then the studs go in, every four hundred and fifty or six hundred millimetres.",
        "Windows get a lintel on top, and a sill trimmer underneath.",
        "Noggings go in halfway up to stiffen everything.",
        "Steel strap bracing goes on, so the wall can't rack sideways.",
        "Then the frame is stood up, plumbed, and bolted down to the slab.",
        "And the roof trusses sit right on top.",
    ],
    "result": "Light, strong, and quick to build. That's why most Australian houses are framed in timber.",
    "end": "Follow for more. Measure twice, follow once.",
}

CAPTION = """Ever wondered what's behind the plasterboard? 👇 How a timber wall frame goes up, step by step.

Typical: 90 mm studs at 450 or 600 centres, 2400 wall height, lintels over openings, strap bracing and tie-downs to the slab.
Typical only. Your engineer's design and AS 1684 govern.

#construction #framing #carpentry #housebuild #renovation #australianbuilding #timberframe #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
X0, X1 = 120, 940
TOP0, TOP1 = 560, 575          # top plate (double)
BOT0, BOT1 = 985, 1000         # bottom plate
SLAB0, SLAB1 = 1000, 1060
SW = 10                        # stud width
STUDS = [X0 + i * 90 for i in range(10)]          # 120 ... 930
OPEN_L, OPEN_R = 490, 750      # clear opening
LINTEL = (480, 595, 760, 630)
SILL = (490, 760, 750, 770)
FULL = [x for x in STUDS if not (OPEN_L <= x < OPEN_R)]
CRIPPLES = [x for x in STUDS if OPEN_L <= x < OPEN_R]   # 570, 660
APEX = (530, 415)

CONC = concrete_points(41, X0 - 30, SLAB0, X1 + 10, SLAB1, 300,
                       lambda x, y: SLAB0 + 4 < y < SLAB1 - 4)


def stud(ctx, x, y0, y1, p, c):
    polyline(ctx, rect_pts(x, y0, x + SW, y0 + (y1 - y0) * p), 1, c, 2.2)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 slab + chalk line
    c = tl.col(1, t); p = prog(t, s1, 0.8)
    if p > 0:
        earth_hatch(ctx, 90, SLAB1, 970, 1110, c, reveal=p)
        polyline(ctx, rect_pts(X0 - 30, SLAB0, X1 + 10, SLAB1), p, c, 3)
        draw_concrete(ctx, CONC, c, 0.6 * clamp((p - 0.4) / 0.6))
        polyline(ctx, [(X0, SLAB0 - 3), (X0 + (X1 - X0) * prog(t, s1 + 0.6, 0.9), SLAB0 - 3)], 1, c, 2, dash=[10, 6])
        leader(ctx, clamp((t - s1 - 1.2) / 0.8), c, (300, SLAB0 - 3), (110, 1150), "CHALK LINE")

    # 2 plates + stud marks
    c = tl.col(2, t); p = prog(t, s2, 0.8)
    if p > 0:
        polyline(ctx, rect_pts(X0, BOT0, X0 + (X1 - X0) * p, BOT1), 1, c, 2.5)
        polyline(ctx, rect_pts(X0, TOP0, X0 + (X1 - X0) * p, TOP1), 1, c, 2.5)
        polyline(ctx, [(X0, (TOP0 + TOP1) / 2), (X0 + (X1 - X0) * p, (TOP0 + TOP1) / 2)], 1, c, 1.2)
        pm = prog(t, s2 + 0.8, 0.8)
        for x in STUDS[:int(len(STUDS) * pm)]:
            for y in (TOP1 + 4, BOT0 - 4):
                polyline(ctx, [(x + SW / 2, y - 8), (x + SW / 2, y + 8)], 1, c, 2)
        leader(ctx, clamp((t - s2 - 1.2) / 0.8), c, (200, TOP0), (110, 445), "TOP PLATE")
        leader(ctx, clamp((t - s2 - 1.5) / 0.8), c, (850, BOT1 - 7), (940, 1150), "BOTTOM PLATE", anchor="r")

    # 3 full-height studs (the ones not in the opening)
    c = tl.col(3, t)
    for i, x in enumerate(FULL):
        ps = prog(t, s3 + i * 0.12, 0.4)
        if ps > 0: stud(ctx, x, TOP1, BOT0, ps, c)
    leader(ctx, clamp((t - s3 - 1.3) / 0.8), c, (215, 820), (110, 1192), "STUDS")

    # 4 opening: lintel, sill trimmer, jack + cripple studs
    c = tl.col(4, t)
    pl = prog(t, s4, 0.6)
    if pl > 0:
        x0, y0, x1, y1 = LINTEL
        polyline(ctx, rect_pts(x0, y0, x0 + (x1 - x0) * pl, y1), 1, c, 3)
        polyline(ctx, [(x0, (y0 + y1) / 2), (x0 + (x1 - x0) * pl, (y0 + y1) / 2)], 1, c, 1.2)
    psl = prog(t, s4 + 0.5, 0.6)
    if psl > 0:
        x0, y0, x1, y1 = SILL
        polyline(ctx, rect_pts(x0, y0, x0 + (x1 - x0) * psl, y1), 1, c, 3)
    pj = prog(t, s4 + 0.9, 0.6)
    if pj > 0:
        for x in CRIPPLES:
            stud(ctx, x, TOP1, LINTEL[1], pj, c)          # cripples above lintel
            stud(ctx, x, SILL[3], BOT0, pj, c)            # jacks under sill
        for x in (OPEN_L - SW - 1, OPEN_R + 1):           # jamb studs
            stud(ctx, x, LINTEL[3], BOT0, pj, c)
        polyline(ctx, [(OPEN_L + 4, LINTEL[3] + 4), (OPEN_R - 4, SILL[1] - 4)], pj, c, 1.2, alpha=0.4)
        polyline(ctx, [(OPEN_R - 4, LINTEL[3] + 4), (OPEN_L + 4, SILL[1] - 4)], pj, c, 1.2, alpha=0.4)
    leader(ctx, clamp((t - s4 - 1.2) / 0.8), c, (620, LINTEL[3]), (560, 690), "LINTEL")
    leader(ctx, clamp((t - s4 - 1.5) / 0.8), c, (680, SILL[1]), (560, 735), "SILL TRIMMER")

    # 5 noggings (staggered)
    c = tl.col(5, t)
    bays = [(a + SW, b) for a, b in zip(STUDS, STUDS[1:]) if not (OPEN_L - SW - 2 <= a < OPEN_R)]
    for i, (a, b) in enumerate(bays):
        pn = prog(t, s5 + i * 0.1, 0.35)
        if pn <= 0: continue
        y = 790 + (10 if i % 2 else -10)
        polyline(ctx, rect_pts(a, y, a + (b - a) * pn, y + 10), 1, c, 2.2)
    leader(ctx, clamp((t - s5 - 1.0) / 0.8), c, (255, 790), (420, 1150), "NOGGING")

    # 6 strap bracing
    c = tl.col(6, t)
    for i, (a, b) in enumerate([((X0 + 5, TOP1 + 3), (OPEN_L - 20, BOT0 - 3)), ((OPEN_L - 20, TOP1 + 3), (X0 + 5, BOT0 - 3)),
                                ((OPEN_R + 15, TOP1 + 3), (X1 - 5, BOT0 - 3)), ((X1 - 5, TOP1 + 3), (OPEN_R + 15, BOT0 - 3))]):
        pb = prog(t, s6 + i * 0.3, 0.6)
        if pb > 0:
            polyline(ctx, [a, b], pb, c, 3)
    leader(ctx, clamp((t - s6 - 1.4) / 0.8), c, (395, 900), (940, 1192), "STRAP BRACE", anchor="r")

    # 7 tie-down bolts + plumb level
    c = tl.col(7, t)
    for i, x in enumerate([165, 345, 800, 890]):
        pt = prog(t, s7 + i * 0.15, 0.4)
        if pt > 0:
            polyline(ctx, [(x, BOT0 - 10), (x, SLAB0 + 30)], pt, c, 3)
            polyline(ctx, [(x - 9, BOT0 - 8), (x + 9, BOT0 - 8)], pt, c, 3)
    pv = prog(t, s7 + 0.6, 0.5) * (1 - clamp((t - tl.step_end(7)) / 0.5))
    if pv > 0:
        polyline(ctx, rect_pts(STUDS[1] + SW + 2, 640, STUDS[1] + SW + 20, 900), 1, c, 2.5, alpha=pv)
        polyline(ctx, rect_pts(STUDS[1] + SW + 5, 760, STUDS[1] + SW + 17, 780), 1, c, 2, alpha=pv)
        dot(ctx, STUDS[1] + SW + 11, 770, 3, c, pv)
    leader(ctx, clamp((t - s7 - 1.0) / 0.8), c, (165, BOT0 - 8), (420, 1192), "TIE-DOWN")

    # 8 roof truss (gable end, fink pattern)
    c = tl.col(8, t)
    pt = prog(t, s8, 0.9)
    if pt > 0:
        ctx.save(); ctx.translate(0, (1 - pt) * -40)
        a = pt
        polyline(ctx, rect_pts(X0, 548, X1, TOP0), 1, c, 2.5, alpha=a)
        polyline(ctx, [(X0, 548), APEX, (X1, 548)], 1, c, 3, alpha=a)
        for seg in [((325, 481), (393, 548)), ((393, 548), APEX), (APEX, (667, 548)), ((667, 548), (735, 481))]:
            polyline(ctx, list(seg), 1, c, 2, alpha=a)
        ctx.restore()
        leader(ctx, clamp((t - s8 - 1.0) / 0.8), c, (735, 481), (940, 445), "ROOF TRUSS", anchor="r")

    # result dims
    r0 = tl.res0
    dim_h(ctx, 940, STUDS[0] + SW / 2, STUDS[1] + SW / 2, "600", prog(t, r0, 0.6))
    dim_v(ctx, 82, TOP0, BOT1, "2400 TYP", prog(t, r0 + 0.3, 0.6))


# ---------------------------------------------------------------- 3D model (mm): front wall + return wall + gable truss
def model3d():
    from engine.three_d import box, member
    P = []; o = 0
    P.append(box(-600, 6000, -150, 0, -3200, 700, o, "concrete")); P[-1].base = True; o += 1
    # front wall (z 0..90)
    P.append(box(0, 5400, 0, 45, 0, 90, o)); o += 1
    studs = [600 * i for i in range(10)] + [5355]
    for x in studs:
        if 2400 < x < 4200: continue                      # opening: handled below
        P.append(box(x, x + 45, 45, 2355, 0, 90, o)); o += 1
    P.append(box(2445, 2490, 45, 2100, 0, 90, o)); P.append(box(4155, 4200, 45, 2100, 0, 90, o)); o += 1   # jambs
    P.append(box(2400, 4245, 2100, 2300, 0, 90, o)); o += 1                                                # lintel
    for x in (3000, 3600):
        P.append(box(x, x + 45, 2300, 2355, 0, 90, o)); P.append(box(x, x + 45, 45, 900, 0, 90, o))        # cripples + jacks
    P.append(box(2490, 4155, 900, 945, 0, 90, o)); o += 1                                                  # sill trimmer
    for i, x in enumerate(studs[:-1]):
        nxt = studs[i + 1]
        if 2400 <= x < 4200 or nxt - x < 100: continue
        y = 1150 + (60 if i % 2 else 0)
        P.append(box(x + 45, nxt, y, y + 45, 0, 90, o))
    o += 1
    P.append(box(0, 5400, 2355, 2400, 0, 90, o)); P.append(box(0, 5400, 2400, 2445, 0, 90, o)); o += 1    # top plates
    for a, b in [((30, 2400), (2380, 60)), ((2380, 2400), (30, 60)), ((4250, 2400), (5380, 60)), ((5380, 2400), (4250, 60))]:
        P.append(member(a, b, 30, 90, 93, o, "steel"))
    o += 1
    # return wall along -z at x 0..90
    P.append(box(0, 90, 0, 45, -2700, 0, o)); o += 1
    for z in range(-2700, 0, 600):
        P.append(box(0, 90, 45, 2355, z, z + 45, o))
    o += 1
    P.append(box(0, 90, 2355, 2445, -2700, 0, o)); o += 1
    # gable truss on the front wall
    apex = (2700, 3345)
    P.append(member((0, 2490), (5400, 2490), 90, 20, 70, o)); o += 1
    P.append(member((0, 2490), apex, 90, 20, 70, o)); P.append(member(apex, (5400, 2490), 90, 20, 70, o)); o += 1
    for a, b in [((1350, 2918), (1800, 2490)), ((1800, 2490), apex), (apex, (3600, 2490)), ((3600, 2490), (4050, 2918))]:
        P.append(member(a, b, 70, 25, 65, o))
    o += 1
    cfg = {"target": (2400, 1500, -900), "yaw": -32, "pitch": 16, "dist": 10500, "scale": 1.38,
           "cy_hook": 1000, "cy_result": 830, "cy_cover": 1010, "cover_scale": 0.95}
    return P, cfg
