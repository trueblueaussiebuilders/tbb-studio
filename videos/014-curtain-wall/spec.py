"""014 Unitised curtain wall (commercial)."""
import math
from engine.blueprint import *

META = {
    "category": "commercial",
    "title": "CURTAIN WALL",
    "subtitle": "COMMERCIAL  //  TYPICAL AU METHOD",
    "dwg": "014",
    "drawing": "CURTAIN WALL",
    "section_label": "SECTION AT SLAB EDGE  (NTS)",
    "hook": ["THAT GLASS WALL", "HOLDS NOTHING UP.", "IT HANGS ON HOOKS."],
    "hook_sub": "HOW A CURTAIN WALL GOES UP",
    "cover": ["GLASS WALLS", "THAT HANG", "ON HOOKS."],
    "xray": {"after_step": 5, "upto": 19, "hot": list(range(12, 20))},   # row 2 units being hooked on
    "steps": [
        ("SET OUT", "Surveyors mark a line off every slab edge. The wall is set to this line, not to the concrete."),
        ("CAST-IN CHANNELS", "Steel anchor channels are cast into the slab edges when each floor is poured."),
        ("BRACKETS", "Brackets bolt into the channels. They adjust in, out, up and down to hit the line."),
        ("FACTORY UNITS", "Each unit is an aluminium frame with the glass already in. Built and sealed in a factory."),
        ("LIFT & HOOK ON", "A crane lifts each unit up the face. It hooks onto the bracket at the slab edge."),
        ("STACK JOINTS", "Each unit slots into the ones below and beside it. The joints let the building move."),
        ("FIRE & SMOKE SEAL", "The gap at each slab edge is packed with fire-rated insulation and sealed on top."),
        ("WATER TEST", "Joints are sprayed with water and checked for leaks. Then the inside is finished."),
    ],
    "result": "A glass wall that hangs off the floors. It carries its own weight and the wind, not the building.",
}

NARRATION = {
    "hook": "That glass wall isn't holding the building up. It hangs on hooks. Here's how.",
    "steps": [
        "First, surveyors mark a line off every slab edge. The wall is set to that line, not to the concrete.",
        "Steel anchor channels are cast into the edge of each slab, when the floor is poured.",
        "Brackets bolt into the channels. They adjust in, out, up and down, to hit the line.",
        "The wall comes in units. Each one is an aluminium frame with the glass already in, built in a factory.",
        "A crane lifts each unit up the face of the building. Installers on the floor hook it onto the bracket.",
        "Each unit slots into the ones below and beside it. These joints let the building move without cracking the glass.",
        "The gap at each slab edge is packed with fire-rated insulation, then sealed. It stops fire and smoke spreading between floors.",
        "Finally, the joints are sprayed with water and checked for leaks. Then the inside is finished.",
    ],
    "result": "The glass wall hangs off the edge of each floor. It carries its own weight and the wind. Not the building.",
    "end": "Follow for more.",
}

