"""Weapons: tiered melee / ranged / magic weapons plus toy & special weapons.

Held weapons stand upright (+Z), blade/head at the top, origin on the grip.
"""
import math

from studlib.geo import by_height, circle_pts, star_pts
from studlib.registry import add, asset
from studlib.tiers import ORDER, TIERS, paint, solid

from tools import handle

CAT = "Weapons"
GEM_TIERS = ("Gold", "Diamond", "Emerald", "Ruby", "Rainbow")


def sword(m, T, tier):
    handle(m, T, -0.65, 0.45, r=0.1, grip=(-0.52, 0.38))
    m.sphere(r=0.17, seg=8, rings=6, color=T["accent"], loc=(0, 0, -0.72))
    m.box((1.15, 0.3, 0.2), bevel=0.06, color=T["accent"], loc=(0, 0, 0.52))
    for s in (-1, 1):
        m.cone(r=0.12, h=0.2, seg=6, color=T["accent"], rot=(0, s * 90, 0), loc=(s * 0.56, 0, 0.52), smooth=False)
    blade = [(0, 0, 0.6), (0, 0, 1.0), (0, 0, 3.25), (0, 0, 3.95)]
    m.tube(blade, [(0.26, 0.075), (0.28, 0.08), (0.25, 0.07), 0], seg=4, up=(0, 1, 0), smooth=False,
           **paint(T, "main", "z", 0.6, 3.95))
    m.box((0.06, 0.166, 2.3), color=T["dark"], loc=(0, 0, 1.95), smooth=False)
    if tier in GEM_TIERS:
        m.gem(r=0.1, h=0.1, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.2, 0.52))


def katana(m, T, tier):
    handle(m, T, -0.9, 0.8, r=0.09, grip=(-0.8, 0.7), pommel=True)
    m.cyl(r=0.32, h=0.07, seg=10, color=T["accent"], loc=(0, 0, 0.84), bevel=0.02, bseg=1)
    m.box((0.14, 0.12, 0.14), color=T["dark"], loc=(0, 0, 0.94))
    pts, rad = [], []
    n = 8
    for i in range(n + 1):
        t = i / n
        pts.append((0, 0.3 * t * t, 0.9 + 3.4 * t))
        rad.append((0.12 * (1 - 0.25 * t), 0.045) if i < n else 0)
    m.tube(pts, rad, seg=4, up=(0, 1, 0), smooth=False, **paint(T, "main", "z", 0.9, 4.3))
    pts2 = [(p[0], p[1] - 0.035, p[2]) for p in pts[:-2]]
    m.tube(pts2, [(0.06, 0.03)] * len(pts2), seg=4, up=(0, 1, 0), smooth=False, color=solid(T, "light", "white"))


def dagger(m, T, tier):
    handle(m, T, -0.5, 0.3, r=0.08, grip=(-0.42, 0.25))
    m.sphere(r=0.12, seg=8, rings=6, color=T["accent"], loc=(0, 0, -0.56))
    m.box((0.62, 0.22, 0.14), bevel=0.05, color=T["accent"], loc=(0, 0, 0.36))
    m.tube([(0, 0, 0.42), (0, 0, 0.7), (0, 0, 1.5), (0, 0, 1.95)], [(0.18, 0.06), (0.2, 0.065), (0.16, 0.05), 0],
           seg=4, up=(0, 1, 0), smooth=False, **paint(T, "main", "z", 0.42, 1.95))
    if tier in GEM_TIERS:
        m.gem(r=0.07, h=0.07, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.13, 0.36))


def battle_axe(m, T, tier):
    top = 3.5
    handle(m, T, 0.0, top, r=0.1, grip=(0.25, 1.2))
    blade = [(0.12, -0.3), (0.5, -0.5), (0.92, -0.78), (1.06, -0.4), (1.1, 0.0), (1.06, 0.4), (0.92, 0.78),
             (0.5, 0.5), (0.12, 0.3)]
    thin = lambda co: co.__class__((co.x, co.y, co.z * (1.0 - 0.5 * max(0.0, abs(co.x) - 0.3) / 0.8)))
    m.prism(blade, depth=0.18, bevel=0.03, bseg=1, rot=(90, 0, 0), loc=(0, 0, top - 0.5), mirror=True,
            deform=thin, **paint(T, "main", "x", -1.1, 1.1))
    m.box((0.34, 0.34, 0.8), bevel=0.06, color=T["accent"], loc=(0, 0, top - 0.5))
    m.cone(r=0.13, h=0.5, seg=6, color=T["dark"], loc=(0, 0, top - 0.05), smooth=False)


