"""011 Re-stumping an older house (reno)."""
import math
from engine.blueprint import *

META = {
    "category": "reno",
    "title": "RE-STUMPING",
    "subtitle": "RENOVATION  //  TYPICAL AU METHOD",
    "dwg": "011",
    "drawing": "RE-STUMPING",
    "section_label": "SECTION ALONG BEARER  (NTS)",
    "hook": ["SLOPING FLOORS?", "STICKING DOORS?", "CHECK THE STUMPS."],
    "hook_sub": "HOW A HOUSE IS RE-STUMPED",
    "cover": ["SLOPING FLOORS?", "TIME FOR", "NEW STUMPS."],
    "steps": [
        ("OLD STUMPS", "Timber stumps rot at ground level or sink. The floor drops and doors start to stick."),
        ("CHECK LEVELS", "The floor is surveyed to see how far out it is. A permit is arranged where required."),
        ("JACK IT UP", "Hydraulic jacks lift the bearers just enough to take the weight off the old stumps."),
        ("OLD STUMPS OUT", "The old stumps are cut free and dug out of the ground."),
        ("DIG & FOOTING", "Each hole goes down to firm ground. A concrete footing goes in the bottom."),
        ("NEW STUMPS", "Concrete or steel stumps are set in, each cut to height off a laser level."),
        ("LOWER & FIX", "The house comes down onto the new stumps. Packers fill gaps and each stump is tied to the bearer."),
        ("BACKFILL", "Holes backfilled. Cracked plaster patched and doors adjusted to close again."),
    ],
    "result": "A level floor on new stumps, sitting on firm ground again.",
}

NARRATION = {
    "hook": "Sloping floors and sticking doors? The stumps might be the problem. Here's how a house is re-stumped.",
    "steps": [
        "Many older Australian houses sit on timber stumps. Over time, they rot at ground level, or sink. The floor drops, and doors start to stick.",
        "First, the floor levels are surveyed, to see how far out it is. A permit is arranged where required.",
        "Hydraulic jacks lift the bearers. Just enough to take the weight off the old stumps.",
        "The old stumps are cut free. Then they're dug out of the ground.",
        "Each hole is dug down to firm ground. A concrete footing goes in the bottom.",
        "New concrete or steel stumps are set in place. Each one is cut to height off a laser level.",
        "The house is lowered onto the new stumps. Packers fill any gaps. Then each stump is tied to the bearer.",
        "The holes are backfilled. Inside, cracked plaster is patched, and doors are adjusted to close again.",
    ],
    "result": "A level floor, on new stumps, sitting on firm ground again.",
    "end": "Follow for more.",
}

