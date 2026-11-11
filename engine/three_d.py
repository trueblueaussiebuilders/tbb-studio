"""Tiny 3D renderer for blueprint-style models: dark solid faces, white edges, painter's algorithm.

Units are mm. Y is up, X along the main run, Z towards the viewer.
A model is a list of Part(verts8, order, kind). Use box() / member() to build them.
"""
import math
from engine.blueprint import BG, BLUE, WHITE, ORANGE, mix, clamp, ease

# vertex order: 0-3 one end (or bottom), 4-7 the other
FACES = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]


class Part:
    def __init__(self, verts, order=0, kind="timber"):
        self.v, self.order, self.kind = verts, order, kind
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
FILL = {"timber": 0.10, "concrete": 0.05, "steel": 0.16, "ground": 0.03}


def render(ctx, parts, cam, alpha=1.0, highlight=None, appear=None):
    """Draw parts. appear(part) -> 0..1 controls build-up (drop-in + fade). highlight(part) -> True paints edges orange."""
    polys = []
    for part in parts:
        a = 1.0 if appear is None else appear(part)
        if a <= 0: continue
        drop = (1 - ease(a)) * 400                                   # members drop into place
        vv = [cam.view((p[0], p[1] + drop, p[2])) for p in part.v]  # view space: x, y, depth (+ = away)
        if min(v[2] for v in vv) <= 1: continue
        cv = tuple(sum(v[j] for v in vv) / 8 for j in range(3))
        for f in FACES:
            vf = [vv[i] for i in f]
            fc = tuple(sum(v[j] for v in vf) / 4 for j in range(3))
            n = _norm(_cross(_sub(vf[1], vf[0]), _sub(vf[3], vf[0])))
            if _dot(n, _sub(fc, cv)) < 0: n = (-n[0], -n[1], -n[2])   # outward
            if _dot(n, fc) >= 0: continue                              # faces away from the camera
            # lighting in view space: light from upper-left-front
            shade = 0.35 + 0.65 * max(0.0, _dot(n, LIGHT_V))
            polys.append((fc[2], [cam.proj(v) for v in vf], shade, part, a))
    polys.sort(key=lambda p: -p[0])                                   # far first
    for depth, pts, shade, part, a in polys:
        col = mix(BG, BLUE, FILL.get(part.kind, 0.1) + 0.25 * shade)
        ctx.new_path(); ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        ctx.close_path()
        ctx.set_source_rgba(*col, alpha * a); ctx.fill_preserve()
        hot = highlight(part) if highlight else False
        ctx.set_source_rgba(*(ORANGE if hot else WHITE), alpha * a * (0.95 if hot else 0.8))
        ctx.set_line_width(1.6 if part.kind != "ground" else 1.0); ctx.stroke()


def orbit_camera(model_cfg, yaw, pitch=None):
    m = model_cfg
    return Camera(m["target"], yaw, m.get("pitch", 20) if pitch is None else pitch, m["dist"], m["scale"], m.get("cx", 540), m["cy"])
