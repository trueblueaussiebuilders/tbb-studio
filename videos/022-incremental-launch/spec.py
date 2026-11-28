"""022 Incremental launch: a bridge deck cast on the bank and pushed across the valley (infrastructure)."""
import math
from engine.blueprint import *

META = {
    "category": "infrastructure",
    "title": "INCREMENTAL LAUNCH",
    "subtitle": "INFRASTRUCTURE  //  TYPICAL METHOD",
    "dwg": "022",
    "drawing": "INCREMENTAL LAUNCH",
    "section_label": "ELEVATION ALONG BRIDGE  (NTS)",
    "hook": ["THIS BRIDGE", "WAS PUSHED", "ACROSS."],
    "hook_sub": "HOW A LAUNCHED BRIDGE IS BUILT",
    "cover": ["THIS BRIDGE", "WAS PUSHED", "ACROSS."],
    "question": "Would you have guessed this bridge was pushed into place? Yes or no below.",
    "hook_start": 0.5,                 # frame 0: abutments, piers and the first deck segments
    "xray": {"after_step": 1, "upto": 3, "hot": [2, 3]},   # piers + abutments in, the whole deck still a ghost
    "steps": [
        ("PIERS FIRST", "The piers and abutments are built across the valley before any deck exists."),
        ("CASTING YARD", "A casting yard and a steel mould are set up on the bank behind one abutment."),
        ("FIRST SEGMENT", "The first deck segment is cast in the mould and left to gain strength."),
        ("LAUNCHING NOSE", "A light steel nose is fixed to the front of the first segment."),
        ("PUSH", "Hydraulic jacks push the deck forward on sliding bearings, one segment length."),
        ("CAST AND PUSH", "The next segment is cast against the back of the last one, then pushed again."),
        ("REPEAT", "Cycle after cycle, the deck creeps across. The nose reaches each pier first."),
        ("FINAL POSITION", "The nose comes off and the deck is lowered onto its permanent bearings."),
    ],
    "result": "The whole deck was built in one spot on the bank, then pushed across the valley.",
}

NARRATION = {
    "hook": "This bridge wasn't built across the valley. It was pushed across.",
    "steps": [
        "First, the piers and abutments are built across the valley. There's no deck yet.",
        "Behind one abutment, a casting yard is set up on the bank, with a steel mould.",
        "The first deck segment is cast in the mould. It's left to gain strength.",
        "A light steel launching nose is fixed to the front.",
        "Then hydraulic jacks push the whole deck forward on sliding bearings. One segment length at a time.",
        "The next segment is cast against the back of the last one. Then the deck is pushed again.",
        "Cycle after cycle, the deck creeps across the valley. The nose reaches each pier first, so the deck never hangs out too far.",
        "At the far side, the nose comes off. The deck is lowered onto its permanent bearings.",
    ],
    "result": "The whole deck was built in one spot on the bank. Then it was pushed across.",
    "end": "Follow for more.",
}

CAPTION = """This bridge was pushed across the valley 👇 How an incrementally launched bridge is built.

Typical: incremental launching is used on some motorway and rail bridges in Australia and around the world, usually where a valley, river, road or rail line makes falsework underneath hard or unsafe. The piers and abutments are built first. A casting yard is set up on the approach behind one abutment, with a steel mould for the deck (often a concrete box girder). Each segment is cast against the back of the one before it, so the deck is one continuous piece. Once a segment has gained strength, hydraulic jacks push the whole deck forward by one segment length, sliding on temporary low-friction bearings on each pier. A light steel launching nose on the front reaches each pier before the deck does, so the deck never cantilevers too far. The cycle repeats until the deck reaches the far abutment. The nose is then removed, further prestressing is often added, and the deck is lowered onto its permanent bearings.
Segment lengths, launch forces, prestressing and bearing details come from the bridge designer.
Typical only. Your engineer's design governs.

#bridgeconstruction #incrementallaunch #civilengineering #infrastructure #bridge #construction #australia #trueblueaussiebuilders"""

