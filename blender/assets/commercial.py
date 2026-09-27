"""Commercial: restaurants, shops, bank, supermarket, gym... with full walk-in
interiors, plus the reusable interior fixtures they are furnished with.

Character scale: floor top at z=1, doors 8 studs tall, ceilings 13 studs,
counters 3.5 studs, tables 3 studs, chair seats ~1.9 studs.

Every building is split into parts so it works in a game:
  <Name>            floor, walls and facade
  <Name>_Roof       roof slab, ceiling lights, rooftop units (hide it to look inside)
  <Name>_Glass      all window glass (set Transparency ~0.4 in Studio)
  <Name>_Door...    door leaves (hinge or slide them)
  <Name>_<Area>     furniture groups (Kitchen, Dining, Counter...) to move or delete
Buildings face -Y (entrance towards -Y).
"""
import math
import random

from studlib.geo import by_normal, circle_pts, star_pts
from studlib.registry import add

CAT = "Commercial"
FL = 1.0     # floor top
T = 1.0      # wall thickness


def reg(name, fn, sub="Restaurants", tags=()):
    add(name, CAT, fn, sub=sub, split=True, tags=list(tags) + ["building", "interior"])


def fix(name, fn, sub="Fixtures", tags=()):
    add(name, CAT, fn, sub=sub, tags=list(tags) + ["fixture"])


def blk(m, size, loc, col, bev=0.0, **kw):
    return m.box(size, color=col, bevel=bev, loc=loc, **kw)


# ----------------------------------------------------------------------------
# pixel font for signs (3x5, a few wide letters)
# ----------------------------------------------------------------------------
FONT = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": [".##", "#..", "#..", "#..", ".##"], "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    "G": [".##", "#..", "#.#", "#.#", ".##"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"], "J": ["..#", "..#", "..#", "#.#", ".#."],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"], "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "P": ["##.", "#.#", "##.", "#..", "#.."],
    "Q": [".#.", "#.#", "#.#", "##.", ".##"], "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"], "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"], "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."], "Z": ["###", "..#", ".#.", "#..", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["##.", "..#", ".#.", "#..", "###"], "3": ["##.", "..#", ".#.", "..#", "##."],
    "4": ["#.#", "#.#", "###", "..#", "..#"], "5": ["###", "#..", "##.", "..#", "##."],
    "6": [".##", "#..", "###", "#.#", "###"], "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"], "9": ["###", "#.#", "###", "..#", "##."],
    "$": [".#.", ".##", "#..", ".#.", "..#", "##.", ".#."], "!": ["#", "#", "#", ".", "#"],
    "-": ["...", "...", "###", "...", "..."], "/": ["..#", "..#", ".#.", "#..", "#.."],
    "+": ["...", ".#.", "###", ".#.", "..."], " ": ["..", "..", "..", "..", ".."],
    "&": [".#.", "#.#", ".#.", "#.#", ".##"], "'": ["#", "#", ".", ".", "."],
}


def text_width(s, px=0.4):
    return (sum(len(FONT[ch][0]) for ch in s) + len(s) - 1) * px


def text(m, s, x=0.0, y=0.0, z=0.0, px=0.4, depth=0.25, col="white"):
    """Blocky pixel letters centred on (x, z), standing in the XZ plane just in front of y (towards -Y)."""
    cx = x - text_width(s, px) / 2
    for ch in s:
        g = FONT[ch]
        extra = (len(g) - 5) // 2
        for r, row in enumerate(g):
            zr = z + (2 - (r - extra)) * px
            k = 0
            while k < len(row):
                if row[k] == "#":
                    j = k
                    while j < len(row) and row[j] == "#":
                        j += 1
                    blk(m, ((j - k) * px, depth, px), (cx + (k + j) / 2 * px, y - depth / 2, zr), col)
                    k = j
                else:
                    k += 1
        cx += (len(g[0]) + 1) * px


def sign(m, s, x, y, z, board="charcoal", letters="white", px=0.45, pad=0.6, depth=0.5, trim=None):
    """A sign board with pixel lettering, front face at y (sticks out towards -Y)."""
    w = text_width(s, px) + pad * 2
    h = 5 * px + pad * 2
    blk(m, (w, depth, h), (x, y - depth / 2, z), board, bev=0.1)
    if trim:
        blk(m, (w + 0.3, depth * 0.6, h + 0.3), (x, y - depth * 0.3, z), trim, bev=0.08)
    text(m, s, x, y - depth, z, px=px, col=letters)
    return w, h


# ----------------------------------------------------------------------------
# building shell: floor, walls with real openings, glazing, doors, roof
# ----------------------------------------------------------------------------
def _band(spec, c):
    if isinstance(spec, str):
        return spec
    for zt, col in spec:
        if zt is None or c.z < zt:
            return col
    return spec[-1][1]


def wall(m, axis, fixed, a0, a1, z0, z1, out, ext, inn, top="concrete", holes=(), t=T, zcuts=()):
    """A straight wall along ``axis`` ('x' or 'y') at ``fixed`` from a0 to a1, with
    rectangular openings ``holes`` = [(a, b, z_bottom, z_top)]. ``out`` (+1/-1) says
    which side is outdoors; ``ext`` / ``inn`` colour the outside / inside faces
    (a name, or [(z_below, colour), ..., (None, colour)] height bands)."""
    oi = 1 if axis == "x" else 0

    def col(c, n):
        v = n[oi] * out
        if v > 0.5:
            return _band(ext, c)
        if v < -0.5:
            return _band(inn, c)
        return top
    pieces = []
    cur = a0
    for ha, hb, za, zb in sorted(holes):
        if ha > cur + 1e-4:
            pieces.append((cur, ha, z0, z1))
        if za > z0 + 1e-4:
            pieces.append((ha, hb, z0, za))
        if zb < z1 - 1e-4:
            pieces.append((ha, hb, zb, z1))
        cur = hb
    if a1 > cur + 1e-4:
        pieces.append((cur, a1, z0, z1))
    for pa, pb, qa, qb in pieces:
        L, h = pb - pa, qb - qa
        mid, zc = (pa + pb) / 2, (qa + qb) / 2
        size = (L, t, h) if axis == "x" else (t, L, h)
        loc = (mid, fixed, zc) if axis == "x" else (fixed, mid, zc)
        cut = [z for z in zcuts if qa + 1e-3 < z < qb - 1e-3]
        m.box(size, color=col, loc=loc, cuts={"z": cut} if cut else None)


def _wbox(m, axis, fixed, along, perp, z, size_along, size_perp, size_z, col):
    size = (size_along, size_perp, size_z) if axis == "x" else (size_perp, size_along, size_z)
    loc = (along, fixed + perp, z) if axis == "x" else (fixed + perp, along, z)
    m.box(size, color=col, loc=loc)


def glazing(m, axis, fixed, a, b, za, zb, out, frame="stainless", bars=1, sill="concrete", t=T, transom=None):
    """Glass pane + frame + mullions filling the hole (a..b, za..zb) of a wall at ``fixed``."""
    w, h = b - a, zb - za
    mid, zc = (a + b) / 2, (za + zb) / 2
    with m.group("Glass"):
        _wbox(m, axis, fixed, mid, 0, zc, w, 0.15, h, "glass")
    d = t * 0.6
    _wbox(m, axis, fixed, a + 0.14, 0, zc, 0.28, d, h, frame)
    _wbox(m, axis, fixed, b - 0.14, 0, zc, 0.28, d, h, frame)
    _wbox(m, axis, fixed, mid, 0, za + 0.14, w, d, 0.28, frame)
    _wbox(m, axis, fixed, mid, 0, zb - 0.14, w, d, 0.28, frame)
    for k in range(1, bars + 1):
        _wbox(m, axis, fixed, a + w * k / (bars + 1), 0, zc, 0.22, 0.45, h, frame)
    if transom:
        _wbox(m, axis, fixed, mid, 0, transom, w, 0.45, 0.22, frame)
    if sill:
        _wbox(m, axis, fixed, mid, out * (t / 2 + 0.25), za - 0.12, w + 0.6, 0.5, 0.3, sill)


def doors(m, axis, fixed, mid, w, h, out, name="Door", leaves=2, frame="stainless", panel="glass",
          handle="stainless", z0=FL, t=T):
    """Door frame (in the wall) + door leaves as their own parts (Door, or DoorL / DoorR)."""
    _wbox(m, axis, fixed, mid - w / 2 + 0.15, 0, z0 + h / 2, 0.3, t + 0.1, h, frame)
    _wbox(m, axis, fixed, mid + w / 2 - 0.15, 0, z0 + h / 2, 0.3, t + 0.1, h, frame)
    _wbox(m, axis, fixed, mid, 0, z0 + h - 0.15, w, t + 0.1, 0.3, frame)
    lw = (w - 0.6) / leaves
    for i in range(leaves):
        g = name if leaves == 1 else name + "LR"[i]
        c = mid - w / 2 + 0.3 + lw * (i + 0.5)
        with m.group(g):
            _wbox(m, axis, fixed, c, 0, z0 + (h - 0.3) / 2, lw - 0.06, 0.3, h - 0.3, frame)
            _wbox(m, axis, fixed, c, 0, z0 + (h - 0.3) / 2 + 0.3, lw - 0.7, 0.36, h - 1.6, panel)
            hx = c + (lw * 0.3 if i == 0 and leaves == 2 else -lw * 0.3 if leaves == 2 else lw * 0.35)
            for s in (-1, 1):
                _wbox(m, axis, fixed, hx, s * 0.3, z0 + 3.6, 0.18, 0.18, 1.6, handle)


def floor_slab(m, W, D, a="tile_cream", b="tile_gray", step=2.0, stripes=False, base="concrete"):
    iw, idp = W / 2 - T, D / 2 - T

    def col(c, n):
        if n.z < 0.5 or abs(c.x) > iw or abs(c.y) > idp:
            return base
        if a == b:
            return a
        if stripes:
            return a if int(math.floor(c.y / step)) % 2 == 0 else b
        return a if (math.floor(c.x / step) + math.floor(c.y / step)) % 2 == 0 else b
    cuts = {"y": step} if stripes else {"x": step, "y": step}
    if a == b:
        cuts = None
    m.box((W, D, FL), color=col, loc=(0, 0, FL / 2), cuts=cuts)


def shell(m, W, D, H=13.0, ext="brick", base="stone_dark", inn="wall_cream", wains="wood_mid", trim="concrete",
          front=(), back=(), left=(), right=(), parapet=2.0, cornice="concrete"):
    """Four walls. front/back/left/right: lists of holes (a, b, z_bottom, z_top) in world coords.
    Returns the wall-top height."""
    top = FL + H + parapet
    ext_b = ext if isinstance(ext, list) else [(FL + 1.5, base), (None, ext)]
    inn_b = inn if isinstance(inn, list) else [(FL + 3.0, wains), (FL + H, inn), (None, trim)]
    zc = sorted({z for z, _ in ext_b + inn_b if z is not None} | {FL + H})
    wall(m, "x", -D / 2 + T / 2, -W / 2, W / 2, FL, top, -1, ext_b, inn_b, trim, front, zcuts=zc)
    wall(m, "x", D / 2 - T / 2, -W / 2, W / 2, FL, top, 1, ext_b, inn_b, trim, back, zcuts=zc)
    wall(m, "y", -W / 2 + T / 2, -D / 2 + T, D / 2 - T, FL, top, -1, ext_b, inn_b, trim, right, zcuts=zc)
    wall(m, "y", W / 2 - T / 2, -D / 2 + T, D / 2 - T, FL, top, 1, ext_b, inn_b, trim, left, zcuts=zc)
    # cornice band round the top and a plinth round the bottom
    for s in (-1, 1):
        blk(m, (W + 0.6, 0.6, 0.6), (0, s * (D / 2 + 0.05), top - 0.3), cornice, bev=0.08)
        blk(m, (0.6, D + 0.6, 0.6), (s * (W / 2 + 0.05), 0, top - 0.3), cornice, bev=0.08)
    return top


def roof(m, W, D, H=13.0, top="concrete_dark", ceiling="white", lights=(), units=((0, 0),), light_col="glow"):
    """Flat roof between the walls (its own part) with ceiling light panels and rooftop units."""
    z = FL + H
    with m.group("Roof"):
        m.box((W - 2 * T, D - 2 * T, 0.8), color=by_normal(top, "concrete", ceiling), loc=(0, 0, z + 0.4))
        for x, y in lights:
            blk(m, (3.0, 1.2, 0.15), (x, y, z - 0.07), light_col)
            blk(m, (3.3, 1.5, 0.08), (x, y, z - 0.02), "lightgray")
        for x, y in units:
            blk(m, (3.0, 2.4, 1.6), (x, y, z + 1.6), "lightgray", bev=0.12)
            m.cyl(r=0.8, h=0.12, seg=8, color="charcoal", loc=(x, y, z + 2.46))
            blk(m, (0.5, 0.5, 1.0), (x + 1.8, y, z + 1.3), "gray")


def grid_lights(W, D, nx, ny, inset=4.0):
    xs = [-W / 2 + inset + (W - 2 * inset) * i / max(1, nx - 1) for i in range(nx)] if nx > 1 else [0.0]
    ys = [-D / 2 + inset + (D - 2 * inset) * j / max(1, ny - 1) for j in range(ny)] if ny > 1 else [0.0]
    return [(x, y) for x in xs for y in ys]


def sidewalk(m, W, D, depth=6.0, door_w=6.0, col="concrete", step="concrete_dark"):
    blk(m, (W + 4, depth, 0.5), (0, -D / 2 - depth / 2, 0.25), col)
    for s in (-1, 1):
        blk(m, (0.3, depth, 0.55), (s * (W / 2 + 2 - 0.15), -D / 2 - depth / 2, 0.27), step)
    blk(m, (door_w + 2, 1.2, 0.5), (0, -D / 2 - 0.6, 0.75), step)


def awning_strip(m, x0, x1, y, z, a="awning_red", b="awning_white", depth=2.6, stripe=1.0):
    w = x1 - x0
    m.box((w, depth, 0.25), color=lambda c, n: a if int(math.floor((c.x - x0) / stripe)) % 2 == 0 else b,
          loc=((x0 + x1) / 2, y - depth / 2, z), rot=(22, 0, 0), cuts={"x": [x0 + stripe * k for k in range(1, int(w / stripe) + 1)]})
    m.box((w, 0.25, 0.9), color=lambda c, n: a if int(math.floor((c.x - x0) / stripe)) % 2 == 0 else b,
          loc=((x0 + x1) / 2, y - depth + 0.05, z - depth * 0.37 - 0.35),
          cuts={"x": [x0 + stripe * k for k in range(1, int(w / stripe) + 1)]})


def planter(m, x, y, w=3.0, col="concrete_dark", plant="leaf"):
    blk(m, (w, 1.2, 1.2), (x, y, 0.6 + 0.5), col, bev=0.1)
    blk(m, (w - 0.3, 0.9, 0.1), (x, y, 1.75), "dirt_dark")
    for k in range(int(w / 0.9)):
        blk(m, (0.8, 0.8, 0.8), (x - w / 2 + 0.55 + k * 0.9, y, 2.1 + (k % 2) * 0.2), plant, bev=0.15)


def potted_plant(m, x, y, z=FL, h=3.0):
    m.cyl(r=0.7, r2=0.85, h=1.4, seg=8, color="clay", loc=(x, y, z + 0.7))
    m.cyl(r=0.1, h=h - 1.2, seg=4, color="bark", loc=(x, y, z + 1.4 + (h - 1.4) / 2))
    for dx, dy, dz, r in ((0, 0, h + 0.3, 0.9), (0.5, 0.2, h - 0.3, 0.7), (-0.45, -0.25, h - 0.2, 0.7)):
        blk(m, (r * 1.6, r * 1.6, r * 1.3), (x + dx, y + dy, z + dz), "leaf" if dz > h else "leaf_dark", bev=0.15)


# ----------------------------------------------------------------------------
# fixtures (local space: sits on z=0, customer side / front towards -Y)
# ----------------------------------------------------------------------------
def chair(m, x, y, rot=0, seat="booth_red", frame="stainless"):
    with m.at((x, y, 0), rot):
        for sx in (-0.6, 0.6):
            for sy in (-0.6, 0.6):
                blk(m, (0.18, 0.18, 1.8), (sx, sy, 0.9), frame)
        blk(m, (1.6, 1.6, 0.35), (0, 0, 1.95), seat, bev=0.1)
        blk(m, (1.6, 0.3, 1.8), (0, 0.72, 3.0), seat, bev=0.1)


def table_sq(m, w=3.2, top="wood_light", leg="charcoal", cloth=None, h=3.0):
    m.cyl(r=0.9, h=0.2, seg=8, color=leg, loc=(0, 0, 0.1))
    blk(m, (0.35, 0.35, h - 0.3), (0, 0, h / 2), leg)
    blk(m, (w, w, 0.25), (0, 0, h - 0.12), top, bev=0.06)
    if cloth:
        m.box((w + 0.1, w + 0.1, 0.08), loc=(0, 0, h + 0.04), cuts={"x": 0.8, "y": 0.8},
              color=lambda c, n, a=cloth: a if (math.floor(c.x / 0.8) + math.floor(c.y / 0.8)) % 2 else "white")


def table2(m, top="wood_light", seat="booth_red", cloth=None):
    table_sq(m, 3.0, top, cloth=cloth)
    chair(m, 0, -2.4, 180, seat)
    chair(m, 0, 2.4, 0, seat)
    blk(m, (0.5, 0.5, 0.6), (0.6, 0.5, 3.3), "white")        # napkin holder
    m.cyl(r=0.15, h=0.6, seg=6, color="sauce_red", loc=(-0.6, 0.6, 3.3))


def table4(m, top="wood_light", seat="booth_red", cloth=None):
    table_sq(m, 3.8, top, cloth=cloth)
    for ang, (x, y) in ((180, (0, -2.8)), (0, (0, 2.8)), (90, (-2.8, 0)), (-90, (2.8, 0))):
        chair(m, x, y, ang, seat)
    for x, y in ((-0.9, -0.9), (0.9, 0.9)):
        m.cyl(r=0.6, h=0.1, seg=8, color="ceramic", loc=(x, y, 3.08))


