"""007 Reinforced concrete block retaining wall (civil)."""
import math
from engine.blueprint import *

META = {
    "category": "civil",
    "title": "BLOCK RETAINING WALL",
    "subtitle": "CIVIL  //  TYPICAL AU METHOD",
    "dwg": "007",
    "drawing": "BLOCK RETAINING WALL",
    "section_label": "SECTION THROUGH WALL  (NTS)",
    "hook": ["THAT WALL IS", "HOLDING BACK", "TONNES OF DIRT."],
    "hook_sub": "HOW A BLOCK RETAINING WALL IS BUILT",
    "cover": ["WHY RETAINING", "WALLS DON'T", "FALL OVER."],
    "steps": [
        ("CUT THE BANK", "Wall set out, bank cut back to a safe batter, and the footing trench dug."),
        ("FOOTING REO", "Reo cage in the trench, with starter bars standing up at the block cores."),
        ("POUR FOOTING", "The footing is poured, casting the starter bars in place."),
        ("LAY THE BLOCKS", "Hollow concrete blocks laid in mortar, around the starter bars."),
        ("BARS + CORE FILL", "Vertical bars lapped to the starters, then the cores filled with concrete."),
        ("WATERPROOF", "Membrane on the back face, with a protection board over it."),
        ("DRAINAGE", "Slotted ag pipe at the base, then free-draining gravel wrapped in geofabric."),
        ("BACKFILL", "Soil placed and compacted in layers. The drain is piped away to stormwater."),
    ],
    "result": "A solid wall holding back the soil, with water drained away so pressure can't build up behind it.",
}

NARRATION = {
    "hook": "That wall is holding back tonnes of soil. Here's how a block retaining wall is built.",
    "steps": [
        "First, the wall is set out. The bank is cut back to a safe slope, and a trench is dug for the footing.",
        "A reinforcement cage goes in the trench. Starter bars stand up where the block cores will be.",
        "Then the footing is poured. The starter bars are cast in, standing up out of the concrete.",
        "Hollow concrete blocks are laid in mortar, around the starter bars.",
        "Vertical bars are lapped with the starters. Then the block cores are filled with concrete.",
        "The back face is waterproofed. A protection board goes over the membrane.",
        "A slotted drain pipe runs along the base. It's covered with free-draining gravel, wrapped in filter fabric.",
        "Finally, the soil is backfilled and compacted in layers. The drain is piped away to stormwater.",
    ],
    "result": "A solid wall that holds back the soil. Water drains away, so pressure never builds up behind it.",
    "end": "Follow for more.",
}

