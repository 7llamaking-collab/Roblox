"""Nature: trees, bushes, rocks, ores, crystals, flowers & plants, clouds."""
import math
import random

from studlib.geo import by_height, by_normal, chain, circle_pts, jitter, star_pts, taper
from studlib.registry import add, asset

CAT = "Nature"


def trunk(m, h, r0=0.7, r1=0.4, col="bark", lean=0.0, seg=8):
    pts = [(0, 0, 0), (lean * 0.3, 0, h * 0.35), (lean * 0.7, 0, h * 0.7), (lean, 0, h)]
    m.tube(pts, [r0 * 1.15, r0 * 0.95, (r0 + r1) / 2, r1], seg=seg, color=col, angle=50)
    # root flares
    for i in range(4):
        a = math.radians(45 + 90 * i)
        m.cone(r=r0 * 0.45, h=r0 * 1.2, seg=5, color=col, rot=(0, 55, 45 + 90 * i),
               loc=(math.cos(a) * r0 * 0.7, math.sin(a) * r0 * 0.7, 0.05), smooth=False)


def blob(m, center, r, cols, seed=1, sub=1, squash=0.85):
    col = cols if isinstance(cols, str) else (lambda c, n, cs=cols: cs[0] if n.z > 0.35 else cs[1])
    m.ico(r=r, sub=sub, color=col, loc=center, scale=(1, 1, squash), deform=jitter(r * 0.08, seed), angle=28)


def canopy(m, top, size, cols, seed=1, n=6):
    rnd = random.Random(seed)
    blob(m, (0, 0, top), size, cols, seed)
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
        d = size * rnd.uniform(0.7, 0.9)
        z = top + rnd.uniform(-0.45, 0.25) * size
        blob(m, (math.cos(a) * d, math.sin(a) * d, z), size * rnd.uniform(0.55, 0.72), cols, seed + i + 1)


def oak(m, leaves=("leaf_light", "leaf"), fruit=None, seed=3, h=8.0, size=4.2):
    trunk(m, h, 0.8, 0.45)
    for s in (-1, 1):
        m.tube([(0, 0, h * 0.6), (s * 1.6, 0.3 * s, h * 0.85), (s * 2.6, 0.4 * s, h * 1.05)], [0.35, 0.25, 0.2],
               seg=6, color="bark")
    canopy(m, h + size * 0.55, size, list(leaves), seed)
    if fruit:
        rnd = random.Random(seed * 7)
        for i in range(12):
            a = rnd.uniform(0, 2 * math.pi)
            z = h + size * rnd.uniform(0.0, 0.9)
            r = size * 1.3 * math.sqrt(max(0.05, 1 - ((z - h - size * 0.55) / (size * 1.1)) ** 2))
            m.sphere(r=0.42, seg=8, rings=6, color=fruit, loc=(math.cos(a) * r, math.sin(a) * r, z))


@asset("OakTree", CAT, sub="Trees")
def oak_tree(m):
    oak(m)


@asset("AppleTree", CAT, sub="Trees", tags=["simulator"])
def apple_tree(m):
    oak(m, fruit="apple_red", seed=5)


@asset("OrangeTree", CAT, sub="Trees", tags=["simulator"])
def orange_tree(m):
    oak(m, leaves=("leaf", "leaf_dark"), fruit="orange", seed=8)


@asset("GoldenTree", CAT, sub="Trees", tags=["simulator", "rare"])
def golden_tree(m):
    oak(m, leaves=("gold_light", "gold"), fruit="gold_dark", seed=13)


@asset("AutumnTree", CAT, sub="Trees")
def autumn_tree(m):
    oak(m, leaves=("autumn_yellow", "autumn_orange"), seed=21)


@asset("RedAutumnTree", CAT, sub="Trees")
def red_autumn_tree(m):
    oak(m, leaves=("autumn_orange", "autumn_red"), seed=22)


