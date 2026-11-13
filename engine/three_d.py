"""Tiny 3D renderer for blueprint-style models: dark solid faces, white edges, z-buffered.

Units are mm. Y is up, X along the main run, Z towards the viewer.
A model is a list of Part(verts8, order, kind). Use box() / member() to build them.

Occlusion is a per-pixel depth test (z-buffer), so overlapping members never bleed
through each other. Everything is rasterised into a supersampled numpy layer and then
composited onto the cairo context, so the look (solid faces + white edges) is unchanged.
"""
import math
import numpy as np
import cairo
from engine.blueprint import BG, BLUE, WHITE, ORANGE, mix, clamp, ease, W, H

# vertex order: 0-3 one end (or bottom), 4-7 the other
FACES = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]


class Part:
    def __init__(self, verts, order=0, kind="timber", base=False):
        self.v, self.order, self.kind, self.base = verts, order, kind, base
        self.c = tuple(sum(p[i] for p in verts) / 8 for i in range(3))


def box(x0, x1, y0, y1, z0, z1, order=0, kind="timber"):
    return Part([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                 (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], order, kind)


def member(p0, p1, depth, z0, z1, order=0, kind="timber"):
    """Straight member in the XY plane from p0 to p1 (centreline), `depth` wide, spanning z0..z1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * depth / 2, dx / L * depth / 2
    a = (p0[0] + nx, p0[1] + ny); b = (p1[0] + nx, p1[1] + ny)
    c = (p1[0] - nx, p1[1] - ny); d = (p0[0] - nx, p0[1] - ny)
    return Part([(d[0], d[1], z0), (c[0], c[1], z0), (b[0], b[1], z0), (a[0], a[1], z0),
                 (d[0], d[1], z1), (c[0], c[1], z1), (b[0], b[1], z1), (a[0], a[1], z1)], order, kind)


def member3d(p0, p1, w, h, order=0, kind="steel"):
    """Straight member between two 3D points with a w x h rectangular section."""
    d = _norm(_sub(p1, p0))
    up = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
    u = _norm(_cross(d, up)); v = _norm(_cross(u, d))
    def ring(p):
        return [tuple(p[i] + s1 * u[i] * w / 2 + s2 * v[i] * h / 2 for i in range(3))
                for s1, s2 in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return Part(ring(p0) + ring(p1), order, kind)


class Camera:
    def __init__(self, target, yaw, pitch, dist, scale, cx, cy, fov=900.0):
        self.t, self.dist, self.scale, self.cx, self.cy, self.f = target, dist, scale, cx, cy, fov
        self.cy_, self.sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        self.cp, self.sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def view(self, p):
        x, y, z = p[0] - self.t[0], p[1] - self.t[1], p[2] - self.t[2]
        x, z = x * self.cy_ + z * self.sy, -x * self.sy + z * self.cy_          # yaw about Y
        y, z = y * self.cp - z * self.sp, y * self.sp + z * self.cp              # pitch about X
        return x, y, self.dist - z                                             # camera looks down -z

    def proj(self, v):
        k = self.f / max(v[2], 1e-3) * self.scale
        return self.cx + v[0] * k, self.cy - v[1] * k


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _norm(a):
    l = math.sqrt(_dot(a, a)) or 1
    return (a[0] / l, a[1] / l, a[2] / l)


LIGHT_V = _norm((-0.4, 0.8, -0.5))   # in view space (depth axis points away)
FILL = {"timber": 0.10, "concrete": 0.05, "steel": 0.16, "ground": 0.03, "eps": 0.22, "brick": 0.12}


SS = 2                               # supersample factor for the 3D layer (anti-aliasing)
_TRIS = [(0, 1, 2), (0, 2, 3)]       # split each quad face into two triangles
_EDGES = sorted({tuple(sorted((f[k], f[(k + 1) % 4]))) for f in FACES for k in range(4)})  # 12 unique box edges


def _tri(pcol, acov, zb, P, D, color, sa):
    """Rasterise one triangle (premultiplied over-composite) with a per-pixel depth test.
    P = 3 screen points, D = 3 view depths (smaller = nearer), sa = source alpha."""
    (x0, y0), (x1, y1), (x2, y2) = P
    Hd, Wd = zb.shape
    ix0 = max(0, int(math.floor(min(x0, x1, x2)))); ix1 = min(Wd, int(math.ceil(max(x0, x1, x2))) + 1)
    iy0 = max(0, int(math.floor(min(y0, y1, y2)))); iy1 = min(Hd, int(math.ceil(max(y0, y1, y2))) + 1)
    if ix1 <= ix0 or iy1 <= iy0: return
    denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(denom) < 1e-6: return
    gx = (np.arange(ix0, ix1) + 0.5)[None, :]; gy = (np.arange(iy0, iy1) + 0.5)[:, None]
    l0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / denom
    l1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / denom
    l2 = 1.0 - l0 - l1
    depth = l0 * D[0] + l1 * D[1] + l2 * D[2]
    zbs = zb[iy0:iy1, ix0:ix1]
    mask = (l0 >= 0) & (l1 >= 0) & (l2 >= 0) & (depth < zbs)
    if not mask.any(): return
    np.copyto(zbs, depth, where=mask)
    saf = np.where(mask, sa, 0.0).astype(np.float32)
    sub = pcol[iy0:iy1, ix0:ix1]; asb = acov[iy0:iy1, ix0:ix1]
    om = (1.0 - saf)[..., None]
    sub *= om; sub += np.asarray(color, np.float32) * saf[..., None]
    asb *= (1.0 - saf); asb += saf


def _seg(pcol, acov, zb, A, B, dA, dB, color, pa, hw):
    """Draw an anti-aliased, depth-tested line segment (hidden-line removal) over the fills."""
    Hd, Wd = zb.shape
    ax, ay = A; bx, by = B
    ix0 = max(0, int(math.floor(min(ax, bx) - hw - 1))); ix1 = min(Wd, int(math.ceil(max(ax, bx) + hw + 1)))
    iy0 = max(0, int(math.floor(min(ay, by) - hw - 1))); iy1 = min(Hd, int(math.ceil(max(ay, by) + hw + 1)))
    if ix1 <= ix0 or iy1 <= iy0: return
    gx = (np.arange(ix0, ix1) + 0.5)[None, :]; gy = (np.arange(iy0, iy1) + 0.5)[:, None]
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = ((gx - ax) * dx + (gy - ay) * dy) / L2 if L2 > 1e-6 else np.zeros_like(gx)
    t = np.clip(t, 0.0, 1.0)
    cx = ax + t * dx; cy = ay + t * dy
    dist = np.hypot(gx - cx, gy - cy)
    cov = np.clip(hw + 0.5 - dist, 0.0, 1.0)
    depth = dA + t * (dB - dA)
    zbs = zb[iy0:iy1, ix0:ix1]
    vis = (cov > 0) & (depth <= zbs + (0.0025 * depth + 2.0))
    saf = np.where(vis, pa * cov, 0.0).astype(np.float32)
    sub = pcol[iy0:iy1, ix0:ix1]; asb = acov[iy0:iy1, ix0:ix1]
    om = (1.0 - saf)[..., None]
    sub *= om; sub += np.asarray(color, np.float32) * saf[..., None]
    asb *= (1.0 - saf); asb += saf


def render(ctx, parts, cam, alpha=1.0, highlight=None, appear=None):
    """Draw parts into a z-buffered layer, then composite onto ctx with `alpha`.
    appear(part) -> 0..1 controls build-up (drop-in + fade). highlight(part) -> True paints edges orange."""
    # gather visible parts; composite far -> near so build-up fades blend correctly
    vis_parts = []
    for part in parts:
        a = 1.0 if appear is None else appear(part)
        if a <= 0: continue
        drop = (1 - ease(a)) * 400                                   # members drop into place
        vv = [cam.view((p[0], p[1] + drop, p[2])) for p in part.v]  # view space: x, y, depth (+ = away)
        if min(v[2] for v in vv) <= 1: continue
        sp = [cam.proj(v) for v in vv]                               # screen coords (1x)
        cz = sum(v[2] for v in vv) / 8
        vis_parts.append((cz, part, vv, sp, clamp(a)))
    if not vis_parts: return
    vis_parts.sort(key=lambda p: (not p[1].base, -p[0]))             # ground first, then far to near

    # only rasterise the model's screen bounding box (the layer is mostly empty otherwise)
    allx = [x for _, _, _, sp, _ in vis_parts for x, y in sp]
    ally = [y for _, _, _, sp, _ in vis_parts for x, y in sp]
    bx0 = max(0, int(math.floor(min(allx))) - 2); bx1 = min(W, int(math.ceil(max(allx))) + 2)
    by0 = max(0, int(math.floor(min(ally))) - 2); by1 = min(H, int(math.ceil(max(ally))) + 2)
    bw, bh = bx1 - bx0, by1 - by0
    if bw <= 0 or bh <= 0: return
    Hd, Wd = bh * SS, bw * SS
    pcol = np.zeros((Hd, Wd, 3), np.float32)      # premultiplied colour
    acov = np.zeros((Hd, Wd), np.float32)         # coverage / alpha
    zb = np.full((Hd, Wd), np.inf, np.float32)    # depth buffer (smaller = nearer)
    vis_parts = [(cz, part, vv, [((x - bx0) * SS, (y - by0) * SS) for x, y in sp], a)
                 for cz, part, vv, sp, a in vis_parts]

    for cz, part, vv, sp, a in vis_parts:
        cv = tuple(sum(v[j] for v in vv) / 8 for j in range(3))
        for f in FACES:
            vf = [vv[i] for i in f]
            fc = tuple(sum(v[j] for v in vf) / 4 for j in range(3))
            n = _norm(_cross(_sub(vf[1], vf[0]), _sub(vf[3], vf[0])))
            if _dot(n, _sub(fc, cv)) < 0: n = (-n[0], -n[1], -n[2])   # outward
            if _dot(n, fc) >= 0: continue                              # faces away from the camera
            shade = 0.35 + 0.65 * max(0.0, _dot(n, LIGHT_V))           # light from upper-left-front
            col = mix(BG, BLUE, FILL.get(part.kind, 0.1) + 0.25 * shade)
            P = [sp[i] for i in f]; D = [vv[i][2] for i in f]
            for i0, i1, i2 in _TRIS:
                _tri(pcol, acov, zb, [P[i0], P[i1], P[i2]], [D[i0], D[i1], D[i2]], col, a)

    # edges (hidden-line removed against the completed depth buffer), on top of the fills.
    # Every box edge is drawn and the per-pixel depth test hides the ones behind a surface.
    for cz, part, vv, sp, a in vis_parts:
        hot = highlight and highlight(part)
        edge = ORANGE if hot else WHITE
        ea = a * (0.95 if hot else 0.8)
        ew = (1.6 if part.kind != "ground" else 1.0) * SS / 2.0
        for i, j in _EDGES:
            _seg(pcol, acov, zb, sp[i], sp[j], vv[i][2], vv[j][2], edge, ea, ew)

    # downsample SS -> 1x (box filter) and composite the bounding box onto the cairo context
    pcol = pcol.reshape(bh, SS, bw, SS, 3).mean((1, 3))
    acov = acov.reshape(bh, SS, bw, SS).mean((1, 3))
    buf = np.empty((bh, bw, 4), np.uint8)
    buf[..., 0] = np.clip(pcol[..., 2] * 255, 0, 255)   # B (cairo ARGB32 is premultiplied BGRA, little-endian)
    buf[..., 1] = np.clip(pcol[..., 1] * 255, 0, 255)   # G
    buf[..., 2] = np.clip(pcol[..., 0] * 255, 0, 255)   # R
    buf[..., 3] = np.clip(acov * 255, 0, 255)           # A
    buf = np.ascontiguousarray(buf)
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, bw)
    surf = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, bw, bh, stride)
    ctx.save()
    ctx.set_source_surface(surf, bx0, by0)
    ctx.paint_with_alpha(clamp(alpha))
    ctx.restore()
    surf.finish()


def orbit_camera(model_cfg, yaw, pitch=None):
    m = model_cfg
    return Camera(m["target"], yaw, m.get("pitch", 20) if pitch is None else pitch, m["dist"], m["scale"], m.get("cx", 540), m["cy"])
