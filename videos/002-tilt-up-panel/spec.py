"""002 Tilt-up concrete panel (commercial)."""
import math
from engine.blueprint import *

META = {
    "title": "TILT-UP PANEL",
    "subtitle": "COMMERCIAL  //  TYPICAL AU METHOD",
    "dwg": "002",
    "section_label": "ELEVATION  (NTS)",
    "hook": ["THESE WALLS", "ARE POURED", "LYING DOWN."],
    "hook_sub": "HOW A TILT-UP PANEL GOES UP",
    "cover": ["POURED FLAT.", "STOOD UP", "IN MINUTES."],
    "steps": [
        ("CASTING BED", "Footings and the floor slab go in first. The slab doubles as the casting bed."),
        ("BOND BREAKER", "Chemical bond breaker sprayed on the slab so the panel won't stick."),
        ("EDGE FORMS", "Edge forms set out to the panel shape, with blockouts for doors and windows."),
        ("REO & INSERTS", "Mesh tied in, plus cast-in inserts for lifting and bracing."),
        ("POUR & CURE", "Panel poured, finished and cured until it reaches lifting strength."),
        ("TILT UP", "Crane rigs to the lifting inserts and tilts the panel up off the slab."),
        ("STAND & BRACE", "Stood on shims at the footing, plumbed, then braced back to the slab."),
        ("GROUT & CONNECT", "Base grouted and the panel tied into the roof steel. Braces come out once the structure's up."),
    ],
    "result": "Big concrete walls, cast right there on site and stood up in a day.",
    "next": "NEXT: HOW BRICK VENEER GOES TOGETHER",
}

NARRATION = {
    "hook": "These concrete walls are poured lying down. Here's how a tilt-up panel goes up.",
    "steps": [
        "Footings and the floor slab go in first. The slab is the casting bed.",
        "Bond breaker gets sprayed on, so the panel won't stick.",
        "Edge forms are set out, with blockouts for the windows and doors.",
        "Mesh goes in, plus cast-in inserts for lifting and bracing.",
        "Then the panel's poured, finished, and left to gain strength.",
        "Crane hooks on, and tilts it up off the slab.",
        "It's stood on the footing, plumbed, and braced back to the slab.",
        "Base gets grouted, and it's tied into the roof steel. Braces come out once the structure's up.",
    ],
    "result": "Big concrete walls, cast right there on site, and stood up in a day.",
    "end": "Follow for more. Next up, brick veneer.",
}

