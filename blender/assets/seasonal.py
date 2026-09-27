"""Holidays: seasonal decorations and props for every event of the year -
New Year, Lunar New Year, Valentine's, St Patrick's, Easter, birthdays & fiestas,
4th of July, summer, Halloween, harvest, Christmas, Hanukkah, Diwali, Kwanzaa,
Day of the Dead and winter.

Same blocky stud style; buildings (haunted house, gingerbread house, Santa's
workshop) are split into parts like the rest of the library. Everything faces -Y.
"""
import math
import random

from studlib.font import text, text_width
from studlib.geo import by_normal, heart_pts, star_pts
from studlib.registry import add

from commercial import FL, blk, sign, storefront, counter, pendant

CAT = "Holidays"


def reg(name, fn, sub, split=False, origin="bottom", tags=()):
    add(name, CAT, fn, sub=sub, split=split, origin=origin, tags=list(tags) + ["holiday", sub.lower()])


def banner(m, s, col="white", board="plastic_red", px=0.3, poles=True, h=None):
    """Hanging banner with pixel lettering between two poles."""
    w = text_width(s, px) + 1.6
    hh = h or 5 * px + 1.0
    z = 7.0
    blk(m, (w, 0.15, hh), (0, 0, z), board, bev=0.05)
    text(m, s, 0, -0.08, z, px=px, depth=0.06, col=col)
    for k in range(int(w / 1.2)):
        x = -w / 2 + 0.6 + k * 1.2
        m.prism([(-0.45, 0), (0.45, 0), (0, -0.8)], depth=0.05, color=["plastic_yellow", "plastic_blue", "plastic_green"][k % 3],
                rot=(90, 0, 0), loc=(x, 0, z - hh / 2))
    if poles:
        for s_ in (-1, 1):
            m.cyl(r=0.15, h=z + hh / 2 + 0.5, seg=6, color="wood_mid", loc=(s_ * (w / 2 + 0.2), 0, (z + hh / 2 + 0.5) / 2))
            blk(m, (0.6, 0.6, 0.3), (s_ * (w / 2 + 0.2), 0, 0.15), "wood_dark")


def bunting(m, L=12.0, cols=("plastic_red", "white", "plastic_blue"), z=6.0, sag=0.8):
    m.tube([(-L / 2, 0, z), (0, 0, z - sag), (L / 2, 0, z)], [0.04] * 3, seg=4, color="string")
    n = int(L / 1.0)
    for k in range(n):
        x = -L / 2 + 0.5 + k * L / n
        zz = z - sag * (1 - (2 * x / L) ** 2) - 0.05
        m.prism([(-0.4, 0), (0.4, 0), (0, -0.8)], depth=0.05, color=cols[k % len(cols)], rot=(90, 0, 0), loc=(x, 0, zz))
    for s in (-1, 1):
        m.cyl(r=0.12, h=z + 0.3, seg=6, color="wood_mid", loc=(s * L / 2, 0, (z + 0.3) / 2))


def balloon(m, x, y, z, col, r=0.8):
    m.lathe([(0, 0), (0.1, 0.05), (r * 0.8, r * 0.6), (r, r * 1.3), (r * 0.8, r * 2.0), (0, r * 2.3)], seg=8,
            color=col, loc=(x, y, z))
    m.cone(r=0.12, h=0.15, seg=6, color=col, loc=(x, y, z - 0.12))


def string_to(m, a, b):
    m.tube([a, ((a[0] + b[0]) / 2 + 0.1, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2), b], [0.02] * 3, seg=3, color="string",
           smooth=False)


# ----------------------------------------------------------------------------
# New Year
# ----------------------------------------------------------------------------
def party_hat(m, col="plastic_purple", dots="plastic_yellow"):
    m.cone(r=0.8, h=2.2, seg=8, color=lambda c, n: dots if int((c.z + 0.2) / 0.4) % 2 else col, cuts={"z": 0.4})
    blk(m, (0.4, 0.4, 0.4), (0, 0, 2.3), "white", bev=0.12)
    m.torus(R=0.8, r=0.1, seg=8, color="gold", loc=(0, 0, 0.1))


def sparkling_cider(m):
    m.lathe([(1.2, 0), (1.3, 1.6), (1.4, 1.8), (0, 1.8)], seg=8, color="stainless", caps=True)
    for i in range(6):
        a = math.radians(60 * i)
        blk(m, (0.35, 0.35, 0.35), (0.7 * math.cos(a), 0.7 * math.sin(a), 1.75), "ice", bev=0.06)
    with m.at((0, 0, 1.0), 0):
        m.lathe([(0.45, 0), (0.45, 1.8), (0.2, 2.6), (0.16, 3.2), (0, 3.2)], seg=8,
                color=lambda c, n: "gold" if c.z > 2.3 else "leaf_deep", cuts={"z": [2.3]})
        blk(m, (0.5, 0.1, 0.6), (0, -0.46, 1.0), "gold")
    for x in (-1.8, 1.8):
        m.lathe([(0.5, 0), (0.5, 0.1), (0.08, 0.2), (0.08, 1.2), (0.45, 1.4), (0.5, 2.2), (0, 2.2)], seg=6,
                color=lambda c, n: "potion_yellow" if 1.5 < c.z < 2.0 else "glass", loc=(x, -0.5, 0), cuts={"z": [1.5, 2.0]})


def countdown_clock(m):
    blk(m, (7.0, 1.0, 3.6), (0, 0, 9.0), "charcoal", bev=0.15)
    text(m, "1159", 0, -0.52, 9.0, px=0.45, depth=0.1, col="neon_red")
    blk(m, (0.25, 0.1, 0.25), (0, -0.52, 9.35), "neon_red")
    blk(m, (0.25, 0.1, 0.25), (0, -0.52, 8.65), "neon_red")
    blk(m, (1.2, 1.2, 7.2), (0, 0, 3.6), "charcoal", bev=0.1)
    m.cyl(r=2.0, h=0.5, seg=8, color="charcoal", loc=(0, 0, 0.25))
    m.lathe([(0, 0), (1.2, 0.1), (1.2, 0.3), (0, 0.4)], seg=8, color="gold", loc=(0, 0, 10.8))
    m.ico(r=0.9, sub=1, color="glow", loc=(0, 0, 12.0), smooth=False)


def disco_ball(m):
    blk(m, (0.1, 0.1, 3.0), (0, 0, 4.5), "chrome")
    m.sphere(r=1.3, seg=10, rings=8, round=True, color=lambda c, n: "chrome" if (int((c.x + 5) * 2) + int((c.z + 5) * 2)) % 2
             else "silver", loc=(0, 0, 1.6), cuts={"x": 0.5, "z": 0.5})


def confetti_cannon(m):
    m.cyl(r=0.6, h=2.6, seg=8, color=lambda c, n: "gold" if int(c.z / 0.5) % 2 else "plastic_purple", rot=(-60, 0, 0),
          loc=(0, 0, 1.4), cuts={"z": 0.5})
    rnd = random.Random(3)
    for i in range(18):
        blk(m, (0.2, 0.05, 0.2), (rnd.uniform(-1.2, 1.2), rnd.uniform(-3.2, -1.2), rnd.uniform(2.4, 4.6)),
            rnd.choice(["plastic_red", "plastic_yellow", "plastic_blue", "neon_green", "plastic_pink"]),
            rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), 0))
    blk(m, (1.6, 1.6, 0.5), (0, 0.4, 0.25), "charcoal", bev=0.08)


def balloon_arch(m, cols=("plastic_pink", "white", "gold", "plastic_purple")):
    for i in range(15):
        a = math.radians(180 * i / 14)
        balloon(m, 5.0 * math.cos(a), 0, 5.0 * math.sin(a) + 0.2, cols[i % len(cols)], r=0.7)
    for s in (-1, 1):
        blk(m, (1.2, 1.2, 0.5), (s * 5.0, 0, 0.25), "charcoal", bev=0.1)


def firework_launcher(m):
    blk(m, (3.0, 3.0, 1.4), (0, 0, 0.7), "plastic_red", bev=0.1)
    for i in range(3):
        for j in range(3):
            x, y = -0.9 + i * 0.9, -0.9 + j * 0.9
            m.cyl(r=0.35, h=1.2 + ((i + j) % 3) * 0.4, seg=6, color=["plastic_blue", "plastic_yellow", "neon_green"][(i + j) % 3],
                  loc=(x, y, 1.4 + 0.6 + ((i + j) % 3) * 0.2))
    text(m, "BOOM", 0, -1.52, 0.7, px=0.14, depth=0.05, col="plastic_yellow")


reg("PartyHat", lambda m: party_hat(m), "NewYear")
reg("SparklingCider", sparkling_cider, "NewYear")
reg("CountdownClock", countdown_clock, "NewYear")
reg("DiscoBall", disco_ball, "NewYear")
reg("ConfettiCannon", confetti_cannon, "NewYear")
reg("BalloonArch", lambda m: balloon_arch(m), "NewYear")
reg("NewYearBanner", lambda m: banner(m, "HAPPY NEW YEAR", "gold", "black", px=0.25), "NewYear")
reg("FireworkLauncher", firework_launcher, "NewYear")


# ----------------------------------------------------------------------------
# Lunar New Year
# ----------------------------------------------------------------------------
def red_lantern(m, z=0.0, r=1.0):
    with m.at((0, 0, z)):
        m.lathe([(0.5 * r, 0), (0.95 * r, 0.4 * r), (1.0 * r, 1.0 * r), (0.95 * r, 1.6 * r), (0.5 * r, 2.0 * r)], seg=8,
                color=lambda c, n: "gold" if abs(c.z - r) < 0.12 else "wall_red", cuts={"z": [r - 0.12, r + 0.12]})
        m.cyl(r=0.5 * r, h=0.25, seg=8, color="gold", loc=(0, 0, 2.05 * r))
        m.cyl(r=0.5 * r, h=0.25, seg=8, color="gold", loc=(0, 0, -0.05))
        for k in range(5):
            blk(m, (0.06, 0.06, 0.8 * r), (-0.2 + k * 0.1, 0, -0.5 * r), "gold")


def lantern_string(m, L=12.0, n=5):
    m.tube([(-L / 2, 0, 8.0), (0, 0, 7.2), (L / 2, 0, 8.0)], [0.04] * 3, seg=4, color="string")
    for k in range(n):
        x = -L / 2 + L * (k + 0.5) / n
        zz = 8.0 - 0.8 * (1 - (2 * x / L) ** 2)
        blk(m, (0.05, 0.05, 0.6), (x, 0, zz - 0.3), "string")
        with m.at((x, 0, zz - 2.6)):
            red_lantern(m, 0, 1.0)
    for s in (-1, 1):
        m.cyl(r=0.15, h=8.3, seg=6, color="wall_red", loc=(s * L / 2, 0, 4.15))


def dragon_head(m):
    blk(m, (3.0, 3.6, 2.4), (0, 0, 2.2), "wall_red", bev=0.3)
    blk(m, (2.4, 1.8, 1.0), (0, -2.2, 1.6), "wall_red", bev=0.2)
    blk(m, (2.6, 1.8, 0.5), (0, -2.0, 0.85), "gold", bev=0.1)
    for x in (-0.8, 0.8):
        blk(m, (0.9, 0.3, 0.9), (x, -1.8, 3.1), "white", bev=0.1)
        blk(m, (0.4, 0.1, 0.4), (x, -1.96, 3.1), "black")
        m.cone(r=0.25, h=1.6, seg=6, color="gold", rot=(-30, x * 15, 0), loc=(x * 0.8, 0.8, 3.4))
    for i in range(6):
        blk(m, (0.5, 0.4, 0.8), (0, -1.2 + i * 0.6, 3.6), "gold", bev=0.1)
    for s in (-1, 1):
        m.tube([(s * 1.1, -3.0, 1.6), (s * 2.2, -3.6, 2.4), (s * 2.8, -3.2, 3.2)], [0.1, 0.08, 0.04], seg=4, color="gold")
    for i in range(5):
        blk(m, (3.4, 0.6, 1.8), (0, 2.4 + i * 0.6, 1.4), "gold" if i % 2 else "wall_red", bev=0.1)


def firecrackers(m):
    blk(m, (0.1, 0.1, 1.0), (0, 0, 6.5), "string")
    for k in range(12):
        z = 5.8 - k * 0.45
        for s in (-1, 1):
            m.cyl(r=0.12, h=0.6, seg=6, color="wall_red", rot=(0, s * 60, 0), loc=(s * 0.28, 0, z))
    blk(m, (0.08, 0.08, 5.6), (0, 0, 3.2), "gold")
    blk(m, (0.6, 0.3, 0.6), (0, 0, 0.7), "gold", bev=0.1)


def red_envelope(m):
    blk(m, (1.4, 0.2, 2.2), (0, 0, 1.1), "wall_red", bev=0.05)
    m.prism([(-0.7, 0), (0.7, 0), (0, -0.6)], depth=0.05, color="brick_dark", rot=(90, 0, 0), loc=(0, -0.12, 2.2))
    m.cyl(r=0.3, h=0.06, seg=8, color="gold", rot=(90, 0, 0), loc=(0, -0.13, 1.5))


def lucky_cat(m):
    blk(m, (2.0, 1.6, 2.2), (0, 0, 1.1), "white", bev=0.3)
    blk(m, (2.2, 1.8, 1.8), (0, -0.1, 2.9), "white", bev=0.35)
    for s in (-1, 1):
        m.pyramid(w=0.6, h=0.7, color="white", loc=(s * 0.7, -0.1, 3.7))
        blk(m, (0.3, 0.1, 0.1), (s * 0.45, -1.02, 3.1), "black")
        blk(m, (0.3, 0.1, 0.4), (s * 0.9, -0.9, 2.7), "pink_inner")
    blk(m, (0.5, 0.5, 1.4), (1.1, -0.3, 3.2), "white", bev=0.15)      # raised paw
    blk(m, (1.6, 0.2, 0.3), (0, -0.92, 2.1), "wall_red")
    m.cyl(r=0.3, h=0.1, seg=8, color="gold", rot=(90, 0, 0), loc=(0, -1.0, 1.85))
    blk(m, (1.0, 0.4, 1.2), (-0.6, -0.8, 1.0), "gold", bev=0.1)
    blk(m, (0.2, 0.1, 0.2), (0, -1.02, 2.8), "pink_nose")


