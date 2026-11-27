"""021 Upstairs floor: open-web floor trusses in a double-storey house (residential)."""
import math
from engine.blueprint import *

META = {
    "category": "residential",
    "title": "UPSTAIRS FLOOR",
    "subtitle": "RESIDENTIAL  //  TYPICAL AU METHOD",
    "dwg": "021",
    "drawing": "UPSTAIRS FLOOR",
    "section_label": "SECTION THROUGH UPPER FLOOR  (NTS)",
    "hook": ["YOUR UPSTAIRS", "FLOOR IS", "MOSTLY AIR."],
    "hook_sub": "HOW AN UPPER FLOOR IS BUILT",
    "cover": ["THE UPSTAIRS", "FLOOR IS", "MOSTLY AIR."],
    "question": "Have you ever felt your upstairs floor bounce? Tell us below.",
    "hook_start": 0.5,
    "xray": {"after_step": 5, "upto": 11, "hot": [11]},   # trusses, trimmers, strongback in; services + floor still ghosts
    "steps": [
        ("GROUND WALLS", "The ground floor wall frames are stood, braced and checked level along the top plates."),
        ("FLOOR TRUSSES", "Factory-made floor trusses are lifted onto the top plates at the spacing on the layout."),
        ("TIE-DOWNS", "Each truss is fixed down to the top plate with steel brackets."),
        ("EDGE TRIMMER", "A trimmer runs around the edge of the floor and closes off the truss ends."),
        ("STRONGBACK", "A strongback runs through the trusses on edge. It stiffens the floor so it doesn't bounce."),
        ("SERVICES", "Pipes, ducts and cables run straight through the open webs. No cutting needed."),
        ("FLOOR SHEETS", "Particleboard flooring sheets are glued and screwed down to the top chords."),
        ("WALLS + CEILING", "Upper wall frames stand on the floor. Plasterboard goes on battens under the trusses."),
    ],
    "result": "The floor spans from wall to wall, and the pipes and ducts are hidden inside it.",
}

NARRATION = {
    "hook": "Your upstairs floor is mostly air. That's what makes it work.",
    "steps": [
        "First, the ground floor wall frames are stood up and braced. The top plates are checked level.",
        "Floor trusses are made in a factory. They're lifted onto the top plates, at the spacing on the layout.",
        "Each truss is fixed down to the top plate with steel brackets.",
        "An edge trimmer runs around the outside of the floor. It closes off the truss ends.",
        "A strongback runs through the trusses, on edge. It ties them together and stiffens the floor, so it doesn't bounce.",
        "Now the services go in. Pipes, ducts and cables run straight through the open webs. No cutting needed.",
        "Particleboard flooring sheets are glued and screwed down to the top chords.",
        "The upper wall frames stand on the new floor. Underneath, plasterboard goes on battens for the ceiling below.",
    ],
    "result": "The floor spans from wall to wall. And the pipes and ducts are hidden inside it.",
    "end": "Follow for more.",
}