CAPTION = """Sloping floors and sticking doors? It might be the stumps 👇 How an older Australian house is re-stumped.

Typical: floor levels surveyed, bearers jacked and temporarily supported, old timber stumps cut out and dug up, holes dug to firm ground, concrete footings, new concrete or adjustable steel stumps set to a level line, packed and tied down to the bearers, then holes backfilled and the inside made good (plaster cracks, doors, windows).
Stump size, spacing, footing depth and tie-downs depend on the soil and the design. Check with your building surveyor about permits.
Typical only. Your engineer's design governs.

#restumping #renovation #renovationaustralia #oldhouse #homereno #construction #builder #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
GND = 1000                           # ground line
BX0, BX1 = 110, 970                  # bearer run
BT, BB = 720, 770                    # bearer top / underside (level)
J_TOP = 676                          # joists sit on the bearer (seen cut)
FL_TOP = 664                         # floorboards
WALL_X0, WALL_X1, WALL_TOP = 160, 520, 530
DOOR = (340, 440, 560)               # door opening x0, x1, head
STUMPS = [200, 400, 600, 800]
SW = 28                              # stump width
OLD_BOT = 1070                       # old stump embedment
HOLE_W, HOLE_BOT = 38, 1095          # half-width of the new hole, hole bottom
FOOT_TOP = 1052                      # top of the concrete footing
NEW_TOP = 780                        # new stump top (packer fills 770..780)
SAG = 24                             # how far the sunken part of the floor has dropped
LIFT = 14                            # jacked just above level
JACKS = [300, 500, 700]

CONC_FOOT = concrete_points(111, 90, FOOT_TOP, 990, HOLE_BOT, 160,
                            lambda x, y: any(abs(x - s) < HOLE_W - 3 for s in STUMPS) and FOOT_TOP + 3 < y < HOLE_BOT - 3)
CONC_STUMP = concrete_points(112, 90, NEW_TOP, 990, FOOT_TOP, 200,
                             lambda x, y: any(abs(x - s) < SW / 2 - 3 for s in STUMPS) and NEW_TOP + 3 < y < FOOT_TOP - 3)


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


def sag(x): return SAG * math.exp(-((x - 600) / 170) ** 2)


def house_dy(x, t, tl):
    """Vertical offset of the house at x: sagging at first, jacked level (and a little high), then lowered."""
    k = prog(t, tl.s(3) + 0.6, 1.4)
    lift = LIFT * k - LIFT * prog(t, tl.s(7) + 0.2, 0.9)
    return sag(x) * (1 - k) - lift


def bent(pts, t, tl, n=24):
    """Subdivide a polyline and push each point down by house_dy(x)."""
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        for j in range(n if i < len(pts) - 2 else n + 1):
            u = j / n
            x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            out.append((x, y + house_dy(x, t, tl)))
    return out


def draw_house(ctx, t, tl, c, p):
    """Bearer, cut joists, floor and an internal wall, all following the floor's sag."""
    xr = BX0 + (BX1 - BX0) * p
    polyline(ctx, bent(rect_pts(BX0, BT, xr, BB), t, tl), 1, c, 3)
    polyline(ctx, bent([(BX0, FL_TOP), (xr, FL_TOP)], t, tl), 1, c, 2)
    for x in range(130, 960, 60):
        if x + 18 > xr: break
        dy = house_dy(x + 9, t, tl)
        polyline(ctx, rect_pts(x, J_TOP + dy, x + 18, BT + dy), 1, c, 2)
        ctx.move_to(x, J_TOP + dy); ctx.line_to(x + 18, BT + dy)                  # cut-member cross
        ctx.move_to(x + 18, J_TOP + dy); ctx.line_to(x, BT + dy)
        ctx.set_line_width(1.2); ctx.set_source_rgba(*c, 0.6); ctx.stroke()
    pw = clamp((p - 0.4) / 0.6)
    if pw <= 0: return
    wa = 0.75 * pw
    polyline(ctx, bent([(WALL_X0, FL_TOP - 12), (WALL_X1, FL_TOP - 12)], t, tl), 1, c, 2, alpha=wa)
    polyline(ctx, bent([(WALL_X0, WALL_TOP + 12), (WALL_X1, WALL_TOP + 12)], t, tl), 1, c, 2, alpha=wa)
    polyline(ctx, bent([(WALL_X0, WALL_TOP), (WALL_X1, WALL_TOP)], t, tl), 1, c, 2, alpha=wa)
    for x in list(range(WALL_X0, WALL_X1 + 1, 60)) + [DOOR[0] - 10, DOOR[1]]:
        if DOOR[0] - 10 < x < DOOR[1] and x not in (DOOR[0] - 10,): continue
        dy = house_dy(x, t, tl)
        polyline(ctx, rect_pts(x, WALL_TOP + 12 + dy, x + 10, FL_TOP - 12 + dy), 1, c, 1.6, alpha=wa)
    polyline(ctx, bent([(DOOR[0], DOOR[2]), (DOOR[1], DOOR[2])], t, tl), 1, c, 2, alpha=wa)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    holes = prog(t, s5, 0.7)                  # holes open up in step 5
    fill = prog(t, s8, 1.0)                   # and are backfilled in step 8

    # 1 ground
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 90, GND, 990, 1110, c, reveal=p)
        polyline(ctx, [(90, GND), (990, GND)], p, c, 3)
    if holes > 0:                              # dug holes (cleared hatch), then backfill fades the hatch back in
        for s in STUMPS:
            ctx.set_source_rgba(*BG, holes * (1 - fill))
            ctx.rectangle(s - HOLE_W + 1, GND - 2, 2 * HOLE_W - 2, HOLE_BOT - GND + 1); ctx.fill()
            a = 1 - fill
            polyline(ctx, [(s - HOLE_W, GND), (s - HOLE_W, HOLE_BOT), (s + HOLE_W, HOLE_BOT), (s + HOLE_W, GND)],
                     holes, tl.col(5, t), 2.5, alpha=1 - 0.75 * fill)
        if fill > 0:
            polyline(ctx, [(90, GND), (990, GND)], 1, tl.col(8, t), 3, alpha=fill)

    # 1 old timber stumps (the sunken one sits lower), rot at ground level
    c = tl.col(1, t)
    for i, s in enumerate(STUMPS):
        po = prog(t, s1 + 0.3 + i * 0.15, 0.6) * (1 - prog(t, s4 + 0.2 + i * 0.3, 0.6))
        if po <= 0: continue
        top = BB + sag(s)                        # old stumps stay where they sank
        bot = OLD_BOT + sag(s)
        lift = prog(t, s4 + 0.2 + i * 0.3, 0.6) * 40     # pulled up as it's dug out
        x0 = s - SW / 2
        polyline(ctx, [(x0, GND), (x0, top - lift), (x0 + SW, top - lift), (x0 + SW, GND)], 1, c, 2.5, alpha=po)
        polyline(ctx, [(x0, GND - lift), (x0, bot - lift), (x0 + SW, bot - lift), (x0 + SW, GND - lift)], 1, c, 2,
                 alpha=po * 0.7, dash=[8, 6])
        for k in range(3):                       # timber grain
            xx = x0 + 7 + k * 7
            polyline(ctx, [(xx, top - lift + 10), (xx, GND - 6)], 1, c, 1, alpha=po * 0.4)
        for k in range(4):                       # rot at ground level
            yy = GND - 18 + k * 9
            polyline(ctx, [(x0 + 2, yy), (x0 + SW - 2, yy + 6)], 1, c, 1.4, alpha=po * 0.8)
        rot = clamp((t - s1 - 1.2) / 0.5) * gone(t, s2 + 0.5)
        if rot > 0:
            ctx.set_source_rgba(*ORANGE, rot * po); ctx.set_line_width(2.5)
            ctx.arc(s, GND - 6, 26, 0, 2 * math.pi); ctx.stroke()

    # 1 the house above (sagging, later level)
    p = prog(t, s1, 1.2)
    if p > 0: draw_house(ctx, t, tl, tl.col(1, t), p)
    label(ctx, clamp((t - s1 - 1.0) / 0.8), c, (130, BB - 25), (110, 445), "BEARER", a=gone(t, s3))
    label(ctx, clamp((t - s1 - 1.4) / 0.8), c, (STUMPS[0] - SW / 2, 900), (110, 1150), "TIMBER STUMP", a=gone(t, s4))
    label(ctx, clamp((t - s1 - 1.8) / 0.8), c, (600 + 26, GND), (940, 1192), "ROT AT GROUND", anchor="r", a=gone(t, s3))

    # 2 levels surveyed: level line + the drop
    c = tl.col(2, t)
    pl = prog(t, s2, 0.9) * gone(t, s4)
    if pl > 0:
        polyline(ctx, [(BX0, BB), (BX1, BB)], pl, BLUE, 2.5, dash=[14, 8])
        pd = prog(t, s2 + 0.8, 0.6) * gone(t, s3 + 1.5)
        if pd > 0:
            for x in (520, 600, 680):
                d = sag(x)
                if d < 6: continue
                polyline(ctx, [(x, BB + 2), (x, BB + d + 2)], pd, ORANGE, 3)
                polyline(ctx, [(x - 7, BB + d - 8), (x, BB + d + 2), (x + 7, BB + d - 8)], pd, ORANGE, 3)
    label(ctx, clamp((t - s2 - 1.0) / 0.8), BLUE, (880, BB), (940, 520), "LEVEL LINE", anchor="r", a=gone(t, s4))
    label(ctx, clamp((t - s2 - 1.5) / 0.8), c, (680, FL_TOP + sag(680)), (560, 445), "OUT OF LEVEL",
          a=gone(t, s3 + 1.5))

    # 3 hydraulic jacks between the stumps (out once the house is down on the new stumps)
    c = tl.col(3, t)
    out = gone(t, s7 + 1.6, 0.6)
    for i, x in enumerate(JACKS):
        pj = prog(t, s3 + i * 0.2, 0.5) * out
        if pj <= 0: continue
        top = BB + house_dy(x, t, tl)
        polyline(ctx, rect_pts(x - 34, GND - 14, x + 34, GND), 1, c, 2, alpha=pj)          # timber pad
        polyline(ctx, rect_pts(x - 16, GND - 70, x + 16, GND - 14), 1, c, 2.5, alpha=pj)   # jack body
        ram = GND - 70 - (GND - 70 - top - 10) * pj
        polyline(ctx, rect_pts(x - 7, ram, x + 7, GND - 70), 1, c, 2.5, alpha=pj)          # ram
        polyline(ctx, rect_pts(x - 20, top, x + 20, min(ram, top + 10)), 1, c, 2.5, alpha=pj)  # head plate
        polyline(ctx, [(x + 16, GND - 50), (x + 34, GND - 64)], 1, c, 2, alpha=pj)          # handle
    if prog(t, s3 + 0.6, 1.4) > 0 and t < s4:
        a = clamp((t - s3 - 0.6) / 0.3) * gone(t, s3 + 2.2)
        for x in JACKS:
            y = BB + 30 + 6 * math.sin(t * 5 + x)
            polyline(ctx, [(x + 40, y + 40), (x + 40, y)], 1, ORANGE, 3, alpha=a)
            polyline(ctx, [(x + 32, y + 10), (x + 40, y - 2), (x + 48, y + 10)], 1, ORANGE, 3, alpha=a)
    label(ctx, clamp((t - s3 - 1.0) / 0.8), c, (JACKS[2] + 16, GND - 45), (940, 1150), "HYDRAULIC JACK", anchor="r",
          a=gone(t, s5))

    # 4 old stumps out: dashed ghosts where they stood
    gh = clamp((t - s4 - 1.0) / 0.5) * gone(t, s5 + 0.4)
    if gh > 0:
        for s in STUMPS:
            polyline(ctx, rect_pts(s - SW / 2, BB + sag(s), s + SW / 2, OLD_BOT + sag(s)), 1, tl.col(4, t), 1.6,
                     alpha=0.6 * gh, dash=[8, 6])
    label(ctx, clamp((t - s4 - 1.2) / 0.8), tl.col(4, t), (STUMPS[1], GND - 30), (110, 1192), "OLD STUMPS OUT",
          a=gone(t, s5))

    # 5 holes to firm ground + concrete footings
    c = tl.col(5, t)
    pf = prog(t, s5 + 0.9, 0.8)
    if pf > 0:
        for s in STUMPS:
            polyline(ctx, rect_pts(s - HOLE_W, FOOT_TOP, s + HOLE_W, HOLE_BOT), pf, c, 2.5)
        draw_concrete(ctx, CONC_FOOT, c, 0.7 * clamp(pf * 2 - 1))
    label(ctx, clamp((t - s5 - 1.4) / 0.8), c, (STUMPS[3] + 30, 1075), (940, 1192), "CONCRETE FOOTING", anchor="r", a=gone(t, s8 + 1.5))

    # 6 new concrete stumps rise out of the footings, cut to a laser line
    c = tl.col(6, t)
    ll = prog(t, s6 + 1.2, 0.8) * gone(t, s7 + 0.4)
    if ll > 0:
        polyline(ctx, [(BX0, NEW_TOP), (BX1, NEW_TOP)], ll, BLUE, 2.5, dash=[14, 8])
    for i, s in enumerate(STUMPS):
        ps = prog(t, s6 + i * 0.25, 0.7)
        if ps <= 0: continue
        top = FOOT_TOP - (FOOT_TOP - NEW_TOP) * ps
        x0 = s - SW / 2
        ctx.set_source_rgba(*BG, 1); ctx.rectangle(x0, top, SW, FOOT_TOP + 20 - top); ctx.fill()
        polyline(ctx, rect_pts(x0, top, x0 + SW, FOOT_TOP + 20), 1, c, 2.5)
        ctx.save(); ctx.rectangle(x0, top, SW, FOOT_TOP - top); ctx.clip()
        draw_concrete(ctx, CONC_STUMP, c, 0.6)
        ctx.restore()
    label(ctx, clamp((t - s6 - 1.0) / 0.8), c, (STUMPS[0] - SW / 2, 900), (110, 1150), "CONCRETE STUMP")
    label(ctx, clamp((t - s6 - 1.8) / 0.8), BLUE, (880, NEW_TOP), (940, 520), "LASER LEVEL", anchor="r",
          a=gone(t, s7 + 0.4))

    # 7 packers + ties to the bearer
    c = tl.col(7, t)
    for i, s in enumerate(STUMPS):
        pp = prog(t, s7 + i * 0.15, 0.4)
        if pp > 0:
            polyline(ctx, rect_pts(s - 18, BB, s + 18, NEW_TOP), pp, c, 2.5)
        pt = prog(t, s7 + 1.4 + i * 0.15, 0.5)
        if pt > 0:
            for sx in (-1, 1):
                x = s + sx * (SW / 2 + 3)
                polyline(ctx, [(x, NEW_TOP + 50), (x, BT + 8)], pt, c, 3)
    label(ctx, clamp((t - s7 - 1.0) / 0.8), c, (STUMPS[2] + 18, BB + 5), (630, 840), "PACKER",
          a=gone(t, s8 + 1.0))
    label(ctx, clamp((t - s7 - 2.0) / 0.8), c, (STUMPS[1] + SW / 2 + 3, NEW_TOP + 30), (430, 900), "TIE-DOWN",
          a=gone(t, s8 + 1.0))

    # 8 backfill + level floor check
    c = tl.col(8, t)
    label(ctx, clamp((t - s8 - 1.0) / 0.8), c, (STUMPS[3] + HOLE_W - 8, GND + 20), (940, 1150), "BACKFILLED", anchor="r")
    pl = prog(t, s8 + 1.4, 0.8)
    if pl > 0:
        polyline(ctx, [(BX0, FL_TOP - 4), (BX1, FL_TOP - 4)], pl, BLUE, 2.5, dash=[14, 8])
    label(ctx, clamp((t - s8 - 2.0) / 0.8), BLUE, (760, FL_TOP - 4), (940, 520), "LEVEL FLOOR", anchor="r")

    # result: stump spacing
    dim_h(ctx, 880, STUMPS[1], STUMPS[2], "SPACING", prog(t, tl.res0, 0.6))


