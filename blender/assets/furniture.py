"""Furniture & home decor, sized for Roblox characters (~5 studs tall).

Seat height ~1.8 studs, table height ~3 studs, doors ~7 studs.
"""
import math

from studlib.geo import by_height, by_normal, circle_pts, jitter
from studlib.registry import asset

CAT = "Furniture"


def legs4(m, w, d, h, r=0.14, color="wood_dark", inset=0.2, square=True):
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (w / 2 - inset), sy * (d / 2 - inset)
            if square:
                m.box((r * 2, r * 2, h), color=color, bevel=0.04, bseg=1, loc=(x, y, h / 2))
            else:
                m.cyl(r=r, r2=r * 0.8, h=h, seg=8, color=color, loc=(x, y, h / 2))


def cushion(m, size, loc, color, rot=(0, 0, 0)):
    m.box(size, color=color, bevel=min(size) * 0.35, bseg=3, loc=loc, rot=rot, angle=60)


def books(m, x0, x1, y, z, depth=0.8, seed=0):
    cols = ["fabric_red", "fabric_blue", "fabric_green", "fabric_yellow", "fabric_purple", "fabric_teal",
            "fabric_orange", "leather"]
    x = x0
    i = seed
    while x < x1 - 0.15:
        w = 0.14 + ((i * 37) % 5) * 0.03
        h = 0.9 + ((i * 53) % 4) * 0.12
        if x + w > x1:
            break
        tilt = 8 if (i * 7) % 11 == 0 else 0
        m.box((w, depth, h), color=cols[(i * 5) % len(cols)], bevel=0.02, bseg=1,
              loc=(x + w / 2, y, z + h / 2), rot=(0, tilt, 0))
        x += w + 0.02
        i += 1


# --- seating --------------------------------------------------------------------
@asset("Chair", CAT, sub="Seating")
def chair(m):
    m.box((1.9, 1.9, 0.25), color="wood", bevel=0.08, loc=(0, 0, 1.75))
    legs4(m, 1.9, 1.9, 1.65, r=0.13, color="wood_mid")
    for x in (-0.75, 0.75):
        m.box((0.24, 0.24, 2.2), color="wood_mid", bevel=0.06, loc=(x, 0.8, 2.9))
    m.box((1.9, 0.22, 0.6), color="wood", bevel=0.08, loc=(0, 0.8, 3.75))
    m.box((1.5, 0.16, 0.25), color="wood", bevel=0.05, loc=(0, 0.8, 2.75))


@asset("DiningChair", CAT, sub="Seating")
def dining_chair(m):
    chair(m)
    cushion(m, (1.7, 1.7, 0.3), (0, -0.05, 1.98), "fabric_red")


@asset("Stool", CAT, sub="Seating")
def stool(m):
    m.cyl(r=0.9, h=0.25, seg=14, color="wood", bevel=0.08, loc=(0, 0, 1.75))
    for i in range(3):
        a = math.radians(120 * i + 90)
        m.tube([(math.cos(a) * 0.55, math.sin(a) * 0.55, 1.7), (math.cos(a) * 0.8, math.sin(a) * 0.8, 0.05)],
               [0.1, 0.1], seg=6, color="wood_mid")
    m.torus(R=0.62, r=0.05, seg=12, rseg=4, color="wood_mid", loc=(0, 0, 0.7))


@asset("BarStool", CAT, sub="Seating")
def bar_stool(m):
    m.cyl(r=0.85, h=0.35, seg=14, color="fabric_red", bevel=0.14, loc=(0, 0, 3.2))
    m.cyl(r=0.12, h=3.0, seg=8, color="chrome", loc=(0, 0, 1.55))
    m.cyl(r=0.8, h=0.12, seg=14, color="chrome", bevel=0.05, loc=(0, 0, 0.06))
    m.torus(R=0.55, r=0.05, seg=12, rseg=4, color="chrome", loc=(0, 0, 1.3))


@asset("Bench", CAT, sub="Seating")
def bench(m):
    m.box((5.0, 1.6, 0.3), color="wood", bevel=0.08, loc=(0, 0, 1.65))
    for x in (-2.1, 2.1):
        m.box((0.3, 1.4, 1.5), color="wood_mid", bevel=0.06, loc=(x, 0, 0.75))


@asset("ParkBench", CAT, sub="Seating")
def park_bench(m):
    for i in range(3):
        m.box((5.4, 0.42, 0.14), color="wood", bevel=0.05, loc=(0, -0.6 + i * 0.5, 1.7))
    for i in range(2):
        m.box((5.4, 0.14, 0.42), color="wood", bevel=0.05, loc=(0, 0.95, 2.4 + i * 0.6), rot=(-12, 0, 0))
    for x in (-2.2, 2.2):
        m.box((0.18, 1.8, 0.2), color="charcoal", bevel=0.05, loc=(x, 0, 1.55))
        m.box((0.18, 0.2, 1.55), color="charcoal", bevel=0.05, loc=(x, -0.7, 0.78))
        m.box((0.18, 0.2, 3.2), color="charcoal", bevel=0.05, loc=(x, 0.85, 1.6), rot=(-12, 0, 0))
        m.box((0.18, 1.6, 0.18), color="charcoal", bevel=0.05, loc=(x, -0.05, 2.35))


@asset("Armchair", CAT, sub="Seating")
def armchair(m):
    col = "fabric_teal"
    m.box((3.2, 2.9, 1.2), color=col, bevel=0.3, bseg=3, loc=(0, 0, 0.9))
    cushion(m, (2.2, 2.3, 0.55), (0, -0.2, 1.75), col)
    m.box((3.2, 0.8, 2.6), color=col, bevel=0.35, bseg=3, loc=(0, 1.05, 2.0))
    for x in (-1.35, 1.35):
        m.box((0.6, 2.9, 1.1), color=col, bevel=0.28, bseg=3, loc=(x, 0, 2.0))
    legs4(m, 3.0, 2.7, 0.35, r=0.12, color="wood_dark", square=False)