# ---------------------------------------------------------------- geometry (px, NTS)
GL = 700                               # approach ground level (both banks)
DK_T, DK_B = 632, 680                  # deck top / soffit
BRG_B = 690                            # top of piers / abutments (bearings sit DK_B..BRG_B)
L = 146                                # segment length
YARD = (104, 250)                      # the newest segment is cast here (front at the left abutment bearing)
ABUT = [(236, 262), (968, 994)]        # abutment walls
PIERS = [493, 737]                     # pier centres
PIER_W, HEAD_W = 14, 30                # half-widths: pier shaft, headstock
NOSE = 140                             # launching nose length
CLIP_X1 = 1012                         # the drawing stops here (the nose runs off past the far abutment)
GROUND = [(56, GL), (262, GL), (300, 760), (420, 1000), (560, 1082), (690, 1082), (820, 960), (940, 760),
          (968, GL), (1024, GL)]
BRGS = [249, PIERS[0], PIERS[1], 981]  # bearing centres

SEG_CONC = concrete_points(221, 4, DK_T + 6, L - 4, DK_B - 6, 18)
BED_CONC = concrete_points(222, 98, 682, 234, 698, 18)


def ground_y(x):
    for (x0, y0), (x1, y1) in zip(GROUND, GROUND[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return GL


def fill_poly(ctx, pts, col, alpha):
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.fill()


def arrow(ctx, x0, y0, x1, y1, col, p=1.0, a=1.0, head=14):
    if p <= 0: return
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    polyline(ctx, [(x0, y0), (xe, ye)], 1, col, 4, alpha=a)
    ang = math.atan2(ye - y0, xe - x0)
    fill_poly(ctx, [(xe, ye), (xe - head * math.cos(ang - 0.5), ye - head * math.sin(ang - 0.5)),
                    (xe - head * math.cos(ang + 0.5), ye - head * math.sin(ang + 0.5))], col, a)


# ---------------------------------------------------------------- launch timeline
def casts(tl):
    """(start, duration, step) for each segment's pour."""
    s3, s6, s7 = tl.s(3), tl.s(6), tl.s(7)
    d7 = tl.step_end(7) - s7
    out = [(s3 + 0.3, 1.3, 3), (s6 + 0.2, 1.1, 6)]
    for j in range(3):
        out.append((s7 + d7 * (0.02 + 0.3 * j), d7 * 0.09, 7))
    return out


def pushes(tl):
    """(start, duration) for each push of one segment length."""
    s5, s6, s7 = tl.s(5), tl.s(6), tl.s(7)
    d5, d6, d7 = (tl.step_end(i) - tl.s(i) for i in (5, 6, 7))
    out = [(s5 + 0.9, min(2.4, d5 - 1.3)), (s6 + 1.5, min(1.8, d6 - 1.8))]
    for j in range(3):
        out.append((s7 + d7 * (0.12 + 0.3 * j), d7 * 0.16))
    return out


def front(t, tl):
    """x of the deck's front end, and how strongly it's moving (0..1) right now."""
    F, moving = YARD[1], 0.0
    for t0, d in pushes(tl):
        k = clamp((t - t0) / d)
        F += L * ease(k)
        if 0 < k < 1: moving = 1.0
        elif t0 - 0.2 < t < t0 + d + 0.3: moving = max(moving, 0.6)
    return F, moving


def nose_arrivals(tl):
    """(time, x) when the nose tip reaches each pier and the far abutment."""
    out = []
    for j, (t0, d) in enumerate(pushes(tl)):
        Fs = YARD[1] + L * j
        for x in BRGS[1:]:
            if Fs + NOSE < x <= Fs + L + NOSE:
                f = (x - NOSE - Fs) / L
                lo, hi = 0.0, 1.0                   # invert the eased push: when does it cover fraction f
                for _ in range(20):
                    mid = (lo + hi) / 2
                    lo, hi = (mid, hi) if ease(mid) < f else (lo, mid)
                out.append((t0 + d * lo, x))
    return out


def draw_section(ctx, t, tl):
    s1, s2, s3, s4, s5, s6, s7, s8 = [tl.s(i) for i in range(1, 9)]
    r0 = tl.res0

    # ---- ground (always there): approach banks, valley, creek, earth hatch
    pg = prog(t, s1 - 0.1, 0.7)
    if pg > 0:
        ctx.save(); ctx.move_to(*GROUND[0])
        for p in GROUND[1:]: ctx.line_to(*p)
        ctx.line_to(1024, 1195); ctx.line_to(56, 1195); ctx.close_path(); ctx.clip()
        earth_hatch(ctx, 56, 640, 1024, 1195, WHITE, alpha=0.16 * pg)
        ctx.restore()
        polyline(ctx, GROUND, pg, WHITE, 3)
        for k in range(3):
            y = 1066 + k * 6
            pts = [(x, y + 3 * math.sin(x / 12 + t * 2 + k)) for x in range(572, 680, 6)]
            polyline(ctx, pts, pg, BLUE, 2, alpha=0.7)

    # ---- 1 abutments + piers (headstocks, pile caps dashed below the ground)
    c1 = tl.col(1, t)
    for j, (a, b) in enumerate(ABUT):
        k = prog(t, s1 + 0.2 + j * 0.3, 0.7)
        if k <= 0: continue
        fill_poly(ctx, rect_pts(a, BRG_B, b, 760)[:4], BG, 1)
        polyline(ctx, rect_pts(a, 760 - (760 - BRG_B) * k, b, 760), 1, c1, 3)
    for j, x in enumerate(PIERS):
        k = prog(t, s1 + 0.4 + j * 0.35, 1.0)
        if k <= 0: continue
        gy = ground_y(x)
        polyline(ctx, rect_pts(x - 34, gy - 6, x + 34, gy + 34), k, c1, 2, alpha=0.6, dash=[8, 6])
        yt = gy - (gy - BRG_B - 16) * k
        fill_poly(ctx, rect_pts(x - PIER_W, yt, x + PIER_W, gy)[:4], BG, 1)
        polyline(ctx, [(x - PIER_W, gy), (x - PIER_W, yt), (x + PIER_W, yt), (x + PIER_W, gy)], 1, c1, 3)
        kh = prog(t, s1 + 1.2 + j * 0.3, 0.5)
        if kh > 0:
            fill_poly(ctx, rect_pts(x - HEAD_W, BRG_B, x + HEAD_W, BRG_B + 16)[:4], BG, 1)
            polyline(ctx, rect_pts(x - HEAD_W, BRG_B, x + HEAD_W, BRG_B + 16), kh, c1, 3)
    label(ctx, clamp((t - s1 - 0.9) / 0.7), c1, (PIERS[0] + PIER_W, 880), (550, 880), "PIER", a=gone(t, s2 + 0.3))
    label(ctx, clamp((t - s1 - 1.3) / 0.7), c1, (ABUT[0][1], 720), (330, 520), "ABUTMENT", a=gone(t, s2 + 0.3))

    # ---- 2 casting yard: shed (faint, beside the deck), casting bed, steel mould
    c2 = tl.col(2, t)
    ks = prog(t, s2 + 0.2, 1.0)
    if ks > 0:
        ka = 0.45 if t > tl.step_end(2) + 0.6 else 1.0
        polyline(ctx, [(100, GL), (100, 590), (172, 556), (244, 590), (244, GL)], ks, c2, 2, alpha=0.7 * ka)
        fill_poly(ctx, rect_pts(96, DK_B, 236, GL)[:4], BG, 1)
        polyline(ctx, rect_pts(96, DK_B, 236, GL), ks, c2, 2.5)
        draw_concrete(ctx, BED_CONC, WHITE, 0.4 * ks)
    km = prog(t, s2 + 1.0, 0.8)
    if km > 0:
        x0, x1 = YARD
        polyline(ctx, [(x0 - 6, DK_T - 8), (x0 - 6, DK_B + 1), (x1 + 2, DK_B + 1)], km, c2, 2.5, dash=[9, 6])
        polyline(ctx, [(x0 - 6, DK_T - 8), (x1 + 2, DK_T - 8)], km, c2, 1.6, alpha=0.6, dash=[9, 6])
    label(ctx, clamp((t - s2 - 0.8) / 0.7), c2, (150, 575), (220, 470), "CASTING YARD", a=gone(t, s3 + 0.3))
    label(ctx, clamp((t - s2 - 1.6) / 0.7), c2, (150, DK_B + 1), (110, 880), "STEEL MOULD", a=gone(t, s3 + 0.3))

    # ---- the deck: cast segments, pushed forward by the jacks
    F, moving = front(t, tl)
    cl = casts(tl)
    for k, (t0, d, step) in enumerate(cl, 1):
        c = clamp((t - t0) / d)
        if c <= 0: continue
        x1 = F - (k - 1) * L; x0 = x1 - L
        col = mix(tl.col(step, t), ORANGE, moving * 0.85)
        xe = x0 + L * c
        fill_poly(ctx, rect_pts(x0, DK_T, xe, DK_B)[:4], BG, 1)
        fill_poly(ctx, rect_pts(x0, DK_T, xe, DK_B)[:4], BLUE, 0.16)
        ctx.save(); ctx.rectangle(x0, DK_T, xe - x0, DK_B - DK_T); ctx.clip(); ctx.translate(x0, 0)
        draw_concrete(ctx, SEG_CONC, WHITE, 0.55); ctx.restore()
        polyline(ctx, rect_pts(x0, DK_T, x1, DK_B), c, col, 3)

    c3 = tl.col(3, t)
    label(ctx, clamp((t - s3 - 1.4) / 0.7), c3, (190, DK_T + 8), (270, 520), "DECK SEGMENT", a=gone(t, s4 + 0.3))
    label(ctx, clamp((t - s3 - 2.2) / 0.7), c3, (130, DK_B - 10), (110, 880), "CONCRETE", a=gone(t, s4 + 0.3))

    # ---- 4 launching nose (steel truss on the front of the deck); comes off in step 8
    c4 = tl.col(4, t)
    kn = prog(t, s4 + 0.2, 1.2)
    off = prog(t, s8 + 0.3, 0.9)
    if kn > 0 and off < 1:
        ctx.save(); ctx.rectangle(56, 400, CLIP_X1 - 56, 820); ctx.clip()
        ctx.translate(0, -90 * ease(off))
        na = 1 - off
        col = mix(c4, ORANGE, moving * 0.85)
        top = lambda x: DK_T + 4 + (x - F) / NOSE * 20
        xs = [F + NOSE * i / 6 for i in range(7)]
        polyline(ctx, [(F, top(F)), (F + NOSE, top(F + NOSE))], kn, col, 3, alpha=na)
        polyline(ctx, [(F, DK_B - 2), (F + NOSE, DK_B - 2)], kn, col, 3, alpha=na)
        zig = [(x, top(x) if i % 2 == 0 else DK_B - 2) for i, x in enumerate(xs)]
        polyline(ctx, zig, clamp(kn * 1.2 - 0.2), col, 2, alpha=na)
        polyline(ctx, [(F + NOSE, top(F + NOSE)), (F + NOSE, DK_B - 2)], clamp(kn * 2 - 1), col, 3, alpha=na)
        ctx.restore()
        # the nose reaches each pier (and the far abutment) before the deck does: a ring flashes as it arrives
        if off <= 0:
            for tx, x in nose_arrivals(tl):
                kf = clamp((t - tx) / 0.7)
                if 0 < kf < 1:
                    ctx.set_source_rgba(*ORANGE, 1 - kf); ctx.set_line_width(3)
                    ctx.arc(x, DK_B + 4, 10 + 26 * kf, 0, 2 * math.pi); ctx.stroke()
    label(ctx, clamp((t - s4 - 1.2) / 0.7), c4, (F + NOSE * 0.5, DK_T + 10), (420, 520), "LAUNCHING NOSE",
          a=gone(t, s5 + 0.3))

    # ---- 5 sliding bearings on the piers, jacks at the abutment, push arrows
    c5 = tl.col(5, t)
    kb = prog(t, s5 + 0.1, 0.5)
    perm = prog(t, s8 + 1.2, 0.6)
    c8 = tl.col(8, t)
    for x in BRGS:
        if kb <= 0: break
        col = mix(c5, c8, perm)
        fill_poly(ctx, rect_pts(x - 10, DK_B, x + 10, BRG_B)[:4], BG, 1)
        polyline(ctx, rect_pts(x - 10, DK_B, x + 10, BRG_B), kb, col, 2.5)
        if perm <= 0:
            polyline(ctx, [(x - 8, DK_B + 5), (x + 8, DK_B + 5)], kb, col, 1.4, alpha=0.8)
        else:
            polyline(ctx, [(x - 7, DK_B + 3), (x + 7, BRG_B - 3)], perm, col, 1.4, alpha=0.8)
            polyline(ctx, [(x + 7, DK_B + 3), (x - 7, BRG_B - 3)], perm, col, 1.4, alpha=0.8)
    kj = prog(t, s5 + 0.3, 0.5)
    if kj > 0:
        x0, x1 = 196, 232
        fill_poly(ctx, rect_pts(x0, DK_B + 2, x1, GL - 2)[:4], BG, 1)
        polyline(ctx, rect_pts(x0, DK_B + 2, x1, GL - 2), kj, c5, 2.5)
        stroke = 8 * moving * (0.5 + 0.5 * math.sin(t * 9))
        polyline(ctx, [(x1, (DK_B + GL) / 2), (x1 + 4 + stroke, (DK_B + GL) / 2)], kj, c5, 4)
    if moving > 0.5 and t < s8:
        for i in range(3):
            ph = ((t * 1.3) + i / 3) % 1
            x = F - 180 + 150 * ph
            arrow(ctx, x - 40, 600, x, 600, ORANGE, 1, a=0.9 * math.sin(math.pi * ph))
    label(ctx, clamp((t - s5 - 0.6) / 0.7), c5, (210, GL - 4), (110, 940), "HYDRAULIC JACKS", a=gone(t, s6 + 0.3))
    label(ctx, clamp((t - s5 - 1.4) / 0.7), c5, (PIERS[0], DK_B + 5), (550, 880), "SLIDING BEARINGS",
          a=gone(t, s6 + 0.3))

    # ---- 6 / 7 next segments (cast against the last), the nose reaching the piers
    c6 = tl.col(6, t)
    label(ctx, clamp((t - s6 - 0.5) / 0.7), c6, (180, DK_T), (260, 520), "NEXT SEGMENT", a=gone(t, s6 + 1.5))
    label(ctx, clamp((t - s6 - 1.0) / 0.7), c6, (YARD[1], DK_B - 8), (330, 880), "CAST AGAINST LAST",
          a=gone(t, s7 + 0.3))
    c7 = tl.col(7, t)
    label(ctx, clamp((t - s7 - 0.4) / 0.7), c7, (PIERS[1], DK_B + 5), (800, 520), "NOSE LANDS FIRST", anchor="r",
          a=gone(t, s8 + 0.3))

    # ---- 8 nose off, permanent bearings
    label(ctx, clamp((t - s8 - 0.4) / 0.7), c8, (1000, DK_T + 6), (990, 520), "NOSE REMOVED", anchor="r",
          a=gone(t, r0))
    label(ctx, clamp((t - s8 - 1.6) / 0.7), c8, (PIERS[1], BRG_B - 2), (690, 880), "PERMANENT BEARING", anchor="r",
          a=gone(t, r0))

    # ---- result: built here (yard), pushed across (arrow along the whole deck)
    kr = prog(t, r0 + 0.3, 0.6)
    if kr > 0:
        polyline(ctx, rect_pts(YARD[0] - 6, DK_T - 14, YARD[1] + 4, DK_B + 8), kr, ORANGE, 3, dash=[10, 7])
        text(ctx, "BUILT HERE", 177, 540, 28, ORANGE, alpha=kr, bold=True, anchor="c")
    ka = prog(t, r0 + 0.9, 1.0)
    if ka > 0:
        arrow(ctx, 270, 590, 960, 590, ORANGE, ka)
        text(ctx, "PUSHED ACROSS", 615, 570, 28, ORANGE, alpha=clamp(ka * 2 - 1), bold=True, anchor="c")
    pt = prog(t, r0 + 1.6, 0.5)
    if pt > 0:
        text(ctx, "NO SCAFFOLD IN THE VALLEY.", 540, 1205, 30, ORANGE, alpha=pt, bold=True, anchor="c")


# ---------------------------------------------------------------- 3D model (mm): three-span bridge over a valley
def model3d():
    from engine.three_d import box, Part
    P = []
    SPAN, N = 32000, 3
    LEN = SPAN * N
    SOF, DD = 26000, 2600                      # deck soffit level, girder depth
    BANK = SOF - 400                           # approach ground level, both banks
    ZW = 13000                                 # half-width of the ground shown
    g = box(-14000, LEN + 14000, -1500, 0, -ZW, ZW, 0, "ground"); g.base = True; P.append(g)
    P.append(box(LEN / 2 - 7000, LEN / 2 + 7000, 0, 150, -ZW, ZW, 0, "glass"))           # creek
    # the valley sides: a short flat approach on top, then a wedge sloping down to the valley floor
    def wedge(xa, xb, ha, hb):
        return Part([(xa, 0, -ZW), (xb, 0, -ZW), (xb, hb, -ZW), (xa, ha, -ZW),
                     (xa, 0, ZW), (xb, 0, ZW), (xb, hb, ZW), (xa, ha, ZW)], 0, "ground")
    P.append(box(-14000, -2000, 0, BANK, -ZW, ZW, 0, "ground"))
    P.append(wedge(-2000, 15000, BANK, 10))
    P.append(box(LEN + 2000, LEN + 14000, 0, BANK, -ZW, ZW, 0, "ground"))
    P.append(wedge(LEN - 15000, LEN + 2000, 10, BANK))
    # 1 abutments (bank seats)
    for x0, x1 in ((-2000, 0), (LEN, LEN + 2000)):
        P.append(box(x0, x1, BANK - 4000, SOF, -7000, 7000, 1, "concrete"))
    # 2, 3 piers: pile cap, blade pier, headstock
    for j, x in enumerate((SPAN, 2 * SPAN)):
        P.append(box(x - 3500, x + 3500, 0, 1200, -5500, 5500, 2 + j, "concrete"))
        P.append(box(x - 1100, x + 1100, 1200, SOF - 900, -3000, 3000, 2 + j, "concrete"))
        P.append(box(x - 1600, x + 1600, SOF - 900, SOF, -5200, 5200, 2 + j, "concrete"))
    # 4..8 deck segments (box girder + deck slab): the first one cast ends up at the far end
    SEG = LEN / 5
    for k in range(5):
        x1 = LEN - k * SEG; x0 = x1 - SEG
        P.append(box(x0 + 30, x1 - 30, SOF, SOF + DD - 350, -3500, 3500, 4 + k, "precast"))
        P.append(box(x0 + 30, x1 - 30, SOF + DD - 350, SOF + DD, -6500, 6500, 4 + k, "precast"))
    # 9 barriers along both edges
    for z0, z1 in ((-6500, -6000), (6000, 6500)):
        P.append(box(0, LEN, SOF + DD, SOF + DD + 1100, z0, z1, 9, "concrete"))
    cfg = {"target": (LEN / 2, 12000, 0), "yaw": 38, "pitch": 22, "dist": 160000, "scale": 1.2,
           "cy_hook": 1060, "cy_result": 830, "cy_cover": 1010, "cover_scale": 1.0}
    return P, cfg