def booth(m, col="booth_red", top="white", edge="stainless"):
    """Diner booth: two high-back benches facing across a table (5 wide x 8 deep)."""
    for s in (-1, 1):
        blk(m, (5.0, 1.8, 1.6), (0, s * 2.9, 0.8), "wood_dark", bev=0.08)
        blk(m, (5.0, 1.8, 0.5), (0, s * 2.9, 1.85), col, bev=0.15)
        blk(m, (5.0, 0.7, 3.6), (0, s * 3.55, 2.6), col, bev=0.15)
        blk(m, (5.0, 0.8, 0.3), (0, s * 3.55, 4.5), "wood_dark", bev=0.06)
    blk(m, (0.4, 0.4, 2.8), (0, 0, 1.4), edge)
    blk(m, (4.2, 2.8, 0.3), (0, 0, 3.0), top, bev=0.08)
    blk(m, (4.3, 2.9, 0.1), (0, 0, 2.85), edge)
    for x in (-1.2, 1.2):
        m.cyl(r=0.55, h=0.08, seg=8, color="ceramic", loc=(x, 0, 3.2))
    blk(m, (0.4, 0.3, 0.5), (0, 0.9, 3.4), "sauce_red")
    blk(m, (0.4, 0.3, 0.5), (0.5, 0.9, 3.4), "banana")


def stool(m, x, y, seat="booth_red", z=0.0):
    with m.at((x, y, z)):
        m.cyl(r=0.7, h=0.15, seg=8, color="stainless", loc=(0, 0, 0.08))
        blk(m, (0.25, 0.25, 2.4), (0, 0, 1.3), "stainless")
        m.cyl(r=0.75, h=0.4, seg=8, color=seat, loc=(0, 0, 2.7), bevel=0.1)
        m.torus(R=0.55, r=0.07, seg=8, color="stainless", loc=(0, 0, 1.0))


def counter(m, L, top="marble", body="wood_mid", kick="charcoal", d=2.2, h=3.5, front_col=None):
    blk(m, (L, d - 0.3, 0.4), (0, 0.15, 0.2), kick)
    m.box((L, d - 0.2, h - 0.6), color=lambda c, n: (front_col or body) if n.y < -0.5 else body, loc=(0, 0.1, (h - 0.2) / 2 + 0.2),
          bevel=0.05)
    blk(m, (L + 0.3, d + 0.2, 0.3), (0, 0, h - 0.15), top, bev=0.06)


def register(m, x=0.0, y=0.0, z=3.5):
    with m.at((x, y, z)):
        blk(m, (1.4, 1.2, 0.5), (0, 0, 0.25), "charcoal", bev=0.08)
        blk(m, (1.1, 0.9, 0.12), (0, -0.05, 0.56), "darkgray")
        blk(m, (0.9, 0.12, 0.7), (0, 0.4, 1.0), "charcoal", bev=0.04, rot=(-15, 0, 0))
        blk(m, (0.75, 0.05, 0.5), (0, 0.33, 1.02), "screen_glow", rot=(-15, 0, 0))
        blk(m, (1.2, 0.8, 0.25), (0, -0.2, -0.1), "gray")


def stove(m, w=4.0):
    blk(m, (w, 2.6, 3.2), (0, 0, 1.6), "stainless", bev=0.06)
    blk(m, (w - 0.6, 0.1, 1.4), (0, -1.32, 1.3), "charcoal", bev=0.03)
    blk(m, (w - 0.8, 0.2, 0.18), (0, -1.45, 2.2), "stainless", bev=0.04)
    for i in range(4):
        m.cyl(r=0.12, h=0.2, seg=6, color="charcoal", rot=(90, 0, 0), loc=(-w / 2 + 0.6 + i * (w - 1.2) / 3, -1.35, 2.85))
    for x in (-w / 4, w / 4):
        for y in (-0.5, 0.5):
            blk(m, (1.2, 1.0, 0.12), (x, y, 3.26), "charcoal")
            m.torus(R=0.35, r=0.05, seg=8, color="iron_dark", loc=(x, y, 3.34))
    blk(m, (w, 0.3, 1.4), (0, 1.15, 3.9), "stainless")
    m.cyl(r=0.55, h=0.8, seg=8, color="steel", loc=(-w / 4, -0.5, 3.75))       # stock pot
    m.cyl(r=0.6, h=0.12, seg=8, color="iron_dark", loc=(w / 4, 0.5, 3.4))      # frying pan
    blk(m, (0.2, 1.2, 0.1), (w / 4, -0.3, 3.44), "iron_dark")


def hood(m, w=8.0, z=9.0):
    m.box((w, 3.0, 1.6), color="stainless", loc=(0, 0.2, z), bevel=0.05)
    blk(m, (w - 0.4, 2.6, 0.1), (0, 0.2, z - 0.82), "darkgray")
    blk(m, (1.6, 1.6, 4.0), (0, 1.0, z + 2.8), "stainless")


def fryer(m):
    blk(m, (2.4, 2.4, 3.2), (0, 0, 1.6), "stainless", bev=0.06)
    for x in (-0.55, 0.55):
        blk(m, (0.9, 1.5, 0.1), (x, -0.1, 3.22), "caramel")
        blk(m, (0.8, 1.2, 0.5), (x, -0.1, 3.5), "silver")
        blk(m, (0.12, 1.0, 0.12), (x, -1.0, 3.9), "charcoal", rot=(30, 0, 0))
    blk(m, (1.6, 0.1, 1.0), (0, -1.22, 1.6), "charcoal")


def grill(m, w=4.0):
    blk(m, (w, 2.6, 3.0), (0, 0, 1.5), "stainless", bev=0.06)
    blk(m, (w - 0.3, 2.3, 0.25), (0, 0, 3.12), "iron_dark")
    for i in range(3):
        m.cyl(r=0.45, h=0.18, seg=8, color="meat", loc=(-w / 2 + 0.9 + i * 1.1, -0.3, 3.33))
        m.cyl(r=0.45, h=0.06, seg=8, color="cheese", loc=(-w / 2 + 0.9 + i * 1.1, -0.3, 3.45))
    blk(m, (1.4, 0.2, 0.1), (w / 2 - 0.8, 0.4, 3.3), "silver")
    blk(m, (w, 0.3, 1.0), (0, 1.15, 3.6), "stainless")


def fridge_c(m, w=4.0, h=8.0, glass=False):
    blk(m, (w, 2.6, h), (0, 0, h / 2), "stainless", bev=0.08)
    for s in (-1, 1):
        blk(m, (w / 2 - 0.2, 0.15, h - 0.8), (s * w / 4, -1.33, h / 2 + 0.2), "glass" if glass else "steel", bev=0.04)
        blk(m, (0.15, 0.25, 2.0), (s * 0.35, -1.5, h * 0.55), "charcoal")
    if glass:
        for z in (2.0, 3.8, 5.6):
            for i in range(6):
                m.cyl(r=0.18, h=1.0, seg=6, color=["plastic_red", "plastic_green", "plastic_blue", "plastic_orange",
                                                   "potion_purple", "plastic_yellow"][i],
                      loc=(-w / 2 + 0.5 + i * (w - 1.0) / 5, -1.0, z))
    blk(m, (w - 0.4, 0.2, 0.4), (0, -1.3, h - 0.3), "charcoal")


def sink_c(m, w=4.0):
    blk(m, (w, 2.6, 3.4), (0, 0, 1.7), "stainless", bev=0.05)
    for x in (-w / 4, w / 4):
        blk(m, (w / 2 - 0.5, 1.8, 0.1), (x, -0.1, 3.36), "steel")
    blk(m, (0.2, 0.2, 1.4), (0, 0.9, 4.1), "chrome")
    blk(m, (0.2, 1.0, 0.2), (0, 0.45, 4.75), "chrome")
    blk(m, (w, 0.3, 1.2), (0, 1.15, 3.9), "stainless")
    for k in range(3):
        m.cyl(r=0.5, h=0.1, seg=8, color="ceramic", loc=(w / 4 + 0.1 * k, -0.2, 3.45 + 0.1 * k))