@asset("Sofa", CAT, sub="Seating")
def sofa(m, width=5.6, col="fabric_blue", seats=2):
    m.box((width, 2.9, 1.2), color=col, bevel=0.3, bseg=3, loc=(0, 0, 0.9))
    inner = width - 1.2
    for i in range(seats):
        w = inner / seats
        cushion(m, (w - 0.08, 2.3, 0.55), (-inner / 2 + w * (i + 0.5), -0.2, 1.75), col)
        cushion(m, (w - 0.1, 0.6, 1.5), (-inner / 2 + w * (i + 0.5), 0.9, 2.55), col)
    m.box((width, 0.7, 2.8), color=col, bevel=0.32, bseg=3, loc=(0, 1.1, 2.0))
    for x in (-(width / 2 - 0.3), width / 2 - 0.3):
        m.box((0.6, 2.9, 1.15), color=col, bevel=0.28, bseg=3, loc=(x, 0, 2.0))
    legs4(m, width - 0.2, 2.7, 0.35, r=0.12, color="wood_dark", square=False)


@asset("LongSofa", CAT, sub="Seating")
def long_sofa(m):
    sofa(m, width=8.0, col="fabric_gray", seats=3)
    for x, c in ((-2.6, "fabric_yellow"), (2.6, "fabric_teal")):
        cushion(m, (1.0, 0.35, 1.0), (x, 0.55, 2.55), c, rot=(-15, 0, 0))


@asset("Beanbag", CAT, sub="Seating")
def beanbag(m):
    m.sphere(r=1.3, seg=14, rings=9, color="fabric_purple", loc=(0, 0, 1.05), scale=(1, 1, 0.8),
             deform=lambda co: co.__class__((co.x, co.y, co.z * (1 - 0.25 * max(0, -co.y) / 1.3))))
    m.sphere(r=0.8, seg=12, rings=8, color="fabric_purple", loc=(0, 0.55, 1.75), scale=(1.2, 0.8, 0.9))


@asset("OfficeChair", CAT, sub="Seating")
def office_chair(m):
    cushion(m, (2.0, 2.0, 0.4), (0, 0, 2.0), "plastic_black")
    cushion(m, (1.9, 0.35, 2.2), (0, 0.9, 3.4), "plastic_black")
    m.box((0.3, 0.2, 1.2), color="chrome", loc=(0, 0.95, 2.4))
    m.cyl(r=0.15, h=1.4, seg=8, color="chrome", loc=(0, 0, 1.1))
    for i in range(5):
        a = math.radians(72 * i)
        m.box((1.2, 0.18, 0.12), color="plastic_black", loc=(math.cos(a) * 0.55, math.sin(a) * 0.55, 0.35),
              rot=(0, 0, 72 * i))
        m.sphere(r=0.14, seg=8, rings=5, color="rubber", loc=(math.cos(a) * 1.1, math.sin(a) * 1.1, 0.14))
    for x in (-1.05, 1.05):
        m.box((0.15, 0.15, 0.7), color="plastic_black", loc=(x, 0.1, 2.5))
        m.box((0.28, 1.2, 0.14), color="plastic_black", bevel=0.05, loc=(x, 0.1, 2.85))


@asset("Throne", CAT, sub="Seating", tags=["rare"])
def throne(m):
    m.box((3.4, 3.0, 1.6), color="gold", bevel=0.12, loc=(0, 0, 0.8))
    cushion(m, (2.4, 2.4, 0.5), (0, -0.2, 1.8), "fabric_red")
    m.box((3.4, 0.6, 5.0), color="gold", bevel=0.12, loc=(0, 1.2, 3.0))
    m.box((2.4, 0.3, 3.4), color="fabric_red", bevel=0.15, loc=(0, 0.85, 3.3))
    for x in (-1.45, 1.45):
        m.box((0.5, 3.0, 1.2), color="gold_dark", bevel=0.1, loc=(x, 0, 2.2))
        m.sphere(r=0.3, seg=10, rings=6, color="gold", loc=(x, -1.3, 2.9))
    for x in (-1.2, 0, 1.2):
        m.cone(r=0.3, h=0.7, seg=6, color="gold", loc=(x, 1.2, 5.5), smooth=False)
        m.gem(r=0.14, h=0.14, seg=6, color="ruby", rot=(90, 0, 0), loc=(x, 0.88, 5.1))


@asset("RockingChair", CAT, sub="Seating")
def rocking_chair(m):
    m.box((1.9, 1.9, 0.22), color="wood", bevel=0.07, loc=(0, 0, 1.6))
    for x in (-0.8, 0.8):
        pts = [(x, -1.4 + 2.8 * i / 8, 0.1 + 0.35 * ((i - 4) / 4) ** 2) for i in range(9)]
        m.tube(pts, [0.1] * 9, seg=6, color="wood_mid", up=(1, 0, 0))
        m.box((0.2, 0.2, 1.5), color="wood_mid", loc=(x, -0.7, 0.9))
        m.box((0.2, 0.2, 3.4), color="wood_mid", loc=(x, 0.8, 1.9), rot=(-8, 0, 0))
    for z in (2.6, 3.1, 3.6):
        m.box((1.8, 0.14, 0.2), color="wood", bevel=0.04, loc=(0, 0.85 + (z - 2.6) * 0.14, z), rot=(-8, 0, 0))


# --- tables -------------------------------------------------------------------------
@asset("Table", CAT, sub="Tables")
def table(m):
    m.box((6.0, 3.6, 0.3), color="wood", bevel=0.1, loc=(0, 0, 2.95))
    legs4(m, 6.0, 3.6, 2.8, r=0.18, color="wood_mid", inset=0.35)
    m.box((5.2, 0.14, 0.4), color="wood_mid", loc=(0, 1.45, 2.6))
    m.box((5.2, 0.14, 0.4), color="wood_mid", loc=(0, -1.45, 2.6))


