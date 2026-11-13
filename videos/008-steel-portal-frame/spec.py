"""008 Steel portal frame (structural)."""
import math
from engine.blueprint import *

META = {
    "category": "structural",
    "title": "STEEL PORTAL FRAME",
    "subtitle": "STRUCTURAL  //  TYPICAL AU METHOD",
    "dwg": "008",
    "drawing": "STEEL PORTAL FRAME",
    "section_label": "FRAME ELEVATION  (NTS)",
    "hook": ["A HUGE ROOF.", "NOT ONE POST", "IN THE MIDDLE."],
    "hook_sub": "HOW A STEEL PORTAL FRAME GOES UP",
    "cover": ["HOW BIG SHEDS", "SPAN WITHOUT", "ANY POSTS."],
    "steps": [
        ("PAD FOOTINGS", "Pad footings dug and poured, with hold-down bolts cast in from a template."),
        ("COLUMNS UP", "Steel columns stood on levelling nuts, bolted down and propped."),
        ("RAFTERS LIFTED", "Rafters bolted together at the apex on the ground, then craned up."),
        ("KNEE & APEX", "Bolted end-plate connections at the knees and apex make one rigid frame."),
        ("PURLINS & GIRTS", "Light steel purlins across the rafters. Girts across the columns."),
        ("BRACING", "Rod or strap bracing in the end bays. Fly braces stop the rafters twisting."),
        ("PLUMB & GROUT", "Frames plumbed and bolts tightened. Props out, base plates grouted."),
        ("SHEETING", "Roof and wall sheeting screwed to the purlins and girts."),
    ],
    "result": "A wide, open space. The whole roof is carried by a row of rigid steel frames.",
}

NARRATION = {
    "hook": "A huge roof, and not one post in the middle. Here's how a steel portal frame goes up.",
    "steps": [
        "First, pad footings are dug and poured. Hold-down bolts are cast in, set out with a template.",
        "Steel columns are stood on the bolts, sitting on levelling nuts. They're propped until the frame is complete.",
        "The rafters are bolted together on the ground. Then a crane lifts them up in one piece.",
        "Bolted connections at the knees and the apex lock it all together. Now it's one rigid frame.",
        "Next, light steel purlins are bolted across the rafters. Girts run across the columns.",
        "Bracing goes into the end bays. Fly braces stop the rafters from twisting.",
        "The frames are checked for plumb, and the bolts are tightened. The props come out, and the base plates are grouted.",
        "Finally, the roof and wall sheeting is screwed to the purlins and girts.",
    ],
    "result": "A wide, open space. The whole roof is carried by a row of rigid steel frames.",
    "end": "Follow for more.",
}

