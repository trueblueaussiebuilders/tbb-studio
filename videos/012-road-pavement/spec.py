"""012 Road pavement layers (civil)."""
import math
from engine.blueprint import *

META = {
    "category": "civil",
    "title": "ROAD PAVEMENT",
    "subtitle": "CIVIL  //  TYPICAL AU METHOD",
    "dwg": "012",
    "drawing": "ROAD PAVEMENT",
    "section_label": "SECTION ACROSS ROAD  (NTS)",
    "hook": ["THE BLACK STUFF", "IS THE THIN BIT.", "IT'S MOSTLY ROCK."],
    "hook_sub": "HOW A ROAD IS BUILT",
    "cover": ["WHAT'S UNDER", "THE ROAD?", "MOSTLY ROCK."],
    "xray": {"after_step": 5, "upto": 5, "hot": [3, 4, 5]},     # kerb and channel on the subbase
    "steps": [
        ("BOX OUT", "Topsoil is stripped. Then the road is dug out down to the design level."),
        ("SUBGRADE", "The natural ground is trimmed to shape and rolled. Soft spots are dug out and replaced."),
        ("SUBSOIL DRAINS", "Trenches along each edge get a slotted pipe, wrapped in fabric and backfilled with gravel."),
        ("SUBBASE", "Crushed rock goes down in layers. Each layer is watered and rolled until it's tight."),
        ("KERB & CHANNEL", "A slip-form machine extrudes the concrete kerb and channel along each edge."),
        ("BASE", "A higher grade crushed rock goes on top. It's trimmed to the final shape and rolled again."),
        ("PRIME & ASPHALT", "A bitumen prime is sprayed on. Then a paver lays hot asphalt and rollers compact it."),
        ("LINES & VERGES", "Line marking goes on the road. The verges are topsoiled and grassed."),
    ],
    "result": "A road that's mostly crushed rock, with a thin asphalt skin on top. Shaped so water runs off.",
}

NARRATION = {
    "hook": "The asphalt is the thin bit. A road is mostly crushed rock.",
    "steps": [
        "First, the topsoil is stripped. Then the road is dug out, down to the design level. This is called boxing out.",
        "The natural ground underneath is the subgrade. It's trimmed to shape and rolled. Any soft spots are dug out and replaced.",
        "Next, subsoil drains go in along each edge. A slotted pipe is wrapped in fabric, then backfilled with gravel. They keep groundwater out of the road.",
        "The subbase goes down next. It's crushed rock, placed in layers. Each layer is watered and rolled until it's tight.",
        "Then a slip-form machine extrudes the concrete kerb and channel along each edge.",
        "A higher grade crushed rock goes on top. This is the base. It's trimmed to the final shape and rolled again.",
        "A bitumen prime is sprayed on the base. Then a paver lays hot asphalt, and rollers compact it while it's still hot.",
        "Finally, the line marking goes on. The verges are topsoiled and grassed.",
    ],
    "result": "A road that's mostly crushed rock, with a thin asphalt skin on top. And it's shaped so the water runs off to the kerbs.",
    "end": "Follow for more.",
}

