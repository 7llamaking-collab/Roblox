"""Low-poly modelling toolkit on top of Blender's bmesh.

A ``Builder`` collects primitives (rounded boxes, cylinders, spheres, lathes,
swept tubes, extruded outlines, tori...) into one mesh. Every face remembers a
palette colour and a rig group, so ``finish()`` can UV-map the mesh onto the
shared palette atlas and (for animals) skin it to bones.

Coordinates are studs: 1 Blender unit = 1 Roblox stud. Z is up, models face -Y.
"""
import math
from contextlib import contextmanager

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

from . import palette

DEFAULT_SMOOTH_ANGLE = 40.0

# Global look. "blocky" (default) matches AnimalBundle: spheres become chamfered
# cubes, tubes get square sections, curved shapes use few sides and everything is
# flat shaded. "round" gives the softer smooth low-poly look.
STYLE = dict(name="blocky", blocky=True, flat=True, max_seg=8, chamfer=0.2)


def set_style(name):
    if name == "round":
        STYLE.update(name="round", blocky=False, flat=False, max_seg=64)
    else:
        STYLE.update(name="blocky", blocky=True, flat=True, max_seg=8)


def _vec3(s):
    if isinstance(s, (int, float)):
        return Vector((s, s, s))
    return Vector(s)


def _matrix(loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    return Matrix.LocRotScale(Vector(loc), Euler([math.radians(a) for a in rot], "XYZ"), _vec3(scale))


# ---------------------------------------------------------------------------
# colour helpers usable as ``color=`` callables: f(center, normal) -> name
# ---------------------------------------------------------------------------
def by_height(*stops):
    """by_height('a', 0.5, 'b', 1.2, 'c'): faces below z=0.5 get 'a', etc."""
    cols = stops[0::2]
    zs = stops[1::2]

    def f(c, n):
        for z, col in zip(zs, cols):
            if c.z < z:
                return col
        return cols[-1]
    return f


def by_normal(top, side, bottom=None, thresh=0.5):
    def f(c, n):
        if n.z > thresh:
            return top
        if bottom is not None and n.z < -thresh:
            return bottom
        return side
    return f


def by_axis(axis, *stops):
    """Like by_height but along 'x', 'y' or 'z' (world, before mirroring)."""
    cols = stops[0::2]
    vals = stops[1::2]
    idx = "xyz".index(axis)

    def f(c, n):
        for v, col in zip(vals, cols):
            if c[idx] < v:
                return col
        return cols[-1]
    return f


RAINBOW = ["rb_red", "rb_orange", "rb_yellow", "rb_green", "rb_cyan", "rb_blue", "rb_purple", "rb_pink"]


def rainbow(axis="z", lo=0.0, hi=1.0, cols=RAINBOW):
    idx = "xyz".index(axis)

    def f(c, n):
        t = (c[idx] - lo) / max(1e-6, hi - lo)
        i = int(max(0, min(len(cols) - 1, t * len(cols))))
        return cols[i]
    return f


def checker(a, b, size=1.0):
    def f(c, n):
        k = int(math.floor(c.x / size) + math.floor(c.y / size) + math.floor(c.z / size))
        return a if k % 2 == 0 else b
    return f


# ---------------------------------------------------------------------------
# deformers usable as ``deform=``: f(co: Vector) -> Vector (local space)
# ---------------------------------------------------------------------------
def taper(z0, z1, s0, s1, axes="xy"):
    def f(co):
        t = 0.0 if z1 == z0 else max(0.0, min(1.0, (co.z - z0) / (z1 - z0)))
        s = s0 + (s1 - s0) * t
        co = co.copy()
        if "x" in axes:
            co.x *= s
        if "y" in axes:
            co.y *= s
        return co
    return f


def jitter(amount, seed=1, axes=(1, 1, 1)):
    def h(x, y, z, k):
        n = math.sin(x * 12.9898 + y * 78.233 + z * 37.719 + k * 11.13 + seed * 3.7) * 43758.5453
        return (n - math.floor(n)) * 2.0 - 1.0

    def f(co):
        k = (round(co.x, 4), round(co.y, 4), round(co.z, 4))
        return Vector((co.x + h(*k, 1) * amount * axes[0],
                       co.y + h(*k, 2) * amount * axes[1],
                       co.z + h(*k, 3) * amount * axes[2]))
    return f


def bend_x(radius):
    """Bend geometry along +Z around the Y axis (curls towards +X)."""
    def f(co):
        a = co.z / radius
        r = radius - co.x
        return Vector((radius - r * math.cos(a), co.y, r * math.sin(a)))
    return f


def chain(*fs):
    def f(co):
        for g in fs:
            co = g(co)
        return co
    return f


# ---------------------------------------------------------------------------
class Builder:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.lay_col = self.bm.faces.layers.int.new("pal")
        self.lay_grp = self.bm.faces.layers.int.new("grp")
        self.groups = ["Root"]
        self.bones = {}          # name -> dict(head, tail, parent)
        self._grp = 0
        self.meta = {}

    # -- rig groups ---------------------------------------------------------
    def bone(self, name, head, tail, parent=None):
        """Declare a bone; faces built inside ``with m.group(name)`` follow it."""
        if name not in self.groups:
            self.groups.append(name)
        self.bones[name] = dict(head=Vector(head), tail=Vector(tail), parent=parent)
        return name

    @contextmanager
    def group(self, name):
        prev = self._grp
        if name not in self.groups:
            self.groups.append(name)
        self._grp = self.groups.index(name)
        try:
            yield
        finally:
            self._grp = prev

    # -- core commit ----------------------------------------------------------
    def _commit(self, tmp, color, smooth=True, angle=DEFAULT_SMOOTH_ANGLE, loc=(0, 0, 0),
                rot=(0, 0, 0), scale=1.0, mirror=False, deform=None, recalc=True,
                pre=None, group=None, cuts=None):
        if deform is not None:
            for v in tmp.verts:
                v.co = deform(v.co.copy())
        bmesh.ops.transform(tmp, matrix=_matrix(loc, rot, scale), verts=tmp.verts)
        if pre is not None:
            bmesh.ops.transform(tmp, matrix=pre, verts=tmp.verts)
        if cuts:
            self._cut(tmp, cuts)
        if STYLE["flat"]:
            smooth = False
        if recalc:
            bmesh.ops.recalc_face_normals(tmp, faces=tmp.faces)
        tmp.normal_update()
        grp = self._grp if group is None else self.groups.index(group)
        passes = [False, True] if mirror else [False]
        out_faces = []
        for flip in passes:
            if flip and isinstance(mirror, str):
                grp_m = self.groups.index(mirror)
            else:
                grp_m = grp
            vmap = {}
            for v in tmp.verts:
                co = v.co.copy()
                if flip:
                    co.x = -co.x
                vmap[v] = self.bm.verts.new(co)
            for f in tmp.faces:
                vs = [vmap[v] for v in f.verts]
                if flip:
                    vs.reverse()
                try:
                    nf = self.bm.faces.new(vs)
                except ValueError:
                    continue
                c = f.calc_center_median()
                n = f.normal.copy()
                if flip:
                    c.x, n.x = -c.x, -n.x
                cname = color(c, n) if callable(color) else color
                nf[self.lay_col] = palette.INDEX[cname]
                nf[self.lay_grp] = grp_m
                nf.smooth = smooth
                out_faces.append(nf)
            thr = math.radians(angle)
            for e in tmp.edges:
                if len(e.link_faces) != 2:
                    continue
                ne = self.bm.edges.get([vmap[e.verts[0]], vmap[e.verts[1]]])
                if ne is not None:
                    ne.smooth = smooth and e.calc_face_angle(math.pi) < thr
        tmp.free()
        return out_faces

    @staticmethod
    def _cut(tmp, cuts):
        """Slice geometry with planes so large faces can carry colour bands.

        cuts: {'z': [0.5, 1.0]} (world values) or {'z': 0.25} (every 0.25 studs).
        """
        for axis, vals in cuts.items():
            i = "xyz".index(axis)
            if isinstance(vals, (int, float)):
                lo = min(v.co[i] for v in tmp.verts)
                hi = max(v.co[i] for v in tmp.verts)
                step = float(vals)
                k = math.floor(lo / step) + 1
                vals = []
                while k * step < hi - 1e-4:
                    vals.append(k * step)
                    k += 1
            no = Vector((0, 0, 0))
            no[i] = 1.0
            for val in vals:
                co = Vector((0, 0, 0))
                co[i] = val
                geom = list(tmp.verts) + list(tmp.edges) + list(tmp.faces)
                bmesh.ops.bisect_plane(tmp, geom=geom, dist=1e-5, plane_co=co, plane_no=no)

    @staticmethod
    def _bevel(tmp, amount, segments, edges=None, min_angle=None):
        if amount <= 0:
            return
        if edges is None:
            edges = list(tmp.edges)
        if min_angle is not None:
            tmp.normal_update()
            edges = [e for e in edges if len(e.link_faces) == 2 and
                     e.calc_face_angle(0) > math.radians(min_angle)]
        if not edges:
            return
        bmesh.ops.bevel(tmp, geom=edges, offset=amount, offset_type="OFFSET", segments=segments,
                        profile=0.5, affect="EDGES", clamp_overlap=True)

    # -- primitives ------------------------------------------------------------
    def box(self, size=(1, 1, 1), color="white", bevel=0.0, bseg=2, **kw):
        """Axis-aligned box centred on ``loc``; ``bevel`` rounds every edge."""
        tmp = bmesh.new()
        bmesh.ops.create_cube(tmp, size=1.0)
        s = _vec3(size)
        for v in tmp.verts:
            v.co = Vector((v.co.x * s.x, v.co.y * s.y, v.co.z * s.z))
        self._bevel(tmp, min(bevel, min(s) * 0.49), 1 if STYLE["blocky"] else bseg)
        kw.setdefault("angle", 50)
        return self._commit(tmp, color, **kw)

    def cyl(self, r=0.5, h=1.0, seg=12, color="white", r2=None, bevel=0.0, bseg=2,
            caps=True, **kw):
        """Cylinder along Z centred on ``loc``; r2 = top radius (for frustums)."""
        seg = min(seg, STYLE["max_seg"])
        if STYLE["blocky"]:
            bseg = 1
        tmp = bmesh.new()
        bmesh.ops.create_cone(tmp, cap_ends=caps, cap_tris=False, segments=seg, radius1=r,
                              radius2=r if r2 is None else r2, depth=h)
        if bevel > 0 and caps:
            self._bevel(tmp, min(bevel, h * 0.45, r * 0.45), bseg, min_angle=60)
        return self._commit(tmp, color, recalc=caps, **kw)

    def sphere(self, r=0.5, seg=12, rings=8, color="white", round=False, **kw):
        tmp = bmesh.new()
        if STYLE["blocky"] and not round:
            bmesh.ops.create_cube(tmp, size=2 * r)
            self._bevel(tmp, r * STYLE["chamfer"], 1)
        else:
            seg = min(seg, STYLE["max_seg"] + 2)
            rings = min(rings, STYLE["max_seg"] - 2) if STYLE["blocky"] else rings
            bmesh.ops.create_uvsphere(tmp, u_segments=seg, v_segments=rings, radius=r)
        return self._commit(tmp, color, **kw)

    def ico(self, r=0.5, sub=1, color="white", **kw):
        if STYLE["blocky"]:
            sub = min(sub, 1)
        tmp = bmesh.new()
        bmesh.ops.create_icosphere(tmp, subdivisions=sub, radius=r)
        kw.setdefault("angle", 30)
        return self._commit(tmp, color, **kw)

    def cone(self, r=0.5, h=1.0, seg=12, color="white", **kw):
        """Cone with base at z=0 and tip at z=h (before transform)."""
        return self.lathe([(r, 0), (0, h)], seg=seg, color=color, **kw)

    def lathe(self, profile, seg=12, color="white", caps=True, **kw):
        """Spin a (radius, z) profile around Z. radius 0 makes a pole."""
        if STYLE["blocky"] and seg > 4:
            seg = min(seg, STYLE["max_seg"])
        tmp = bmesh.new()
        rings = []
        for r, z in profile:
            if r <= 1e-6:
                rings.append([tmp.verts.new((0, 0, z))])
            else:
                rings.append([tmp.verts.new((r * math.cos(2 * math.pi * j / seg),
                                             r * math.sin(2 * math.pi * j / seg), z))
                              for j in range(seg)])
        for a, b in zip(rings[:-1], rings[1:]):
            for j in range(seg):
                j1 = (j + 1) % seg
                va = [a[0], a[0]] if len(a) == 1 else [a[j], a[j1]]
                vb = [b[0], b[0]] if len(b) == 1 else [b[j1], b[j]]
                quad = va + vb
                uniq = []
                for v in quad:
                    if v not in uniq:
                        uniq.append(v)
                if len(uniq) >= 3:
                    tmp.faces.new(uniq)
        if caps:
            if len(rings[0]) > 1:
                tmp.faces.new(list(reversed(rings[0])))
            if len(rings[-1]) > 1:
                tmp.faces.new(rings[-1])
        closed = caps or (len(rings[0]) == 1 and len(rings[-1]) == 1)
        return self._commit(tmp, color, recalc=closed, **kw)

    def tube(self, points, radii, seg=8, color="white", caps=True, up=(0, 0, 1), twist=0.0, **kw):
        """Sweep an (elliptical) ring along a polyline.

        radii: one value per point, either r or (r_side, r_up). A radius of 0 at an
        end makes a pointed tip.
        """
        pts = [Vector(p) for p in points]
        n = len(pts)
        rads = [(r, r) if isinstance(r, (int, float)) else tuple(r) for r in radii]
        square = STYLE["blocky"] and seg > 4
        if square:
            # square cross-section with flat top: corners at 45 degrees
            seg = 4
            rads = [(a * 1.25, b * 1.25) for a, b in rads]
        upv = Vector(up)
        tmp = bmesh.new()
        rings = []
        prev_side = None
        for i, p in enumerate(pts):
            if i == 0:
                t = pts[1] - pts[0]
            elif i == n - 1:
                t = pts[-1] - pts[-2]
            else:
                t = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
            t.normalize()
            side = t.cross(upv)
            if side.length < 1e-4:
                side = prev_side if prev_side is not None else t.orthogonal()
            side.normalize()
            if prev_side is not None and side.dot(prev_side) < 0:
                side = -side
            prev_side = side
            u = side.cross(t).normalized()
            rx, ry = rads[i]
            if rx <= 1e-6 and ry <= 1e-6:
                rings.append([tmp.verts.new(p)])
                continue
            ring = []
            for j in range(seg):
                a = 2 * math.pi * j / seg + math.radians(twist) * i + (math.pi / 4 if square else 0.0)
                ring.append(tmp.verts.new(p + side * (rx * math.cos(a)) + u * (ry * math.sin(a))))
            rings.append(ring)
        for a, b in zip(rings[:-1], rings[1:]):
            for j in range(seg):
                j1 = (j + 1) % seg
                va = [a[0], a[0]] if len(a) == 1 else [a[j], a[j1]]
                vb = [b[0], b[0]] if len(b) == 1 else [b[j1], b[j]]
                uniq = []
                for v in va + vb:
                    if v not in uniq:
                        uniq.append(v)
                if len(uniq) >= 3:
                    tmp.faces.new(uniq)
        if caps:
            if len(rings[0]) > 1:
                tmp.faces.new(list(reversed(rings[0])))
            if len(rings[-1]) > 1:
                tmp.faces.new(rings[-1])
        return self._commit(tmp, color, **kw)

    def prism(self, outline, depth=0.2, color="white", bevel=0.0, bseg=2, taper_to=None, **kw):
        """Extrude a 2D outline (XY, counter-clockwise) along Z, centred.

        taper_to: optional scale for the +Z face (makes wedge/blade profiles).
        """
        tmp = bmesh.new()
        lo = [tmp.verts.new((x, y, -depth / 2)) for x, y in outline]
        s = 1.0 if taper_to is None else taper_to
        hi = [tmp.verts.new((x * s, y * s, depth / 2)) for x, y in outline]
        tmp.faces.new(list(reversed(lo)))
        tmp.faces.new(hi)
        k = len(outline)
        for i in range(k):
            i1 = (i + 1) % k
            tmp.faces.new([lo[i], lo[i1], hi[i1], hi[i]])
        if bevel > 0:
            tmp.normal_update()
            rim = [e for e in tmp.edges if any(len(f.verts) > 4 or f.normal.z ** 2 > 0.9
                                               for f in e.link_faces)
                   and not all(f.normal.z ** 2 > 0.9 for f in e.link_faces)]
            self._bevel(tmp, bevel, bseg, edges=rim)
        kw.setdefault("angle", 50)
        return self._commit(tmp, color, **kw)

    def torus(self, R=0.5, r=0.15, seg=16, rseg=8, color="white", arc=360.0, **kw):
        """Torus in the XY plane; ``arc`` < 360 makes an open ring (handles)."""
        if STYLE["blocky"]:
            seg = max(4, min(seg, int(STYLE["max_seg"] * max(arc, 90) / 360 + 0.5)))
            rseg = 4
        tmp = bmesh.new()
        closed = arc >= 359.9
        nseg = seg if closed else seg + 1
        rings = []
        for i in range(nseg):
            a = math.radians(arc) * i / seg
            c = Vector((R * math.cos(a), R * math.sin(a), 0))
            d = Vector((math.cos(a), math.sin(a), 0))
            rings.append([tmp.verts.new(c + d * (r * math.cos(2 * math.pi * j / rseg)) +
                                        Vector((0, 0, r * math.sin(2 * math.pi * j / rseg))))
                          for j in range(rseg)])
        count = seg if closed else seg
        for i in range(count):
            a, b = rings[i], rings[(i + 1) % nseg]
            for j in range(rseg):
                j1 = (j + 1) % rseg
                tmp.faces.new([a[j], a[j1], b[j1], b[j]])
        if not closed:
            tmp.faces.new(list(reversed(rings[0])))
            tmp.faces.new(rings[-1])
        return self._commit(tmp, color, **kw)

    def wedge(self, size=(1, 1, 1), color="white", **kw):
        """Triangular prism: full height at -Y, zero at +Y (a ramp)."""
        x, y, z = size
        pts = [(-y / 2, -z / 2), (y / 2, -z / 2), (-y / 2, z / 2)]
        tmp = bmesh.new()
        lo = [tmp.verts.new((-x / 2, a, b)) for a, b in pts]
        hi = [tmp.verts.new((x / 2, a, b)) for a, b in pts]
        tmp.faces.new(list(reversed(lo)))
        tmp.faces.new(hi)
        for i in range(3):
            i1 = (i + 1) % 3
            tmp.faces.new([lo[i], lo[i1], hi[i1], hi[i]])
        kw.setdefault("smooth", False)
        return self._commit(tmp, color, **kw)

    def panel(self, points, thick=0.06, color="white", **kw):
        """Thin sheet through arbitrary 3D points (wing membranes, feathers, fins)."""
        tmp = bmesh.new()
        pts = [Vector(p) for p in points]
        n = Vector((0, 0, 0))
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
        n = n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))
        top = [tmp.verts.new(p + n * thick / 2) for p in pts]
        bot = [tmp.verts.new(p - n * thick / 2) for p in pts]
        tmp.faces.new(top)
        tmp.faces.new(list(reversed(bot)))
        k = len(pts)
        for i in range(k):
            i1 = (i + 1) % k
            tmp.faces.new([bot[i], bot[i1], top[i1], top[i]])
        kw.setdefault("smooth", False)
        return self._commit(tmp, color, **kw)

    def pyramid(self, w=0.3, h=0.5, color="white", **kw):
        """Square pyramid, base centred at the origin, tip at +Z (before rot)."""
        r = w / math.sqrt(2)
        prev = kw.pop("deform", None)
        spin = Matrix.Rotation(math.pi / 4, 3, "Z")
        kw["deform"] = (lambda co: prev(spin @ co)) if prev else (lambda co: spin @ co)
        kw.setdefault("smooth", False)
        return self.lathe([(r, 0), (0, h)], seg=4, color=color, **kw)

    def gem(self, r=0.5, h=1.0, seg=6, crown=0.35, table=0.55, color="diamond", **kw):
        """Faceted crystal/gem: pointed bottom, flat table top."""
        prof = [(0, 0), (r, h * (1 - crown)), (r * table, h)]
        kw.setdefault("smooth", False)
        return self.lathe(prof, seg=seg, color=color, **kw)

    def crystal(self, r=0.3, h=1.2, seg=6, tip=0.25, color="amethyst", **kw):
        """Hexagonal crystal shard with pointed tip (base at z=0)."""
        prof = [(r * 0.8, 0), (r, h * 0.12), (r, h * (1 - tip)), (0, h)]
        kw.setdefault("smooth", False)
        return self.lathe(prof, seg=seg, color=color, **kw)

    # -- composite helpers -------------------------------------------------------
    def eye(self, pos, r=0.12, color="eye_black", shine=True, look=(0, -1, 0), **kw):
        """Eye. Blocky: square pixel eye (black square + white highlight square)
        centred on ``pos`` and facing ``look``; round: glossy sphere."""
        if STYLE["blocky"]:
            L = Vector(look)
            L.z = 0
            if L.length < 1e-6:
                L = Vector((0, -1, 0))
            L.normalize()
            yaw = math.degrees(math.atan2(L.x, -L.y))
            rz = Matrix.Rotation(math.radians(yaw), 3, "Z")
            p = Vector(pos)
            self.box((2 * r, r * 0.6, 2 * r), color=color, loc=p, rot=(0, 0, yaw), **kw)
            if shine:
                side = 1.0 if p.x >= 0 else -1.0
                off = rz @ Vector((side * r * 0.42, -r * 0.33, r * 0.42))
                self.box((r * 0.8, r * 0.1, r * 0.8), color="eye_white", loc=p + off, rot=(0, 0, yaw), **kw)
            return
        self.sphere(r=r, seg=10, rings=6, color=color, loc=pos, **kw)
        if shine:
            L = Vector(look).normalized()
            p = Vector(pos) + L * (r * 0.72) + Vector((-r * 0.35, 0, r * 0.4))
            mir = kw.get("mirror", False)
            self.sphere(r=r * 0.32, seg=6, rings=4, color="eye_white", loc=p, mirror=mir,
                        **{k: v for k, v in kw.items() if k not in ("mirror",)})

    def leaf(self, length=1.0, width=0.45, thick=0.06, color="leaf", **kw):
        """Pointed leaf lying along +Y from the origin (flat on XY)."""
        pts = []
        n = 6
        for i in range(n + 1):
            t = i / n
            w = math.sin(math.pi * t) ** 0.8 * width / 2
            pts.append((w, t * length))
        outline = [(x, y) for x, y in pts] + [(-x, y) for x, y in reversed(pts[1:-1])]
        outline = [(x, y) for x, y in outline]
        # make CCW: right side goes up, left side comes down -> clockwise; reverse
        outline = list(reversed(outline))
        kw.setdefault("angle", 60)
        return self.prism(outline, depth=thick, color=color, **kw)

    # -- output --------------------------------------------------------------------
    def tri_count(self):
        return sum(len(f.verts) - 2 for f in self.bm.faces)


def circle_pts(r, n, start=90.0, sx=1.0, sy=1.0):
    return [(sx * r * math.cos(math.radians(start + 360.0 * i / n)),
             sy * r * math.sin(math.radians(start + 360.0 * i / n))) for i in range(n)]


def star_pts(r_out, r_in, n=5, start=90.0):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(start + 180.0 * i / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def heart_pts(size=1.0, n=24):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x / 32 * size, y / 32 * size))
    return list(reversed(pts))
