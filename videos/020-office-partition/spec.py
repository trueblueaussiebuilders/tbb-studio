"""020 Office partition wall with a deflection head (commercial)."""
import math
from engine.blueprint import *

META = {
    "category": "commercial",
    "title": "OFFICE PARTITION",
    "subtitle": "COMMERCIAL  //  TYPICAL AU METHOD",
    "dwg": "020",
    "drawing": "OFFICE PARTITION",
    "section_label": "WALL ELEVATION + HEAD DETAIL  (NTS)",
    "hook": ["THIS OFFICE WALL", "HAS A GAP", "AT THE TOP."],
    "hook_sub": "HOW AN OFFICE PARTITION IS BUILT",
    "cover": ["THE GAP AT", "THE TOP IS", "ON PURPOSE."],
    "question": "Did you know office walls are built to let the floor above move? Yes or no below.",
    "hook_start": 0.5,
    "hook_hot": [3],                   # hook callout (orange on the 3D model): the studs, cut short of the slab
    "xray": {"after_step": 4, "upto": 3, "hot": [3]},     # tracks + studs in, batts and boards still ghosts
    "steps": [
        ("SET OUT", "The wall line is marked on the floor and plumbed up to the slab above."),
        ("FLOOR TRACK", "A steel track is fixed to the floor slab along the line."),
        ("DEFLECTION HEAD", "A track with extra-deep legs is fixed to the slab above."),
        ("STUDS, CUT SHORT", "Studs stand in the tracks, cut short to leave a gap at the top."),
        ("NOGGINGS + CABLES", "Noggings go where things will hang. Cables run through the studs."),
        ("ACOUSTIC BATTS", "Insulation fills the cavity to cut the sound between rooms."),
        ("PLASTERBOARD", "Sheets are screwed to the studs on both sides, never to the top track."),
        ("SEAL + CEILING", "The top gap is sealed with a flexible sealant. Then the ceiling goes in."),
    ],
    "result": "When the slab above sags, the track slides down over the studs. The wall doesn't crack.",
}

NARRATION = {
    "hook": "This office wall has a gap at the top. It's there on purpose.",
    "steps": [
        "First, the wall is set out. A line is marked on the floor, and a laser plumbs it up to the slab above.",
        "A steel floor track is fixed to the slab along the line.",
        "At the top, a deflection head track is fixed to the slab above. Its legs are extra deep.",
        "Steel studs stand in the tracks. They are cut short, so there's a gap at the top. They are not screwed to the top track.",
        "Noggings go in where cabinets or screens will hang. Cables run through the holes in the studs.",
        "Acoustic insulation fills the cavity. It cuts the sound between rooms.",
        "Plasterboard is screwed to the studs on both sides. But never to the top track.",
        "The gap at the top is sealed with a flexible sealant. Then the ceiling goes in.",
    ],
    "result": "When the floor above sags under load, the track slides down over the studs. The wall moves with it, and it doesn't crack.",
    "end": "Follow for more.",
}