CAPTION = """The asphalt is the thin bit 👇 How a typical Australian road is built, layer by layer.

Typical flexible pavement: topsoil stripped and the road boxed out, subgrade trimmed, rolled and proof rolled (soft spots dug out and replaced), subsoil drains along the edges, crushed rock subbase in compacted layers, slip-formed concrete kerb and channel, a higher grade crushed rock base trimmed to shape, a bitumen prime, then asphalt laid by a paver and rolled hot. Line marking and verges finish it off. The road has a crossfall so water runs to the kerbs.
Layer types and thicknesses depend on the subgrade, the traffic and the design.
Typical only. Your engineer's design governs.

#roadconstruction #civilengineering #asphalt #pavement #roadworks #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS; layers exaggerated)
NS = 720                             # natural surface
SG0 = 860                            # subgrade level at the crown (road centre)
CROWN = 540
BX0, BX1 = 150, 930                  # box-out edges
LIP0, LIP1 = 240, 840                # channel lips (edges of the base + asphalt)
T_SB, T_B, T_AC = 90, 70, 22         # subbase, base, asphalt thickness (px)
DR_X = [166, 914]                    # subsoil drain centrelines
DR_HW, DR_BOT = 15, 985


def sg(x): return SG0 + 0.05 * abs(x - CROWN)
def sb(x): return sg(x) - T_SB
def bs(x): return sb(x) - T_B
def ac(x): return bs(x) - T_AC


def layer_pts(top, bot, x0, x1, n=12):
    """Closed polygon between two surface functions from x0 to x1 (breaks at the crown)."""
    xs = sorted({x0 + (x1 - x0) * k / n for k in range(n + 1)} | ({CROWN} if x0 < CROWN < x1 else set()))
    return [(x, top(x)) for x in xs] + [(x, bot(x)) for x in reversed(xs)]


def kerb_pts(side):
    pts = [(150, 650), (180, 650), (192, 700), (LIP0, ac(LIP0)), (LIP0, sb(LIP0)), (150, sb(150))]
    return pts if side < 0 else [(1080 - x, y) for x, y in pts]


def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def clip_poly(ctx, pts, xr=None):
    """ctx.save() + clip to polygon (optionally also left of xr). Caller must ctx.restore()."""
    ctx.save(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.clip()
    if xr is not None: ctx.rectangle(0, 0, xr, H); ctx.clip()


SB_GRAVEL = gravel(121, BX0, 760, BX1, 885, 260)
B_GRAVEL = [(x, y, r * 0.75) for x, y, r in gravel(122, LIP0, 690, LIP1, 805, 320)]
DR_GRAVEL = gravel(123, 140, 860, 940, DR_BOT, 200)
AC_DOTS = concrete_points(124, LIP0, 670, LIP1, 725, 260)
KERB_CONC = concrete_points(125, 140, 640, 940, 800, 220)


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


def roller(ctx, x, surf, col, a=1.0, r=20):
    """Smooth drum roller sitting on surface `surf` at x."""
    if a <= 0: return
    y = surf(x) - r - 2
    ctx.set_source_rgba(*BG, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(*col, a); ctx.set_line_width(2.5); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    ctx.arc(x, y, 4, 0, 2 * math.pi); ctx.fill()
    polyline(ctx, rect_pts(x - 34, y - r - 44, x + 26, y - r - 8), 1, col, 2.5, alpha=a)     # body
    polyline(ctx, [(x - 10, y - r - 44), (x - 10, y - r - 66), (x + 16, y - r - 66)], 1, col, 2, alpha=a)  # ROPS


def sweep(t, t0, d, x0=BX0, x1=BX1):
    """x position of a machine working left to right."""
    return x0 + (x1 - x0) * clamp((t - t0) / d)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 natural ground, then the box is dug out
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 90, NS, 990, 1110, c, reveal=p)
        polyline(ctx, [(90, NS), (990, NS)], p, c, 3)
        polyline(ctx, [(90, NS + 22), (990, NS + 22)], p, c, 1.4, alpha=0.6, dash=[10, 8])     # topsoil
    pb = prog(t, s1 + 1.0, 1.6)
    if pb > 0:
        box = [(BX0, NS - 2)] + [(x, sg(x)) for x in (BX0, CROWN, BX1)] + [(BX1, NS - 2)]
        ctx.save(); ctx.rectangle(BX0 - 2, 0, (BX1 - BX0 + 4) * pb, H); ctx.clip()
        fill_poly(ctx, box, BG, 1)
        ctx.restore()
        polyline(ctx, [(BX0, NS), (BX0, sg(BX0)), (CROWN, SG0), (BX1, sg(BX1)), (BX1, NS)], pb, c, 3)
    label(ctx, clamp((t - s1 - 0.6) / 0.8), c, (110, NS), (110, 600), "NATURAL SURFACE", a=gone(t, s4))
    label(ctx, clamp((t - s1 - 2.0) / 0.8), c, (700, 800), (940, 1150), "BOX OUT", anchor="r", a=gone(t, s2))

    # 2 subgrade trimmed + rolled
    c = tl.col(2, t)
    psg = prog(t, s2, 0.8)
    if psg > 0:
        polyline(ctx, [(BX0, sg(BX0)), (CROWN, SG0), (BX1, sg(BX1))], psg, ORANGE if t < s3 else c, 3.5)
    if s2 + 0.6 < t < s3 + 0.3:
        x = sweep(t, s2 + 0.6, 2.6, BX0 + 40, BX1 - 40)
        roller(ctx, x, sg, c, a=clamp((t - s2 - 0.6) / 0.3) * gone(t, s3 - 0.2, 0.4))
    label(ctx, clamp((t - s2 - 1.2) / 0.8), c, (760, sg(760)), (940, 1150), "SUBGRADE", anchor="r")

    # 3 subsoil drains along each edge
    c = tl.col(3, t)
    for k, xc in enumerate(DR_X):
        pd = prog(t, s3 + k * 0.4, 0.6)
        if pd <= 0: continue
        top = sg(xc)
        x0, x1 = xc - DR_HW, xc + DR_HW
        ybot = top + (DR_BOT - top) * pd
        fill_poly(ctx, rect_pts(x0, top, x1, ybot), BG, 1)
        polyline(ctx, [(x0, top), (x0, ybot), (x1, ybot), (x1, top)], 1, c, 2.5)
        pp = prog(t, s3 + 1.0 + k * 0.3, 0.5)
        if pp > 0:
            ctx.set_source_rgba(*c, pp); ctx.set_line_width(2.5)
            ctx.arc(xc, DR_BOT - 16, 10, 0, 2 * math.pi); ctx.stroke()
            ctx.set_dash([4, 4]); ctx.arc(xc, DR_BOT - 16, 13, 0, 2 * math.pi); ctx.stroke(); ctx.set_dash([])
        pg = prog(t, s3 + 1.6 + k * 0.3, 0.6)
        if pg > 0:
            ctx.save(); ctx.rectangle(x0 + 2, DR_BOT - (DR_BOT - top) * pg, x1 - x0 - 4, (DR_BOT - top) * pg); ctx.clip()
            draw_gravel(ctx, [g for g in DR_GRAVEL if abs(g[0] - xc) < DR_HW - 4 and math.hypot(g[0] - xc, g[1] - DR_BOT + 16) > 16],
                        c, 0.6)
            ctx.restore()
    label(ctx, clamp((t - s3 - 1.4) / 0.8), c, (DR_X[0], DR_BOT - 16), (110, 1192), "SUBSOIL DRAIN", a=gone(t, s5))

    # 4 subbase in two compacted layers
    c = tl.col(4, t)
    for k in range(2):
        t0 = s4 + k * 1.5
        pl = prog(t, t0, 1.0)
        if pl <= 0: continue
        top = (lambda x, k=k: sg(x) - T_SB * (k + 1) / 2)
        bot = (lambda x, k=k: sg(x) - T_SB * k / 2)
        poly = layer_pts(top, bot, BX0, BX1)
        clip_poly(ctx, poly, BX0 + (BX1 - BX0) * pl)
        fill_poly(ctx, poly, BG, 1)
        draw_gravel(ctx, SB_GRAVEL, c, 0.55)
        ctx.restore()
        polyline(ctx, [(BX0, top(BX0)), (CROWN, top(CROWN)), (BX1, top(BX1))], pl, c, 2.5 if k == 1 else 1.4,
                 alpha=1 if k == 1 else 0.6, dash=None if k == 1 else [12, 8])
        if t0 + 0.4 < t < t0 + 1.5:
            roller(ctx, sweep(t, t0 + 0.4, 1.0, BX0 + 40, BX1 - 40), top, c,
                   a=clamp((t - t0 - 0.4) / 0.2) * gone(t, t0 + 1.3, 0.2))
    if t >= s4:
        polyline(ctx, [(BX0, sb(BX0)), (BX0, sg(BX0))], 1, c, 2.5)
        polyline(ctx, [(BX1, sb(BX1)), (BX1, sg(BX1))], 1, c, 2.5)
    label(ctx, clamp((t - s4 - 1.2) / 0.8), c, (330, sb(330) + 40), (110, 1150), "SUBBASE")

    # 5 slip-formed kerb and channel, each side
    c = tl.col(5, t)
    for k, side in enumerate((-1, 1)):
        pk = prog(t, s5 + 0.2 + k * 0.6, 0.6)
        if pk <= 0: continue
        pts = [(x, y - (1 - pk) * 90) for x, y in kerb_pts(side)]
        ctx.push_group()
        fill_poly(ctx, pts, BG, 1)
        polyline(ctx, pts + [pts[0]], 1, c, 2.5)
        clip_poly(ctx, pts); draw_concrete(ctx, KERB_CONC, c, 0.6); ctx.restore()
        ctx.pop_group_to_source(); ctx.paint_with_alpha(pk)
    label(ctx, clamp((t - s5 - 1.3) / 0.8), c, (200, 740), (300, 1192), "KERB & CHANNEL")

    # 6 base course, trimmed by a grader (left to right)
    c = tl.col(6, t)
    pb = prog(t, s6, 1.4)
    if pb > 0:
        poly = layer_pts(bs, sb, LIP0, LIP1)
        xr = LIP0 + (LIP1 - LIP0) * pb
        clip_poly(ctx, poly, xr)
        fill_poly(ctx, poly, BG, 1)
        draw_gravel(ctx, B_GRAVEL, c, 0.6)
        ctx.restore()
        polyline(ctx, [(LIP0, bs(LIP0)), (CROWN, bs(CROWN)), (LIP1, bs(LIP1))], pb, c, 2.5)
        if t < s6 + 2.6:
            roller(ctx, sweep(t, s6 + 1.0, 1.4, LIP0 + 30, LIP1 - 30), bs, c,
                   a=clamp((t - s6 - 1.0) / 0.2) * gone(t, s6 + 2.4, 0.2))
    label(ctx, clamp((t - s6 - 1.0) / 0.8), c, (420, (bs(420) + sb(420)) / 2), (110, 482), "BASE", a=gone(t, s7 + 1.0))

    # 7 prime (sprayed orange line), then asphalt behind a paver, then a roller
    c = tl.col(7, t)
    pp = prog(t, s7, 0.9)
    if pp > 0:
        polyline(ctx, [(LIP0, bs(LIP0) - 1), (CROWN, bs(CROWN) - 1), (LIP1, bs(LIP1) - 1)], pp,
                 mix(ORANGE, c, clamp((t - s7 - 1.2) / 0.6)), 3)
    pa = prog(t, s7 + 1.0, 1.8)
    if pa > 0:
        xr = LIP0 + (LIP1 - LIP0) * pa
        poly = layer_pts(ac, bs, LIP0, LIP1)
        clip_poly(ctx, poly, xr)
        fill_poly(ctx, poly, mix(BG, c, 0.08), 1)
        draw_concrete(ctx, AC_DOTS, c, 0.5)
        ctx.restore()
        xs = [x for x in (LIP0, CROWN, LIP1) if x <= xr] + [xr]
        polyline(ctx, [(x, ac(x)) for x in xs], 1, c, 2.5)
        pv = clamp((t - s7 - 0.8) / 0.2) * gone(t, s7 + 2.9, 0.3)
        if pv > 0:                                            # paver: hopper in front, screed behind
            y = ac(xr) - 6
            polyline(ctx, rect_pts(xr, y - 58, xr + 90, y), 1, c, 2.5, alpha=pv)
            polyline(ctx, [(xr + 90, y - 58), (xr + 118, y - 74), (xr + 118, y - 20), (xr + 90, y - 20)], 1, c, 2, alpha=pv)
            polyline(ctx, rect_pts(xr - 16, y - 14, xr, y + 4), 1, c, 2.5, alpha=pv)
            polyline(ctx, [(xr + 20, y - 58), (xr + 20, y - 84), (xr + 50, y - 84)], 1, c, 2, alpha=pv)
        if t < s7 + 3.8:
            roller(ctx, max(LIP0 + 30, xr - 150) if pa < 1 else sweep(t, s7 + 2.8, 0.9, LIP1 - 150, LIP1 - 30), ac, c,
                   a=clamp((t - s7 - 1.6) / 0.3) * gone(t, s7 + 3.6, 0.2))
    label(ctx, clamp((t - s7 - 1.4) / 0.8), c, (330, ac(330) + 10), (110, 445), "ASPHALT")
    label(ctx, clamp((t - s7 - 0.6) / 0.8), ORANGE, (820, bs(820)), (940, 520), "PRIME", anchor="r", a=gone(t, s8))

    # 8 line marking + verges topsoiled and grassed
    c = tl.col(8, t)
    pm = prog(t, s8, 0.5)
    if pm > 0:
        y = ac(CROWN)
        fill_poly(ctx, rect_pts(CROWN - 14, y - 5, CROWN + 14, y), c, pm)
    for k, side in enumerate((-1, 1)):
        pv = prog(t, s8 + 0.6 + k * 0.4, 0.6)
        if pv <= 0: continue
        pts = [(90, NS - 26), (150, 652), (150, NS), (90, NS)]
        if side > 0: pts = [(1080 - x, y) for x, y in pts]
        fill_poly(ctx, pts, BG, pv)
        polyline(ctx, [pts[0], pts[1]], pv, c, 2.5)
        for j in range(5):                                    # grass ticks
            u = (j + 0.5) / 5
            gx = pts[0][0] + (pts[1][0] - pts[0][0]) * u; gy = pts[0][1] + (pts[1][1] - pts[0][1]) * u
            polyline(ctx, [(gx, gy), (gx - 5, gy - 12)], pv, c, 1.6, alpha=0.8)
            polyline(ctx, [(gx, gy), (gx + 5, gy - 12)], pv, c, 1.6, alpha=0.8)
    label(ctx, clamp((t - s8 - 0.8) / 0.8), c, (CROWN, ac(CROWN) - 5), (560, 445), "LINE MARKING", a=gone(t, tl.res0))
    label(ctx, clamp((t - s8 - 1.6) / 0.8), c, (120, NS - 18), (110, 600), "VERGE")

    # result: crossfall arrows both ways + pavement depth
    r0 = tl.res0
    pf = prog(t, r0, 0.8)
    if pf > 0:
        for sgn in (-1, 1):
            x0, x1 = CROWN + sgn * 40, CROWN + sgn * 260
            y0, y1 = ac(x0) - 34, ac(x1) - 34
            polyline(ctx, [(x0, y0), (x1, y1)], pf, BLUE, 3)
            if pf >= 1:
                polyline(ctx, [(x1 - sgn * 16, y1 - 10), (x1, y1), (x1 - sgn * 14, y1 + 10)], 1, BLUE, 3)
        text(ctx, "CROSSFALL", CROWN, ac(CROWN) - 60, 26, BLUE, alpha=clamp(pf * 2 - 1), bold=True, anchor="c", spacing=4)
    dim_v(ctx, 700, ac(700), sg(700), "PAVEMENT", prog(t, r0 + 0.6, 0.6))


# ---------------------------------------------------------------- 3D model (mm): layer-cake road, layers stepped back to show each one
def model3d():
    from engine.three_d import box
    P = []; o = 0
    L = 10000                              # length of road shown
    RW = 7000                              # between channel lips
    KW, KH = 500, 350                      # kerb width, kerb top above the asphalt
    SB, BS, AC = 1000, 650, 300             # layer thicknesses (exaggerated so each layer reads)
    yb, ya, yt = SB, SB + BS, SB + BS + AC
    P.append(box(-1200, L + 1200, -500, 0, -1800, RW + 1800, o, "ground")); P[-1].base = True; o += 1
    for k in range(2):                      # subbase in two layers, full width incl. under the kerbs
        P.append(box(0, L, k * SB / 2, (k + 1) * SB / 2, -KW, RW + KW, o, "brick")); o += 1
    for i in range(3):                      # kerb and channel, slip-formed in lengths
        x0, x1 = i * L / 3, (i + 1) * L / 3
        P.append(box(x0, x1, SB, yt + KH, -KW, -KW * 0.45, o + i, "concrete"))
        P.append(box(x0, x1, SB, yt, -KW * 0.45, 0, o + i, "concrete"))
        P.append(box(x0, x1, SB, yt + KH, RW + KW * 0.45, RW + KW, o + i, "concrete"))
        P.append(box(x0, x1, SB, yt, RW, RW + KW * 0.45, o + i, "concrete"))
    o += 3
    P.append(box(2200, L, yb, ya, 0, RW, o, "eps")); o += 1                     # base, stepped back
    for i in range(3):                      # asphalt laid in runs, stepped back further
        x0 = 4400 + i * (L - 4400) / 3
        P.append(box(x0, x0 + (L - 4400) / 3, ya, yt, 0, RW, o, "steel")); o += 1
    for i in range(4):                      # centreline marking dashes
        x0 = 4800 + i * 1500
        P.append(box(x0, x0 + 900, yt, yt + 15, RW / 2 - 70, RW / 2 + 70, o, "eps"))
    o += 1
    cfg = {"target": (L / 2, 500, RW / 2), "yaw": 118, "pitch": 22, "dist": 24000, "scale": 1.5,
           "cy_hook": 1040, "cy_result": 830, "cy_cover": 1010, "cover_scale": 1.0}
    return P, cfg
