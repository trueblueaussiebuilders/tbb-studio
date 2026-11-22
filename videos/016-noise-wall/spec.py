"""016 Freeway noise wall (infrastructure)."""
import math
from engine.blueprint import *

META = {
    "category": "infrastructure",
    "title": "NOISE WALL",
    "subtitle": "INFRASTRUCTURE  //  TYPICAL AU METHOD",
    "dwg": "016",
    "hook_start": 0.6,                 # frame 0 already shows posts, plinths and the first panels
    "drawing": "NOISE WALL",
    "section_label": "ELEVATION ALONG WALL  (NTS)",
    "hook": ["THAT FREEWAY WALL", "STANDS ON", "HIDDEN PILES."],
    "hook_sub": "HOW A NOISE WALL GOES UP",
    "cover": ["THE FREEWAY", "WALL HAS", "HIDDEN PILES."],
    "xray": {"after_step": 4, "upto": 12, "hot": list(range(1, 13))},   # piles + posts in, panels still to come
    "steps": [
        ("SET OUT", "Surveyors peg every post position along the line. Buried services are found and marked first."),
        ("BORE THE PILES", "A piling rig drills a deep hole at each post position. The base is cleaned out."),
        ("STEEL CAGE", "A reinforcement cage is lowered into each hole, held off the sides with spacers."),
        ("POST + POUR", "The steel post is set in the hole, plumb and to line. Then the hole is filled with concrete."),
        ("PLINTH PANEL", "A precast plinth goes in first at ground level. It closes the gap so noise can't leak under."),
        ("PANELS SLIDE IN", "A crane lowers each panel between the post flanges. They stack one on top of another."),
        ("SEALS + CAPS", "Rubber seals close the joints at the posts. Caps go on top of the posts."),
        ("FINISH", "The ground is backfilled and landscaped. The panels often get an anti-graffiti coating."),
    ],
    "result": "Wind pushes on the panels. The posts carry it down into the piles. That's what keeps the wall standing.",
}

NARRATION = {
    "hook": "That freeway wall isn't just panels. Every post sits in a buried pile.",
    "steps": [
        "First, surveyors peg every post position along the line. Buried services are found and marked before any digging.",
        "A piling rig drills a deep hole at each post position. The bottom of the hole is cleaned out.",
        "A steel reinforcement cage is lowered into each hole. Spacers hold it off the sides.",
        "The steel post is set in the hole, plumb and on line. Then the hole is filled with concrete.",
        "A precast plinth goes in first, at ground level. It closes the gap, so noise can't leak under the wall.",
        "A crane lowers each panel down between the post flanges. They stack, one on top of another.",
        "Rubber seals close the joints at the posts. Then caps go on top of the posts.",
        "Finally, the ground is backfilled and landscaped. The panels often get an anti-graffiti coating.",
    ],
    "result": "Wind pushes on the panels. The posts carry that load down into the piles. That's what keeps the wall standing.",
    "end": "Follow for more.",
}