def prep_table(m, w=5.0):
    for sx in (-1, 1):
        for sy in (-1, 1):
            blk(m, (0.2, 0.2, 3.3), (sx * (w / 2 - 0.2), sy * 1.0, 1.65), "stainless")
    blk(m, (w, 2.4, 0.2), (0, 0, 3.4), "stainless", bev=0.04)
    blk(m, (w - 0.2, 2.2, 0.1), (0, 0, 1.0), "stainless")
    blk(m, (1.6, 1.1, 0.15), (-0.8, -0.2, 3.58), "wood_light")
    for i, c in enumerate(("tomato", "lettuce", "onion", "cheese")):
        blk(m, (0.35, 0.35, 0.3), (-1.3 + i * 0.3, -0.2, 3.8), c)
    for i in range(3):
        blk(m, (0.8, 0.8, 0.5), (0.9 + (i % 2) * 0.9, -0.3 + (i // 2) * 0.9, 3.75), "stainless")
        blk(m, (0.7, 0.7, 0.1), (0.9 + (i % 2) * 0.9, -0.3 + (i // 2) * 0.9, 4.0), ["tomato", "lettuce", "cheese"][i])
    for i in range(3):
        blk(m, (1.0, 1.0, 0.6), (-1.5 + i * 1.3, 0.2, 1.4), ["potato", "onion", "carrot"][i], bev=0.1)


def soda_fountain(m):
    blk(m, (3.0, 2.0, 2.6), (0, 0, 1.3 + 3.5), "charcoal", bev=0.1)
    for i, c in enumerate(("plastic_red", "chocolate", "plastic_green", "plastic_orange")):
        blk(m, (0.6, 0.1, 1.2), (-1.05 + i * 0.7, -1.02, 5.4), c, bev=0.03)
        blk(m, (0.2, 0.3, 0.3), (-1.05 + i * 0.7, -1.1, 4.4), "silver")
    blk(m, (3.0, 1.6, 0.1), (0, -0.4, 3.9), "stainless")
    for i in range(3):
        m.cyl(r=0.3, r2=0.36, h=0.8, seg=6, color="white", loc=(1.8, -0.3 + i * 0.1, 3.9 + 0.4 + i * 0.7))


def menu_board(m, w=9.0, h=3.6, board="menu_black", items=("burger", "fries", "soda", "icecream"), title=None):
    """Wall/ceiling menu board with pictures and price bars (face -Y)."""
    blk(m, (w, 0.4, h), (0, 0, 0), board, bev=0.06)
    blk(m, (w + 0.2, 0.3, h + 0.2), (0, 0.1, 0), "stainless", bev=0.05)
    n = len(items)
    for i, it in enumerate(items):
        x = -w / 2 + w * (i + 0.5) / n
        col = {"burger": "bread", "fries": "banana", "soda": "plastic_red", "icecream": "icecream_straw",
               "pizza": "pizza_sauce", "coffee": "chocolate", "donut": "frosting_pink", "sushi": "fish_orange",
               "cake": "frosting_white", "hotdog": "sauce_red"}.get(it, "white")
        blk(m, (1.4, 0.15, 1.1), (x, -0.25, 0.5), col, bev=0.1)
        for k in range(2):
            blk(m, (1.6 - k * 0.5, 0.1, 0.18), (x, -0.25, -0.55 - k * 0.4), "white" if k == 0 else "neon_yellow")
    if title:
        text(m, title, 0, -0.3, h / 2 - 0.45, px=0.13, depth=0.1, col="neon_yellow")


def pizza_oven(m):
    blk(m, (5.0, 4.0, 3.2), (0, 0, 1.6), "brick", bev=0.1)
    m.lathe([(2.4, 3.2), (2.3, 4.2), (1.8, 5.2), (1.0, 5.8), (0, 6.0)], seg=8, color="brick_dark", rot=(0, 0, 22.5))
    blk(m, (1.8, 0.5, 1.4), (0, -1.9, 3.9), "black")
    m.box((2.4, 0.4, 1.8), color="brick_dark", loc=(0, -2.0, 4.0), bevel=0.05)
    blk(m, (1.4, 0.3, 0.8), (0, -2.0, 3.8), "fire")
    blk(m, (0.9, 0.9, 2.4), (0, 0.6, 6.8), "brick_dark")
    for x in (-1.5, 1.5):
        blk(m, (1.0, 0.8, 0.7), (x, -1.7, 0.6), "wood_mid", bev=0.08)


def espresso(m):
    blk(m, (2.4, 1.6, 1.8), (0, 0, 0.9), "stainless", bev=0.12)
    blk(m, (2.2, 1.4, 0.3), (0, 0, 1.95), "charcoal")
    for x in (-0.6, 0.6):
        blk(m, (0.4, 0.4, 0.3), (x, -0.9, 1.2), "charcoal")
        m.cyl(r=0.2, r2=0.25, h=0.35, seg=6, color="white", loc=(x, -0.95, 0.35))
    m.cyl(r=0.35, h=0.1, seg=8, color="chrome", rot=(90, 0, 0), loc=(0, -0.82, 1.5))


def pastry_case(m, w=5.0):
    blk(m, (w, 2.4, 2.4), (0, 0, 1.2), "wood_dark", bev=0.06)
    blk(m, (w - 0.2, 2.2, 1.6), (0, 0, 3.2), "glass", bev=0.04)
    blk(m, (w, 2.4, 0.2), (0, 0, 4.1), "wood_dark")
    rnd = random.Random(3)
    for row, z in enumerate((2.55, 3.35)):
        for i in range(int(w / 0.9)):
            c = rnd.choice(["donut", "frosting_pink", "cookie", "cheese", "chocolate", "bread"])
            blk(m, (0.6, 0.6, 0.3), (-w / 2 + 0.6 + i * 0.9, -0.2 + row * 0.2, z), c, bev=0.12)
        blk(m, (w - 0.3, 2.0, 0.08), (0, 0, z - 0.2), "white")


def icecream_case(m, w=6.0):
    blk(m, (w, 2.6, 2.8), (0, 0, 1.4), "white", bev=0.08)
    m.box((w - 0.2, 2.2, 1.0), color="glass", loc=(0, 0.1, 3.3), rot=(-25, 0, 0), bevel=0.04)
    cols = ["icecream_straw", "icecream_mint", "icecream_van", "chocolate", "candy_blue", "lemon", "frosting_pink",
            "cookie"]
    n = int(w / 0.9)
    for i in range(n):
        for j in range(2):
            x, y = -w / 2 + 0.6 + i * (w - 1.2) / max(1, n - 1), -0.3 + j * 0.9
            blk(m, (0.75, 0.75, 0.4), (x, y, 2.75), "stainless")
            blk(m, (0.65, 0.65, 0.2), (x, y, 3.0), cols[(i + j * 3) % len(cols)], bev=0.08)
    blk(m, (w, 0.3, 0.5), (0, -1.35, 2.0), "icecream_straw")


def host_stand(m):
    blk(m, (2.0, 1.4, 3.8), (0, 0, 1.9), "wood_dark", bev=0.08)
    blk(m, (2.2, 1.6, 0.2), (0, 0, 3.9), "wood_mid", rot=(-10, 0, 0))
    blk(m, (1.0, 0.8, 0.05), (0, 0, 4.05), "paper", rot=(-10, 0, 0))


def trash_c(m):
    blk(m, (1.8, 1.8, 3.4), (0, 0, 1.7), "wood_mid", bev=0.08)
    blk(m, (1.2, 0.1, 0.5), (0, -0.92, 2.9), "charcoal")
    blk(m, (2.0, 2.0, 0.25), (0, 0, 3.5), "charcoal")


def jukebox(m):
    blk(m, (2.6, 1.8, 3.4), (0, 0, 1.7), "wood_dark", bev=0.1)
    m.cyl(r=1.3, h=1.8, seg=8, color="neon_orange", rot=(90, 0, 0), loc=(0, 0, 3.4),
          deform=lambda co: co.__class__((co.x, co.y, max(co.z, -0.2))))
    blk(m, (1.8, 0.1, 1.0), (0, -0.92, 2.6), "glass")
    for i in range(5):
        blk(m, (0.25, 0.1, 1.2), (-0.8 + i * 0.4, -0.93, 1.3), ["neon_pink", "neon_blue", "neon_yellow", "neon_green",
                                                             "neon_purple"][i])


# --- store fixtures ------------------------------------------------------------
PRODUCTS = ["plastic_red", "plastic_blue", "plastic_yellow", "plastic_green", "plastic_orange", "plastic_purple",
            "white", "bread", "chocolate", "plastic_pink", "milk", "lemon"]


def gondola(m, L=10.0, seed=1, levels=4, both=True, h=6.0):
    """Double-sided store shelving stocked with product boxes (runs along X)."""
    rnd = random.Random(seed)
    blk(m, (L, 0.4, h), (0, 0, h / 2), "white")
    blk(m, (L, 2.6, 0.6), (0, 0, 0.3), "charcoal")
    for side in ((-1, 1) if both else (-1,)):
        for k in range(levels):
            z = 0.7 + k * (h - 1.0) / levels
            blk(m, (L, 1.1, 0.12), (0, side * 0.75, z), "lightgray")
            x = -L / 2 + 0.3
            while x < L / 2 - 0.6:
                w = rnd.choice((0.5, 0.7, 0.9))
                hh = rnd.uniform(0.6, (h - 1.0) / levels - 0.3)
                col = rnd.choice(PRODUCTS)
                blk(m, (w - 0.08, 0.9, hh), (x + w / 2, side * 0.8, z + 0.06 + hh / 2), col)
                x += w
    blk(m, (L + 0.1, 2.7, 0.3), (0, 0, h + 0.15), "plastic_red")


def cooler_wall(m, L=12.0, h=8.0, seed=2):
    """Glass-door drink coolers (face -Y)."""
    rnd = random.Random(seed)
    blk(m, (L, 2.4, h), (0, 0.2, h / 2), "white", bev=0.06)
    doors = int(L / 2.4)
    for i in range(doors):
        x = -L / 2 + (i + 0.5) * L / doors
        blk(m, (L / doors - 0.2, 0.2, h - 1.4), (x, -1.0, h / 2 - 0.1), "glass")
        blk(m, (0.12, 0.3, 2.0), (x + L / doors / 2 - 0.4, -1.15, h * 0.5), "stainless")
        for z in (1.2, 2.7, 4.2, 5.7):
            for j in range(3):
                col = rnd.choice(["plastic_red", "plastic_blue", "plastic_green", "plastic_orange", "milk", "lemon"])
                m.cyl(r=0.22, h=1.1, seg=6, color=col, loc=(x - 0.6 + j * 0.6, -0.6, z + 0.55))
    blk(m, (L, 2.4, 0.8), (0, 0.2, h - 0.4), "plastic_blue")


def freezer_chest(m, L=8.0, seed=3):
    rnd = random.Random(seed)
    blk(m, (L, 3.0, 2.8), (0, 0, 1.4), "white", bev=0.1)
    blk(m, (L - 0.4, 2.6, 0.12), (0, 0, 2.85), "glass")
    x = -L / 2 + 0.5
    while x < L / 2 - 0.5:
        blk(m, (0.8, 1.0, 0.4), (x + 0.4, rnd.choice((-0.6, 0.5)), 2.5), rnd.choice(["ice", "icecream_straw",
                                                                                      "plastic_blue", "meat"]))
        x += 0.9


def checkout(m):
    """Checkout lane: conveyor belt, scanner, register, card reader, candy rack."""
    blk(m, (7.0, 2.4, 3.2), (0, 0, 1.6), "white", bev=0.08)
    blk(m, (4.2, 1.8, 0.12), (-1.2, 0, 3.26), "rubber")
    for x in (-3.2, 0.8):
        m.cyl(r=0.12, h=1.8, seg=6, color="stainless", rot=(90, 0, 0), loc=(x, 0, 3.26))
    blk(m, (1.2, 1.4, 0.2), (1.8, 0, 3.3), "charcoal")
    blk(m, (0.8, 0.8, 0.2), (1.8, 0, 3.42), "glass")
    register(m, 2.8, 0.6, 3.2)
    blk(m, (0.3, 0.3, 1.2), (3.2, -0.9, 3.8), "charcoal")
    blk(m, (0.5, 0.2, 0.8), (3.2, -1.0, 4.6), "screen_glow")
    for i, c in enumerate(("plastic_red", "lemon", "plastic_green")):
        blk(m, (0.8, 0.5, 0.5), (-2.8 + i * 0.9, -0.2, 3.6), c, bev=0.06)
    # candy rack at the lane
    blk(m, (2.0, 0.8, 4.0), (-2.2, -1.8, 2.0), "white")
    for k in range(4):
        for i in range(3):
            blk(m, (0.5, 0.3, 0.6), (-2.8 + i * 0.6, -2.3, 0.8 + k * 0.9),
                ["chocolate", "candy_pink", "plastic_yellow", "candy_blue"][(i + k) % 4])
    m.cyl(r=0.12, h=6.0, seg=6, color="stainless", loc=(3.3, 0.9, 3.0))
    blk(m, (1.4, 0.3, 1.0), (3.3, 0.9, 6.3), "neon_green")


def produce_stand(m, L=6.0, fruits=("apple_red", "orange", "banana", "lime", "grape", "lemon")):
    blk(m, (L, 3.4, 1.6), (0, 0, 0.8), "wood_mid", bev=0.08)
    n = len(fruits)
    for i, c in enumerate(fruits):
        x = -L / 2 + L * (i + 0.5) / n
        m.box((L / n - 0.2, 3.0, 0.8), color="wood_light", loc=(x, 0, 2.0), rot=(-18, 0, 0), bevel=0.05)
        for k in range(6):
            blk(m, (0.5, 0.5, 0.5), (x - 0.3 + (k % 2) * 0.6, -1.0 + (k // 2) * 0.9, 2.5 + (k // 2) * 0.3), c, bev=0.12)
    blk(m, (L, 0.3, 0.8), (0, -1.75, 1.5), "leaf")


def cart(m, col="plastic_red"):
    for sx in (-0.9, 0.9):
        for sy in (-1.3, 1.1):
            m.cyl(r=0.25, h=0.3, seg=6, color="charcoal", rot=(0, 90, 0), loc=(sx, sy, 0.25))
    blk(m, (1.9, 2.8, 0.15), (0, -0.1, 0.8), "stainless")
    m.box((2.2, 3.0, 1.8), color="stainless", loc=(0, 0, 2.4), bevel=0.05,
          deform=lambda co: co.__class__((co.x * (1 - 0.15 * (0.5 - co.z)), co.y, co.z)))
    blk(m, (2.0, 2.8, 0.1), (0, 0, 1.55), col)
    blk(m, (2.4, 0.2, 0.2), (0, 1.8, 3.6), col, bev=0.05)
    for sx in (-1.0, 1.0):
        blk(m, (0.12, 0.12, 2.8), (sx, 1.55, 2.0), "stainless", rot=(-12, 0, 0))


def clothes_rack(m, L=5.0, seed=4):
    rnd = random.Random(seed)
    for s in (-1, 1):
        blk(m, (0.15, 0.15, 4.2), (s * L / 2, 0, 2.1), "chrome")
        blk(m, (0.2, 1.4, 0.15), (s * L / 2, 0, 0.1), "chrome")
    blk(m, (L, 0.12, 0.12), (0, 0, 4.1), "chrome")
    x = -L / 2 + 0.35
    cols = ["fabric_red", "fabric_blue", "fabric_navy", "fabric_green", "fabric_yellow", "fabric_purple",
            "fabric_pink", "fabric_teal", "fabric_white", "fabric_gray"]
    while x < L / 2 - 0.2:
        c = rnd.choice(cols)
        blk(m, (0.25, 1.6, 2.2), (x, 0, 2.9), c)
        blk(m, (0.25, 2.2, 0.5), (x, 0, 3.75), c)
        x += 0.32


def mannequin(m, shirt="fabric_red", pants="fabric_navy"):
    m.cyl(r=0.8, h=0.2, seg=8, color="charcoal", loc=(0, 0, 0.1))
    blk(m, (0.2, 0.2, 1.0), (0, 0, 0.7), "chrome")
    for s in (-1, 1):
        blk(m, (0.55, 0.6, 2.2), (s * 0.35, 0, 2.2), pants)
    blk(m, (1.6, 0.9, 2.0), (0, 0, 4.2), shirt, bev=0.1)
    for s in (-1, 1):
        blk(m, (0.45, 0.5, 1.9), (s * 1.05, 0, 4.1), shirt, rot=(0, s * 8, 0))
    blk(m, (0.3, 0.3, 0.3), (0, 0, 5.3), "ceramic")
    blk(m, (0.9, 0.9, 1.0), (0, 0, 5.9), "ceramic", bev=0.15)


def fitting_room(m, col="velvet"):
    blk(m, (4.0, 0.3, 7.0), (0, 1.85, 3.5), "wall_cream")
    for s in (-1, 1):
        blk(m, (0.3, 4.0, 7.0), (s * 2.0, 0, 3.5), "wall_cream")
    blk(m, (4.0, 0.15, 0.15), (0, -1.9, 6.8), "brass")
    m.box((3.6, 0.3, 5.8), color=lambda c, n: col if int(math.floor(c.x / 0.6)) % 2 else "velvet",
          loc=(0.2, -1.9, 3.8), cuts={"x": 0.6})
    blk(m, (1.4, 0.1, 3.0), (0, 1.66, 3.8), "glass")
    blk(m, (0.8, 0.8, 1.6), (1.4, 1.2, 0.8), "wood_mid")


def folded_shelf(m, L=6.0, seed=5, h=7.0):
    rnd = random.Random(seed)
    blk(m, (L, 1.6, h), (0, 0.4, h / 2), "wood_light", bev=0.05)
    for k in range(4):
        z = 1.0 + k * 1.5
        blk(m, (L - 0.2, 1.4, 0.12), (0, 0.2, z), "wood_pale")
        for i in range(int(L / 1.1)):
            col = rnd.choice(["fabric_red", "fabric_blue", "fabric_white", "fabric_gray", "fabric_yellow", "fabric_green"])
            for j in range(rnd.randint(2, 4)):
                blk(m, (0.9, 1.0, 0.2), (-L / 2 + 0.6 + i * 1.1, -0.1, z + 0.17 + j * 0.2), col)


def tv_wall(m, L=12.0, h=7.0, seed=6):
    rnd = random.Random(seed)
    blk(m, (L, 0.5, h), (0, 0.3, h / 2), "charcoal")
    for row in range(2):
        for i in range(3):
            x = -L / 2 + L * (i + 0.5) / 3
            z = 2.2 + row * 2.8
            blk(m, (L / 3 - 0.6, 0.3, 2.3), (x, -0.05, z), "black", bev=0.05)
            blk(m, (L / 3 - 0.9, 0.1, 2.0), (x, -0.22, z), rnd.choice(["screen_glow", "neon_blue", "wall_sky",
                                                                       "leaf_light", "neon_purple"]))


def display_table(m, L=6.0, item="laptop", seed=7):
    rnd = random.Random(seed)
    blk(m, (L, 3.0, 0.3), (0, 0, 3.0), "white", bev=0.06)
    blk(m, (L - 0.6, 2.6, 2.8), (0, 0, 1.4), "charcoal")
    n = int(L / 1.8)
    for i in range(n):
        x = -L / 2 + L * (i + 0.5) / n
        if item == "laptop":
            blk(m, (1.4, 1.0, 0.1), (x, -0.4, 3.2), "silver")
            blk(m, (1.4, 0.1, 1.0), (x, 0.1, 3.7), "silver", rot=(-15, 0, 0))
            blk(m, (1.2, 0.05, 0.8), (x, 0.03, 3.7), rnd.choice(["screen_glow", "wall_sky", "neon_blue"]), rot=(-15, 0, 0))
        else:  # phones on stands
            for j in range(2):
                blk(m, (0.2, 0.2, 0.4), (x - 0.4 + j * 0.8, -0.3, 3.35), "charcoal")
                blk(m, (0.5, 0.08, 0.9), (x - 0.4 + j * 0.8, -0.35, 3.9), "black", rot=(-15, 0, 0))
                blk(m, (0.42, 0.05, 0.8), (x - 0.4 + j * 0.8, -0.4, 3.9), rnd.choice(["screen_glow", "neon_pink",
                                                                                     "neon_green"]), rot=(-15, 0, 0))


def jewelry_case(m, L=6.0, seed=8):
    rnd = random.Random(seed)
    blk(m, (L, 2.4, 2.6), (0, 0, 1.3), "wood_deep", bev=0.08)
    blk(m, (L - 0.2, 2.2, 1.2), (0, 0, 3.2), "glass")
    blk(m, (L, 2.4, 0.15), (0, 0, 3.85), "brass")
    blk(m, (L - 0.4, 2.0, 0.1), (0, 0, 2.66), "velvet")
    for i in range(int(L / 0.9)):
        x = -L / 2 + 0.6 + i * 0.9
        kind = i % 3
        if kind == 0:
            m.torus(R=0.22, r=0.06, seg=8, color="gold", rot=(90, 0, 0), loc=(x, -0.2, 2.95))
            blk(m, (0.16, 0.16, 0.16), (x, -0.2, 3.2), rnd.choice(["diamond", "ruby", "emerald", "sapphire"]), rot=(45, 0, 45))
        elif kind == 1:
            m.torus(R=0.35, r=0.04, seg=8, color=rnd.choice(["gold", "silver"]), loc=(x, 0.2, 2.75))
            blk(m, (0.14, 0.14, 0.14), (x, -0.15, 2.8), rnd.choice(["diamond", "ruby", "amethyst"]), rot=(45, 0, 45))
        else:
            blk(m, (0.5, 0.4, 0.4), (x, 0, 2.9), "velvet", bev=0.08)
            blk(m, (0.2, 0.2, 0.2), (x, -0.05, 3.2), "diamond", rot=(45, 0, 45))


def teller_desk(m, L=12.0, windows=3):
    """Bank teller counter with glass partitions, computers and cash trays (tellers stand at +Y)."""
    blk(m, (L, 2.4, 3.8), (0, 0, 1.9), "marble", bev=0.06)
    blk(m, (L, 0.3, 3.8), (0, -1.3, 1.9), "marble_dark")
    blk(m, (L + 0.4, 2.8, 0.3), (0, 0, 3.95), "marble_dark", bev=0.05)
    for i in range(windows):
        x = -L / 2 + L * (i + 0.5) / windows
        blk(m, (L / windows - 0.3, 0.2, 4.0), (x, -0.4, 6.1), "glass")
        blk(m, (1.4, 0.3, 0.5), (x, -0.4, 4.35), "vault")
        blk(m, (1.3, 0.8, 0.9), (x, 0.6, 4.55), "charcoal", bev=0.06)
        blk(m, (1.1, 0.1, 0.7), (x, 0.18, 4.6), "screen_glow")
        blk(m, (0.8, 0.5, 0.2), (x - 0.9, 0.5, 4.2), "cash", bev=0.03)
        text(m, str(i + 1), x, -1.46, 2.6, px=0.22, depth=0.1, col="brass")
    for i in range(windows + 1):
        blk(m, (0.3, 0.4, 4.2), (-L / 2 + L * i / windows, -0.4, 6.2), "brass")
    blk(m, (L + 0.4, 0.6, 0.4), (0, -0.4, 8.3), "brass")


def vault_door(m, r=4.0):
    """Round vault door on its frame (face -Y), door wheel sticks out."""
    blk(m, (2 * r + 2.4, 1.6, 2 * r + 2.4), (0, 0.4, r + 1.2), "vault", bev=0.2)
    m.cyl(r=r, h=1.4, seg=8, color="stainless", rot=(90, 0, 0), loc=(0, -0.6, r + 1.2), bevel=0.2)
    m.cyl(r=r - 0.6, h=0.3, seg=8, color="vault", rot=(90, 0, 0), loc=(0, -1.35, r + 1.2))
    for i in range(8):
        a = math.radians(45 * i)
        blk(m, (0.5, 0.4, 0.5), ((r - 0.35) * math.cos(a), -1.4, r + 1.2 + (r - 0.35) * math.sin(a)), "brass")
    m.torus(R=1.4, r=0.18, seg=8, color="brass", rot=(90, 0, 0), loc=(0, -1.9, r + 1.2))
    for a in (0, 45, 90, 135):
        blk(m, (2.8, 0.25, 0.25), (0, -1.9, r + 1.2), "brass", rot=(0, a, 0))
    m.cyl(r=0.45, h=0.6, seg=8, color="brass", rot=(90, 0, 0), loc=(0, -1.8, r + 1.2))
    for s in (-1, 1):
        blk(m, (0.8, 1.0, 1.4), (r * 0.95 * s, -0.9, r + 1.2), "steel", bev=0.1)


def deposit_boxes(m, L=8.0, h=8.0):
    blk(m, (L, 1.4, h), (0, 0.4, h / 2), "vault")
    for i in range(int(L / 1.0)):
        for k in range(int(h / 0.9)):
            x, z = -L / 2 + 0.5 + i * 1.0, 0.5 + k * 0.9
            blk(m, (0.9, 0.2, 0.8), (x, -0.35, z), "stainless")
            blk(m, (0.2, 0.1, 0.12), (x, -0.5, z), "brass")


def money_pallet(m, kind="cash"):
    blk(m, (3.4, 3.4, 0.4), (0, 0, 0.2), "wood_mid")
    if kind == "cash":
        for layer in range(4):
            for i in range(3):
                for j in range(2):
                    blk(m, (1.0, 1.5, 0.5), (-1.1 + i * 1.1, -0.75 + j * 1.55, 0.65 + layer * 0.5),
                        "cash" if (i + j + layer) % 2 else "cash_dark", bev=0.04)
                    blk(m, (0.2, 1.52, 0.52), (-1.1 + i * 1.1, -0.75 + j * 1.55, 0.65 + layer * 0.5), "white")
    else:
        for layer in range(4):
            n = 4 - layer
            for i in range(n):
                for j in range(2):
                    m.lathe([(0.75, 0), (0.55, 0.4), (0, 0.4)], seg=4, color=by_normal("gold_light", "gold", thresh=0.8),
                            loc=(-(n - 1) * 0.6 + i * 1.2, -0.7 + j * 1.4, 0.4 + layer * 0.4), rot=(0, 0, 45),
                            scale=(1.0, 0.55, 1.0), smooth=False)


def queue_posts(m, L=10.0, rows=2):
    for r in range(rows):
        y = r * 3.0
        for i in range(int(L / 3.3) + 1):
            x = -L / 2 + i * 3.3
            m.cyl(r=0.45, h=0.2, seg=8, color="brass", loc=(x, y, 0.1))
            m.cyl(r=0.12, h=3.0, seg=6, color="brass", loc=(x, y, 1.6))
            m.cyl(r=0.2, h=0.2, seg=6, color="brass", loc=(x, y, 3.1))
            if i:
                m.tube([(x - 3.3, y, 2.9), (x - 1.65, y, 2.3), (x, y, 2.9)], [0.1, 0.1, 0.1], seg=4, color="velvet")


def bench_seat(m, L=6.0, col="leather_dark"):
    for s in (-1, 1):
        blk(m, (0.3, 1.6, 1.6), (s * (L / 2 - 0.4), 0, 0.8), "stainless")
    blk(m, (L, 1.8, 0.5), (0, 0, 1.85), col, bev=0.12)
    blk(m, (L, 0.4, 1.8), (0, 0.8, 2.9), col, bev=0.12)


def office_desk(m, chair_col="charcoal", screen="screen_glow"):
    blk(m, (5.0, 2.6, 0.25), (0, 0, 3.0), "wood_light", bev=0.05)
    for s in (-1, 1):
        blk(m, (0.25, 2.4, 2.9), (s * 2.3, 0, 1.45), "gray")
    blk(m, (1.4, 2.2, 2.6), (1.4, 0, 1.4), "gray", bev=0.05)
    blk(m, (2.2, 0.2, 1.4), (-0.4, 0.8, 4.1), "black", bev=0.05)
    blk(m, (2.0, 0.1, 1.2), (-0.4, 0.68, 4.1), screen)
    blk(m, (0.3, 0.3, 0.6), (-0.4, 0.9, 3.4), "black")
    blk(m, (1.8, 0.7, 0.1), (-0.4, -0.2, 3.18), "charcoal")
    m.cyl(r=0.25, h=0.5, seg=6, color="white", loc=(1.6, -0.3, 3.4))
    with m.at((0, -2.2, 0)):
        m.cyl(r=1.0, h=0.2, seg=5, color="charcoal", loc=(0, 0, 0.3))
        blk(m, (0.25, 0.25, 1.6), (0, 0, 1.2), "chrome")
        blk(m, (1.8, 1.8, 0.4), (0, 0, 2.1), chair_col, bev=0.12)
        blk(m, (1.8, 0.4, 2.2), (0, -0.8, 3.3), chair_col, bev=0.12)


def cubicle(m, w=7.0, d=7.0, panel="fabric_gray"):
    blk(m, (w, 0.3, 4.5), (0, d / 2, 2.25), panel, bev=0.05)
    blk(m, (0.3, d, 4.5), (-w / 2, 0, 2.25), panel, bev=0.05)
    blk(m, (w + 0.1, 0.4, 0.2), (0, d / 2, 4.55), "chrome")
    blk(m, (0.4, d + 0.1, 0.2), (-w / 2, 0, 4.55), "chrome")
    with m.at((0, d / 2 - 1.6, 0), 180):
        office_desk(m)


def water_cooler(m):
    blk(m, (1.4, 1.4, 3.4), (0, 0, 1.7), "white", bev=0.08)
    m.cyl(r=0.6, h=1.6, seg=8, color="glass", loc=(0, 0, 4.2))
    for x, c in ((-0.3, "plastic_blue"), (0.3, "plastic_red")):
        blk(m, (0.2, 0.3, 0.3), (x, -0.8, 2.6), c)


def printer(m):
    blk(m, (2.6, 2.0, 2.6), (0, 0, 1.3), "lightgray", bev=0.1)
    blk(m, (2.4, 1.8, 0.5), (0, 0, 2.85), "gray", bev=0.06)
    blk(m, (1.4, 1.0, 0.1), (0, -0.6, 2.2), "paper")
    blk(m, (0.6, 0.1, 0.3), (0.7, -1.02, 2.3), "screen_glow")


def treadmill(m):
    blk(m, (2.0, 5.0, 0.6), (0, 0, 0.3), "charcoal", bev=0.1)
    blk(m, (1.6, 4.4, 0.1), (0, 0, 0.62), "rubber")
    for s in (-1, 1):
        blk(m, (0.2, 0.2, 3.6), (s * 0.9, -2.2, 2.0), "silver", rot=(10, 0, 0))
    blk(m, (2.2, 0.8, 0.8), (0, -2.6, 3.9), "charcoal", bev=0.1)
    blk(m, (1.4, 0.1, 0.5), (0, -2.2, 4.0), "screen_glow", rot=(-30, 0, 0))


def weight_rack(m, L=6.0):
    blk(m, (L, 1.6, 0.4), (0, 0, 1.2), "charcoal")
    blk(m, (L, 1.6, 0.4), (0, 0, 2.6), "charcoal")
    for s in (-1, 1):
        blk(m, (0.3, 1.6, 3.0), (s * L / 2, 0, 1.5), "charcoal")
    for tier, z in enumerate((1.7, 3.1)):
        for i in range(int(L / 0.8)):
            x = -L / 2 + 0.5 + i * 0.8
            w = 0.25 + i * 0.03
            blk(m, (0.25, 1.2, 0.25), (x, 0, z), "chrome")
            for yy in (-0.45, 0.45):
                blk(m, (0.45 + w, 0.3, 0.45 + w), (x, yy, z), "plastic_black" if tier else "plastic_red", bev=0.05)


def bench_press(m):
    blk(m, (1.4, 4.0, 0.4), (0, 0.5, 1.8), "leather_dark", bev=0.12)
    blk(m, (0.3, 3.0, 1.6), (0, 0.5, 0.8), "charcoal")
    for s in (-1, 1):
        blk(m, (0.3, 0.3, 4.2), (s * 1.8, -1.2, 2.1), "charcoal")
    m.cyl(r=0.1, h=6.0, seg=6, color="chrome", rot=(0, 90, 0), loc=(0, -1.1, 4.0))
    for s in (-1, 1):
        m.cyl(r=0.9, h=0.4, seg=8, color="plastic_black", rot=(0, 90, 0), loc=(s * 2.4, -1.1, 4.0))


def punching_bag(m, z_top=13.0):
    m.cyl(r=0.9, h=4.0, seg=8, color="plastic_red", loc=(0, 0, 4.5), bevel=0.2)
    m.cyl(r=0.95, h=0.4, seg=8, color="charcoal", loc=(0, 0, 6.6))
    blk(m, (0.1, 0.1, z_top - 6.8), (0, 0, (z_top + 6.8) / 2), "iron_dark")


def claw_machine(m, col="plastic_pink"):
    blk(m, (3.0, 3.0, 3.2), (0, 0, 1.6), col, bev=0.1)
    blk(m, (2.8, 2.8, 3.4), (0, 0, 4.9), "glass")
    for sx in (-1.45, 1.45):
        for sy in (-1.45, 1.45):
            blk(m, (0.2, 0.2, 3.6), (sx, sy, 4.9), col)
    blk(m, (3.2, 3.2, 1.0), (0, 0, 7.1), col, bev=0.1)
    text(m, "WIN", 0, -1.62, 7.1, px=0.18, depth=0.1, col="neon_yellow")
    rnd = random.Random(9)
    for i in range(9):
        blk(m, (0.7, 0.7, 0.7), (-0.8 + (i % 3) * 0.8, -0.4 + (i // 3) * 0.6, 3.6 + (i % 2) * 0.3),
            rnd.choice(["plastic_yellow", "plastic_blue", "neon_green", "fur_white", "frosting_pink"]), bev=0.2)
    blk(m, (0.1, 0.1, 1.2), (0.3, 0.2, 5.9), "chrome")
    for a in (0, 120, 240):
        blk(m, (0.08, 0.08, 0.6), (0.3 + 0.2 * math.cos(math.radians(a)), 0.2 + 0.2 * math.sin(math.radians(a)), 5.2),
            "chrome")
    blk(m, (2.4, 0.6, 0.3), (0, -1.6, 3.1), "charcoal")
    m.cyl(r=0.08, h=0.5, seg=4, color="charcoal", loc=(-0.5, -1.6, 3.5))
    m.cyl(r=0.2, h=0.15, seg=6, color="plastic_red", loc=(-0.5, -1.6, 3.8))
    blk(m, (0.4, 0.2, 0.4), (0.6, -1.7, 3.35), "neon_green")


def arcade_cab(m, col="plastic_blue", screen="neon_purple"):
    blk(m, (2.4, 2.4, 4.0), (0, 0.2, 2.0), col, bev=0.1)
    blk(m, (2.4, 1.6, 2.4), (0, 0.6, 5.2), col, bev=0.1)
    blk(m, (2.0, 0.15, 1.6), (0, -0.25, 5.0), screen, rot=(-12, 0, 0))
    blk(m, (2.4, 1.4, 0.3), (0, -1.0, 4.0), "charcoal", rot=(-12, 0, 0))
    blk(m, (0.2, 0.2, 0.5), (-0.5, -1.1, 4.3), "charcoal")
    blk(m, (0.3, 0.3, 0.15), (-0.5, -1.1, 4.6), "plastic_red")
    for i in range(3):
        m.cyl(r=0.14, h=0.12, seg=6, color=["neon_yellow", "neon_green", "neon_pink"][i], loc=(0.2 + i * 0.35, -1.05, 4.2))
    blk(m, (2.4, 0.4, 0.8), (0, -0.05, 6.6), "neon_yellow")


def fish_tank_row(m, L=8.0, seed=10):
    rnd = random.Random(seed)
    blk(m, (L, 2.4, 3.0), (0, 0, 1.5), "wood_dark", bev=0.06)
    for i in range(int(L / 2.6)):
        x = -L / 2 + 1.3 + i * 2.6
        blk(m, (2.4, 2.2, 2.4), (x, 0, 4.2), "water")
        blk(m, (2.4, 2.2, 0.3), (x, 0, 5.55), "charcoal")
        blk(m, (2.2, 2.0, 0.3), (x, 0, 3.15), "sand")
        for k in range(3):
            blk(m, (0.4, 0.15, 0.3), (x - 0.6 + k * 0.6, -1.12, 3.8 + (k % 2) * 0.6),
                rnd.choice(["fish_orange", "neon_blue", "plastic_yellow", "neon_pink"]))
        blk(m, (0.2, 0.2, 1.0), (x + 0.7, 0.3, 3.8), "leaf")


def pet_cages(m, L=8.0, seed=11):
    rnd = random.Random(seed)
    blk(m, (L, 2.6, 0.4), (0, 0, 0.2), "wood_mid")
    for row in range(2):
        for i in range(int(L / 2.6)):
            x = -L / 2 + 1.3 + i * 2.6
            z = 0.4 + row * 2.6
            blk(m, (2.4, 2.4, 0.2), (x, 0, z + 0.1), "sand")
            for k in range(5):
                blk(m, (0.08, 0.08, 2.2), (x - 1.1 + k * 0.55, -1.15, z + 1.3), "chrome")
            blk(m, (2.4, 2.4, 0.15), (x, 0, z + 2.45), "chrome")
            c = rnd.choice(["fur_white", "fur_orange", "fur_gray", "fur_tan", "fur_brown"])
            blk(m, (1.0, 1.2, 0.8), (x, 0.1, z + 0.6), c, bev=0.15)
            blk(m, (0.8, 0.7, 0.7), (x, -0.5, z + 1.1), c, bev=0.15)
            for s in (-0.2, 0.2):
                blk(m, (0.12, 0.05, 0.12), (x + s, -0.87, z + 1.2), "eye_black")


def slushie(m):
    blk(m, (3.0, 2.0, 1.2), (0, 0, 0.6 + 3.5), "white", bev=0.1)
    for i, c in enumerate(("candy_blue", "plastic_red", "lime")):
        blk(m, (0.9, 1.6, 2.0), (-1.0 + i * 1.0, 0, 5.3), "glass")
        blk(m, (0.8, 1.5, 1.4), (-1.0 + i * 1.0, 0, 5.0), c)
        blk(m, (0.3, 0.3, 0.4), (-1.0 + i * 1.0, -0.9, 4.2), "charcoal")


def sushi_loop(m, L=14.0, D=5.0, seed=12):
    """Conveyor-belt sushi counter loop with plates (L along X)."""
    rnd = random.Random(seed)
    blk(m, (L + 2.6, D + 2.6, 3.0), (0, 0, 1.5), "wood_dark", bev=0.08)
    blk(m, (L + 2.8, D + 2.8, 0.25), (0, 0, 3.1), "wood_light", bev=0.05)
    blk(m, (L, D, 0.2), (0, 0, 3.3), "stainless")
    blk(m, (L - 2.0, D - 2.0, 0.4), (0, 0, 3.4), "wood_deep")
    per = 2 * (L + D)
    for k in range(int(per / 1.6)):
        s = k * 1.6
        if s < L:
            x, y = -L / 2 + s, -D / 2 + 0.5
        elif s < L + D:
            x, y = L / 2 - 0.5, -D / 2 + (s - L)
        elif s < 2 * L + D:
            x, y = L / 2 - (s - L - D), D / 2 - 0.5
        else:
            x, y = -L / 2 + 0.5, D / 2 - (s - 2 * L - D)
        m.cyl(r=0.45, h=0.08, seg=8, color=rnd.choice(["plastic_red", "plastic_blue", "plastic_yellow", "white"]),
              loc=(x, y, 3.45))
        blk(m, (0.5, 0.3, 0.25), (x, y, 3.6), "sushi_rice")
        blk(m, (0.5, 0.3, 0.1), (x, y, 3.78), rnd.choice(["fish_orange", "meat_light", "egg_yolk"]))


# standalone fixtures (the same pieces the buildings are furnished with)
for _n, _f, _sub in (
        ("RestaurantTable2", lambda m: table2(m), "Restaurant"), ("RestaurantTable4", lambda m: table4(m), "Restaurant"),
        ("CheckeredTable4", lambda m: table4(m, top="wood_mid", seat="wood_dark", cloth="plastic_red"), "Restaurant"),
        ("DinerBooth", lambda m: booth(m), "Restaurant"), ("TealBooth", lambda m: booth(m, "booth_teal"), "Restaurant"),
        ("DinerStool", lambda m: stool(m, 0, 0), "Restaurant"), ("HostStand", host_stand, "Restaurant"),
        ("ServiceCounter", lambda m: (counter(m, 8.0), register(m, 2.0, 0.3)), "Restaurant"),
        ("CashRegister", lambda m: register(m, 0, 0, 0), "Restaurant"), ("Jukebox", jukebox, "Restaurant"),
        ("MenuBoard", lambda m: menu_board(m, title="MENU"), "Restaurant"), ("RestaurantTrashCan", trash_c, "Restaurant"),
        ("CommercialStove", stove, "Kitchen"), ("ExhaustHood", lambda m: hood(m, 6.0, 0.0), "Kitchen"),
        ("DeepFryer", fryer, "Kitchen"), ("FlatGrill", grill, "Kitchen"), ("CommercialFridge", fridge_c, "Kitchen"),
        ("DrinkFridge", lambda m: fridge_c(m, glass=True), "Kitchen"), ("DishSink", sink_c, "Kitchen"),
        ("PrepTable", prep_table, "Kitchen"), ("PizzaOven", pizza_oven, "Kitchen"),
        ("SodaFountain", lambda m: (counter(m, 4.0, top="stainless", body="stainless"), soda_fountain(m)), "Kitchen"),
        ("EspressoMachine", espresso, "Kitchen"), ("PastryCase", pastry_case, "Kitchen"),
        ("IceCreamCase", icecream_case, "Kitchen"),
        ("SushiConveyor", sushi_loop, "Kitchen"),
        ("GroceryShelf", gondola, "Store"), ("DrinkCooler", cooler_wall, "Store"), ("FreezerChest", freezer_chest, "Store"),
        ("CheckoutLane", checkout, "Store"), ("ProduceStand", produce_stand, "Store"), ("ShoppingCart", cart, "Store"),
        ("SlushieMachine", lambda m: (counter(m, 4.0), slushie(m)), "Store"),
        ("ClothingRack", clothes_rack, "Store"), ("Mannequin", mannequin, "Store"), ("FittingRoom", fitting_room, "Store"),
        ("ClothesShelf", folded_shelf, "Store"), ("TVWall", tv_wall, "Store"), ("LaptopTable", display_table, "Store"),
        ("PhoneTable", lambda m: display_table(m, item="phone"), "Store"), ("JewelryCase", jewelry_case, "Store"),
        ("FishTankRow", fish_tank_row, "Store"), ("PetCages", pet_cages, "Store"),
        ("TellerCounter", teller_desk, "Bank"), ("VaultDoor", vault_door, "Bank"), ("DepositBoxes", deposit_boxes, "Bank"),
        ("CashPallet", money_pallet, "Bank"), ("GoldPallet", lambda m: money_pallet(m, "gold"), "Bank"),
        ("QueuePosts", queue_posts, "Bank"), ("LobbyBench", bench_seat, "Bank"),
        ("OfficeDesk", office_desk, "Office"), ("Cubicle", cubicle, "Office"), ("WaterCooler", water_cooler, "Office"),
        ("OfficePrinter", printer, "Office"),
        ("Treadmill", treadmill, "Gym"), ("DumbbellRack", weight_rack, "Gym"), ("BenchPress", bench_press, "Gym"),
        ("PunchingBag", lambda m: punching_bag(m, 9.0), "Gym"),
        ("ClawMachine", claw_machine, "Arcade"), ("ArcadeCabinet", arcade_cab, "Arcade")):
    fix(_n, _f, sub="Fixtures" + _sub)


# ----------------------------------------------------------------------------
# restaurants
# ----------------------------------------------------------------------------
def _diner(m):
    W, D, H = 40.0, 34.0, 12.0
    Y0, Y1 = -D / 2, D / 2
    zt = FL + H
    win_z = (FL + 3.0, FL + 10.0)
    front = [(-3.0, 3.0, FL, FL + 8.5), (-18.0, -5.0, *win_z), (5.0, 18.0, *win_z)]
    sides = [(-14.0, -3.0, *win_z)]
    back = [(12.0, 15.5, FL, FL + 8.0)]
    floor_slab(m, W, D, "white", "black", step=2.0)
    shell(m, W, D, H, ext=[(FL + 1.5, "stainless"), (FL + 2.6, "wall_red"), (FL + 3.0, "stainless"), (None, "white")],
          inn=[(FL + 3.0, "wall_red"), (FL + 3.4, "stainless"), (FL + H, "wall_cream"), (None, "concrete")],
          trim="stainless", front=front, back=back, left=sides, right=sides, cornice="wall_red")
    for a, b, za, zb in front[1:]:
        glazing(m, "x", Y0 + T / 2, a, b, za, zb, -1, frame="stainless", bars=2, sill="wall_red")
    for sx, face in ((W / 2 - T / 2, 1), (-W / 2 + T / 2, -1)):
        for a, b, za, zb in sides:
            glazing(m, "y", sx, a, b, za, zb, face, frame="stainless", bars=1, sill="wall_red")
    doors(m, "x", Y0 + T / 2, 0.0, 6.0, 8.5, -1, name="Door", frame="stainless")
    doors(m, "x", Y1 - T / 2, 13.75, 3.5, 8.0, 1, name="BackDoor", leaves=1, frame="stainless", panel="steel")
    # kitchen partition with a pass-through window and a swing door
    wall(m, "x", 8.5, -W / 2 + T, W / 2 - T, FL, zt, -1,
         [(FL + 3.0, "wall_red"), (FL + 3.4, "stainless"), (None, "wall_cream")],
         [(FL + 3.0, "tile_white"), (None, "tile_white")], "stainless",
         holes=[(-9.0, 5.0, FL + 3.8, FL + 7.0), (9.0, 12.5, FL, FL + 8.0)], t=0.6, zcuts=(FL + 3.0, FL + 3.4))
    blk(m, (14.4, 1.6, 0.3), (-2.0, 8.5, FL + 3.8), "stainless")
    with m.group("KitchenDoor"):
        blk(m, (3.3, 0.3, 7.6), (10.75, 8.5, FL + 3.9), "stainless", bev=0.05)
        m.cyl(r=0.6, h=0.4, seg=8, color="glass", rot=(90, 0, 0), loc=(10.75, 8.5, FL + 5.8))
    # front of house
    with m.group("Booths"):
        for x in (-15.5, -9.5, 9.5, 15.5):
            with m.at((x, -12.0, FL)):
                booth(m, "booth_red")
    with m.group("Tables"):
        for x in (-13.0, 13.0):
            with m.at((x, -2.5, FL)):
                table4(m, top="white", seat="booth_red")
    with m.group("Counter"):
        with m.at((-2.0, 5.2, FL)):
            counter(m, 20.0, top="white", body="wall_red", front_col="stainless")
        for i in range(8):
            stool(m, -10.5 + i * 2.4, 2.6, z=FL)
        register(m, 6.5, 5.3, FL + 3.5)
        for x in (-8.0, -3.0, 2.0):
            with m.at((x, 5.4, FL + 3.5)):
                m.lathe([(0, 0), (0.9, 0.1), (0.9, 0.2), (0, 0.2)], seg=8, color="stainless")
                m.lathe([(0, 0.2), (0.8, 0.3), (0.5, 1.2), (0, 1.3)], seg=8, color="glass")
                blk(m, (1.0, 1.0, 0.4), (0, 0, 0.5), "frosting_pink", bev=0.15)
    with m.group("Kitchen"):
        for x, fn in ((-15.0, stove), (-10.5, grill), (-6.8, fryer)):
            with m.at((x, 14.6, FL)):
                fn(m)
        with m.at((-11.0, 13.6, FL)):
            hood(m, 11.0, 9.0)
        with m.at((-2.0, 11.6, FL)):
            prep_table(m, 5.0)
        with m.at((4.5, 14.6, FL)):
            sink_c(m, 4.0)
        with m.at((15.5, 14.6, FL)):
            fridge_c(m, 4.0)
        with m.at((-2.0, 14.9, FL)):
            blk(m, (6.0, 1.2, 0.2), (0, 0, 6.0), "stainless")
            for k in range(5):
                m.cyl(r=0.5, h=0.1, seg=8, color="ceramic", loc=(-2.2 + k * 1.1, 0, 6.15))
    with m.group("Decor"):
        with m.at((-2.0, 8.0, FL + 9.2)):
            menu_board(m, 12.0, 3.2, items=("burger", "fries", "hotdog", "soda", "icecream"), title="MENU")
        with m.at((-17.5, 3.0, FL), 90):
            jukebox(m)
        potted_plant(m, 18.0, 4.0)
        potted_plant(m, -18.0, -5.5)
        # checkered floor strip at the counter and a neon "OPEN" sign in the window
        with m.at((12.0, -16.2, FL + 8.0)):
            text(m, "OPEN", 0, 0, 0, px=0.3, depth=0.15, col="neon_red")
    roof(m, W, D, H, lights=grid_lights(W, D, 4, 3, inset=6.0), units=((-8, 8), (8, 10)))
    # facade: big neon sign on the parapet, awnings, sidewalk
    with m.group("Sign"):
        sign(m, "DINER", 0, Y0 - 0.1, zt + 1.2, board="wall_red", letters="neon_yellow", px=0.65, trim="stainless")
        for x in (-10.0, 10.0):
            m.prism(star_pts(1.0, 0.45, 5), depth=0.3, color="neon_yellow", rot=(90, 0, 0), loc=(x, Y0 - 0.3, zt + 1.2))
    awning_strip(m, -18.0, -5.0, Y0, FL + 11.0, "wall_red", "white")
    awning_strip(m, 5.0, 18.0, Y0, FL + 11.0, "wall_red", "white")
    sidewalk(m, W, D)
    for x in (-8.0, 8.0):
        planter(m, x, Y0 - 5.0, 4.0, col="wall_red")


reg("Diner", _diner)


# ----------------------------------------------------------------------------
# a storefront template the other buildings share
# ----------------------------------------------------------------------------
def storefront(m, W, D, H=12.0, ext="brick", base="stone_dark", inn="wall_cream", wains="wood_mid", trim="concrete",
               cornice="concrete", flo=("tile_cream", "tile_gray", 2.0, False), frame="stainless", door_w=6.0,
               door_panel="glass", win=(FL + 2.0, FL + 10.0), side_win=True, back_door=None, sign_txt=None,
               board="charcoal", letters="white", px=0.6, sign_trim=None, awning=None, lights=(4, 3),
               units=((-6.0, 4.0), (6.0, 6.0)), light_col="glow", sidewalk_col="concrete", extra_front=(),
               extra_left=(), extra_right=(), sill="concrete"):
    Y0, Y1 = -D / 2, D / 2
    front = [(-door_w / 2, door_w / 2, FL, FL + 8.5)]
    wins = []
    lx = (-W / 2 + 2.0, -door_w / 2 - 1.5)
    rx = (door_w / 2 + 1.5, W / 2 - 2.0)
    if lx[1] - lx[0] > 2.5:
        wins = [(lx[0], lx[1], *win), (rx[0], rx[1], *win)]
    front += wins + list(extra_front)
    sides = []
    if side_win:
        n = max(1, int((D - 6) / 11))
        for i in range(n):
            yc = -D / 2 + 4.5 + (i + 0.5) * (D - 9) / n
            sides.append((yc - 2.5, yc + 2.5, FL + 3.5, FL + 9.5))
    back = [(back_door - 1.75, back_door + 1.75, FL, FL + 8.0)] if back_door is not None else []
    floor_slab(m, W, D, *flo)
    shell(m, W, D, H, ext=ext, base=base, inn=inn, wains=wains, trim=trim, front=front, back=back,
          left=sides + list(extra_left), right=sides + list(extra_right), cornice=cornice)
    for a, b, za, zb in wins:
        glazing(m, "x", Y0 + T / 2, a, b, za, zb, -1, frame=frame, bars=max(1, int((b - a) / 4.5)), sill=sill)
    for sx, face in ((W / 2 - T / 2, 1), (-W / 2 + T / 2, -1)):
        for a, b, za, zb in sides:
            glazing(m, "y", sx, a, b, za, zb, face, frame=frame, bars=1, sill=sill)
    doors(m, "x", Y0 + T / 2, 0.0, door_w, 8.5, -1, name="Door", frame=frame, panel=door_panel)
    if back_door is not None:
        doors(m, "x", Y1 - T / 2, back_door, 3.5, 8.0, 1, name="BackDoor", leaves=1, frame="stainless", panel="steel")
    roof(m, W, D, H, lights=grid_lights(W, D, *lights, inset=5.0), units=units, light_col=light_col)
    sidewalk(m, W, D, col=sidewalk_col, door_w=door_w)
    zt = FL + H
    if sign_txt:
        with m.group("Sign"):
            sign(m, sign_txt, 0, Y0 - 0.1, zt + 1.0, board=board, letters=letters, px=px, trim=sign_trim)
    if awning and wins:
        for a, b, _, zb in wins:
            awning_strip(m, a, b, Y0, zb + 1.0, awning[0], awning[1])
    return dict(Y0=Y0, Y1=Y1, zt=zt, ix=W / 2 - T, iy=D / 2 - T)


def back_row(m, g, items, y):
    """Place fixtures [(x, fn)] against a back wall at y (facing -Y)."""
    for x, fn in items:
        with m.at((x, y, FL)):
            fn(m)


def pendant(m, x, y, zt, col="neon_yellow", shade="charcoal", drop=3.0):
    blk(m, (0.1, 0.1, drop), (x, y, zt - drop / 2), "charcoal")
    m.cyl(r=0.9, r2=0.3, h=0.8, seg=8, color=shade, loc=(x, y, zt - drop - 0.2))
    blk(m, (0.8, 0.8, 0.2), (x, y, zt - drop - 0.6), col)


def burger_icon(m, x, y, z, s=1.0):
    with m.at((x, y, z)):
        m.cyl(r=2.0 * s, h=0.8 * s, seg=8, color="bread_crust", loc=(0, 0, 0.4 * s))
        blk(m, (4.2 * s, 4.2 * s, 0.25 * s), (0, 0, 0.95 * s), "lettuce", bev=0.1)
        m.cyl(r=2.05 * s, h=0.7 * s, seg=8, color="meat", loc=(0, 0, 1.4 * s))
        blk(m, (4.0 * s, 4.0 * s, 0.2 * s), (0, 0, 1.85 * s), "cheese", rot=(0, 0, 45))
        m.lathe([(2.0 * s, 1.95 * s), (2.0 * s, 2.5 * s), (1.5 * s, 3.3 * s), (0, 3.6 * s)], seg=8, color="bread_crust")
        for a in range(0, 360, 60):
            blk(m, (0.25 * s, 0.25 * s, 0.1 * s), (1.2 * s * math.cos(math.radians(a)), 1.2 * s * math.sin(math.radians(a)),
                                                   3.1 * s), "offwhite")


def _burger_restaurant(m):
    W, D, H = 44.0, 36.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "charcoal"), (FL + 10.6, "wall_red"), (None, "plastic_yellow")],
                   inn=[(FL + 3.0, "tile_white"), (FL + 3.3, "wall_red"), (FL + H, "wall_cream"), (None, "concrete")],
                   trim="plastic_yellow", cornice="plastic_yellow", flo=("tile_white", "wall_red", 2.0, False),
                   frame="charcoal", sign_txt="BURGERS", board="plastic_yellow", letters="wall_red", px=0.65,
                   awning=("wall_red", "plastic_yellow"), back_door=15.0, lights=(4, 4),
                   extra_left=[(11.0, 15.5, FL + 3.0, FL + 7.5)])
    zt, iy = b["zt"], b["iy"]
    glazing(m, "y", W / 2 - T / 2, 11.0, 15.5, FL + 3.0, FL + 7.5, 1, frame="charcoal", bars=1, sill="stainless")
    with m.group("Counter"):
        with m.at((-4.0, 4.0, FL)):
            counter(m, 22.0, top="stainless", body="wall_red", front_col="plastic_yellow")
        for x in (-12.0, -6.0, 0.0):
            register(m, x, 4.2, FL + 3.5)
        with m.at((10.5, 4.0, FL)):
            counter(m, 5.0, top="stainless", body="stainless")
            soda_fountain(m)
        with m.at((W / 2 - T - 1.6, 13.25, FL), -90):     # drive-thru window counter
            counter(m, 6.0, top="stainless", body="stainless", d=2.4)
            register(m, 0, 0.3, 3.5)
    with m.group("Kitchen"):
        back_row(m, "Kitchen", [(-18.5, lambda m: grill(m, 4.0)), (-14.3, lambda m: grill(m, 4.0)), (-10.8, fryer),
                                (-8.2, fryer), (-4.2, lambda m: fridge_c(m, 4.0)), (0.2, lambda m: sink_c(m, 4.0)),
                                (5.0, lambda m: fridge_c(m, 4.4, glass=True))], iy - 1.4)
        with m.at((-14.0, iy - 2.2, FL)):
            hood(m, 11.0, 9.0)
        for x in (-12.0, -5.0):
            with m.at((x, 10.0, FL)):
                prep_table(m, 5.0)
    with m.group("MenuBoards"):
        for x in (-12.0, -1.0):
            blk(m, (0.12, 0.12, 2.6), (x - 3.5, 5.4, zt - 1.3), "charcoal")
            blk(m, (0.12, 0.12, 2.6), (x + 3.5, 5.4, zt - 1.3), "charcoal")
            with m.at((x, 5.4, zt - 4.4)):
                menu_board(m, 10.0, 3.4, items=("burger", "fries", "soda", "icecream", "hotdog"), title="MENU")
    with m.group("Dining"):
        for x in (-16.0, -8.0):
            for y in (-11.0, -3.0):
                with m.at((x, y, FL)):
                    table4(m, top="white", seat="plastic_yellow")
        for x in (8.0, 15.0):
            for y in (-11.5, -5.5):
                with m.at((x, y, FL), 90):
                    table2(m, top="white", seat="wall_red")
        with m.at((0.0, -12.5, FL)):
            trash_c(m)
        with m.at((2.4, -12.5, FL)):
            trash_c(m)
    with m.group("Roof"):
        blk(m, (0.8, 0.8, 5.0), (W / 2 - 6.0, -D / 2 + 6.0, zt + 2.5), "charcoal")
        burger_icon(m, W / 2 - 6.0, -D / 2 + 6.0, zt + 5.0, 1.2)
    # drive-thru lane: menu post and speaker
    with m.at((W / 2 + 7.0, -4.0, 0)):
        blk(m, (0.6, 0.6, 3.0), (0, 0, 1.5), "charcoal")
        with m.at((0, 0, 5.0), -90):
            menu_board(m, 5.0, 3.6, items=("burger", "fries", "soda"), title="ORDER")
    with m.at((W / 2 + 6.0, 2.0, 0)):
        blk(m, (0.4, 0.4, 3.2), (0, 0, 1.6), "charcoal")
        blk(m, (1.2, 1.0, 1.4), (0, 0, 3.5), "plastic_yellow", bev=0.1)
    blk(m, (8.0, 36.0, 0.3), (W / 2 + 6.0, 0, 0.15), "asphalt")
    for yy in (-14.0, -6.0, 2.0, 10.0):
        blk(m, (0.4, 3.0, 0.05), (W / 2 + 6.0, yy, 0.32), "road_yellow")


reg("BurgerRestaurant", _burger_restaurant)


def _pizzeria(m):
    W, D, H = 36.0, 32.0, 12.0
    b = storefront(m, W, D, H, ext="brick", base="stone_dark", inn="wall_cream", wains="wood_dark",
                   flo=("wood_light", "wood", 1.0, True), frame="wood_dark", door_panel="glass",
                   sign_txt="PIZZA", board="fabric_green", letters="white", px=0.7, sign_trim="white",
                   awning=("fabric_green", "white"), back_door=12.0, sill="stone_light")
    zt, iy = b["zt"], b["iy"]
    with m.group("Kitchen"):
        with m.at((-6.0, iy - 2.1, FL)):
            pizza_oven(m)
        back_row(m, "Kitchen", [(-15.0, lambda m: fridge_c(m, 3.6)), (2.5, lambda m: sink_c(m, 4.0)),
                                (6.8, stove)], iy - 1.4)
        with m.at((-4.0, 6.8, FL)):
            prep_table(m, 6.0)
    with m.group("Counter"):
        with m.at((-1.0, 3.2, FL)):
            counter(m, 16.0, top="wood_light", body="brick", front_col="brick")
        register(m, 5.0, 3.4, FL + 3.5)
        with m.at((-4.0, 3.2, FL + 3.5)):
            blk(m, (5.0, 2.0, 1.4), (0, 0, 0.7), "glass")
            for k in range(3):
                m.cyl(r=0.75, h=0.12, seg=8, color="pizza_sauce", loc=(-1.6 + k * 1.6, 0, 0.3))
                m.cyl(r=0.65, h=0.05, seg=8, color="cheese", loc=(-1.6 + k * 1.6, 0, 0.38))
    with m.group("Dining"):
        for x in (-11.0, -3.0, 5.0):
            with m.at((x, -8.5, FL)):
                table4(m, top="wood_mid", seat="wood_dark", cloth="plastic_red")
        for y in (-9.0, -1.0):
            with m.at((14.0, y, FL), 90):
                booth(m, "fabric_green", top="wood_light", edge="wood_dark")
    with m.group("Decor"):
        with m.at((-1.0, iy - 0.3, FL + 9.0)):
            menu_board(m, 8.0, 3.0, board="wood_dark", items=("pizza", "pizza", "soda", "icecream"), title="PIZZA")
        for i, c in enumerate(("fabric_green", "white", "plastic_red")):
            blk(m, (0.2, 1.2, 3.0), (-W / 2 + T + 0.1, -4.0 + i * 1.2, FL + 7.0), c)
        potted_plant(m, -15.5, -12.5)
        for x in (-10.0, 0.0, 10.0):
            pendant(m, x, -8.5, zt, col="glow", shade="fabric_green")


reg("Pizzeria", _pizzeria)


def _sushi_bar(m):
    W, D, H = 38.0, 32.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "stone_dark"), (None, "wood_dark")],
                   inn=[(FL + 3.0, "wood_dark"), (FL + H, "wall_cream"), (None, "concrete")], trim="wood_deep",
                   cornice="wall_red", flo=("wood_light", "wood_pale", 1.0, True), frame="wood_deep",
                   door_panel="wood_mid", sign_txt="SUSHI", board="black", letters="wall_red", px=0.7,
                   sign_trim="wall_red", back_door=13.0, light_col="neon_orange", sill="wood_deep")
    zt, iy = b["zt"], b["iy"]
    with m.group("SushiCounter"):
        with m.at((-3.0, 1.0, FL)):
            sushi_loop(m, 16.0, 5.0)
        for i in range(7):
            for s in (-1, 1):
                stool(m, -11.0 + i * 2.7, 1.0 + s * 5.2, seat="wall_red", z=FL)
    with m.group("Kitchen"):
        back_row(m, "Kitchen", [(-14.5, lambda m: fridge_c(m, 4.0)), (-10.0, lambda m: sink_c(m, 4.0)),
                                (-5.0, lambda m: prep_table(m, 5.0)), (0.5, stove), (5.0, lambda m: fridge_c(m, 4.0, glass=True))],
                 iy - 1.4)
    with m.group("Tatami"):
        blk(m, (8.0, 22.0, 1.0), (W / 2 - T - 4.0, -3.0, FL + 0.5), "wood_light", bev=0.05)
        blk(m, (7.6, 21.6, 0.1), (W / 2 - T - 4.0, -3.0, FL + 1.05), "corn_husk")
        for y in (-10.0, -3.0, 4.0):
            blk(m, (3.4, 3.0, 0.3), (W / 2 - T - 4.0, y, FL + 2.4), "wood_dark", bev=0.05)
            blk(m, (0.5, 0.5, 1.1), (W / 2 - T - 4.0, y, FL + 1.65), "wood_dark")
            for dy in (-2.2, 2.2):
                blk(m, (1.6, 1.4, 0.3), (W / 2 - T - 4.0, y + dy, FL + 1.25), "fabric_red", bev=0.1)
    with m.group("Decor"):
        for x in (-12.0, -3.0, 6.0):
            blk(m, (0.1, 0.1, 2.0), (x, 1.0, zt - 1.0), "charcoal")
            m.cyl(r=0.8, h=1.6, seg=8, color="wall_red", loc=(x, 1.0, zt - 2.8), bevel=0.2)
            m.cyl(r=0.5, h=0.2, seg=8, color="black", loc=(x, 1.0, zt - 2.0))
            m.cyl(r=0.5, h=0.2, seg=8, color="black", loc=(x, 1.0, zt - 3.6))
        for i in range(4):   # noren curtain over the door
            blk(m, (1.35, 0.1, 2.2), (-2.1 + i * 1.4, -D / 2 + T + 0.2, FL + 7.2), "wall_navy")
        with m.at((-4.0, iy - 0.3, FL + 9.2)):
            menu_board(m, 10.0, 2.6, board="wood_dark", items=("sushi", "sushi", "sushi", "soda"))
        potted_plant(m, -16.0, -12.5)
    with m.group("Sign"):
        for x in (-12.0, 12.0):
            m.cyl(r=1.0, h=2.2, seg=8, color="wall_red", loc=(x, -D / 2 - 1.0, zt - 1.5), bevel=0.2)
            blk(m, (0.2, 1.2, 0.2), (x, -D / 2 - 0.5, zt), "charcoal")


reg("SushiBar", _sushi_bar)


def armchair_c(m, col="leather"):
    blk(m, (2.6, 2.4, 1.3), (0, 0, 0.65 + 0.3), col, bev=0.2)
    blk(m, (2.6, 0.7, 2.4), (0, 0.9, 2.0), col, bev=0.2)
    for s in (-1, 1):
        blk(m, (0.5, 2.4, 1.8), (s * 1.3, 0, 1.2), col, bev=0.15)
    for sx in (-1, 1):
        for sy in (-1, 1):
            blk(m, (0.25, 0.25, 0.3), (sx * 1.1, sy * 1.0, 0.15), "wood_dark")


def _coffee_shop(m):
    W, D, H = 34.0, 28.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "brick_dark"), (None, "wall_green")], inn="wall_cream",
                   wains="wood_mid", trim="wood_dark", cornice="wood_dark", flo=("wood_mid", "wood", 1.0, True),
                   frame="wood_dark", sign_txt="COFFEE", board="wall_green", letters="white", px=0.6,
                   sign_trim="wood_dark", awning=("wall_green", "white"), back_door=11.0, light_col="neon_yellow")
    zt, iy = b["zt"], b["iy"]
    with m.group("Counter"):
        with m.at((-4.0, 4.5, FL)):
            counter(m, 14.0, top="wood_light", body="wood_dark", front_col="wood_mid")
        for x in (-8.5, -4.5):
            with m.at((x, 4.9, FL + 3.5)):
                espresso(m)
        with m.at((5.5, 4.5, FL)):
            pastry_case(m, 5.0)
        register(m, 0.0, 4.6, FL + 3.5)
        back_row(m, "Counter", [(-12.5, lambda m: fridge_c(m, 3.4, 7.0, glass=True)), (-3.0, lambda m: sink_c(m, 4.0)),
                                (3.0, lambda m: counter(m, 6.0, top="wood_light", body="wood_dark"))], iy - 1.4)
    with m.group("Seating"):
        for x, y in ((-11.0, -8.0), (-4.0, -8.0), (-11.0, -2.0)):
            with m.at((x, y, FL)):
                table2(m, top="wood_light", seat="wood_dark")
        for x in (6.0, 11.0):
            with m.at((x, -9.0, FL), 180):
                armchair_c(m, "leather")
        with m.at((8.5, -7.0, FL)):
            m.cyl(r=1.3, h=0.2, seg=8, color="wood_light", loc=(0, 0, 2.0))
            blk(m, (0.3, 0.3, 1.9), (0, 0, 1.0), "charcoal")
            m.cyl(r=0.3, r2=0.35, h=0.6, seg=6, color="white", loc=(0.3, 0, 2.4))
        for x in (6.0, 11.0):
            with m.at((x, -1.5, FL), 0):
                armchair_c(m, "fabric_green")
    with m.group("Decor"):
        with m.at((-4.0, iy - 0.3, FL + 8.6)):
            menu_board(m, 10.0, 3.4, board="menu_black", items=("coffee", "coffee", "donut", "cake"), title="COFFEE")
        with m.at((W / 2 - T - 0.8, 3.0, FL), -90):
            blk(m, (6.0, 1.4, 8.0), (0, 0.2, 4.0), "wood_dark", bev=0.05)
            rnd = random.Random(21)
            for k in range(4):
                blk(m, (5.6, 1.2, 0.12), (0, 0, 1.2 + k * 1.8), "wood_mid")
                x = -2.6
                while x < 2.6:
                    w = rnd.choice((0.25, 0.35, 0.45))
                    blk(m, (w - 0.04, 0.9, 1.2), (x + w / 2, -0.1, 1.9 + k * 1.8),
                        rnd.choice(["fabric_red", "fabric_blue", "fabric_green", "fabric_yellow", "paper"]))
                    x += w
        for x in (-9.0, 0.0, 9.0):
            pendant(m, x, -5.0, zt, col="neon_yellow", shade="wood_dark")
        potted_plant(m, -14.5, -11.0)
        potted_plant(m, 14.5, -11.5)


reg("CoffeeShop", _coffee_shop)


def _ice_cream_parlor(m):
    W, D, H = 30.0, 26.0, 11.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "white"), (FL + 10.0, "frosting_pink"), (None, "white")],
                   inn=[(FL + 3.0, "icecream_mint"), (FL + H, "wall_peach"), (None, "white")], trim="white",
                   cornice="icecream_mint", flo=("frosting_pink", "white", 2.0, False), frame="white",
                   sign_txt="ICE CREAM", board="white", letters="frosting_pink", px=0.5, sign_trim="icecream_mint",
                   awning=("frosting_pink", "white"), back_door=9.0, lights=(3, 3), win=(FL + 2.0, FL + 9.0))
    zt, iy = b["zt"], b["iy"]
    with m.group("Counter"):
        with m.at((-3.0, 4.0, FL)):
            icecream_case(m, 10.0)
        with m.at((5.5, 4.0, FL)):
            counter(m, 5.0, top="white", body="frosting_pink")
        register(m, 5.5, 4.2, FL + 3.5)
        back_row(m, "Counter", [(-10.0, lambda m: freezer_chest(m, 6.0)), (-3.0, lambda m: sink_c(m, 4.0)),
                                (2.0, lambda m: fridge_c(m, 4.0))], iy - 1.4)
        for k in range(4):
            m.cone(r=0.45, h=1.1, seg=6, color="cone", rot=(180, 0, 0), loc=(7.2 + k * 0.5, 4.0, FL + 5.2))
    with m.group("Seating"):
        for x in (-9.0, -2.0, 5.0):
            with m.at((x, -7.0, FL)):
                table2(m, top="white", seat=["frosting_pink", "icecream_mint", "lemon"][int(x) % 3])
        for i in range(4):
            stool(m, 9.5, -9.0 + i * 2.4, seat="icecream_mint", z=FL)
        with m.at((12.2, -5.5, FL), -90):
            counter(m, 10.0, top="white", body="white", d=1.4, h=3.6)
    with m.group("Decor"):
        with m.at((-3.0, iy - 0.3, FL + 8.2)):
            menu_board(m, 9.0, 2.6, board="white", items=("icecream", "icecream", "icecream", "cake"))
    with m.group("Roof"):
        with m.at((10.0, -D / 2 + 4.0, zt)):
            m.cone(r=1.8, h=5.0, seg=8, color="cone", rot=(180, 0, 0), loc=(0, 0, 5.2))
            blk(m, (3.4, 3.4, 2.6), (0, 0, 6.2), "frosting_pink", bev=0.6)
            blk(m, (2.8, 2.8, 2.2), (0, 0, 8.2), "icecream_mint", bev=0.5)
            blk(m, (0.8, 0.8, 0.8), (0, 0, 9.7), "cherry", bev=0.2)


