"""003 Brick veneer wall (residential)."""
import math
from engine.blueprint import *

META = {
    "title": "BRICK VENEER WALL",
    "subtitle": "RESIDENTIAL  //  TYPICAL AU DETAIL",
    "dwg": "003",
    "section_label": "WALL SECTION  (NTS)",
    "hook": ["THAT BRICK HOUSE?", "IT'S HELD UP", "BY TIMBER."],
    "hook_sub": "HOW BRICK VENEER GOES TOGETHER",
    "cover": ["THAT BRICK HOUSE", "IS HELD UP", "BY TIMBER."],
    "steps": [
        ("SLAB EDGE", "Slab edge often stepped down (rebated) so the bricks sit below floor level."),
        ("FRAME & ROOF", "Timber wall frame stood and tied down, then the roof trusses and eaves go on."),
        ("WALL WRAP", "Breathable wall wrap fixed around the outside of the frame."),
        ("FIRST COURSES", "First courses laid on the slab edge, with flashing and weep holes to let water out."),
        ("WALL TIES", "Ties screwed to the studs, ready to be built into the mortar joints."),
        ("BRICKWORK", "Brick skin goes up course by course, with a cavity between bricks and frame."),
        ("INSULATE & LINE", "Insulation batts in the frame, plasterboard on the inside."),
        ("SHRINKAGE GAP", "Gap left under the eaves and window sills so the timber can shrink without cracking the bricks."),
    ],
    "result": "The frame holds the house up. The bricks are the raincoat.",
    "next": "NEXT: HOW A TIMBER WALL FRAME GOES UP",
}

NARRATION = {
    "hook": "That brick house? It's actually held up by timber. Here's how brick veneer goes together.",
    "steps": [
        "It starts at the slab edge, usually stepped down so the bricks sit below the floor.",
        "The timber frame's stood and tied down, and the roof goes on.",
        "Wall wrap goes around the outside of the frame.",
        "First courses go down, with flashing and weep holes to let water out.",
        "Wall ties are screwed to the studs, ready for the brickwork.",
        "Then the brick skin goes up, with a cavity behind it.",
        "Inside, insulation batts, then plasterboard.",
        "And a gap's left under the eaves, so the frame can shrink without cracking the bricks.",
    ],
    "result": "The frame holds the house up. The bricks are basically a tough raincoat.",
    "end": "Follow for more. Next up, timber wall frames.",
}

CAPTION = """That brick house? It's held up by timber 👇 How a brick veneer wall goes together.

Typical: 90 timber studs, a 40 to 60 cavity, 110 brick skin tied back to the frame. The brick carries its own weight, the frame carries the roof.
Typical only. Your engineer's design and the drawings govern.

#construction #brickveneer #bricklaying #housebuild #australianbuilding #carpentry #building #truebluebuilds"""

# ---------------------------------------------------------------- geometry (px, NTS)
BX0, BX1 = 250, 340            # brick skin
FX0, FX1 = 380, 455            # frame (stud zone)
PB0, PB1 = 455, 468            # plasterboard
SOFFIT = 470                   # eave lining
BRICK_TOP = 485                # leaves the shrinkage gap under the soffit
TP0, TP1 = 470, 490            # top plate
BP0, BP1 = 985, 1000           # bottom plate
FLOOR = 1000                   # slab top inside
REBATE = 1030                  # slab top under the bricks
SLAB_X0 = 245
N_COURSES = 28
COURSE = (REBATE - BRICK_TOP) / N_COURSES
TIE_COURSES = [4, 10, 16, 22]

def _in_slab(x, y):
    if 249 < x < 376 and REBATE + 4 < y < 1146: return True
    if 376 <= x < 456 and FLOOR + 4 < y < 1146: return True
    if 456 <= x < 936 and FLOOR + 4 < y < 1076: return True
    return False
CONC = concrete_points(31, SLAB_X0, FLOOR, 940, 1150, 700, _in_slab)
SLAB_PTS = [(SLAB_X0, REBATE), (FX0, REBATE), (FX0, FLOOR), (940, FLOOR), (940, 1080), (460, 1080), (460, 1150), (SLAB_X0, 1150), (SLAB_X0, REBATE)]