def spear(m, T, tier):
    top = 5.3
    handle(m, T, 0.0, top, r=0.08, grip=(1.3, 2.3))
    m.cyl(r=0.12, h=0.3, seg=8, color=T["accent"], loc=(0, 0, top), bevel=0.03)
    m.tube([(0, 0, top + 0.1), (0, 0, top + 0.45), (0, 0, top + 0.9), (0, 0, top + 1.4)],
           [(0.1, 0.05), (0.28, 0.08), (0.18, 0.06), 0], seg=4, up=(0, 1, 0), smooth=False,
           **paint(T, "main", "z", top + 0.1, top + 1.4))
    for a in range(0, 360, 60):
        m.cone(r=0.05, h=0.5, seg=4, color="fabric_red" if tier != "Rainbow" else "rb_pink",
               rot=(180 - 12, 0, a), loc=(0, 0, top - 0.1), smooth=False)


def war_hammer(m, T, tier):
    top = 3.2
    handle(m, T, 0.0, top, r=0.1, grip=(0.25, 1.1))
    m.box((1.35, 0.72, 0.72), bevel=0.1, bseg=2, loc=(0, 0, top + 0.2), **paint(T, "main", "x", -0.68, 0.68))
    for s in (-1, 1):
        m.box((0.14, 0.8, 0.8), bevel=0.05, color=T["dark"], loc=(s * 0.55, 0, top + 0.2))
        m.box((0.1, 0.5, 0.5), bevel=0.04, color=T["light"] if T["light"] != "white" else "rb_yellow",
              loc=(s * 0.7, 0, top + 0.2))
    m.box((0.4, 0.78, 0.78), bevel=0.05, color=T["accent"], loc=(0, 0, top + 0.2))
    m.cone(r=0.14, h=0.45, seg=6, color=T["accent"], loc=(0, 0, top + 0.56), smooth=False)


def bow(m, T, tier):
    pts, rad = [], []
    n = 12
    for i in range(n + 1):
        t = i / n
        z = -2.0 + 4.0 * t
        y = -0.55 * math.cos(math.pi * (t - 0.5)) + 0.08 * math.cos(math.pi * (t - 0.5)) ** 8
        tip = abs(2 * t - 1)
        y += 0.12 * tip ** 6
        pts.append((0, y, z))
        rad.append((0.08 - 0.04 * tip, 0.1 - 0.05 * tip))
    m.tube(pts, rad, seg=6, up=(1, 0, 0), **paint(T, "main", "z", -2.0, 2.0))
    top, bot = pts[-1], pts[0]
    m.tube([(0, top[1] + 0.02, top[2] - 0.05), (0, bot[1] + 0.02, bot[2] + 0.05)], [0.022, 0.022], seg=4,
           color="lightgray", smooth=False)
    m.cyl(r=0.13, h=0.7, seg=8, color=T["grip"], loc=(0, pts[6][1], 0), scale=(1, 0.8, 1), bevel=0.03)
    for p in (top, bot):
        m.sphere(r=0.08, seg=6, rings=4, color=T["accent"], loc=p)


def staff(m, T, tier):
    top = 4.2
    m.cyl(r=0.09, r2=0.11, h=top, seg=8, color=T["handle"], loc=(0, 0, top / 2))
    for z in (0.1, 1.4, 2.6, top - 0.1):
        m.cyl(r=0.14, h=0.12, seg=8, color=T["accent"], loc=(0, 0, z), bevel=0.03)
    for i in range(4):
        a = math.radians(90 * i + 45)
        c, s = math.cos(a), math.sin(a)
        m.tube([(c * 0.08, s * 0.08, top), (c * 0.32, s * 0.32, top + 0.35), (c * 0.2, s * 0.2, top + 0.75),
                (c * 0.06, s * 0.06, top + 0.9)], [0.05, 0.05, 0.04, 0.0], seg=5, color=T["accent"])
    orb = paint(T, "gem", "z", top + 0.3, top + 0.82)
    m.ico(r=0.28, sub=1, loc=(0, 0, top + 0.56), **orb)
    m.ico(r=0.1, sub=0, color="glow" if tier != "Wood" else "wood_pale", loc=(0, 0, top + 0.56))


