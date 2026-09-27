"""Fruits, vegetables and snacks."""
import math

from studlib.geo import by_height, by_normal, circle_pts, jitter, star_pts, taper
from studlib.registry import asset

CAT = "Food"


def stem_leaf(m, top, stem_len=0.28, leaf=True, lean=12, leaf_col="leaf", leaf_len=0.55, stem_col="wood_dark"):
    x, y, z = top
    tip = (x + math.sin(math.radians(lean)) * stem_len, y, z + math.cos(math.radians(lean)) * stem_len)
    m.tube([(x, y, z - 0.05), tip], [0.055, 0.04], seg=6, color=stem_col)
    if leaf:
        m.leaf(length=leaf_len, width=leaf_len * 0.5, thick=0.05, color=leaf_col,
               loc=(tip[0] - 0.02, y, tip[2] - 0.08), rot=(62, 0, -110))


@asset("Apple", CAT, sub="Fruit")
def apple(m):
    prof = [(0, 0.1), (0.22, 0.03), (0.48, 0.1), (0.62, 0.32), (0.64, 0.58), (0.56, 0.84),
            (0.36, 1.0), (0.14, 0.97), (0, 0.86)]
    m.lathe(prof, seg=14, color="apple_red")
    stem_leaf(m, (0, 0, 0.9))


@asset("GreenApple", CAT, sub="Fruit")
def green_apple(m):
    prof = [(0, 0.1), (0.22, 0.03), (0.48, 0.1), (0.62, 0.32), (0.64, 0.58), (0.56, 0.84),
            (0.36, 1.0), (0.14, 0.97), (0, 0.86)]
    m.lathe(prof, seg=14, color="apple_green")
    stem_leaf(m, (0, 0, 0.9), leaf_col="leaf_dark")


@asset("GoldenApple", CAT, sub="Fruit", tags=["rare"])
def golden_apple(m):
    prof = [(0, 0.1), (0.22, 0.03), (0.48, 0.1), (0.62, 0.32), (0.64, 0.58), (0.56, 0.84),
            (0.36, 1.0), (0.14, 0.97), (0, 0.86)]
    m.lathe(prof, seg=14, color="gold")
    stem_leaf(m, (0, 0, 0.9), leaf_col="gold_light", stem_col="gold_dark")


@asset("Banana", CAT, sub="Fruit")
def banana(m):
    pts, rad = [], []
    n = 9
    for i in range(n + 1):
        t = i / n
        a = math.radians(-70 + 140 * t)
        pts.append((math.sin(a) * 1.1, 0, 0.62 - math.cos(a) * 0.62 * 0.9 + 0.1))
        r = 0.2 * math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.55
        rad.append(max(r, 0.05))
    m.tube(pts, rad, seg=5, color="banana", angle=30)
    # stem end + dark tip
    a0 = math.radians(-70)
    m.tube([pts[-1], (pts[-1][0] + 0.18, 0, pts[-1][2] + 0.14)], [0.055, 0.05], seg=5, color="banana_dark")
    m.sphere(r=0.06, seg=5, rings=3, color="wood_dark", loc=pts[0])


@asset("Orange", CAT, sub="Fruit")
def orange(m):
    m.sphere(r=0.6, seg=14, rings=10, color="orange", loc=(0, 0, 0.58), scale=(1, 1, 0.96))
    m.cyl(r=0.07, h=0.08, seg=6, color="leaf_dark", loc=(0, 0, 1.15))
    m.leaf(length=0.5, width=0.26, thick=0.05, color="leaf", loc=(0.02, 0, 1.15), rot=(70, 0, -100))


@asset("Lemon", CAT, sub="Fruit")
def lemon(m):
    m.lathe([(0, -0.62), (0.08, -0.56), (0.32, -0.38), (0.42, -0.12), (0.42, 0.12),
             (0.32, 0.38), (0.08, 0.56), (0, 0.62)], seg=12, color="lemon",
            rot=(0, 90, 0), loc=(0, 0, 0.42))


@asset("Strawberry", CAT, sub="Fruit")
def strawberry(m):
    prof = [(0, 0), (0.12, 0.08), (0.32, 0.35), (0.45, 0.68), (0.46, 0.9), (0.36, 1.04), (0, 1.08)]
    m.lathe(prof, seg=12, color="strawberry")
    # seeds
    for i in range(18):
        a = i * 137.5
        h = 0.22 + (i % 6) * 0.13
        r = [0.21, 0.31, 0.38, 0.43, 0.46, 0.45][i % 6] + 0.01
        x, y = math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r
        m.sphere(r=0.035, seg=4, rings=2, color="strawberry_seed", loc=(x, y, h), smooth=False)
    m.prism(star_pts(0.42, 0.14, 6), depth=0.05, color="leaf", loc=(0, 0, 1.06), bevel=0.015, bseg=1)
    m.tube([(0, 0, 1.05), (0.03, 0, 1.25)], [0.05, 0.035], seg=6, color="leaf_dark")


