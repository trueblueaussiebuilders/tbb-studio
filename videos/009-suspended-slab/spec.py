"""009 Suspended concrete slab on table forms (commercial)."""
import math
from engine.blueprint import *

META = {
    "category": "commercial",
    "title": "SUSPENDED SLAB",
    "subtitle": "COMMERCIAL  //  TYPICAL AU METHOD",
    "dwg": "009",
    "drawing": "SUSPENDED SLAB",
    "section_label": "SECTION THROUGH FLOOR  (NTS)",
    "hook": ["A CONCRETE FLOOR,", "POURED IN", "MID-AIR."],
    "hook_sub": "HOW A SUSPENDED SLAB IS BUILT",
    "cover": ["HOW TOWERS", "POUR A FLOOR", "IN MID-AIR."],
    "steps": [
        ("COLUMNS", "Columns poured up to the underside of the new slab, with starter bars sticking up."),
        ("TABLE FORMS", "Table forms craned up, rolled into place and jacked to the exact soffit level."),
        ("INFILLS & EDGES", "Infill formwork around the columns. Edge forms on, and edge screens for safety."),
        ("BOTTOM STEEL", "Bar chairs on the deck, then the bottom reinforcement laid on top of them."),
        ("SERVICES", "Sleeves leave holes for pipes. Electrical conduits are laid between the bars."),
        ("TOP STEEL", "Extra top bars over the columns. The steel is inspected before the pour."),
        ("THE POUR", "Concrete pumped in, vibrated and screeded to level. Then finished and cured."),
        ("STRIP & BACK-PROP", "Once it's strong enough, the tables are lowered and rolled out. Back-props go in."),
    ],
    "result": "A finished floor. The tables are craned up a level, and the cycle starts again.",
}

NARRATION = {
    "hook": "A concrete floor, poured in mid-air. Here's how a suspended slab is built on table forms.",
    "steps": [
        "First, the columns are poured up to the underside of the new slab. Starter bars are left sticking out the top.",
        "Table forms are craned up and rolled into place. Screw jacks raise each one to the exact level.",
        "Infill formwork closes the gaps around the columns. Edge forms go on, and edge screens protect the workers.",
        "Bar chairs go down on the deck. Then the bottom reinforcement is laid on top of them.",
        "Services go in next. Sleeves leave holes for pipes. Electrical conduits are laid between the bars.",
        "Extra top bars go over the columns. Then the steel is inspected before the pour.",
        "Concrete is pumped in, vibrated, and screeded to level. Then it's finished and cured.",
        "Once the concrete is strong enough, the tables are lowered and rolled out. Back-props carry the load for a while longer.",
    ],
    "result": "A finished floor. The tables are craned up a level, and the cycle starts again.",
    "end": "Follow for more.",
}