reg("IceCreamParlor", _ice_cream_parlor)


def _donut_shop(m):
    W, D, H = 28.0, 24.0, 11.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "white"), (None, "wall_peach")], inn="wall_cream", wains="frosting_pink",
                   trim="white", cornice="frosting_pink", flo=("white", "frosting_pink", 2.0, False), frame="white",
                   sign_txt="DONUTS", board="frosting_pink", letters="white", px=0.55, awning=("frosting_pink", "white"),
                   back_door=8.0, lights=(3, 3), win=(FL + 2.0, FL + 9.0))
    zt, iy = b["zt"], b["iy"]
    with m.group("Counter"):
        for x in (-7.0, -1.8):
            with m.at((x, 3.5, FL)):
                pastry_case(m, 5.0)
        with m.at((5.5, 3.5, FL)):
            counter(m, 6.0, top="white", body="frosting_pink")
        register(m, 4.5, 3.7, FL + 3.5)
        with m.at((7.3, 3.9, FL + 3.5)):
            espresso(m)
        back_row(m, "Counter", [(-8.0, lambda m: fridge_c(m, 4.0, glass=True)), (-2.5, fryer), (2.0, lambda m: sink_c(m, 4.0))],
                 iy - 1.4)
        for k in range(3):   # donut racks
            blk(m, (3.0, 1.6, 0.1), (8.0, iy - 1.2, FL + 2.0 + k * 1.6), "stainless")
            for j in range(4):
                m.torus(R=0.3, r=0.15, seg=8, color=["frosting_pink", "chocolate", "donut", "candy_blue"][(j + k) % 4],
                        loc=(6.9 + j * 0.7, iy - 1.2, FL + 2.2 + k * 1.6))
    with m.group("Seating"):
        for x in (-8.0, -1.0, 6.0):
            with m.at((x, -6.5, FL)):
                table2(m, top="white", seat="frosting_pink")
    with m.group("Roof"):
        m.torus(R=3.0, r=1.4, seg=8, rseg=6, color=lambda c, n: "frosting_pink" if c.y < -0.3 else "donut",
                rot=(90, 0, 0), loc=(0, -D / 2 + 5.0, zt + 5.6))
        for a in range(0, 360, 40):
            r = math.radians(a)
            blk(m, (0.5, 0.3, 0.2), (3.0 * math.cos(r), -D / 2 + 3.4, zt + 5.6 + 3.0 * math.sin(r)),
                ["sprinkle_blue", "sprinkle_yellow", "white"][a // 40 % 3], rot=(0, a, 0))
        blk(m, (0.8, 0.8, 2.6), (0, -D / 2 + 5.0, zt + 1.3), "charcoal")


reg("DonutShop", _donut_shop)


# ----------------------------------------------------------------------------
# bank
# ----------------------------------------------------------------------------
def atm(m, col="plastic_blue"):
    blk(m, (2.4, 2.0, 6.0), (0, 0, 3.0), "stainless", bev=0.1)
    blk(m, (2.4, 2.0, 1.0), (0, 0, 6.4), col, bev=0.1)
    text(m, "ATM", 0, -1.02, 6.4, px=0.2, depth=0.08, col="white")
    blk(m, (1.6, 0.1, 1.2), (0, -1.02, 4.6), "screen_glow", rot=(-10, 0, 0))
    blk(m, (1.8, 0.8, 0.2), (0, -1.2, 3.5), "charcoal", rot=(-20, 0, 0))
    blk(m, (0.8, 0.1, 0.15), (0, -1.02, 3.0), "black")
    blk(m, (0.6, 0.1, 0.15), (0, -1.02, 5.6), "black")


fix("BankATM", atm, sub="FixturesBank")


def column(m, x, y, z0, z1, r=0.9, col="marble", cap="marble"):
    blk(m, (2.4, 2.4, 0.6), (x, y, z0 + 0.3), cap, bev=0.08)
    m.cyl(r=r, h=z1 - z0 - 1.2, seg=8, color=col, loc=(x, y, (z0 + z1) / 2))
    blk(m, (2.4, 2.4, 0.6), (x, y, z1 - 0.3), cap, bev=0.08)


def _grand_bank(m):
    W, D, H = 44.0, 40.0, 15.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "marble_dark"), (None, "marble")],
                   inn=[(FL + 3.0, "marble_green"), (FL + 3.4, "brass"), (FL + H, "wall_cream"), (None, "marble")],
                   trim="marble", cornice="marble", flo=("marble", "marble_dark", 3.0, False), frame="brass",
                   door_w=7.0, door_panel="wood_dark", win=(FL + 3.0, FL + 11.0), back_door=None, lights=(3, 3),
                   units=((-12.0, 14.0), (12.0, 14.0)), sill="marble_dark")
    zt, iy, Y0 = b["zt"], b["iy"], b["Y0"]
    # classical portico: steps, six columns, entablature with the name and a pediment
    for k in range(3):
        blk(m, (W - 4.0 - k * 2.0, 1.4, 0.5), (0, Y0 - 7.8 + k * 1.2, 0.25 + k * 0.5), "marble", bev=0.05)
    for x in (-19.0, -12.0, -5.2, 5.2, 12.0, 19.0):
        column(m, x, Y0 - 4.0, 0.5, zt + 1.0)
    blk(m, (W + 2.0, 8.0, 2.2), (0, Y0 - 3.6, zt + 2.1), "marble", bev=0.1)
    text(m, "BANK", 0, Y0 - 7.62, zt + 2.1, px=0.36, depth=0.25, col="brass")
    m.prism([(-(W / 2 + 1.0), 0), (W / 2 + 1.0, 0), (0, 5.0)], depth=8.0, color="marble", rot=(90, 0, 0),
            loc=(0, Y0 - 3.6, zt + 3.2), smooth=False)
    m.prism([(-5.0, 0), (5.0, 0), (0, 2.6)], depth=0.3, color="brass", rot=(90, 0, 0), loc=(0, Y0 - 7.7, zt + 3.6))
    # vault partition with a staff door; the vault door itself stands in front of the opening
    wall(m, "x", 10.5, -W / 2 + T, W / 2 - T, FL, zt, -1, [(FL + 3.0, "marble_green"), (None, "wall_cream")],
         "vault", "marble", holes=[(-4.2, 4.2, FL, FL + 8.8), (15.0, 18.5, FL, FL + 8.0)], t=0.8, zcuts=(FL + 3.0,))
    with m.group("Vault"):
        with m.at((0.0, 9.2, FL)):
            vault_door(m, 4.0)
        for x in (-14.0, 14.0):
            with m.at((x, iy - 1.0, FL)):
                deposit_boxes(m, 10.0, 9.0)
        for x, kind in ((-6.0, "cash"), (-2.0, "gold"), (2.0, "cash"), (6.0, "gold")):
            with m.at((x, 14.5, FL)):
                money_pallet(m, kind)
        for x in (-3.0, 3.0):
            with m.at((x, 18.0, FL)):
                money_pallet(m, "cash")
    with m.group("StaffDoor"):
        blk(m, (3.3, 0.3, 7.8), (16.75, 10.5, FL + 3.9), "wood_dark", bev=0.05)
    with m.group("Tellers"):
        with m.at((0.0, 2.0, FL)):
            teller_desk(m, 26.0, 5)
        for i in range(5):
            with m.at((-10.4 + i * 5.2, 5.2, FL)):
                m.cyl(r=1.0, h=0.2, seg=5, color="charcoal", loc=(0, 0, 0.3))
                blk(m, (0.25, 0.25, 1.9), (0, 0, 1.3), "chrome")
                blk(m, (1.8, 1.8, 0.4), (0, 0, 2.4), "leather_dark", bev=0.12)
                blk(m, (1.8, 0.4, 2.0), (0, 0.8, 3.5), "leather_dark", bev=0.12)
    with m.group("Lobby"):
        with m.at((0.0, -7.0, FL)):
            queue_posts(m, 13.2, 2)
        for y in (-14.0, -6.0):
            with m.at((-W / 2 + T + 1.2, y, FL), 90):
                bench_seat(m, 6.0)
        for x, y in ((14.0, -12.0), (14.0, -4.0)):
            with m.at((x, y, FL), 90):
                office_desk(m, chair_col="leather_dark")
        with m.at((W / 2 - T - 1.2, -16.0, FL), -90):
            atm(m)
        for x, y in ((-19.5, -17.5), (19.5, 0.5), (-19.5, 0.5)):
            potted_plant(m, x, y, h=4.0)
        blk(m, (12.0, 8.0, 0.08), (0, -13.0, FL + 0.04), "velvet")
    with m.group("Roof"):
        for y in (-12.0, -3.0):
            blk(m, (0.12, 0.12, 2.0), (0, y, zt - 1.0), "brass")
            m.torus(R=1.8, r=0.15, seg=8, color="brass", loc=(0, y, zt - 2.6))
            for a in range(0, 360, 45):
                r = math.radians(a)
                m.cyl(r=0.12, h=0.6, seg=4, color="offwhite", loc=(1.8 * math.cos(r), y + 1.8 * math.sin(r), zt - 2.2))
                blk(m, (0.25, 0.25, 0.3), (1.8 * math.cos(r), y + 1.8 * math.sin(r), zt - 1.75), "glow")
    with m.group("Security"):
        for x, y in ((-20.5, -18.5), (20.5, -18.5), (-20.5, 9.5), (20.5, 9.5)):
            blk(m, (0.8, 1.2, 0.6), (x, y, zt - 1.2), "white", bev=0.1)
            blk(m, (0.3, 0.3, 0.3), (x, y - 0.7 if y < 0 else y - 0.7, zt - 1.2), "black")
    with m.at((W / 2 + 1.0, -D / 2 - 3.0, 0.5), 180):
        atm(m, "wall_green")


