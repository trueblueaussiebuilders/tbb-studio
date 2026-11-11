"""001 Waffle pod slab (residential)."""
import math
from engine.blueprint import *

META = {
    "title": "WAFFLE POD SLAB",
    "subtitle": "RESIDENTIAL  //  TYPICAL AU DETAIL",
    "dwg": "001",
    "hook": ["THERE'S POLYSTYRENE", "UNDER A LOT OF", "NEW HOUSES."],
    "hook_sub": "HERE'S HOW THE SLAB GOES IN",
    "steps": [
        ("SITE SCRAPE & LEVEL", "Topsoil stripped and the building pad cut and levelled to design level."),
        ("COMPACTED PAD", "Sand or crushed rock bed placed, compacted and screeded flat."),
        ("FORMWORK & PLUMBING", "Edge beam trenches dug, perimeter formwork pegged, drainage laid under the slab."),
        ("VAPOUR BARRIER", "0.2 mm polyethylene membrane laid over the pad, lapped and taped."),
        ("WAFFLE PODS", "EPS pods set out in a grid on spacers, leaving ribs between them."),
        ("REINFORCEMENT", "Bars in the ribs, trench mesh in the edge beams, fabric mesh on chairs over the pods."),
        ("INSPECTION", "Steel, cover and setout checked before any concrete arrives."),
        ("POUR & FINISH", "Concrete placed, vibrated, screeded, finished and cured."),
    ],
    "result": "A stiff ribbed raft that uses less concrete and digging than a conventional slab.",
    "next": "NEXT: HOW A TILT-UP PANEL GOES UP",
}

NARRATION = {
    "hook": "There's polystyrene under a lot of new Aussie houses. Here's how it goes in.",
    "steps": [
        "Site's scraped, and the pad's cut level.",
        "Sand or crushed rock goes down, compacted flat.",
        "Edge beams dug, formwork pegged, drainage run under the slab.",
        "Plastic vapour barrier over the lot, lapped and taped.",
        "Then the pods. Polystyrene blocks in a grid, with gaps for the ribs.",
        "Steel goes in. Bars in the ribs, trench mesh in the edges, mesh over the top.",
        "Steel gets inspected before any concrete turns up.",
        "Then it's poured, vibrated, screeded and finished.",
    ],
    "result": "The result is a stiff, ribbed raft, with less concrete and less digging than a conventional slab.",
    "end": "Follow for more. Next up, tilt-up panels.",
}

CAPTION = """There's polystyrene under a lot of new Aussie houses. This is how a waffle pod slab goes in 👇

Typical: 1090 sq EPS pods, 110 rib, 85 topping, 300 wide edge beams.
Typical only. Your engineer's design governs.

#construction #australianbuilding #slab #concrete #housebuild #building #civilengineering #truebluebuilds"""

# ---------------------------------------------------------------- geometry (px)
# horizontal ~0.28 px/mm, vertical 1 px/mm (section NTS)
X0, XB, P1L, P1R, P2L, P2R, XR = 150, 234, 236, 539, 570, 875, 906
XBREAK = 915
Y_TOP, Y_POD, Y_PAD, Y_GND, Y_BEAM, Y_HATCH = 560, 645, 870, 920, 1020, 1100

PAD_DOTS = gravel(7, 110, Y_PAD + 6, 930, Y_GND - 6, 260)

def _in_concrete(x, y):
    if Y_TOP + 4 < y < Y_POD - 4 and X0 + 4 < x < XBREAK: return True
    if X0 + 4 < x < XB - 4 and Y_TOP < y < Y_BEAM - 4: return True
    for a, b in ((P1R, P2L), (P2R, XR)):
        if a + 4 < x < b - 4 and Y_POD - 2 < y < Y_PAD - 4: return True
    return False
CONC = concrete_points(8, X0, Y_TOP, XBREAK, Y_BEAM, 900, _in_concrete)