@asset("Cherries", CAT, sub="Fruit")
def cherries(m):
    for x, z in ((-0.32, 0.3), (0.3, 0.26)):
        m.sphere(r=0.3, seg=12, rings=8, color="cherry", loc=(x, 0, z), scale=(1, 1, 0.92))
        m.tube([(x, 0, z + 0.25), (x * 0.6, 0, z + 0.6), (0.02, 0, 1.25)], [0.035, 0.03, 0.03],
               seg=5, color="leaf_dark")
    m.leaf(length=0.55, width=0.28, thick=0.05, color="leaf", loc=(0.02, 0, 1.22), rot=(70, 0, -70))


@asset("Grapes", CAT, sub="Fruit")
def grapes(m):
    rows = [(4, 0.95, 0.42), (4, 0.72, 0.36), (3, 0.5, 0.28), (2, 0.3, 0.18), (1, 0.12, 0.0)]
    k = 0
    for n, z, r in rows:
        for i in range(n):
            a = 2 * math.pi * i / max(n, 1) + k * 0.5
            m.sphere(r=0.17, seg=8, rings=6, color="grape" if (i + k) % 3 else "grape_dark",
                     loc=(math.cos(a) * r, math.sin(a) * r, z + 0.05))
        k += 1
    m.tube([(0, 0, 1.05), (0.02, 0, 1.35), (0.12, 0, 1.45)], [0.05, 0.04, 0.035], seg=5, color="wood_dark")
    m.leaf(length=0.6, width=0.4, thick=0.05, color="leaf", loc=(0.05, 0, 1.3), rot=(60, 0, -60))


@asset("Watermelon", CAT, sub="Fruit")
def watermelon(m):
    stripes = lambda c, n: "melon_dark" if int((math.degrees(math.atan2(c.y, c.x)) + 360) / 30) % 2 else "melon_rind"
    m.sphere(r=1.0, seg=12, rings=9, color=stripes, loc=(0, 0, 0.8), scale=(1.25, 1.0, 0.82), angle=35)
    m.cyl(r=0.07, h=0.12, seg=5, color="wood_dark", loc=(0, 0, 1.62))


@asset("WatermelonSlice", CAT, sub="Fruit")
def watermelon_slice(m):
    # half disc wedge: outline in XZ, extruded along Y
    n = 10
    rim = [(math.cos(math.pi * (1 - i / n)) * 1.0, math.sin(math.pi * (1 - i / n)) * 1.0) for i in range(n + 1)]
    outline = list(reversed(rim))
    m.prism([(x, -y) for x, y in rim], depth=0.32, color="melon_rind", rot=(90, 0, 0),
            loc=(0, 0, 1.0), bevel=0.03, bseg=1, scale=(1, 1, 1))
    inner = [(x * 0.82, -y * 0.82) for x, y in rim]
    m.prism(inner, depth=0.36, color="watermelon", rot=(90, 0, 0), loc=(0, 0, 1.0 - 0.02))
    band = [(x * 0.88, -y * 0.88) for x, y in rim]
    m.prism(band, depth=0.34, color="melon_pale", rot=(90, 0, 0), loc=(0, 0, 1.0 - 0.01))
    seeds = [(math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r)
             for a, r in ((200, 0.55), (235, 0.62), (270, 0.5), (305, 0.62), (340, 0.55), (250, 0.32), (292, 0.32))]
    for i, (x, y) in enumerate((x, -y) for x, y in seeds):
        for s in (-1, 1):
            m.sphere(r=0.045, seg=4, rings=3, color="black", loc=(x, s * 0.18, 1.0 - y),
                     scale=(0.7, 0.5, 1.2), smooth=False)


@asset("Pineapple", CAT, sub="Fruit")
def pineapple(m):
    def diamond(c, n):
        a = math.degrees(math.atan2(c.y, c.x))
        k = int((a + 360) / 45) + int(c.z / 0.22)
        return "pineapple" if k % 2 else "pineapple_dark"
    prof = [(0, 0), (0.32, 0.02), (0.46, 0.2), (0.52, 0.55), (0.5, 0.9), (0.4, 1.15), (0.2, 1.25), (0, 1.26)]
    m.lathe(prof, seg=8, color=diamond, smooth=False)
    for ring, (n, h, tilt, L) in enumerate([(6, 1.2, 35, 0.75), (5, 1.26, 20, 0.95), (3, 1.3, 8, 0.8)]):
        for i in range(n):
            a = 360 * i / n + ring * 25
            m.leaf(length=L, width=0.22, thick=0.05, color="leaf" if ring % 2 else "leaf_dark",
                   loc=(0, 0, h), rot=(90 - tilt, 0, a - 90))


@asset("Peach", CAT, sub="Fruit")
def peach(m):
    def blush(c, n):
        return "peach_dark" if c.x + c.y * 0.3 > 0.15 else "peach"
    m.sphere(r=0.58, seg=14, rings=10, color=blush, loc=(0, 0, 0.56))
    stem_leaf(m, (0, 0, 1.08), stem_len=0.14)