reg("GrandBank", _grand_bank, sub="Bank")


# ----------------------------------------------------------------------------
# stores
# ----------------------------------------------------------------------------
def _supermarket(m):
    W, D, H = 64.0, 48.0, 14.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "brick_dark"), (FL + 12.0, "white"), (None, "plastic_green")],
                   inn=[(FL + 3.0, "plastic_green"), (FL + H, "white"), (None, "concrete")], trim="white",
                   cornice="plastic_green", flo=("tile_white", "tile_gray", 3.0, False), frame="stainless",
                   door_w=8.0, sign_txt="SUPERMARKET", board="plastic_green", letters="white", px=0.7,
                   sign_trim="white", back_door=24.0, lights=(6, 5),
                   units=((-18.0, 8.0), (-4.0, 10.0), (10.0, 8.0), (22.0, 12.0)), win=(FL + 2.0, FL + 11.0))
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Checkouts"):
        for x in (-26.0, -19.0, -12.0):
            with m.at((x, -14.0, FL), 90):
                checkout(m)
    with m.group("Produce"):
        for x, fr in ((14.0, ("apple_red", "orange", "banana", "lime", "grape", "lemon")),
                      (24.0, ("tomato", "carrot", "broccoli", "eggplant", "potato", "cabbage"))):
            with m.at((x, -15.0, FL)):
                produce_stand(m, 8.0, fr)
        with m.at((19.0, -8.5, FL)):
            produce_stand(m, 8.0, ("watermelon", "pineapple", "coconut", "peach", "pear", "strawberry"))
    with m.group("Aisles"):
        for i, x in enumerate((-24.0, -16.0, -8.0, 0.0, 8.0, 16.0)):
            with m.at((x, 5.5, FL), 90):
                gondola(m, 18.0, seed=30 + i, levels=4, h=6.5)
    with m.group("Coolers"):
        with m.at((-14.0, iy - 1.4, FL)):
            cooler_wall(m, 26.0, 8.0, seed=41)
        for x in (6.0, 15.0):
            with m.at((x, iy - 2.0, FL)):
                freezer_chest(m, 8.0, seed=int(x))
    with m.group("Deli"):
        with m.at((ix - 1.3, 4.0, FL), -90):
            pastry_case(m, 6.0)
        with m.at((ix - 1.3, 11.0, FL), -90):
            counter(m, 7.0, top="stainless", body="white")
        with m.at((ix - 1.3, -3.0, FL), -90):
            freezer_chest(m, 6.0, seed=7)
    with m.group("Carts"):
        for k in range(4):
            with m.at((6.0 + k * 0.9, -20.5, FL)):
                cart(m, "plastic_red" if k % 2 else "plastic_green")
    with m.group("AisleSigns"):
        for i, x in enumerate((-24.0, -16.0, -8.0, 0.0, 8.0, 16.0)):
            blk(m, (0.1, 0.1, 3.0), (x, 5.5, zt - 1.5), "charcoal")
            blk(m, (3.4, 0.3, 1.6), (x, 5.5, zt - 3.8), "plastic_green", bev=0.06)
            text(m, str(i + 1), x, 5.3, zt - 3.8, px=0.22, depth=0.1, col="white")