@asset("CherryBlossomTree", CAT, sub="Trees")
def cherry_blossom(m):
    trunk(m, 7.0, 0.7, 0.4, col="bark_dark", lean=0.8)
    for s in (-1, 1):
        m.tube([(0.5, 0, 5.0), (s * 2.2 + 0.5, 0.4 * s, 6.8), (s * 3.4 + 0.5, 0.4 * s, 7.4)], [0.3, 0.22, 0.15],
               seg=6, color="bark_dark")
    canopy(m, 9.0, 3.6, ["blossom_light", "blossom"], seed=31, n=7)


@asset("BirchTree", CAT, sub="Trees")
def birch(m):
    spots = lambda c, n: "black" if (int(c.z * 2.3) % 3 == 0 and n.x + n.y > 0.3) else "white"
    m.tube([(0, 0, 0), (0, 0, 5), (0.2, 0, 10)], [0.55, 0.45, 0.35], seg=8, color=spots, cuts={"z": 0.45})
    canopy(m, 10.5, 3.0, ["autumn_yellow", "leaf_light"], seed=41, n=5)


@asset("PineTree", CAT, sub="Trees")
def pine_tree(m, snow=False):
    m.cyl(r=0.6, r2=0.45, h=3.0, seg=7, color="bark", loc=(0, 0, 1.5))
    for i, (r, z, h) in enumerate(((4.2, 2.4, 5.0), (3.4, 5.0, 4.6), (2.6, 7.5, 4.2), (1.7, 9.9, 3.6))):
        green = "pine" if i % 2 else "pine_dark"
        kw = {}
        if snow:
            cap = z + h * 0.62
            col = (lambda c, n, cap=cap, z=z, g=green: "snow" if c.z > cap or (z + 0.45 < c.z < z + 0.95 and n.z > -0.2)
                   else g)
            kw["cuts"] = {"z": [cap]}
        else:
            col = green
        m.lathe([(0, 0), (r, 0.5), (r * 0.9, 0.9), (0, h)], seg=8, color=col, loc=(0, 0, z),
                deform=jitter(0.12, i + 2), rot=(0, 0, 22 * i), smooth=False, **kw)


@asset("SnowyPineTree", CAT, sub="Trees")
def snowy_pine(m):
    pine_tree(m, snow=True)


@asset("PalmTree", CAT, sub="Trees")
def palm_tree(m):
    pts = [(0, 0, 0), (0.5, 0, 3), (1.4, 0, 6), (2.6, 0, 8.6), (3.2, 0, 9.6)]
    m.tube(pts, [0.6, 0.5, 0.45, 0.4, 0.38], seg=7, color=lambda c, n: "bark" if int(c.z / 0.7) % 2 else "wood_mid",
           cuts={"z": 0.7}, angle=50)
    top = (3.2, 0, 9.6)
    for i in range(7):
        a = 360 * i / 7
        droop = lambda co: co.__class__((co.x, co.y, co.z - 0.35 * co.y ** 2 / 1.0))
        m.leaf(length=4.2, width=1.3, thick=0.1, color="leaf" if i % 2 else "leaf_dark", loc=top,
               rot=(10, 0, a), deform=droop)
    for i in range(3):
        a = math.radians(120 * i)
        m.sphere(r=0.42, seg=8, rings=6, color="coconut", loc=(top[0] + math.cos(a) * 0.5, math.sin(a) * 0.5, 9.2))


@asset("DeadTree", CAT, sub="Trees")
def dead_tree(m):
    trunk(m, 6.0, 0.6, 0.3, col="bark_dark")
    for s, h, L in ((1, 3.5, 2.4), (-1, 4.5, 2.0), (1, 5.4, 1.5), (-1, 2.6, 1.6)):
        m.tube([(0, 0, h), (s * L * 0.6, 0.2 * s, h + L * 0.4), (s * L, 0.3 * s, h + L * 0.9)], [0.22, 0.14, 0.02],
               seg=5, color="bark_dark")


@asset("SpookyTree", CAT, sub="Trees")
def spooky_tree(m):
    dead_tree(m)
    for x, z in ((1.4, 5.5), (-1.2, 6.3)):
        m.sphere(r=0.3, seg=8, rings=6, color="pumpkin", loc=(x, 0.1, z - 0.4))