@asset("RoundTable", CAT, sub="Tables")
def round_table(m):
    m.cyl(r=2.2, h=0.28, seg=20, color="wood_light", bevel=0.1, loc=(0, 0, 2.95))
    m.cyl(r=0.25, h=2.8, seg=10, color="wood_mid", loc=(0, 0, 1.45))
    m.cyl(r=1.1, r2=0.6, h=0.3, seg=14, color="wood_mid", bevel=0.08, loc=(0, 0, 0.15))


@asset("CoffeeTable", CAT, sub="Tables")
def coffee_table(m):
    m.box((4.0, 2.2, 0.25), color="wood_dark", bevel=0.08, loc=(0, 0, 1.35))
    m.box((3.6, 1.9, 0.12), color="wood_dark", bevel=0.04, loc=(0, 0, 0.45))
    legs4(m, 4.0, 2.2, 1.25, r=0.13, color="wood_deep", inset=0.25)
    m.cyl(r=0.3, h=0.35, seg=10, color="plastic_white", loc=(1.1, 0.3, 1.65))
    m.box((1.0, 0.7, 0.12), color="fabric_red", loc=(-0.8, -0.1, 1.54), rot=(0, 0, 10))


@asset("Desk", CAT, sub="Tables")
def desk(m):
    m.box((5.0, 2.4, 0.25), color="wood_light", bevel=0.07, loc=(0, 0, 2.9))
    m.box((1.6, 2.2, 2.75), color="wood", bevel=0.06, loc=(1.6, 0, 1.4))
    for z in (0.7, 1.55, 2.3):
        m.box((1.4, 0.1, 0.65), color="wood_light", bevel=0.04, loc=(1.6, -1.12, z))
        m.box((0.4, 0.08, 0.1), color="gold", loc=(1.6, -1.2, z + 0.1))
    m.box((0.22, 2.1, 2.75), color="wood", loc=(-2.3, 0, 1.4))


@asset("Nightstand", CAT, sub="Bedroom")
def nightstand(m):
    m.box((1.8, 1.6, 2.0), color="wood", bevel=0.08, loc=(0, 0, 1.1))
    for z in (0.7, 1.5):
        m.box((1.5, 0.1, 0.6), color="wood_light", bevel=0.04, loc=(0, -0.8, z))
        m.sphere(r=0.08, seg=6, rings=4, color="gold", loc=(0, -0.88, z))
    legs4(m, 1.8, 1.6, 0.12, r=0.1, color="wood_dark", inset=0.15)


@asset("PicnicTable", CAT, sub="Tables")
def picnic_table(m):
    for i in range(4):
        m.box((6.0, 0.62, 0.18), color="wood", bevel=0.05, loc=(0, -0.95 + i * 0.64, 2.9))
    for s in (-1, 1):
        for i in range(2):
            m.box((6.0, 0.55, 0.16), color="wood", bevel=0.05, loc=(0, s * (2.0 + i * 0.56) - s * 0.28, 1.7))
        for x in (-2.3, 2.3):
            m.box((0.2, 0.2, 3.4), color="wood_mid", loc=(x, s * 1.0, 1.45), rot=(s * -32, 0, 0))
    for x in (-2.3, 2.3):
        m.box((0.2, 4.6, 0.2), color="wood_mid", loc=(x, 0, 1.55))


# --- bedroom --------------------------------------------------------------------------
@asset("Bed", CAT, sub="Bedroom")
def bed(m, width=3.6, blanket="fabric_blue", frame="wood"):
    L = 7.2
    m.box((width + 0.3, L, 0.7), color=frame, bevel=0.1, loc=(0, 0, 0.75))
    legs4(m, width + 0.3, L, 0.45, r=0.16, color="wood_dark", inset=0.2)
    m.box((width, L - 0.4, 0.7), color="fabric_white", bevel=0.2, bseg=2, loc=(0, -0.1, 1.4))
    m.box((width + 0.1, L * 0.62, 0.3), color=blanket, bevel=0.12, bseg=2, loc=(0, -L * 0.17, 1.72))
    m.box((width + 0.12, 0.4, 0.32), color="fabric_white", bevel=0.12, bseg=2, loc=(0, L * 0.12, 1.73))
    np = 2 if width > 4 else 1
    for i in range(np):
        x = 0 if np == 1 else (-1 + 2 * i) * width / 4
        cushion(m, (width / np - 0.4, 1.3, 0.45), (x, L / 2 - 1.0, 1.95), "fabric_white")
    m.box((width + 0.3, 0.35, 3.4), color=frame, bevel=0.12, loc=(0, L / 2 + 0.1, 1.7))
    m.box((width + 0.3, 0.3, 1.9), color=frame, bevel=0.1, loc=(0, -L / 2 - 0.1, 0.95))


@asset("DoubleBed", CAT, sub="Bedroom")
def double_bed(m):
    bed(m, width=5.4, blanket="fabric_red", frame="wood_dark")


@asset("KidsBed", CAT, sub="Bedroom")
def kids_bed(m):
    bed(m, width=3.4, blanket="fabric_pink", frame="plastic_white")


@asset("BunkBed", CAT, sub="Bedroom")
def bunk_bed(m):
    L, W = 7.0, 3.6
    for x in (-W / 2, W / 2):
        for y in (-L / 2, L / 2):
            m.box((0.3, 0.3, 7.0), color="wood", bevel=0.06, loc=(x, y, 3.5))
    for z, col in ((1.1, "fabric_blue"), (4.6, "fabric_green")):
        m.box((W, L, 0.35), color="wood_mid", bevel=0.06, loc=(0, 0, z))
        m.box((W - 0.2, L - 0.3, 0.6), color="fabric_white", bevel=0.18, loc=(0, 0, z + 0.45))
        m.box((W - 0.1, L * 0.6, 0.25), color=col, bevel=0.1, loc=(0, -L * 0.18, z + 0.8))
        cushion(m, (W - 0.8, 1.1, 0.4), (0, L / 2 - 0.9, z + 0.95), "fabric_white")
    for y in (-L / 2, L / 2):
        m.box((W, 0.2, 0.4), color="wood_mid", loc=(0, y, 6.2))
    m.box((0.15, L, 0.4), color="wood_mid", loc=(-W / 2, 0, 5.8))
    for x in (W / 2 + 0.05,):
        for z in (1.8, 2.6, 3.4, 4.2):
            m.box((0.15, 1.2, 0.15), color="wood_light", loc=(x + 0.1, -L / 2 + 1.0, z))
        for y in (-L / 2 + 0.4, -L / 2 + 1.6):
            m.box((0.15, 0.15, 5.0), color="wood_light", loc=(x + 0.1, y, 2.5))