CAPTION = """These walls are poured lying down 👇 How a tilt-up concrete panel goes up, step by step.

Common on warehouses, schools and shopping centres around Australia. Typical panels are 150 to 200 thick, cast on the floor slab, then craned up and propped until the roof structure ties them in.
Typical only. Your engineer's design and the lifting design govern.

#construction #tiltup #concrete #commercialconstruction #australianbuilding #civilengineering #crane #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry
GND = 1010
SLAB_X0, SLAB_X1, SLAB_TOP = 330, 940, 970
FOOT_X0, FOOT_X1, FOOT_BOT = 190, 300, 1100
T, L = 26, 520                         # panel thickness / length (px, NTS)
PIVOT0 = (900, SLAB_TOP)               # bottom edge of panel while lying (top edge points toward the footing)
PIVOT1 = (232, 1002)                   # bottom edge once stood on shims at the footing
SOLID = [(-L, 0)]                      # local x range of concrete (section cut clear of openings)
INSERTS = [-430, -300]                 # lifting inserts on the up face (local x)

CONC_SLAB = concrete_points(21, SLAB_X0, SLAB_TOP, SLAB_X1, GND, 220)
CONC_FOOT = concrete_points(22, FOOT_X0, GND - 30, FOOT_X1, FOOT_BOT, 90)
CONC_PANEL = concrete_points(23, -L, -T, 0, 0, 260,
                             lambda x, y: -T + 3 < y < -3 and any(a + 3 < x < b - 3 for a, b in SOLID))


def pose(t, tl):
    """Panel transform: (pivot x, pivot y, angle)."""
    s6, s7 = tl.s(6), tl.s(7)
    th = (math.pi / 2) * prog(t, s6 + 0.3, 2.0)
    k = prog(t, s7, 1.4)
    x = PIVOT0[0] + (PIVOT1[0] - PIVOT0[0]) * k
    y = PIVOT0[1] + (PIVOT1[1] - PIVOT0[1]) * k - 30 * math.sin(math.pi * k)
    return x, y, th


def to_global(t, tl, lx, ly):
    px, py, th = pose(t, tl)
    return px + lx * math.cos(th) - ly * math.sin(th), py + lx * math.sin(th) + ly * math.cos(th)


def faded(ctx, alpha, fn):
    if alpha <= 0: return
    ctx.push_group(); fn(); ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    lying_labels = 1 - clamp((t - s6) / 0.4)          # labels pointing at the flat panel fade as it lifts

    # 1 footing + slab
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 100, GND, FOOT_X0, 1160, c, reveal=p)
        earth_hatch(ctx, FOOT_X1, GND, 940, 1160, c, reveal=p)
        earth_hatch(ctx, FOOT_X0, FOOT_BOT, FOOT_X1, 1160, c, reveal=p)
        polyline(ctx, [(100, GND), (FOOT_X0, GND)], p, c, 3)
        polyline(ctx, [(FOOT_X1, GND), (SLAB_X0, GND)], p, c, 3)
        polyline(ctx, rect_pts(FOOT_X0, GND - 10, FOOT_X1, FOOT_BOT), p, c, 3)
        polyline(ctx, rect_pts(SLAB_X0, SLAB_TOP, SLAB_X1, GND), p, c, 3)
        if p > 0.5:
            a = (p - 0.5) * 2
            ctx.set_source_rgba(*c, 0.12 * a); ctx.rectangle(SLAB_X0, SLAB_TOP, SLAB_X1 - SLAB_X0, GND - SLAB_TOP); ctx.fill()
            ctx.rectangle(FOOT_X0, GND - 10, FOOT_X1 - FOOT_X0, FOOT_BOT - GND + 10); ctx.fill()
            draw_concrete(ctx, CONC_SLAB + CONC_FOOT, c, 0.7 * a)
        leader(ctx, clamp((t - s1 - 0.9) / 0.8), c, (245, 1060), (110, 1192), "FOOTING")
        leader(ctx, clamp((t - s1 - 1.2) / 0.8), c, (800, 990), (930, 1150), "FLOOR SLAB", anchor="r")

    # 2 bond breaker spray
    c = tl.col(2, t); p = prog(t, s2, 1.4)
    if p > 0:
        polyline(ctx, [(370, SLAB_TOP - 3), (370 + 545 * p, SLAB_TOP - 3)], 1, c, 2.5, dash=[8, 6])
        if p < 1:
            nx = 370 + 545 * p
            polyline(ctx, [(nx, 900), (nx + 40, 860)], 1, c, 4)                      # spray wand
            for i in range(9):
                fx = nx - 18 + (i % 5) * 9; fy = 905 + ((t * 300 + i * 17) % 60)
                dot(ctx, fx, fy, 2, c, 0.8)
        leader(ctx, clamp((t - s2 - 1.0) / 0.8), c, (600, SLAB_TOP - 3), (560, 1192), "BOND BREAKER")

    # panel, drawn in its own coordinates (lying -> tilting -> standing)
    px, py, th = pose(t, tl)
    ctx.save(); ctx.translate(px, py); ctx.rotate(th)

    # 3 edge forms + blockout (removed before the lift)
    c = tl.col(3, t); p = prog(t, s3, 0.8)
    form_a = p * (1 - clamp((t - s6) / 0.3))
    if form_a > 0:
        for x0 in (-L - 8, 0):
            polyline(ctx, rect_pts(x0, -T - 8, x0 + 8, 0), 1, c, 2.5, alpha=form_a)
            polyline(ctx, [(x0 + (0 if x0 < 0 else 8), -T + 2), (x0 + (-14 if x0 < 0 else 22), 0)], 1, c, 2, alpha=form_a)

    # 4 reo + inserts
    c = tl.col(4, t); p = prog(t, s4, 0.9)
    if p > 0:
        for a, b in SOLID:
            for yy in (-T + 8, -8):
                polyline(ctx, [(a + 6, yy), (a + 6 + (b - a - 12) * p, yy)], 1, c, 1.8, alpha=0.9)
        pi = prog(t, s4 + 0.7, 0.5)
        for lx in INSERTS:
            dot(ctx, lx, -T, 6, c, pi)
            polyline(ctx, [(lx, -T), (lx, -10)], pi, c, 3)

    # 5 pour (left to right as placed)
    c = tl.col(5, t); p = prog(t, s5, 1.6)
    if p > 0:
        ctx.save(); ctx.rectangle(-L, -T - 10, L * p, T + 12); ctx.clip()
        for a, b in SOLID:
            ctx.set_source_rgba(*c, 0.16); ctx.rectangle(a, -T, b - a, T); ctx.fill()
        draw_concrete(ctx, CONC_PANEL, c, 0.8)
        ctx.restore()
        for a, b in SOLID:
            polyline(ctx, rect_pts(a, -T, b, 0), p, c, 3)
    ctx.restore()

    # labels for the flat panel (fade out as it lifts)
    def flat_labels():
        c3, c4 = tl.col(3, t), tl.col(4, t)
        leader(ctx, clamp((t - s3 - 0.8) / 0.8), c3, (PIVOT0[0] - L - 4, SLAB_TOP - 20), (110, 445), "EDGE FORM")
        leader(ctx, clamp((t - s4 - 1.2) / 0.8), c4, (PIVOT0[0] - 430, SLAB_TOP - T), (560, 445), "LIFT INSERT", anchor="r")
        leader(ctx, clamp((t - s4 - 1.5) / 0.8), c4, (PIVOT0[0] - 120, SLAB_TOP - 8), (940, 445), "MESH", anchor="r")
    faded(ctx, lying_labels, flat_labels)

    # 6 crane rigging (drops in, lifts, released after bracing)
    c = tl.col(6, t)
    drop = prog(t, s6, 0.4)
    rel = 1 - clamp((t - s7 - 2.2) / 0.4)
    if drop > 0 and rel > 0:
        pts = [to_global(t, tl, lx, -T) for lx in INSERTS]
        hx = sum(p[0] for p in pts) / 2 + 30
        hy = min(min(p[1] for p in pts) - 120, 430)
        hy_draw = 400 + (hy - 400) * drop
        a = rel
        for (ix, iy) in pts:
            polyline(ctx, [(hx, hy_draw), (hx + (ix - hx) * drop, hy_draw + (iy - hy_draw) * drop)], 1, c, 2.5, alpha=a)
        polyline(ctx, [(hx, 380), (hx, hy_draw)], 1, c, 3, alpha=a)
        ctx.set_source_rgba(*c, a); ctx.set_line_width(4)
        ctx.arc(hx, hy_draw - 12, 10, 0.3, math.pi * 1.6); ctx.stroke()
        text(ctx, "CRANE", hx + 18, 420, 22, c, alpha=a * clamp((t - s6 - 0.4) / 0.3), bold=True)

    # 7 shims + brace
    c = tl.col(7, t)
    ps = prog(t, s7 + 1.2, 0.3)
    if ps > 0:
        for x in (236, 250):
            polyline(ctx, rect_pts(x - 4, 1002, x + 4, GND), ps, c, 2)
    pb = prog(t, s7 + 1.4, 0.8)
    brace_out = 1 - clamp((t - s8 - 2.0) / 0.6)
    if pb > 0 and brace_out > 0:
        polyline(ctx, [(258, 700), (600, SLAB_TOP - 6)], pb, c, 4, alpha=brace_out)
        polyline(ctx, [(258, 716), (590, SLAB_TOP - 6)], pb, c, 2, alpha=brace_out)
        polyline(ctx, rect_pts(585, SLAB_TOP - 8, 620, SLAB_TOP), pb, c, 2.5, alpha=brace_out)
        dot(ctx, 258, 700, 6, c, pb * brace_out)
        leader(ctx, clamp((t - s7 - 2.0) / 0.8) * brace_out, c, (430, 835), (940, 640), "TEMP BRACE", anchor="r")

    # 8 grout + roof steel
    c = tl.col(8, t)
    pg = prog(t, s8, 0.5)
    if pg > 0:
        ctx.set_source_rgba(*c, 0.5 * pg); ctx.rectangle(226, 1002, 38, 8); ctx.fill()
        leader(ctx, clamp((t - s8 - 0.3) / 0.8), c, (226, 1006), (110, 1150), "GROUT")
    pr = prog(t, s8 + 0.8, 0.8)
    if pr > 0:
        y0 = 505
        polyline(ctx, rect_pts(258, y0, 258 + 400 * pr, y0 + 22), 1, c, 2.5)
        polyline(ctx, [(258, y0 + 6), (258 + 400 * pr, y0 + 6)], 1, c, 1.5)
        polyline(ctx, [(258, y0 + 16), (258 + 400 * pr, y0 + 16)], 1, c, 1.5)
        polyline(ctx, rect_pts(258, y0 - 8, 274, y0 + 34), pr, c, 2)                # cleat
        leader(ctx, clamp((t - s8 - 1.4) / 0.8), c, (520, y0 + 11), (560, 445), "ROOF STEEL")

    # result dims
    r0 = tl.res0
    dim_v(ctx, 175, 482, 1002, "6-12 m TYP", prog(t, r0, 0.6))
    dim_h(ctx, 470, 232, 258, "150-200", prog(t, r0 + 0.4, 0.6))