@asset("MushroomTree", CAT, sub="Trees", tags=["fantasy"])
def mushroom_tree(m):
    m.tube([(0, 0, 0), (0.4, 0, 3), (0.2, 0, 6)], [0.9, 0.7, 0.6], seg=10, color="offwhite")
    m.lathe([(0, 5.6), (3.4, 5.8), (3.6, 6.3), (3.0, 7.4), (1.6, 8.3), (0, 8.5)], seg=14, color="plastic_purple",
            loc=(0.2, 0, 0))
    rnd = random.Random(4)
    for i in range(8):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(1.0, 2.8)
        z = 8.5 - (r / 3.4) ** 2 * 2.3
        m.sphere(r=0.35, seg=8, rings=5, color="white", loc=(0.2 + math.cos(a) * r, math.sin(a) * r, z),
                 scale=(1, 1, 0.5))


# --- bushes & ground cover ---------------------------------------------------------------
@asset("Bush", CAT, sub="Bushes")
def bush(m, cols=("leaf_light", "leaf"), extra=None, seed=2):
    rnd = random.Random(seed)
    for i in range(5):
        a = 2 * math.pi * i / 5
        d = 0.9 if i else 0
        r = rnd.uniform(1.0, 1.3)
        blob(m, (math.cos(a) * d, math.sin(a) * d, r * 0.8), r, list(cols), seed + i)
    if extra:
        for i in range(10):
            a = rnd.uniform(0, 2 * math.pi)
            z = rnd.uniform(0.8, 2.0)
            r = 1.6 * math.sqrt(max(0.1, 1 - ((z - 1) / 1.4) ** 2))
            m.sphere(r=0.2, seg=6, rings=4, color=extra, loc=(math.cos(a) * r, math.sin(a) * r, z))


@asset("BerryBush", CAT, sub="Bushes", tags=["simulator"])
def berry_bush(m):
    bush(m, ("leaf", "leaf_dark"), extra="blueberry", seed=5)


@asset("FlowerBush", CAT, sub="Bushes")
def flower_bush(m):
    bush(m, ("leaf", "leaf_dark"), extra="blossom", seed=9)


@asset("Hedge", CAT, sub="Bushes")
def hedge(m):
    m.box((6.0, 1.8, 2.6), color=by_normal("leaf_light", "leaf"), bevel=0.35, bseg=2, loc=(0, 0, 1.3),
          deform=jitter(0.08, 3), cuts={"x": 1.0, "z": 0.9}, angle=30)


@asset("GrassTuft", CAT, sub="Plants")
def grass_tuft(m):
    for i in range(7):
        a = i * 51
        m.cone(r=0.12, h=0.8 + (i % 3) * 0.25, seg=4, color="grass" if i % 2 else "leaf",
               rot=(12 + (i % 3) * 6, 0, a), loc=(math.cos(math.radians(a)) * 0.2, math.sin(math.radians(a)) * 0.2, 0),
               smooth=False)


@asset("Fern", CAT, sub="Plants")
def fern(m):
    for i in range(7):
        m.leaf(length=1.6, width=0.55, thick=0.05, color="leaf" if i % 2 else "leaf_dark", loc=(0, 0, 0.1),
               rot=(38 + (i % 2) * 12, 0, i * 51), deform=lambda co: co.__class__((co.x, co.y, co.z - 0.2 * co.y ** 2)))


@asset("Reeds", CAT, sub="Plants")
def reeds(m):
    for i, (x, y, h) in enumerate(((0, 0, 2.2), (0.3, 0.1, 1.8), (-0.25, 0.2, 2.0), (0.1, -0.3, 1.6))):
        m.cyl(r=0.04, h=h, seg=5, color="leaf_dark", loc=(x, y, h / 2))
        m.cyl(r=0.1, h=0.45, seg=6, color="wood_dark", loc=(x, y, h - 0.2), bevel=0.04)
    for i in range(5):
        m.leaf(length=1.3, width=0.2, thick=0.03, color="leaf", loc=(0, 0, 0), rot=(70, 0, i * 72))