CAPTION = """Your upstairs floor is mostly air 👇 How an upper floor is built.

Typical: many double-storey houses in Australia have a timber-framed upper floor. A common choice is open-web floor trusses: timber top and bottom chords joined by galvanised steel webs, made in a factory to the truss maker's design and often set out at 450 or 600 millimetre centres. Other houses use I-joists, LVL or solid timber joists, or a concrete slab.
The ground floor wall frames are stood, braced and checked level. The trusses are lifted onto the top plates at the spacing on the truss layout and fixed down with tie-down brackets. An edge trimmer closes off the truss ends around the perimeter. On longer spans, a strongback (a timber member on edge, run through the webs and fixed to each truss) ties the trusses together and stiffens the floor against bounce. Plumbing, ducts and cables run through the open webs instead of through holes cut in solid joists. Particleboard flooring sheets are glued and screwed or nailed to the top chords, then the upper wall frames go up. The ceiling below is plasterboard on battens or furring channels under the bottom chords.
Truss depth, spacing, spans, strongback positions and fixings come from the truss design and the engineer.
Typical only. Your engineer's design governs.

#doublestorey #floortrusses #houseframing #carpentry #newhome #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
SX0, SX1 = 70, 1010                   # ground slab extent
ST, SB = 1130, 1180                   # ground slab top / bottom
WALLS = [(110, 150), (930, 970)]      # ground + upper wall frames (outside face, inside face)
BP_T = 1112                           # ground wall bottom plate top
TP1, TP = 775, 760                    # double top plate: joint / top of the top plates
TX0, TX1 = 126, 954                   # truss ends (the edge trimmers sit outside them)
BC_T = 730                            # bottom chord top (bottom chord = BC_T..TP)
TC_T, TC_B = 630, 660                 # top chord
FL_T = 616                            # flooring sheet top (sheet = FL_T..TC_T)
UBP_T = 598                           # upper wall bottom plate top
UW_TOP = 445                          # upper walls cut off here (break line)
CEIL_T, CEIL_B = 772, 782             # plasterboard ceiling (battens TP..CEIL_T)
WEB_X = [146 + (934 - 146) * i / 8 for i in range(9)]     # web joints, alternating top / bottom chord
BACK_STUDS = list(range(215, 900, 110))                    # faint studs of the far wall, seen in elevation
SBK = (532, 548, 690, BC_T)           # strongback cut section (x0, x1, y0, y1), sits in the V at mid-span
DUCT = (343, 702, 24)                 # duct (cut, runs across the trusses) in the open triangle at x = 343
PIPE = [(640, FL_T), (640, 676), (905, 684)]                # waste pipe: up through the floor, then along with a fall
SPAN_Y = 1062

SLAB_CONC = concrete_points(211, SX0, ST, SX1, SB, 150)


def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def timber_cut(ctx, x0, y0, x1, y1, col, p, alpha=1.0, width=2.5):
    """Cut timber: box with a diagonal cross."""
    if p <= 0: return
    fill_poly(ctx, rect_pts(x0, y0, x1, y1)[:4], BG, 1)
    polyline(ctx, rect_pts(x0, y0, x1, y1), p, col, width, alpha=alpha)
    polyline(ctx, [(x0, y0), (x1, y1)], p, col, 1.4, alpha=0.7 * alpha)
    polyline(ctx, [(x1, y0), (x0, y1)], p, col, 1.4, alpha=0.7 * alpha)


def web_pts():
    return [(x, TC_B if i % 2 == 0 else BC_T) for i, x in enumerate(WEB_X)]


def open_triangles():
    """The open spaces between the webs (for the 'mostly air' highlight)."""
    pts = web_pts(); tris = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if a[1] == TC_B:                                   # web goes down: open triangle under the top chord
            tris.append([a, (b[0], TC_B), b])
        else:                                              # web goes up: open triangle over the bottom chord
            tris.append([a, b, (b[0], BC_T)])
    return tris


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    # ---- ground slab (always there)
    pg = prog(t, s1 - 0.1, 0.6)
    if pg > 0:
        polyline(ctx, [(SX0, ST), (SX1, ST)], pg, WHITE, 3)
        polyline(ctx, [(SX0, SB), (SX1, SB)], pg, WHITE, 2, alpha=0.6)
        draw_concrete(ctx, SLAB_CONC, WHITE, 0.4 * pg)

    # ---- 1 ground floor walls: far-wall studs (faint), the two cut walls, double top plates
    c1 = tl.col(1, t)
    for i, x in enumerate(BACK_STUDS):
        k = prog(t, s1 + 0.3 + i * 0.08, 0.5)
        if k > 0:
            polyline(ctx, rect_pts(x - 6, TP1 + 15, x + 6, BP_T), k, WHITE, 1.4, alpha=0.28)
    kbp = prog(t, s1 + 0.3, 0.8)
    if kbp > 0:
        polyline(ctx, [(WALLS[0][1], TP1 + 15), (WALLS[1][0], TP1 + 15)], kbp, WHITE, 1.4, alpha=0.28)
        polyline(ctx, [(WALLS[0][1], BP_T), (WALLS[1][0], BP_T)], kbp, WHITE, 1.4, alpha=0.28)
    for j, (a, b) in enumerate(WALLS):
        k = prog(t, s1 + 0.2 + j * 0.3, 0.8)
        if k <= 0: continue
        timber_cut(ctx, a, BP_T, b, ST, c1, k)
        yt = BP_T - (BP_T - (TP1 + 15)) * k
        polyline(ctx, rect_pts(a + 6, yt, b - 6, BP_T), 1, c1, 2.5)
        kp = prog(t, s1 + 1.0 + j * 0.3, 0.6)
        timber_cut(ctx, a, TP1, b, TP1 + 15, c1, kp)
        timber_cut(ctx, a, TP, b, TP1, c1, kp)
    kl = prog(t, s1 + 1.8, 0.8) * gone(t, s3 + 0.3)
    if kl > 0:
        polyline(ctx, [(WALLS[0][0] - 20, TP - 10), (WALLS[1][1] + 20, TP - 10)], kl, ORANGE, 2, alpha=0.85, dash=[10, 7])
    label(ctx, clamp((t - s1 - 1.2) / 0.8), c1, (WALLS[0][1], 960), (200, 960), "GROUND FLOOR WALL", a=gone(t, s2 + 0.3))
    label(ctx, clamp((t - s1 - 2.0) / 0.8), ORANGE, (WALLS[1][0] - 40, TP - 10), (880, 850), "TOP PLATES LEVEL",
          anchor="r", a=gone(t, s2 + 0.3))

    # ---- 2 floor truss: chords, end blocks, steel webs (nail plates at the joints)
    c2 = tl.col(2, t)
    kt = prog(t, s2 + 0.2, 1.0)
    if kt > 0:
        lift = (1 - ease(clamp((t - s2 - 0.2) / 0.9))) * -60          # lowered onto the plates
        ctx.save(); ctx.translate(0, lift)
        a = clamp((t - s2 - 0.1) / 0.3)
        polyline(ctx, rect_pts(TX0, TC_T, TX1, TC_B), 1, c2, 3, alpha=a)
        polyline(ctx, rect_pts(TX0, BC_T, TX1, TP), 1, c2, 3, alpha=a)
        for x0 in (TX0, TX1 - 20):
            polyline(ctx, rect_pts(x0, TC_B, x0 + 20, BC_T), 1, c2, 2.5, alpha=a)
        polyline(ctx, web_pts(), kt, c2, 4, alpha=a)
        if kt >= 1:
            for (x, y) in web_pts()[1:-1]:
                dot(ctx, x, y, 5, c2, 0.9)
        ctx.restore()
    label(ctx, clamp((t - s2 - 1.4) / 0.8), c2, (300, TC_T), (330, 530), "FLOOR TRUSS", a=gone(t, s3 + 0.3))
    label(ctx, clamp((t - s2 - 2.0) / 0.8), c2, (392, 695), (300, 850), "STEEL WEBS", a=gone(t, s3 + 0.3))
    label(ctx, clamp((t - s2 - 2.6) / 0.8), c2, (760, TP - 15), (820, 920), "TIMBER CHORDS", anchor="r",
          a=gone(t, s3 + 0.3))

    # ---- 3 tie-down brackets (both ends: over the bottom chord and the top plates)
    c3 = tl.col(3, t)
    for j, x in enumerate((WALLS[0][1] - 6, WALLS[1][0] - 26)):
        k = prog(t, s3 + 0.3 + j * 0.4, 0.6)
        if k <= 0: continue
        polyline(ctx, rect_pts(x, BC_T + 6, x + 32, TP1 + 12), k, c3, 3)
        if k >= 1:
            for y in (BC_T + 16, BC_T + 26, TP + 8, TP1 + 4):
                dot(ctx, x + 16, y, 3, c3, 0.9)
    label(ctx, clamp((t - s3 - 1.1) / 0.8), c3, (WALLS[0][1] + 10, TP + 4), (220, 850), "TIE-DOWN BRACKET",
          a=gone(t, s4 + 0.3))

    # ---- 4 edge trimmers (cut, outside the truss ends)
    c4 = tl.col(4, t)
    for j, (x0, x1) in enumerate(((WALLS[0][0], TX0), (TX1, WALLS[1][1]))):
        k = prog(t, s4 + 0.2 + j * 0.4, 0.7)
        if k <= 0: continue
        yt = TP - (TP - TC_T) * k
        fill_poly(ctx, rect_pts(x0, yt, x1, TP)[:4], BG, 1)
        polyline(ctx, rect_pts(x0, yt, x1, TP), 1, c4, 3)
        if k >= 1:
            polyline(ctx, [(x0, TC_T), (x1, TP)], 1, c4, 1.2, alpha=0.6)
    label(ctx, clamp((t - s4 - 1.0) / 0.8), c4, (WALLS[0][0] + 8, 650), (190, 530), "EDGE TRIMMER", a=gone(t, s5 + 0.3))

    # ---- 5 strongback (cut, on edge, in the V at mid-span) + its run shown dashed along the floor
    c5 = tl.col(5, t)
    k = prog(t, s5 + 0.3, 0.6)
    if k > 0:
        x0, x1, y0, y1 = SBK
        timber_cut(ctx, x0, y1 - (y1 - y0) * k, x1, y1, c5, 1)
        if k >= 1:
            dot(ctx, (x0 + x1) / 2, (y0 + y1) / 2, 3, c5, 0.9)
    label(ctx, clamp((t - s5 - 1.0) / 0.8), c5, (SBK[1], 712), (580, 850), "STRONGBACK", a=gone(t, s6 + 0.3))
    label(ctx, clamp((t - s5 - 1.8) / 0.8), c5, (SBK[0], 700), (480, 530), "ON EDGE", anchor="r", a=gone(t, s6 + 0.3))

    # ---- 6 services: duct (cut) in an open triangle, waste pipe along the truss through the webs
    c6 = tl.col(6, t)
    flow = prog(t, r0 + 0.8, 0.3) * gone(t, r0 + 3.4, 0.4)
    kd = prog(t, s6 + 0.3, 0.6)
    if kd > 0:
        x, y, r = DUCT
        ctx.set_source_rgba(*BG, 1); ctx.arc(x, y, r * kd, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgba(*c6, 1); ctx.set_line_width(3); ctx.arc(x, y, r * kd, 0, 2 * math.pi); ctx.stroke()
        ctx.set_line_width(1.4); ctx.arc(x, y, r * kd - 6, 0, 2 * math.pi); ctx.stroke()
        if flow > 0:                                       # air: a pulse in the duct
            ph = (t * 1.6) % 1
            ctx.set_source_rgba(*ORANGE, flow * (1 - ph)); ctx.set_line_width(3)
            ctx.arc(x, y, 4 + 12 * ph, 0, 2 * math.pi); ctx.stroke()
    kp = prog(t, s6 + 1.0, 1.2)
    if kp > 0:
        polyline(ctx, PIPE, kp, c6, 18)
        polyline(ctx, PIPE, kp, BG, 12)
        if flow > 0:                                       # water: dashes running along the pipe
            ctx.save()
            ctx.set_dash([14, 18], -t * 60)
            ctx.set_source_rgba(*ORANGE, 0.9 * flow); ctx.set_line_width(4)
            ctx.move_to(*PIPE[0])
            for p in PIPE[1:]: ctx.line_to(*p)
            ctx.stroke(); ctx.set_dash([]); ctx.restore()
    label(ctx, clamp((t - s6 - 0.9) / 0.8), c6, (DUCT[0] - 10, DUCT[1] + DUCT[2]), (300, 920), "DUCT",
          a=gone(t, s7 + 0.3))
    label(ctx, clamp((t - s6 - 2.0) / 0.8), c6, (800, 681), (860, 530), "WASTE PIPE", anchor="r", a=gone(t, s7 + 0.3))

    # ---- 7 flooring sheets (glued + screwed to the top chords)
    c7 = tl.col(7, t)
    for j, (a, b) in enumerate(((WALLS[0][0], 540), (540, WALLS[1][1]))):
        k = prog(t, s7 + 0.2 + j * 0.5, 0.7)
        if k <= 0: continue
        xe = a + (b - a) * k
        fill_poly(ctx, rect_pts(a + 1, FL_T, xe - 1, TC_T)[:4], BLUE, 0.22)
        polyline(ctx, rect_pts(a + 1, FL_T, xe - 1, TC_T), 1, c7, 2.5)
    kg = prog(t, s7 + 1.4, 0.8)
    if kg > 0:
        for x in range(170, 920, 75):
            dot(ctx, x, FL_T + 7, 2.5, c7, 0.9 * kg)
    label(ctx, clamp((t - s7 - 0.9) / 0.8), c7, (330, FL_T), (360, 530), "FLOORING SHEETS", a=gone(t, s8 + 0.3))
    label(ctx, clamp((t - s7 - 1.8) / 0.8), c7, (770, FL_T + 7), (880, 470), "GLUED + SCREWED", anchor="r",
          a=gone(t, s8 + 0.3))

    # ---- 8 upper wall frames on the floor + plasterboard ceiling on battens below
    c8 = tl.col(8, t)
    for j, (a, b) in enumerate(WALLS):
        k = prog(t, s8 + 0.2 + j * 0.3, 0.8)
        if k <= 0: continue
        timber_cut(ctx, a, UBP_T, b, FL_T, c8, 1)
        yt = UBP_T - (UBP_T - UW_TOP) * k
        polyline(ctx, [(a + 6, UBP_T), (a + 6, yt)], 1, c8, 2.5)
        polyline(ctx, [(b - 6, UBP_T), (b - 6, yt)], 1, c8, 2.5)
        if k >= 1:                                         # break line: the wall carries on up
            polyline(ctx, [(a - 8, UW_TOP + 6), (a + 14, UW_TOP + 6), (a + 20, UW_TOP - 6), (a + 26, UW_TOP + 14),
                           (a + 32, UW_TOP + 6), (b + 8, UW_TOP + 6)], 1, WHITE, 1.6, alpha=0.7)
    kc = prog(t, s8 + 1.2, 0.9)
    if kc > 0:
        x0, x1 = WALLS[0][1], WALLS[1][0]
        for x in range(190, 900, 90):
            if x < x0 + (x1 - x0) * kc:
                polyline(ctx, rect_pts(x - 10, TP, x + 10, CEIL_T), 1, c8, 1.8)
        xe = x0 + (x1 - x0) * kc
        fill_poly(ctx, rect_pts(x0, CEIL_T, xe, CEIL_B)[:4], BLUE, 0.22)
        polyline(ctx, rect_pts(x0, CEIL_T, xe, CEIL_B), 1, c8, 2.5)
    label(ctx, clamp((t - s8 - 0.8) / 0.8), c8, (WALLS[0][1] - 6, 520), (210, 520), "UPPER WALL FRAME", a=gone(t, r0))
    label(ctx, clamp((t - s8 - 1.9) / 0.8), c8, (620, CEIL_B), (650, 920), "CEILING BELOW", a=gone(t, r0))

    # ---- result: the open space inside the floor lights up, span dimension, services flow
    ka = prog(t, r0 + 0.3, 0.5) * gone(t, r0 + 3.4, 0.4)
    if ka > 0:
        for i, tri in enumerate(open_triangles()):
            k = prog(t, r0 + 0.3 + i * 0.08, 0.3) * ka
            if k > 0:
                fill_poly(ctx, tri, ORANGE, 0.22 * k)
    kdim = prog(t, r0 + 0.5, 0.8)
    if kdim > 0:
        dim_h(ctx, SPAN_Y, WALLS[0][1], WALLS[1][0], "SPANS WALL TO WALL", kdim, ORANGE)
    pt = prog(t, r0 + 0.8, 0.5)
    if pt > 0:
        text(ctx, "MOSTLY AIR. ROOM FOR SERVICES.", 540, 1205, 30, ORANGE, alpha=pt, bold=True, anchor="c")


# ---------------------------------------------------------------- 3D model (mm): a two-wall strip of the house
def model3d():
    from engine.three_d import box, member3d
    P = []; o = 0
    SP, LZ, WH = 5400, 4800, 2400              # span (x), length along the walls (z), ground wall height
    FL = 150                                    # slab top
    TP = FL + WH                                # top of the ground floor top plates
    D = 350                                     # truss depth
    g = box(-900, SP + 900, -300, 0, -900, LZ + 900, o, "ground"); g.base = True; P.append(g)
    P.append(box(-100, SP + 100, 0, FL, -100, LZ + 100, o, "concrete")); o += 1
    # 1 ground floor wall frames: the two bearing walls along z + the far end wall
    for x0 in (0, SP - 90):
        P.append(box(x0, x0 + 90, FL, FL + 45, 0, LZ, o)); P.append(box(x0, x0 + 90, TP - 90, TP, 0, LZ, o))
        for z in range(0, LZ, 600):
            P.append(box(x0, x0 + 90, FL + 45, TP - 90, z, z + 45, o))
    P.append(box(90, SP - 90, FL, FL + 45, 0, 90, o)); P.append(box(90, SP - 90, TP - 90, TP, 0, 90, o))
    for x in range(600, SP - 300, 600):
        P.append(box(x, x + 45, FL + 45, TP - 90, 0, 90, o))
    o += 1
    # 2.. floor trusses, one order each so they drop in one by one
    zs = list(range(150, LZ, 600))
    nx = 8
    for z in zs:
        zc = z + 45
        P.append(box(35, SP - 35, TP, TP + 45, z, z + 90, o))                  # bottom chord (flat)
        P.append(box(35, SP - 35, TP + D - 45, TP + D, z, z + 90, o))          # top chord (flat)
        for x0 in (35, SP - 125):
            P.append(box(x0, x0 + 90, TP + 45, TP + D - 45, z, z + 90, o))     # end blocks
        xs = [125 + (SP - 250) * i / nx for i in range(nx + 1)]
        for i in range(nx):
            ya = TP + D - 45 if i % 2 == 0 else TP + 45
            yb = TP + 45 if i % 2 == 0 else TP + D - 45
            for dz in (-30, 30):                                               # a steel web each side of the chord
                P.append(member3d((xs[i], ya, zc + dz), (xs[i + 1], yb, zc + dz), 45, 6, o, "steel"))
        o += 1
    # edge trimmers (both ends of the trusses)
    for x0 in (0, SP - 35):
        P.append(box(x0, x0 + 35, TP, TP + D, 0, LZ, o))
    o += 1
    # strongback on edge at mid-span
    xm = SP / 2 - 300
    P.append(box(xm - 22, xm + 22, TP + 45, TP + 45 + 190, 0, LZ, o)); o += 1
    ORD_STRONG = o - 1
    # services: waste pipe along a truss bay, a duct across the trusses
    P.append(member3d((SP * 0.55, TP + 250, 2550), (SP - 400, TP + 225, 2550), 100, 100, o, "membrane"))
    P.append(member3d((SP * 0.55, TP + 250, 2550), (SP * 0.55, TP + D + 40, 2550), 100, 100, o, "membrane"))
    P.append(box(SP * 0.3 - 110, SP * 0.3 + 110, TP + 70, TP + 290, 0, LZ, o, "glass")); o += 1
    # flooring over the far half (the near half left open to show the trusses)
    for z0, z1 in ((0, 1200), (1200, 2400)):
        P.append(box(0, SP, TP + D, TP + D + 22, z0, z1, o, "board"))
    o += 1
    # upper wall frames on the far end wall and the left wall (far half)
    UB = TP + D + 22
    P.append(box(0, SP, UB, UB + 45, 0, 90, o)); P.append(box(0, SP, UB + WH - 90, UB + WH, 0, 90, o))
    for x in range(0, SP, 600):
        P.append(box(x, x + 45, UB + 45, UB + WH - 90, 0, 90, o))
    P.append(box(0, 90, UB, UB + 45, 90, 2400, o)); P.append(box(0, 90, UB + WH - 90, UB + WH, 90, 2400, o))
    for z in range(600, 2400, 600):
        P.append(box(0, 90, UB + 45, UB + WH - 90, z, z + 45, o))
    o += 1
    # plasterboard ceiling under the far half
    P.append(box(90, SP - 90, TP - 45, TP - 32, 90, 2400, o, "board")); o += 1
    cfg = {"target": (SP / 2, 2700, LZ / 2), "yaw": 55, "pitch": 30, "dist": 26000, "scale": 2.1,
           "cy_hook": 1115, "cy_result": 830, "cy_cover": 1000, "cover_scale": 0.85}
    return P, cfg