@asset("Wardrobe", CAT, sub="Bedroom")
def wardrobe(m):
    m.box((4.2, 2.2, 7.0), color="wood", bevel=0.1, loc=(0, 0, 3.7))
    m.box((4.4, 2.4, 0.3), color="wood_dark", bevel=0.08, loc=(0, 0, 7.3))
    legs4(m, 4.2, 2.2, 0.3, r=0.14, color="wood_dark", inset=0.2)
    for x in (-1.02, 1.02):
        m.box((1.95, 0.12, 6.4), color="wood_light", bevel=0.06, loc=(x, -1.1, 3.8))
        m.box((0.12, 0.12, 0.8), color="gold", bevel=0.03, loc=(x * 0.1 + (0.08 if x > 0 else -0.08), -1.2, 3.9))


@asset("Dresser", CAT, sub="Bedroom")
def dresser(m):
    m.box((4.4, 2.0, 3.2), color="wood_mid", bevel=0.1, loc=(0, 0, 1.8))
    m.box((4.6, 2.2, 0.25), color="wood_dark", bevel=0.08, loc=(0, 0, 3.45))
    legs4(m, 4.4, 2.0, 0.25, r=0.14, color="wood_dark", inset=0.25)
    for i in range(3):
        z = 0.85 + i * 0.95
        for x in (-1.05, 1.05):
            m.box((2.0, 0.1, 0.8), color="wood", bevel=0.05, loc=(x, -1.0, z))
            m.sphere(r=0.1, seg=6, rings=4, color="gold", loc=(x, -1.08, z))
    m.box((2.6, 0.2, 2.0), color="wood_dark", bevel=0.08, loc=(0, 0.8, 4.6))
    m.box((2.2, 0.1, 1.6), color="glass", loc=(0, 0.7, 4.6))


@asset("Bookshelf", CAT, sub="Living")
def bookshelf(m):
    W, D, H = 4.2, 1.4, 6.4
    m.box((0.2, D, H), color="wood_mid", loc=(-W / 2 + 0.1, 0, H / 2))
    m.box((0.2, D, H), color="wood_mid", loc=(W / 2 - 0.1, 0, H / 2))
    m.box((W, 0.12, H), color="wood_dark", loc=(0, D / 2 - 0.06, H / 2))
    for i in range(5):
        z = 0.1 + i * 1.55
        m.box((W, D, 0.18), color="wood_mid", bevel=0.04, loc=(0, 0, min(z, H - 0.09)))
        if i < 4:
            books(m, -W / 2 + 0.25, W / 2 - 0.25, 0.05, z + 0.09, depth=1.0, seed=i * 3)


@asset("WallShelf", CAT, sub="Living")
def wall_shelf(m):
    m.box((4.0, 1.0, 0.18), color="wood", bevel=0.05, loc=(0, 0, 0.09))
    for x in (-1.5, 1.5):
        m.prism([(0, 0), (0.8, 0), (0, -0.8)], depth=0.12, color="charcoal", rot=(90, 0, 90), loc=(x, 0.1, 0.0))
    books(m, -1.8, 0.6, 0.0, 0.18, depth=0.8, seed=11)
    m.cyl(r=0.3, r2=0.35, h=0.5, seg=10, color="clay", loc=(1.3, 0, 0.43))
    m.sphere(r=0.35, seg=8, rings=6, color="leaf", loc=(1.3, 0, 0.85), deform=jitter(0.05, 3))


# --- kitchen ------------------------------------------------------------------------------
@asset("Fridge", CAT, sub="Kitchen")
def fridge(m):
    m.box((3.0, 2.6, 7.0), color="plastic_white", bevel=0.2, bseg=2, loc=(0, 0, 3.6))
    m.box((2.9, 0.1, 0.08), color="lightgray", loc=(0, -1.31, 4.9))
    for z0, z1 in ((0.5, 4.6), (5.2, 6.8)):
        m.box((0.16, 0.2, (z1 - z0) * 0.5), color="chrome", bevel=0.05, loc=(1.15, -1.4, (z0 + z1) / 2))
    m.box((0.9, 0.06, 0.7), color="fabric_yellow", loc=(-0.6, -1.32, 5.8), rot=(0, 8, 0))
    legs4(m, 3.0, 2.6, 0.12, r=0.12, color="charcoal", inset=0.25)


@asset("Stove", CAT, sub="Kitchen")
def stove(m):
    m.box((3.2, 2.6, 3.2), color="plastic_white", bevel=0.12, loc=(0, 0, 1.6))
    m.box((3.2, 2.6, 0.12), color="charcoal", bevel=0.04, loc=(0, 0, 3.24))
    for x in (-0.75, 0.75):
        for y in (-0.55, 0.55):
            m.cyl(r=0.48, h=0.08, seg=12, color="black", loc=(x, y, 3.32))
            m.torus(R=0.34, r=0.04, seg=12, rseg=4, color="iron_dark", loc=(x, y, 3.37))
    m.box((2.6, 0.1, 1.6), color="black", bevel=0.05, loc=(0, -1.31, 1.4))
    m.box((1.8, 0.08, 1.0), color="glass", loc=(0, -1.35, 1.4))
    m.box((2.2, 0.16, 0.14), color="chrome", bevel=0.04, loc=(0, -1.45, 2.4))
    m.box((3.2, 0.4, 0.6), color="plastic_white", bevel=0.08, loc=(0, 1.1, 3.5))
    for x in (-1.1, -0.4, 0.4, 1.1):
        m.cyl(r=0.14, h=0.12, seg=8, color="charcoal", rot=(90, 0, 0), loc=(x, -1.33, 2.85))