@asset("Pear", CAT, sub="Fruit")
def pear(m):
    prof = [(0, 0.05), (0.3, 0.02), (0.52, 0.2), (0.56, 0.42), (0.44, 0.7), (0.3, 0.92), (0.24, 1.12),
            (0.14, 1.28), (0, 1.3)]
    m.lathe(prof, seg=14, color="pear")
    stem_leaf(m, (0, 0, 1.28), stem_len=0.22)


@asset("Coconut", CAT, sub="Fruit")
def coconut(m):
    m.ico(r=0.62, sub=2, color="coconut", loc=(0, 0, 0.58), deform=jitter(0.03, 3), angle=25)
    for a in (0, 120, 240):
        x, y = math.cos(math.radians(a)) * 0.14, math.sin(math.radians(a)) * 0.14
        m.sphere(r=0.07, seg=6, rings=4, color="wood_deep", loc=(x, y - 0.0, 1.17), scale=(1, 1, 0.5))


@asset("CoconutHalf", CAT, sub="Fruit")
def coconut_half(m):
    m.lathe([(0, 0.02), (0.35, 0.0), (0.58, 0.18), (0.62, 0.5), (0.52, 0.5), (0.48, 0.24),
             (0.3, 0.14), (0, 0.14)], seg=14, color=by_height("coconut", 0.47, "coconut_meat"))
    m.cyl(r=0.5, h=0.02, seg=14, color="milk", loc=(0, 0, 0.42))


@asset("Mango", CAT, sub="Fruit")
def mango(m):
    m.sphere(r=0.5, seg=14, rings=10, color=lambda c, n: "mango_red" if c.z > 0.75 and c.x > -0.1 else "mango",
             loc=(0, 0, 0.5), scale=(1.25, 0.85, 1.0), deform=taper(-0.5, 0.5, 0.85, 1.1, axes="y"))
    stem_leaf(m, (-0.35, 0, 0.92), stem_len=0.12, lean=-20)


@asset("Blueberries", CAT, sub="Fruit")
def blueberries(m):
    spots = [(0, 0, 0.2), (0.34, 0.05, 0.2), (-0.3, 0.12, 0.2), (0.1, 0.32, 0.2), (0.05, -0.3, 0.2),
             (0.15, 0.08, 0.5), (-0.14, -0.05, 0.47)]
    for x, y, z in spots:
        m.sphere(r=0.2, seg=10, rings=7, color="blueberry", loc=(x, y, z))
        m.prism(star_pts(0.07, 0.03, 5), depth=0.03, color="grape_dark", loc=(x, y, z + 0.19))


@asset("Lime", CAT, sub="Fruit")
def lime(m):
    m.sphere(r=0.42, seg=12, rings=8, color="lime", loc=(0, 0, 0.4), scale=(1, 1, 0.95))
    m.cyl(r=0.05, h=0.06, seg=5, color="leaf_dark", loc=(0, 0, 0.81))


@asset("Kiwi", CAT, sub="Fruit")
def kiwi(m):
    m.sphere(r=0.45, seg=12, rings=8, color="kiwi_brown", loc=(0, 0, 0.4), scale=(1.2, 1, 0.9))


@asset("KiwiHalf", CAT, sub="Fruit")
def kiwi_half(m):
    m.lathe([(0, 0.0), (0.3, 0.02), (0.44, 0.18), (0.46, 0.4), (0, 0.4)], seg=14,
            color=by_height("kiwi_brown", 0.39, "kiwi_green"))
    m.cyl(r=0.14, h=0.02, seg=10, color="melon_pale", loc=(0, 0, 0.405))
    for i in range(10):
        a = math.radians(36 * i)
        m.sphere(r=0.025, seg=4, rings=2, color="black", loc=(math.cos(a) * 0.2, math.sin(a) * 0.2, 0.405),
                 scale=(1.6, 1, 0.5), rot=(0, 0, 36 * i), smooth=False)


@asset("Avocado", CAT, sub="Fruit")
def avocado(m):
    m.lathe([(0, 0), (0.34, 0.05), (0.48, 0.3), (0.44, 0.62), (0.3, 0.92), (0.14, 1.1), (0, 1.14)],
            seg=12, color="avocado_dark")


@asset("AvocadoHalf", CAT, sub="Fruit")
def avocado_half(m):
    prof = [(0, 0), (0.34, 0.05), (0.48, 0.3), (0.44, 0.62), (0.3, 0.92), (0.14, 1.1), (0, 1.14)]
    flat = lambda co: co.__class__((co.x, min(co.y, 0.0), co.z))
    m.lathe(prof, seg=12, color=lambda c, n: "avocado" if n.z > 0.9 else "avocado_dark",
            rot=(90, 0, 0), loc=(0, 0.57, 0), deform=flat)
    m.lathe([(0, 0), (0.3, 0.07), (0.42, 0.3), (0.38, 0.6), (0.25, 0.88), (0, 1.02)], seg=12,
            color="melon_pale", rot=(90, 0, 0), loc=(0, 0.52, 0.012),
            deform=lambda co: co.__class__((co.x, min(co.y, 0.0), co.z)), scale=(1, 1, 1))
    m.sphere(r=0.22, seg=10, rings=7, color="seed_brown", loc=(0, 0.2, 0.0))