def bricks(ctx, c, n_from, n_to, alpha=1.0):
    """Courses n_from..n_to (1 = bottom), drawn in section with a 45 deg brick hatch."""
    for n in range(n_from, n_to + 1):
        y1 = REBATE - (n - 1) * COURSE; y0 = y1 - COURSE
        ctx.set_source_rgba(*c, 0.9 * alpha); ctx.set_line_width(2)
        ctx.rectangle(BX0, y0 + 1.5, BX1 - BX0, COURSE - 3); ctx.stroke()
        clip_rect(ctx, BX0, y0 + 1.5, BX1, y1 - 1.5)
        ctx.set_source_rgba(*c, 0.3 * alpha); ctx.set_line_width(1.2)
        for k in range(-30, 120, 10):
            ctx.move_to(BX0 + k, y1); ctx.line_to(BX0 + k + COURSE, y0)
        ctx.stroke(); ctx.restore()


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 slab edge
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 100, 1060, SLAB_X0, 1200, c, reveal=p)
        earth_hatch(ctx, SLAB_X0, 1150, 460, 1200, c, reveal=p)
        earth_hatch(ctx, 460, 1080, 940, 1200, c, reveal=p)
        polyline(ctx, [(100, 1060), (SLAB_X0, 1060)], p, c, 3)
        polyline(ctx, SLAB_PTS, p, c, 3)
        a = clamp((p - 0.4) / 0.6)
        draw_concrete(ctx, CONC, c, 0.7 * a)
        leader(ctx, clamp((t - s1 - 0.9) / 0.8), c, (300, REBATE), (560, 1128), "REBATED SLAB EDGE")

    # 2 frame + roof
    c = tl.col(2, t); p = prog(t, s2, 0.8)
    if p > 0:
        polyline(ctx, rect_pts(FX0, BP0, FX1, BP1), p, c, 3)
        polyline(ctx, rect_pts(FX0, TP0, FX1, TP1), p, c, 3)
        polyline(ctx, [(FX0, TP1), (FX0, BP0)], p, c, 1.6, alpha=0.6)        # stud beyond
        polyline(ctx, [(FX1, TP1), (FX1, BP0)], p, c, 1.6, alpha=0.6)
        polyline(ctx, rect_pts(FX0, 730, FX1, 745), p, c, 2.5)                 # nogging
        dot(ctx, (FX0 + FX1) / 2, 992, 4, c, p)                                # tie-down bolt
    pr = prog(t, s2 + 0.7, 0.9)
    if pr > 0:
        polyline(ctx, rect_pts(150, 455, 940, SOFFIT), pr, c, 3)               # truss bottom chord + eave
        polyline(ctx, [(150, 445), (150, SOFFIT)], pr, c, 3)                   # fascia
        polyline(ctx, [(150, SOFFIT), (FX0, SOFFIT)], pr, c, 2, dash=[6, 4])
    leader(ctx, clamp((t - s2 - 1.4) / 0.8), c, (FX1 - 10, 640), (560, 640), "TIMBER FRAME")

    # 3 wrap
    c = tl.col(3, t); p = prog(t, s3, 0.9)
    if p > 0:
        polyline(ctx, [(FX0 - 3, TP0), (FX0 - 3, BP1)], p, c, 3, dash=[10, 6])
        leader(ctx, clamp((t - s3 - 0.9) / 0.8), c, (FX0 - 3, 760), (560, 760), "WALL WRAP")

    # 4 first courses, flashing, weep
    c = tl.col(4, t)
    n4 = int(2 * clamp((t - s4) / 0.8))
    if n4 > 0: bricks(ctx, c, 1, n4)
    pf = prog(t, s4 + 0.8, 0.8)
    if pf > 0:
        yj = REBATE - 2 * COURSE
        polyline(ctx, [(BX0 + 6, yj), (BX1, yj), (FX0 - 6, yj - 14), (FX0 - 6, yj - 60)], pf, c, 3)
        leader(ctx, clamp((t - s4 - 1.2) / 0.8), c, (BX1 + 10, yj - 2), (110, 1150), "FLASHING")
        ctx.set_source_rgba(*c, pf); ctx.set_line_width(2.5)                   # weep hole arrow
        ctx.move_to(BX0 + 20, REBATE - COURSE / 2); ctx.line_to(BX0 - 30, REBATE - COURSE / 2); ctx.stroke()
        ctx.move_to(BX0 - 30, REBATE - COURSE / 2); ctx.line_to(BX0 - 20, REBATE - COURSE / 2 - 7)
        ctx.move_to(BX0 - 30, REBATE - COURSE / 2); ctx.line_to(BX0 - 20, REBATE - COURSE / 2 + 7); ctx.stroke()
        leader(ctx, clamp((t - s4 - 1.5) / 0.8), c, (BX0 - 30, REBATE - COURSE / 2), (110, 1192), "WEEP HOLE")

    # 5 ties
    c = tl.col(5, t)
    for i, n in enumerate(TIE_COURSES):
        pt = prog(t, s5 + i * 0.25, 0.5)
        if pt <= 0: continue
        y = REBATE - n * COURSE
        pts = [(FX0, y - 10), (FX0 - 14, y - 10), (FX0 - 20, y - 4), (FX0 - 28, y - 10), (FX0 - 34, y - 4), (BX1 - 2, y), (BX0 + 30, y)]
        polyline(ctx, pts, pt, c, 2.5)
        dot(ctx, FX0, y - 10, 4, c, pt)
    leader(ctx, clamp((t - s5 - 1.2) / 0.8), c, (FX0 - 26, REBATE - 16 * COURSE - 7), (560, 820), "WALL TIE")

    # 6 brickwork up
    c = tl.col(6, t)
    n6 = 2 + int((N_COURSES - 2) * clamp((t - s6) / 2.0))
    if n6 > 2: bricks(ctx, c, 3, n6)
    leader(ctx, clamp((t - s6 - 1.2) / 0.8), c, (BX0 + 30, 600), (110, 640), "BRICK")
    leader(ctx, clamp((t - s6 - 1.6) / 0.8), c, ((BX1 + FX0) / 2, 700), (560, 700), "CAVITY")

    # 7 insulation + plasterboard
    c = tl.col(7, t); p = prog(t, s7, 1.0)
    if p > 0:
        clip_rect(ctx, FX0 + 2, TP1 + 2, FX1 - 2, TP1 + 2 + (BP0 - TP1 - 4) * p)
        ctx.set_source_rgba(*c, 0.7); ctx.set_line_width(2)
        y = TP1 + 6; flip = 0
        ctx.move_to(FX0 + 6, y)
        while y < BP0:                                      # batt symbol: zig loops across the stud zone
            ctx.curve_to(FX1 + 8, y, FX1 + 8, y + 18, FX0 + 6, y + 18) if flip == 0 else ctx.curve_to(FX0 - 8, y, FX0 - 8, y + 18, FX1 - 6, y + 18)
            y += 18; flip ^= 1
        ctx.stroke(); ctx.restore()
        leader(ctx, clamp((t - s7 - 0.6) / 0.8), c, ((FX0 + FX1) / 2, 880), (560, 880), "INSULATION")
    pp = prog(t, s7 + 0.9, 0.7)
    if pp > 0:
        polyline(ctx, rect_pts(PB0, TP1, PB1, BP0), pp, c, 2.5)
        leader(ctx, clamp((t - s7 - 1.3) / 0.8), c, (PB1, 940), (560, 940), "PLASTERBOARD")

    # 8 shrinkage gap
    c = tl.col(8, t); p = prog(t, s8, 0.6)
    if p > 0:
        for y in (SOFFIT, BRICK_TOP):
            polyline(ctx, [(BX0 - 26, y), (BX0 - 6, y)], p, c, 2)
        polyline(ctx, [(BX0 - 16, SOFFIT - 16), (BX0 - 16, BRICK_TOP + 16)], p, c, 2)
        leader(ctx, clamp((t - s8 - 0.5) / 0.8), c, (BX1 - 20, (SOFFIT + BRICK_TOP) / 2), (560, 520), "SHRINKAGE GAP")
        leader(ctx, clamp((t - s8 - 0.9) / 0.8), c, (300, SOFFIT - 2), (560, 445), "EAVE LINING")

    # result dims
    r0 = tl.res0
    dim_h(ctx, 432, BX0, BX1, "110", prog(t, r0, 0.6))
    dim_h(ctx, 432, BX1, FX0 - 3, "50", prog(t, r0 + 0.3, 0.6))
    dim_h(ctx, 432, FX0, FX1, "90", prog(t, r0 + 0.6, 0.6))
