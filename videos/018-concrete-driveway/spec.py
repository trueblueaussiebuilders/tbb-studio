"""018 Concrete driveway (civil)."""
import math
from engine.blueprint import *

META = {
    "category": "civil",
    "title": "CONCRETE DRIVEWAY",
    "subtitle": "CIVIL  //  TYPICAL AU METHOD",
    "dwg": "018",
    "drawing": "CONCRETE DRIVEWAY",
    "section_label": "SECTION ALONG DRIVEWAY  (NTS)",
    "hook": ["THOSE CRACKS IN", "YOUR DRIVEWAY", "WERE PLANNED."],
    "hook_sub": "HOW A CONCRETE DRIVEWAY IS BUILT",
    "cover": ["THE CRACKS", "ARE ON", "PURPOSE."],
    "question": "Go and look: do the cracks in your driveway sit in the joints? Tell us below.",
    "hook_start": 0.5,
    "xray": {"after_step": 4, "upto": 5, "hot": [5]},     # mesh on the base, the slab still to come
    "steps": [
        ("DIG + TRIM", "Topsoil off. The ground is trimmed so the drive falls away from the garage."),
        ("ROCK BASE", "Crushed rock goes down in layers. Each layer is compacted."),
        ("FORMS + JOINT", "Timber forms are pegged to level. A foam strip separates the garage slab."),
        ("MESH ON CHAIRS", "Bar chairs lift the mesh so it ends up inside the concrete."),
        ("POUR + SCREED", "Concrete is poured, then screeded off the forms to level."),
        ("FLOAT + BROOM", "Floated smooth, broomed across for grip, edges rounded."),
        ("SAW CUTS", "Joints are cut part-way through. Each one is a planned weak line."),
        ("CURE", "Kept damp or sprayed with curing compound. No cars until it's strong."),
    ],
    "result": "Concrete shrinks as it dries. The cuts make it crack in a straight line, hidden in the joint.",
}

NARRATION = {
    "hook": "Those cracks in your driveway? They were planned.",
    "steps": [
        "First, the topsoil is stripped. The ground is dug out and trimmed, so the driveway falls away from the garage.",
        "A crushed rock base is spread in layers. Each layer is compacted with a plate compactor or a roller.",
        "Timber forms are pegged along the edges, set to the finished levels. A foam isolation strip goes against the garage slab.",
        "Steel mesh goes in on plastic bar chairs. That lifts it up, so it ends up inside the concrete, not under it.",
        "The concrete is poured. Then it's screeded off the forms with a straight edge, to the right level.",
        "It's floated smooth, then broomed across for grip. The edges are rounded off with an edging tool.",
        "Soon after, joints are saw cut across the slab. Each cut makes a weak line, part-way through the concrete.",
        "Finally, it's kept damp, or sprayed with a curing compound, so it hardens slowly. Cars stay off until it's strong enough.",
    ],
    "result": "Concrete shrinks as it dries, so it will crack. The saw cuts make sure it cracks in a straight line, hidden in the joint.",
    "end": "Follow for more.",
}