@asset("DragonFruit", CAT, sub="Fruit")
def dragonfruit(m):
    m.sphere(r=0.5, seg=12, rings=8, color="dragonfruit", loc=(0, 0, 0.55), scale=(0.95, 0.95, 1.15))
    for ring, (theta, n) in enumerate(((120, 5), (80, 6), (40, 5))):
        for i in range(n):
            a = 360 * i / n + ring * 30
            t = math.radians(theta)
            r, z = 0.5 * 0.95 * math.sin(t), 0.55 + 0.5 * 1.15 * math.cos(t)
            m.leaf(length=0.36, width=0.2, thick=0.04, color="leaf_light" if ring != 1 else "lime",
                   loc=(math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r, z),
                   rot=(180 - theta - 28, 0, a - 90))
    for i in range(4):
        m.leaf(length=0.3, width=0.16, thick=0.04, color="leaf_light", loc=(0, 0, 1.1), rot=(62, 0, 90 * i))


# --- vegetables --------------------------------------------------------------
@asset("Carrot", CAT, sub="Vegetable")
def carrot(m):
    m.lathe([(0, 0), (0.1, 0.25), (0.22, 0.8), (0.26, 1.15), (0.2, 1.24), (0, 1.26)], seg=8,
            color="carrot", angle=50)
    for a in (0, 120, 240):
        m.leaf(length=0.75, width=0.24, thick=0.05, color="leaf", loc=(0, 0, 1.2), rot=(78, 0, a))


@asset("Corn", CAT, sub="Vegetable")
def corn(m):
    prof = [(0, 0.1), (0.2, 0.12)]
    for i in range(12):
        z = 0.2 + i * 0.1
        r = 0.3 - max(0, (z - 1.0)) * 0.35
        prof.append((r if i % 2 == 0 else r - 0.035, z))
    prof += [(0.16, 1.48), (0, 1.54)]

    def kernels(c, n):
        a = int((math.degrees(math.atan2(c.y, c.x)) + 360) / 30)
        return "corn" if (a + int(c.z / 0.1)) % 2 else "egg_yolk"
    m.lathe(prof, seg=12, color=kernels, angle=35)
    for a in (0, 120, 240):
        d = math.radians(a + 90)
        m.leaf(length=1.2, width=0.5, thick=0.05, color="corn_husk" if a else "leaf",
               loc=(math.cos(d) * 0.22, math.sin(d) * 0.22, 0.0), rot=(74, 0, a))


@asset("Tomato", CAT, sub="Vegetable")
def tomato(m):
    m.sphere(r=0.55, seg=14, rings=10, color="tomato", loc=(0, 0, 0.48), scale=(1, 1, 0.85))
    m.prism(star_pts(0.32, 0.1, 5), depth=0.05, color="leaf", loc=(0, 0, 0.95), bevel=0.015, bseg=1)
    m.cyl(r=0.05, h=0.14, seg=5, color="leaf_dark", loc=(0, 0, 1.02))


@asset("Pumpkin", CAT, sub="Vegetable")
def pumpkin(m):
    for i in range(8):
        a = math.radians(45 * i)
        m.sphere(r=0.55, seg=10, rings=8, color="pumpkin" if i % 2 else "pumpkin_dark",
                 loc=(math.cos(a) * 0.42, math.sin(a) * 0.42, 0.6), scale=(0.75, 0.75, 1.0),
                 rot=(0, 0, 45 * i))
    m.tube([(0, 0, 1.05), (0.05, 0, 1.35), (0.15, 0, 1.45)], [0.1, 0.08, 0.07], seg=6, color="wood_mid")
    m.leaf(length=0.5, width=0.35, thick=0.05, color="leaf", loc=(0.05, 0.05, 1.12), rot=(80, 0, 40))


@asset("Eggplant", CAT, sub="Vegetable")
def eggplant(m):
    m.tube([(0, 0, 0.3), (0.2, 0, 0.35), (0.62, 0, 0.5), (0.95, 0, 0.72), (1.1, 0, 0.85)],
           [0.28, 0.34, 0.3, 0.2, 0.12], seg=12, color="eggplant", angle=45)
    m.lathe([(0.2, 0), (0.24, 0.05), (0.12, 0.2), (0, 0.22)], seg=6, color="leaf_dark",
            loc=(1.02, 0, 0.78), rot=(0, 55, 0))
    m.tube([(1.1, 0, 0.85), (1.25, 0, 1.0)], [0.05, 0.045], seg=5, color="leaf_dark")