def orange_bowl(m):
    m.lathe([(0, 0), (1.2, 0.1), (1.8, 0.8), (1.7, 0.9), (0, 0.4)], seg=8, color="ceramic")
    for i, (x, y, z) in enumerate(((0, 0, 0.9), (0.8, 0.3, 0.8), (-0.7, 0.4, 0.8), (0.2, -0.8, 0.8), (0.1, 0.2, 1.6))):
        m.sphere(r=0.5, seg=8, rings=6, round=True, color="orange", loc=(x, y, z + 0.3))
        m.leaf(length=0.4, width=0.2, thick=0.04, color="leaf", loc=(x, y, z + 0.8), rot=(20, 0, 40 * i))


def lunar_gate(m):
    for s in (-1, 1):
        m.cyl(r=0.8, h=12.0, seg=8, color="wall_red", loc=(s * 7.0, 0, 6.0))
        blk(m, (2.2, 2.2, 0.8), (s * 7.0, 0, 0.4), "stone", bev=0.1)
    m.box((18.0, 2.0, 1.0), color="wall_red", loc=(0, 0, 10.0), bevel=0.1)
    m.box((20.0, 2.6, 1.0), color="black", loc=(0, 0, 12.3), bevel=0.1,
          deform=lambda co: co.__class__((co.x, co.y, co.z + 0.02 * co.x * co.x)))
    blk(m, (4.0, 0.3, 2.0), (0, -1.1, 11.1), "gold", bev=0.05)
    blk(m, (3.4, 0.1, 1.4), (0, -1.28, 11.1), "wall_red")
    for x in (-4.5, 4.5):
        with m.at((x, 0, 6.4)):
            red_lantern(m, 0, 0.9)
        blk(m, (0.05, 0.05, 1.8), (x, 0, 9.0), "string")


reg("RedLantern", lambda m: red_lantern(m), "LunarNewYear")
reg("LanternString", lambda m: lantern_string(m), "LunarNewYear")
reg("DragonDanceHead", dragon_head, "LunarNewYear")
reg("Firecrackers", firecrackers, "LunarNewYear")
reg("RedEnvelope", red_envelope, "LunarNewYear")
reg("LuckyCat", lucky_cat, "LunarNewYear")
reg("MandarinBowl", orange_bowl, "LunarNewYear")
reg("LunarGate", lunar_gate, "LunarNewYear")


# ----------------------------------------------------------------------------
# Valentine's Day
# ----------------------------------------------------------------------------
def heart(m, s=1.0, col="apple_red", depth=0.6, loc=(0, 0, 0), rot=(90, 0, 0)):
    m.prism(heart_pts(s, 16), depth=depth, color=col, rot=rot, loc=loc, bevel=0.08 * s)


def heart_balloon(m, col="apple_red"):
    heart(m, 1.6, col, 0.9, loc=(0, 0, 5.5))
    string_to(m, (0, 0, 4.2), (0.2, 0, 0.2))
    blk(m, (0.8, 0.8, 0.4), (0.2, 0, 0.2), "gold", bev=0.1)


def chocolate_box(m):
    heart(m, 2.0, "velvet", 0.6, loc=(0, 0, 0.3), rot=(0, 0, 180))
    heart(m, 2.1, "wall_red", 0.2, loc=(0.2, 0.8, 1.5), rot=(-60, 0, 180))
    for x, y in ((-0.9, -0.4), (0.0, -0.9), (0.9, -0.4), (-0.4, 0.4), (0.5, 0.4), (0.0, -0.1)):
        blk(m, (0.55, 0.55, 0.3), (x, y - 0.4, 0.7), "chocolate", bev=0.12)
    m.box((0.4, 3.6, 0.1), color="gold", loc=(0.2, 0.2, 1.5), rot=(-60, 0, 0))


def rose_bouquet(m):
    m.cone(r=1.4, h=3.2, seg=8, color="paper", rot=(180, 0, 0), loc=(0, 0, 3.4))
    blk(m, (1.0, 0.3, 0.6), (0, -0.7, 1.2), "fabric_red", bev=0.1)
    rnd = random.Random(8)
    for i in range(7):
        a = math.radians(360 * i / 7)
        x, y = 0.8 * math.cos(a) * (i > 0), 0.8 * math.sin(a) * (i > 0)
        z = 3.8 + rnd.uniform(-0.2, 0.3)
        blk(m, (0.7, 0.7, 0.6), (x, y, z), "apple_red", bev=0.18)
        blk(m, (0.4, 0.4, 0.2), (x, y, z + 0.35), "apple_red_dark")
        m.leaf(length=0.6, width=0.25, thick=0.04, color="leaf", loc=(x, y, z - 0.4), rot=(60, 0, 50 * i))


def teddy_bear(m, col="fur_brown", heart_col="apple_red"):
    blk(m, (2.2, 1.8, 2.4), (0, 0, 1.4), col, bev=0.4)
    blk(m, (2.0, 1.8, 1.8), (0, -0.1, 3.3), col, bev=0.4)
    for s in (-1, 1):
        blk(m, (0.7, 0.5, 0.7), (s * 0.8, 0.1, 4.2), col, bev=0.2)
        blk(m, (0.8, 1.2, 0.8), (s * 0.8, -0.6, 0.4), col, bev=0.25)
        blk(m, (0.7, 0.8, 1.4), (s * 1.3, -0.3, 1.8), col, bev=0.2, rot=(0, s * -20, 0))
        blk(m, (0.2, 0.1, 0.2), (s * 0.4, -1.02, 3.5), "eye_black")
    blk(m, (0.8, 0.5, 0.6), (0, -1.0, 3.0), "fur_tan", bev=0.15)
    blk(m, (0.3, 0.1, 0.2), (0, -1.27, 3.2), "black")
    heart(m, 0.7, heart_col, 0.3, loc=(0, -1.0, 1.4))


def love_letter(m):
    blk(m, (2.4, 0.15, 1.6), (0, 0, 0.8), "paper", bev=0.03)
    m.prism([(-1.2, 0), (1.2, 0), (0, -0.9)], depth=0.05, color="offwhite", rot=(90, 0, 0), loc=(0, -0.1, 1.6))
    heart(m, 0.35, "apple_red", 0.1, loc=(0, -0.15, 0.95))


def cupid_bow(m):
    pts = [(0, -0.5 * math.cos(math.pi * (t / 10 - 0.5)), -2.0 + 4.0 * t / 10) for t in range(11)]
    m.tube(pts, [0.08] * 11, seg=4, up=(1, 0, 0), color="gold")
    m.tube([(0, pts[0][1] + 0.02, -2.0), (0, pts[0][1] + 0.02, 2.0)], [0.02, 0.02], seg=3, color="white", smooth=False)
    m.cyl(r=0.04, h=3.6, seg=4, color="wood_light", rot=(90, 0, 0), loc=(0, -0.9, 0))
    heart(m, 0.35, "apple_red", 0.1, loc=(0, -2.8, 0), rot=(0, 0, 0))
    for s in (-1, 1):
        m.prism([(0, 0), (0.3, 0.4), (0, 0.3)], depth=0.04, color="white", rot=(90, 0, 90 + s * 90), loc=(0, 0.8, 0))


def heart_arch(m):
    for i in range(13):
        a = math.radians(180 * i / 12)
        heart(m, 0.7, ["apple_red", "plastic_pink", "white"][i % 3], 0.4,
              loc=(4.5 * math.cos(a), 0, 4.5 * math.sin(a) + 0.8))
    for s in (-1, 1):
        blk(m, (1.2, 1.2, 1.0), (s * 4.5, 0, 0.5), "white", bev=0.15)
        m.cyl(r=0.2, h=1.2, seg=6, color="leaf_dark", loc=(s * 4.5, 0, 1.4))


def love_bench(m):
    for s in (-1, 1):
        blk(m, (0.4, 1.6, 1.8), (s * 2.6, 0, 0.9), "iron_dark", bev=0.05)
    blk(m, (5.6, 1.8, 0.3), (0, 0, 1.9), "wood_light", bev=0.05)
    heart(m, 1.6, "apple_red", 0.3, loc=(0, 0.8, 2.2))


reg("HeartBalloon", lambda m: heart_balloon(m), "Valentines")
reg("PinkHeartBalloon", lambda m: heart_balloon(m, "plastic_pink"), "Valentines")
reg("HeartChocolateBox", chocolate_box, "Valentines")
reg("RoseBouquet", rose_bouquet, "Valentines")
reg("TeddyBear", lambda m: teddy_bear(m), "Valentines")
reg("LoveLetter", love_letter, "Valentines")
reg("CupidBow", cupid_bow, "Valentines", origin="center")
reg("HeartArch", heart_arch, "Valentines")
reg("LoveBench", love_bench, "Valentines")


# ----------------------------------------------------------------------------
# St Patrick's Day
# ----------------------------------------------------------------------------
def shamrock(m, s=1.0, col="leaf", loc=(0, 0, 0), rot=(90, 0, 0), four=False):
    with m.at(loc):
        for k in range(4 if four else 3):
            a = (90 * k + 45) if four else (120 * k + 90)
            r = math.radians(a)
            heart(m, 0.6 * s, col, 0.2 * s, loc=(0.55 * s * math.cos(r), 0, 0.55 * s * math.sin(r)),
                  rot=(90, a - 90, 0))
        blk(m, (0.15 * s, 0.15 * s, 1.0 * s), (0.2 * s, 0, -0.9 * s), col)


def pot_of_gold(m):
    m.lathe([(1.2, 0), (1.7, 0.6), (1.9, 1.4), (1.6, 2.2), (1.7, 2.4), (0, 2.4)], seg=8, color="iron_dark")
    m.lathe([(0, 2.3), (1.6, 2.3), (1.3, 2.8), (0.6, 3.2), (0, 3.3)], seg=8, color="gold")
    for i in range(8):
        a = math.radians(45 * i)
        m.cyl(r=0.35, h=0.12, seg=8, color="gold_light", loc=(1.2 * math.cos(a), 1.2 * math.sin(a), 3.0),
              rot=(20, 10, 0))
    for i, c in enumerate(("rb_red", "rb_orange", "rb_yellow", "rb_green", "rb_blue", "rb_purple")):
        m.torus(R=5.0 - i * 0.45, r=0.22, seg=12, color=c, arc=90, rot=(90, 0, 180), loc=(4.8, 0.8, 2.4))


def leprechaun_hat(m):
    m.cyl(r=1.6, h=0.2, seg=8, color="leaf_deep", loc=(0, 0, 0.1))
    m.cyl(r=1.0, r2=1.15, h=2.0, seg=8, color="leaf_deep", loc=(0, 0, 1.2))
    m.cyl(r=1.02, h=0.4, seg=8, color="black", loc=(0, 0, 0.5))
    blk(m, (0.6, 0.2, 0.5), (0, -1.0, 0.5), "gold", bev=0.05)
    blk(m, (0.3, 0.25, 0.25), (0, -1.05, 0.5), "black")
    shamrock(m, 0.5, "leaf_light", loc=(0.8, -0.7, 1.6), rot=(90, 0, 0))


def horseshoe(m):
    m.torus(R=1.0, r=0.2, seg=10, rseg=4, arc=240, color="gold", rot=(90, 0, -30 + 90), loc=(0, 0, 1.2))
    for i in range(5):
        a = math.radians(-30 + i * 60)
        blk(m, (0.12, 0.3, 0.12), (1.0 * math.cos(a + math.pi / 2), -0.1, 1.2 + 1.0 * math.sin(a + math.pi / 2)), "black")


def giant_shamrock(m):
    shamrock(m, 2.0, "leaf", loc=(0, 0, 3.2), four=True)
    blk(m, (2.0, 2.0, 0.5), (0.4, 0, 0.25), "wood_mid", bev=0.1)


def shamrock_garland(m, L=10.0):
    m.tube([(-L / 2, 0, 5.0), (0, 0, 4.2), (L / 2, 0, 5.0)], [0.05] * 3, seg=4, color="leaf_dark")
    for k in range(7):
        x = -L / 2 + L * (k + 0.5) / 7
        z = 5.0 - 0.8 * (1 - (2 * x / L) ** 2) - 0.6
        shamrock(m, 0.5, "leaf" if k % 2 else "leaf_light", loc=(x, 0, z))
    for s in (-1, 1):
        m.cyl(r=0.12, h=5.3, seg=6, color="wood_mid", loc=(s * L / 2, 0, 2.65))


reg("PotOfGold", pot_of_gold, "StPatricks")
reg("LeprechaunHat", leprechaun_hat, "StPatricks")
reg("LuckyHorseshoe", horseshoe, "StPatricks")
reg("GiantShamrock", giant_shamrock, "StPatricks")
reg("ShamrockGarland", lambda m: shamrock_garland(m), "StPatricks")


# ----------------------------------------------------------------------------
# Easter & spring
# ----------------------------------------------------------------------------
EGG = [(0, 0), (0.55, 0.08), (0.85, 0.5), (0.95, 1.0), (0.85, 1.5), (0.6, 1.95), (0.3, 2.2), (0, 2.3)]