CAPTION = """That freeway wall isn't just panels 👇 How a noise wall goes up next to a freeway.

Typical: the wall line and post positions are surveyed and pegged, and buried services are located (often by potholing) before piling. A piling rig bores a hole at each post position, the base is cleaned, and a reinforcement cage goes in with spacers. The steel post (often a universal column) is set plumb and to line in the hole and the pile is poured around it. A precast plinth or bottom panel closes the gap at ground level, then the panels (precast concrete, or lighter panels such as acrylic, timber or composite) are lowered in by crane between the post flanges and stack on each other. Seals go in at the post joints, caps go on the posts, the ground is backfilled and landscaped, and many walls get an anti-graffiti coating.
Wind load on the panels goes into the posts and down into the piles, so pile depth depends on the wall height, the wind and the ground.
Typical only. Your engineer's design governs.

#noisewall #freeway #civilengineering #infrastructure #piling #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
GL = 980                              # finished ground line
PX = [330, 600, 870]                  # post centres
PH = 32                               # pile half-width
PILE_B = 1195                         # pile toe
POST_T, POST_B, PW = 585, 1160, 12    # post top, embedded bottom, half-width
WALL_R = 965                          # wall runs on past the last post (break line)
PLINTH = (940, 1000)                  # plinth panel top / bottom (slightly below ground)
ROWS = [(855, 940), (770, 855), (685, 770), (600, 685)]   # panel rows, bottom up
SERV = (465, 1090)                    # buried service found at set-out

BAYS = [(PX[0] + 4, PX[1] - 4), (PX[1] + 4, PX[2] - 4), (PX[2] + 4, WALL_R)]
PILE_CONC = [concrete_points(160 + i, x - PH + 4, GL + 4, x + PH - 4, PILE_B - 4, 70) for i, x in enumerate(PX)]
ROW_CONC = [concrete_points(170 + j, BAYS[0][0], y0, WALL_R, y1, 26) for j, (y0, y1) in enumerate([PLINTH] + ROWS)]


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


def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def arrow(ctx, x0, y0, x1, y1, col, p=1.0, a=1.0, head=12):
    if p <= 0: return
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    polyline(ctx, [(x0, y0), (xe, ye)], 1, col, 3, alpha=a)
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    polyline(ctx, [(xe - ux * head - uy * head * 0.8, ye - uy * head + ux * head * 0.8), (xe, ye),
                   (xe - ux * head + uy * head * 0.8, ye - uy * head - ux * head * 0.8)], 1, col, 3, alpha=a)


def panel(ctx, x0, x1, y0, y1, col, k, dy=0.0, seed=0):
    """One precast panel in elevation (dark fill, outline, concrete stipple)."""
    if k <= 0: return
    fill_poly(ctx, rect_pts(x0, y0 + dy, x1, y1 + dy)[:4], BG, k)
    polyline(ctx, rect_pts(x0, y0 + dy, x1, y1 + dy), 1, col, 2.5, alpha=k)
    pts = [(x, y + dy, r) for x, y, r in ROW_CONC[seed] if x0 + 6 < x < x1 - 6]
    draw_concrete(ctx, pts, col, 0.35 * k)


def post(ctx, x, col, k, dy=0.0, embedded=False):
    """Steel post (column) in elevation: two flanges and the web line."""
    if k <= 0: return
    top, bot = POST_T + dy, POST_B + dy
    fill_poly(ctx, rect_pts(x - PW, top, x + PW, min(bot, GL + 2) if embedded else bot)[:4], BG, k)
    above = [(x - PW, GL), (x - PW, top), (x + PW, top), (x + PW, GL)] if embedded else \
        rect_pts(x - PW, top, x + PW, bot)
    polyline(ctx, above, 1, col, 3, alpha=k)
    polyline(ctx, [(x, top + 4), (x, (GL if embedded else bot) - 4)], 1, col, 1.4, alpha=0.6 * k)
    if embedded:   # cast into the pile: drawn dashed inside the concrete
        polyline(ctx, [(x - PW, GL), (x - PW, bot), (x + PW, bot), (x + PW, GL)], 1, col, 2, alpha=0.8 * k, dash=[6, 5])


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    # ---- ground (step 1): surface line, faint earth below
    pg = prog(t, s1 + 0.1, 1.0)
    if pg > 0:
        earth_hatch(ctx, 90, GL, 990, 1205, WHITE, 0.12, reveal=pg)
        earth_hatch(ctx, 90, GL, 990, GL + 18, WHITE, 0.3, reveal=pg)
        polyline(ctx, [(90, GL), (990, GL)], pg, WHITE, 3)

    # ---- 1 set out: pegs at each post, a blue string line, a service found and marked
    c1 = tl.col(1, t)
    polyline(ctx, [(110, GL - 14), (980, GL - 14)], prog(t, s1 + 0.6, 0.9) * gone(t, s3, 0.5), BLUE, 2, dash=[10, 7])
    for i, x in enumerate(PX):
        k = prog(t, s1 + 0.8 + i * 0.25, 0.3) * gone(t, s2 + 0.4 + i * 0.9, 0.3)
        if k > 0:
            polyline(ctx, [(x, GL - 40), (x, GL)], 1, ORANGE, 4, alpha=k)
            fill_poly(ctx, [(x - 9, GL - 40), (x + 9, GL - 40), (x, GL - 52)], ORANGE, k)
    label(ctx, clamp((t - s1 - 1.0) / 0.8), c1, (PX[0] - 4, GL - 30), (110, 900), "SET-OUT PEGS", a=gone(t, s2))
    ps = prog(t, s1 + 1.7, 0.6) * gone(t, s4, 0.6)      # the service is avoided, then out of the story
    if ps > 0:
        ctx.set_source_rgba(*BG, ps); ctx.arc(*SERV, 20, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgba(*ORANGE, ps); ctx.set_line_width(3); ctx.set_dash([7, 5])
        ctx.arc(*SERV, 20, 0, 2 * math.pi); ctx.stroke(); ctx.set_dash([])
        polyline(ctx, [(SERV[0] - 60, SERV[1]), (SERV[0] - 22, SERV[1])], ps, ORANGE, 2, dash=[7, 5])
        polyline(ctx, [(SERV[0] + 22, SERV[1]), (SERV[0] + 70, SERV[1])], ps, ORANGE, 2, dash=[7, 5])
    label(ctx, clamp((t - s1 - 2.0) / 0.8), ORANGE, (SERV[0] - 14, SERV[1] + 14), (110, 1170), "SERVICES FOUND",
          a=gone(t, s2 + 0.2))

    # ---- 2 bore the holes, one after another, with the auger
    c2 = tl.col(2, t)
    hole_t = [s2 + 0.4 + i * 0.9 for i in range(3)]
    for i, x in enumerate(PX):
        k = prog(t, hole_t[i], 0.8)
        if k <= 0: continue
        yb = GL + (PILE_B - GL) * k
        fill_poly(ctx, rect_pts(x - PH, GL, x + PH, yb)[:4], BG, 1)
        polyline(ctx, [(x - PH, GL), (x - PH, yb), (x + PH, yb), (x + PH, GL)], 1, c2, 2.5,
                 dash=None if t > s4 else [9, 6])
    # the auger: a mast over the hole being drilled, spiral flights on the bottom
    for i, x in enumerate(PX):
        t0 = hole_t[i]
        if not (t0 - 0.1 <= t < t0 + 0.95): continue
        k = prog(t, t0, 0.8)
        tip = GL - 60 + (PILE_B - 10 - GL + 60) * k
        ak = clamp((t - t0 + 0.1) / 0.15) * clamp((t0 + 0.95 - t) / 0.15)
        polyline(ctx, [(x, 470), (x, tip)], 1, WHITE, 4, alpha=ak)
        for j in range(8):
            y = tip - j * 22
            if y < 470: break
            polyline(ctx, [(x - 22, y), (x + 22, y - 11)], 1, c2, 3, alpha=ak)
    ax = next((x for x, t0 in zip(PX, hole_t) if t < t0 + 0.95), PX[-1])
    label(ctx, clamp((t - s2 - 0.5) / 0.6), WHITE, (ax, 520), (940, 445), "PILING RIG AUGER", anchor="r",
          a=gone(t, hole_t[-1] + 0.9))
    label(ctx, clamp((t - s2 - 1.4) / 0.8), c2, (PX[0] - PH, 1090), (110, 1060), "PILE HOLE", a=gone(t, s3 + 0.2))

    # ---- 3 steel cages lowered in
    c3 = tl.col(3, t)
    for i, x in enumerate(PX):
        k = prog(t, s3 + 0.2 + i * 0.6, 0.9)
        if k <= 0: continue
        dy = -(1 - k) * 260
        ctx.save(); ctx.rectangle(80, 400, 920, PILE_B + 2 - 400); ctx.clip()
        for cx in (x - PH + 9, x + PH - 9):
            polyline(ctx, [(cx, GL - 30 + dy), (cx, PILE_B - 10 + dy)], 1, c3, 2.5)
        for y in range(int(GL - 20), PILE_B - 10, 26):
            polyline(ctx, [(x - PH + 9, y + dy), (x + PH - 9, y + dy)], 1, c3, 1.6, alpha=0.8)
        ctx.restore()
    label(ctx, clamp((t - s3 - 1.0) / 0.8), c3, (PX[0] - PH + 9, 1140), (110, 1150), "STEEL CAGE", a=gone(t, s4 + 0.5))

    # ---- 4 posts dropped in plumb, then concrete poured
    c4 = tl.col(4, t)
    pour_t = s4 + 1.9
    for i, x in enumerate(PX):
        kp = prog(t, pour_t + i * 0.35, 0.8)
        if kp > 0:
            ytop = PILE_B - (PILE_B - GL) * kp
            ctx.save(); ctx.rectangle(x - PH + 2, ytop, 2 * PH - 4, PILE_B - ytop); ctx.clip()
            draw_concrete(ctx, PILE_CONC[i], c4 if t < s5 else WHITE, 0.7)
            ctx.restore()
    for i, x in enumerate(PX):
        k = prog(t, s4 + 0.2 + i * 0.45, 0.7)
        if k <= 0: continue
        post(ctx, x, tl.col(4, t), 1.0, dy=-(1 - k) * 320, embedded=t > pour_t + 0.4 + i * 0.35)
    # plumb check on the first post
    pb = prog(t, s4 + 1.1, 0.4) * gone(t, s5, 0.4)
    polyline(ctx, [(PX[0] + 34, POST_T - 10), (PX[0] + 34, GL - 20)], pb, BLUE, 2, dash=[8, 6])
    if pb > 0: dot(ctx, PX[0] + 34, GL - 20, 7, BLUE, pb)
    label(ctx, clamp((t - s4 - 0.6) / 0.8), c4, (PX[0] - PW, 700), (110, 700), "STEEL POST", a=gone(t, s6))
    label(ctx, clamp((t - s4 - 1.2) / 0.8), BLUE, (PX[0] + 34, 620), (940, 482), "SET PLUMB + ON LINE", anchor="r",
          a=gone(t, s5))
    label(ctx, clamp((t - pour_t - 0.5) / 0.8), c4, (PX[0] - PH, 1100), (110, 1060), "CONCRETE PILE", a=gone(t, s6))

    # ---- 5 plinth panels at ground level
    c5 = tl.col(5, t)
    for i, (x0, x1) in enumerate(BAYS):
        k = prog(t, s5 + 0.3 + i * 0.4, 0.6)
        panel(ctx, x0, x1, *PLINTH, c5, clamp(k * 3), dy=-(1 - k) * 160, seed=0)
    label(ctx, clamp((t - s5 - 1.2) / 0.8), c5, (PX[0] + 30, 975), (110, 1010), "PLINTH", a=gone(t, s7))
    pn = prog(t, s5 + 2.0, 0.4) * gone(t, s6 + 0.3, 0.4)
    if pn > 0:
        text(ctx, "NO GAP UNDER", (PX[0] + PX[1]) / 2 + 5, 1042, 24, ORANGE, alpha=pn, bold=True, anchor="c", spacing=2)

    # ---- 6 panels slide down between the flanges, row by row
    c6 = tl.col(6, t)
    order = [(j, i) for j in range(len(ROWS)) for i in range(len(BAYS))]
    gap = max((tl.step_end(6) - s6 - 1.0) / len(order), 0.12)
    hook = None
    for n, (j, i) in enumerate(order):
        t0 = s6 + 0.2 + n * gap
        k = prog(t, t0, 0.45)
        if k <= 0: continue
        (x0, x1), (y0, y1) = BAYS[i], ROWS[j]
        dy = -(1 - k) * (y1 - 420)
        panel(ctx, x0, x1, y0, y1, c6, clamp(k * 4), dy=dy, seed=j + 1)
        if k < 1: hook = ((x0 + x1) / 2, y0 + dy)
    if hook:   # crane line on the panel being lowered
        polyline(ctx, [(hook[0], 400), (hook[0], hook[1] - 18)], 1, WHITE, 2)
        polyline(ctx, [(hook[0], hook[1] - 18), (hook[0] - 50, hook[1])], 1, WHITE, 1.6)
        polyline(ctx, [(hook[0], hook[1] - 18), (hook[0] + 50, hook[1])], 1, WHITE, 1.6)
    label(ctx, clamp((t - s6 - 0.8) / 0.8), c6, ((PX[1] + PX[2]) / 2, 520), (940, 482),
          "LOWERED BETWEEN POSTS", anchor="r", a=gone(t, s7))
    label(ctx, clamp((t - s6 - 1.6) / 0.8), c6, (PX[0] - PW, 640), (110, 640), "POST FLANGE", a=gone(t, s7))

    # posts are drawn over the panels (the panels sit inside the flanges)
    for i, x in enumerate(PX):
        if t >= s5:
            post(ctx, x, tl.col(4, t) if t < s6 else WHITE, 1.0, embedded=True)

    # ---- 7 seals down each post, caps on top
    c7 = tl.col(7, t)
    for i, x in enumerate(PX):
        for sx in (x - PW - 4, x + PW + 4):
            if i == 0 and sx < x: continue          # end post: panels on one side only
            polyline(ctx, [(sx, ROWS[-1][0] + 4), (sx, PLINTH[1] - 4)], prog(t, s7 + 0.2 + i * 0.3, 0.9), ORANGE, 3)
        k = prog(t, s7 + 1.6 + i * 0.25, 0.4)
        if k > 0:
            dy = -(1 - k) * 60
            fill_poly(ctx, rect_pts(x - 20, POST_T - 14 + dy, x + 20, POST_T + dy)[:4], BG, k)
            polyline(ctx, rect_pts(x - 20, POST_T - 14 + dy, x + 20, POST_T + dy), 1, c7, 3, alpha=k)
    label(ctx, clamp((t - s7 - 0.6) / 0.8), c7, (PX[0] + PW + 4, 760), (110, 760), "RUBBER SEAL", a=gone(t, s8))
    label(ctx, clamp((t - s7 - 1.8) / 0.8), c7, (PX[2], POST_T - 16), (940, 445), "POST CAP", anchor="r", a=gone(t, s8))

    # ---- 8 backfill + landscaping + anti-graffiti coat sweeping across the panels
    c8 = tl.col(8, t)
    pf = prog(t, s8 + 0.2, 0.8)
    if pf > 0:
        polyline(ctx, [(90, GL - 6), (990, GL - 6)], pf, c8, 2, alpha=0.8)
        for x in (160, 460, 520, 735, 800, 940):
            k = prog(t, s8 + 0.6 + (x - 180) / 900, 0.4)
            if k <= 0: continue
            r = 20 + (x % 3) * 5
            ctx.set_source_rgba(*BG, k); ctx.arc(x, GL - 6, r * k, math.pi, 2 * math.pi); ctx.fill()
            ctx.set_source_rgba(*c8, k); ctx.set_line_width(2.5); ctx.arc(x, GL - 6, r * k, math.pi, 2 * math.pi); ctx.stroke()
    pc = prog(t, s8 + 1.4, 1.4)
    if 0 < pc < 1:
        xs = BAYS[0][0] + (WALL_R - BAYS[0][0] + 160) * pc
        ctx.save(); ctx.rectangle(BAYS[0][0], ROWS[-1][0], WALL_R - BAYS[0][0], PLINTH[0] - ROWS[-1][0]); ctx.clip()
        g = cairo.LinearGradient(xs - 160, 0, xs, 0)
        g.add_color_stop_rgba(0, *BLUE, 0.0); g.add_color_stop_rgba(0.8, *BLUE, 0.35); g.add_color_stop_rgba(1, *BLUE, 0.0)
        ctx.set_source(g); ctx.paint(); ctx.restore()
    label(ctx, clamp((t - s8 - 1.0) / 0.8), c8, (160, GL - 30), (110, 900), "LANDSCAPING", a=gone(t, r0))
    label(ctx, clamp((t - s8 - 1.6) / 0.8), c8, (735, 640), (940, 482), "ANTI-GRAFFITI COAT", anchor="r", a=gone(t, r0))

    # ---- result: wind on the panels -> posts -> down into the piles
    pw = prog(t, r0 + 0.1, 0.6)
    for x in (465, 735):
        arrow(ctx, x, 700, x - 105, 700, BLUE, p=pw)
        arrow(ctx, x, 700, x + 105, 700, BLUE, p=pw)
    if pw > 0:
        text(ctx, "WIND ON PANELS", 540, 520, 30, BLUE, alpha=clamp(pw * 2 - 1), bold=True, anchor="c", spacing=3)
    pd = prog(t, r0 + 0.8, 0.8)
    for x in PX[1:]:
        arrow(ctx, x + 40, 760, x + 40, PILE_B - 20, BLUE, p=pd)
    if pd > 0:
        for i, ln in enumerate(("INTO THE", "PILES")):
            text(ctx, ln, (PX[0] + PX[1]) / 2, 1110 + i * 40, 30, BLUE, alpha=clamp(pd * 2 - 1), bold=True, anchor="c",
                 spacing=2)
    dim_v(ctx, 250, ROWS[-1][0], GL, "WALL", prog(t, r0 + 1.4, 0.6))
    dim_v(ctx, 250, GL, PILE_B, "PILE", prog(t, r0 + 1.8, 0.6), col=ORANGE)


# ---------------------------------------------------------------- 3D model (mm): a run of noise wall, cut-away ground
def model3d():
    from engine.three_d import box
    P = []; o = 0
    BAY, NB = 4000, 3                         # post spacing, bays
    HW = 5000                                 # wall height above ground
    PD, PS = 4200, 750                        # pile depth, pile size (square, NTS)
    LX = BAY * NB
    # x-ray ground: a thin plate for the ground surface, with the buried piles hanging below it
    g = box(-1500, LX + 1500, -450, 0, -4500, 1300, o, "ground"); g.base = True; P.append(g); o += 1
    xs = [i * BAY for i in range(NB + 1)]
    for x in xs:                              # piles, one by one
        P.append(box(x - PS / 2, x + PS / 2, -PD, 0, -PS / 2, PS / 2, o, "concrete")); o += 1
    for x in xs:                              # steel posts (UC), web + flanges
        P.append(box(x - 130, x + 130, 0, HW + 150, -15, 15, o, "steel"))
        P.append(box(x - 130, x - 105, 0, HW + 150, -130, 130, o, "steel"))
        P.append(box(x + 105, x + 130, 0, HW + 150, -130, 130, o, "steel"))
        o += 1
    for b in range(NB):                       # plinth panels
        P.append(box(xs[b] + 110, xs[b + 1] - 110, -150, 500, -60, 60, o, "precast")); o += 1
    rows = 4; RH = (HW - 500) / rows
    for r in range(rows):                     # panels, row by row
        for b in range(NB):
            P.append(box(xs[b] + 110, xs[b + 1] - 110, 500 + r * RH, 500 + (r + 1) * RH - 20, -60, 60, o, "precast"))
            o += 1
    for x in xs:                              # post caps
        P.append(box(x - 170, x + 170, HW + 150, HW + 230, -170, 170, o, "steel"))
    o += 1
    cfg = {"target": (LX / 2, -900, 0), "yaw": -30, "pitch": 20, "dist": 42000, "scale": 2.6,
           "cy_hook": 1160, "cy_result": 830, "cy_cover": 1010, "cover_scale": 0.92}
    return P, cfg