@asset("KitchenCounter", CAT, sub="Kitchen")
def kitchen_counter(m):
    m.box((4.0, 2.4, 3.0), color="wood_light", bevel=0.08, loc=(0, 0, 1.55))
    m.box((4.1, 2.5, 0.22), color="marble", bevel=0.06, loc=(0, 0, 3.12))
    m.box((4.0, 2.2, 0.15), color="charcoal", loc=(0, 0.05, 0.08))
    for x in (-1.0, 1.0):
        m.box((1.9, 0.1, 2.2), color="wood", bevel=0.05, loc=(x, -1.2, 1.5))
        m.box((0.1, 0.1, 0.5), color="chrome", loc=(x * 0.12, -1.28, 2.1))


@asset("KitchenSink", CAT, sub="Kitchen")
def kitchen_sink(m):
    kitchen_counter(m)
    m.box((2.0, 1.4, 0.1), color="steel", loc=(0, -0.1, 3.25))
    m.box((1.8, 1.2, 0.08), color="iron_dark", loc=(0, -0.1, 3.28))
    m.tube([(0, 0.8, 3.2), (0, 0.8, 4.0), (0, 0.5, 4.25), (0, 0.25, 4.0)], [0.08, 0.08, 0.08, 0.07], seg=6,
           color="chrome")
    for x in (-0.4, 0.4):
        m.cyl(r=0.1, h=0.2, seg=6, color="chrome", loc=(x, 0.85, 3.35))


@asset("Microwave", CAT, sub="Kitchen")
def microwave(m):
    m.box((2.2, 1.4, 1.3), color="plastic_white", bevel=0.1, loc=(0, 0, 0.65))
    m.box((1.4, 0.06, 0.9), color="screen", loc=(-0.3, -0.7, 0.65))
    m.box((0.45, 0.06, 1.0), color="plastic_black", loc=(0.75, -0.7, 0.65))
    m.box((0.3, 0.04, 0.14), color="neon_green", loc=(0.75, -0.74, 0.95))


@asset("Toaster", CAT, sub="Kitchen")
def toaster(m):
    m.box((1.4, 0.9, 1.0), color="chrome", bevel=0.25, bseg=3, loc=(0, 0, 0.5))
    for y in (-0.18, 0.18):
        m.box((1.0, 0.14, 0.05), color="charcoal", loc=(0, y, 1.0))
        m.box((0.8, 0.1, 0.3), color="bread", bevel=0.04, loc=(0, y, 1.08))
    m.box((0.12, 0.2, 0.1), color="plastic_black", loc=(0.72, 0, 0.7))


# --- bathroom -------------------------------------------------------------------------------
@asset("Toilet", CAT, sub="Bathroom")
def toilet(m):
    m.lathe([(0.5, 0), (0.55, 0.8), (0.9, 1.5), (0.95, 1.7), (0, 1.7)], seg=14, color="ceramic",
            scale=(1, 1.3, 1), loc=(0, -0.2, 0))
    m.torus(R=0.7, r=0.12, seg=14, rseg=5, color="plastic_white", loc=(0, -0.2, 1.78), scale=(1, 1.3, 1))
    m.box((1.9, 0.9, 1.8), color="ceramic", bevel=0.15, loc=(0, 1.05, 2.2))
    m.box((2.0, 1.0, 0.18), color="ceramic", bevel=0.06, loc=(0, 1.05, 3.15))
    m.box((0.3, 0.1, 0.1), color="chrome", loc=(-0.6, 0.56, 2.8))


@asset("Bathtub", CAT, sub="Bathroom")
def bathtub(m):
    m.box((6.4, 3.2, 2.2), color="ceramic", bevel=0.4, bseg=3, loc=(0, 0, 1.3))
    m.box((5.6, 2.4, 0.1), color="water", loc=(0, 0, 2.1))
    for x in (-2.8, 2.8):
        for y in (-1.2, 1.2):
            m.sphere(r=0.25, seg=8, rings=5, color="gold", loc=(x, y, 0.2))
    m.tube([(2.9, 0, 2.3), (2.9, 0, 3.0), (2.6, 0, 3.2)], [0.08, 0.08, 0.08], seg=6, color="chrome")
    for i in range(5):
        m.sphere(r=0.2 + (i % 2) * 0.08, seg=8, rings=5, color="white",
                 loc=(-1.5 + i * 0.6, (i % 3 - 1) * 0.5, 2.2))


@asset("BathroomSink", CAT, sub="Bathroom")
def bathroom_sink(m):
    m.cyl(r=0.3, r2=0.45, h=2.6, seg=10, color="ceramic", loc=(0, 0.2, 1.3))
    m.lathe([(0.3, 0), (1.1, 0.35), (1.2, 0.6), (1.0, 0.6), (0.35, 0.2), (0, 0.2)], seg=14, color="ceramic",
            loc=(0, 0, 2.5), scale=(1, 0.8, 1))
    m.tube([(0, 0.9, 3.0), (0, 0.9, 3.5), (0, 0.55, 3.55)], [0.07, 0.07, 0.06], seg=6, color="chrome")


@asset("Mirror", CAT, sub="Bathroom", origin="center")
def mirror(m):
    m.box((2.4, 0.2, 3.2), color="gold", bevel=0.08, loc=(0, 0, 0))
    m.box((2.0, 0.05, 2.8), color="glass", loc=(0, -0.1, 0))