@asset("Tulip", CAT, sub="Flowers")
def tulip(m, col="plastic_red"):
    m.cyl(r=0.05, h=1.4, seg=5, color="leaf_dark", loc=(0, 0, 0.7))
    for i in range(3):
        a = 120 * i
        m.sphere(r=0.24, seg=8, rings=6, color=col, loc=(math.cos(math.radians(a)) * 0.08,
                                                      math.sin(math.radians(a)) * 0.08, 1.55), scale=(0.6, 0.8, 1.25),
                 rot=(0, 0, a))
    m.leaf(length=0.8, width=0.3, thick=0.04, color="leaf", loc=(0, 0, 0.1), rot=(70, 0, 30))
    m.leaf(length=0.7, width=0.28, thick=0.04, color="leaf", loc=(0, 0, 0.15), rot=(66, 0, 200))


@asset("Daisy", CAT, sub="Flowers")
def daisy(m):
    m.cyl(r=0.04, h=1.3, seg=5, color="leaf_dark", loc=(0, 0, 0.65))
    for i in range(10):
        m.leaf(length=0.38, width=0.14, thick=0.03, color="white", loc=(0, 0, 1.33), rot=(0, 0, 36 * i))
    m.cyl(r=0.12, h=0.1, seg=8, color="egg_yolk", loc=(0, 0, 1.35), bevel=0.04)
    m.leaf(length=0.6, width=0.25, thick=0.04, color="leaf", loc=(0, 0, 0.3), rot=(60, 0, 40))


@asset("Sunflower", CAT, sub="Flowers")
def sunflower(m):
    m.tube([(0, 0, 0), (0, 0.1, 2.0), (0, 0, 3.0)], [0.1, 0.09, 0.08], seg=6, color="leaf_dark")
    for i in range(14):
        m.leaf(length=0.7, width=0.3, thick=0.04, color="plastic_yellow",
               rot=(90, 0, 0), pre=None, loc=(0, -0.05, 3.1),
               deform=lambda co, a=i * 360 / 14: co.__class__((co.x * math.cos(math.radians(a)) - co.y * math.sin(math.radians(a)),
                                                               co.x * math.sin(math.radians(a)) + co.y * math.cos(math.radians(a)),
                                                               co.z)))
    m.cyl(r=0.38, h=0.14, seg=12, color="chocolate", rot=(90, 0, 0), loc=(0, -0.1, 3.1), bevel=0.05)
    for s in (-1, 1):
        m.leaf(length=0.9, width=0.45, thick=0.04, color="leaf", loc=(0, 0, 1.2 + s * 0.2), rot=(40, 0, 90 * s))


@asset("Rose", CAT, sub="Flowers")
def rose(m):
    m.cyl(r=0.04, h=1.4, seg=5, color="leaf_dark", loc=(0, 0, 0.7))
    m.sphere(r=0.24, seg=8, rings=6, color="apple_red_dark", loc=(0, 0, 1.52), scale=(1, 1, 0.9))
    for i in range(5):
        a = 72 * i
        m.sphere(r=0.2, seg=8, rings=5, color="apple_red", loc=(math.cos(math.radians(a)) * 0.16,
                                                               math.sin(math.radians(a)) * 0.16, 1.45),
                 scale=(0.5, 1, 1), rot=(0, 20, a))
    m.leaf(length=0.5, width=0.25, thick=0.04, color="leaf", loc=(0, 0, 0.6), rot=(55, 0, 60))


@asset("FlowerPatch", CAT, sub="Flowers")
def flower_patch(m):
    m.cyl(r=1.6, h=0.2, seg=12, color="grass", loc=(0, 0, 0.1), deform=jitter(0.08, 3, (1, 1, 0.3)))
    cols = ["plastic_red", "plastic_yellow", "white", "plastic_purple", "plastic_pink"]
    rnd = random.Random(7)
    for i in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.2, 1.3)
        x, y = math.cos(a) * r, math.sin(a) * r
        h = rnd.uniform(0.4, 0.8)
        m.cyl(r=0.03, h=h, seg=4, color="leaf_dark", loc=(x, y, 0.2 + h / 2))
        m.prism(star_pts(0.18, 0.08, 5), depth=0.05, color=cols[i % 5], loc=(x, y, 0.22 + h))
        m.sphere(r=0.06, seg=6, rings=4, color="egg_yolk", loc=(x, y, 0.26 + h))