reg("Supermarket", _supermarket, sub="Stores")


def _convenience_store(m):
    W, D, H = 32.0, 24.0, 11.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "charcoal"), (FL + 9.4, "white"), (FL + 10.0, "plastic_orange"),
                                    (FL + 10.6, "plastic_green"), (FL + 11.2, "wall_red"), (None, "white")],
                   inn=[(FL + 3.0, "tile_gray"), (FL + H, "white"), (None, "concrete")], trim="white",
                   cornice="plastic_green", flo=("tile_white", "tile_cream", 2.0, False), frame="stainless",
                   sign_txt="24/7", board="plastic_green", letters="white", px=0.7, sign_trim="plastic_orange",
                   back_door=12.0, lights=(4, 3), units=((-6.0, 3.0),), win=(FL + 2.0, FL + 9.0))
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Counter"):
        with m.at((-ix + 1.3, -5.0, FL), 90):
            counter(m, 8.0, top="white", body="plastic_green", front_col="plastic_orange")
        register(m, -ix + 1.4, -6.5, FL + 3.5)
        with m.at((-ix + 1.5, 3.0, FL), 90):
            counter(m, 5.0, top="white", body="white")
            slushie(m)
        with m.at((-ix + 0.8, -5.0, FL + 6.0), 90):
            blk(m, (6.0, 0.8, 3.0), (0, 0.2, 0), "white")
            for i in range(6):
                for k in range(3):
                    blk(m, (0.7, 0.4, 0.7), (-2.4 + i * 0.95, -0.3, -0.9 + k * 0.9), ["chocolate", "plastic_red",
                                                                                       "candy_blue"][(i + k) % 3])
    with m.group("Aisles"):
        for i, y in enumerate((-4.0, 3.0)):
            with m.at((3.0, y, FL)):
                gondola(m, 12.0, seed=50 + i, levels=4, h=5.5)
    with m.group("Coolers"):
        with m.at((3.0, iy - 1.4, FL)):
            cooler_wall(m, 18.0, 8.0, seed=52)
        with m.at((ix - 1.6, -4.0, FL), -90):
            freezer_chest(m, 6.0, seed=53)
        with m.at((ix - 1.2, 4.0, FL), -90):
            atm(m, "plastic_orange")
    with m.group("Sign"):
        with m.at((W / 2 + 3.0, -D / 2 - 4.0, 0.5)):
            blk(m, (0.8, 0.8, 12.0), (0, 0, 6.0), "charcoal")
            blk(m, (6.0, 0.8, 4.0), (0, 0, 13.0), "plastic_green", bev=0.1)
            text(m, "24/7", 0, -0.42, 13.0, px=0.4, depth=0.1, col="white")