CAPTION = """Those cracks in your driveway were planned 👇 How a concrete driveway is built.

Typical: topsoil is stripped and the ground is dug out and trimmed, with falls away from the garage and the house. A crushed rock base is placed in layers and compacted. Timber edge forms are pegged to the finished levels, and an isolation joint (a compressible foam strip) goes where the driveway meets the garage slab or another structure. Reinforcing mesh sits on bar chairs so it ends up inside the concrete, not on the ground. The concrete is poured, screeded off the forms, floated, broomed across for grip and edged. Control joints are saw cut soon after the pour (or tooled in while it's wet), part-way through the slab, so the shrinkage cracks form in the joints instead of wandering across the slab. It's then cured, and cars stay off it until it has gained enough strength.
Slab thickness, mesh, joint spacing and concrete strength depend on the loads, the ground and your council's crossover rules.
Typical only. Your engineer's design governs.

#concretedriveway #driveway #concrete #concreting #civilconstruction #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS; layers exaggerated)
GX0, GX1 = 70, 226                    # garage slab (left)
GT, GB = 868, 990                     # garage slab top / bottom
DX0, DX1 = 234, 962                   # driveway: isolation joint 226..234, form face at DX1
ST, BT = 80, 62                       # slab and base thickness (px)
NS = 836                              # natural surface before the dig
CUTS = [416, 598, 780]                # saw cut positions
EARTH_B = 1180


def top(x):
    """Finished slab top: falls away from the garage."""
    return GT + 2 + (x - DX0) * 40.0 / (DX1 - DX0)


def line(off, x0=DX0, x1=DX1, n=12):
    return [(x0 + (x1 - x0) * i / n, top(x0 + (x1 - x0) * i / n) + off) for i in range(n + 1)]


SLAB_CONC = concrete_points(181, DX0, GT, DX1, GT + 130, 380, inside=lambda x, y: top(x) + 4 < y < top(x) + ST - 4)
BASE_GRAV = gravel(182, DX0, GT + ST, DX1 + 30, GT + ST + BT + 45, 420)
BASE_GRAV = [(x, y, r) for x, y, r in BASE_GRAV if top(x) + ST + 5 < y < top(x) + ST + BT - 5 and x < DX1 + 24]
GAR_CONC = concrete_points(183, GX0, GT, GX1, GB, 50)

# plan inset (top band): same x as the section so the joints line up
PY0, PY1 = 470, 630


def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def arrow(ctx, x0, y0, x1, y1, col, p=1.0, a=1.0, head=12, width=3):
    if p <= 0: return
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    polyline(ctx, [(x0, y0), (xe, ye)], 1, col, width, alpha=a)
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    polyline(ctx, [(xe - ux * head - uy * head * 0.8, ye - uy * head + ux * head * 0.8), (xe, ye),
                   (xe - ux * head + uy * head * 0.8, ye - uy * head - ux * head * 0.8)], 1, col, width, alpha=a)


def plan(ctx, t, tl, a):
    """Driveway plan: garage on the left, forms, mesh, the pour, broom marks, then the saw cuts across."""
    if a <= 0: return
    s1, s3, s4, s5, s6, s7 = tl.s(1), tl.s(3), tl.s(4), tl.s(5), tl.s(6), tl.s(7)
    ctx.push_group()
    text(ctx, "DRIVEWAY PLAN", DX0, PY0 - 18, 22, BLUE, bold=True, spacing=3)
    fill_poly(ctx, rect_pts(GX0 + 20, PY0 - 10, DX1 + 30, PY1 + 10)[:4], BG, 0.9)
    # garage: three walls, door opening towards the driveway
    polyline(ctx, [(GX1, PY0 - 6), (GX0 + 20, PY0 - 6), (GX0 + 20, PY1 + 6), (GX1, PY1 + 6)], 1, WHITE, 5, alpha=0.8)
    polyline(ctx, [(GX1, PY0 - 6), (GX1, PY1 + 6)], 1, WHITE, 1.6, alpha=0.6, dash=[7, 6])
    text(ctx, "GARAGE", (GX0 + 20 + GX1) / 2, (PY0 + PY1) / 2 + 8, 22, WHITE, alpha=0.8, bold=True, anchor="c")
    # driveway outline (set out in step 1)
    polyline(ctx, rect_pts(DX0, PY0, DX1, PY1), prog(t, s1 + 0.4, 1.0), WHITE, 1.6, alpha=0.6, dash=[9, 6])
    # pour (step 5): fill sweeps from the garage out
    pp = prog(t, s5 + 0.3, 2.0)
    if pp > 0:
        fill_poly(ctx, rect_pts(DX0, PY0, DX0 + (DX1 - DX0) * pp, PY1)[:4], BLUE, 0.22)
    # mesh (step 4): faint grid
    pm = prog(t, s4 + 0.3, 1.0)
    if pm > 0:
        ctx.set_source_rgba(*tl.col(4, t), 0.35 * pm * (1 - 0.6 * prog(t, s5 + 0.3, 2.0))); ctx.set_line_width(1.2)
        xe = DX0 + (DX1 - DX0) * pm
        for x in range(DX0 + 20, int(xe), 24):
            ctx.move_to(x, PY0 + 6); ctx.line_to(x, PY1 - 6)
        for y in range(PY0 + 18, PY1, 24):
            ctx.move_to(DX0 + 6, y); ctx.line_to(xe, y)
        ctx.stroke()
    # broom marks across the width (step 6)
    pb = prog(t, s6 + 0.5, 1.6)
    if pb > 0:
        ctx.set_source_rgba(*tl.col(6, t), 0.45); ctx.set_line_width(1.4)
        x = DX0 + 8
        while x < DX0 + (DX1 - DX0) * pb:
            ctx.move_to(x, PY0 + 10); ctx.line_to(x, PY1 - 10); x += 9
        ctx.stroke()
    # forms along both edges and the end (step 3), pegs outside
    c3 = tl.col(3, t)
    pf = prog(t, s3 + 0.2, 1.0)
    polyline(ctx, [(DX0, PY0), (DX1, PY0), (DX1, PY1), (DX0, PY1)], pf, c3, 5)
    kp = prog(t, s3 + 1.0, 0.5)
    if kp > 0:
        for x in range(DX0 + 50, DX1, 110):
            dot(ctx, x, PY0 - 11, 5, c3, kp); dot(ctx, x, PY1 + 11, 5, c3, kp)
    # isolation joint against the garage (step 3)
    polyline(ctx, [(DX0 - 4, PY0), (DX0 - 4, PY1)], prog(t, s3 + 1.4, 0.5), BLUE, 6)
    # saw cuts across the drive (step 7), one after another, in step with the section
    for i, x in enumerate(CUTS):
        polyline(ctx, [(x, PY0 + 2), (x, PY1 - 2)], prog(t, s7 + 0.3 + i * 0.7, 0.6), ORANGE, 4)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    cap = [(s3 + 0.6, s4, "FORMS PEGGED TO LEVEL"), (s4 + 0.6, s5, "MESH OVER THE WHOLE SLAB"),
           (s6 + 0.6, s7, "BROOMED ACROSS FOR GRIP"), (s7 + 0.6, tl.s(8), "JOINTS CUT ACROSS THE DRIVE")]
    for t0, t1, s in cap:
        k = clamp((t - t0) / 0.3) * gone(t, t1 - 0.1, 0.3) * a
        if k > 0:
            text(ctx, s, DX1, PY1 + 46, 22, WHITE, alpha=0.9 * k, bold=True, anchor="r", spacing=1)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    # ---- garage slab (context) + earth under everything
    pg = prog(t, s1, 0.8)
    if pg > 0:
        polyline(ctx, rect_pts(GX0, GT, GX1, GB), pg, WHITE, 3)
        draw_concrete(ctx, GAR_CONC, WHITE, 0.45 * pg)
        earth_hatch(ctx, GX0, GB, DX1 + 40, EARTH_B, WHITE, 0.12, reveal=pg)

    # ---- 1 strip the topsoil, dig and trim to the fall
    c1 = tl.col(1, t)
    pdig = prog(t, s1 + 0.6, 1.6)
    # natural surface + topsoil band, removed left to right
    xs = DX0 + (DX1 + 40 - DX0) * pdig
    if xs < DX1 + 40:
        polyline(ctx, [(xs, NS), (DX1 + 40, NS)], 1, WHITE, 2.5, alpha=0.8 * pg)
        earth_hatch(ctx, xs, NS, DX1 + 40, top(DX1) + ST + BT, WHITE, 0.3 * pg)
    # the trimmed cut line (bottom of the base), drawn behind the dig
    cut = line(ST + BT)
    polyline(ctx, cut + [(DX1 + 40, top(DX1) + ST + BT)], pdig, c1, 3)
    polyline(ctx, [(GX1, GT), (DX0, GT), (DX0, top(DX0) + ST + BT)], prog(t, s1 + 0.6, 0.4), c1, 2.5)
    pa = prog(t, s1 + 2.0, 0.6) * gone(t, s2 + 0.4)
    arrow(ctx, 290, 790, 520, 808, BLUE, p=pa, head=10)
    if pa > 0:
        text(ctx, "FALL", 405, 776, 26, BLUE, alpha=clamp(pa * 2 - 1), bold=True, anchor="c", spacing=3)
    label(ctx, clamp((t - s1 - 0.8) / 0.8), WHITE, (760, NS), (640, 740), "TOPSOIL STRIPPED", a=gone(t, s2))
    label(ctx, clamp((t - s1 - 1.8) / 0.8), c1, (420, top(420) + ST + BT), (330, 1080), "TRIMMED TO FALL",
          a=gone(t, s2 + 0.2))

    # ---- 2 crushed rock base in two layers, each compacted by a plate compactor running along it
    c2 = tl.col(2, t)
    for j in range(2):
        t0 = s2 + 0.2 + j * 1.5
        k = prog(t, t0, 0.7)
        if k <= 0: continue
        y_lo, y_hi = ST + BT - j * BT / 2, ST + BT - (j + 1) * BT / 2
        xe = DX0 + (DX1 + 30 - DX0) * k
        ctx.save(); ctx.rectangle(DX0, 780, xe - DX0, 300); ctx.clip()
        poly = line(y_hi, DX0, DX1 + 30) + line(y_lo, DX0, DX1 + 30)[::-1]
        fill_poly(ctx, poly, BG, 1)
        draw_gravel(ctx, [(x, y, r) for x, y, r in BASE_GRAV if top(x) + y_hi < y < top(x) + y_lo], c2, 0.6)
        polyline(ctx, line(y_hi, DX0, DX1 + 30), 1, c2, 2.5)
        ctx.restore()
        # plate compactor pass
        kc = prog(t, t0 + 0.6, 0.8)
        if 0 < kc < 1:
            x = DX0 + 40 + (DX1 - DX0 - 60) * kc
            y = top(x) + y_hi
            jig = 2 * math.sin(t * 60)
            fill_poly(ctx, rect_pts(x - 28, y - 20 + jig, x + 28, y - 2 + jig)[:4], BG, 1)
            polyline(ctx, rect_pts(x - 28, y - 20 + jig, x + 28, y - 2 + jig), 1, WHITE, 2.5)
            polyline(ctx, [(x - 10, y - 20 + jig), (x - 52, y - 74)], 1, WHITE, 2.5)
            polyline(ctx, [(x - 62, y - 70), (x - 42, y - 80)], 1, WHITE, 3)
            for d in (-1, 1):
                polyline(ctx, [(x + d * 36, y - 16), (x + d * 44, y - 8)], 1, ORANGE, 2)
    label(ctx, clamp((t - s2 - 0.9) / 0.8), c2, (520, top(520) + ST + BT * 0.7), (330, 1080), "CRUSHED ROCK BASE",
          a=gone(t, s3 + 0.3))
    label(ctx, clamp((t - s2 - 2.4) / 0.8), c2, (760, top(760) + ST + 6), (640, 740), "COMPACTED IN LAYERS",
          a=gone(t, s3 + 0.3))

    # ---- 3 forms + pegs at the end, isolation joint against the garage slab
    c3 = tl.col(3, t)
    kf = prog(t, s3 + 0.2, 0.6)
    if kf > 0:
        dy = -(1 - kf) * 120
        y0, y1 = top(DX1) - 4 + dy, top(DX1) + ST + dy
        fill_poly(ctx, rect_pts(DX1, y0, DX1 + 14, y1)[:4], BG, 1)
        polyline(ctx, rect_pts(DX1, y0, DX1 + 14, y1), 1, c3, 3)
    kpg = prog(t, s3 + 0.7, 0.5)
    if kpg > 0:
        y0 = top(DX1) - 24
        yb = y0 + (top(DX1) + ST + BT + 50 - y0) * kpg
        polyline(ctx, rect_pts(DX1 + 16, y0, DX1 + 28, yb), 1, c3, 2.5)
    kj = prog(t, s3 + 1.6, 0.6)
    if kj > 0:
        y1 = GT + (top(DX0) + ST - GT) * kj
        fill_poly(ctx, rect_pts(GX1, GT, DX0, y1)[:4], BLUE, 0.9)
    label(ctx, clamp((t - s3 - 0.7) / 0.8), c3, (DX1 + 7, top(DX1) + 20), (940, 790), "TIMBER FORM", anchor="r",
          a=gone(t, s5))
    label(ctx, clamp((t - s3 - 1.6) / 0.8), BLUE, (DX0 - 4, GT + 24), (290, 790), "ISOLATION JOINT", a=gone(t, s5))

    # ---- 4 bar chairs on the base, mesh across the top of them
    c4 = tl.col(4, t)
    my = 32                                                  # mesh height below the finished top
    chairs = list(range(DX0 + 40, DX1 - 10, 76))
    for i, x in enumerate(chairs):
        k = prog(t, s4 + 0.2 + i * 0.08, 0.3)
        if k <= 0: continue
        yb, yt = top(x) + ST, top(x) + my + 3
        polyline(ctx, [(x - 8, yb), (x, yt), (x + 8, yb)], 1, c4, 2, alpha=k)
    km = prog(t, s4 + 1.0, 0.5)
    if km > 0:
        dy = -(1 - km) * 90
        polyline(ctx, line(my + dy, DX0 + 14, DX1 - 14), 1, c4, 2.5)
        for x in range(DX0 + 22, DX1 - 14, 28):
            dot(ctx, x, top(x) + my - 5 + dy, 3.5, c4, 1)
    label(ctx, clamp((t - s4 - 1.3) / 0.8), c4, (560, top(560) + my - 2), (640, 740), "STEEL MESH", a=gone(t, s5 + 0.6))
    label(ctx, clamp((t - s4 - 0.6) / 0.8), c4, (chairs[7], top(chairs[7]) + ST - 4), (640, 1080), "BAR CHAIR",
          a=gone(t, s5 + 0.6))

    # ---- 5 pour (fills from the garage out), then the straight edge runs along the forms
    c5 = tl.col(5, t)
    kp = prog(t, s5 + 0.2, 2.0)
    if kp > 0:
        xe = DX0 + (DX1 - DX0) * kp
        ctx.save(); ctx.rectangle(DX0, 780, xe - DX0, 300); ctx.clip()
        poly = line(0) + line(ST)[::-1]
        fill_poly(ctx, poly, BG, 0.75)
        draw_concrete(ctx, SLAB_CONC, c5 if t < s6 else WHITE, 0.7)
        polyline(ctx, line(0), 1, c5, 3)
        ctx.restore()
        # keep the mesh visible inside the concrete (dashed once it's cast in)
        polyline(ctx, line(my, DX0 + 14, min(xe, DX1 - 14)), 1, tl.col(4, t) if t < s6 else WHITE, 2, alpha=0.8, dash=[8, 6])
    ks = prog(t, s5 + 1.6, 1.6)
    if 0 < ks < 1:
        x = DX0 + 20 + (DX1 - DX0 - 40) * ks
        fill_poly(ctx, rect_pts(x - 10, top(x) - 16, x + 10, top(x))[:4], BG, 1)
        polyline(ctx, rect_pts(x - 10, top(x) - 16, x + 10, top(x)), 1, ORANGE, 3)
    label(ctx, clamp((t - s5 - 0.6) / 0.8), c5, (420, top(420) + 30), (330, 1080), "CONCRETE", a=gone(t, s6))
    sx = DX0 + 20 + (DX1 - DX0 - 40) * clamp(ks)
    label(ctx, clamp((t - s5 - 1.8) / 0.8), ORANGE, (sx, top(sx) - 16), (940, 740), "STRAIGHT EDGE", anchor="r",
          a=gone(t, s6))

    # ---- 6 float + broom: texture marks along the top, then a rounded edge at the form
    c6 = tl.col(6, t)
    kb = prog(t, s6 + 0.4, 1.8)
    if kb > 0:
        xe = DX0 + (DX1 - DX0) * kb
        ctx.set_source_rgba(*c6, 0.9); ctx.set_line_width(1.6)
        x = DX0 + 6
        while x < xe:
            ctx.move_to(x, top(x) - 1); ctx.line_to(x + 3, top(x) - 7); x += 11
        ctx.stroke()
    ke = prog(t, s6 + 1.8, 0.5)
    if ke > 0:
        x, y = DX1 - 2, top(DX1)
        ctx.set_source_rgba(*c6, ke); ctx.set_line_width(4)
        ctx.new_path(); ctx.arc(x - 12, y + 12, 12, -math.pi / 2, 0); ctx.stroke()
    label(ctx, clamp((t - s6 - 0.9) / 0.8), c6, (700, top(700) - 4), (640, 790), "BROOMED FOR GRIP", a=gone(t, s7))
    label(ctx, clamp((t - s6 - 2.0) / 0.8), c6, (DX1 - 8, top(DX1) + 2), (940, 740), "ROUNDED EDGE", anchor="r",
          a=gone(t, s7))

    # ---- 7 saw cuts: a blade drops into each joint, one after another
    c7 = tl.col(7, t)
    depth = ST * 0.28
    for i, x in enumerate(CUTS):
        t0 = s7 + 0.3 + i * 0.7
        k = prog(t, t0, 0.6)
        if k <= 0: continue
        y = top(x)
        fill_poly(ctx, rect_pts(x - 3, y - 2, x + 3, y + depth * k)[:4], BG, 1)
        polyline(ctx, [(x - 3, y), (x - 3, y + depth * k), (x + 3, y + depth * k), (x + 3, y)], 1, c7, 2.5)
        if t < t0 + 0.75:   # the blade
            ab = clamp((t - t0 + 0.1) / 0.15) * clamp((t0 + 0.75 - t) / 0.15)
            cy = y + depth * k - 40
            ctx.set_source_rgba(*WHITE, ab); ctx.set_line_width(2.5)
            ctx.new_path(); ctx.arc(x, cy, 40, 0, 2 * math.pi); ctx.stroke()
            for j in range(8):
                ang = j * math.pi / 4 + t * 12
                polyline(ctx, [(x + 30 * math.cos(ang), cy + 30 * math.sin(ang)),
                               (x + 40 * math.cos(ang), cy + 40 * math.sin(ang))], 1, ORANGE, 2.5, alpha=ab)
    label(ctx, clamp((t - s7 - 0.8) / 0.8), c7, (CUTS[1], top(CUTS[1]) + 4), (640, 790), "SAW CUT", a=gone(t, s8))
    label(ctx, clamp((t - s7 - 1.9) / 0.8), c7, (CUTS[2] + 3, top(CUTS[2]) + depth), (640, 1080), "PART-WAY THROUGH",
          a=gone(t, s8))

    # ---- 8 cure: curing compound sprayed along the top, then "no cars yet"
    kc = prog(t, s8 + 0.3, 1.6)
    if kc > 0:
        polyline(ctx, line(-3), kc, BLUE, 4, alpha=0.9 * gone(t, r0, 0.5))
        x = DX0 + (DX1 - DX0) * kc
        if kc < 1:
            for d in (-1, 0, 1):
                polyline(ctx, [(x, top(x) - 60), (x + d * 22, top(x) - 8)], 1, BLUE, 2, alpha=0.8, dash=[4, 5])
    label(ctx, clamp((t - s8 - 0.9) / 0.8), BLUE, (450, top(450) - 3), (290, 790), "CURING COMPOUND",
          a=gone(t, r0))
    kn = gone(t, r0, 0.4)
    if kn > 0:
        ctx.push_group()
        stamp(ctx, "NO CARS YET", 760, 752, prog(t, s8 + 2.0, 0.35), ORANGE, angle=-0.08)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(kn)

    # plan inset (steps 1-8)
    plan(ctx, t, tl, prog(t, s1 + 0.2, 0.4) * gone(t, r0, 0.5))

    # ---- result: the slab shrinks, and cracks right under the cuts
    pr = prog(t, r0 + 0.2, 0.6)
    if pr > 0:
        for x in (330, 507, 689, 871):
            arrow(ctx, x - 50, 820, x - 12, 820, BLUE, p=pr, head=9)
            arrow(ctx, x + 50, 820, x + 12, 820, BLUE, p=pr, head=9)
        text(ctx, "CONCRETE SHRINKS", 540, 540, 34, BLUE, alpha=clamp(pr * 2 - 1), bold=True, anchor="c", spacing=2)
        text(ctx, "AS IT DRIES", 540, 590, 34, BLUE, alpha=clamp(pr * 2 - 1), bold=True, anchor="c", spacing=2)
    for i, x in enumerate(CUTS):
        k = prog(t, r0 + 1.2 + i * 0.35, 0.5)
        if k <= 0: continue
        y0, y1 = top(x) + depth, top(x) + ST
        pts = [(x, y0)] + [(x + (5 if j % 2 else -5), y0 + (y1 - y0) * j / 5) for j in range(1, 5)] + [(x, y1)]
        polyline(ctx, pts, k, ORANGE, 3)
    pc = prog(t, r0 + 1.4, 0.5)
    if pc > 0:
        text(ctx, "IT CRACKS IN THE JOINTS", 540, 680, 34, ORANGE, alpha=pc, bold=True, anchor="c", spacing=1)


# ---------------------------------------------------------------- 3D model (mm): garage + driveway
def model3d():
    from engine.three_d import box
    P = []
    L, HW = 9000, 1500                        # driveway length, half width
    g = box(-4800, L + 900, -300, 0, -3100, 3100, 0, "ground"); g.base = True; P.append(g)
    # garage (context, on from frame 0): slab, walls, roller door, roof
    GL_, GH = 4200, 2500
    P.append(box(-GL_, 0, 0, 300, -2800, 2800, 0, "concrete"))
    P.append(box(-GL_, 0, 300, GH, -2800, -2690, 0, "brick"))
    P.append(box(-GL_, 0, 300, GH, 2690, 2800, 0, "brick"))
    P.append(box(-GL_, -GL_ + 110, 300, GH, -2690, 2690, 0, "brick"))
    P.append(box(-110, 0, 2150, GH, -2690, 2690, 0, "brick"))
    P.append(box(-80, -40, 220, 2150, -2500, 2500, 0, "steel"))
    P.append(box(-GL_ - 200, 250, GH, GH + 120, -3000, 3000, 0, "steel"))
    # 1-2 crushed rock base in two layers
    P.append(box(0, L, 0, 50, -HW - 60, HW + 60, 1, "ground"))
    P.append(box(0, L, 50, 100, -HW - 60, HW + 60, 2, "ground"))
    # 3 forms along both sides and the end, with pegs
    P.append(box(0, L, 100, 320, -HW - 40, -HW, 3, "timber"))
    P.append(box(0, L, 100, 320, HW, HW + 40, 3, "timber"))
    P.append(box(L, L + 40, 100, 320, -HW - 40, HW + 40, 3, "timber"))
    for x in range(600, L, 1500):
        for z in (-HW - 90, HW + 40):
            P.append(box(x, x + 50, 60, 380, z, z + 50, 3, "timber"))
    # 4 isolation joint against the garage slab
    P.append(box(0, 30, 100, 300, -HW, HW, 4, "membrane"))
    # 5 mesh on chairs
    for z in range(-HW + 150, HW, 300):
        P.append(box(80, L - 80, 150, 166, z - 8, z + 8, 5, "steel"))
    for x in range(150, L, 300):
        P.append(box(x - 8, x + 8, 166, 182, -HW + 80, HW - 80, 5, "steel"))
    # 6 the slab
    P.append(box(30, L, 100, 300, -HW, HW, 6, "concrete"))
    # 7 saw cuts across the slab
    for x in (2250, 4500, 6750):
        P.append(box(x - 25, x + 25, 300, 310, -HW, HW, 7, "steel"))
    cfg = {"target": (2600, 400, 0), "yaw": -120, "pitch": 28, "dist": 26000, "scale": 1.75,
           "cy_hook": 1150, "cy_result": 800, "cy_cover": 1000, "cover_scale": 1.0}
    return P, cfg