# ---------------------------------------------------------------- 3D model (mm): subfloor on new stumps, floor + wall frame part-built
def model3d():
    from engine.three_d import box
    P = []; o = 0
    XS = [0, 1800, 3600, 5400, 7200]           # stump spacing along the bearers
    ZS = [0, 1800, 3600]                       # bearer lines
    ST, SH = 100, 600                          # stump size, height above ground
    P.append(box(-900, 8100, -150, 0, -900, 4500, o, "ground")); P[-1].base = True; o += 1
    for z in ZS:                               # footings just showing at ground level
        for x in XS:
            P.append(box(x - 200, x + 200, 0, 40, z - 200, z + 200, o, "concrete"))
    o += 1
    for z in ZS:                               # new stumps, one bearer line at a time
        for x in XS:
            P.append(box(x - ST / 2, x + ST / 2, 40, SH, z - ST / 2, z + ST / 2, o, "concrete"))
        o += 1
    for z in ZS:                               # packers
        for x in XS:
            P.append(box(x - 60, x + 60, SH, SH + 20, z - 60, z + 60, o, "steel"))
    o += 1
    for z in ZS:                               # bearers
        P.append(box(-150, 7350, SH + 20, SH + 170, z - 45, z + 45, o))
    o += 1
    for i, x in enumerate(range(-100, 7300, 450)):   # floor joists across the bearers
        P.append(box(x, x + 45, SH + 170, SH + 310, -250, 3850, o + i // 6))
    o += 3
    P.append(box(-150, 3600, SH + 310, SH + 330, -250, 3850, o, "eps")); o += 1      # flooring, half laid
    y0 = SH + 330                                   # wall frame on the floor at the back edge
    P.append(box(-150, 3600, y0, y0 + 45, -250, -160, o))
    for x in range(-150, 3600, 450):
        P.append(box(x, x + 45, y0 + 45, y0 + 2355, -250, -160, o))
    P.append(box(-150, 3600, y0 + 2355, y0 + 2400, -250, -160, o)); o += 1
    cfg = {"target": (3600, 900, 1800), "yaw": 32, "pitch": 22, "dist": 16000, "scale": 1.5,
           "cy_hook": 1030, "cy_result": 830, "cy_cover": 1010, "cover_scale": 1.0}
    return P, cfg