reg("ConvenienceStore", _convenience_store, sub="Stores")


def _clothing_store(m):
    W, D, H = 36.0, 30.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "black"), (None, "white")], inn="white", wains="wood_light",
                   trim="black", cornice="black", flo=("wood_pale", "wood_light", 1.0, True), frame="black",
                   sign_txt="FASHION", board="black", letters="white", px=0.6, awning=("black", "white"),
                   back_door=13.0, win=(FL + 1.5, FL + 10.0))
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Window"):
        for x, (sh, pa) in ((-13.0, ("fabric_red", "fabric_navy")), (-9.0, ("fabric_yellow", "fabric_gray")),
                            (9.0, ("fabric_pink", "fabric_white")), (13.0, ("fabric_teal", "fabric_navy"))):
            with m.at((x, -D / 2 + T + 2.0, FL)):
                blk(m, (3.0, 3.0, 0.6), (0, 0, 0.3), "white", bev=0.05)
                with m.at((0, 0, 0.6)):
                    mannequin(m, sh, pa)
    with m.group("Racks"):
        for i, (x, y) in enumerate(((-10.0, -4.0), (0.0, -4.0), (10.0, -4.0), (-10.0, 3.0), (0.0, 3.0), (10.0, 3.0))):
            with m.at((x, y, FL)):
                clothes_rack(m, 6.0, seed=60 + i)
    with m.group("Shelves"):
        for y in (-6.0, 2.0):
            with m.at((-ix + 0.9, y, FL), 90):
                folded_shelf(m, 7.0, seed=int(y) + 70)
    with m.group("FittingRooms"):
        for x in (-12.0, -7.8, -3.6):
            with m.at((x, iy - 2.2, FL)):
                fitting_room(m)
    with m.group("Counter"):
        with m.at((10.0, 9.0, FL)):
            counter(m, 8.0, top="white", body="black")
        register(m, 10.0, 9.2, FL + 3.5)
        with m.at((ix - 0.6, 2.0, FL), -90):
            blk(m, (3.0, 0.3, 7.0), (0, 0, 4.5), "glass")
            blk(m, (3.4, 0.4, 7.4), (0, 0.1, 4.5), "black")
        with m.at((2.0, 11.0, FL)):
            bench_seat(m, 5.0, "fabric_gray")
        blk(m, (10.0, 6.0, 0.08), (0, -0.5, FL + 0.04), "rug_red")
    with m.group("Roof"):
        for x in (-10.0, 0.0, 10.0):
            pendant(m, x, -0.5, zt, col="glow", shade="black")


reg("ClothingStore", _clothing_store, sub="Stores")


def _electronics_store(m):
    W, D, H = 38.0, 30.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "charcoal"), (None, "wall_navy")], inn="white", wains="plastic_blue",
                   trim="charcoal", cornice="plastic_blue", flo=("tile_white", "tile_gray", 2.0, False),
                   frame="charcoal", sign_txt="ELECTRONICS", board="plastic_blue", letters="white", px=0.5,
                   sign_trim="charcoal", back_door=14.0, light_col="glow")
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("TVs"):
        with m.at((-8.0, iy - 0.6, FL)):
            tv_wall(m, 18.0, 7.5, seed=80)
        with m.at((-ix + 0.6, 0.0, FL), 90):
            tv_wall(m, 12.0, 7.0, seed=81)
    with m.group("Tables"):
        for i, (x, y, it) in enumerate(((-7.0, -6.0, "laptop"), (4.0, -6.0, "phone"), (-7.0, 1.5, "laptop"),
                                        (4.0, 1.5, "phone"))):
            with m.at((x, y, FL)):
                display_table(m, 7.0, it, seed=90 + i)
    with m.group("Games"):
        with m.at((10.0, iy - 1.4, FL)):
            gondola(m, 12.0, seed=95, levels=4, both=False, h=6.5)
    with m.group("Counter"):
        with m.at((ix - 1.3, -6.0, FL), -90):
            counter(m, 8.0, top="white", body="plastic_blue")
        register(m, ix - 1.4, -7.5, FL + 3.5)
        with m.at((ix - 1.2, 3.0, FL), -90):
            for k in range(3):
                blk(m, (1.6, 1.4, 2.4), (-2.0 + k * 2.0, 0, 1.2), "charcoal", bev=0.2)
                m.cyl(r=0.5, h=0.1, seg=8, color="gray", rot=(90, 0, 0), loc=(-2.0 + k * 2.0, -0.72, 1.6))


reg("ElectronicsStore", _electronics_store, sub="Stores")


def _jewelry_store(m):
    W, D, H = 28.0, 24.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "marble_dark"), (None, "marble")], inn="wall_cream", wains="velvet",
                   trim="brass", cornice="brass", flo=("marble", "marble_dark", 2.0, False), frame="brass",
                   sign_txt="JEWELRY", board="black", letters="gold", px=0.55, sign_trim="brass",
                   awning=("black", "white"), back_door=9.0, lights=(3, 3), sill="marble_dark")
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Cases"):
        for x in (-4.0, 4.0):
            with m.at((x, 5.0, FL)):
                jewelry_case(m, 7.0, seed=int(x) + 100)
        for s in (-1, 1):
            with m.at((s * 8.5, -2.5, FL), -90 * s):
                jewelry_case(m, 7.0, seed=110 + s)
    with m.group("Back"):
        with m.at((-8.0, iy - 1.2, FL)):
            blk(m, (4.0, 2.4, 6.0), (0, 0, 3.0), "vault", bev=0.1)
            m.cyl(r=0.8, h=0.3, seg=8, color="brass", rot=(90, 0, 0), loc=(0, -1.3, 3.4))
        with m.at((6.0, iy - 0.4, FL + 4.0)):
            blk(m, (6.0, 0.3, 4.0), (0, 0, 0), "glass")
            blk(m, (6.4, 0.4, 4.4), (0, 0.1, 0), "brass")
        with m.at((0.0, -8.0, FL)):
            for x in (-3.0, 3.0):
                m.cyl(r=0.4, h=0.2, seg=8, color="brass", loc=(x, 0, 0.1))
                m.cyl(r=0.1, h=3.0, seg=6, color="brass", loc=(x, 0, 1.6))
            m.tube([(-3.0, 0, 2.9), (0, 0, 2.2), (3.0, 0, 2.9)], [0.1, 0.1, 0.1], seg=4, color="velvet")
    with m.group("Roof"):
        blk(m, (0.12, 0.12, 2.0), (0, 0, zt - 1.0), "brass")
        for r_, z in ((2.0, zt - 2.4), (1.2, zt - 3.2)):
            m.torus(R=r_, r=0.15, seg=8, color="brass", loc=(0, 0, z))
            for a in range(0, 360, 45):
                r = math.radians(a)
                blk(m, (0.3, 0.3, 0.6), (r_ * math.cos(r), r_ * math.sin(r), z - 0.4), "diamond", rot=(45, 0, 45))


reg("JewelryStore", _jewelry_store, sub="Stores")


def _pet_store(m):
    W, D, H = 34.0, 28.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "wood_mid"), (None, "wall_sky")], inn="wall_mint", wains="wood_light",
                   trim="white", cornice="plastic_orange", flo=("tile_cream", "tile_white", 2.0, False), frame="white",
                   sign_txt="PET STORE", board="plastic_orange", letters="white", px=0.5, sign_trim="white",
                   awning=("plastic_orange", "white"), back_door=12.0)
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("FishTanks"):
        with m.at((-ix + 1.3, 1.0, FL), 90):
            fish_tank_row(m, 13.0, seed=120)
    with m.group("Cages"):
        with m.at((ix - 1.4, 1.0, FL), -90):
            pet_cages(m, 13.0, seed=121)
    with m.group("Shelves"):
        with m.at((0.0, 1.0, FL)):
            gondola(m, 12.0, seed=122, levels=3, h=5.0)
        with m.at((-2.0, iy - 1.4, FL)):
            gondola(m, 14.0, seed=123, levels=4, both=False, h=6.5)
    with m.group("Counter"):
        with m.at((-8.0, -7.0, FL)):
            counter(m, 7.0, top="white", body="plastic_orange")
        register(m, -8.0, -6.8, FL + 3.5)
    with m.group("PetStuff"):
        with m.at((8.0, -8.0, FL)):   # cat tree
            blk(m, (3.0, 3.0, 0.5), (0, 0, 0.25), "fabric_cream")
            for x, y, h in ((-0.8, -0.8, 5.0), (0.9, 0.7, 3.4)):
                blk(m, (0.6, 0.6, h), (x, y, h / 2), "rope")
                blk(m, (2.0, 2.0, 0.4), (x, y, h + 0.2), "fabric_cream", bev=0.1)
            blk(m, (1.8, 1.8, 1.6), (0.9, 0.7, 4.4), "fabric_cream", bev=0.2)
            blk(m, (0.8, 0.1, 0.8), (0.9, -0.2, 4.3), "black")
        with m.at((3.0, -9.0, FL)):   # dog bed
            blk(m, (3.4, 2.6, 0.8), (0, 0, 0.4), "fabric_red", bev=0.3)
            blk(m, (2.6, 1.8, 0.3), (0, 0, 0.75), "fabric_cream", bev=0.1)
        with m.at((12.0, -10.5, FL + 5.0)):   # hanging bird cage
            blk(m, (0.1, 0.1, 6.0), (0, 0, 5.0), "charcoal")
            m.cyl(r=1.0, h=2.2, seg=8, color="brass", loc=(0, 0, 1.1), caps=False)
            m.cyl(r=1.05, h=0.2, seg=8, color="brass", loc=(0, 0, 0))
            m.cone(r=1.05, h=0.8, seg=8, color="brass", loc=(0, 0, 2.2))
            blk(m, (0.5, 0.6, 0.5), (0, 0, 0.9), "plastic_yellow", bev=0.1)


reg("PetStore", _pet_store, sub="Stores")


# ----------------------------------------------------------------------------
# gym, arcade, office
# ----------------------------------------------------------------------------
def boxing_ring(m, s=12.0):
    blk(m, (s, s, 1.6), (0, 0, 0.8), "charcoal", bev=0.1)
    blk(m, (s - 0.4, s - 0.4, 0.2), (0, 0, 1.7), "plastic_blue")
    for sx in (-1, 1):
        for sy in (-1, 1):
            blk(m, (0.5, 0.5, 4.2), (sx * (s / 2 - 0.3), sy * (s / 2 - 0.3), 3.7), "plastic_red" if sx == sy else "plastic_blue")
    for z in (2.8, 3.8, 4.8):
        for sy in (-1, 1):
            blk(m, (s - 0.6, 0.15, 0.15), (0, sy * (s / 2 - 0.3), z), "white")
            blk(m, (0.15, s - 0.6, 0.15), (sy * (s / 2 - 0.3), 0, z), "white")


fix("BoxingRing", boxing_ring, sub="FixturesGym")


def _gym(m):
    W, D, H = 46.0, 36.0, 14.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "black"), (None, "charcoal")], inn=[(FL + 3.0, "charcoal"),
                   (FL + H, "wall_sky"), (None, "concrete")], trim="wall_red", cornice="wall_red",
                   flo=("rubber", "rubber", 2.0, False), frame="charcoal", sign_txt="GYM", board="wall_red",
                   letters="white", px=1.0, sign_trim="black", back_door=16.0, lights=(5, 4), win=(FL + 2.0, FL + 11.0))
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Cardio"):
        for i in range(5):
            with m.at((-18.0 + i * 3.6, -12.0, FL)):
                treadmill(m)
    with m.group("Weights"):
        blk(m, (0.3, 22.0, 8.0), (ix - 0.15, 0.0, FL + 5.0), "glass")        # mirror wall
        for y in (-7.0, 1.0, 9.0):
            with m.at((ix - 1.4, y, FL), -90):
                weight_rack(m, 7.0)
        for x, y in ((6.0, -4.0), (6.0, 4.0), (12.0, 0.0)):
            with m.at((x, y, FL)):
                bench_press(m)
        blk(m, (12.0, 20.0, 0.1), (10.0, 0.0, FL + 0.05), "wall_navy")
    with m.group("Boxing"):
        with m.at((-12.0, 8.0, FL)):
            boxing_ring(m, 12.0)
        for y in (-3.0, 0.5):
            with m.at((-ix + 2.0, y, FL)):
                punching_bag(m, H)
    with m.group("FrontDesk"):
        with m.at((15.0, -12.0, FL)):
            counter(m, 8.0, top="white", body="wall_red")
        register(m, 15.0, -11.8, FL + 3.5)
        with m.at((20.0, -14.5, FL), -90):
            water_cooler(m)
    with m.group("Lockers"):
        for i in range(8):
            with m.at((6.0 + i * 1.6, iy - 0.9, FL)):
                blk(m, (1.5, 1.6, 7.0), (0, 0, 3.5), "plastic_blue" if i % 2 else "wall_navy", bev=0.05)
                for z in (2.0, 5.5):
                    blk(m, (1.0, 0.1, 0.12), (0, -0.82, z), "charcoal")
                blk(m, (0.15, 0.1, 0.4), (0.5, -0.82, 3.6), "stainless")
        with m.at((12.0, iy - 3.5, FL)):
            bench_seat(m, 8.0, "wall_red")


reg("Gym", _gym, sub="Leisure")


def air_hockey(m):
    blk(m, (4.0, 7.0, 2.8), (0, 0, 1.4), "plastic_blue", bev=0.1)
    blk(m, (3.6, 6.6, 0.1), (0, 0, 2.85), "white")
    blk(m, (3.6, 0.1, 0.02), (0, 0, 2.92), "plastic_red")
    for y in (-2.6, 2.6):
        m.cyl(r=0.35, h=0.4, seg=8, color="plastic_red" if y < 0 else "plastic_yellow", loc=(0, y, 3.1))
    m.cyl(r=0.25, h=0.1, seg=8, color="black", loc=(0.5, 0.8, 2.95))


fix("AirHockey", air_hockey, sub="FixturesArcade")