CAPTION = """How do big sheds and warehouses span so far with no posts in the middle? 👇 How a steel portal frame goes up.

Typical: hot-rolled steel columns and rafters with haunched, bolted end-plate connections at the knees and apex, cold-formed C or Z purlins and girts, rod or strap bracing in the end bays, fly braces to the rafter's inside flange, and hold-down bolts cast into pad footings with grouted base plates.
Frame spacing and member sizes depend on the span, the wind region and the loads.
Typical only. Your engineer's design governs.

#steelframe #portalframe #structuralsteel #shedbuild #warehouse #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
GND = 1060
CXS = (200, 880)                    # column centrelines
CW = 13                             # half column depth
EAVE, APEX, MID = 700, 625, 540     # rafter top at outer column face / at apex
RD = 24                             # rafter depth
K = (EAVE - APEX) / (MID - (CXS[0] - CW))
FT0, FT1, FW = GND, 1118, 60        # pad footing top / bottom / half width
BP0, BP1 = 1044, 1050               # base plate
PURLINS = [230, 300, 370, 440, 510]
GIRTS = [760, 840, 920, 1000]
FLY = [300, 440]
PROP_Y, PROP_X = 940, (330, 750)
SHEET = 18                          # sheeting offset from rafter top / column face


def rt(x):
    """Rafter top y at x (symmetric about the apex)."""
    if x > MID: x = 2 * MID - x
    return EAVE - (x - (CXS[0] - CW)) * K


def rb(x): return rt(x) + RD


def mx(x): return 2 * MID - x


CONC_F = [concrete_points(81 + i, c - FW, FT0, c + FW, FT1, 70,
                          lambda x, y, c=c: c - FW + 4 < x < c + FW - 4 and FT0 + 4 < y < FT1 - 4)
          for i, c in enumerate(CXS)]


def label(ctx, p, col, tip, elbow, txt, anchor="l"):
    """Leader + typed label on a dark plate so linework never strikes through the text."""
    if p <= 0: return
    polyline(ctx, [tip, elbow], clamp(p * 2), col, 2)
    dot(ctx, tip[0], tip[1], 5, col, clamp(p * 4))
    n = int(len(txt) * clamp(p * 2 - 1))
    if n <= 0: return
    font(ctx, 24, True)
    w = ctx.text_extents(txt[:n]).x_advance
    x = elbow[0] + 10 if anchor == "l" else elbow[0] - 10 - w
    ctx.set_source_rgba(*BG, 0.92); ctx.rectangle(x - 6, elbow[1] - 14, w + 12, 28); ctx.fill()
    text(ctx, txt, x, elbow[1] + 8, 24, col, bold=True, chars=n)


def fill_poly(ctx, pts, col, alpha):
    ctx.new_path(); ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    ctx.close_path(); ctx.set_source_rgba(*col, alpha); ctx.fill()


def rafter_pts(side):
    x0 = CXS[0] + CW
    pts = [(x0, rt(x0)), (MID, rt(MID)), (MID, rb(MID)), (x0, rb(x0)), (x0, rt(x0))]
    return pts if side == 0 else [(mx(x), y) for x, y in pts]


def column_pts(i):
    c = CXS[i]; xo, xi = (c - CW, c + CW) if i == 0 else (c + CW, c - CW)
    return [(xo, BP0), (xo, rt(xo)), (xi, rt(xi)), (xi, BP0), (xo, BP0)]


def haunch_pts(side):
    x0 = CXS[0] + CW
    pts = [(x0, rb(x0)), (x0, rb(x0) + 40), (x0 + 70, rb(x0 + 70)), (x0, rb(x0))]
    return pts if side == 0 else [(mx(x), y) for x, y in pts]


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 ground, pad footings, hold-down bolts
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 90, GND, 990, 1120, c, reveal=p)
        polyline(ctx, [(90, GND), (990, GND)], p, c, 3)
        for i, cx in enumerate(CXS):
            pf = prog(t, s1 + 0.6 + i * 0.3, 0.7)
            if pf <= 0: continue
            ctx.set_source_rgba(*BG, 1); ctx.rectangle(cx - FW, FT0, 2 * FW, FT1 - FT0); ctx.fill()
            polyline(ctx, rect_pts(cx - FW, FT0, cx + FW, FT1), pf, c, 3)
            draw_concrete(ctx, CONC_F[i], c, 0.6 * clamp(pf * 2 - 1))
            pb = prog(t, s1 + 1.2 + i * 0.3, 0.5)
            for bx in (cx - 16, cx + 16):
                polyline(ctx, [(bx, 1100), (bx, 1100 - (1100 - 1034) * pb)], 1, c, 2.5)
                polyline(ctx, [(bx, 1100), (bx + (6 if bx > cx else -6), 1100)], pb, c, 2.5)
        label(ctx, clamp((t - s1 - 1.4) / 0.8), c, (CXS[0] - 48, 1100), (110, 1150), "PAD FOOTING")
        label(ctx, clamp((t - s1 - 1.8) / 0.8), c, (CXS[0] + 16, 1088), (420, 1192), "HOLD-DOWN BOLTS")

    # 2 columns on levelling nuts, propped
    c = tl.col(2, t)
    props_out = 1 - prog(t, s7 + 0.3, 0.6)
    for i, cx in enumerate(CXS):
        pc = prog(t, s2 + i * 0.35, 0.8)
        if pc <= 0: continue
        for bx in (cx - 16, cx + 16):
            dot(ctx, bx, BP1 + 4, 4, c, pc)                                     # levelling nuts
        polyline(ctx, rect_pts(cx - 30, BP0, cx + 30, BP1), pc, c, 2.5)         # base plate
        ctx.save(); ctx.rectangle(0, BP0 - (BP0 - 640) * pc, W, BP0); ctx.clip()
        polyline(ctx, column_pts(i), 1, c, 3)
        xc = cx                                                               # web centreline
        polyline(ctx, [(xc, BP0 - 4), (xc, rt(xc) + 6)], 1, c, 1.2, alpha=0.5, dash=[14, 8])
        ctx.restore()
        pp = prog(t, s2 + 1.0 + i * 0.3, 0.6) * props_out
        if pp > 0:
            xf = cx + CW if i == 0 else cx - CW
            polyline(ctx, [(xf, PROP_Y), (PROP_X[i], GND - 4)], pp, c, 2.5, alpha=0.9)
            polyline(ctx, [(PROP_X[i] - 14, GND - 3), (PROP_X[i] + 14, GND - 3)], pp, c, 3)
    label(ctx, clamp((t - s2 - 1.4) / 0.8), c, (CXS[0] + CW, 860), (290, 860), "COLUMN")
    label(ctx, clamp((t - s2 - 1.8) / 0.8) * props_out, c, ((CXS[1] - CW + PROP_X[1]) / 2, (PROP_Y + GND) / 2),
          (700, 960), "TEMPORARY PROP", anchor="r")

    # 3 rafters craned in (drop from above)
    c = tl.col(3, t); p = prog(t, s3, 1.0)
    if p > 0:
        ctx.save(); ctx.translate(0, -(1 - p) * 140)
        for side in (0, 1):
            polyline(ctx, rafter_pts(side), 1, c, 3, alpha=p)
        ctx.restore()
        label(ctx, clamp((t - s3 - 1.1) / 0.8), c, (420, rb(420) - 2), (450, 730), "RAFTER")

    # 4 knee + apex connections
    c = tl.col(4, t)
    for side in (0, 1):
        pk = prog(t, s4 + side * 0.3, 0.7)
        if pk <= 0: continue
        hp = haunch_pts(side)
        polyline(ctx, hp, pk, c, 2.5)
        xp = CXS[0] + CW if side == 0 else CXS[1] - CW
        polyline(ctx, [(xp, rt(xp)), (xp, rb(xp) + 40)], pk, c, 5)               # end plate
        for yy in (rt(xp) + 10, rt(xp) + 32, rt(xp) + 54):
            dot(ctx, xp + (6 if side == 0 else -6), yy, 3, c, pk)
    pa = prog(t, s4 + 0.6, 0.7)
    if pa > 0:
        polyline(ctx, [(MID - 22, rb(MID - 22)), (MID, rb(MID) + 22), (MID + 22, rb(MID + 22))], pa, c, 2.5)
        polyline(ctx, [(MID, rt(MID)), (MID, rb(MID) + 22)], pa, c, 5)
        for yy in (rt(MID) + 10, rt(MID) + 30):
            dot(ctx, MID - 6, yy, 3, c, pa); dot(ctx, MID + 6, yy, 3, c, pa)
    label(ctx, clamp((t - s4 - 1.0) / 0.8), c, (CXS[0] + CW + 8, rb(CXS[0] + CW) + 22), (290, 790), "KNEE CONNECTION")
    label(ctx, clamp((t - s4 - 1.4) / 0.8), c, (MID, rb(MID) + 14), (560, 520), "APEX PLATE")

    # 5 purlins (Z sections on the rafters) and girts (on the column faces)
    c = tl.col(5, t)
    for k, x in enumerate(PURLINS):
        pp = prog(t, s5 + k * 0.15, 0.35)
        if pp <= 0: continue
        for xx, sg in ((x, 1), (mx(x), -1)):
            y = rt(xx)
            polyline(ctx, [(xx - 7 * sg, y), (xx, y), (xx, y - 16), (xx + 7 * sg, y - 16)], 1, c, 2.5, alpha=pp)
    for k, y in enumerate(GIRTS):
        pg = prog(t, s5 + 0.9 + k * 0.15, 0.35)
        if pg <= 0: continue
        for i, cx in enumerate(CXS):
            xo = cx - CW if i == 0 else cx + CW
            sg = -1 if i == 0 else 1
            polyline(ctx, [(xo, y - 7), (xo, y), (xo + 16 * sg, y), (xo + 16 * sg, y + 7)], 1, c, 2.5, alpha=pg)
    label(ctx, clamp((t - s5 - 1.0) / 0.8), c, (PURLINS[3], rt(PURLINS[3]) - 14), (420, 482), "PURLINS")
    label(ctx, clamp((t - s5 - 1.8) / 0.8), c, (CXS[1] + CW + 16, GIRTS[0] + 4), (940, 520), "GIRTS", anchor="r")

    # 6 fly braces from purlins to the rafter's bottom flange
    c = tl.col(6, t)
    for k, x in enumerate(FLY):
        pf = prog(t, s6 + 0.3 + k * 0.3, 0.5)
        if pf <= 0: continue
        polyline(ctx, [(x + 4, rt(x) - 2), (x + 30, rb(x + 30) + 2)], pf, c, 2.5)
        polyline(ctx, [(mx(x) - 4, rt(x) - 2), (mx(x) - 30, rb(x + 30) + 2)], pf, c, 2.5)
    label(ctx, clamp((t - s6 - 1.0) / 0.8), c, (FLY[0] + 17, (rt(FLY[0]) + rb(FLY[0] + 30)) / 2), (110, 445), "FLY BRACES")

    # 7 props out, base plates grouted
    c = tl.col(7, t)
    pg = prog(t, s7 + 0.8, 0.8)
    if pg > 0:
        for cx in CXS:
            clip_rect(ctx, cx - 36, BP1, cx - 36 + 72 * pg, FT0)
            ctx.set_source_rgba(*c, 0.35); ctx.rectangle(cx - 36, BP1, 72, FT0 - BP1); ctx.fill()
            ctx.restore()
            polyline(ctx, [(cx - 36, FT0), (cx - 36, BP1), (cx + 36, BP1), (cx + 36, FT0)], pg, c, 2)
        label(ctx, clamp((t - s7 - 1.3) / 0.8), c, (CXS[0] + 32, BP1 + 5), (300, 1010), "GROUT")

    # 8 roof + wall sheeting
    c = tl.col(8, t)
    pr = prog(t, s8, 1.0)
    if pr > 0:
        xe = CXS[0] - CW - SHEET
        roof = [(xe, rt(CXS[0] - CW) - SHEET + 4), (MID, APEX - SHEET), (mx(xe), rt(CXS[0] - CW) - SHEET + 4)]
        polyline(ctx, roof, pr, c, 3.5)
    pw = prog(t, s8 + 0.7, 0.9)
    if pw > 0:
        for xw in (CXS[0] - CW - SHEET, CXS[1] + CW + SHEET):
            y0 = rt(CXS[0] - CW) - SHEET + 6
            polyline(ctx, [(xw, y0), (xw, y0 + (GND - 12 - y0) * pw)], 1, c, 3.5)
        label(ctx, clamp((t - s8 - 1.2) / 0.8), c, (640, APEX - SHEET + (640 - MID) * K), (940, 445), "ROOF + WALL SHEETING", anchor="r")

    # result dims
    r0 = tl.res0
    dim_h(ctx, 1036, CXS[0] + CW, CXS[1] - CW, "CLEAR SPAN", prog(t, r0, 0.6))


# ---------------------------------------------------------------- 3D model (mm): frames going up along the shed, end bay clad
def model3d():
    from engine.three_d import box, member3d
    P = []; o = 0
    SPAN, EH, RISE, BAY, NF = 20000, 6000, 1700, 7000, 4
    L = BAY * (NF - 1)
    P.append(box(-3000, SPAN + 3000, -300, 0, -3500, L + 3500, o, "ground")); P[-1].base = True; o += 1
    for f in range(NF):                                                            # pad footings
        z = f * BAY
        for x in (0, SPAN):
            P.append(box(x - 500, x + 500, 0, 60, z - 500, z + 500, o, "concrete"))
    o += 1
    for f in range(NF):                                                            # frames, one by one
        z = f * BAY
        for x in (0, SPAN):
            P.append(member3d((x, 60, z), (x, EH, z), 220, 420, o, "steel"))
        o += 1
        for x0, x1 in ((0, SPAN / 2), (SPAN, SPAN / 2)):                           # rafters, in 2 pieces each side
            xm = (x0 + x1) / 2
            P.append(member3d((x0, EH, z), (xm, EH + RISE / 2, z), 220, 420, o, "steel"))
            P.append(member3d((xm, EH + RISE / 2, z), (x1, EH + RISE, z), 220, 420, o, "steel"))
        o += 1
    # rod bracing in the first bay (walls + roof)
    for x in (0, SPAN):
        P.append(member3d((x, 300, 0), (x, EH - 300, BAY), 50, 50, o, "steel"))
        P.append(member3d((x, EH - 300, 0), (x, 300, BAY), 50, 50, o, "steel"))
    for x0, x1 in ((0, SPAN / 2), (SPAN, SPAN / 2)):
        P.append(member3d((x0, EH + 250, 0), (x1, EH + RISE + 250, BAY), 50, 50, o, "steel"))
        P.append(member3d((x1, EH + RISE + 250, 0), (x0, EH + 250, BAY), 50, 50, o, "steel"))
    o += 1
    # purlins (one piece per bay so they sort cleanly), both slopes
    n = 6
    for k in range(n + 1):
        u = k / n
        for x0, x1 in ((0, SPAN / 2), (SPAN, SPAN / 2)):
            x = x0 + (x1 - x0) * u; y = EH + 210 + RISE * u + 100
            for b in range(NF - 1):
                P.append(box(x - 75, x + 75, y - 100, y + 100, b * BAY + 110, (b + 1) * BAY - 110, o, "steel"))
        o += (1 if k % 2 else 0)
    o += 1
    # girts on both side walls
    for y in (1500, 3000, 4500):
        for x, sg in ((0, -1), (SPAN, 1)):
            for b in range(NF - 1):
                P.append(box(x + sg * 210, x + sg * 410, y - 100, y + 100, b * BAY + 110, (b + 1) * BAY - 110, o, "steel"))
    o += 1
    # sheeting on the first bay only, so the frame stays visible
    for x0, x1 in ((0, SPAN / 2), (SPAN, SPAN / 2)):
        xm = (x0 + x1) / 2
        P.append(member3d((x0 + (-500 if x0 == 0 else 500), EH + 360, BAY / 2), (x1, EH + RISE + 460, BAY / 2), BAY, 60, o, "timber"))
    P.append(box(-480, -420, 100, EH + 300, 0, BAY, o, "timber"))
    o += 1
    cfg = {"target": (SPAN / 2, 3600, L / 2), "yaw": 20, "pitch": 22, "dist": 52000, "scale": 1.3,
           "cy_hook": 1060, "cy_result": 820, "cy_cover": 1000, "cover_scale": 1.1}
    return P, cfg