@asset("Potato", CAT, sub="Vegetable")
def potato(m):
    m.ico(r=0.5, sub=2, color="potato", loc=(0, 0, 0.35), scale=(1.3, 0.9, 0.7), deform=jitter(0.05, 7))
    for x, y, z in ((0.3, -0.28, 0.5), (-0.4, -0.2, 0.35), (0.1, 0.3, 0.6)):
        m.sphere(r=0.04, seg=4, rings=2, color="potato_dark", loc=(x, y, z))


@asset("Broccoli", CAT, sub="Vegetable")
def broccoli(m):
    m.tube([(0, 0, 0), (0, 0, 0.6)], [0.18, 0.14], seg=8, color="cabbage")
    for x, y, z, r in ((0, 0, 0.8, 0.34), (0.3, 0.1, 0.7, 0.26), (-0.28, 0.12, 0.72, 0.26),
                       (0.05, -0.3, 0.7, 0.26), (0.02, 0.3, 0.74, 0.24)):
        m.ico(r=r, sub=1, color="broccoli", loc=(x, y, z), deform=jitter(0.02, 2), angle=40)


@asset("Mushroom", CAT, sub="Vegetable")
def mushroom(m):
    m.lathe([(0.16, 0), (0.14, 0.35), (0.12, 0.55), (0, 0.55)], seg=10, color="offwhite")
    m.lathe([(0, 0.45), (0.5, 0.48), (0.55, 0.6), (0.45, 0.82), (0.22, 0.95), (0, 0.97)],
            seg=12, color=by_normal("apple_red", "apple_red", "offwhite", thresh=0.3))
    for a, h, r in ((20, 0.82, 0.3), (140, 0.78, 0.36), (260, 0.8, 0.32), (0, 0.95, 0.0)):
        x, y = math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r
        m.sphere(r=0.08, seg=6, rings=4, color="white", loc=(x, y, h), scale=(1, 1, 0.45))


@asset("Onion", CAT, sub="Vegetable")
def onion(m):
    m.lathe([(0, 0), (0.25, 0.03), (0.48, 0.25), (0.46, 0.55), (0.25, 0.8), (0.08, 0.95), (0, 1.0)],
            seg=12, color="onion")
    m.lathe([(0.06, 0.95), (0.03, 1.15), (0, 1.2)], seg=5, color="leaf")


@asset("Pepper", CAT, sub="Vegetable")
def pepper(m):
    for i in range(4):
        a = math.radians(90 * i + 45)
        m.sphere(r=0.36, seg=10, rings=8, color="pepper_red", loc=(math.cos(a) * 0.16, math.sin(a) * 0.16, 0.48),
                 scale=(0.9, 0.9, 1.35))
    m.cyl(r=0.12, h=0.1, seg=6, color="leaf_dark", loc=(0, 0, 0.98))
    m.tube([(0, 0, 1.0), (0.08, 0, 1.22)], [0.05, 0.04], seg=5, color="leaf_dark")


@asset("Cabbage", CAT, sub="Vegetable")
def cabbage(m):
    m.sphere(r=0.5, seg=12, rings=8, color="cabbage", loc=(0, 0, 0.5))
    for i in range(6):
        a = 60 * i
        m.sphere(r=0.42, seg=10, rings=6, color="leaf_light" if i % 2 else "cabbage",
                 loc=(math.cos(math.radians(a)) * 0.2, math.sin(math.radians(a)) * 0.2, 0.42),
                 scale=(0.9, 1.25, 0.95), rot=(0, 25, a))


@asset("Radish", CAT, sub="Vegetable")
def radish(m):
    m.lathe([(0, 0), (0.05, 0.1), (0.3, 0.3), (0.34, 0.5), (0.22, 0.68), (0, 0.72)], seg=10, color="radish")
    for a in (0, 120, 240):
        m.leaf(length=0.6, width=0.3, thick=0.05, color="leaf", loc=(0, 0, 0.68), rot=(72, 0, a))


# --- snacks & meals ------------------------------------------------------------
@asset("Bread", CAT, sub="Snack")
def bread(m):
    m.box((1.6, 0.9, 0.5), color="bread", bevel=0.18, bseg=2, loc=(0, 0, 0.25))
    m.sphere(r=0.5, seg=12, rings=6, color="bread_crust", loc=(0, 0, 0.5), scale=(1.6, 0.9, 0.55))
    for x in (-0.45, 0, 0.45):
        m.sphere(r=0.2, seg=8, rings=4, color="bread", loc=(x, 0, 0.74 - abs(x) * 0.07),
                 scale=(0.35, 1.0, 0.18), rot=(0, 0, 28))


@asset("Baguette", CAT, sub="Snack")
def baguette(m):
    m.tube([(-1.2, 0, 0.2), (-1.0, 0, 0.22), (1.0, 0, 0.22), (1.2, 0, 0.2)], [0.08, 0.2, 0.2, 0.08],
           seg=10, color="bread_crust")
    for x in (-0.6, -0.1, 0.4):
        m.box((0.36, 0.12, 0.05), color="bread", loc=(x, 0, 0.4), rot=(0, 0, 30))