def _arcade_hall(m):
    W, D, H = 40.0, 32.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "black"), (None, "wall_navy")], inn=[(FL + 3.0, "black"),
                   (FL + H, "wall_navy"), (None, "concrete")], trim="neon_purple", cornice="neon_purple",
                   flo=("wall_navy", "wall_navy", 2.0, False), frame="black", sign_txt="ARCADE", board="black",
                   letters="neon_pink", px=0.7, sign_trim="neon_blue", back_door=14.0, light_col="neon_purple",
                   win=(FL + 3.0, FL + 9.0))
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    cols = ["plastic_blue", "plastic_red", "plastic_purple", "plastic_green", "plastic_orange", "black"]
    scr = ["neon_purple", "neon_green", "neon_blue", "neon_pink", "neon_yellow", "screen_glow"]
    with m.group("Cabinets"):
        for i in range(7):
            with m.at((-15.0 + i * 3.0, iy - 1.4, FL)):
                arcade_cab(m, cols[i % 6], scr[i % 6])
        for i in range(5):
            for s, ang in ((-1, 0), (1, 180)):
                with m.at((-9.0 + i * 3.0, 2.0 + s * 1.5, FL), ang):
                    arcade_cab(m, cols[(i + s) % 6], scr[(i + 2) % 6])
    with m.group("Claws"):
        for i in range(4):
            with m.at((-ix + 1.8, -9.0 + i * 3.6, FL), 90):
                claw_machine(m, ["plastic_pink", "plastic_blue", "plastic_yellow", "plastic_green"][i])
    with m.group("Prizes"):
        with m.at((ix - 1.4, 2.0, FL), -90):
            counter(m, 10.0, top="glass", body="black", front_col="neon_purple")
            blk(m, (10.0, 1.4, 8.0), (0, 2.2, 4.0), "black")
            rnd = random.Random(140)
            for k in range(3):
                blk(m, (10.0, 1.4, 0.15), (0, 1.8, 3.8 + k * 1.8), "white")
                for j in range(7):
                    blk(m, (0.9, 0.9, 0.9), (-4.2 + j * 1.4, 1.6, 4.4 + k * 1.8),
                        rnd.choice(["fur_white", "plastic_yellow", "frosting_pink", "neon_blue", "fur_orange"]), bev=0.25)
        register(m, ix - 1.6, -1.0, FL + 3.5)
    with m.group("Games"):
        with m.at((6.0, -8.0, FL)):
            air_hockey(m)
        with m.at((-4.0, -9.0, FL)):
            blk(m, (1.8, 1.8, 5.0), (0, 0, 2.5), "stainless", bev=0.1)
            blk(m, (1.2, 0.1, 0.8), (0, -0.92, 3.8), "screen_glow")
            text(m, "$", 0, -0.95, 2.4, px=0.18, depth=0.08, col="neon_green")


reg("ArcadeHall", _arcade_hall, sub="Leisure")


def glass_partition(m, axis, fixed, a0, a1, z0=FL, h=9.0, door=None):
    holes = [door] if door else []
    cur = a0
    segs = []
    for d in sorted(holes):
        segs.append((cur, d[0]))
        cur = d[1]
    segs.append((cur, a1))
    for sa, sb in segs:
        _wbox(m, axis, fixed, (sa + sb) / 2, 0, z0 + h / 2, sb - sa, 0.3, h, "stainless")
        with m.group("Glass"):
            _wbox(m, axis, fixed, (sa + sb) / 2, 0, z0 + h / 2 + 0.3, sb - sa - 0.3, 0.4, h - 1.2, "glass")
    _wbox(m, axis, fixed, (a0 + a1) / 2, 0, z0 + h + 0.2, a1 - a0, 0.5, 0.4, "stainless")


def _office(m):
    W, D, H = 44.0, 36.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "stone_dark"), (None, "concrete")], inn="white", wains="fabric_gray",
                   trim="concrete", cornice="concrete_dark", flo=("fabric_gray", "fabric_gray", 2.0, False),
                   frame="charcoal", sign_txt="OFFICE", board="wall_navy", letters="white", px=0.6,
                   back_door=16.0, lights=(5, 4), win=(FL + 2.5, FL + 10.5))
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Reception"):
        with m.at((0.0, -9.0, FL)):
            counter(m, 9.0, top="white", body="wood_mid", front_col="wall_navy")
        with m.at((1.0, -7.5, FL + 3.5)):
            blk(m, (1.6, 0.2, 1.2), (0, 0, 0.8), "black")
        for x in (-12.0, -8.0):
            with m.at((x, -14.0, FL), 180):
                armchair_c(m, "fabric_navy")
        potted_plant(m, -16.0, -15.0, h=4.0)
        potted_plant(m, 16.0, -15.0, h=4.0)
    with m.group("Cubicles"):
        for i in range(3):
            for j in range(2):
                with m.at((-17.0 + i * 7.5, 0.5 + j * 8.0, FL)):
                    cubicle(m, 7.0, 7.0, panel=["fabric_gray", "fabric_blue"][j])
    with m.group("MeetingRoom"):
        glass_partition(m, "x", 3.5, 5.0, ix, door=(7.0, 10.0))
        glass_partition(m, "y", 5.0, 3.5, iy)
        with m.at((13.0, 10.5, FL)):
            blk(m, (10.0, 4.4, 0.3), (0, 0, 3.0), "wood_dark", bev=0.06)
            for x in (-3.5, 3.5):
                blk(m, (0.6, 3.0, 2.8), (x, 0, 1.4), "charcoal")
            for x in (-3.6, -1.2, 1.2, 3.6):
                for s in (-1, 1):
                    with m.at((x, s * 3.3, 0), 0 if s > 0 else 180):
                        m.cyl(r=0.9, h=0.2, seg=5, color="charcoal", loc=(0, 0, 0.3))
                        blk(m, (0.2, 0.2, 1.6), (0, 0, 1.2), "chrome")
                        blk(m, (1.6, 1.6, 0.35), (0, 0, 2.1), "leather_dark", bev=0.1)
                        blk(m, (1.6, 0.35, 1.8), (0, 0.7, 3.1), "leather_dark", bev=0.1)
        with m.at((13.0, iy - 0.3, FL + 5.5)):
            blk(m, (8.0, 0.3, 4.2), (0, 0, 0), "black")
            blk(m, (7.6, 0.1, 3.8), (0, -0.2, 0), "screen_glow")
    with m.group("Services"):
        with m.at((ix - 1.2, -6.0, FL), -90):
            water_cooler(m)
        with m.at((ix - 1.6, -2.0, FL), -90):
            printer(m)
        with m.at((12.0, -12.0, FL), 180):
            office_desk(m, chair_col="leather_dark")


reg("Office", _office, sub="Leisure")


# ----------------------------------------------------------------------------
# more services: pharmacy, hair salon, laundromat, movie theater
# ----------------------------------------------------------------------------
def salon_chair(m, col="leather_dark"):
    m.cyl(r=1.0, h=0.2, seg=8, color="chrome", loc=(0, 0, 0.1))
    m.cyl(r=0.3, h=1.4, seg=6, color="chrome", loc=(0, 0, 0.9))
    blk(m, (2.2, 2.2, 0.6), (0, 0, 1.9), col, bev=0.15)
    blk(m, (2.2, 0.5, 2.8), (0, 0.9, 3.4), col, bev=0.15)
    blk(m, (1.2, 0.4, 0.8), (0, 1.0, 5.1), col, bev=0.15)
    for s in (-1, 1):
        blk(m, (0.3, 1.8, 0.3), (s * 1.2, 0, 2.8), "chrome")
    blk(m, (1.2, 0.8, 0.2), (0, -1.6, 0.5), "chrome", rot=(20, 0, 0))


def salon_station(m):
    """Mirror + shelf on the wall (face -Y) with a styling chair in front."""
    blk(m, (4.0, 0.3, 5.0), (0, 0.2, 6.0), "glass")
    blk(m, (4.4, 0.4, 5.4), (0, 0.35, 6.0), "wood_dark")
    blk(m, (4.0, 1.2, 0.3), (0, -0.4, 3.4), "wood_light")
    for i, c in enumerate(("potion_blue", "potion_red", "white", "plastic_pink")):
        m.cyl(r=0.18, h=0.7, seg=6, color=c, loc=(-1.4 + i * 0.6, -0.5, 3.9))
    blk(m, (0.8, 0.6, 0.4), (1.2, -0.5, 3.75), "charcoal")      # hair dryer
    with m.at((0, -2.8, 0)):
        salon_chair(m)


def washer(m, dryer=False):
    blk(m, (2.6, 2.6, 3.2), (0, 0, 1.6), "white", bev=0.12)
    blk(m, (2.6, 0.5, 0.6), (0, 1.0, 3.5), "white", bev=0.08)
    m.cyl(r=0.9, h=0.2, seg=8, color="chrome", rot=(90, 0, 0), loc=(0, -1.35, 1.6))
    m.cyl(r=0.7, h=0.1, seg=8, color="charcoal" if dryer else "glass", rot=(90, 0, 0), loc=(0, -1.45, 1.6))
    blk(m, (0.7, 0.1, 0.3), (-0.6, 0.72, 3.5), "screen_glow")
    m.cyl(r=0.15, h=0.1, seg=6, color="charcoal", rot=(90, 0, 0), loc=(0.6, 0.72, 3.5))


def theater_seat(m, col="velvet"):
    blk(m, (1.8, 1.8, 0.5), (0, 0, 1.4), col, bev=0.12)
    blk(m, (1.8, 0.4, 2.2), (0, 0.8, 2.5), col, bev=0.12)
    for s in (-1, 1):
        blk(m, (0.25, 1.8, 1.9), (s * 1.0, 0, 0.95), "charcoal")
        m.cyl(r=0.2, h=0.4, seg=6, color="charcoal", loc=(s * 1.0, -0.6, 2.0))


def seat_rows(m, rows=5, per=8, col="velvet", step_h=0.8, pitch=3.2):
    for r in range(rows):
        z = r * step_h
        if r:
            blk(m, (per * 2.1 + 1.0, pitch, step_h), (0, r * pitch, z - step_h / 2), "wall_navy")
        for i in range(per):
            with m.at((-(per - 1) * 1.05 + i * 2.1, r * pitch, z)):
                theater_seat(m, col)


for _n, _f in (("SalonChair", salon_chair), ("SalonStation", salon_station), ("Washer", washer),
               ("CoinDryer", lambda m: washer(m, True)), ("TheaterSeat", theater_seat),
               ("TheaterSeatRows", lambda m: seat_rows(m, 3, 6))):
    fix(_n, _f, sub="FixturesServices")


def _pharmacy(m):
    W, D, H = 36.0, 30.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "stone_dark"), (None, "white")], inn="white", wains="plastic_green",
                   trim="plastic_green", cornice="plastic_green", flo=("tile_white", "tile_gray", 2.0, False),
                   frame="stainless", sign_txt="PHARMACY", board="plastic_green", letters="white", px=0.55,
                   sign_trim="white", back_door=13.0)
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Sign"):
        blk(m, (3.0, 0.4, 1.0), (-W / 2 + 4.0, -D / 2 - 0.5, zt + 1.0), "neon_green")
        blk(m, (1.0, 0.4, 3.0), (-W / 2 + 4.0, -D / 2 - 0.5, zt + 1.0), "neon_green")
    with m.group("Aisles"):
        for i, y in enumerate((-4.0, 2.0)):
            with m.at((-4.0, y, FL)):
                gondola(m, 14.0, seed=150 + i, levels=4, h=5.5)
        with m.at((-ix + 1.0, 1.0, FL), 90):
            gondola(m, 14.0, seed=153, levels=4, both=False, h=6.5)
    with m.group("Counter"):
        with m.at((6.0, iy - 5.0, FL)):
            counter(m, 14.0, top="white", body="plastic_green")
        for x in (2.0, 9.0):
            register(m, x, iy - 4.8, FL + 3.5)
        with m.at((6.0, iy - 1.2, FL)):
            gondola(m, 14.0, seed=155, levels=5, both=False, h=7.5)
        blk(m, (14.0, 0.3, 1.2), (6.0, iy - 5.5, FL + 8.5), "plastic_green")
        text(m, "RX", 6.0, iy - 5.7, FL + 8.5, px=0.18, depth=0.06, col="white")
    with m.group("Seating"):
        with m.at((ix - 1.2, -6.0, FL), -90):
            bench_seat(m, 6.0, "plastic_blue")
        with m.at((ix - 1.2, 1.0, FL), -90):
            cooler_wall(m, 6.0, 7.0, seed=156)


reg("Pharmacy", _pharmacy, sub="Stores")


def _hair_salon(m):
    W, D, H = 32.0, 26.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "black"), (None, "wall_lilac")], inn="white", wains="plastic_purple",
                   trim="black", cornice="black", flo=("white", "black", 2.0, False), frame="black",
                   sign_txt="HAIR SALON", board="black", letters="neon_pink", px=0.5, awning=("plastic_purple", "white"),
                   back_door=11.0)
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Stations"):
        for i in range(4):
            with m.at((-10.5 + i * 5.2, iy - 0.4, FL)):
                salon_station(m)
    with m.group("Washing"):
        with m.at((-ix + 1.3, 2.0, FL), 90):
            for k in range(2):
                with m.at((-2.0 + k * 4.0, 0, 0)):
                    blk(m, (3.0, 2.0, 3.2), (0, 0.3, 1.6), "charcoal", bev=0.1)
                    blk(m, (2.4, 1.2, 0.6), (0, 0.4, 3.4), "white", bev=0.15)
                    with m.at((0, -2.0, 0)):
                        salon_chair(m, "plastic_black")
    with m.group("Reception"):
        with m.at((9.0, -7.0, FL)):
            counter(m, 6.0, top="white", body="plastic_purple")
        register(m, 9.0, -6.8, FL + 3.5)
        for y in (-9.0, -4.0):
            with m.at((-ix + 1.2, y - 2.0, FL), 90):
                bench_seat(m, 4.0, "plastic_purple")
        potted_plant(m, 13.5, -10.5)


reg("HairSalon", _hair_salon, sub="Services")


def _laundromat(m):
    W, D, H = 34.0, 28.0, 12.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "stone_dark"), (None, "wall_sky")], inn="white", wains="plastic_blue",
                   trim="white", cornice="plastic_blue", flo=("tile_white", "wall_sky", 2.0, False), frame="stainless",
                   sign_txt="LAUNDRY", board="plastic_blue", letters="white", px=0.6, awning=("plastic_blue", "white"),
                   back_door=12.0)
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Washers"):
        for i in range(6):
            with m.at((-12.5 + i * 2.8, iy - 1.4, FL)):
                washer(m)
        for i in range(5):
            with m.at((-ix + 1.4, -6.0 + i * 2.8, FL), 90):
                washer(m, True)
        for i in range(4):
            for s, ang in ((-1, 180), (1, 0)):
                with m.at((2.0 + i * 2.8, 2.5 + s * 1.35, FL), ang):
                    washer(m)
    with m.group("Tables"):
        with m.at((6.0, -6.0, FL)):
            blk(m, (8.0, 3.0, 0.3), (0, 0, 3.2), "white", bev=0.06)
            for sx in (-3.6, 3.6):
                blk(m, (0.4, 2.6, 3.0), (sx, 0, 1.5), "stainless")
            for k in range(3):
                blk(m, (1.6, 1.2, 0.5 - k * 0.1), (-2.4 + k * 2.4, 0, 3.6), ["fabric_blue", "fabric_white", "fabric_red"][k])
        with m.at((ix - 1.2, -8.0, FL), -90):
            bench_seat(m, 6.0, "plastic_blue")
        with m.at((ix - 1.2, 0.0, FL), -90):
            blk(m, (2.4, 2.0, 6.0), (0, 0, 3.0), "plastic_red", bev=0.1)
            blk(m, (1.6, 0.1, 1.2), (0, -1.02, 4.0), "screen_glow")
            text(m, "$", 0, -1.05, 2.4, px=0.18, depth=0.06, col="white")


reg("Laundromat", _laundromat, sub="Services")


def _movie_theater(m):
    W, D, H = 44.0, 48.0, 16.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "black"), (None, "wall_red")], inn=[(FL + 3.0, "velvet"),
                   (FL + H, "wall_navy"), (None, "concrete")], trim="gold", cornice="gold",
                   flo=("rug_red", "rug_red", 2.0, False), frame="gold", door_w=8.0, sign_txt="CINEMA",
                   board="black", letters="neon_yellow", px=0.8, sign_trim="gold", back_door=18.0, lights=(4, 5),
                   light_col="neon_yellow", win=(FL + 2.0, FL + 10.0), side_win=False)
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    # lobby with a snack bar, then a wall with two doorways into the auditorium
    wall(m, "x", -8.0, -ix, ix, FL, zt, -1, [(FL + 3.0, "velvet"), (None, "wall_red")], "wall_navy", "gold",
         holes=[(-16.0, -11.0, FL, FL + 8.0), (11.0, 16.0, FL, FL + 8.0)], t=0.8, zcuts=(FL + 3.0,))
    with m.group("SnackBar"):
        with m.at((-6.0, -13.5, FL)):
            counter(m, 14.0, top="white", body="wall_red", front_col="gold")
        for x in (-11.0, -1.0):
            register(m, x, -13.3, FL + 3.5)
        with m.at((-6.0, -13.5, FL + 3.5)):
            blk(m, (3.0, 2.0, 2.6), (-1.5, 0, 1.3), "glass")
            blk(m, (2.8, 1.8, 1.4), (-1.5, 0, 0.8), "corn")
        with m.at((-6.0, -9.2, FL + 8.8)):
            menu_board(m, 14.0, 3.0, items=("soda", "icecream", "hotdog", "fries"), title="SNACKS")
        with m.at((8.5, -13.5, FL)):
            counter(m, 4.0, top="stainless", body="stainless")
            soda_fountain(m)
    with m.group("Screen"):
        blk(m, (W - 6.0, 0.6, 11.0), (0, iy - 0.5, FL + 8.0), "white")
        blk(m, (W - 5.0, 0.4, 11.6), (0, iy - 0.3, FL + 8.0), "black")
        for s in (-1, 1):
            m.box((3.0, 0.6, 12.0), color="velvet", loc=(s * (W / 2 - 3.5), iy - 1.0, FL + 7.5),
                  cuts={"x": [s * (W / 2 - 3.5) + k * 0.6 - 1.5 for k in range(1, 5)]})
        blk(m, (W - 2.0, 3.0, 1.0), (0, iy - 1.5, FL + 0.5), "wall_navy")
    with m.group("Seats"):
        with m.at((0.0, 12.0, FL), 180):      # front row nearest the screen, rows rise towards the back
            seat_rows(m, 6, 12, "velvet", step_h=0.9, pitch=3.3)
    with m.group("Posters"):
        for x, c, ang in ((-ix + 0.2, "neon_blue", -90), (ix - 0.2, "neon_pink", 90)):
            with m.at((x, -15.0, FL + 5.0), ang):
                blk(m, (3.6, 0.2, 5.2), (0, 0, 0), "gold")
                blk(m, (3.2, 0.1, 4.8), (0, 0.12, 0), c)
                blk(m, (1.6, 0.1, 1.6), (0, 0.18, 0.6), "white", rot=(0, 45, 0))


reg("MovieTheater", _movie_theater, sub="Leisure")