# --- living & decor ------------------------------------------------------------------------------
@asset("TV", CAT, sub="Living")
def tv(m):
    m.box((5.4, 0.25, 3.1), color="plastic_black", bevel=0.08, loc=(0, 0, 2.1))
    m.box((5.0, 0.05, 2.7), color="screen", loc=(0, -0.13, 2.1))
    m.box((1.6, 0.8, 0.12), color="plastic_black", bevel=0.04, loc=(0, 0.1, 0.06))
    m.box((0.3, 0.2, 0.6), color="plastic_black", loc=(0, 0.1, 0.4))


@asset("TVStand", CAT, sub="Living")
def tv_stand(m):
    m.box((6.0, 1.8, 1.8), color="wood_dark", bevel=0.08, loc=(0, 0, 1.0))
    legs4(m, 6.0, 1.8, 0.12, r=0.1, color="charcoal", inset=0.25)
    for x in (-2.0, 0.0, 2.0):
        m.box((1.8, 0.1, 1.4), color="wood", bevel=0.04, loc=(x, -0.9, 1.0))
    m.box((1.2, 0.8, 0.35), color="plastic_black", bevel=0.05, loc=(0, 0, 2.08))


@asset("FloorLamp", CAT, sub="Lighting")
def floor_lamp(m):
    m.cyl(r=0.8, h=0.18, seg=14, color="charcoal", bevel=0.05, loc=(0, 0, 0.09))
    m.cyl(r=0.08, h=5.4, seg=8, color="charcoal", loc=(0, 0, 2.8))
    m.lathe([(0.7, 5.2), (1.1, 5.2), (0.75, 6.4), (0.4, 6.4)], seg=14, color="fabric_cream", caps=False)
    m.sphere(r=0.3, seg=8, rings=6, color="glow", loc=(0, 0, 5.6))


@asset("TableLamp", CAT, sub="Lighting")
def table_lamp(m):
    m.lathe([(0, 0), (0.45, 0), (0.5, 0.2), (0.35, 0.5), (0.48, 0.9), (0.2, 1.3), (0.08, 1.4), (0, 1.4)],
            seg=12, color="fabric_teal")
    m.lathe([(0.5, 1.4), (0.85, 1.4), (0.55, 2.4), (0.3, 2.4)], seg=12, color="fabric_cream", caps=False)
    m.sphere(r=0.2, seg=8, rings=6, color="glow", loc=(0, 0, 1.65))


@asset("CeilingLamp", CAT, sub="Lighting", origin=(0, 0, 2.0))
def ceiling_lamp(m):
    m.cyl(r=0.4, h=0.12, seg=12, color="charcoal", loc=(0, 0, 2.0))
    m.cyl(r=0.03, h=1.2, seg=5, color="charcoal", loc=(0, 0, 1.4))
    m.lathe([(0.15, 0.8), (1.0, 0.1), (1.0, 0.0), (0.9, 0.0), (0.12, 0.72)], seg=14, color="plastic_yellow",
            caps=False)
    m.sphere(r=0.22, seg=8, rings=6, color="glow", loc=(0, 0, 0.2))


@asset("Fireplace", CAT, sub="Living")
def fireplace(m):
    for x in (-2.1, 2.1):
        m.box((1.2, 1.6, 4.2), color="brick", bevel=0.06, loc=(x, 0, 2.1), cuts={"z": 0.5},
              deform=None)
    m.box((5.4, 1.6, 1.4), color="brick", bevel=0.06, loc=(0, 0, 4.9))
    m.box((6.0, 2.0, 0.35), color="wood_dark", bevel=0.08, loc=(0, -0.1, 5.75))
    m.box((3.0, 1.0, 4.2), color="coal", loc=(0, 0.3, 2.1))
    for i, x in enumerate((-0.6, 0.0, 0.6)):
        m.tube([(x - 0.5, -0.1, 0.25), (x + 0.5, 0.1, 0.25)], [0.14, 0.14], seg=6, color="wood_mid")
    m.cone(r=0.6, h=1.6, seg=7, color="fire", loc=(0, -0.1, 0.3), smooth=False)
    m.cone(r=0.35, h=1.0, seg=6, color="fire_light", loc=(0.1, -0.3, 0.3), smooth=False)
    m.box((6.4, 2.2, 0.4), color="stone", bevel=0.08, loc=(0, -0.2, 0.2))


@asset("Rug", CAT, sub="Living")
def rug(m):
    m.box((6.0, 4.0, 0.1), color="rug_red", bevel=0.04, loc=(0, 0, 0.05))
    m.box((5.0, 3.0, 0.02), color="fabric_yellow", loc=(0, 0, 0.1))
    m.box((4.6, 2.6, 0.03), color="rug_red", loc=(0, 0, 0.11))
    m.prism([(0, 0.8), (1.2, 0), (0, -0.8), (-1.2, 0)], depth=0.04, color="fabric_cream", loc=(0, 0, 0.13))


@asset("RoundRug", CAT, sub="Living")
def round_rug(m):
    for r, c, z in ((2.6, "rug_blue", 0.05), (2.0, "fabric_cream", 0.08), (1.4, "rug_blue", 0.1),
                    (0.7, "fabric_yellow", 0.12)):
        m.cyl(r=r, h=0.06, seg=20, color=c, loc=(0, 0, z - 0.02))


@asset("PottedPlant", CAT, sub="Decor")
def potted_plant(m):
    m.lathe([(0, 0), (0.55, 0), (0.75, 1.3), (0.85, 1.35), (0.85, 1.5), (0, 1.5)], seg=12,
            color=by_height("clay", 1.3, "brick"))
    m.cyl(r=0.72, h=0.05, seg=12, color="dirt", loc=(0, 0, 1.52))
    for i in range(8):
        a = i * 45 + (i % 2) * 20
        m.leaf(length=1.4 - (i % 2) * 0.3, width=0.55, thick=0.06, color="leaf" if i % 2 else "leaf_dark",
               loc=(0, 0, 1.5), rot=(52 + (i % 3) * 10, 0, a))