CAPTION = """That glass wall isn't holding the building up 👇 How a unitised curtain wall goes on an office building.

Typical: the slab edges are surveyed and a set-out line is established, cast-in anchor channels go into the slab edges during each pour, and adjustable brackets are bolted to the channels. The wall is made of factory-built units (aluminium frames with the double-glazed units already installed and sealed), craned up the face and hooked onto the brackets. Each unit interlocks with its neighbours at the stack and mullion joints, which take up floor deflection, thermal movement and building sway. The gap between the slab edge and the facade gets a tested perimeter fire and smoke seal. Joints are water tested on site before the internal linings go in.
A curtain wall carries its own weight and the wind back to the floors. It doesn't hold the building up.
Typical only. Your engineer's and facade designer's design governs.

#curtainwall #facade #glazing #commercialconstruction #highrise #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
SLABS = [(560, 632), (960, 1032)]    # (top, soffit) of the upper and lower slab
SL0, SE = 90, 560                    # slab drawn from the break line to the slab edge
FI, GI, GO, FO = 640, 692, 714, 732  # unit frame inner face, glass inner/outer pane, frame outer face
JOINT = [t - 25 for t, _ in SLABS]   # stack joints just above each slab: 535, 935
CH0, CH1 = 490, 526                  # cast-in channel
STAGE = 200                          # where the unit sits "in the factory" (offset to the right)
CLIP = (90, 400, 990, 1212)

SLAB_CONC = [concrete_points(141 + i, SL0 + 20, t, SE, b, 150,
                             lambda x, y, t=t, b=b: t + 4 < y < b - 4 and not (CH0 - 6 < x < CH1 + 6 and y < t + 40))
             for i, (t, b) in enumerate(SLABS)]


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


def unit(ctx, ytop, ybot, c, a=1.0, dx=0.0, dy=0.0, hook=True):
    """One curtain wall unit in section: head + sill transoms, double glazing, mullion beyond, hook at the head."""
    if a <= 0: return
    ctx.push_group()
    y0, y1 = ytop + dy, ybot + dy
    X = lambda x: x + dx
    fill_poly(ctx, rect_pts(X(FI), y0, X(FO), y1)[:4], BG, 0.85)
    polyline(ctx, [(X(FI), y0 + 28), (X(FI), y1 - 28)], 1, c, 1.6, alpha=0.4)          # mullion beyond
    polyline(ctx, [(X(FO), y0 + 28), (X(FO), y1 - 28)], 1, c, 1.6, alpha=0.4)
    polyline(ctx, rect_pts(X(FI), y0, X(FO), y0 + 28), 1, c, 2.5)                       # head transom
    polyline(ctx, rect_pts(X(FI), y1 - 28, X(FO), y1), 1, c, 2.5)                       # sill transom
    for gx in (GI, GO):                                                                 # double glazing
        polyline(ctx, [(X(gx), y0 + 28), (X(gx), y1 - 28)], 1, c, 2.5)
    for yy in (y0 + 30, y1 - 42):                                                       # spacers
        polyline(ctx, rect_pts(X(GI) + 3, yy, X(GO) - 3, yy + 12), 1, c, 1.4, alpha=0.8)
    fill_poly(ctx, rect_pts(X(GI) + 2, y0 + 44, X(GO) - 2, y1 - 44)[:4], BLUE, 0.10)    # glass tint
    if hook:                                                                            # hook bracket on the head
        polyline(ctx, [(X(FI), y0 - 9), (X(FI - 28), y0 - 9), (X(FI - 28), y0 + 9)], 1, c, 3)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def bracket(ctx, top, c, p):
    """Slab bracket: plate on the slab, bolted into the channel, with an upstand the unit hooks over."""
    if p <= 0: return
    bx = (CH0 + CH1) / 2
    polyline(ctx, rect_pts(CH0 - 12, top - 10, FI - 12, top), p, c, 2.5)
    polyline(ctx, rect_pts(FI - 18, top - 26, FI - 12, top - 10), clamp(p * 2 - 1), c, 2.5)
    polyline(ctx, [(bx, top - 16), (bx, top + 11)], clamp(p * 2 - 1), c, 3)              # T-bolt into the channel
    polyline(ctx, [(bx - 10, top + 11), (bx + 10, top + 11)], clamp(p * 2 - 1), c, 3)


def arrow(ctx, x0, y0, x1, y1, col, p=1.0, a=1.0, head=12):
    if p <= 0: return
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    polyline(ctx, [(x0, y0), (xe, ye)], 1, col, 3, alpha=a)
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    polyline(ctx, [(xe - ux * head - uy * head * 0.8, ye - uy * head + ux * head * 0.8), (xe, ye),
                   (xe - ux * head + uy * head * 0.8, ye - uy * head - ux * head * 0.8)], 1, col, 3, alpha=a)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    # slabs (context, from the start of step 1): break line on the left, slab edge on the right
    c = tl.col(1, t); p = prog(t, s1, 0.8)
    if p > 0:
        for i, (top, bot) in enumerate(SLABS):
            polyline(ctx, [(SL0 + 20, top), (SE, top), (SE, bot), (SL0 + 20, bot)], p, c, 3)
            mid = (top + bot) / 2
            polyline(ctx, [(SL0 + 20, top - 8), (SL0 + 20, mid - 10), (SL0 + 8, mid - 4), (SL0 + 32, mid + 4),
                           (SL0 + 20, mid + 10), (SL0 + 20, bot + 8)], p, c, 1.6, alpha=0.7)
            draw_concrete(ctx, SLAB_CONC[i], c, 0.5 * p)

    # 1 set-out line
    po = prog(t, s1 + 0.6, 1.0)
    if po > 0:
        polyline(ctx, [(FI, 410), (FI, 1205)], po, BLUE, 2, alpha=0.9 * gone(t, s5 + 1.0, 1.0), dash=[14, 10])
    label(ctx, clamp((t - s1 - 0.8) / 0.8), c, (SE, 600), (110, 700), "SLAB EDGE", a=gone(t, s3))
    label(ctx, clamp((t - s1 - 1.5) / 0.8), BLUE, (FI, 470), (940, 482), "SET-OUT LINE", anchor="r", a=gone(t, s3))

    # 2 cast-in anchor channels
    c = tl.col(2, t)
    for i, (top, _) in enumerate(SLABS):
        pc = prog(t, s2 + 0.2 + i * 0.4, 0.6)
        if pc <= 0: continue
        fill_poly(ctx, rect_pts(CH0, top, CH1, top + 18)[:4], BG, pc)
        polyline(ctx, [(CH0 + 8, top), (CH0, top), (CH0, top + 18), (CH1, top + 18), (CH1, top), (CH1 - 8, top)], pc, c, 2.5)
        for ax in (CH0 + 8, CH1 - 8):                                             # anchors into the concrete
            polyline(ctx, [(ax, top + 18), (ax, top + 44)], pc, c, 2.5)
            if pc >= 1: polyline(ctx, [(ax - 7, top + 44), (ax + 7, top + 44)], 1, c, 3)
    label(ctx, clamp((t - s2 - 0.9) / 0.8), c, (CH0, SLABS[1][0] + 9), (110, 1150), "CAST-IN CHANNEL", a=gone(t, s4))

    # 3 brackets, with an "adjusts" wiggle
    c = tl.col(3, t)
    for i, (top, _) in enumerate(SLABS):
        bracket(ctx, top, c, prog(t, s3 + i * 0.4, 0.8))
    padj = clamp((t - s3 - 1.4) / 0.4) * gone(t, s4)
    if padj > 0:
        for top, _ in SLABS:
            arrow(ctx, FI - 70, top - 46, FI + 10, top - 46, ORANGE, a=padj, head=10)
            arrow(ctx, FI + 10, top - 46, FI - 70, top - 46, ORANGE, a=padj, head=10)
            arrow(ctx, SE, top - 80, SE, top - 22, ORANGE, a=padj, head=10)
            arrow(ctx, SE, top - 22, SE, top - 80, ORANGE, a=padj, head=10)
    label(ctx, clamp((t - s3 - 0.6) / 0.8), c, (CH0 - 10, SLABS[0][0] - 10), (110, 482), "BRACKET", a=gone(t, s5))
    label(ctx, clamp((t - s3 - 1.4) / 0.8), ORANGE, (SE, SLABS[1][0] - 80), (110, 860), "ADJUSTS 3 WAYS",
          a=gone(t, s4 + 0.3))

    # units (clipped to the drawing band so the ones above/below run off the edge cleanly)
    clip_rect(ctx, *CLIP)
    # the unit below is already up (the wall goes up floor by floor)
    unit(ctx, JOINT[1], JOINT[1] + 400, mix(WHITE, BLUE, 0.35), a=0.75 * prog(t, s5, 0.5))
    # 4 the main unit "in the factory" (staged to the right), 5 craned in and hooked on
    c = tl.col(4, t) if t < s5 else tl.col(5, t)
    pu = prog(t, s4, 0.6)
    m = prog(t, s5 + 0.2, 1.6)
    drop = 1 - prog(t, s5 + 1.8, 0.35)
    dx = STAGE * (1 - m); dy = -60 * math.sin(math.pi * m) - 16 * drop * (m >= 1)
    unit(ctx, JOINT[0], JOINT[1], c, a=pu, dx=dx, dy=dy)
    rope = prog(t, s5, 0.3) * gone(t, s5 + 2.4, 0.4)
    if rope > 0:
        hx, hy = (FI + FO) / 2 + dx, JOINT[0] + dy - 30
        polyline(ctx, [(hx, 400), (hx, hy)], 1, WHITE, 2, alpha=rope)
        polyline(ctx, [(hx, hy), (hx, hy + 14), (hx - 10, hy + 22), (hx - 18, hy + 14)], 1, WHITE, 3, alpha=rope)
        polyline(ctx, [(hx - 20, hy + 30), (hx, hy + 14), (hx + 20, hy + 30)], 1, WHITE, 1.6, alpha=0.6 * rope)
    # 6 the unit above comes down and its sill slots over the head of this one
    c6 = tl.col(6, t)
    pdn = prog(t, s6 + 0.1, 1.3)
    if pdn > 0:
        unit(ctx, JOINT[0] - 400, JOINT[0], c6, dy=-170 * (1 - pdn), a=clamp(pdn * 3))
    ctx.restore()
    label(ctx, clamp((t - s4 - 0.5) / 0.8), c, (FI + STAGE + 20, JOINT[0] - 2), (940, 482), "FACTORY-MADE UNIT",
          anchor="r", a=gone(t, s5))
    label(ctx, clamp((t - s4 - 1.3) / 0.8), c, (GO + STAGE, 820), (940, 1150), "GLASS ALREADY IN", anchor="r",
          a=gone(t, s5))
    label(ctx, clamp((t - s5 - 0.3) / 0.8), WHITE, ((FI + FO) / 2 + dx, 420), (940, 445), "CRANE", anchor="r",
          a=gone(t, s5 + 2.4, 0.4))
    label(ctx, clamp((t - s5 - 2.0) / 0.8), tl.col(5, t), (FI - 28, JOINT[0] - 4), (110, 445), "HOOKED ON",
          a=gone(t, s7))

    # stack joint highlight + movement arrows
    pj = clamp((t - s6 - 1.4) / 0.4) * gone(t, s7 + 0.3)
    if pj > 0:
        for jy in JOINT:
            ctx.set_source_rgba(*ORANGE, 0.9 * pj); ctx.set_line_width(3)
            ctx.rectangle(FI - 6, jy - 12, FO - FI + 12, 24); ctx.stroke()
        k = 0.5 + 0.5 * math.sin((t - s6) * 6)
        arrow(ctx, FO + 26, JOINT[0] - 10 - 10 * k, FO + 26, JOINT[0] - 55, ORANGE, a=pj, head=10)
        arrow(ctx, FO + 26, JOINT[0] + 10 + 10 * k, FO + 26, JOINT[0] + 55, ORANGE, a=pj, head=10)
    label(ctx, clamp((t - s6 - 1.4) / 0.8), ORANGE, (FO + 6, JOINT[0] - 12), (940, 445), "STACK JOINT", anchor="r",
          a=gone(t, s8))
    label(ctx, clamp((t - s6 - 2.0) / 0.8), ORANGE, (FO + 26, JOINT[0] + 55), (940, 640), "LETS IT MOVE", anchor="r",
          a=gone(t, s7 + 0.3))

    # 7 perimeter fire + smoke seal in the gap at each slab edge
    c = tl.col(7, t)
    for i, (top, bot) in enumerate(SLABS):
        pf = prog(t, s7 + i * 0.4, 0.8)
        if pf <= 0: continue
        clip_rect(ctx, SE, top, SE + (FI - SE) * pf, bot)
        fill_poly(ctx, rect_pts(SE, top, FI, bot)[:4], mix(BG, c, 0.12), 1)
        ctx.set_source_rgba(*c, 0.8); ctx.set_line_width(1.6)
        for row in range(4):                                                  # insulation squiggle
            y = top + 10 + row * 15
            ctx.move_to(SE, y)
            for x in range(SE, FI + 1, 4):
                ctx.line_to(x, y + 5 * math.sin((x - SE) / 6.0))
            ctx.stroke()
        ctx.restore()
        ps = prog(t, s7 + 1.0 + i * 0.4, 0.6)
        polyline(ctx, [(SE, top - 2), (FI, top - 2)], ps, ORANGE, 5)
    label(ctx, clamp((t - s7 - 1.0) / 0.8), ORANGE, (600, SLABS[0][0] - 2), (110, 520), "SMOKE SEAL", a=gone(t, r0))
    label(ctx, clamp((t - s7 - 0.4) / 0.8), c, (600, SLABS[1][0] + 36), (110, 1150), "FIRE-RATED INSULATION",
          a=gone(t, r0))

    # 8 water test: spray at the joints, then a stamp
    pw = prog(t, s8, 0.4) * gone(t, s8 + 2.6, 0.4)
    if pw > 0:
        for j, jy in enumerate(JOINT):
            nx, ny = 880, jy - 60
            polyline(ctx, rect_pts(nx, ny - 8, nx + 50, ny + 8), 1, WHITE, 2.5, alpha=pw)      # nozzle
            for k in range(7):
                u = ((t - s8) * 1.6 + k / 7) % 1
                x = nx - (nx - FO - 10) * u; y = ny + (jy - ny) * u + 14 * math.sin(k * 2.1)
                dot(ctx, x, y, 4, BLUE, pw * (1 - u * 0.5))
    label(ctx, clamp((t - s8 - 0.3) / 0.8), BLUE, (880, JOINT[0] - 60), (940, 445), "WATER TEST", anchor="r",
          a=gone(t, r0))
    sa = gone(t, r0, 0.5)
    if sa > 0 and t > s8 + 1.8:
        ctx.push_group()
        stamp(ctx, "NO LEAKS", 330, 800, clamp((t - s8 - 1.8) / 0.35), BLUE)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(sa)

    # result: own weight down into the bracket, wind onto the glass, floor to floor
    pr = prog(t, r0, 0.6)
    if pr > 0:
        arrow(ctx, FI - 28, JOINT[0] - 110, FI - 28, JOINT[0] - 22, BLUE, p=pr)
        text(ctx, "OWN WEIGHT", FI - 44, JOINT[0] - 70, 24, BLUE, alpha=clamp(pr * 2 - 1), bold=True, anchor="r")
    pw2 = prog(t, r0 + 0.6, 0.6)
    for k, y in enumerate((720, 790, 860)):
        arrow(ctx, 930, y, FO + 14, y, BLUE, p=clamp(pw2 * 1.4 - k * 0.2))
    if pw2 > 0:
        text(ctx, "WIND", 930, 690, 26, BLUE, alpha=clamp(pw2 * 2 - 1), bold=True, anchor="r", spacing=4)
    dim_v(ctx, 300, SLABS[0][0], SLABS[1][0], "FLOOR TO FLOOR", prog(t, r0 + 1.2, 0.6))


# ---------------------------------------------------------------- 3D model (mm): office floors with the wall going up
def model3d():
    from engine.three_d import box
    P = []; o = 0
    UW, FH, NU, NL = 1500, 3600, 8, 4                  # unit width, floor to floor, units per row, floors
    LX, LZ = UW * NU, 9000                              # building plan; facade on the +Z face (towards the camera)
    ZF0, ZF1 = LZ + 120, LZ + 270                       # unit frame depth, just off the slab edge
    P.append(box(-2500, LX + 2500, -300, 0, -2500, LZ + 3500, o, "ground")); P[-1].base = True; o += 1
    for x in (900, LX / 2, LX - 900):                   # columns set back from the edges
        for z in (1200, LZ - 1500):
            P.append(box(x - 250, x + 250, 0, NL * FH, z - 250, z + 250, o, "concrete"))
    o += 1
    for k in range(1, NL + 1):                          # suspended slabs
        P.append(box(0, LX, k * FH - 250, k * FH, 0, LZ, o, "concrete"))
    o += 1
    for k in range(1, NL + 1):                          # slab edge brackets, one per mullion
        for i in range(NU + 1):
            x = min(max(i * UW, 120), LX - 120)
            P.append(box(x - 110, x + 110, k * FH, k * FH + 120, LZ - 250, ZF0, o, "steel"))
    o += 1
    rows = [NU, NU, 5]                                  # units hung so far, floor by floor
    for r, n in enumerate(rows):
        y0, y1 = r * FH + 300, (r + 1) * FH + 300
        for i in range(n):
            x0, x1 = i * UW + 8, (i + 1) * UW - 8
            P.append(box(x0, x0 + 90, y0, y1, ZF0, ZF1, o, "steel"))                    # mullions
            P.append(box(x1 - 90, x1, y0, y1, ZF0, ZF1, o, "steel"))
            P.append(box(x0 + 90, x1 - 90, y1 - 120, y1, ZF0, ZF1, o, "steel"))       # head + sill transoms
            P.append(box(x0 + 90, x1 - 90, y0, y0 + 120, ZF0, ZF1, o, "steel"))
            P.append(box(x0 + 90, x1 - 90, y0 + 120, y1 - 120, ZF0 + 50, ZF0 + 90, o, "glass"))
            o += 1
    cfg = {"target": (LX / 2, NL * FH / 2, LZ / 2), "yaw": -25, "pitch": 12, "dist": 46000, "scale": 1.8,
           "cy_hook": 1080, "cy_result": 820, "cy_cover": 975, "cover_scale": 0.92}
    return P, cfg
