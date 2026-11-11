"""005 Super-T girder bridge deck (infrastructure)."""
import math
from engine.blueprint import *

META = {
    "category": "infrastructure",
    "title": "SUPER-T BRIDGE",
    "subtitle": "INFRASTRUCTURE  //  TYPICAL AU METHOD",
    "dwg": "005",
    "section_label": "SECTION AT PIER  (NTS)",
    "hook": ["MOST FREEWAY", "BRIDGES START", "IN A FACTORY."],
    "hook_sub": "HOW A SUPER-T BRIDGE GOES TOGETHER",
    "cover": ["HOW A FREEWAY", "BRIDGE IS", "REALLY BUILT."],
    "steps": [
        ("PILES & PIER", "Bored piles drilled and poured, then the pier column formed up on top."),
        ("HEADSTOCK", "A reinforced concrete headstock is cast across the top of the pier."),
        ("BEARINGS", "Elastomeric bearings set dead level under each girder position."),
        ("GIRDERS IN", "Precast Super-T girders trucked in and craned onto the bearings."),
        ("FLANGES = FORMWORK", "The wide top flanges butt together, so the girders become the deck formwork."),
        ("DECK REO", "Deck reinforcement tied over the girders, with continuity steel over the pier."),
        ("DECK POUR", "The deck slab is poured on top, locking the girders together."),
        ("BARRIERS & SURFACE", "Traffic barriers go on the edges, then joints and the wearing surface."),
    ],
    "result": "Big spans, built fast, with most of the bridge made in a factory.",
}

NARRATION = {
    "hook": "Most freeway bridges in Australia start life in a factory. Here's how a Super-T bridge goes together.",
    "steps": [
        "Bored piles are drilled and poured. Then the pier column is formed up on top.",
        "A reinforced concrete headstock is cast across the top of the pier.",
        "Rubber bearings are set dead level, one under each girder.",
        "Precast Super-T girders are trucked in and craned onto the bearings.",
        "Their wide top flanges butt together, so the girders become the formwork for the deck.",
        "Deck reinforcement is tied over the top, with extra steel over the pier.",
        "Then the deck slab is poured, locking all the girders together.",
        "Finally, the traffic barriers go on, then the joints and the road surface.",
    ],
    "result": "Big spans, built fast, with most of the bridge made in a factory.",
    "end": "Follow for more.",
}