@asset("Cheese", CAT, sub="Snack")
def cheese(m):
    m.wedge((0.9, 1.3, 0.55), color="cheese", loc=(0, 0, 0.275), rot=(0, 0, 0))
    for x, y, z, r in ((0.46, -0.1, 0.2, 0.09), (0.46, -0.4, 0.35, 0.06), (-0.46, 0.0, 0.15, 0.08),
                       (0.1, 0.2, 0.05, 0.07)):
        m.sphere(r=r, seg=6, rings=4, color="cheese_dark", loc=(x, y, z), scale=(0.5, 1, 1))


@asset("Donut", CAT, sub="Snack")
def donut(m):
    m.torus(R=0.45, r=0.24, seg=16, rseg=8, color="donut", loc=(0, 0, 0.24))
    m.torus(R=0.45, r=0.245, seg=16, rseg=8, color="frosting_pink", loc=(0, 0, 0.27),
            deform=lambda co: co if co.z > -0.02 else co.__class__((co.x, co.y, -0.02)))
    cols = ["sprinkle_blue", "sprinkle_yellow", "white", "candy_green"]
    for i in range(14):
        a = i * 137.5
        r = 0.45 + math.sin(i * 1.7) * 0.12
        m.box((0.1, 0.03, 0.03), color=cols[i % 4],
              loc=(math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r, 0.51), rot=(0, 0, a * 1.3))


@asset("Cookie", CAT, sub="Snack")
def cookie(m):
    m.cyl(r=0.6, h=0.16, seg=14, color="cookie", bevel=0.05, loc=(0, 0, 0.08))
    for i in range(7):
        a = i * 137.5
        r = 0.18 + (i % 3) * 0.14
        m.box((0.1, 0.1, 0.06), color="cookie_chip", bevel=0.02, bseg=1,
              loc=(math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r, 0.17), rot=(0, 0, a))


@asset("CakeSlice", CAT, sub="Snack")
def cake_slice(m):
    out = [(0, 0), (1.1, -0.38), (1.1, 0.38)]
    m.prism(out, depth=0.3, color="bread", loc=(-0.55, 0, 0.15))
    m.prism(out, depth=0.08, color="jam", loc=(-0.55, 0, 0.34), scale=(0.99, 0.99, 1))
    m.prism(out, depth=0.3, color="bread", loc=(-0.55, 0, 0.53))
    m.prism(out, depth=0.1, color="frosting_white", loc=(-0.55, 0, 0.73), scale=(1.01, 1.01, 1), bevel=0.03)
    m.sphere(r=0.13, seg=8, rings=6, color="cherry", loc=(0.3, 0, 0.9))
    m.tube([(0.3, 0, 1.0), (0.36, 0, 1.15)], [0.02, 0.02], seg=4, color="leaf_dark")


@asset("Cupcake", CAT, sub="Snack")
def cupcake(m):
    m.lathe([(0.3, 0), (0.42, 0.5), (0, 0.5)], seg=12, color="plastic_pink", smooth=False)
    m.lathe([(0.44, 0.46), (0.48, 0.58), (0.4, 0.72), (0.3, 0.82), (0.2, 0.95), (0.08, 1.05), (0, 1.08)],
            seg=12, color="frosting_white")
    m.sphere(r=0.1, seg=8, rings=6, color="cherry", loc=(0, 0, 1.13))


@asset("IceCream", CAT, sub="Snack")
def ice_cream(m):
    m.cone(r=0.32, h=1.0, seg=10, color="cone", rot=(180, 0, 0), loc=(0, 0, 1.0), smooth=False)
    m.sphere(r=0.34, seg=12, rings=8, color="icecream_straw", loc=(0, 0, 1.12))
    m.sphere(r=0.3, seg=12, rings=8, color="icecream_mint", loc=(0, 0, 1.48))
    m.sphere(r=0.08, seg=8, rings=6, color="cherry", loc=(0, 0, 1.8))


@asset("Popsicle", CAT, sub="Snack")
def popsicle(m):
    m.box((0.12, 0.05, 0.6), color="wood_pale", loc=(0, 0, 0.3), bevel=0.02)
    m.box((0.46, 0.2, 0.9), color=by_height("candy_pink", 0.78, "icecream_van", 1.08, "candy_blue"),
          bevel=0.12, bseg=2, loc=(0, 0, 0.9), cuts={"z": [0.78, 1.08]})


@asset("Lollipop", CAT, sub="Snack")
def lollipop(m):
    m.cyl(r=0.04, h=1.0, seg=6, color="white", loc=(0, 0, 0.5))
    def swirl(c, n):
        dx, dz = c.x, c.z - 1.35
        a = math.degrees(math.atan2(dz, dx)) + math.hypot(dx, dz) * 700
        return ["candy_pink", "white", "candy_blue", "white"][int((a + 3600) / 45) % 4]
    prof = [(0, -0.09), (0.14, -0.09), (0.28, -0.08), (0.42, -0.05), (0.45, 0), (0.42, 0.05),
            (0.28, 0.08), (0.14, 0.09), (0, 0.09)]
    m.lathe(prof, seg=16, color=swirl, rot=(90, 0, 0), loc=(0, 0, 1.35), angle=50)