@asset("LilyPad", CAT, sub="Plants")
def lily_pad(m):
    pts = circle_pts(1.0, 14, start=20)[:13] + [(0, 0)]
    m.prism(pts, depth=0.08, color="lily", loc=(0, 0, 0.04))
    for i in range(8):
        m.leaf(length=0.4, width=0.2, thick=0.03, color="blossom", loc=(0.2, 0, 0.1), rot=(40, 0, 45 * i))
    m.sphere(r=0.1, seg=6, rings=4, color="egg_yolk", loc=(0.2, 0, 0.18))


@asset("Cactus", CAT, sub="Plants")
def cactus(m):
    m.lathe([(0.6, 0), (0.6, 4.0), (0.45, 4.6), (0, 4.8)], seg=8, color="cactus", angle=50)
    for s, z, h in ((1, 1.6, 1.4), (-1, 2.3, 1.1)):
        m.tube([(0, 0, z), (s * 1.2, 0, z), (s * 1.3, 0, z + 0.3), (s * 1.3, 0, z + h)], [0.35, 0.35, 0.35, 0.3],
               seg=8, color="cactus")
        m.sphere(r=0.3, seg=8, rings=5, color="cactus", loc=(s * 1.3, 0, z + h))
    m.sphere(r=0.2, seg=8, rings=5, color="blossom", loc=(0, 0, 4.8))


@asset("BigMushroom", CAT, sub="Plants")
def big_mushroom(m):
    m.lathe([(0.5, 0), (0.4, 1.4), (0.36, 2.0), (0, 2.0)], seg=10, color="offwhite")
    m.lathe([(0, 1.8), (1.6, 1.9), (1.7, 2.2), (1.4, 2.8), (0.7, 3.2), (0, 3.3)], seg=14,
            color=by_normal("apple_red", "apple_red", "offwhite", thresh=0.3))
    for a, r, z in ((20, 1.0, 3.0), (140, 1.2, 2.9), (260, 1.1, 2.95), (0, 0, 3.32), (80, 1.5, 2.5), (200, 1.55, 2.45)):
        m.sphere(r=0.22, seg=8, rings=5, color="white", loc=(math.cos(math.radians(a)) * r,
                                                            math.sin(math.radians(a)) * r, z), scale=(1, 1, 0.45))


@asset("Log", CAT, sub="Plants")
def log(m):
    m.cyl(r=0.7, h=4.0, seg=10, color=lambda c, n: "wood_pale" if abs(n.x) > 0.9 else "bark", rot=(0, 90, 0),
          loc=(0, 0, 0.7), bevel=0.06)
    m.cyl(r=0.45, h=4.02, seg=10, color="wood_light", rot=(0, 90, 0), loc=(0, 0, 0.7), smooth=False)
    m.tube([(0.5, 0, 1.2), (0.7, 0.2, 1.8)], [0.18, 0.1], seg=6, color="bark")


@asset("Stump", CAT, sub="Plants")
def stump(m):
    m.lathe([(0, 0), (1.1, 0), (0.9, 0.3), (0.85, 1.4), (0, 1.4)], seg=10,
            color=lambda c, n: "wood_pale" if n.z > 0.9 else "bark")
    m.cyl(r=0.55, h=0.02, seg=10, color="wood_light", loc=(0, 0, 1.41))
    m.sphere(r=0.25, seg=8, rings=5, color="apple_red", loc=(0.8, -0.5, 0.5), scale=(1, 1, 0.5))
    m.cyl(r=0.08, h=0.4, seg=6, color="offwhite", loc=(0.8, -0.5, 0.3))