CAPTION = """Most freeway bridges start in a factory 👇 How a Super-T girder bridge goes together.

Precast, pre-tensioned Super-T girders sit on bearings on the pier headstocks. Their top flanges act as permanent formwork for the cast-in-place deck. Typical girder depths run from about 750 to 1800 mm.
Typical only. Every bridge is individually designed.

#infrastructure #bridge #civilengineering #construction #precast #concrete #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
GND = 1060
COL = (480, 600)
HS_TOP, HS_BOT = 820, 900
GX0, GW, NG = 150, 195, 4
G_TOP, G_FL, G_BOT = 650, 664, 808
DECK_TOP = 625
BAR_TOP = 565


def girder_pts(x0):
    W = GW
    return [(x0, G_TOP), (x0 + W, G_TOP), (x0 + W, G_FL), (x0 + W - 32, G_FL), (x0 + W / 2 + 50, G_BOT),
            (x0 + W / 2 - 50, G_BOT), (x0 + 32, G_FL), (x0, G_FL), (x0, G_TOP)]


def void_pts(x0):
    W = GW
    return [(x0 + 44, G_FL + 10), (x0 + W - 44, G_FL + 10), (x0 + W / 2 + 36, G_BOT - 14), (x0 + W / 2 - 36, G_BOT - 14), (x0 + 44, G_FL + 10)]


HEADSTOCK = [(150, HS_TOP), (930, HS_TOP), (930, 860), (800, HS_BOT), (280, HS_BOT), (150, 860), (150, HS_TOP)]
CONC_HS = concrete_points(51, 150, HS_TOP, 930, HS_BOT, 260,
                          lambda x, y: HS_TOP + 4 < y < HS_BOT - 4 and (y < 856 or 290 < x < 790))
CONC_COL = concrete_points(52, COL[0], HS_BOT, COL[1], GND, 120, lambda x, y: COL[0] + 4 < x < COL[1] - 4)
CONC_DECK = concrete_points(53, 150, DECK_TOP, 930, G_TOP, 220, lambda x, y: DECK_TOP + 3 < y < G_TOP - 3)


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]

    # 1 piles + pier column
    c = tl.col(1, t); p = prog(t, s1, 0.9)
    if p > 0:
        earth_hatch(ctx, 90, GND, 970, 1110, c, reveal=p)
        polyline(ctx, [(90, GND), (970, GND)], p, c, 3)
        polyline(ctx, [(500, GND), (500, 1110)], p, c, 2, dash=[10, 6])
        polyline(ctx, [(580, GND), (580, 1110)], p, c, 2, dash=[10, 6])
        pc = prog(t, s1 + 0.7, 0.8)
        if pc > 0:
            polyline(ctx, rect_pts(COL[0], GND - (GND - HS_BOT) * pc, COL[1], GND), 1, c, 3)
            if pc >= 1: draw_concrete(ctx, CONC_COL, c, 0.6)
        leader(ctx, clamp((t - s1 - 1.2) / 0.8), c, (540, 1095), (110, 1192), "BORED PILE")
        leader(ctx, clamp((t - s1 - 1.5) / 0.8), c, (COL[1], 990), (940, 1150), "PIER", anchor="r")

    # 2 headstock
    c = tl.col(2, t); p = prog(t, s2, 0.9)
    if p > 0:
        polyline(ctx, HEADSTOCK, p, c, 3)
        draw_concrete(ctx, CONC_HS, c, 0.6 * clamp((p - 0.5) * 2))
        leader(ctx, clamp((t - s2 - 1.0) / 0.8), c, (250, 880), (110, 1150), "HEADSTOCK")

    # 3 bearings
    c = tl.col(3, t)
    for i in range(NG):
        pb = prog(t, s3 + i * 0.15, 0.4)
        if pb <= 0: continue
        xc = GX0 + i * GW + GW / 2
        polyline(ctx, rect_pts(xc - 34, G_BOT + 2, xc + 34, HS_TOP), pb, c, 2.5)
        for yy in (G_BOT + 6, G_BOT + 10):
            polyline(ctx, [(xc - 30, yy), (xc + 30, yy)], pb, c, 1)
    leader(ctx, clamp((t - s3 - 0.9) / 0.8), c, (GX0 + 3 * GW + GW / 2 + 34, 814), (940, 1192), "BEARING", anchor="r")

    # 4 girders drop in, one at a time
    c = tl.col(4, t)
    for i in range(NG):
        pg = prog(t, s4 + i * 0.4, 0.6)
        if pg <= 0: continue
        x0 = GX0 + i * GW
        ctx.save(); ctx.translate(0, -(1 - pg) * 120)
        polyline(ctx, girder_pts(x0), 1, c, 2.8, alpha=pg)
        polyline(ctx, void_pts(x0), 1, c, 1.6, alpha=0.7 * pg)
        for k in range(3):                                         # prestressing strands
            dot(ctx, x0 + GW / 2 - 24 + k * 24, G_BOT - 7, 2.5, c, pg)
        ctx.restore()
    leader(ctx, clamp((t - s4 - 1.8) / 0.8), c, (GX0 + 3 * GW + 150, 730), (940, 445), "SUPER-T GIRDER", anchor="r")

    # 5 flange joints highlighted
    c = tl.col(5, t); p = prog(t, s5, 0.6)
    if p > 0:
        for i in range(1, NG):
            x = GX0 + i * GW
            ctx.set_source_rgba(*c, p); ctx.arc(x, (G_TOP + G_FL) / 2, 9, 0, 2 * math.pi); ctx.set_line_width(2.5); ctx.stroke()
        fade = 1 - clamp((t - tl.step_end(5)) / 0.4)
        leader(ctx, clamp((t - s5 - 0.6) / 0.8) * fade, c, (GX0 + GW, G_TOP), (110, 445), "FLANGES BUTT TOGETHER")

    # 6 deck reo
    c = tl.col(6, t); p = prog(t, s6, 1.0)
    if p > 0:
        for yy in (DECK_TOP + 7, G_TOP - 7):
            polyline(ctx, [(160, yy), (160 + 760 * p, yy)], 1, c, 2)
            x = 175
            while x < 160 + 760 * p:
                dot(ctx, x, yy, 3, c); x += 30
        leader(ctx, clamp((t - s6 - 1.0) / 0.8), c, (600, DECK_TOP + 7), (560, 520), "DECK REO")

    # 7 deck pour
    c = tl.col(7, t); p = prog(t, s7, 1.4)
    if p > 0:
        clip_rect(ctx, 150, DECK_TOP - 2, 150 + 780 * p, G_TOP)
        ctx.set_source_rgba(*c, 0.16); ctx.rectangle(150, DECK_TOP, 780, G_TOP - DECK_TOP); ctx.fill()
        draw_concrete(ctx, CONC_DECK, c, 0.8)
        ctx.restore()
        polyline(ctx, [(150, DECK_TOP), (150 + 780 * p, DECK_TOP)], 1, c, 3)
        polyline(ctx, [(150, DECK_TOP), (150, G_TOP)], p, c, 3)
        polyline(ctx, [(930, DECK_TOP), (930, G_TOP)], clamp(p * 2 - 1), c, 3)
        leader(ctx, clamp((t - s7 - 1.2) / 0.8), c, (300, DECK_TOP + 12), (110, 520), "DECK SLAB")

    # 8 barriers + wearing surface
    c = tl.col(8, t); p = prog(t, s8, 0.8)
    if p > 0:
        for x0, sgn in ((150, 1), (930, -1)):
            pts = [(x0, DECK_TOP), (x0, BAR_TOP), (x0 + sgn * 22, BAR_TOP), (x0 + sgn * 28, 600), (x0 + sgn * 40, DECK_TOP - 6), (x0 + sgn * 40, DECK_TOP)]
            polyline(ctx, pts, p, c, 3)
        pw = prog(t, s8 + 0.7, 0.8)
        if pw > 0:
            polyline(ctx, rect_pts(190, DECK_TOP - 7, 190 + 700 * pw, DECK_TOP), 1, c, 2)
        leader(ctx, clamp((t - s8 - 1.0) / 0.8), c, (912, 590), (940, 520), "BARRIER", anchor="r")
        leader(ctx, clamp((t - s8 - 1.4) / 0.8), c, (700, DECK_TOP - 4), (560, 482), "WEARING SURFACE")

    # result dims
    r0 = tl.res0
    dim_v(ctx, 108, G_TOP, G_BOT, "750-1800", prog(t, r0, 0.6))
    dim_h(ctx, 975, GX0, GX0 + GW, "~2.1 m", prog(t, r0 + 0.4, 0.6))


# ---------------------------------------------------------------- 3D model (mm): abutment, pier, one finished span, next span going in
def _supert(x0, z0, z1, order):
    from engine.three_d import Part, box
    W, D = 2100, 1500
    yb = 7300
    top = box(x0, x0 + W, yb + D - 150, yb + D, z0, z1, order, "concrete")
    web = Part([(x0 + 350, yb + D - 150, z0), (x0 + W - 350, yb + D - 150, z0), (x0 + W / 2 + 450, yb, z0), (x0 + W / 2 - 450, yb, z0),
                (x0 + 350, yb + D - 150, z1), (x0 + W - 350, yb + D - 150, z1), (x0 + W / 2 + 450, yb, z1), (x0 + W / 2 - 450, yb, z1)],
               order, "concrete")
    return [web, top]


def model3d():
    from engine.three_d import box
    P = []; o = 0
    P.append(box(-2500, 10900, -400, 0, -2500, 24000, o, "ground")); P[-1].base = True; o += 1
    P.append(box(-300, 8700, 0, 7300, -1800, 0, o, "concrete")); o += 1                       # abutment
    P.append(box(3450, 4950, 0, 6100, 13250, 14750, o, "concrete")); o += 1                   # pier column
    P.append(box(-300, 8700, 6100, 7200, 13000, 15000, o, "concrete")); o += 1                # headstock
    for i in range(4):                                                                       # span 1 girders
        P += _supert(i * 2100, 0, 13900, o); o += 1
    P.append(box(0, 8400, 8800, 9000, 0, 13950, o, "concrete")); o += 1                       # deck, span 1
    P.append(box(0, 350, 9000, 9900, 0, 13950, o, "concrete")); P.append(box(8050, 8400, 9000, 9900, 0, 13950, o, "concrete")); o += 1
    for i in range(2):                                                                       # span 2, girders going in
        P += _supert(i * 2100, 14100, 26000, o); o += 1
    cfg = {"target": (4200, 5500, 13000), "yaw": -25, "pitch": 10, "dist": 42000, "scale": 1.95,
           "cy_hook": 1010, "cy_result": 820, "cy_cover": 1020, "cover_scale": 0.95}
    return P, cfg