def painted_egg(m, base, a, style="stripes", loc=(0, 0, 0), s=1.0):
    def col(c, n):
        z = (c.z - loc[2]) / s
        if style == "stripes":
            return a if int(z / 0.45) % 2 else base
        if style == "zigzag":
            return a if 0.9 < z + 0.15 * math.sin(math.atan2(c.y - loc[1], c.x - loc[0]) * 4) < 1.4 else base
        if style == "dots":
            ang = math.degrees(math.atan2(c.y - loc[1], c.x - loc[0])) % 90
            return a if (30 < ang < 60 and 0.5 < z < 1.8 and int(z / 0.6) % 2 == 0) else base
        return base
    m.lathe([(r * s, z * s) for r, z in EGG], seg=8, color=col, loc=loc, cuts={"z": [loc[2] + k * 0.15 * s for k in range(1, 15)]})
    if style == "dots":
        for k in range(10):
            ang = math.radians(36 * k + (18 if k % 2 else 0))
            z = (0.7 if k % 2 else 1.4)
            rr = 0.93 * s
            m.box((0.28 * s, 0.28 * s, 0.28 * s), color=a, bevel=0.06 * s,
                  loc=(loc[0] + rr * math.cos(ang), loc[1] + rr * math.sin(ang), loc[2] + z * s))


def egg_basket(m):
    m.lathe([(1.4, 0), (1.8, 0.3), (2.2, 1.4), (2.1, 1.5), (0, 0.2)], seg=8,
            color=lambda c, n: "wood_light" if int(c.z / 0.3) % 2 else "wood_mid", cuts={"z": 0.3})
    m.torus(R=2.0, r=0.12, seg=8, arc=180, color="wood_mid", rot=(90, 0, 0), loc=(0, 0, 1.4))
    blk(m, (3.6, 3.6, 0.2), (0, 0, 1.3), "grass")
    for i, (b, a, st) in enumerate((("plastic_pink", "white", "stripes"), ("candy_blue", "lemon", "zigzag"),
                                    ("lemon", "plastic_purple", "dots"), ("icecream_mint", "plastic_pink", "stripes"))):
        ang = math.radians(90 * i + 20)
        painted_egg(m, b, a, st, loc=(0.9 * math.cos(ang), 0.9 * math.sin(ang), 1.2), s=0.55)


def bunny_statue(m, col="white"):
    blk(m, (2.4, 3.0, 2.2), (0, 0.3, 1.1), col, bev=0.45)
    blk(m, (1.8, 1.8, 1.7), (0, -1.3, 2.4), col, bev=0.4)
    for s in (-1, 1):
        blk(m, (0.5, 0.35, 2.0), (s * 0.45, -1.1, 4.1), col, bev=0.15, rot=(0, s * -10, 0))
        blk(m, (0.3, 0.1, 1.5), (s * 0.45, -1.3, 4.1), "pink_inner", rot=(0, s * -10, 0))
        blk(m, (0.2, 0.1, 0.2), (s * 0.4, -2.22, 2.6), "eye_black")
        blk(m, (0.6, 1.0, 0.5), (s * 0.7, -1.2, 0.25), col, bev=0.15)
    blk(m, (0.25, 0.1, 0.18), (0, -2.23, 2.2), "pink_nose")
    blk(m, (0.8, 0.8, 0.8), (0, 1.9, 1.0), "white", bev=0.3)


def chocolate_bunny(m):
    bunny_statue(m, "chocolate")
    blk(m, (2.0, 0.2, 0.6), (0, -1.9, 1.0), "gold", bev=0.05)


def egg_hunt_sign(m):
    blk(m, (0.5, 0.5, 4.0), (0, 0.2, 2.0), "wood_mid")
    blk(m, (5.0, 0.3, 1.6), (0, 0, 4.2), "wood_light", bev=0.1)
    text(m, "EGG HUNT", 0, -0.16, 4.2, px=0.15, depth=0.05, col="plastic_pink")
    painted_egg(m, "plastic_pink", "white", "stripes", loc=(1.8, -0.5, 0.0), s=0.5)
    painted_egg(m, "candy_blue", "lemon", "zigzag", loc=(-1.4, -0.8, 0.0), s=0.45)