def _concrete_path(ctx):
    ctx.new_path()
    ctx.rectangle(X0, Y_TOP, XBREAK - X0, Y_POD - Y_TOP)
    ctx.rectangle(X0, Y_POD, XB - X0, Y_BEAM - Y_POD)
    ctx.rectangle(P1R, Y_POD, P2L - P1R, Y_PAD - Y_POD)
    ctx.rectangle(P2R, Y_POD, XR - P2R, Y_PAD - Y_POD)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 ground
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 100, Y_GND, 940, Y_HATCH, c, reveal=p)
        polyline(ctx, [(100, Y_GND), (940, Y_GND)], p, c, 3)
        a = 1 - clamp((t - s1 - 1.6) / 0.6)
        polyline(ctx, [(100, 780), (380, 760), (650, 810), (940, 790)], prog(t, s1 + 0.3, 0.8), c, 2.5, a * 0.8, dash=[14, 10])
        text(ctx, "EXISTING SURFACE", 660, 760, 22, c, alpha=a * clamp((t - s1 - 0.8) / 0.3), bold=True)
        leader(ctx, clamp((t - s1 - 1.0) / 0.8), c, (520, Y_GND + 50), (600, 1192), "NATURAL GROUND")

    # 2 pad
    c = tl.col(2, t); p = prog(t, s2, 0.8)
    if p > 0:
        clip_rect(ctx, 100, Y_PAD - 2, 100 + 840 * p, Y_GND); draw_gravel(ctx, PAD_DOTS, c); ctx.restore()
        polyline(ctx, [(100, Y_PAD), (940, Y_PAD)], p, c, 3)
        leader(ctx, clamp((t - s2 - 0.7) / 0.8), c, (780, Y_PAD + 25), (760, 1147), "COMPACTED PAD")

    # 3 trench, formwork, drainage
    c = tl.col(3, t); p = prog(t, s3, 0.6)
    if p > 0:
        ctx.set_source_rgba(*BG, p); ctx.rectangle(X0 + 1, Y_PAD - 1, XB - X0 - 2, Y_BEAM - Y_PAD + 1); ctx.fill()
        polyline(ctx, [(X0, Y_PAD), (X0, Y_BEAM), (XB, Y_BEAM), (XB, Y_PAD)], p, c, 3)
        fp = prog(t, s3 + 0.5, 0.6)
        polyline(ctx, rect_pts(X0 - 22, Y_TOP - 20, X0, Y_GND + 10), fp, c, 2.5)
        polyline(ctx, [(X0 - 34, Y_TOP + 120), (X0 - 34, Y_GND + 90), (X0 - 28, Y_GND + 110), (X0 - 22, Y_GND + 90), (X0 - 22, Y_TOP + 120)], fp, c, 2)
        pp = prog(t, s3 + 0.9, 0.5)
        if pp > 0:
            ctx.set_source_rgba(*c, 1); ctx.set_line_width(3)
            ctx.arc(705, Y_GND + 45, 16, -math.pi / 2, -math.pi / 2 + 2 * math.pi * pp); ctx.stroke()
            ctx.arc(705, Y_GND + 45, 9, 0, 2 * math.pi * pp); ctx.stroke()
        leader(ctx, clamp((t - s3 - 1.1) / 0.8), c, (X0 - 22, Y_TOP + 60), (110, 445), "FORMWORK")
        leader(ctx, clamp((t - s3 - 1.4) / 0.8), c, (705, Y_GND + 62), (640, 1147), "DRAINAGE", anchor="r")

    # 4 membrane
    c = tl.col(4, t); p = prog(t, s4, 1.1)
    if p > 0:
        polyline(ctx, [(X0 + 5, Y_TOP - 10), (X0 + 5, Y_BEAM - 5), (XB - 5, Y_BEAM - 5), (XB - 5, Y_PAD - 5), (XBREAK + 10, Y_PAD - 5)],
                 p, c, 3, dash=[12, 7])
        leader(ctx, clamp((t - s4 - 1.0) / 0.8), c, (420, Y_PAD - 5), (330, 1192), "0.2mm MEMBRANE")

    # 5 pods
    c = tl.col(5, t)
    for k, (a, b) in enumerate(((P1L, P1R), (P2L, P2R))):
        p = prog(t, s5 + k * 0.45, 0.7)
        if p <= 0: continue
        ctx.save(); ctx.translate(0, (1 - p) * -60)
        polyline(ctx, rect_pts(a, Y_POD, b, Y_PAD - 8), 1, c, 3, alpha=p)
        polyline(ctx, [(a, Y_POD), (b, Y_PAD - 8)], 1, c, 1.5, alpha=0.45 * p)
        polyline(ctx, [(b, Y_POD), (a, Y_PAD - 8)], 1, c, 1.5, alpha=0.45 * p)
        text(ctx, "EPS POD", (a + b) / 2, (Y_POD + Y_PAD) / 2 + 9, 26, c, alpha=p, bold=True, anchor="c")
        ctx.restore()
        if k == 0:
            for xs in ((P1R + P2L) / 2, (P2R + XR) / 2):
                polyline(ctx, rect_pts(xs - 6, Y_PAD - 30, xs + 6, Y_PAD - 8), p, c, 2, alpha=p)
    leader(ctx, clamp((t - s5 - 1.2) / 0.8), c, (P2L + 4, Y_POD + 40), (610, 445), "1090 SQ POD")

    # 6 reinforcement
    c = tl.col(6, t)
    p = prog(t, s6, 0.7)
    if p > 0:
        polyline(ctx, rect_pts(X0 + 16, Y_TOP + 22, XB - 16, Y_BEAM - 22), p, c, 2.5)
        for y in (Y_TOP + 32, Y_BEAM - 32):
            for x in (X0 + 27, (X0 + XB) / 2, XB - 27):
                dot(ctx, x, y, 6, c, p)
    p = prog(t, s6 + 0.5, 0.6)
    if p > 0:
        for xr in ((P1R + P2L) / 2, (P2R + XR) / 2):
            dot(ctx, xr, Y_PAD - 45, 7, c, p)
            polyline(ctx, [(xr - 10, Y_PAD - 31), (xr, Y_PAD - 50), (xr + 10, Y_PAD - 31)], p, c, 2)
    p = prog(t, s6 + 0.9, 0.9)
    if p > 0:
        ym = Y_TOP + 32
        polyline(ctx, [(X0 + 20, ym), (XBREAK, ym)], p, c, 2.5)
        x = X0 + 40
        while x < X0 + 20 + (XBREAK - X0 - 20) * p:
            dot(ctx, x, ym, 4.5, c); x += 34
        for xc in (330, 450, 680, 800):
            polyline(ctx, [(xc - 10, Y_POD), (xc, ym + 5), (xc + 10, Y_POD)], p, c, 2)
    leader(ctx, clamp((t - s6 - 0.9) / 0.8), c, (XB - 27, Y_BEAM - 32), (110, 1147), "TRENCH MESH")
    leader(ctx, clamp((t - s6 - 1.2) / 0.8), c, ((P1R + P2L) / 2, Y_PAD - 45), (470, 445), "RIB BAR", anchor="r")
    leader(ctx, clamp((t - s6 - 1.5) / 0.8), c, (850, Y_TOP + 32), (960, 445), "MESH", anchor="r")

    # 7 inspection
    stamp(ctx, "INSPECTED", 555, 715, prog(t, s7 + 0.3, 0.35), tl.col(7, t), fade=clamp((t - tl.step_end(7)) / 0.6))

    # 8 pour
    c = tl.col(8, t); p = prog(t, s8, 1.8)
    if p > 0:
        ylev = Y_BEAM - (Y_BEAM - Y_TOP) * p
        ctx.save(); ctx.rectangle(0, ylev, W, H); ctx.clip()
        _concrete_path(ctx); ctx.set_source_rgba(*c, 0.16); ctx.fill()
        draw_concrete(ctx, CONC, c)
        ctx.restore()
        polyline(ctx, [(X0, Y_TOP), (XBREAK, Y_TOP)], prog(t, s8 + 1.6, 0.6), c, 3.5)
        polyline(ctx, [(XBREAK, Y_TOP - 15), (XBREAK, 600), (XBREAK + 12, 610), (XBREAK - 12, 625), (XBREAK, 635), (XBREAK, Y_PAD + 10)],
                 prog(t, s8 + 1.8, 0.5), c, 2)

    # result: dimensions
    r0 = tl.res0
    dim_v(ctx, 85, Y_TOP, Y_POD, "85", prog(t, r0, 0.6))
    dim_v(ctx, 85, Y_POD, Y_PAD, "225", prog(t, r0 + 0.3, 0.6))
    dim_h(ctx, 515, X0, XB, "300", prog(t, r0 + 0.5, 0.6))
    dim_h(ctx, 515, P1L, P1R, "1090", prog(t, r0 + 0.7, 0.6))
    dim_h(ctx, 515, P1R, P2L, "110", prog(t, r0 + 0.9, 0.6))