@asset("Monstera", CAT, sub="Decor")
def monstera(m):
    m.cyl(r=0.7, r2=0.8, h=1.2, seg=12, color="plastic_white", loc=(0, 0, 0.6), bevel=0.06)
    for i in range(6):
        a = i * 60
        L = 2.0 + (i % 3) * 0.3
        rad = math.radians(a)
        m.tube([(0, 0, 1.2), (math.cos(rad) * 0.5, math.sin(rad) * 0.5, 2.2 + (i % 2) * 0.4)], [0.05, 0.04],
               seg=5, color="leaf_dark")
        m.leaf(length=1.2, width=1.0, thick=0.06, color="leaf" if i % 2 else "leaf_dark",
               loc=(math.cos(rad) * 0.5, math.sin(rad) * 0.5, 2.2 + (i % 2) * 0.4), rot=(25, 0, a - 90))


@asset("CactusPot", CAT, sub="Decor")
def cactus_pot(m):
    m.cyl(r=0.45, r2=0.55, h=0.8, seg=10, color="plastic_pink", loc=(0, 0, 0.4), bevel=0.05)
    m.lathe([(0.3, 0.8), (0.36, 1.2), (0.36, 2.0), (0.25, 2.3), (0, 2.38)], seg=8, color="cactus", angle=50)
    m.tube([(0.3, 0, 1.4), (0.6, 0, 1.45), (0.62, 0, 1.9)], [0.14, 0.14, 0.12], seg=8, color="cactus")
    m.sphere(r=0.12, seg=8, rings=5, color="blossom", loc=(0, 0, 2.4))


@asset("WallClock", CAT, sub="Decor", origin="center")
def wall_clock(m):
    m.cyl(r=1.0, h=0.2, seg=20, color="wood_dark", bevel=0.06, rot=(90, 0, 0))
    m.cyl(r=0.85, h=0.05, seg=20, color="paper", rot=(90, 0, 0), loc=(0, -0.1, 0))
    for i in range(12):
        a = math.radians(30 * i)
        m.box((0.05, 0.03, 0.14 if i % 3 else 0.22), color="charcoal", rot=(0, -30 * i, 0),
              loc=(math.sin(a) * 0.7, -0.13, math.cos(a) * 0.7))
    m.box((0.06, 0.03, 0.5), color="charcoal", loc=(0.0, -0.15, 0.22))
    m.box((0.06, 0.03, 0.4), color="plastic_red", rot=(0, 60, 0), loc=(0.17, -0.16, -0.1))


@asset("GrandfatherClock", CAT, sub="Decor")
def grandfather_clock(m):
    m.box((1.8, 1.2, 6.0), color="wood_dark", bevel=0.08, loc=(0, 0, 3.2))
    m.box((2.0, 1.4, 0.3), color="wood_deep", bevel=0.06, loc=(0, 0, 0.15))
    m.box((2.0, 1.4, 0.4), color="wood_deep", bevel=0.06, loc=(0, 0, 6.3))
    m.cyl(r=0.7, h=0.1, seg=16, color="paper", rot=(90, 0, 0), loc=(0, -0.62, 5.2))
    m.torus(R=0.72, r=0.06, seg=16, rseg=4, color="gold", rot=(90, 0, 0), loc=(0, -0.64, 5.2))
    m.box((1.1, 0.06, 2.6), color="glass", loc=(0, -0.62, 2.6))
    m.cyl(r=0.03, h=1.6, seg=4, color="gold", loc=(0, -0.58, 3.0))
    m.cyl(r=0.28, h=0.08, seg=12, color="gold", rot=(90, 0, 0), loc=(0, -0.58, 2.2))


@asset("PictureFrame", CAT, sub="Decor", origin="center")
def picture_frame(m):
    m.box((2.6, 0.15, 2.0), color="gold", bevel=0.05, loc=(0, 0, 0))
    m.box((2.2, 0.05, 1.6), color=lambda c, n: "tile_blue" if c.z > 0.0 else "grass",
          loc=(0, -0.08, 0), cuts={"z": [0.0]})
    m.sphere(r=0.2, seg=8, rings=5, color="plastic_yellow", loc=(0.6, -0.1, 0.45), scale=(1, 0.2, 1))
    m.prism([(-0.9, 0), (-0.3, 0.55), (0.3, 0)], depth=0.04, color="stone_dark", rot=(90, 0, 0), loc=(0, -0.11, -0.05))


@asset("Piano", CAT, sub="Living")
def piano(m):
    m.box((5.0, 2.0, 4.0), color="plastic_black", bevel=0.1, loc=(0, 0.4, 2.2))
    m.box((5.0, 1.2, 0.4), color="plastic_black", bevel=0.06, loc=(0, -0.9, 2.6))
    m.box((4.6, 0.9, 0.1), color="plastic_white", loc=(0, -1.05, 2.85))
    for i in range(18):
        if i % 7 in (2, 6):
            continue
        m.box((0.12, 0.5, 0.1), color="plastic_black", loc=(-2.1 + i * 0.25, -0.8, 2.93))
    for x in (-2.2, 2.2):
        m.box((0.3, 0.3, 2.4), color="plastic_black", loc=(x, -1.2, 1.2))
    m.box((1.8, 0.8, 0.12), color="paper", loc=(0, -0.4, 3.6), rot=(-60, 0, 0))


@asset("Computer", CAT, sub="Living")
def computer(m):
    m.box((2.6, 0.2, 1.6), color="plastic_black", bevel=0.06, loc=(0, 0.3, 1.5))
    m.box((2.4, 0.05, 1.4), color="screen_glow", loc=(0, 0.18, 1.5))
    m.box((0.2, 0.2, 0.8), color="plastic_black", loc=(0, 0.45, 0.5))
    m.box((1.0, 0.7, 0.08), color="plastic_black", bevel=0.03, loc=(0, 0.45, 0.04))
    m.box((2.2, 0.8, 0.1), color="plastic_white", bevel=0.03, loc=(0, -0.7, 0.05))
    m.box((0.3, 0.45, 0.12), color="plastic_white", bevel=0.05, loc=(1.5, -0.7, 0.06))