@asset("Candy", CAT, sub="Snack")
def candy(m):
    m.sphere(r=0.3, seg=12, rings=8, color="candy_blue", loc=(0, 0, 0.3), scale=(1.25, 1, 1))
    for s in (-1, 1):
        m.cone(r=0.24, h=0.34, seg=7, color="candy_pink", loc=(s * 0.66, 0, 0.3), rot=(0, s * -90, 0),
               smooth=False)
        m.cyl(r=0.07, h=0.12, seg=6, color="candy_pink", loc=(s * 0.36, 0, 0.3), rot=(0, 90, 0))


@asset("ChocolateBar", CAT, sub="Snack")
def chocolate_bar(m):
    m.box((1.2, 0.7, 0.12), color="chocolate", bevel=0.03, loc=(0, 0, 0.06))
    for i in range(4):
        for j in range(2):
            m.box((0.26, 0.28, 0.08), color="chocolate", bevel=0.03, bseg=1,
                  loc=(-0.44 + i * 0.29, -0.16 + j * 0.32, 0.14))
    m.box((0.62, 0.74, 0.16), color="plastic_red", bevel=0.02, loc=(0.32, 0, 0.08))


@asset("PizzaSlice", CAT, sub="Snack")
def pizza_slice(m):
    tri = [(-0.55, 0), (0.75, -0.55), (0.75, 0.55)]
    m.prism(tri, depth=0.1, color="cheese", loc=(0, 0, 0.1))
    m.tube([(0.78, -0.58, 0.14), (0.8, 0, 0.16), (0.78, 0.58, 0.14)], [0.12, 0.13, 0.12], seg=8, color="bread_crust")
    for x, y in ((0.3, -0.15), (0.45, 0.25), (0.05, 0.08), (0.55, -0.3)):
        m.cyl(r=0.1, h=0.04, seg=10, color="pepperoni", loc=(x, y, 0.16))


@asset("Burger", CAT, sub="Snack")
def burger(m):
    m.cyl(r=0.6, h=0.2, seg=14, color="bread", bevel=0.08, loc=(0, 0, 0.1))
    m.cyl(r=0.64, h=0.18, seg=14, color="meat", bevel=0.06, loc=(0, 0, 0.3))
    m.cyl(r=0.66, h=0.04, seg=6, color="cheese", loc=(0, 0, 0.41), rot=(0, 0, 15), smooth=False)
    m.cyl(r=0.66, h=0.05, seg=10, color="lettuce", loc=(0, 0, 0.45), deform=jitter(0.03, 5, (1, 1, 0)))
    m.cyl(r=0.5, h=0.06, seg=12, color="tomato", loc=(0, 0, 0.5))
    m.lathe([(0.6, 0.52), (0.62, 0.62), (0.55, 0.8), (0.35, 0.93), (0, 0.97)], seg=14, color="bread")
    for i in range(7):
        a = i * 137.5
        r = 0.15 + (i % 3) * 0.12
        m.sphere(r=0.03, seg=4, rings=3, color="offwhite",
                 loc=(math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r,
                      0.94 - (r / 0.6) ** 2 * 0.3), scale=(1.5, 1, 0.6))


@asset("HotDog", CAT, sub="Snack")
def hotdog(m):
    m.box((1.4, 0.55, 0.3), color="bread", bevel=0.14, loc=(0, 0, 0.15))
    for s in (-1, 1):
        m.box((1.35, 0.14, 0.2), color="bread", bevel=0.07, loc=(0, s * 0.22, 0.38))
    m.tube([(-0.85, 0, 0.36), (0, 0, 0.36), (0.85, 0, 0.36)], [0.14, 0.15, 0.14], seg=8, color="meat_light")
    m.tube([(-0.55, 0, 0.5), (-0.3, 0.06, 0.52), (0, -0.06, 0.52), (0.3, 0.06, 0.52), (0.55, 0, 0.5)],
           [0.03] * 5, seg=4, color="egg_yolk")


@asset("Taco", CAT, sub="Snack")
def taco(m):
    R = 0.7
    half = [(math.cos(math.radians(180 + 180 * i / 10)) * R, math.sin(math.radians(180 + 180 * i / 10)) * R + R)
            for i in range(11)]
    for s in (-1, 1):
        m.prism(half, depth=0.06, color="corn", bevel=0.02, bseg=1, rot=(90 + s * 14, 0, 0),
                loc=(0, s * 0.1, 0.02))
    m.sphere(r=0.6, seg=10, rings=6, color="lettuce", loc=(0, 0, 0.66), scale=(1.05, 0.32, 0.18),
             deform=jitter(0.04, 9))
    m.sphere(r=0.55, seg=10, rings=6, color="meat", loc=(0, 0, 0.6), scale=(1.0, 0.26, 0.2))
    for x in (-0.35, 0.0, 0.32):
        m.box((0.18, 0.12, 0.06), color="cheese", loc=(x, 0, 0.76), rot=(0, 0, 30))
    m.box((0.1, 0.1, 0.08), color="tomato", loc=(0.2, 0.02, 0.73), rot=(0, 0, 10))