def shield(m, T, tier):
    prof = [(0, 0.2), (0.45, 0.18), (0.85, 0.1), (1.1, 0.0), (1.1, -0.06), (0, -0.06)]
    m.lathe(prof, seg=16, rot=(90, 0, 0), loc=(0, 0, 0), **paint(T, "main", "x", -1.1, 1.1))
    m.torus(R=1.1, r=0.08, seg=16, rseg=5, color=T["accent"], rot=(90, 0, 0), loc=(0, 0.0, 0))
    m.sphere(r=0.26, seg=10, rings=6, color=T["accent"], loc=(0, -0.2, 0), scale=(1, 0.7, 1))
    for a in (0, 90):
        m.box((2.0, 0.06, 0.16), color=T["dark"], rot=(0, a, 0), loc=(0, -0.16, 0))
    for a in range(0, 360, 45):
        r = 0.95
        m.sphere(r=0.05, seg=6, rings=4, color=T["accent"],
                 loc=(math.cos(math.radians(a)) * r, -0.1, math.sin(math.radians(a)) * r))
    m.box((0.2, 0.3, 0.9), bevel=0.06, color=T["grip"], loc=(0, 0.25, 0))
    if tier in GEM_TIERS:
        m.gem(r=0.14, h=0.14, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.34, 0))


TIERED = [("Sword", sword, (0, 0, 0)), ("Katana", katana, (0, 0, 0)), ("Dagger", dagger, (0, 0, 0)),
          ("BattleAxe", battle_axe, (0, 0, 0.7)), ("Spear", spear, (0, 0, 1.8)),
          ("WarHammer", war_hammer, (0, 0, 0.6)), ("Bow", bow, (0, 0, 0)), ("Staff", staff, (0, 0, 1.6)),
          ("Shield", shield, (0, 0, 0))]

for _name, _fn, _grip in TIERED:
    for _tier in ORDER:
        add(f"{_tier}{_name}", CAT, (lambda m, f=_fn, t=_tier: f(m, TIERS[t], t)), sub=_name,
            origin=_grip, tags=["tiered", _tier.lower()])


# --- special weapons -----------------------------------------------------------------
@asset("Arrow", CAT, sub="Special", origin="center")
def arrow(m):
    m.cyl(r=0.035, h=2.4, seg=6, color="wood", loc=(0, 0, 1.2))
    m.tube([(0, 0, 2.35), (0, 0, 2.55), (0, 0, 2.75)], [(0.1, 0.03), (0.12, 0.035), 0], seg=4, up=(0, 1, 0),
           smooth=False, color="iron")
    for a in (0, 120, 240):
        m.prism([(0, 0), (0.16, 0.08), (0.16, 0.45), (0, 0.5)], depth=0.02, color="fabric_red", rot=(90, 0, a),
                loc=(0, 0, 0.05))


@asset("Slingshot", CAT, sub="Special", origin=(0, 0, 0.4))
def slingshot(m):
    m.tube([(0, 0, 0), (0, 0, 0.8)], [0.09, 0.09], seg=8, color="wood_mid")
    for s in (-1, 1):
        m.tube([(0, 0, 0.75), (s * 0.3, 0, 1.2), (s * 0.35, 0, 1.55)], [0.08, 0.07, 0.07], seg=8, color="wood_mid",
               mirror=False)
    m.tube([(-0.35, 0, 1.5), (0, 0.25, 1.4), (0.35, 0, 1.5)], [0.025, 0.025, 0.025], seg=4, color="plastic_red")
    m.box((0.2, 0.08, 0.14), bevel=0.03, color="leather", loc=(0, 0.25, 1.4))
    m.cyl(r=0.11, h=0.5, seg=8, color="leather", loc=(0, 0, 0.35), bevel=0.02)


@asset("Boomerang", CAT, sub="Special", origin="center")
def boomerang(m):
    pts = [(-0.95, -0.45, 0.06), (-0.5, -0.05, 0.06), (0, 0.25, 0.06), (0.5, -0.05, 0.06), (0.95, -0.45, 0.06)]
    m.tube(pts, [(0.14, 0.05), (0.19, 0.06), (0.22, 0.06), (0.19, 0.06), (0.14, 0.05)], seg=8, up=(0, 0, 1),
           color=lambda c, n: "plastic_orange" if abs(c.x) < 0.55 else "plastic_blue", cuts={"x": [-0.55, 0.55]})