@asset("ArcadeMachine", CAT, sub="Living")
def arcade_machine(m):
    m.box((2.4, 2.2, 5.6), color="plastic_purple", bevel=0.1, loc=(0, 0.2, 2.8))
    m.box((2.0, 0.1, 1.6), color="screen_glow", loc=(0, -0.9, 4.0), rot=(-10, 0, 0))
    m.box((2.4, 1.0, 0.8), color="plastic_purple", bevel=0.08, loc=(0, -1.0, 2.8), rot=(15, 0, 0))
    m.cyl(r=0.06, h=0.4, seg=6, color="charcoal", loc=(-0.5, -1.2, 3.35))
    m.sphere(r=0.15, seg=8, rings=5, color="plastic_red", loc=(-0.5, -1.2, 3.6))
    for x, c in ((0.2, "plastic_yellow"), (0.55, "plastic_green"), (0.9, "plastic_blue")):
        m.cyl(r=0.12, h=0.1, seg=8, color=c, loc=(x, -1.15, 3.2), rot=(15, 0, 0))
    m.box((2.4, 1.0, 0.8), color="neon_pink", bevel=0.08, loc=(0, 0.1, 5.4))


@asset("TrashCan", CAT, sub="Decor")
def trash_can(m):
    m.cyl(r=0.9, r2=1.0, h=2.4, seg=14, color="plastic_green", loc=(0, 0, 1.2), bevel=0.06, cuts={"z": [0.8, 1.6]},
          )
    m.cyl(r=1.08, h=0.2, seg=14, color="plastic_green", loc=(0, 0, 2.5), bevel=0.06)
    m.box((0.8, 0.2, 0.15), color="charcoal", bevel=0.05, loc=(0, 0, 2.68))


@asset("Door", CAT, sub="Building")
def door(m):
    m.box((4.0, 0.4, 7.4), color="wood_dark", loc=(0, 0, 3.7))
    m.box((3.4, 0.5, 7.0), color="wood", bevel=0.05, loc=(0, 0, 3.5))
    for z in (2.0, 5.0):
        m.box((2.6, 0.55, 2.2), color="wood_light", bevel=0.08, loc=(0, 0, z))
    m.sphere(r=0.16, seg=8, rings=6, color="gold", loc=(1.3, -0.35, 3.5))


@asset("Window", CAT, sub="Building", origin="center")
def window(m):
    m.box((4.0, 0.4, 4.0), color="plastic_white", loc=(0, 0, 0))
    m.box((3.5, 0.2, 3.5), color="glass", loc=(0, 0, 0))
    m.box((0.2, 0.45, 3.6), color="plastic_white", loc=(0, 0, 0))
    m.box((3.6, 0.45, 0.2), color="plastic_white", loc=(0, 0, 0))
    m.box((4.4, 0.8, 0.2), color="plastic_white", bevel=0.05, loc=(0, -0.2, -2.1))
    for x in (-1.5, 1.5):
        m.box((0.8, 0.25, 4.2), color="fabric_red", bevel=0.1, loc=(x * 1.35, -0.4, 0.05))


@asset("Crate", CAT, sub="Storage")
def crate(m):
    m.box((3.0, 3.0, 3.0), color="wood", bevel=0.06, loc=(0, 0, 1.5))
    for ax in range(3):
        for s in (-1, 1):
            if ax == 2:
                continue
            loc = [0, 0, 1.5]
            loc[ax] = s * 1.52
            size = [3.1, 3.1, 0.35]
            size[ax] = 0.1
            m.box(size, color="wood_dark", loc=(loc[0], loc[1], 1.5 + 1.35), bevel=0.02, bseg=1)
            m.box(size, color="wood_dark", loc=(loc[0], loc[1], 1.5 - 1.35), bevel=0.02, bseg=1)
    for s in (-1, 1):
        m.box((0.3, 0.1, 3.9), color="wood_dark", rot=(0, 45, 0), loc=(0, s * 1.53, 1.5))
        m.box((0.1, 0.3, 3.9), color="wood_dark", rot=(45, 0, 0), loc=(s * 1.53, 0, 1.5))


@asset("Barrel", CAT, sub="Storage")
def barrel(m):
    m.lathe([(0, 0), (1.0, 0), (1.2, 0.8), (1.25, 1.5), (1.2, 2.2), (1.0, 3.0), (0, 3.0)], seg=14,
            color="wood")
    for z, r in ((0.35, 1.07), (1.0, 1.23), (2.0, 1.23), (2.65, 1.07)):
        m.torus(R=r, r=0.06, seg=14, rseg=4, color="iron_dark", loc=(0, 0, z))


@asset("TreasureChest", CAT, sub="Storage")
def treasure_chest(m):
    m.box((3.0, 2.0, 1.6), color="wood_mid", bevel=0.06, loc=(0, 0, 0.8))
    m.cyl(r=1.0, h=3.0, seg=12, color="wood_mid", rot=(0, 90, 0), loc=(0, 0, 1.6),
          deform=lambda co: co.__class__((min(co.x, 0.02), co.y, co.z)))
    for x in (-1.2, 0, 1.2):
        m.box((0.25, 2.08, 1.62), color="gold", loc=(x, 0, 0.8))
        m.torus(R=1.02, r=0.1, seg=12, rseg=4, arc=180, color="gold", rot=(90, 0, 90), loc=(x, 0, 1.6))
    m.box((0.5, 0.2, 0.6), color="gold", bevel=0.05, loc=(0, -1.05, 1.5))
    m.cyl(r=0.08, h=0.1, seg=6, color="charcoal", rot=(90, 0, 0), loc=(0, -1.16, 1.45))