CAPTION = """This office wall has a gap at the top 👇 How a partition wall is built.

Typical: office partitions in Australia are usually lightweight steel stud walls. The wall is set out on the floor and plumbed up to the slab above. A floor track is fixed to the slab, and a deflection head track (a top track with deep legs) is fixed to the soffit. Studs, often at 600 or 450 millimetre centres, stand in the tracks and are cut short, so there's a gap under the top track, and they aren't screwed to it. Noggings or fixing plates go where joinery, screens or TVs will hang, and cables run through the punched holes in the studs. Acoustic insulation fills the cavity. Plasterboard is screwed to the studs but not to the top track, and the top joint is sealed with a flexible (and where needed, fire-rated) sealant.
Why: a concrete floor deflects under load and creeps over time. The deflection head lets the slab move down without crushing the wall or cracking the plasterboard.
The gap, stud size and spacing, board layers and any fire or acoustic rating come from the design and the manufacturer's tested system.
Typical only. Your engineer's design governs.

#officefitout #partitionwall #steelframing #plasterboard #commercialconstruction #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
EX0, EX1 = 110, 610                   # wall elevation: left / right end
SX0, SX1 = 70, 630                    # slab above / floor slab extent in the elevation
ST, SB = 425, 475                     # slab above: top / soffit
TRK = 40                              # head track leg depth (elevation)
STUD_TOP = 500                        # stud tops (gap under the track flange)
FT, FB = 1110, 1160                   # floor slab: top / bottom
FTRK = 16                             # floor track height
STUDS = [120, 245, 370, 495, 600]     # stud centres (about 600 centres)
NOG_Y = 820
CABLE_Y = 960
CEIL_Y = 612
SAG = 16                              # result: exaggerated slab deflection at mid-span (px)

# head detail (section through the top of the wall, magnified)
DX0, DX1, DY0, DY1 = 650, 1000, 440, 1010
DSL_T, DSL_B = 495, 555               # detail slab: top / soffit
DTX0, DTX1 = 762, 888                 # detail track outside faces
DLEG = 140                            # detail leg length (to y = DSL_B + DLEG)
DST_TOP = 610                         # detail stud top
DSTUD = (772, 878)
DBRK = 840                            # detail break line (bottom of the detail)
DBOARD = ((744, 760), (890, 906))     # board faces in the detail
DBOARD_TOP = 585
DROWS = (885, 935, 985)               # label rows under the detail

SLAB_CONC = concrete_points(201, SX0, ST, SX1, SB, 130)
FLOOR_CONC = concrete_points(202, SX0, FT, SX1, FB, 130)
DSLAB_CONC = concrete_points(203, DX0 + 6, DSL_T, DX1 - 6, DSL_B, 90)


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


def batt(ctx, x0, x1, y0, y1, col, alpha, p=1.0):
    """Insulation symbol: a zig-zag filling the bay from the bottom up (p = how far up it's filled)."""
    if p <= 0: return
    yt = y1 - (y1 - y0) * p
    pts, y, k = [], y1, 0
    while y > yt:
        pts.append((x0 + 6 if k % 2 == 0 else x1 - 6, y)); y -= 26; k += 1
    if len(pts) > 1: polyline(ctx, pts, 1, col, 2, alpha=alpha)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0
    # result: the slab above sags (exaggerated), the head track goes down with it, the studs stay put
    kd = prog(t, r0 + 0.3, 1.6) * (1 - prog(t, tl.end0 - 0.3, 0.3))
    sag = lambda x: SAG * kd * math.sin(math.pi * clamp((x - SX0) / (SX1 - SX0)))
    dsag = 22 * kd                    # the same movement in the magnified detail

    # ---- existing structure: slab above + floor slab (on from step 1)
    pg = prog(t, s1, 0.8)
    if pg > 0:
        xs = [SX0 + (SX1 - SX0) * i / 24 for i in range(25)]
        top = [(x, ST + sag(x)) for x in xs]; bot = [(x, SB + sag(x)) for x in xs]
        fill_poly(ctx, top + bot[::-1], BG, 1)
        polyline(ctx, top, pg, WHITE, 3); polyline(ctx, bot, pg, WHITE, 3)
        ctx.save(); ctx.translate(0, sag(340)); draw_concrete(ctx, SLAB_CONC, WHITE, 0.4 * pg); ctx.restore()
        polyline(ctx, [(SX0, FT), (SX1, FT)], pg, WHITE, 3)
        polyline(ctx, [(SX0, FB), (SX1, FB)], pg, WHITE, 2, alpha=0.6)
        draw_concrete(ctx, FLOOR_CONC, WHITE, 0.4 * pg)
        text(ctx, "SLAB ABOVE", 340, ST + 34 + sag(340), 22, WHITE, alpha=0.75 * pg * gone(t, s3 + 0.2), bold=True,
             anchor="c", spacing=3)
        text(ctx, "FLOOR SLAB", 340, FT + 34, 22, WHITE, alpha=0.75 * pg * gone(t, s2 + 0.2), bold=True, anchor="c",
             spacing=3)

    # ---- 1 set out: chalk line ends, laser plumb lines up the wall ends, ghost of the wall
    c1 = tl.col(1, t)
    kl = prog(t, s1 + 0.5, 0.8) * gone(t, s4 + 0.5)
    if kl > 0:
        for x in (EX0, EX1):
            polyline(ctx, [(x, FT - 4), (x, SB + 2)], kl, ORANGE, 2, alpha=0.85, dash=[10, 7])
            dot(ctx, x, FT - 4, 6, ORANGE, kl)
    kg = prog(t, s1 + 1.2, 0.8) * gone(t, s3 + 0.4)
    if kg > 0:
        polyline(ctx, rect_pts(EX0, SB, EX1, FT), 1, BLUE, 2, alpha=0.5 * kg, dash=[10, 8])
    label(ctx, clamp((t - s1 - 1.0) / 0.8), ORANGE, (EX0, 700), (EX0 + 50, 700), "LASER PLUMB LINE", a=gone(t, s2 + 0.3))
    label(ctx, clamp((t - s1 - 2.0) / 0.8), c1, (EX1, FT - 4), (EX1 - 50, 1040), "WALL LINE", anchor="r",
          a=gone(t, s2 + 0.3))

    # ---- 2 floor track + fixings
    c2 = tl.col(2, t)
    kf = prog(t, s2 + 0.2, 0.9)
    if kf > 0:
        polyline(ctx, rect_pts(EX0, FT - FTRK, EX1, FT), kf, c2, 3)
        for i, x in enumerate(range(EX0 + 60, EX1, 120)):
            k = prog(t, s2 + 1.0 + i * 0.15, 0.3)
            if k > 0:
                polyline(ctx, [(x, FT - FTRK - 2), (x, FT + 18)], k, c2, 3)
    label(ctx, clamp((t - s2 - 0.9) / 0.8), c2, (300, FT - FTRK), (330, 1040), "FLOOR TRACK", a=gone(t, s3 + 0.3))

    # ---- 3 deflection head track (elevation: the deep leg hangs below the soffit)
    c3 = tl.col(3, t)
    kh = prog(t, s3 + 0.2, 0.9)
    if kh > 0:
        xs = [EX0 + (EX1 - EX0) * i / 20 for i in range(21)]
        top = [(x, SB + sag(x)) for x in xs]; bot = [(x, SB + TRK + sag(x)) for x in xs]
        fill_poly(ctx, top + bot[::-1], BG, 1)
        polyline(ctx, top + bot[::-1] + [top[0]], kh, c3, 3)
    label(ctx, clamp((t - s3 - 0.9) / 0.8), c3, (200, SB + TRK), (150, 580), "DEFLECTION HEAD TRACK",
          a=gone(t, s4 + 0.3))

    # ---- 4 studs (cut short: their tops stop inside the track legs, shown dashed behind the leg)
    c4 = tl.col(4, t)
    for i, x in enumerate(STUDS):
        k = prog(t, s4 + 0.2 + i * 0.2, 0.6)
        if k <= 0: continue
        yt = FT - FTRK - (FT - FTRK - STUD_TOP) * k
        y_leg = SB + TRK + sag(x)
        ctx.save(); ctx.rectangle(0, y_leg, W, H); ctx.clip()
        fill_poly(ctx, rect_pts(x - 7, yt, x + 7, FT - FTRK)[:4], BG, 1)
        polyline(ctx, rect_pts(x - 7, yt, x + 7, FT - FTRK), 1, c4, 2.5)
        ctx.restore()
        if yt < y_leg:
            polyline(ctx, [(x - 7, y_leg), (x - 7, yt), (x + 7, yt), (x + 7, y_leg)], 1, c4, 1.6, alpha=0.7, dash=[5, 4])
    label(ctx, clamp((t - s4 - 1.3) / 0.8), c4, (STUDS[2] + 7, 700), (STUDS[2] + 50, 700), "STEEL STUDS",
          a=gone(t, s5 + 0.3))

    # ---- 5 noggings + a cable through the stud holes, power outlet
    c5 = tl.col(5, t)
    for i in range(len(STUDS) - 1):
        k = prog(t, s5 + 0.2 + i * 0.2, 0.4)
        if k > 0:
            polyline(ctx, rect_pts(STUDS[i] + 7, NOG_Y - 7, STUDS[i] + 7 + (STUDS[i + 1] - STUDS[i] - 14) * k, NOG_Y + 7),
                     1, c5, 2.5)
    kc = prog(t, s5 + 1.3, 1.2)
    if kc > 0:
        pts = [(EX0 - 30, CABLE_Y)] + [(x, CABLE_Y) for x in STUDS[1:4]] + [(STUDS[3] + 40, CABLE_Y),
                                                                           (STUDS[3] + 40, CABLE_Y + 50)]
        polyline(ctx, pts, kc, ORANGE if t < s8 else WHITE, 3)
        for x in STUDS:
            if x - 7 < EX0 - 30 + (STUDS[3] + 40 - EX0 + 30) * kc:
                ctx.set_source_rgba(*c5, 0.9); ctx.set_line_width(2)
                ctx.arc(x, CABLE_Y, 8, 0, 2 * math.pi); ctx.stroke()
        if kc >= 1:
            polyline(ctx, rect_pts(STUDS[3] + 22, CABLE_Y + 50, STUDS[3] + 58, CABLE_Y + 96), prog(t, s5 + 2.5, 0.4), c5, 3)
    label(ctx, clamp((t - s5 - 0.9) / 0.8), c5, (300, NOG_Y - 7), (330, 740), "NOGGING", a=gone(t, s6 + 0.3))
    label(ctx, clamp((t - s5 - 2.0) / 0.8), ORANGE, (STUDS[2], CABLE_Y), (150, 1040), "CABLE THROUGH STUDS",
          a=gone(t, s6 + 0.3))

    # ---- 6 acoustic batts in each bay
    c6 = tl.col(6, t)
    for i in range(len(STUDS) - 1):
        batt(ctx, STUDS[i] + 9, STUDS[i + 1] - 9, STUD_TOP + 12, FT - FTRK - 4, c6, 0.55,
             prog(t, s6 + 0.2 + i * 0.3, 0.9))
    label(ctx, clamp((t - s6 - 1.4) / 0.8), c6, (STUDS[1] + 60, 660), (STUDS[1] + 60, 580), "ACOUSTIC BATTS",
          a=gone(t, s7 + 0.3))

    # ---- 7 plasterboard: two sheets on the near face (cutaway: the right bays stay open)
    c7 = tl.col(7, t)
    for j, (a, b) in enumerate([(EX0, 245), (245, 370)]):
        k = prog(t, s7 + 0.2 + j * 0.5, 0.6)
        if k <= 0: continue
        yt = FT - 2 - (FT - 2 - (SB + 12)) * k
        fill_poly(ctx, rect_pts(a + 1, yt, b - 1, FT - 2)[:4], BG, 0.92)
        fill_poly(ctx, rect_pts(a + 1, yt, b - 1, FT - 2)[:4], BLUE, 0.16)
        polyline(ctx, rect_pts(a + 1, yt, b - 1, FT - 2), 1, c7, 2.5)
        if k >= 1:                                         # screw lines on the studs (not into the top track)
            for x in (a + 10, (a + b) / 2, b - 10):
                for y in range(int(SB + TRK + 60), FT - 30, 90):
                    dot(ctx, x, y, 2.5, c7, 0.9)
    label(ctx, clamp((t - s7 - 1.0) / 0.8), c7, (180, 760), (180, 660), "PLASTERBOARD", a=gone(t, s8 + 0.3))

    # ---- 8 suspended ceiling (section) with hangers up to the slab
    c8 = tl.col(8, t)
    kce = prog(t, s8 + 1.4, 0.9)
    if kce > 0:
        polyline(ctx, [(SX0, CEIL_Y), (SX1, CEIL_Y)], kce, c8, 4)
        for x in range(SX0 + 40, SX1, 140):
            polyline(ctx, [(x, SB + sag(x)), (x, CEIL_Y)], kce, c8, 1.6, alpha=0.7, dash=[6, 5])
    label(ctx, clamp((t - s8 - 2.0) / 0.8), c8, (520, CEIL_Y), (520, 700), "SUSPENDED CEILING", anchor="r",
          a=gone(t, r0))

    # ---- head detail (from step 3): slab, deep-leg track, stud cut short, boards, sealant
    head_detail(ctx, t, tl, dsag)

    # ---- result
    pt = prog(t, r0 + 0.6, 0.5)
    if pt > 0:
        arrow(ctx, 340, ST + 4 + sag(340), 340, SB - 4 + sag(340), ORANGE, p=pt, head=10, width=4)
        text(ctx, "SLAB SAGS. TRACK SLIDES. NO CRACKS.", 540, 1205, 30, ORANGE, alpha=pt, bold=True, anchor="c")
        text(ctx, "MOVEMENT EXAGGERATED", 340, 1060, 20, WHITE, alpha=0.6 * pt, bold=True, anchor="c", spacing=2)


def head_detail(ctx, t, tl, dsag):
    s3, s4, s5, s7, s8 = tl.s(3), tl.s(4), tl.s(5), tl.s(7), tl.s(8)
    r0 = tl.res0
    kb = prog(t, s3 + 0.2, 0.5)
    if kb <= 0: return
    ctx.push_group()
    fill_poly(ctx, rect_pts(DX0, DY0, DX1, DY1)[:4], BG, 0.95)
    polyline(ctx, rect_pts(DX0, DY0, DX1, DY1), 1, BLUE, 2, alpha=0.8)
    text(ctx, "HEAD DETAIL", DX0 + 14, DY0 + 32, 24, BLUE, bold=True, spacing=3)
    ctx.save(); ctx.rectangle(DX0 + 2, DY0 + 44, DX1 - DX0 - 4, DBRK - DY0 - 30); ctx.clip()
    # slab above (moves down in the result)
    y0, y1 = DSL_T + dsag, DSL_B + dsag
    polyline(ctx, [(DX0, y1), (DX1, y1)], 1, WHITE, 3)
    ctx.save(); ctx.translate(0, dsag); draw_concrete(ctx, DSLAB_CONC, WHITE, 0.45); ctx.restore()
    polyline(ctx, [(DX0, y0), (DX1, y0)], 1, WHITE, 2, alpha=0.5)
    # deep-leg track: flange under the soffit, two legs down
    c3 = tl.col(3, t)
    kt = prog(t, s3 + 0.5, 0.9)
    if kt > 0:
        yl = y1 + DLEG
        polyline(ctx, [(DTX0, yl), (DTX0, y1 + 1), (DTX1, y1 + 1), (DTX1, yl)], kt, c3, 4)
        polyline(ctx, [(DTX0 + 6, yl), (DTX0 + 6, y1 + 7), (DTX1 - 6, y1 + 7), (DTX1 - 6, yl)], kt, c3, 1.6, alpha=0.7)
        if kt >= 1:
            polyline(ctx, [(825, y0 + 15), (825, y1 + 8)], prog(t, s3 + 1.4, 0.4), c3, 3)   # fixing into the slab
    # stud, cut short: top well below the flange
    c4 = tl.col(4, t)
    ks = prog(t, s4 + 0.2, 0.8)
    if ks > 0:
        yt = DBRK + 20 - (DBRK + 20 - DST_TOP) * ks
        fill_poly(ctx, rect_pts(DSTUD[0], yt, DSTUD[1], DBRK + 20)[:4], BG, 1)
        polyline(ctx, [(DSTUD[0], DBRK + 20), (DSTUD[0], yt), (DSTUD[1], yt), (DSTUD[1], DBRK + 20)], 1, c4, 3)
        polyline(ctx, [(DSTUD[0] + 10, yt + 2), (DSTUD[0] + 10, DBRK + 20)], 1, c4, 1.4, alpha=0.6)
        polyline(ctx, [(DSTUD[1] - 10, yt + 2), (DSTUD[1] - 10, DBRK + 20)], 1, c4, 1.4, alpha=0.6)
    # plasterboard both sides, stopping short of the soffit; screws into the stud only, below the legs
    c7 = tl.col(7, t)
    kp = prog(t, s7 + 0.2, 0.9)
    if kp > 0:
        for a, b in DBOARD:
            yt = DBRK + 20 - (DBRK + 20 - DBOARD_TOP) * kp
            fill_poly(ctx, rect_pts(a, yt, b, DBRK + 20)[:4], BLUE, 0.22)
            polyline(ctx, [(a, DBRK + 20), (a, yt), (b, yt), (b, DBRK + 20)], 1, c7, 2.5)
        for y in (DSL_B + DLEG + 40, DSL_B + DLEG + 110):
            k = prog(t, s7 + 1.4, 0.4)
            if k > 0:
                polyline(ctx, [(DBOARD[0][0] - 6, y), (DSTUD[0] + 16, y)], k, c7, 3)
                polyline(ctx, [(DBOARD[1][1] + 6, y), (DSTUD[1] - 16, y)], k, c7, 3)
    # flexible sealant between the board tops and the soffit (squeezes as the slab comes down)
    ke = prog(t, s8 + 0.2, 0.8)
    if ke > 0:
        for a, b in DBOARD:
            ytop = y1 + 1
            yb = DBOARD_TOP
            fill_poly(ctx, rect_pts(a - 4, ytop + (yb - ytop) * (1 - ke), b + 4, yb)[:4], ORANGE, 0.85)
    ctx.restore()
    # break line at the bottom of the detail
    polyline(ctx, [(DX0 + 40, DBRK + 8), (790, DBRK + 8), (805, DBRK - 8), (820, DBRK + 22), (835, DBRK + 8),
                   (DX1 - 40, DBRK + 8)], 1, WHITE, 1.6, alpha=0.6)
    # the gap (dimension), shrinking in the result
    kg = prog(t, s4 + 1.0, 0.6) * (1 - prog(t, s7 + 0.1, 0.3) * (1 - prog(t, r0 + 0.3, 0.4)))
    if kg > 0 and DSL_B + dsag + 7 < DST_TOP - 6:
        dim_v(ctx, 955, DSL_B + dsag + 7, DST_TOP, "GAP", kg, ORANGE)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(kb)

    # labels under the detail (rows), each fades when the next step starts
    r1, r2, r3 = DROWS
    label(ctx, clamp((t - s3 - 1.0) / 0.8), c3, (DTX0, DSL_B + DLEG - 20), (DX0 + 18, r1), "DEEP LEGS",
          a=gone(t, s4 + 0.3) * kb)
    label(ctx, clamp((t - s4 - 1.6) / 0.8), c4, (DSTUD[0] + 20, DST_TOP + 4), (DX0 + 18, r2), "STUD CUT SHORT",
          a=gone(t, s5 + 0.3))
    label(ctx, clamp((t - s4 - 2.4) / 0.8), c4, (DSTUD[1] - 20, DST_TOP + 70), (DX1 - 18, r3), "NOT FIXED AT TOP", anchor="r",
          a=gone(t, s5 + 0.3))
    label(ctx, clamp((t - s7 - 1.2) / 0.8), c7, (DBOARD[0][0] - 6, DSL_B + DLEG + 40), (DX0 + 18, r3),
          "SCREWS INTO STUD", a=gone(t, s8 + 0.3))
    label(ctx, clamp((t - s7 - 2.0) / 0.8), c7, (DBOARD[1][1], DSL_B + 60), (DX1 - 18, r1), "NONE IN TRACK", anchor="r",
          a=gone(t, s8 + 0.3))
    label(ctx, clamp((t - s8 - 0.9) / 0.8), ORANGE, (DBOARD[0][0] - 2, DBOARD_TOP - 12), (DX0 + 18, r3),
          "FLEXIBLE SEALANT", a=gone(t, r0))


# ---------------------------------------------------------------- 3D model (mm): an L of partition walls
def model3d():
    from engine.three_d import box
    P = []
    g = box(-600, 5500, -200, 0, -1200, 4100, 0, "ground"); g.base = True; P.append(g)
    L, D, HT = 4800, 3600, 2700                 # wall A along x, wall B along z, slab soffit
    TW = 46                                     # half the stud depth (92 mm studs)
    # 0 slab above: a cut-away strip over the wall line only, so the wall stays visible
    P.append(box(-300, L + 400, HT, HT + 200, -350, 350, 0, "concrete"))
    P.append(box(L - 350, L + 400, HT, HT + 200, 350, D + 300, 0, "concrete"))
    # 1 floor tracks
    P.append(box(0, L + TW, 0, 30, -TW, TW, 1, "steel"))
    P.append(box(L - TW, L + TW, 0, 30, TW, D, 1, "steel"))
    # 2 deflection head tracks (deep legs)
    P.append(box(0, L + TW, HT - 90, HT, -TW - 4, TW + 4, 2, "steel"))
    P.append(box(L - TW - 4, L + TW + 4, HT - 90, HT, TW, D, 2, "steel"))
    # 3 studs, cut short (top at HT - 40, inside the legs)
    for x in range(0, L + 1, 600):
        P.append(box(x - 20 if x else 0, x + 20 if x < L else L + TW, 30, HT - 40, -TW, TW, 3, "steel"))
    for z in range(600, D + 1, 600):
        P.append(box(L - TW, L + TW, 30, HT - 40, z - 20, z + 20, 3, "steel"))
    # 4 noggings
    P.append(box(0, L, 1180, 1230, -TW + 6, TW - 6, 4, "steel"))
    P.append(box(L - TW + 6, L + TW - 6, 1180, 1230, TW, D, 4, "steel"))
    # 5 acoustic batts: wall A's middle bays only (cut-away), all of wall B
    for x in range(1800, 3600, 600):
        P.append(box(x + 20, x + 580, 30, HT - 120, -38, 38, 5, "eps"))
    for z in range(0, D, 600):
        P.append(box(L - 38, L + 38, 30, HT - 120, z + 66 if z == 0 else z + 20, z + 580, 5, "eps"))
    # 6 plasterboard: the inside faces in full; the outside faces (towards the camera) only over the end bays,
    #   so the finished model is a cut-away that still shows the studs and batts
    P.append(box(0, L - TW, 30, HT - 10, TW, TW + 13, 6, "board"))
    P.append(box(0, 1200, 30, HT - 10, -TW - 13, -TW, 6, "board"))
    P.append(box(L - TW - 13, L - TW, 30, HT - 10, TW + 13, D, 6, "board"))
    P.append(box(L + TW, L + TW + 13, 30, HT - 10, D - 1200, D, 6, "board"))
    cfg = {"target": (2600, 1200, 1300), "yaw": -130, "pitch": 22, "dist": 22000, "scale": 2.4,
           "cy_hook": 1060, "cy_result": 820, "cy_cover": 980, "cover_scale": 0.9}
    return P, cfg