@asset("Shuriken", CAT, sub="Special", origin="center")
def shuriken(m):
    m.prism(star_pts(0.6, 0.18, 4, start=45), depth=0.06, color="steel", bevel=0.02, bseg=1, rot=(90, 0, 0),
            smooth=False)
    m.cyl(r=0.1, h=0.1, seg=8, color="charcoal", rot=(90, 0, 0))


@asset("Bomb", CAT, sub="Special")
def bomb(m):
    m.sphere(r=0.6, seg=14, rings=10, color="charcoal", loc=(0, 0, 0.6))
    m.cyl(r=0.2, h=0.2, seg=10, color="iron_dark", loc=(0, 0, 1.22))
    m.tube([(0, 0, 1.3), (0.05, 0, 1.45), (0.18, 0, 1.55)], [0.04, 0.035, 0.03], seg=5, color="rope")
    m.ico(r=0.1, sub=0, color="fire", loc=(0.22, 0, 1.6))
    m.sphere(r=0.12, seg=6, rings=4, color="white", loc=(-0.25, -0.45, 0.95), scale=(1, 0.5, 1.4), rot=(0, 30, 0))


@asset("Blaster", CAT, sub="Special", origin=(0, 0, 0.3))
def blaster(m):
    m.box((0.3, 0.45, 0.8), bevel=0.1, color="plastic_black", loc=(0, 0.25, 0.35), rot=(-15, 0, 0))
    m.box((0.4, 1.3, 0.45), bevel=0.14, color="plastic_blue", loc=(0, -0.2, 0.9))
    m.cyl(r=0.16, h=0.6, seg=10, color="plastic_white", rot=(90, 0, 0), loc=(0, -1.0, 0.95))
    m.cyl(r=0.1, h=0.05, seg=10, color="neon_green", rot=(90, 0, 0), loc=(0, -1.31, 0.95))
    for y in (-0.55, -0.3, -0.05):
        m.torus(R=0.23, r=0.03, seg=10, rseg=4, color="neon_green", rot=(90, 0, 0), loc=(0, y, 0.9),
                scale=(0.95, 1, 1.1))
    m.box((0.1, 0.25, 0.2), color="plastic_black", loc=(0, 0.0, 0.55))
    m.box((0.14, 0.3, 0.18), bevel=0.04, color="plastic_orange", loc=(0, -0.2, 1.2))


@asset("MagicWand", CAT, sub="Special", origin=(0, 0, 0.3))
def magic_wand(m):
    m.cyl(r=0.05, r2=0.035, h=1.5, seg=6, color="charcoal", loc=(0, 0, 0.75))
    m.cyl(r=0.065, h=0.4, seg=6, color="white", loc=(0, 0, 0.2))
    m.prism(star_pts(0.3, 0.13, 5), depth=0.1, color="gold", bevel=0.03, bseg=1, rot=(90, 0, 0),
            loc=(0, 0, 1.7))


@asset("Trident", CAT, sub="Special", origin=(0, 0, 1.8))
def trident(m):
    m.cyl(r=0.08, h=4.6, seg=8, color="gold_dark", loc=(0, 0, 2.3))
    m.box((1.0, 0.14, 0.14), bevel=0.04, color="gold", loc=(0, 0, 4.7))
    for x in (-0.42, 0.0, 0.42):
        top = 5.6 if x == 0 else 5.3
        m.tube([(x, 0, 4.7), (x, 0, top - 0.3), (x, 0, top)], [(0.06, 0.04), (0.08, 0.05), 0], seg=4, up=(0, 1, 0),
               smooth=False, color="gold")
    m.sphere(r=0.12, seg=8, rings=6, color="diamond", loc=(0, 0, 4.7))


@asset("Crossbow", CAT, sub="Special", origin=(0, 0.3, 0.3))
def crossbow(m):
    m.box((0.2, 1.6, 0.2), bevel=0.05, color="wood", loc=(0, 0, 0.5))
    m.box((0.18, 0.4, 0.5), bevel=0.06, color="wood_dark", loc=(0, 0.6, 0.3), rot=(20, 0, 0))
    pts = [(math.sin(math.radians(a)) * 0.9, -0.7 + (1 - math.cos(math.radians(a))) * 0.4, 0.55)
           for a in range(-70, 71, 20)]
    m.tube(pts, [0.05] * len(pts), seg=6, color="iron_dark")
    m.tube([pts[0], (0, -0.1, 0.62), pts[-1]], [0.012] * 3, seg=3, color="string", smooth=False)
    m.cyl(r=0.03, h=1.0, seg=5, color="iron", rot=(90, 0, 0), loc=(0, -0.4, 0.64))