@asset("Sushi", CAT, sub="Snack")
def sushi(m):
    m.box((0.9, 0.5, 0.35), color="sushi_rice", bevel=0.15, loc=(0, 0, 0.18))
    m.box((1.0, 0.56, 0.12), color="fish_orange", bevel=0.05, loc=(0, 0, 0.41))
    m.box((0.18, 0.6, 0.5), color="nori", loc=(0, 0, 0.25))


@asset("Egg", CAT, sub="Snack")
def egg(m):
    m.lathe([(0, 0), (0.28, 0.05), (0.38, 0.3), (0.34, 0.6), (0.2, 0.82), (0, 0.88)], seg=12,
            color="offwhite")


@asset("FriedEgg", CAT, sub="Snack")
def fried_egg(m):
    m.cyl(r=0.6, h=0.06, seg=12, color="white", loc=(0, 0, 0.03), deform=jitter(0.06, 4, (1, 1, 0)),
          scale=(1.1, 1, 1))
    m.sphere(r=0.22, seg=10, rings=6, color="egg_yolk", loc=(0.05, 0, 0.06), scale=(1, 1, 0.55))


@asset("Steak", CAT, sub="Snack")
def steak(m):
    m.cyl(r=0.6, h=0.2, seg=10, color="meat", bevel=0.06, loc=(0, 0, 0.1), scale=(1.3, 0.9, 1),
          deform=jitter(0.03, 11, (1, 1, 0)))
    for i in range(3):
        m.box((1.0, 0.05, 0.02), color="chocolate_dark", loc=(0, -0.3 + i * 0.3, 0.205), rot=(0, 0, 30))
    m.tube([(-0.5, 0.35, 0.12), (0.2, 0.52, 0.12)], [0.05, 0.05], seg=5, color="meat_light")


@asset("MeatDrumstick", CAT, sub="Snack")
def drumstick(m):
    m.tube([(0.1, 0, 0.3), (0.55, 0, 0.35), (0.95, 0, 0.3)], [0.3, 0.34, 0.28], seg=10, color="caramel")
    m.sphere(r=0.35, seg=10, rings=8, color="caramel", loc=(0.9, 0, 0.3), scale=(1.1, 1, 0.9))
    m.tube([(0.15, 0, 0.3), (-0.45, 0, 0.3)], [0.08, 0.08], seg=6, color="offwhite")
    for y in (-0.08, 0.08):
        m.sphere(r=0.1, seg=6, rings=4, color="offwhite", loc=(-0.5, y, 0.3))


@asset("Honeypot", CAT, sub="Snack")
def honeypot(m):
    m.lathe([(0, 0), (0.4, 0.02), (0.55, 0.3), (0.52, 0.65), (0.36, 0.8), (0.38, 0.9), (0, 0.9)],
            seg=12, color=by_height("clay", 0.82, "honey"))
    m.lathe([(0.39, 0.82), (0.36, 0.95), (0, 0.97)], seg=12, color="honey")
    m.tube([(0.12, -0.3, 0.95), (0.12, -0.36, 0.7)], [0.08, 0.02], seg=6, color="honey")
    m.torus(R=0.4, r=0.05, seg=12, rseg=5, color="rope", loc=(0, 0, 0.78))


@asset("MilkCarton", CAT, sub="Snack")
def milk_carton(m):
    m.box((0.5, 0.5, 0.9), color=by_height("plastic_white", 0.3, "plastic_blue", 0.68, "plastic_white"),
          bevel=0.02, loc=(0, 0, 0.45), cuts={"z": [0.3, 0.68]})
    # gable roof: triangle in (z, y) extruded along X
    m.prism([(0, -0.25), (0.26, 0), (0, 0.25)], depth=0.5, color="plastic_white", rot=(0, -90, 0),
            loc=(0, 0, 0.9), smooth=False)
    m.box((0.5, 0.06, 0.12), color="plastic_white", loc=(0, 0, 1.2), bevel=0.02)


@asset("Juice", CAT, sub="Snack")
def juice(m):
    m.lathe([(0, 0), (0.3, 0), (0.34, 0.8), (0, 0.8)], seg=12, color=by_height("glass", 0.06, "orange", 0.7, "glass"))
    m.cyl(r=0.035, h=0.6, seg=5, color="plastic_pink", loc=(0.1, 0, 0.95), rot=(0, 12, 0))
    m.cyl(r=0.1, h=0.03, seg=8, color="lemon", loc=(-0.3, 0, 0.78), rot=(90, 0, 0))