@asset("Seaweed", CAT, sub="Underwater")
def seaweed(m):
    for i, (x, h) in enumerate(((0, 3.0), (0.4, 2.2), (-0.35, 2.5))):
        pts = [(x + 0.2 * math.sin(k * 1.3 + i), 0, h * k / 6) for k in range(7)]
        m.tube(pts, [(0.18, 0.05)] * 6 + [0], seg=4, color="leaf_dark" if i % 2 else "moss", up=(0, 1, 0))


@asset("Coral", CAT, sub="Underwater")
def coral(m):
    def branch(p, d, L, r, depth):
        e = (p[0] + d[0] * L, p[1] + d[1] * L, p[2] + d[2] * L)
        m.tube([p, e], [r, r * 0.8], seg=6, color="octopus")
        m.sphere(r=r * 0.8, seg=6, rings=4, color="octopus", loc=e)
        if depth:
            for s in (-1, 1):
                nd = (d[0] + s * 0.5, d[1] + s * 0.2, d[2])
                n = math.sqrt(sum(v * v for v in nd))
                branch(e, tuple(v / n for v in nd), L * 0.7, r * 0.75, depth - 1)
    branch((0, 0, 0), (0, 0, 1), 1.2, 0.25, 2)


@asset("Seashell", CAT, sub="Underwater")
def seashell(m):
    fan = lambda co: co.__class__((co.x, max(co.y, -0.15), co.z))
    stripes = lambda c, n: "peach" if int((math.degrees(math.atan2(c.y + 0.15, c.x)) + 360) / 12.9) % 2 else "offwhite"
    m.lathe([(0, 0.42), (0.35, 0.38), (0.7, 0.2), (0.85, 0.0), (0, 0.0)], seg=28, color=stripes, deform=fan,
            smooth=False)
    m.box((0.5, 0.25, 0.2), color="peach", bevel=0.05, loc=(0, -0.2, 0.1))


@asset("Cloud", CAT, sub="Sky", origin="center")
def cloud(m):
    for x, y, z, r in ((0, 0, 0, 2.2), (2.2, 0.2, -0.4, 1.7), (-2.2, -0.1, -0.5, 1.6), (1.0, 0.6, 1.0, 1.5),
                       (-1.0, 0.3, 0.8, 1.4), (3.6, 0, -0.9, 1.0), (-3.5, 0, -0.9, 1.0)):
        m.sphere(r=r, seg=12, rings=8, color="white", loc=(x, y, z), scale=(1, 0.8, 0.85))


@asset("RainCloud", CAT, sub="Sky", origin="center")
def rain_cloud(m):
    for x, y, z, r in ((0, 0, 0, 2.2), (2.2, 0.2, -0.4, 1.7), (-2.2, -0.1, -0.5, 1.6), (1.0, 0.6, 1.0, 1.5)):
        m.sphere(r=r, seg=12, rings=8, color="gray", loc=(x, y, z), scale=(1, 0.8, 0.85))
    for x in (-1.8, -0.6, 0.6, 1.8):
        m.lathe([(0, 0), (0.18, 0.2), (0, 0.6)], seg=6, color="water", loc=(x, 0, -3.0 + (x % 1.0)))


# --- rocks, ores & crystals --------------------------------------------------------------------
def rock(m, r=1.0, seed=1, col="stone", loc=(0, 0, 0), squash=0.7):
    cols = {"stone": ("stone_light", "stone"), "sandstone": ("sand", "sandstone"), "dark": ("stone", "stone_dark"),
            "snow": ("snow", "stone")}[col]
    m.ico(r=r, sub=1, color=lambda c, n: cols[0] if n.z > 0.6 else cols[1], loc=(loc[0], loc[1], loc[2] + r * squash * 0.8),
          scale=(1.15, 1.0, squash), deform=jitter(r * 0.16, seed), smooth=False)


@asset("SmallRock", CAT, sub="Rocks")
def small_rock(m):
    rock(m, 0.8, seed=2)


@asset("Rock", CAT, sub="Rocks")
def rock_mid(m):
    rock(m, 1.6, seed=4)