def flower_cart(m):
    blk(m, (5.0, 3.0, 1.6), (0, 0, 1.6), "wood_mid", bev=0.1)
    for s in (-1, 1):
        m.cyl(r=1.0, h=0.3, seg=8, color="wood_dark", rot=(0, 90, 0), loc=(s * 2.6, 0.6, 1.0))
    m.tube([(2.5, -1.2, 2.0), (4.0, -1.8, 1.8)], [0.1, 0.1], seg=4, color="wood_dark")
    rnd = random.Random(5)
    for i in range(12):
        x, y = -2.0 + (i % 6) * 0.8, -0.8 + (i // 6) * 1.4
        m.cyl(r=0.05, h=0.8, seg=4, color="leaf_dark", loc=(x, y, 2.8))
        blk(m, (0.5, 0.5, 0.4), (x, y, 3.3), rnd.choice(["plastic_pink", "plastic_yellow", "plastic_red", "white",
                                                        "plastic_purple"]), bev=0.12)
    for x in (-2.4, 2.4):
        blk(m, (0.15, 0.15, 3.0), (x, 1.4, 3.8), "wood_dark")
    m.box((5.4, 3.4, 0.2), color=lambda c, n: "awning_green" if int((c.x + 10) / 0.9) % 2 else "white",
          loc=(0, 0.2, 5.4), cuts={"x": 0.9}, rot=(-10, 0, 0))


reg("EggBasket", egg_basket, "Easter")
reg("StripedEasterEgg", lambda m: painted_egg(m, "plastic_pink", "white", "stripes"), "Easter")
reg("ZigzagEasterEgg", lambda m: painted_egg(m, "candy_blue", "lemon", "zigzag"), "Easter")
reg("DottedEasterEgg", lambda m: painted_egg(m, "lemon", "plastic_purple", "dots"), "Easter")
reg("GoldenEasterEgg", lambda m: painted_egg(m, "gold", "gold_light", "stripes"), "Easter")
reg("EasterBunny", lambda m: bunny_statue(m), "Easter")
reg("ChocolateBunny", chocolate_bunny, "Easter")
reg("EggHuntSign", egg_hunt_sign, "Easter")
reg("FlowerCart", flower_cart, "Easter")


# ----------------------------------------------------------------------------
# birthdays & fiestas
# ----------------------------------------------------------------------------
def star_pinata(m):
    blk(m, (0.1, 0.1, 3.0), (0, 0, 7.0), "string")
    c0 = (0, 0, 4.2)
    m.ico(r=1.2, sub=0, color="plastic_pink", loc=c0, smooth=False)
    spikes = (((1, 0, 0), (0, 90, 0), "plastic_yellow"), ((-1, 0, 0), (0, -90, 0), "plastic_blue"),
              ((0, 1, 0), (-90, 0, 0), "neon_green"), ((0, -1, 0), (90, 0, 0), "plastic_orange"),
              ((0, 0, 1), (0, 0, 0), "plastic_purple"), ((0, 0, -1), (180, 0, 0), "plastic_red"))
    for d, rot, c in spikes:
        m.cone(r=0.55, h=1.6, seg=6, color=c, rot=rot, loc=(c0[0] + d[0] * 0.9, c0[1] + d[1] * 0.9, c0[2] + d[2] * 0.9))
        blk(m, (0.1, 0.1, 0.8), (c0[0] + d[0] * 2.5, c0[1] + d[1] * 2.5, c0[2] + d[2] * 2.5 - 0.4), c)


def donkey_pinata(m):
    cols = ["plastic_pink", "plastic_yellow", "plastic_blue", "neon_green", "plastic_orange"]
    m.box((2.0, 3.6, 1.8), color=lambda c, n: cols[int((c.z + 5) / 0.36) % 5], loc=(0, 0, 3.2), cuts={"z": 0.36})
    m.box((1.2, 1.2, 2.4), color=lambda c, n: cols[int((c.z + 5) / 0.36) % 5], loc=(0, -1.9, 4.6), cuts={"z": 0.36},
          rot=(20, 0, 0))
    blk(m, (1.2, 1.6, 1.0), (0, -2.6, 5.6), "plastic_pink", bev=0.15)
    for s in (-1, 1):
        blk(m, (0.3, 0.3, 1.0), (s * 0.4, -2.2, 6.4), "plastic_yellow")
        blk(m, (0.15, 0.05, 0.15), (s * 0.45, -3.42, 5.8), "eye_black")
        for y in (-1.2, 1.2):
            m.box((0.5, 0.5, 2.2), color=lambda c, n: cols[int((c.z + 5) / 0.36) % 5], loc=(s * 0.6, y, 1.4),
                  cuts={"z": 0.36})
    blk(m, (0.3, 0.3, 1.2), (0, 1.9, 3.4), "plastic_blue", rot=(-30, 0, 0))


def maracas(m):
    for s in (-1, 1):
        with m.at((s * 0.9, 0, 0), s * 15):
            m.cyl(r=0.15, h=1.4, seg=6, color="wood_mid", loc=(0, 0, 0.7))
            blk(m, (1.2, 1.2, 1.3), (0, 0, 1.9), "plastic_red" if s < 0 else "plastic_green", bev=0.4)
            blk(m, (1.25, 1.25, 0.25), (0, 0, 1.9), "plastic_yellow")


def balloon_bunch(m, cols=("plastic_red", "plastic_blue", "plastic_yellow", "neon_green", "plastic_purple")):
    rnd = random.Random(12)
    for i, c in enumerate(cols):
        x, y = rnd.uniform(-1.2, 1.2), rnd.uniform(-0.8, 0.8)
        z = 4.5 + rnd.uniform(0, 1.8)
        balloon(m, x, y, z, c, 0.75)
        string_to(m, (x, y, z - 0.25), (0, 0, 0.6))
    blk(m, (0.8, 0.8, 0.6), (0, 0, 0.3), "gold", bev=0.12)


reg("StarPinata", star_pinata, "Party")
reg("DonkeyPinata", donkey_pinata, "Party")
reg("Maracas", maracas, "Party")
reg("BalloonBunch", lambda m: balloon_bunch(m), "Party")
reg("BirthdayBanner", lambda m: banner(m, "HAPPY BIRTHDAY", "white", "plastic_blue", px=0.25), "Party")
reg("PartyBunting", lambda m: bunting(m, 12.0, ("plastic_red", "plastic_yellow", "plastic_blue", "neon_green")), "Party")


# ----------------------------------------------------------------------------
# 4th of July & summer
# ----------------------------------------------------------------------------
def star_top_hat(m):
    m.cyl(r=1.6, h=0.2, seg=8, color="plastic_blue", loc=(0, 0, 0.1))
    m.cyl(r=1.0, h=2.4, seg=8, color=lambda c, n: "plastic_red" if int(c.z / 0.4) % 2 else "white", loc=(0, 0, 1.4),
          cuts={"z": 0.4})
    m.cyl(r=1.02, h=0.5, seg=8, color="plastic_blue", loc=(0, 0, 0.5))
    for i in range(4):
        a = math.radians(90 * i)
        m.prism(star_pts(0.22, 0.1, 5), depth=0.06, color="white", rot=(90, 0, 90 * i),
                loc=(1.04 * math.sin(a), -1.04 * math.cos(a), 0.5))


def sparkler(m):
    m.cyl(r=0.05, h=3.0, seg=4, color="iron_dark", loc=(0, 0, 1.5))
    m.cyl(r=0.1, h=1.2, seg=4, color="charcoal", loc=(0, 0, 2.4))
    for i in range(10):
        a = math.radians(36 * i)
        blk(m, (0.8, 0.06, 0.06), (0.4 * math.cos(a), 0, 3.1 + 0.4 * math.sin(a)), "fire_light", rot=(0, -36 * i, 0))
    blk(m, (0.3, 0.3, 0.3), (0, 0, 3.1), "white", bev=0.08)


def big_rocket(m):
    m.cyl(r=0.9, h=5.0, seg=8, color=lambda c, n: ["plastic_red", "white", "plastic_blue"][int(c.z / 0.9) % 3],
          loc=(0, 0, 3.2), cuts={"z": 0.9})
    m.cone(r=1.0, h=1.6, seg=8, color="plastic_red", loc=(0, 0, 5.7))
    m.prism(star_pts(0.5, 0.22, 5), depth=0.1, color="white", rot=(90, 0, 0), loc=(0, -0.95, 3.2))
    for i in range(4):
        m.prism([(0, 0), (1.0, 0), (0, 1.4)], depth=0.12, color="plastic_blue", rot=(90, 0, 90 * i),
                loc=(0, 0, 0.7), deform=lambda co: co.__class__((co.x + 0.85, co.y, co.z)))
    blk(m, (0.1, 0.1, 0.8), (0, 0, 0.3), "string")


def bbq_grill(m):
    for s in (-1, 1):
        blk(m, (0.2, 0.2, 3.0), (s * 1.4, 0.8, 1.5), "charcoal")
        blk(m, (0.2, 0.2, 3.0), (s * 1.4, -0.8, 1.5), "charcoal")
    m.cyl(r=1.5, h=3.4, seg=8, color="charcoal", rot=(0, 90, 0), loc=(0, 0, 3.3),
          deform=lambda co: co.__class__((co.x, co.y, min(co.z, 0.0))))
    m.cyl(r=1.5, h=3.4, seg=8, color="charcoal", rot=(0, 90, 0), loc=(0, 0.3, 3.9),
          deform=lambda co: co.__class__((co.x, co.y, max(co.z, 0.3))), )
    blk(m, (3.2, 2.8, 0.1), (0, 0, 3.3), "iron")
    for x in (-0.9, 0.0, 0.9):
        m.cyl(r=0.2, h=1.4, seg=6, color="meat", rot=(90, 0, 0), loc=(x, -0.5, 3.45))
    blk(m, (1.2, 0.3, 0.2), (0, -1.6, 4.6), "wood_mid")
    blk(m, (1.6, 1.6, 0.1), (2.3, 0, 2.2), "wood_light")


def picnic_set(m):
    m.box((6.0, 6.0, 0.1), color=lambda c, n: "plastic_red" if (math.floor(c.x / 1.0) + math.floor(c.y / 1.0)) % 2
          else "white", loc=(0, 0, 0.05), cuts={"x": 1.0, "y": 1.0})
    blk(m, (2.2, 1.4, 1.2), (1.4, 1.4, 0.7), "wood_light", bev=0.1)
    m.torus(R=0.7, r=0.08, seg=8, arc=180, color="wood_mid", rot=(90, 0, 0), loc=(1.4, 1.4, 1.3))
    for x, y in ((-1.5, -1.0), (-0.3, -1.6)):
        m.cyl(r=0.6, h=0.08, seg=8, color="white", loc=(x, y, 0.15))
        blk(m, (0.8, 0.3, 0.3), (x, y, 0.3), "bread")
    m.cyl(r=0.3, h=1.2, seg=6, color="plastic_red", loc=(-1.6, 1.2, 0.7))


def beach_umbrella(m, a="plastic_red", b="white"):
    m.cyl(r=0.12, h=6.0, seg=6, color="white", loc=(0, 0, 3.0))
    m.lathe([(0, 6.2), (3.6, 5.2), (3.5, 5.0), (0, 5.8)], seg=8, color=lambda c, n: a if int(
        (math.degrees(math.atan2(c.y, c.x)) + 360) / 45) % 2 else b, rot=(0, 0, 0))
    blk(m, (0.3, 0.3, 0.3), (0, 0, 6.3), a, bev=0.08)


def beach_ball(m):
    cols = ["plastic_red", "white", "plastic_blue", "plastic_yellow"]
    m.sphere(r=1.2, seg=8, rings=6, round=True, loc=(0, 0, 1.2),
             color=lambda c, n: cols[int((math.degrees(math.atan2(c.y, c.x)) + 360) / 45) % 4] if abs(n.z) < 0.85 else "white")


def sand_bucket(m):
    m.lathe([(0.8, 0), (1.0, 1.4), (0.95, 1.5), (0.7, 0.1), (0, 0.1)], seg=8, color="plastic_blue", caps=False)
    m.cyl(r=0.72, h=0.1, seg=8, color="plastic_blue", loc=(0, 0, 0.05))
    m.cyl(r=0.9, h=0.1, seg=8, color="sand", loc=(0, 0, 1.2))
    m.torus(R=1.0, r=0.05, seg=8, arc=180, color="plastic_yellow", rot=(90, 0, 0), loc=(0, 0, 1.5))
    with m.at((1.4, 0.2, 0), 30):
        blk(m, (0.2, 0.2, 1.6), (0, 0, 1.0), "plastic_red", rot=(20, 0, 0))
        blk(m, (0.8, 0.1, 0.9), (0, -0.35, 0.3), "plastic_red", rot=(20, 0, 0))


def surfboard(m, col="plastic_orange"):
    m.prism([(0, 0), (0.7, 0.8), (0.8, 3.0), (0.6, 5.2), (0, 6.2), (-0.6, 5.2), (-0.8, 3.0), (-0.7, 0.8)], depth=0.25,
            color=lambda c, n: col if abs(c.x) > 0.15 else "white", rot=(80, 0, 0), loc=(0, 0.4, 0.2),
            cuts={"x": [-0.15, 0.15]})
    blk(m, (0.8, 0.8, 0.3), (0, 0.5, 0.15), "sand")


def pool_float(m, kind="donut"):
    if kind == "donut":
        m.torus(R=1.6, r=0.7, seg=8, rseg=6, color=lambda c, n: "frosting_pink" if n.z > 0.3 else "donut", loc=(0, 0, 0.7))
        for a in range(0, 360, 45):
            r = math.radians(a)
            blk(m, (0.35, 0.12, 0.1), (1.6 * math.cos(r), 1.6 * math.sin(r), 1.4), ["sprinkle_blue", "sprinkle_yellow",
                                                                                   "white"][a // 45 % 3], rot=(0, 0, a))
    else:
        m.torus(R=1.6, r=0.7, seg=8, rseg=6, color="flamingo", loc=(0, 0, 0.7))
        m.tube([(0, -1.6, 1.0), (0, -2.0, 2.6), (0, -1.6, 3.6), (0, -2.2, 4.0)], [0.4, 0.35, 0.35, 0.3], seg=6,
               color="flamingo")
        blk(m, (0.5, 0.8, 0.4), (0, -2.6, 3.9), "black", bev=0.1)
        for s in (-1, 1):
            blk(m, (0.12, 0.1, 0.12), (s * 0.3, -2.2, 4.1), "eye_black")


def lifeguard_chair(m):
    for sx in (-1, 1):
        for sy in (-1, 1):
            blk(m, (0.3, 0.3, 6.0), (sx * 1.2, sy * 1.2, 3.0), "white", rot=(sy * -5, sx * 5, 0))
    blk(m, (2.6, 2.4, 0.3), (0, 0, 6.1), "white")
    blk(m, (2.6, 0.3, 2.2), (0, 1.2, 7.3), "plastic_red")
    for k in range(5):
        blk(m, (2.2, 0.2, 0.2), (0, -1.3, 1.0 + k * 1.0), "white")
    m.cyl(r=0.1, h=3.0, seg=6, color="white", loc=(1.2, 1.2, 8.0))
    m.lathe([(0, 9.8), (1.8, 9.2), (0, 9.4)], seg=8, color="plastic_red")
    text(m, "LIFEGUARD", 0, 1.03, 7.3, px=0.1, depth=0.05, col="white")


def beach_cooler(m):
    blk(m, (2.6, 1.8, 1.8), (0, 0, 0.9), "plastic_blue", bev=0.15)
    blk(m, (2.7, 1.9, 0.5), (0, 0, 2.0), "white", bev=0.12)
    m.torus(R=0.5, r=0.06, seg=6, arc=180, color="white", rot=(90, 0, 0), loc=(0, 0, 2.2))


def beach_towel(m):
    m.box((3.0, 6.0, 0.08), color=lambda c, n: ["plastic_blue", "white", "plastic_yellow"][int((c.y + 10) / 0.8) % 3],
          loc=(0, 0, 0.04), cuts={"y": 0.8})
    blk(m, (1.4, 0.6, 0.4), (0, 2.4, 0.25), "white", bev=0.15)


reg("FlagBunting", lambda m: bunting(m, 12.0, ("plastic_red", "white", "plastic_blue")), "July4th")
reg("StarTopHat", star_top_hat, "July4th")
reg("Sparkler", sparkler, "July4th")
reg("BigFireworkRocket", big_rocket, "July4th")
reg("BBQGrill", bbq_grill, "July4th")
reg("PicnicSet", picnic_set, "July4th")
reg("StarBalloons", lambda m: balloon_bunch(m, ("plastic_red", "white", "plastic_blue", "plastic_red", "white")), "July4th")
reg("BeachUmbrella", lambda m: beach_umbrella(m), "Summer")
reg("BlueBeachUmbrella", lambda m: beach_umbrella(m, "plastic_blue", "plastic_yellow"), "Summer")
reg("BeachBall", beach_ball, "Summer")
reg("SandBucket", sand_bucket, "Summer")
reg("Surfboard", lambda m: surfboard(m), "Summer")
reg("BlueSurfboard", lambda m: surfboard(m, "plastic_blue"), "Summer")
reg("DonutFloat", lambda m: pool_float(m, "donut"), "Summer")
reg("FlamingoFloat", lambda m: pool_float(m, "flamingo"), "Summer")
reg("LifeguardChair", lifeguard_chair, "Summer")
reg("BeachCooler", beach_cooler, "Summer")
reg("BeachTowel", beach_towel, "Summer")


# ----------------------------------------------------------------------------
# Halloween
# ----------------------------------------------------------------------------
def pumpkin(m, face="happy", s=1.0, loc=(0, 0, 0), lit=True):
    x0, y0, z0 = loc
    with m.at(loc):
        m.box((2.4 * s, 2.2 * s, 1.9 * s), color=lambda c, n: "pumpkin_dark" if abs(c.x) < 0.12 * s or
              abs(abs(c.x) - 0.7 * s) < 0.12 * s else "pumpkin", bevel=0.45 * s, loc=(0, 0, 0.95 * s),
              cuts={"x": [k * s for k in (-0.82, -0.58, -0.12, 0.12, 0.58, 0.82)]})
        blk(m, (0.25 * s, 0.25 * s, 0.6 * s), (0, 0, 2.1 * s), "leaf_dark", bev=0.05, rot=(0, 15, 0))
        if face is None:
            return
        glow = "fire_light" if lit else "black"
        y = -1.11 * s
        if face == "happy":
            for sx in (-1, 1):
                m.prism([(-0.25, 0), (0.25, 0), (0, 0.4)], depth=0.1, color=glow, rot=(90, 0, 0),
                        loc=(sx * 0.5 * s, y, 1.2 * s), scale=s)
            m.prism([(-0.7, 0.2), (0.7, 0.2), (0.4, -0.2), (-0.4, -0.2)], depth=0.1, color=glow, rot=(90, 0, 0),
                    loc=(0, y, 0.65 * s), scale=s)
        elif face == "scary":
            for sx in (-1, 1):
                m.prism([(-0.3, 0.3), (0.3, 0.15), (0.0, -0.1)] if sx < 0 else [(-0.3, 0.15), (0.3, 0.3), (0.0, -0.1)],
                        depth=0.1, color=glow, rot=(90, 0, 0), loc=(sx * 0.5 * s, y, 1.25 * s), scale=s)
            m.prism([(-0.8, 0.2), (-0.5, -0.1), (-0.3, 0.1), (0, -0.2), (0.3, 0.1), (0.5, -0.1), (0.8, 0.2), (0.4, -0.3),
                     (-0.4, -0.3)], depth=0.1, color=glow, rot=(90, 0, 0), loc=(0, y, 0.65 * s), scale=s)
        else:   # cat face
            for sx in (-1, 1):
                blk(m, (0.3 * s, 0.1, 0.3 * s), (sx * 0.45 * s, y, 1.25 * s), glow)
            m.prism([(-0.15, 0), (0.15, 0), (0, -0.2)], depth=0.1, color=glow, rot=(90, 0, 0), loc=(0, y, 0.95 * s), scale=s)
            for sx in (-1, 1):
                blk(m, (0.6 * s, 0.1, 0.06 * s), (sx * 0.6 * s, y, 0.85 * s), glow)


def pumpkin_stack(m):
    pumpkin(m, "happy", 1.2, (0, 0, 0))
    pumpkin(m, "scary", 0.9, (0.1, 0, 2.3))
    pumpkin(m, "cat", 0.6, (-0.1, 0, 4.0))


def ghost_decor(m):
    m.lathe([(1.4, 0.3), (1.3, 1.5), (1.1, 2.8), (0.6, 3.6), (0, 3.8)], seg=8, color="white", rot=(0, 0, 22.5))
    for i in range(8):
        a = math.radians(45 * i + 22.5)
        m.cone(r=0.35, h=0.6, seg=4, color="white", rot=(180, 0, 0), loc=(1.3 * math.cos(a), 1.3 * math.sin(a), 0.35))
    for sx in (-1, 1):
        blk(m, (0.35, 0.1, 0.5), (sx * 0.4, -1.2, 2.7), "black")
    blk(m, (0.5, 0.1, 0.6), (0, -1.28, 1.9), "black")
    for sx in (-1, 1):
        blk(m, (0.5, 1.2, 0.4), (sx * 1.3, -0.4, 2.2), "white", bev=0.12, rot=(0, sx * -30, 0))


def pumpkin_pail(m):
    pumpkin(m, "happy", 0.9, (0, 0, 0))
    blk(m, (1.9, 1.8, 0.3), (0, 0, 1.75), "black")
    rnd = random.Random(2)
    for i in range(6):
        blk(m, (0.4, 0.25, 0.25), (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.5, 0.5), 1.95),
            rnd.choice(["plastic_red", "plastic_purple", "neon_green", "chocolate", "lemon"]), rot=(0, 0, rnd.uniform(0, 90)))
    m.torus(R=1.1, r=0.06, seg=8, arc=180, color="black", rot=(90, 0, 0), loc=(0, 0, 1.9))


def bat_decor(m):
    blk(m, (0.8, 0.7, 0.9), (0, 0, 0), "black", bev=0.2)
    for s in (-1, 1):
        m.prism([(0, 0.3), (1.2, 0.6), (2.0, 0.2), (1.7, -0.1), (1.3, 0.1), (0.9, -0.2), (0.5, 0.0), (0, -0.2)],
                depth=0.08, color="charcoal", rot=(90, 0, 0), scale=(s, 1, 1))
        m.pyramid(w=0.2, h=0.3, color="black", loc=(s * 0.22, 0, 0.45))
        blk(m, (0.12, 0.1, 0.12), (s * 0.18, -0.36, 0.1), "neon_red")


def skeleton(m):
    B = "offwhite"
    blk(m, (1.2, 1.1, 1.1), (0, 0, 5.4), B, bev=0.2)
    for sx in (-1, 1):
        blk(m, (0.3, 0.1, 0.3), (sx * 0.28, -0.56, 5.5), "black")
    blk(m, (0.6, 0.1, 0.15), (0, -0.56, 5.05), "black")
    blk(m, (0.25, 0.25, 2.2), (0, 0, 3.7), B)
    for k in range(4):
        blk(m, (1.4 - k * 0.1, 0.5, 0.15), (0, -0.1, 4.4 - k * 0.35), B)
    blk(m, (1.2, 0.5, 0.4), (0, 0, 2.5), B, bev=0.08)
    for sx in (-1, 1):
        blk(m, (0.2, 0.2, 1.3), (sx * 0.45, 0, 1.7), B)
        blk(m, (0.2, 0.2, 1.2), (sx * 0.45, 0, 0.6), B)
        blk(m, (0.4, 0.6, 0.2), (sx * 0.45, -0.2, 0.1), B)
        blk(m, (0.18, 0.18, 1.2), (sx * 0.9, 0, 3.9), B, rot=(0, sx * 10, 0))
        blk(m, (0.18, 0.18, 1.1), (sx * 1.05, 0, 2.8), B)


def candy_corn(m, s=1.0):
    m.prism([(-0.9 * s, 0), (0.9 * s, 0), (0.5 * s, 1.2 * s), (0, 2.0 * s), (-0.5 * s, 1.2 * s)], depth=0.9 * s,
            color=lambda c, n: "white" if c.z > 1.4 * s else ("plastic_orange" if c.z > 0.6 * s else "lemon"),
            rot=(90, 0, 0), bevel=0.15 * s, cuts={"z": [0.6 * s, 1.4 * s]})


def candy_pile(m):
    rnd = random.Random(6)
    for i in range(16):
        x, y = rnd.uniform(-1.2, 1.2), rnd.uniform(-1.2, 1.2)
        z = 0.2 + (1.2 - math.hypot(x, y)) * 0.5
        col = rnd.choice(["plastic_red", "plastic_purple", "neon_green", "plastic_orange", "lemon", "plastic_blue"])
        with m.at((x, y, max(0.2, z)), rnd.uniform(0, 180)):
            blk(m, (0.6, 0.35, 0.35), (0, 0, 0), col, bev=0.1)
            for s in (-1, 1):
                m.prism([(0, -0.2), (0.3, 0), (0, 0.2)], depth=0.05, color=col, rot=(90, 0, 0 if s > 0 else 180),
                        loc=(s * 0.3, 0, 0))


def cross_tombstone(m):
    blk(m, (2.4, 1.6, 0.3), (0, 0, 0.15), "dirt", bev=0.08)
    blk(m, (0.6, 0.5, 3.6), (0, 0.2, 2.0), "stone", bev=0.08)
    blk(m, (2.0, 0.5, 0.6), (0, 0.2, 2.8), "stone", bev=0.08)
    blk(m, (0.4, 0.4, 0.4), (0.8, -0.5, 0.4), "moss", bev=0.12)


def rip_tombstone(m):
    blk(m, (2.6, 1.8, 0.3), (0, 0, 0.15), "dirt", bev=0.08)
    m.prism([(-1.0, 0), (1.0, 0), (1.0, 1.8), (0.6, 2.4), (0, 2.6), (-0.6, 2.4), (-1.0, 1.8)], depth=0.5,
            color="stone_light", rot=(90, 0, 0), loc=(0, 0.3, 0.3), bevel=0.06)
    text(m, "RIP", 0, 0.04, 2.0, px=0.2, depth=0.06, col="stone_dark")
    blk(m, (1.2, 0.08, 0.1), (0, 0.02, 1.2), "stone_dark")


def graveyard_fence(m, L=10.0):
    for k in range(int(L / 1.0) + 1):
        x = -L / 2 + k * 1.0
        blk(m, (0.15, 0.15, 3.0), (x, 0, 1.5), "black")
        m.pyramid(w=0.3, h=0.4, color="black", loc=(x, 0, 3.0))
    for z in (0.6, 2.4):
        blk(m, (L, 0.15, 0.15), (0, 0, z), "black")
    for s in (-1, 1):
        blk(m, (0.8, 0.8, 3.8), (s * (L / 2 + 0.4), 0, 1.9), "stone_dark", bev=0.1)
        m.pyramid(w=1.0, h=0.6, color="stone", loc=(s * (L / 2 + 0.4), 0, 3.8))


def zombie_hand(m):
    m.lathe([(1.2, 0), (0.6, 0.4), (0, 0.5)], seg=8, color="dirt_dark", deform=lambda co: co.__class__((co.x, co.y, co.z)))
    blk(m, (0.5, 0.4, 1.8), (0, 0, 1.2), "moss", rot=(8, 0, 0))
    blk(m, (0.8, 0.5, 0.7), (0, -0.1, 2.3), "moss", bev=0.1)
    for i in range(4):
        blk(m, (0.16, 0.16, 0.6), (-0.3 + i * 0.2, -0.15, 2.9 + (i % 2) * 0.1), "moss", rot=(-15 + i * 8, 0, 0))
    blk(m, (0.18, 0.18, 0.5), (0.45, -0.1, 2.5), "moss", rot=(0, 40, 0))
    blk(m, (0.55, 0.45, 0.35), (0, 0, 0.9), "fabric_gray", bev=0.05)


def mummy(m):
    wrap = lambda c, n: "offwhite" if int((c.z + c.x * 0.3) / 0.4) % 2 else "paper"
    m.box((1.8, 1.2, 3.0), color=wrap, loc=(0, 0, 2.3), bevel=0.2, cuts={"z": 0.4})
    m.box((1.4, 1.2, 1.4), color=wrap, loc=(0, 0, 4.5), bevel=0.25, cuts={"z": 0.4})
    for s in (-1, 1):
        blk(m, (0.25, 0.1, 0.2), (s * 0.3, -0.61, 4.6), "neon_green")
        m.box((0.6, 0.6, 2.0), color=wrap, loc=(s * 0.5, 0, 0.9), bevel=0.1, cuts={"z": 0.4})
        m.box((0.5, 1.8, 0.5), color=wrap, loc=(s * 1.1, -0.7, 3.3), bevel=0.1, cuts={"y": 0.4})


def monster_decor(m):
    blk(m, (2.0, 1.4, 3.0), (0, 0, 3.6), "fabric_navy", bev=0.15)
    blk(m, (1.6, 1.4, 1.8), (0, 0, 6.0), "moss", bev=0.15)
    blk(m, (1.7, 1.5, 0.4), (0, 0, 7.0), "black")
    for s in (-1, 1):
        blk(m, (0.3, 0.1, 0.25), (s * 0.35, -0.72, 6.3), "white")
        blk(m, (0.15, 0.1, 0.15), (s * 0.35, -0.75, 6.3), "black")
        m.cyl(r=0.15, h=0.6, seg=6, color="gray", rot=(0, 90, 0), loc=(s * 0.95, 0, 5.8))
        blk(m, (0.7, 0.7, 2.2), (s * 0.55, 0, 1.1), "charcoal", bev=0.1)
        blk(m, (0.55, 0.6, 2.6), (s * 1.3, -0.5, 4.2), "fabric_navy", bev=0.1, rot=(-70, 0, 0))
        blk(m, (0.5, 0.5, 0.5), (s * 1.3, -1.8, 4.6), "moss", bev=0.1)
    blk(m, (1.0, 0.1, 0.1), (0, -0.72, 5.5), "black")
    for k in range(3):
        blk(m, (0.1, 0.12, 0.3), (-0.3 + k * 0.3, -0.72, 5.5), "black")


def witch_broom(m):
    m.cyl(r=0.1, h=4.2, seg=6, color="wood_mid", rot=(0, 75, 0), loc=(0, 0, 1.4))
    m.cone(r=0.7, h=1.8, seg=8, color="corn_husk", rot=(0, -105, 0), loc=(-1.7, 0, 0.9))
    m.torus(R=0.3, r=0.06, seg=8, color="fabric_purple", rot=(0, -15, 0), loc=(-1.4, 0, 0.9))
    blk(m, (0.8, 0.8, 0.4), (-2.0, 0, 0.2), "stone_dark", bev=0.1)


def bubbling_cauldron(m):
    for s in (-1, 1):
        m.tube([(s * 1.8, -1.2, 0), (s * 1.3, 0, 3.6), (s * 1.8, 1.2, 0)], [0.1] * 3, seg=4, color="wood_dark")
    m.lathe([(0.8, 0.4), (1.5, 0.8), (1.8, 1.8), (1.5, 2.8), (1.6, 3.0), (0, 3.0)], seg=8, color="iron_dark")
    m.cyl(r=1.4, h=0.1, seg=8, color="neon_green", loc=(0, 0, 2.85))
    for x, y, r in ((0.4, 0.2, 0.4), (-0.5, -0.3, 0.3), (0.1, -0.6, 0.25)):
        blk(m, (r * 2, r * 2, r * 1.6), (x, y, 3.0), "slime", bev=r * 0.4)
    for i in range(5):
        a = math.radians(72 * i)
        m.cone(r=0.3, h=0.7, seg=5, color="fire" if i % 2 else "fire_light", loc=(0.7 * math.cos(a), 0.7 * math.sin(a), 0))


def potion_shelf(m):
    blk(m, (5.0, 1.4, 6.0), (0, 0.3, 3.0), "wood_dark", bev=0.05)
    rnd = random.Random(13)
    for k in range(3):
        z = 1.0 + k * 1.8
        blk(m, (4.6, 1.2, 0.15), (0, 0.1, z), "wood_mid")
        for i in range(5):
            x = -1.8 + i * 0.9
            c = rnd.choice(["potion_red", "potion_blue", "potion_green", "potion_purple", "neon_green"])
            m.lathe([(0, 0), (0.3, 0.05), (0.35, 0.5), (0.15, 0.8), (0.12, 1.1), (0, 1.1)], seg=6,
                    color=lambda cc, n, c=c, z=z: c if cc.z < z + 0.55 else "glass", loc=(x, -0.2, z + 0.1),
                    cuts={"z": [z + 0.55]})
    for i in range(3):
        blk(m, (0.4, 0.1, 1.4), (-2.3 + i * 0.1, -0.44, 5.8 - i * 0.3), "offwhite", rot=(0, 0, 0))


def hanging_spider(m):
    blk(m, (0.06, 0.06, 4.0), (0, 0, 5.5), "offwhite")
    blk(m, (1.2, 1.4, 0.9), (0, 0.2, 3.2), "black", bev=0.3)
    blk(m, (0.8, 0.8, 0.7), (0, -0.7, 3.2), "black", bev=0.2)
    for s in (-1, 1):
        blk(m, (0.14, 0.1, 0.14), (s * 0.2, -1.12, 3.3), "neon_red")
        for k in range(4):
            y = -0.4 + k * 0.4
            m.tube([(s * 0.5, y, 3.2), (s * 1.4, y + (k - 1.5) * 0.3, 3.9), (s * 2.0, y + (k - 1.5) * 0.5, 2.6)], [0.07] * 3,
                   seg=4, color="black")


def haunted_house(m):
    """Crooked two-storey haunted house with glowing windows (decor, not walk-in)."""
    W, D = 16.0, 12.0
    blk(m, (W + 2, D + 2, 0.8), (0, 0, 0.4), "stone_dark", bev=0.1)
    m.box((W, D, 7.0), color=lambda c, n: "plank_gray" if int(c.z / 0.8) % 2 else "stone_dark", loc=(0, 0, 4.3),
          bevel=0.1, cuts={"z": 0.8})
    m.box((W - 2, D - 1, 6.0), color=lambda c, n: "plank_gray" if int(c.z / 0.8) % 2 else "stone_dark",
          loc=(0.4, 0, 10.8), bevel=0.1, cuts={"z": 0.8}, rot=(0, 2.5, 0))
    with m.group("Roof"):
        m.prism([(-(D / 2 + 1.2), 0), (D / 2 + 1.2, 0), (0.6, 6.5)], depth=W + 0.6, color="obsidian", rot=(90, 0, 90),
                loc=(0.8, 0, 13.8), smooth=False)
        blk(m, (1.6, 1.6, 4.0), (-4.5, 2.0, 17.0), "brick_dark", bev=0.1, rot=(0, -5, 0))
        m.cone(r=2.2, h=5.0, seg=4, color="obsidian", loc=(W / 2 - 1.0, -D / 2 + 1.0, 14.5), rot=(0, 0, 45))
    blk(m, (3.2, 3.2, 14.0), (W / 2 - 1.0, -D / 2 + 1.0, 7.8), "plank_gray", bev=0.1)
    for x, z in ((-5.0, 4.5), (0.0, 4.5), (-5.0, 10.5), (1.0, 10.5), (W / 2 - 1.0, 12.0)):
        blk(m, (1.8, 0.2, 2.4), (x, -D / 2 - (1.62 if x > 6 else 0.02), z), "neon_yellow" if z < 11 else "neon_green")
        blk(m, (2.2, 0.3, 0.3), (x, -D / 2 - (1.7 if x > 6 else 0.1), z), "wood_dark", rot=(0, 20, 0))
    with m.group("Door"):
        blk(m, (2.6, 0.3, 4.2), (4.5, -D / 2 - 0.05, 2.9), "wood_deep", bev=0.05)
        blk(m, (0.3, 0.2, 0.3), (5.4, -D / 2 - 0.25, 2.9), "brass")
    blk(m, (5.0, 2.2, 0.4), (4.5, -D / 2 - 1.1, 0.6), "wood_dark")
    for x in (2.3, 6.7):
        blk(m, (0.3, 0.3, 4.4), (x, -D / 2 - 2.0, 2.8), "wood_dark")
    blk(m, (5.4, 2.6, 0.3), (4.5, -D / 2 - 1.2, 5.1), "obsidian", rot=(-8, 0, 0))
    with m.at((-3.0, -D / 2 - 2.5, 0.8)):
        pumpkin(m, "scary", 0.8)
    with m.at((-6.0, -D / 2 - 2.0, 0.8)):
        pumpkin(m, "happy", 0.6)


for _n, _f in (("HappyPumpkin", lambda m: pumpkin(m, "happy")), ("ScaryPumpkin", lambda m: pumpkin(m, "scary")),
               ("CatPumpkin", lambda m: pumpkin(m, "cat")), ("PlainPumpkin", lambda m: pumpkin(m, None)),
               ("PumpkinStack", pumpkin_stack), ("GhostDecor", ghost_decor), ("PumpkinPail", pumpkin_pail),
               ("Skeleton", skeleton), ("CandyCorn", lambda m: candy_corn(m)), ("CandyPile", candy_pile),
               ("CrossTombstone", cross_tombstone), ("RIPTombstone", rip_tombstone),
               ("GraveyardFence", lambda m: graveyard_fence(m)), ("ZombieHand", zombie_hand), ("Mummy", mummy),
               ("MonsterDecor", monster_decor), ("WitchBroom", witch_broom), ("BubblingCauldron", bubbling_cauldron),
               ("PotionShelf", potion_shelf), ("HangingSpider", hanging_spider)):
    reg(_n, _f, "Halloween")
reg("BatDecor", bat_decor, "Halloween", origin="center")
reg("HauntedHouse", haunted_house, "Halloween", split=True)
reg("TrickOrTreatBanner", lambda m: banner(m, "TRICK OR TREAT", "plastic_orange", "black", px=0.25), "Halloween")


# ----------------------------------------------------------------------------
# harvest & Thanksgiving
# ----------------------------------------------------------------------------
def roast_turkey(m):
    m.cyl(r=2.4, h=0.2, seg=8, color="ceramic", loc=(0, 0, 0.1), bevel=0.05)
    blk(m, (2.4, 3.0, 1.8), (0, 0, 1.1), "caramel", bev=0.6)
    for s in (-1, 1):
        m.tube([(s * 0.9, -1.0, 1.0), (s * 1.3, -1.9, 1.3)], [0.4, 0.3], seg=6, color="caramel")
        blk(m, (0.3, 0.3, 0.3), (s * 1.35, -2.1, 1.35), "white", bev=0.08)
    for x, y in ((-1.6, 1.4), (1.7, 1.2), (1.5, -1.6)):
        blk(m, (0.5, 0.5, 0.4), (x, y, 0.4), "lettuce", bev=0.1)
        blk(m, (0.3, 0.3, 0.3), (x + 0.3, y, 0.45), "tomato", bev=0.1)


def cornucopia(m):
    stripes = lambda c, n: "wood_light" if int((c.x + 5) / 0.45) % 2 else "wood_mid"
    m.lathe([(1.3, 0), (1.0, 1.2), (0.6, 2.4), (0.3, 3.2), (0, 3.6)], seg=8, color=stripes, rot=(0, -90, 0),
            loc=(0.6, 0, 1.3), cuts={"x": 0.45})
    m.tube([(-3.0, 0, 1.3), (-3.5, 0, 1.8), (-3.2, 0, 2.3)], [0.18, 0.12, 0.02], seg=4, color="wood_mid")
    for i, (c, x, y, z) in enumerate((("pumpkin", 1.2, -0.2, 0.5), ("apple_red", 1.4, 0.8, 0.45), ("grape", 1.9, -0.9, 0.4),
                                      ("corn", 2.2, 0.3, 0.35), ("pear", 1.0, -1.0, 0.4), ("orange", 0.8, 0.4, 1.7))):
        m.box((0.8, 0.8, 0.8), color=c, bevel=0.2, loc=(x, y, z))


def harvest_table(m):
    blk(m, (8.0, 3.4, 0.3), (0, 0, 3.0), "wood_mid", bev=0.06)
    for sx in (-3.6, 3.6):
        for sy in (-1.4, 1.4):
            blk(m, (0.35, 0.35, 2.9), (sx, sy, 1.45), "wood_dark")
    m.box((7.4, 1.0, 0.05), color="plastic_orange", loc=(0, 0, 3.17))
    with m.at((0, 0, 3.15)):
        roast_turkey(m)
    for x in (-3.0, 3.0):
        m.cyl(r=0.8, h=0.3, seg=8, color="bread_crust", loc=(x, 0.6, 3.3))
        m.cyl(r=0.7, h=0.1, seg=8, color="pumpkin", loc=(x, 0.6, 3.48))
    for x in (-2.6, -1.0, 1.0, 2.6):
        for y in (-1.2, 1.2):
            m.cyl(r=0.5, h=0.06, seg=8, color="ceramic", loc=(x, y, 3.18))


def leaf_pile(m):
    rnd = random.Random(9)
    for i in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0, 1.8)
        z = (1.9 - r) * 0.6 + 0.1
        m.leaf(length=0.7, width=0.4, thick=0.05, color=rnd.choice(["autumn_orange", "autumn_red", "autumn_yellow",
                                                                   "caramel"]),
               loc=(math.cos(a) * r, math.sin(a) * r, z), rot=(rnd.uniform(-40, 40), rnd.uniform(-40, 40), rnd.uniform(0, 360)))
    m.lathe([(2.0, 0), (1.2, 0.7), (0, 1.0)], seg=8, color="autumn_orange", smooth=False)


def corn_stalks(m):
    for i in range(6):
        a = math.radians(60 * i)
        x, y = 0.35 * math.cos(a), 0.35 * math.sin(a)
        blk(m, (0.2, 0.2, 6.0), (x, y, 3.0), "corn_husk", rot=(math.sin(a) * 6, -math.cos(a) * 6, 0))
        m.leaf(length=1.6, width=0.3, thick=0.04, color="corn_husk", loc=(x, y, 4.5), rot=(40, 0, 60 * i))
    m.torus(R=0.55, r=0.15, seg=8, color="rope", loc=(0, 0, 2.2))
    blk(m, (0.5, 0.4, 1.2), (0.7, -0.5, 1.8), "corn", bev=0.1)


def gourd_pile(m):
    for i, (x, y, c, s) in enumerate(((0, 0, "pumpkin", 1.0), (1.3, 0.3, "lemon", 0.6), (-1.2, 0.4, "cabbage", 0.7),
                                      (0.5, -1.1, "white", 0.6), (-0.6, -1.0, "pumpkin_dark", 0.5))):
        pumpkin(m, None, s, (x, y, 0))
    blk(m, (4.0, 3.4, 0.3), (0, 0, -0.1), "corn_husk")


def harvest_wreath(m):
    m.torus(R=1.4, r=0.4, seg=8, rseg=4, color="wood_mid", rot=(90, 0, 22.5))
    rnd = random.Random(4)
    for i in range(12):
        a = math.radians(30 * i)
        m.leaf(length=0.6, width=0.35, thick=0.05, color=rnd.choice(["autumn_orange", "autumn_red", "autumn_yellow"]),
               loc=(1.4 * math.cos(a), -0.35, 1.4 * math.sin(a)), rot=(90, 30 * i, 0))
    blk(m, (0.8, 0.3, 0.5), (0, -0.4, -1.4), "plastic_orange", bev=0.1)


reg("RoastTurkey", roast_turkey, "Harvest")
reg("Cornucopia", cornucopia, "Harvest")
reg("HarvestTable", harvest_table, "Harvest")
reg("LeafPile", leaf_pile, "Harvest")
reg("CornStalks", corn_stalks, "Harvest")
reg("GourdPile", gourd_pile, "Harvest")
reg("HarvestWreath", harvest_wreath, "Harvest", origin="center")


# ----------------------------------------------------------------------------
# Christmas
# ----------------------------------------------------------------------------
ORN = ["plastic_red", "gold", "plastic_blue", "silver", "plastic_purple"]


def xmas_tree(m, green=("pine", "pine_dark"), orn=ORN, snow=False, h=1.0, star="gold_light", lights=True):
    m.cyl(r=0.6 * h, h=1.6 * h, seg=6, color="bark", loc=(0, 0, 0.8 * h))
    rnd = random.Random(17)
    for i, (r, z, hh) in enumerate(((4.0, 1.4, 4.2), (3.2, 3.8, 3.8), (2.4, 6.0, 3.4), (1.5, 8.0, 3.0))):
        r, z, hh = r * h, z * h, hh * h
        col = (lambda c, n, z=z, g=green[i % 2]: "snow" if n.z > 0.45 and snow else g)
        m.lathe([(0, 0), (r, 0.3 * h), (r * 0.9, 0.7 * h), (0, hh)], seg=8, color=col, loc=(0, 0, z),
                rot=(0, 0, 22.5 * i), smooth=False)
        for k in range(6 - i):
            a = rnd.uniform(0, 2 * math.pi)
            rr = r * 0.8
            m.sphere(r=0.3 * h, seg=6, rings=4, round=True, color=orn[(i + k) % len(orn)],
                     loc=(rr * math.cos(a), rr * math.sin(a), z + 0.5 * h))
        if lights:
            for k in range(8):
                a = math.radians(45 * k + 20 * i)
                blk(m, (0.2 * h, 0.2 * h, 0.2 * h), (r * 0.72 * math.cos(a), r * 0.72 * math.sin(a), z + 1.0 * h),
                    ["neon_yellow", "neon_red", "neon_green", "neon_blue"][(k + i) % 4])
    m.prism(star_pts(0.9 * h, 0.4 * h, 5), depth=0.3 * h, color=star, rot=(90, 0, 0), loc=(0, 0, 11.4 * h))


def ornament(m, col, cap="gold"):
    m.sphere(r=1.0, seg=10, rings=8, round=True, color=lambda c, n: "white" if abs(c.z - 1.0) < 0.18 else col,
             loc=(0, 0, 1.0), cuts={"z": [0.82, 1.18]})
    m.cyl(r=0.3, h=0.35, seg=6, color=cap, loc=(0, 0, 2.1))
    m.torus(R=0.18, r=0.05, seg=6, color=cap, rot=(90, 0, 0), loc=(0, 0, 2.4))


def star_topper(m):
    m.prism(star_pts(1.4, 0.6, 5), depth=0.5, color="gold_light", rot=(90, 0, 0), loc=(0, 0, 2.2), bevel=0.08)
    m.cyl(r=0.3, h=1.0, seg=6, color="gold", loc=(0, 0, 0.5))


def santa_sleigh(m):
    m.box((4.4, 7.0, 2.6), color="plastic_red", loc=(0, 0, 2.6), bevel=0.4,
          deform=lambda co: co.__class__((co.x, co.y, co.z + (0.9 if co.y < -2.0 and co.z > 0 else 0))))
    blk(m, (3.8, 3.0, 0.6), (0, 1.0, 3.8), "leather_dark", bev=0.15)
    blk(m, (3.8, 0.5, 1.6), (0, 2.6, 4.4), "leather_dark", bev=0.15)
    blk(m, (4.6, 7.2, 0.3), (0, 0, 3.95), "gold", bev=0.05)
    with m.group("Runners"):
        for s in (-1, 1):
            m.tube([(s * 1.8, 3.4, 0.2), (s * 1.8, -3.0, 0.2), (s * 1.8, -4.4, 1.2), (s * 1.8, -4.0, 2.2)], [0.18] * 4,
                   seg=4, color="gold")
            for y in (-2.0, 2.0):
                blk(m, (0.2, 0.2, 1.2), (s * 1.8, y, 0.8), "gold")
    with m.group("Sack"):
        blk(m, (2.4, 2.4, 2.6), (0, 3.0, 5.0), "leather", bev=0.6)
        for i, c in enumerate(("plastic_green", "plastic_blue", "plastic_yellow")):
            blk(m, (0.9, 0.9, 0.9), (-0.6 + i * 0.6, 3.0, 6.4 + (i % 2) * 0.3), c, bev=0.08)


def santa_sack(m):
    blk(m, (2.6, 2.4, 2.8), (0, 0, 1.4), "leather", bev=0.7)
    m.cone(r=0.9, h=1.0, seg=6, color="leather", loc=(0, 0, 2.7))
    m.torus(R=0.5, r=0.1, seg=6, color="gold", loc=(0, 0, 3.0))
    for i, c in enumerate(("plastic_red", "plastic_green", "plastic_blue")):
        blk(m, (0.8, 0.8, 0.8), (-0.5 + i * 0.5, 0.2, 3.6 + (i % 2) * 0.3), c, bev=0.08)


def santa_hat(m, col="fabric_red"):
    m.cyl(r=1.3, h=0.6, seg=8, color="fur_white", loc=(0, 0, 0.3), bevel=0.2)
    m.lathe([(1.1, 0.5), (0.8, 1.6), (0.4, 2.4), (0, 2.8)], seg=8, color=col,
            deform=lambda co: co.__class__((co.x + 0.35 * max(0, co.z - 1.4) ** 1.5, co.y, co.z)))
    blk(m, (0.6, 0.6, 0.6), (0.95, 0, 2.6), "fur_white", bev=0.2)


def toy_soldier(m):
    for s in (-1, 1):
        blk(m, (0.6, 0.7, 2.4), (s * 0.4, 0, 1.2), "fabric_navy", bev=0.08)
        blk(m, (0.65, 0.9, 0.4), (s * 0.4, -0.1, 0.2), "black", bev=0.08)
    blk(m, (1.6, 1.0, 2.2), (0, 0, 3.5), "plastic_red", bev=0.12)
    blk(m, (1.62, 1.02, 0.3), (0, 0, 2.5), "gold")
    for s in (-1, 1):
        blk(m, (0.45, 0.5, 2.0), (s * 1.0, 0, 3.4), "plastic_red", bev=0.08)
        blk(m, (0.5, 0.4, 0.3), (s * 0.8, 0, 4.5), "gold")
    blk(m, (1.2, 1.0, 1.2), (0, 0, 5.2), "ceramic", bev=0.2)
    for s in (-1, 1):
        blk(m, (0.2, 0.1, 0.2), (s * 0.3, -0.52, 5.3), "eye_black")
        m.cyl(r=0.12, h=0.1, seg=6, color="plastic_pink", rot=(90, 0, 0), loc=(s * 0.4, -0.52, 5.0))
    m.cyl(r=0.65, h=1.6, seg=8, color="black", loc=(0, 0, 6.4))
    blk(m, (0.3, 0.1, 0.3), (0, -0.66, 6.2), "gold")
    blk(m, (0.2, 0.2, 2.6), (1.4, -0.3, 3.2), "wood_mid")


def sled(m):
    blk(m, (2.2, 5.0, 0.3), (0, 0, 1.2), "wood_light", bev=0.06)
    for k in range(4):
        blk(m, (2.2, 0.1, 0.32), (0, -1.8 + k * 1.2, 1.21), "wood_mid")
    for s in (-1, 1):
        m.tube([(s * 0.9, 2.4, 0.2), (s * 0.9, -2.0, 0.2), (s * 0.9, -2.9, 0.8), (s * 0.9, -2.6, 1.5)], [0.1] * 4, seg=4,
               color="plastic_red")
        for y in (-1.5, 1.5):
            blk(m, (0.12, 0.12, 1.0), (s * 0.9, y, 0.7), "plastic_red")
    m.tube([(-0.9, -2.6, 1.5), (0, -3.0, 1.4), (0.9, -2.6, 1.5)], [0.05] * 3, seg=4, color="rope")


def ice_skates(m):
    for s in (-1, 1):
        with m.at((s * 0.8, 0, 0)):
            blk(m, (0.1, 2.4, 0.2), (0, 0, 0.1), "silver")
            for y in (-0.8, 0.8):
                blk(m, (0.1, 0.1, 0.5), (0, y, 0.4), "silver")
            blk(m, (1.0, 2.2, 0.8), (0, 0, 1.0), "white", bev=0.2)
            blk(m, (1.0, 1.0, 1.4), (0, 0.6, 2.0), "white", bev=0.2)
            for k in range(3):
                blk(m, (0.8, 0.1, 0.08), (0, -0.05 + k * 0.001, 1.4 + k * 0.4), "fabric_red")


def candy_cane_lamp(m):
    stripes = lambda c, n: "plastic_red" if int((c.z + c.x) / 0.5) % 2 else "white"
    m.box((0.6, 0.6, 9.0), color=stripes, loc=(0, 0, 4.5), cuts={"z": 0.5})
    m.torus(R=1.0, r=0.3, seg=8, arc=180, color=stripes, rot=(90, 0, 0), loc=(1.0, 0, 9.0))
    blk(m, (1.2, 1.2, 0.8), (2.0, 0, 8.4), "gold", bev=0.1)
    blk(m, (0.9, 0.9, 0.6), (2.0, 0, 7.8), "glow")
    blk(m, (1.6, 1.6, 0.4), (0, 0, 0.2), "charcoal", bev=0.08)


def xmas_lights(m, L=12.0):
    m.tube([(-L / 2, 0, 6.0), (-L / 4, 0, 5.3), (0, 0, 5.1), (L / 4, 0, 5.3), (L / 2, 0, 6.0)], [0.04] * 5, seg=4,
           color="leaf_deep")
    for k in range(16):
        x = -L / 2 + 0.4 + k * (L - 0.8) / 15
        z = 6.0 - 0.9 * (1 - (2 * x / L) ** 2) - 0.25
        m.lathe([(0, 0), (0.14, 0.1), (0.14, 0.3), (0, 0.5)], seg=6, color=["neon_red", "neon_green", "neon_blue",
                                                                           "neon_yellow"][k % 4],
                loc=(x, 0, z - 0.2), rot=(180, 0, 0))
    for s in (-1, 1):
        m.cyl(r=0.12, h=6.3, seg=6, color="wood_mid", loc=(s * L / 2, 0, 3.15))


def mistletoe(m):
    blk(m, (0.06, 0.06, 2.0), (0, 0, 3.0), "fabric_red")
    blk(m, (0.8, 0.2, 0.4), (0, 0, 2.0), "fabric_red", bev=0.05)
    for i in range(6):
        m.leaf(length=0.9, width=0.4, thick=0.05, color="leaf", loc=(0, 0, 1.8), rot=(110, 0, 60 * i))
    for i in range(4):
        blk(m, (0.2, 0.2, 0.2), (0.2 * math.cos(i * 1.6), 0.2 * math.sin(i * 1.6), 1.6), "white", bev=0.06)


def advent_calendar(m):
    blk(m, (5.0, 0.4, 6.0), (0, 0, 3.0), "plastic_red", bev=0.1)
    for i in range(24):
        x, z = -1.9 + (i % 6) * 0.76, 5.0 - (i // 6) * 1.1
        blk(m, (0.6, 0.1, 0.8), (x, -0.22, z), ["plastic_green", "gold", "white"][i % 3], bev=0.03)
        text(m, str(i + 1), x, -0.28, z, px=0.06, depth=0.03, col="black")
    blk(m, (5.4, 0.6, 0.4), (0, 0, 6.1), "plastic_green", bev=0.05)
    blk(m, (5.4, 0.6, 0.4), (0, 0, 0.2), "plastic_green", bev=0.05)


def hot_cocoa(m):
    m.cyl(r=0.8, h=1.6, seg=8, color=lambda c, n: "plastic_red" if abs(c.z - 0.8) > 0.35 or n.z else "white",
          loc=(0, 0, 0.8), cuts={"z": [0.45, 1.15]})
    m.torus(R=0.45, r=0.12, seg=8, arc=200, color="plastic_red", rot=(90, 0, 90), loc=(0.85, 0, 0.8))
    m.cyl(r=0.72, h=0.05, seg=8, color="chocolate", loc=(0, 0, 1.55))
    for x, y in ((0.2, 0.1), (-0.25, -0.1), (0.05, -0.3)):
        blk(m, (0.28, 0.28, 0.28), (x, y, 1.7), "white", bev=0.06)


def cookies_and_milk(m):
    m.cyl(r=1.4, h=0.12, seg=8, color="ceramic", loc=(0, 0, 0.06))
    for i in range(4):
        a = math.radians(90 * i)
        m.cyl(r=0.45, h=0.14, seg=8, color="cookie", loc=(0.6 * math.cos(a), 0.6 * math.sin(a), 0.2 + 0.1 * (i % 2)))
    with m.at((1.8, 0.4, 0)):
        m.cyl(r=0.45, h=1.4, seg=8, color=lambda c, n: "milk" if c.z < 1.1 else "glass", loc=(0, 0, 0.7), cuts={"z": [1.1]})


def north_pole_sign(m):
    m.cyl(r=0.4, h=8.0, seg=8, color=lambda c, n: "plastic_red" if int((c.z + c.x) / 0.6) % 2 else "white",
          loc=(0, 0, 4.0), cuts={"z": 0.6})
    m.sphere(r=0.6, seg=8, rings=6, round=True, color="gold", loc=(0, 0, 8.4))
    blk(m, (5.6, 0.3, 1.2), (0.6, -0.5, 6.0), "wood_light", bev=0.08)
    text(m, "NORTH POLE", 0.6, -0.66, 6.0, px=0.12, depth=0.05, col="plastic_red")
    blk(m, (3.0, 3.0, 0.6), (0, 0, 0.3), "snow", bev=0.3)


def santa_chimney(m):
    blk(m, (3.0, 3.0, 5.0), (0, 0, 2.5), "brick", bev=0.08, cuts={"z": 0.5})
    blk(m, (3.4, 3.4, 0.6), (0, 0, 5.2), "snow", bev=0.2)
    for s in (-1, 1):
        blk(m, (0.6, 0.6, 1.6), (s * 0.45, 0, 5.9), "fabric_red", bev=0.1, rot=(0, s * 10, 0))
        blk(m, (0.65, 0.65, 0.3), (s * 0.45, 0, 5.4), "fur_white", bev=0.08)
        blk(m, (0.7, 1.1, 0.5), (s * 0.55, -0.2, 6.8), "black", bev=0.1)


def xmas_arch(m):
    for i in range(15):
        a = math.radians(180 * i / 14)
        with m.at((5.0 * math.cos(a), 0, 5.0 * math.sin(a) + 0.5)):
            blk(m, (1.1, 1.1, 1.1), (0, 0, 0), "pine" if i % 2 else "pine_dark", bev=0.2)
            if i % 2:
                blk(m, (0.35, 0.35, 0.35), (0, -0.55, 0), ["plastic_red", "gold", "plastic_blue"][i % 3], bev=0.1)
    for s in (-1, 1):
        blk(m, (1.2, 1.2, 1.0), (s * 5.0, 0, 0.5), "plastic_red", bev=0.1)
    blk(m, (1.2, 0.3, 0.8), (0, -0.6, 5.5), "plastic_red", bev=0.05)


def gingerbread_house(m, s=1.0):
    W, D, H = 8.0 * s, 7.0 * s, 5.0 * s
    blk(m, (W + 1, D + 1, 0.4 * s), (0, 0, 0.2 * s), "frosting_white", bev=0.1)
    blk(m, (W, D, H), (0, 0, 0.4 * s + H / 2), "cookie", bev=0.2)
    with m.group("Roof"):
        m.prism([(-(D / 2 + 0.8 * s), 0), (D / 2 + 0.8 * s, 0), (0, 3.6 * s)], depth=W + 0.8 * s,
                color=by_normal("frosting_white", "chocolate", thresh=0.95), rot=(90, 0, 90), loc=(0, 0, 0.4 * s + H),
                smooth=False)
        for k in range(6):
            x = -W / 2 + 0.7 * s + k * (W - 1.4 * s) / 5
            m.torus(R=0.35 * s, r=0.1 * s, seg=6, color=["candy_pink", "candy_green", "candy_blue"][k % 3], rot=(90, 0, 0),
                    loc=(x, -D / 2 - 0.5 * s, 0.4 * s + H + 0.2 * s))
    with m.group("Door"):
        blk(m, (1.6 * s, 0.2, 2.6 * s), (0, -D / 2 - 0.05, 0.4 * s + 1.3 * s), "chocolate", bev=0.1)
    for x in (-2.4 * s, 2.4 * s):
        blk(m, (1.4 * s, 0.2, 1.4 * s), (x, -D / 2 - 0.05, 0.4 * s + 2.8 * s), "lemon", bev=0.05)
        blk(m, (1.6 * s, 0.25, 0.2 * s), (x, -D / 2 - 0.1, 0.4 * s + 2.8 * s), "frosting_white")
        blk(m, (0.2 * s, 0.25, 1.6 * s), (x, -D / 2 - 0.1, 0.4 * s + 2.8 * s), "frosting_white")
    for x in (-3.0 * s, 3.0 * s):
        stripes = lambda c, n: "plastic_red" if int((c.z + c.x) / (0.4 * s)) % 2 else "white"
        m.box((0.4 * s, 0.4 * s, 3.0 * s), color=stripes, loc=(x, -D / 2 - 1.0 * s, 1.5 * s), cuts={"z": 0.4 * s})
    for k in range(7):
        m.sphere(r=0.25 * s, seg=6, rings=4, round=True, color=["candy_pink", "candy_green", "plastic_red"][k % 3],
                 loc=(-W / 2 + 0.6 * s + k * (W - 1.2 * s) / 6, -D / 2 - 0.15, 0.4 * s + H - 0.3 * s))


def santas_workshop(m):
    """Walk-in toy workshop: work benches, a toy conveyor, gift piles and Santa's desk."""
    W, D, H = 40.0, 32.0, 13.0
    b = storefront(m, W, D, H, ext=[(FL + 1.5, "stone_dark"), (None, "plank_red")], inn="wall_cream",
                   wains="wood_mid", trim="white", cornice="snow", flo=("wood_light", "wood", 1.0, True), frame="white",
                   sign_txt="TOY WORKSHOP", board="plastic_green", letters="white", px=0.5, sign_trim="plastic_red",
                   awning=("plastic_red", "white"), back_door=14.0, light_col="neon_yellow")
    zt, iy, ix = b["zt"], b["iy"], b["ix"]
    with m.group("Workbenches"):
        rnd = random.Random(31)
        for x in (-12.0, -4.0, 4.0):
            with m.at((x, -4.0, FL)):
                blk(m, (6.0, 3.0, 0.4), (0, 0, 3.2), "wood_mid", bev=0.05)
                for sx in (-2.6, 2.6):
                    for sy in (-1.2, 1.2):
                        blk(m, (0.4, 0.4, 3.0), (sx, sy, 1.5), "wood_dark")
                for k in range(4):
                    blk(m, (0.8, 0.8, 0.8), (-2.0 + k * 1.3, rnd.uniform(-0.6, 0.6), 3.8),
                        rnd.choice(["plastic_red", "plastic_blue", "plastic_yellow", "plastic_green"]), bev=0.15)
                blk(m, (0.3, 1.0, 0.2), (1.8, 0.8, 3.5), "iron")
    with m.group("ToyBelt"):
        blk(m, (30.0, 3.0, 0.4), (-1.0, 6.0, FL + 2.6), "rubber")
        for k in range(10):
            blk(m, (0.3, 3.2, 2.4), (-15.0 + k * 3.2, 6.0, FL + 1.2), "stainless")
        rnd = random.Random(32)
        for k in range(9):
            x = -14.0 + k * 3.1
            blk(m, (1.4, 1.4, 1.4), (x, 6.0, FL + 3.5), rnd.choice(["plastic_red", "plastic_green", "plastic_blue",
                                                                   "gold", "plastic_purple"]), bev=0.1)
            blk(m, (0.3, 1.45, 1.45), (x, 6.0, FL + 3.5), "gold")
    with m.group("Gifts"):
        rnd = random.Random(33)
        for k in range(10):
            s = rnd.uniform(1.0, 1.8)
            x, y = rnd.uniform(12.0, 17.5), rnd.uniform(-12.0, 2.0)
            blk(m, (s, s, s), (x, y, FL + s / 2), rnd.choice(["plastic_red", "plastic_green", "plastic_blue", "gold"]),
                bev=0.1)
            blk(m, (0.25, s + 0.05, s + 0.05), (x, y, FL + s / 2), "white")
    with m.group("Desk"):
        with m.at((-12.0, iy - 3.0, FL)):
            blk(m, (6.0, 3.0, 0.4), (0, 0, 3.2), "wood_dark", bev=0.08)
            blk(m, (6.0, 3.0, 3.0), (0, 0, 1.5), "wood_mid", bev=0.08)
            blk(m, (2.4, 1.6, 0.1), (0, -0.2, 3.45), "paper")
            with m.at((0, 2.4, 0)):
                blk(m, (2.6, 2.4, 0.8), (0, 0, 2.0), "fabric_red", bev=0.2)
                blk(m, (2.6, 0.6, 3.4), (0, 1.0, 3.4), "fabric_red", bev=0.2)
    with m.group("Tree"):
        with m.at((ix - 5.0, iy - 5.0, FL)):
            xmas_tree(m, h=0.9)


reg("ChristmasTreeDecorated", lambda m: xmas_tree(m), "Christmas")
reg("SnowyChristmasTree", lambda m: xmas_tree(m, snow=True), "Christmas")
reg("PinkChristmasTree", lambda m: xmas_tree(m, green=("frosting_pink", "candy_pink"), orn=("white", "silver", "gold"),
                                             star="white"), "Christmas")
reg("GoldChristmasTree", lambda m: xmas_tree(m, green=("gold", "gold_dark"), orn=("plastic_red", "white"),
                                             star="plastic_red"), "Christmas")
reg("RedOrnament", lambda m: ornament(m, "plastic_red"), "Christmas")
reg("GoldOrnament", lambda m: ornament(m, "gold", "silver"), "Christmas")
reg("BlueOrnament", lambda m: ornament(m, "plastic_blue"), "Christmas")
reg("StarTopper", star_topper, "Christmas")
reg("SantaSleigh", santa_sleigh, "Christmas", split=True)
reg("SantaSack", santa_sack, "Christmas")
reg("SantaHat", lambda m: santa_hat(m), "Christmas")
reg("ElfHat", lambda m: santa_hat(m, "plastic_green"), "Christmas")
reg("ToySoldier", toy_soldier, "Christmas")
reg("Sled", sled, "Christmas")
reg("IceSkates", ice_skates, "Christmas")
reg("CandyCaneLamp", candy_cane_lamp, "Christmas")
reg("ChristmasLights", lambda m: xmas_lights(m), "Christmas")
reg("Mistletoe", mistletoe, "Christmas")
reg("AdventCalendar", advent_calendar, "Christmas")
reg("HotCocoa", hot_cocoa, "Christmas")
reg("CookiesAndMilk", cookies_and_milk, "Christmas")
reg("NorthPoleSign", north_pole_sign, "Christmas")
reg("SantaChimney", santa_chimney, "Christmas")
reg("ChristmasArch", xmas_arch, "Christmas")
reg("GingerbreadHouse", lambda m: gingerbread_house(m), "Christmas", split=True)
reg("SantasWorkshop", santas_workshop, "Christmas", split=True, tags=["interior", "building"])


# ----------------------------------------------------------------------------
# Hanukkah, Diwali, Kwanzaa, Day of the Dead
# ----------------------------------------------------------------------------
def candle(m, x, y, z, h=1.2, col="white", flame=True):
    m.cyl(r=0.14, h=h, seg=6, color=col, loc=(x, y, z + h / 2))
    if flame:
        m.lathe([(0, 0), (0.12, 0.12), (0, 0.45)], seg=4, color="fire_light", loc=(x, y, z + h))


def menorah(m):
    blk(m, (2.4, 1.6, 0.4), (0, 0, 0.2), "gold", bev=0.1)
    blk(m, (0.3, 0.3, 3.0), (0, 0, 1.9), "gold")
    for i in range(4):
        r = 0.5 + i * 0.55
        m.torus(R=r, r=0.08, seg=8, arc=180, color="gold", rot=(90, 0, 0), loc=(0, 0, 3.4), scale=(1, 1, 1.2))
        for s in (-1, 1):
            blk(m, (0.3, 0.3, 0.2), (s * r, 0, 3.45), "gold")
            candle(m, s * r, 0, 3.55)
    blk(m, (0.35, 0.35, 0.3), (0, 0, 3.8), "gold")
    candle(m, 0, 0, 3.95)


def dreidel(m):
    blk(m, (1.6, 1.6, 1.8), (0, 0, 1.4), "plastic_blue", bev=0.1)
    m.pyramid(w=1.6, h=0.9, color="plastic_blue", loc=(0, 0, 0.5), rot=(180, 0, 0))
    m.cyl(r=0.15, h=0.9, seg=6, color="plastic_blue", loc=(0, 0, 2.7))
    for i in range(4):
        with m.at((0, 0, 1.4), 90 * i):
            blk(m, (0.8, 0.1, 0.8), (0, -0.82, 0), "silver")


def gelt(m):
    for i, (x, y, z) in enumerate(((0, 0, 0.1), (0.9, 0.3, 0.1), (-0.8, 0.4, 0.1), (0.2, -0.7, 0.1), (0.1, 0.1, 0.35),
                                   (0.5, -0.2, 0.6))):
        m.cyl(r=0.55, h=0.2, seg=8, color="gold", loc=(x, y, z), bevel=0.04)
    m.torus(R=0.35, r=0.06, seg=8, color="gold_dark", loc=(0.5, -0.2, 0.72))


def diya(m, x=0.0, y=0.0, z=0.0):
    with m.at((x, y, z)):
        m.lathe([(0, 0), (0.6, 0.1), (0.8, 0.35), (0.7, 0.4), (0.3, 0.25), (0, 0.25)], seg=8, color="clay")
        m.pyramid(w=0.3, h=0.4, color="clay", loc=(0.75, 0, 0.3), rot=(0, 70, 0))
        m.lathe([(0, 0), (0.12, 0.15), (0, 0.55)], seg=4, color="fire_light", loc=(0.8, 0, 0.45))


def diya_row(m):
    for i in range(5):
        diya(m, -3.0 + i * 1.5, 0, 0.0)
    m.box((8.0, 1.6, 0.1), color=lambda c, n: ["plastic_orange", "plastic_pink", "lemon"][int((c.x + 10) / 0.8) % 3],
          loc=(0, 0, -0.05), cuts={"x": 0.8})


def rangoli(m):
    cols = ["plastic_pink", "plastic_orange", "lemon", "plastic_green", "plastic_blue", "plastic_purple"]
    for i, r in enumerate((3.0, 2.4, 1.8, 1.2, 0.6)):
        m.cyl(r=r, h=0.08, seg=8, color=cols[i], loc=(0, 0, 0.04 + i * 0.02), rot=(0, 0, 22.5 * (i % 2)))
    for k in range(8):
        a = math.radians(45 * k)
        m.prism([(0, 0.2), (0.3, 0), (0, -0.2), (-0.3, 0)], depth=0.06, color=cols[(k + 2) % 6],
                loc=(2.5 * math.cos(a), 2.5 * math.sin(a), 0.14), rot=(0, 0, 45 * k), scale=2.0)


def sky_lantern(m):
    blk(m, (0.06, 0.06, 2.0), (0, 0, 6.0), "string")
    m.lathe([(0, 0), (1.2, 0.8), (1.2, 1.4), (0, 2.2)], seg=8, color="plastic_orange", loc=(0, 0, 3.0), rot=(0, 0, 22.5))
    for k in range(8):
        a = math.radians(45 * k + 22.5)
        blk(m, (0.1, 0.1, 1.4), (1.21 * math.cos(a), 1.21 * math.sin(a), 3.75), "lemon")
    blk(m, (0.5, 0.5, 0.5), (0, 0, 3.4), "glow")


def kinara(m):
    blk(m, (5.0, 1.2, 0.6), (0, 0, 0.3), "wood_dark", bev=0.1)
    for i in range(7):
        x = -2.1 + i * 0.7
        h = 0.6 + (3 - abs(i - 3)) * 0.2
        blk(m, (0.5, 0.5, h), (x, 0, 0.6 + h / 2), "wood_mid", bev=0.05)
        candle(m, x, 0, 0.6 + h, 1.4, "plastic_red" if i < 3 else ("black" if i == 3 else "plastic_green"))
    m.box((6.0, 2.4, 0.08), color=lambda c, n: ["plastic_red", "black", "plastic_green"][int((c.x + 10) / 0.5) % 3],
          loc=(0, 0, 0.04), cuts={"x": 0.5})


def sugar_skull(m):
    blk(m, (2.2, 1.9, 2.0), (0, 0, 1.5), "white", bev=0.4)
    blk(m, (1.6, 1.5, 0.9), (0, -0.1, 0.45), "white", bev=0.2)
    for s in (-1, 1):
        m.cyl(r=0.4, h=0.1, seg=8, color="plastic_blue", rot=(90, 0, 0), loc=(s * 0.5, -0.97, 1.6))
        m.cyl(r=0.2, h=0.12, seg=8, color="black", rot=(90, 0, 0), loc=(s * 0.5, -0.98, 1.6))
        for k in range(4):
            a = math.radians(90 * k)
            blk(m, (0.15, 0.08, 0.15), (s * 0.5 + 0.55 * math.cos(a), -0.98, 1.6 + 0.55 * math.sin(a)), "plastic_pink")
    m.prism([(-0.2, 0), (0.2, 0), (0, 0.3)], depth=0.1, color="black", rot=(90, 0, 0), loc=(0, -0.98, 1.0))
    blk(m, (1.0, 0.08, 0.08), (0, -0.87, 0.45), "black")
    for k in range(5):
        blk(m, (0.08, 0.08, 0.35), (-0.4 + k * 0.2, -0.87, 0.45), "black")
    for k, c in enumerate(("plastic_orange", "plastic_pink", "lemon")):
        blk(m, (0.35, 0.1, 0.35), (-0.5 + k * 0.5, -0.97, 2.25), c, bev=0.08)


def marigold_garland(m, L=10.0):
    m.tube([(-L / 2, 0, 5.0), (0, 0, 4.0), (L / 2, 0, 5.0)], [0.05] * 3, seg=4, color="leaf_dark")
    for k in range(14):
        x = -L / 2 + 0.4 + k * (L - 0.8) / 13
        z = 5.0 - 1.0 * (1 - (2 * x / L) ** 2) - 0.2
        blk(m, (0.5, 0.5, 0.5), (x, 0, z), "plastic_orange" if k % 2 else "lemon", bev=0.15)
    for s in (-1, 1):
        m.cyl(r=0.12, h=5.3, seg=6, color="wood_mid", loc=(s * L / 2, 0, 2.65))


reg("Menorah", menorah, "Hanukkah")
reg("Dreidel", dreidel, "Hanukkah")
reg("GeltCoins", gelt, "Hanukkah")
reg("DiyaLamp", lambda m: diya(m), "Diwali")
reg("DiyaRow", diya_row, "Diwali")
reg("Rangoli", rangoli, "Diwali")
reg("SkyLantern", sky_lantern, "Diwali")
reg("Kinara", kinara, "Kwanzaa")
reg("SugarSkull", sugar_skull, "DayOfTheDead")
reg("MarigoldGarland", lambda m: marigold_garland(m), "DayOfTheDead")


# ----------------------------------------------------------------------------
# winter
# ----------------------------------------------------------------------------
def snow_fort(m):
    for k in range(9):
        a = math.radians(-30 + k * 30)
        for z in range(3):
            if k in (3, 4, 5) and z < 2:
                continue
            blk(m, (1.4, 1.4, 1.0), (4.0 * math.cos(a) , 4.0 * math.sin(a) - 2.0, 0.5 + z * 1.0), "snow", bev=0.2,
                rot=(0, 0, math.degrees(a)))
    for i in range(4):
        m.sphere(r=0.5, seg=6, rings=4, round=True, color="snow", loc=(-1.0 + (i % 2) * 0.9, 0.2 + (i // 2) * 0.8,
                                                                      0.5 + (i // 3) * 0.7))


def snowball_pile(m):
    for layer, (n, z) in enumerate(((3, 0.55), (2, 1.45), (1, 2.35))):
        for i in range(n):
            for j in range(n):
                m.sphere(r=0.55, seg=8, rings=6, round=True, color="snow",
                         loc=((i - (n - 1) / 2) * 1.0, (j - (n - 1) / 2) * 1.0, z))


def snowman_decor(m):
    for z, r in ((1.6, 1.6), (4.2, 1.2), (6.2, 0.9)):
        m.sphere(r=r, seg=10, rings=8, round=True, color="snow", loc=(0, 0, z))
    for s in (-1, 1):
        blk(m, (0.2, 0.1, 0.2), (s * 0.35, -0.85, 6.4), "eye_black")
        m.tube([(s * 1.1, 0, 4.4), (s * 2.2, 0, 5.2), (s * 2.5, 0, 5.8)], [0.08, 0.06, 0.04], seg=4, color="bark")
    m.cone(r=0.16, h=0.8, seg=6, color="carrot", rot=(90, 0, 0), loc=(0, -0.85, 6.1))
    m.torus(R=0.95, r=0.2, seg=8, color="fabric_red", loc=(0, 0, 5.3))
    blk(m, (0.4, 0.3, 1.2), (0.6, -0.85, 4.8), "fabric_red", bev=0.05)
    m.cyl(r=1.0, h=0.15, seg=8, color="black", loc=(0, 0, 7.0))
    m.cyl(r=0.65, h=1.1, seg=8, color="black", loc=(0, 0, 7.6))
    for z in (3.8, 4.4, 5.0):
        blk(m, (0.2, 0.1, 0.2), (0, -1.2 if z < 4.5 else -1.1, z - 0.2), "coal")


reg("SnowFort", snow_fort, "Winter")
reg("SnowballPile", snowball_pile, "Winter")
reg("SnowmanDecor", snowman_decor, "Winter")