CAPTION = """Ever wondered why a retaining wall doesn't just tip over? 👇 How a reinforced block retaining wall is built.

Typical: hollow concrete blocks (often 200 or 300 mm) on a reinforced concrete footing with a heel under the retained soil, vertical bars lapped to footing starters, cores filled with concrete, a membrane on the back face, and a slotted ag drain in free-draining gravel at the base.
Taller walls, and walls near boundaries or buildings, generally need an engineer's design and a permit. Check with your council.
Typical only. Your engineer's design governs.

#retainingwall #civilconstruction #blockwork #concrete #landscaping #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
LOW_GL = 990                       # ground on the low (front) side
HIGH_GL = 600                      # ground on the retained (back) side
FT0, FT1 = 1010, 1080              # footing top / bottom
FX0, FX1 = 270, 620                # footing toe / heel ends
WX0, WX1 = 340, 420                # block wall faces
SHELL = 12                         # block face shell thickness
COURSES = 6
CH = (FT0 - HIGH_GL) / COURSES     # course height
BAR_X = 380
GRAV_X1, GRAV_TOP = 520, 640       # drainage gravel zone
PIPE = (472, FT0 - 16, 15)

# in-situ ground after the cut: excavated profile, then down to the bottom of the frame
CUT = [(90, LOW_GL), (255, LOW_GL), (255, 1085), (635, 1085), (850, HIGH_GL), (970, HIGH_GL)]
INSITU = CUT + [(970, 1110), (90, 1110)]
BANK = [(220, LOW_GL), (420, HIGH_GL), (970, HIGH_GL)]          # original steep bank (dashed)
BACKFILL = [(436, HIGH_GL), (850, HIGH_GL), (635, 1085), (620, 1085), (620, FT0), (GRAV_X1, FT0),
            (GRAV_X1, GRAV_TOP), (436, GRAV_TOP)]

CONC_F = concrete_points(71, FX0, FT0, FX1, FT1, 170, lambda x, y: FT0 + 4 < y < FT1 - 4 and FX0 + 4 < x < FX1 - 4)
CONC_CORE = concrete_points(72, WX0 + SHELL, HIGH_GL, WX1 - SHELL, FT0, 70,
                            lambda x, y: WX0 + SHELL + 4 < x < WX1 - SHELL - 4)
GRAV = gravel(73, 440, GRAV_TOP + 8, GRAV_X1 - 6, FT0 - 6, 140)


def poly_hatch(ctx, pts, col, alpha=0.35, reveal=1.0, step=36):
    """Earth hatch clipped to a polygon, revealed left to right."""
    if reveal <= 0: return
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
    ctx.save()
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.clip()
    ctx.rectangle(x1, y1, (x2 - x1) * reveal, y2 - y1); ctx.clip()
    ctx.set_source_rgba(*col, alpha); ctx.set_line_width(2)
    h = y2 - y1
    for k in range(int(-h) - 40, int(x2 - x1) + 40, step):
        for j in range(3):
            ctx.move_to(x1 + k + j * 8, y2); ctx.line_to(x1 + k + j * 8 + h, y1)
    ctx.stroke(); ctx.restore()


def label(ctx, p, col, tip, elbow, txt, anchor="l"):
    """Engine leader, plus a dark plate behind the text so leader lines never strike through it."""
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


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 existing bank (dashed), excavated profile, in-situ ground
    c = tl.col(1, t); p = prog(t, s1, 1.0)
    if p > 0:
        bank = 1 - clamp((t - s2) / 0.6)
        if bank > 0:
            polyline(ctx, BANK, 1, c, 2, alpha=0.8 * bank * clamp(p * 3), dash=[12, 8])
        poly_hatch(ctx, INSITU, c, reveal=prog(t, s1 + 0.5, 0.9))
        polyline(ctx, CUT, prog(t, s1 + 0.5, 0.9), c, 3)
        label(ctx, clamp((t - s1 - 0.6) / 0.8) * bank, c, (330, 770), (110, 445), "EXISTING BANK")
        tr = 1 - clamp((t - s3) / 0.5)
        label(ctx, clamp((t - s1 - 1.4) / 0.8) * tr, c, (450, 1085), (110, 1192), "FOOTING TRENCH")
        label(ctx, clamp((t - s1 - 1.8) / 0.8) * (1 - clamp((t - s4) / 0.5)), c, (760, 800), (940, 482),
               "CUT BATTER", anchor="r")

    # 2 footing reo cage + starter bar
    c = tl.col(2, t); p = prog(t, s2, 0.9)
    if p > 0:
        for yy in (FT0 + 9, FT1 - 9):
            polyline(ctx, [(FX0 + 10, yy), (FX0 + 10 + (FX1 - FX0 - 20) * p, yy)], 1, c, 2)
            x = FX0 + 22
            while x < FX0 + 10 + (FX1 - FX0 - 20) * p:
                dot(ctx, x, yy, 3, c); x += 32
        ps = prog(t, s2 + 0.7, 0.8)
        polyline(ctx, [(BAR_X + 90, FT1 - 14), (BAR_X, FT1 - 14), (BAR_X, FT0 - 140)], ps, c, 3.5)
        label(ctx, clamp((t - s2 - 1.3) / 0.8), c, (BAR_X, 930), (110, 1150), "STARTER BAR")

    # 3 footing pour
    c = tl.col(3, t); p = prog(t, s3, 1.1)
    if p > 0:
        clip_rect(ctx, FX0, FT0 - 2, FX0 + (FX1 - FX0) * p, FT1 + 2)
        ctx.set_source_rgba(*c, 0.14); ctx.rectangle(FX0, FT0, FX1 - FX0, FT1 - FT0); ctx.fill()
        draw_concrete(ctx, CONC_F, c, 0.75)
        ctx.restore()
        polyline(ctx, rect_pts(FX0, FT0, FX1, FT1), p, c, 3)
        label(ctx, clamp((t - s3 - 1.0) / 0.8), c, (580, 1060), (940, 1192), "CONCRETE FOOTING", anchor="r")

    # 4 block courses
    c = tl.col(4, t)
    for i in range(COURSES):
        pb = prog(t, s4 + 0.2 + i * 0.35, 0.4)
        if pb <= 0: continue
        y1 = FT0 - i * CH; y0 = y1 - CH
        dy = -(1 - pb) * 40
        ctx.save(); ctx.translate(0, dy)
        polyline(ctx, rect_pts(WX0, y0, WX1, y1), 1, c, 2.5, alpha=pb)
        for x in (WX0 + SHELL, WX1 - SHELL):
            polyline(ctx, [(x, y0 + 3), (x, y1 - 3)], 1, c, 1.5, alpha=0.8 * pb)
        ctx.restore()
    label(ctx, clamp((t - s4 - 2.0) / 0.8), c, (WX0, 740), (110, 520), "HOLLOW BLOCKS")

    # 5 vertical bar + core fill (bottom up)
    c = tl.col(5, t)
    pv = prog(t, s5, 0.7)
    if pv > 0:
        polyline(ctx, [(BAR_X + 7, FT0 - 110), (BAR_X + 7, FT0 - 110 - (FT0 - 110 - HIGH_GL - 25) * pv)], 1, c, 3.5)
    pc = prog(t, s5 + 0.8, 1.4)
    if pc > 0:
        ytop = FT0 - (FT0 - HIGH_GL) * pc
        clip_rect(ctx, WX0 + SHELL, ytop, WX1 - SHELL, FT0)
        ctx.set_source_rgba(*c, 0.14); ctx.rectangle(WX0 + SHELL, HIGH_GL, WX1 - WX0 - 2 * SHELL, FT0 - HIGH_GL); ctx.fill()
        draw_concrete(ctx, CONC_CORE, c, 0.75)
        ctx.restore()
        label(ctx, clamp((t - s5 - 1.6) / 0.8), c, (BAR_X, 660), (110, 445), "CORE FILL + BAR")

    # 6 membrane + protection board on the back face
    c = tl.col(6, t); p = prog(t, s6, 0.9)
    if p > 0:
        polyline(ctx, [(WX1 + 3, FT0), (WX1 + 3, HIGH_GL + 4)], p, ORANGE if t < tl.step_end(6) else c, 4)
        pb = prog(t, s6 + 0.8, 0.7)
        if pb > 0:
            polyline(ctx, rect_pts(WX1 + 7, FT0 - (FT0 - HIGH_GL - 4) * pb, WX1 + 15, FT0), 1, c, 1.8)
        label(ctx, clamp((t - s6 - 0.7) / 0.8), c, (WX1 + 4, 640), (940, 445), "MEMBRANE", anchor="r")

    # 7 ag pipe + gravel in geofabric
    c = tl.col(7, t)
    pp = prog(t, s7, 0.6)
    if pp > 0:
        x, y, r = PIPE
        ctx.set_source_rgba(*c, pp); ctx.set_line_width(3)
        ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
        ctx.set_dash([4, 5]); ctx.set_line_width(2)
        ctx.new_path(); ctx.arc(x, y, r - 5, 0, 2 * math.pi); ctx.stroke(); ctx.set_dash([])
        label(ctx, clamp((t - s7 - 0.5) / 0.8), c, (x + r, y), (940, 1150), "SLOTTED AG PIPE", anchor="r")
    pg = prog(t, s7 + 0.8, 1.2)
    if pg > 0:
        ytop = FT0 - (FT0 - GRAV_TOP) * pg
        clip_rect(ctx, WX1 + 15, ytop, GRAV_X1, FT0)
        draw_gravel(ctx, [g for g in GRAV if math.dist(g[:2], PIPE[:2]) > PIPE[2] + g[2] + 2], c)
        ctx.restore()
        polyline(ctx, [(WX1 + 17, FT0 - 2), (GRAV_X1, FT0 - 2), (GRAV_X1, GRAV_TOP), (WX1 + 17, GRAV_TOP)],
                 prog(t, s7 + 1.8, 0.7), c, 2, dash=[8, 6])
        label(ctx, clamp((t - s7 - 1.4) / 0.8), c, (GRAV_X1 - 10, 700), (940, 482), "DRAINAGE GRAVEL", anchor="r")

    # 8 compacted backfill in layers + low-side ground
    c = tl.col(8, t); p = prog(t, s8, 1.6)
    if p > 0:
        ytop = FT1 - (FT1 - HIGH_GL) * p
        ctx.save(); ctx.rectangle(400, ytop, 600, FT1 + 10 - ytop); ctx.clip()
        poly_hatch(ctx, BACKFILL, c, alpha=0.28, step=28)
        ctx.restore()
        for yy in range(FT1 - 45, HIGH_GL, -45):                    # compaction layers
            if yy < ytop: break
            # right end of each layer follows the batter
            xr = 635 + (850 - 635) * (1085 - yy) / (1085 - HIGH_GL)
            x0 = (GRAV_X1 if yy > GRAV_TOP else WX1 + 17)
            if yy > FT0: x0 = 620
            polyline(ctx, [(x0, yy), (xr, yy)], 1, c, 1.5, alpha=0.6, dash=[10, 8])
        polyline(ctx, [(WX1 + 15, HIGH_GL), (850, HIGH_GL)], prog(t, s8 + 1.4, 0.6), c, 3)
        polyline(ctx, [(255, LOW_GL), (WX0, LOW_GL)], prog(t, s8 + 1.4, 0.6), c, 3)
        label(ctx, clamp((t - s8 - 1.2) / 0.8), c, (760, 650), (940, 520), "COMPACTED BACKFILL", anchor="r")

    # result dims
    r0 = tl.res0
    pd = prog(t, r0, 0.6)
    if pd > 0:
        polyline(ctx, [(WX0 - 6, HIGH_GL), (186, HIGH_GL)], pd, BLUE, 1.5, dash=[6, 6])
        dim_v(ctx, 200, HIGH_GL, LOW_GL, "RETAINED HEIGHT", pd)


# ---------------------------------------------------------------- 3D model (mm): wall run with a stepped cutaway at the near end
def model3d():
    from engine.three_d import box, member3d
    P = []; o = 0
    L = 6000
    # low-side ground (towards viewer, +z) and in-situ ground under everything
    P.append(box(-400, L + 400, -900, -550, -2800, 1800, o, "ground")); P[-1].base = True; o += 1
    P.append(box(0, L, -550, -150, 100, 400, o, "concrete"))                       # footing toe
    for x in range(0, L, 400):                                                         # footing heel (sliced for clean sorting)
        P.append(box(x, x + 400, -550, -150, -1000, 100, o, "concrete"))
    o += 1
    ch = 200; nc = 9
    for k in range(nc):                                                                # block courses, stretcher bond
        xs = sorted(set([0, L] + list(range(200 if k % 2 else 400, L, 400))))
        for a, b in zip(xs, xs[1:]):
            P.append(box(a + 5, b - 5, -150 + k * ch + 5, -150 + (k + 1) * ch - 5, -100, 100, o, "concrete"))
        o += 1
    top = -150 + nc * ch
    for x in range(0, L, 400):                                                         # ag pipe (sliced for clean sorting)
        P.append(member3d((x, -60, -280), (x + 400, -60, -280), 120, 120, o, "steel"))
    o += 1
    # drainage gravel, sliced to line up with the block courses so it always sorts behind the wall
    for k in range(6):
        xs = sorted(set([0, L] + list(range(200 if k % 2 else 400, L, 400))))
        for a, b in zip(xs, xs[1:]):
            P.append(box(a, b, -150 + k * ch, -150 + (k + 1) * ch, -480, -110, o + k // 3, "eps"))
    o += 2
    for x in range(0, L - 1600, 600):                                                  # compacted backfill, stepped back at the far end
        P.append(box(x, x + 600, -150, top - 200, -2600, -480, o + x // 1800, "ground"))
    o += 3
    cfg = {"target": (3000, 500, -500), "yaw": -52, "pitch": 30, "dist": 14000, "scale": 1.8,
           "cy_hook": 1110, "cy_result": 800, "cy_cover": 990, "cover_scale": 0.88}
    return P, cfg