@asset("Boulder", CAT, sub="Rocks")
def boulder(m):
    rock(m, 3.2, seed=6, squash=0.8)


@asset("RockCluster", CAT, sub="Rocks")
def rock_cluster(m):
    rock(m, 1.8, seed=8)
    rock(m, 1.1, seed=9, loc=(2.0, 0.6, 0))
    rock(m, 0.8, seed=10, loc=(-1.7, -0.8, 0))


@asset("DesertRock", CAT, sub="Rocks")
def desert_rock(m):
    rock(m, 1.8, seed=12, col="sandstone", squash=0.9)


@asset("SnowyRock", CAT, sub="Rocks")
def snowy_rock(m):
    rock(m, 1.8, seed=14, col="snow")


ORES = [("Coal", "coal", "charcoal"), ("Copper", "copper", "bronze"), ("Iron", "iron", "iron_dark"),
        ("Gold", "gold", "gold_dark"), ("Diamond", "diamond", "diamond_dark"), ("Emerald", "emerald", "emerald_dark"),
        ("Ruby", "ruby", "ruby_dark"), ("Amethyst", "amethyst", "amethyst_dark"), ("Rainbow", None, None)]


def ore_rock(m, gem, gem_dark, seed):
    rock(m, 1.7, seed=seed, col="dark", squash=0.8)
    rnd = random.Random(seed)
    rb = ["rb_red", "rb_orange", "rb_yellow", "rb_green", "rb_cyan", "rb_blue", "rb_purple"]
    for i in range(7):
        a = 2 * math.pi * i / 7 + rnd.uniform(-0.2, 0.2)
        z = rnd.uniform(0.6, 2.2)
        r = 1.75 * math.sqrt(max(0.15, 1 - ((z - 1.1) / 1.6) ** 2))
        c = rb[i % 7] if gem is None else (gem if i % 3 else gem_dark)
        if gem in ("coal", "iron", "copper", "gold"):
            m.ico(r=0.32, sub=0, color=c, loc=(math.cos(a) * r, math.sin(a) * r, z), smooth=False)
        else:
            m.crystal(r=0.22, h=0.8, color=c, loc=(math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, z - 0.2),
                      rot=(rnd.uniform(30, 60), 0, math.degrees(a) - 90))


for _i, (_n, _g, _gd) in enumerate(ORES):
    add(f"{_n}Ore", CAT, (lambda m, g=_g, gd=_gd, s=_i: ore_rock(m, g, gd, 20 + s)), sub="Ores",
        tags=["mining", "simulator"])


CRYSTALS = [("Amethyst", "amethyst", "amethyst_dark"), ("Diamond", "diamond", "diamond_dark"),
            ("Emerald", "emerald", "emerald_dark"), ("Ruby", "ruby", "ruby_dark"),
            ("Sapphire", "sapphire", "blueberry"), ("Topaz", "topaz", "gold_dark"), ("Pink", "crystal_pink", "frosting_pink")]


def crystal_cluster(m, c1, c2, seed):
    rnd = random.Random(seed)
    m.ico(r=1.0, sub=1, color="stone_dark", loc=(0, 0, 0.2), scale=(1.4, 1.2, 0.4), deform=jitter(0.1, seed),
          smooth=False)
    m.crystal(r=0.5, h=3.0, color=c1, loc=(0, 0, 0.1), rot=(0, 0, 10))
    for i in range(6):
        a = 60 * i + rnd.uniform(-15, 15)
        h = rnd.uniform(1.2, 2.2)
        m.crystal(r=rnd.uniform(0.25, 0.38), h=h, color=c1 if i % 2 else c2, loc=(0, 0, 0.1),
                  rot=(rnd.uniform(25, 45), 0, a), pre=None)


for _i, (_n, _c1, _c2) in enumerate(CRYSTALS):
    add(f"{_n}Crystals", CAT, (lambda m, a=_c1, b=_c2, s=_i: crystal_cluster(m, a, b, 50 + s)), sub="Crystals",
        tags=["mining", "simulator"])