CAPTION = """How do they pour a concrete floor up in the air? 👇 How a suspended slab goes in on table forms.

Typical: a reinforced or post-tensioned concrete slab on prefabricated table forms, with infill formwork around the columns, bar chairs under the bottom reinforcement, extra top bars over the columns, cast-in sleeves and conduits, a pre-pour inspection, and back-props after the forms are stripped.
Slab thickness, reinforcement, stripping times and back-propping all depend on the design and the concrete strength.
Typical only. Your engineer's design governs.

#concreteslab #formwork #commercialconstruction #concrete #highrise #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
FL0, FL1 = 1060, 1100               # floor below: top / bottom
SOF, TOS = 700, 640                 # new slab soffit / top
XL, SE = 100, 850                   # left break line / slab edge
CXS, CW = (330, 800), 22            # column centrelines, half width
TABLES = [(120, 286, (142, 264)), (374, 756, (396, 576, 734))]     # deck x0, x1, leg xs
INFILL = [(286, CXS[0] - CW), (CXS[0] + CW, 374), (756, CXS[1] - CW), (CXS[1] + CW, 872)]
SCREEN_X = 892                      # edge screen
BOT, TOP = 688, 653                 # bottom / top bar levels
SLEEVE = (560, 586)
BACKPROPS = (210, 470, 660)

CONC_FLOOR = concrete_points(91, XL, FL0, SE, FL1, 150, lambda x, y: FL0 + 4 < y < FL1 - 4 and x > XL + 6)
CONC_COL = [concrete_points(92 + i, c - CW, SOF, c + CW, FL0, 45, lambda x, y, c=c: c - CW + 4 < x < c + CW - 4)
            for i, c in enumerate(CXS)]
CONC_SLAB = concrete_points(95, XL, TOS, SE, SOF, 260,
                            lambda x, y: TOS + 4 < y < SOF - 4 and XL + 6 < x < SE - 4
                            and not (SLEEVE[0] - 4 < x < SLEEVE[1] + 4))


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


def break_line(ctx, x, y0, y1, p, col):
    ym = (y0 + y1) / 2
    polyline(ctx, [(x, y0 - 10), (x, ym - 10), (x - 9, ym - 3), (x + 9, ym + 3), (x, ym + 10), (x, y1 + 10)], p, col, 2)


def draw_table(ctx, x0, x1, legs, c, p_drop=1.0):
    """Table form: ply deck, joists, bearer, legs with screw jacks and cross bracing."""
    polyline(ctx, rect_pts(x0, SOF, x1, SOF + 9), 1, c, 2.5)                     # ply deck
    for x in range(int(x0) + 10, int(x1) - 6, 34):                               # joists (in section)
        ctx.set_source_rgba(*c, 0.9); ctx.set_line_width(2); ctx.rectangle(x, SOF + 9, 12, 16); ctx.stroke()
    polyline(ctx, rect_pts(x0 + 6, SOF + 25, x1 - 6, SOF + 43), 1, c, 2.5)       # bearer
    for x in legs:
        polyline(ctx, [(x - 5, SOF + 43), (x - 5, FL0 - 34)], 1, c, 2.5)
        polyline(ctx, [(x + 5, SOF + 43), (x + 5, FL0 - 34)], 1, c, 2.5)
        polyline(ctx, [(x, FL0 - 34), (x, FL0 - 6)], 1, c, 3)                    # screw jack
        polyline(ctx, [(x - 10, FL0 - 22), (x + 10, FL0 - 22)], 1, c, 3)          # jack nut
        polyline(ctx, [(x - 14, FL0 - 4), (x + 14, FL0 - 4)], 1, c, 3)            # base plate
    for a, b in zip(legs[:-1], legs[1:]):                                         # cross bracing
        polyline(ctx, [(a + 5, SOF + 70), (b - 5, FL0 - 60)], 1, c, 1.6, alpha=0.75)
        polyline(ctx, [(a + 5, FL0 - 60), (b - 5, SOF + 70)], 1, c, 1.6, alpha=0.75)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 floor below + columns with starter bars
    c = tl.col(1, t); p = prog(t, s1, 0.8)
    if p > 0:
        polyline(ctx, rect_pts(XL, FL0, SE, FL1)[:4], p, c, 3)
        draw_concrete(ctx, CONC_FLOOR, c, 0.5 * p)
        break_line(ctx, XL, FL0, FL1, p, c)
        for cx in CXS:
            polyline(ctx, [(cx - CW, FL1), (cx - CW, FL1 + 30)], p, c, 1.5, dash=[8, 6])
            polyline(ctx, [(cx + CW, FL1), (cx + CW, FL1 + 30)], p, c, 1.5, dash=[8, 6])
    for i, cx in enumerate(CXS):
        pc = prog(t, s1 + 0.5 + i * 0.3, 0.9)
        if pc <= 0: continue
        ctx.set_source_rgba(*BG, 1); ctx.rectangle(cx - CW, FL0 - (FL0 - SOF) * pc, 2 * CW, (FL0 - SOF) * pc); ctx.fill()
        clip_rect(ctx, cx - CW - 4, FL0 - (FL0 - SOF) * pc - 2, cx + CW + 4, FL0 + 2)
        polyline(ctx, [(cx - CW, FL0), (cx - CW, SOF), (cx + CW, SOF), (cx + CW, FL0)], 1, c, 3)
        draw_concrete(ctx, CONC_COL[i], c, 0.55)
        ctx.restore()
        ps = prog(t, s1 + 1.4 + i * 0.3, 0.6)
        for dx in (-11, 11):
            polyline(ctx, [(cx + dx, SOF + 30), (cx + dx, SOF - 46 * ps)], 1 if ps > 0 else 0, c, 2.5)
    label(ctx, clamp((t - s1 - 0.8) / 0.8), c, (170, FL1 - 8), (110, 1150), "FLOOR BELOW")
    label(ctx, clamp((t - s1 - 1.3) / 0.8), c, (CXS[1] + CW, 900), (950, 1150), "COLUMN", anchor="r")
    label(ctx, clamp((t - s1 - 1.9) / 0.8), c, (CXS[0] - 11, SOF - 30), (180, 520), "STARTER BARS", a=gone(t, s3))

    # 2 table forms, rolled in and jacked up; lowered and rolled out in step 8
    c = tl.col(2, t)
    lower = prog(t, s8 + 0.2, 0.7); out = prog(t, s8 + 0.9, 0.9)
    for k, (x0, x1, legs) in enumerate(TABLES):
        pt = prog(t, s2 + k * 0.5, 0.9)
        if pt <= 0 or out >= 1: continue
        jack = prog(t, s2 + 1.2 + k * 0.3, 0.6)
        clip_rect(ctx, XL - 4, 0, W, H)                     # tables roll in / out past the break line
        ctx.push_group()
        ctx.translate(-(1 - pt) * 260 - out * 260, (1 - jack) * 22 + lower * 22)
        draw_table(ctx, x0, x1, legs, c)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(pt * (1 - out))
        ctx.restore()
    lab_jack = gone(t, s8)
    label(ctx, clamp((t - s2 - 1.6) / 0.8), c, (TABLES[1][0] + 140, SOF + 4), (620, 520), "TABLE FORM", a=gone(t, s4))
    label(ctx, clamp((t - s2 - 2.1) / 0.8), c, (TABLES[1][2][0], FL0 - 22), (470, 1150), "SCREW JACK", a=lab_jack)

    # 3 infills around the columns, edge form, edge screen
    c = tl.col(3, t)
    for k, (x0, x1) in enumerate(INFILL):
        pi = prog(t, s3 + k * 0.2, 0.5) * (1 - out)
        if pi <= 0: continue
        ctx.push_group()
        ctx.translate(0, lower * 22)
        polyline(ctx, rect_pts(x0, SOF, x1, SOF + 9), 1, c, 2.5)
        xm = (x0 + x1) / 2
        polyline(ctx, rect_pts(xm - 6, SOF + 9, xm + 6, SOF + 30), 1, c, 2)
        polyline(ctx, [(xm, SOF + 30), (xm, FL0 - 4)], 1, c, 2, alpha=0.8)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(pi)
    pe = prog(t, s3 + 0.9, 0.6)
    if pe > 0:
        polyline(ctx, rect_pts(SE, TOS - 10, SE + 8, SOF), pe, c, 2.5)                  # edge form board
        polyline(ctx, [(SE + 8, TOS + 6), (SE + 20, SOF)], pe, c, 2)                    # kicker
    ps = prog(t, s3 + 1.2, 1.0)
    if ps > 0:
        ytop = FL1 - (FL1 - 560) * ps
        for x in (SCREEN_X - 5, SCREEN_X + 5):
            polyline(ctx, [(x, FL1), (x, ytop)], 1, c, 2)
        ctx.save(); ctx.rectangle(SCREEN_X - 5, ytop, 10, FL1 - ytop); ctx.clip()
        ctx.set_source_rgba(*c, 0.5); ctx.set_line_width(1)
        for y in range(560, FL1, 12):
            ctx.move_to(SCREEN_X - 5, y); ctx.line_to(SCREEN_X + 5, y + 10)
        ctx.stroke(); ctx.restore()
        polyline(ctx, [(SE, FL0 + 20), (SCREEN_X - 5, FL0 + 20)], 1, c, 2.5)             # bracket to floor below
    label(ctx, clamp((t - s3 - 0.8) / 0.8), c, ((INFILL[1][0] + INFILL[1][1]) / 2, SOF + 4), (180, 482), "INFILL",
          a=gone(t, s4))
    label(ctx, clamp((t - s3 - 1.4) / 0.8), c, (SE + 4, TOS - 6), (950, 520), "EDGE FORM", anchor="r", a=gone(t, s7))
    label(ctx, clamp((t - s3 - 2.0) / 0.8), c, (SCREEN_X - 5, 960), (950, 1192), "EDGE SCREEN", anchor="r")

    # 7 concrete (drawn under the steel so the bars still read in section)
    c7 = tl.col(7, t); pp = prog(t, s7, 1.6)
    if pp > 0:
        xf = XL + (SE - XL) * pp
        ctx.save(); ctx.rectangle(XL, TOS - 2, xf - XL, SOF - TOS + 2); ctx.clip()
        ctx.set_source_rgba(*BG, 1); ctx.rectangle(XL, TOS, SE - XL, SOF - TOS); ctx.fill()
        ctx.set_source_rgba(*c7, 0.10); ctx.rectangle(XL, TOS, SE - XL, SOF - TOS); ctx.fill()
        draw_concrete(ctx, CONC_SLAB, c7, 0.55)
        polyline(ctx, [(XL, TOS), (SE, TOS)], 1, c7, 3)
        ctx.restore()
        if pp < 1:                                                                       # poker vibrator at the front
            polyline(ctx, [(xf - 10, TOS - 70), (xf - 24, SOF - 14)], 1, c7, 3)
        break_line(ctx, XL, TOS, SOF, pp, c7)

    # 4 bar chairs + bottom bars
    c = tl.col(4, t)
    pch = prog(t, s4, 0.8)
    for k, x in enumerate(range(150, SE - 20, 90)):
        a = clamp(pch * 10 - k)
        if a <= 0: continue
        ctx.set_source_rgba(*c, a); ctx.set_line_width(2)
        ctx.move_to(x - 7, SOF); ctx.line_to(x, BOT + 5); ctx.line_to(x + 7, SOF); ctx.stroke()
    pb = prog(t, s4 + 0.8, 1.0)
    if pb > 0:
        polyline(ctx, [(XL + 4, BOT), (SE - 10, BOT)], pb, c, 2.5)
        for x in range(112, SE - 14, 26):
            if x < XL + (SE - XL) * pb: dot(ctx, x, BOT - 6, 3.2, c)
    label(ctx, clamp((t - s4 - 1.2) / 0.8), c, (150 + 90, SOF - 6), (180, 520), "BAR CHAIRS", a=gone(t, s5))
    label(ctx, clamp((t - s4 - 1.8) / 0.8), c, (500, BOT), (620, 482), "BOTTOM BARS", a=gone(t, s5))

    # 5 services: pipe sleeve + conduit
    c = tl.col(5, t)
    psl = prog(t, s5, 0.6)
    if psl > 0:
        polyline(ctx, rect_pts(SLEEVE[0], TOS - 6, SLEEVE[1], SOF), psl, c, 2.5)
    pcd = prog(t, s5 + 0.6, 1.0)
    if pcd > 0:
        polyline(ctx, [(XL + 4, 670), (440, 670), (470, 676), (520, 676)], pcd, c, 2, dash=[10, 6])
        if pcd >= 1: polyline(ctx, rect_pts(520, 668, 540, SOF), 1, c, 2)            # cast-in box
    label(ctx, clamp((t - s5 - 1.0) / 0.8), c, (SLEEVE[1], TOS + 12), (620, 520), "PIPE SLEEVE", a=gone(t, s6))
    label(ctx, clamp((t - s5 - 1.6) / 0.8), c, (250, 670), (180, 482), "CONDUIT", a=gone(t, s6))

    # 6 top bars over the columns on high chairs, then inspection
    c = tl.col(6, t)
    for k, (x0, x1) in enumerate(((CXS[0] - 150, CXS[0] + 150), (CXS[1] - 150, SE - 10))):
        pt = prog(t, s6 + k * 0.4, 0.8)
        if pt <= 0: continue
        pts = [(x0, TOP), (x1, TOP)] + ([(x1, BOT - 12)] if x1 > SE - 20 else [])
        polyline(ctx, pts, pt, c, 3)
        for x in range(int(x0) + 25, int(x1), 60):
            if x < x0 + (x1 - x0) * pt:
                polyline(ctx, [(x, SOF), (x, TOP + 3)], 1, c, 1.5, alpha=0.8)
                dot(ctx, x + 12, TOP + 6, 3.2, c)
    label(ctx, clamp((t - s6 - 1.0) / 0.8), c, (CXS[0] + 90, TOP), (180, 520), "TOP BARS", a=gone(t, s7))
    stamp(ctx, "INSPECTED", 640, 465, prog(t, s6 + 2.0, 0.35), c, fade=clamp((t - tl.step_end(6)) / 0.6))
    label(ctx, clamp((t - s7 - 1.0) / 0.8), c7, (200, 668), (180, 520), "CONCRETE SLAB", a=gone(t, s8))

    # 8 back-props under the new slab
    c = tl.col(8, t)
    for k, x in enumerate(BACKPROPS):
        pb = prog(t, s8 + 1.6 + k * 0.25, 0.6)
        if pb <= 0: continue
        polyline(ctx, [(x - 14, SOF + 3), (x + 14, SOF + 3)], pb, c, 3)
        polyline(ctx, [(x - 4, SOF + 5), (x - 4, 880)], pb, c, 2.5)
        polyline(ctx, [(x + 4, SOF + 5), (x + 4, 880)], pb, c, 2.5)
        polyline(ctx, [(x, 860), (x, FL0 - 5)], pb, c, 3)
        polyline(ctx, [(x - 10, 900), (x + 10, 900)], pb, c, 3)
        polyline(ctx, [(x - 14, FL0 - 3), (x + 14, FL0 - 3)], pb, c, 3)
    label(ctx, clamp((t - s8 - 2.2) / 0.8), c, (BACKPROPS[1] + 4, 960), (470, 1150), "BACK-PROPS")

    # result dims
    r0 = tl.res0
    dim_h(ctx, 596, CXS[0], CXS[1], "COLUMN GRID", prog(t, r0, 0.6))


# ---------------------------------------------------------------- 3D model (mm): floor plate, half poured, half still on the tables
def model3d():
    from engine.three_d import box, member3d
    P = []; o = 0
    GX, GZ, NX, NZ = 8000, 7500, 3, 2           # column grid and bays
    LX, LZ = GX * NX, GZ * NZ
    H, T = 3200, 250                            # floor to soffit, slab thickness
    P.append(box(-1500, LX + 1500, -300, 0, -1500, LZ + 1500, o, "ground")); P[-1].base = True; o += 1
    for i in range(NX + 1):                     # columns
        for j in range(NZ + 1):
            P.append(box(i * GX - 300, i * GX + 300, 0, H, j * GZ - 300, j * GZ + 300, o, "concrete"))
    o += 1
    for i in range(NX):                         # two table forms per bay, bay by bay
        for j in range(NZ):
            x0, z0 = i * GX, j * GZ
            for k in range(2):
                tx0, tx1 = x0 + 500 + k * 3600, x0 + 3900 + k * 3600 - 400
                tz0, tz1 = z0 + 500, z0 + GZ - 500
                P.append(box(tx0, tx1, H - 300, H, tz0, tz1, o, "timber"))
                for lx in (tx0 + 300, tx1 - 300):
                    for lz in (tz0 + 400, tz1 - 400):
                        P.append(box(lx - 60, lx + 60, 0, H - 300, lz - 60, lz + 60, o, "steel"))
            o += 1
    for i in range(NX + 1):                     # infill strips along the column lines
        P.append(box(i * GX - 500, i * GX + 500, H - 120, H, -300, LZ + 300, o, "timber"))
    o += 1
    for x0, x1 in ((-700, -600), ):             # edge screen down one side
        for j in range(NZ * 2):
            P.append(box(x0, x1, -200, H + 1500, j * GZ / 2 + 60, (j + 1) * GZ / 2 - 60, o, "steel"))
    o += 1
    XP = GX * 2                                 # poured up to here; bars visible beyond it
    for k in range(int((LX - XP) / 600) + 1):   # bars one way
        x = XP + 150 + k * 600
        if x > LX + 200: break
        P.append(box(x - 40, x + 40, H + 60, H + 140, -200, LZ + 200, o, "steel"))
    o += 1
    for k in range(int(LZ / 600) + 1):          # bars the other way
        z = -150 + k * 600
        P.append(box(XP, LX + 250, H + 140, H + 220, z - 40, z + 40, o, "steel"))
    o += 1
    # concrete, poured strip by strip. Split into half-bay panels: the renderer interpolates depth
    # linearly, so one huge face would let the tables underneath bleed through.
    xs = [-400, GX / 2, GX, GX * 1.5, GX * 2]
    zs = [-400, GZ / 2, GZ, GZ * 1.5, LZ + 400]
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            P.append(box(xs[i], xs[i + 1], H, H + T, zs[j], zs[j + 1], o, "concrete"))
        o += 1
    cfg = {"target": (LX / 2, 1700, LZ / 2), "yaw": 28, "pitch": 24, "dist": 52000, "scale": 1.55,
           "cy_hook": 1060, "cy_result": 820, "cy_cover": 1000, "cover_scale": 0.98}
    return P, cfg
