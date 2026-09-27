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
    m.sphere(r=0.17, seg=8, rings=6, color=T["accent"], loc=(0, 0, -0.74))
    m.box((0.2, 0.2, 0.12), color=T["dark"], bevel=0.03, loc=(0, 0, -0.58))
    # layered cross-guard
    m.box((1.2, 0.3, 0.2), bevel=0.06, color=T["accent"], loc=(0, 0, 0.52))
    m.box((0.46, 0.36, 0.3), bevel=0.07, color=T["dark"], loc=(0, 0, 0.55))
    for s in (-1, 1):
        m.box((0.2, 0.34, 0.3), bevel=0.05, color=T["dark"], loc=(s * 0.62, 0, 0.58), rot=(0, s * -20, 0))
        m.pyramid(w=0.16, h=0.22, color=T["accent"], loc=(s * 0.7, 0, 0.7), rot=(0, s * 25, 0))
    blade = [(0, 0, 0.62), (0, 0, 1.0), (0, 0, 3.25), (0, 0, 3.95)]
    m.tube(blade, [(0.26, 0.075), (0.28, 0.08), (0.25, 0.07), 0], seg=4, up=(0, 1, 0), smooth=False,
           **paint(T, "main", "z", 0.6, 3.95))
    # bright edges along both sides of the blade
    edge = solid(T, "light", "white")
    for s in (-1, 1):
        m.tube([(s * 0.27, 0, 0.95), (s * 0.245, 0, 3.25), (s * 0.05, 0, 3.86)], [0.03, 0.03, 0.02], seg=4, color=edge)
    m.box((0.06, 0.166, 2.3), color=T["dark"], loc=(0, 0, 1.95), smooth=False)
    m.box((0.3, 0.17, 0.3), color=T["dark"], bevel=0.04, loc=(0, 0, 0.78))
    if tier in GEM_TIERS:
        m.gem(r=0.1, h=0.1, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.2, 0.55))
        m.gem(r=0.08, h=0.08, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.13, -0.74))


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


def greatsword(m, T, tier):
    handle(m, T, -1.1, 0.55, r=0.11, grip=(-0.95, 0.45))
    m.box((0.34, 0.34, 0.3), bevel=0.08, color=T["accent"], loc=(0, 0, -1.2))
    m.pyramid(w=0.2, h=0.25, color=T["accent"], loc=(0, 0, -1.47), rot=(180, 0, 0))
    m.box((0.6, 0.4, 0.34), bevel=0.08, color=T["dark"], loc=(0, 0, 0.66))
    for s in (-1, 1):
        m.tube([(s * 0.25, 0, 0.66), (s * 0.8, 0, 0.62), (s * 1.05, 0, 0.35)], [0.12, 0.1, 0.06], seg=4,
               color=T["accent"])
        m.box((0.16, 0.44, 0.16), bevel=0.04, color=T["dark"], loc=(s * 1.05, 0, 0.3))
    m.box((0.5, 0.2, 0.5), bevel=0.05, color=T["dark"], loc=(0, 0, 1.05))
    m.tube([(0, 0, 0.8), (0, 0, 1.4), (0, 0, 4.6), (0, 0, 5.4)], [(0.36, 0.09), (0.38, 0.1), (0.33, 0.09), 0], seg=4,
           up=(0, 1, 0), smooth=False, **paint(T, "main", "z", 0.8, 5.4))
    edge = solid(T, "light", "white")
    for s in (-1, 1):
        m.tube([(s * 0.37, 0, 1.3), (s * 0.33, 0, 4.6), (s * 0.06, 0, 5.3)], [0.035, 0.035, 0.02], seg=4, color=edge)
    m.box((0.08, 0.205, 3.2), color=T["dark"], loc=(0, 0, 2.9), smooth=False)
    for z in (1.6, 2.2, 2.8):
        m.box((0.12, 0.21, 0.12), color=T["accent"], bevel=0.02, loc=(0, 0, z))
    if tier in GEM_TIERS:
        m.gem(r=0.14, h=0.14, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.24, 0.66))


def scimitar(m, T, tier):
    handle(m, T, -0.6, 0.4, r=0.09, grip=(-0.5, 0.33))
    m.tube([(0, 0, -0.62), (0, -0.2, -0.75), (0, -0.28, -0.62)], [0.08, 0.07, 0.06], seg=4, color=T["accent"])
    m.box((0.9, 0.24, 0.16), bevel=0.05, color=T["accent"], loc=(0, 0, 0.46))
    for s in (-1, 1):
        m.box((0.16, 0.26, 0.26), bevel=0.05, color=T["dark"], loc=(s * 0.45, 0, 0.5))
    pts, rad = [], []
    n = 7
    for i in range(n + 1):
        t = i / n
        pts.append((0.35 * t * t, 0, 0.55 + 3.0 * t))
        w = 0.15 + 0.12 * math.sin(math.pi * min(1.0, t * 1.15)) if i < n else 0
        rad.append((w, 0.06) if i < n else 0)
    m.tube(pts, rad, seg=4, up=(0, 1, 0), smooth=False, **paint(T, "main", "z", 0.55, 3.55))
    m.tube([(p[0] - rad[i][0] * 0.95, 0, p[2]) for i, p in enumerate(pts[:-1])], [0.03] * n, seg=4,
           color=solid(T, "light", "white"))
    if tier in GEM_TIERS:
        m.gem(r=0.08, h=0.08, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.15, 0.46))


def mace(m, T, tier):
    top = 2.6
    handle(m, T, 0.0, top, r=0.1, grip=(0.2, 1.0))
    m.box((0.7, 0.7, 0.7), bevel=0.14, loc=(0, 0, top + 0.35), **paint(T, "main", "z", top, top + 0.7))
    for rx, ry in ((0, 0), (90, 0), (-90, 0), (0, 90), (0, -90), (180, 0)):
        m.pyramid(w=0.26, h=0.38, color=solid(T, "light", "white"), loc=(0, 0, top + 0.35), rot=(rx, ry, 0),
                  pre=None, deform=lambda co: co.__class__((co.x, co.y, co.z + 0.33)))
    for a in range(4):
        m.pyramid(w=0.2, h=0.3, color=T["dark"], loc=(0, 0, top + 0.35), rot=(0, 45, 90 * a + 45),
                  deform=lambda co: co.__class__((co.x, co.y, co.z + 0.4)))
    m.cyl(r=0.16, h=0.25, seg=8, color=T["accent"], loc=(0, 0, top - 0.05), bevel=0.04)
    if tier in GEM_TIERS:
        m.gem(r=0.1, h=0.1, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.36, top + 0.35))


def halberd(m, T, tier):
    top = 5.0
    handle(m, T, 0.0, top, r=0.08, grip=(1.3, 2.3))
    for z in (2.6, 3.6, top - 0.2):
        m.box((0.22, 0.22, 0.16), bevel=0.04, color=T["accent"], loc=(0, 0, z))
    blade = [(0.08, -0.2), (0.4, -0.35), (0.95, -0.6), (1.0, 0.0), (0.95, 0.45), (0.4, 0.3), (0.08, 0.25)]
    m.prism(blade, depth=0.1, bevel=0.03, rot=(90, 0, 0), loc=(0, 0, top - 0.3), **paint(T, "main", "x", 0, 1.0))
    m.prism([(-0.08, -0.12), (-0.55, 0.0), (-0.08, 0.12)], depth=0.1, color=T["dark"], rot=(90, 0, 0),
            loc=(0, 0, top - 0.25))
    m.tube([(0, 0, top), (0, 0, top + 0.4), (0, 0, top + 1.2)], [(0.12, 0.05), (0.16, 0.06), 0], seg=4, up=(0, 1, 0),
           smooth=False, **paint(T, "main", "z", top, top + 1.2))
    m.box((0.3, 0.26, 0.4), bevel=0.05, color=T["dark"], loc=(0, 0, top - 0.25))


TIERED = [("Sword", sword, (0, 0, 0)), ("Greatsword", greatsword, (0, 0, 0)), ("Scimitar", scimitar, (0, 0, 0)),
          ("Mace", mace, (0, 0, 0.5)), ("Halberd", halberd, (0, 0, 1.8)), ("Katana", katana, (0, 0, 0)), ("Dagger", dagger, (0, 0, 0)),
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


# --- legendary elemental weapons -------------------------------------------------------
ELEMENTS = {
    "Flame": dict(main="lava", edge="fire_light", guard="obsidian", accent="gold", gem="fire", deco="fire",
                  grip="rug_red"),
    "Frost": dict(main="ice", edge="white", guard="diamond_dark", accent="silver", gem="diamond", deco="diamond_light",
                  grip="fabric_navy"),
    "Thunder": dict(main="plastic_yellow", edge="white", guard="sapphire", accent="gold", gem="neon_blue",
                    deco="neon_blue", grip="fabric_navy"),
    "Shadow": dict(main="obsidian", edge="amethyst", guard="black", accent="amethyst_dark", gem="neon_pink",
                   deco="amethyst", grip="charcoal"),
    "Nature": dict(main="leaf", edge="leaf_light", guard="bark", accent="wood_light", gem="emerald", deco="leaf_dark",
                   grip="bark_dark"),
    "Crystal": dict(main="crystal_pink", edge="white", guard="amethyst", accent="silver", gem="diamond_light",
                    deco="amethyst", grip="fabric_purple"),
}


def legend_sword(m, name, E):
    T = dict(handle=E["guard"], grip=E["grip"], grip2=E["accent"], accent=E["accent"])
    handle(m, T, -0.75, 0.45, r=0.11, grip=(-0.62, 0.38))
    m.gem(r=0.16, h=0.2, seg=6, color=E["gem"], loc=(0, 0, -0.95))
    m.box((1.3, 0.34, 0.24), bevel=0.07, color=E["guard"], loc=(0, 0, 0.55))
    m.box((0.5, 0.4, 0.4), bevel=0.08, color=E["accent"], loc=(0, 0, 0.58))
    m.gem(r=0.12, h=0.12, seg=6, color=E["gem"], rot=(90, 0, 0), loc=(0, -0.22, 0.58))
    m.tube([(0, 0, 0.7), (0, 0, 1.1), (0, 0, 3.6), (0, 0, 4.4)], [(0.3, 0.08), (0.32, 0.09), (0.28, 0.08), 0], seg=4,
           up=(0, 1, 0), smooth=False, color=E["main"])
    for s in (-1, 1):
        m.tube([(s * 0.31, 0, 1.05), (s * 0.28, 0, 3.6), (s * 0.05, 0, 4.3)], [0.035, 0.035, 0.02], seg=4, color=E["edge"])
    m.box((0.07, 0.186, 2.6), color=E["deco"], loc=(0, 0, 2.2), smooth=False)
    if name == "Flame":
        for s in (-1, 1):
            for k, z in enumerate((0.75, 1.1)):
                m.pyramid(w=0.2, h=0.5 - 0.1 * k, color="fire" if k else "fire_light", loc=(s * (0.55 - 0.1 * k), 0, z),
                          rot=(0, s * 30, 0))
    elif name == "Frost":
        for s in (-1, 1):
            m.crystal(r=0.09, h=0.6, color="diamond_light", loc=(s * 0.6, 0, 0.6), rot=(0, s * 40, 0))
            m.crystal(r=0.07, h=0.4, color="diamond", loc=(s * 0.4, 0, 0.7), rot=(0, s * 15, 0))
    elif name == "Thunder":
        bolt = [(0.2, 1.0), (-0.5, -0.05), (0.0, -0.05), (-0.25, -1.0), (0.55, 0.2), (0.05, 0.2), (0.4, 1.0)]
        for y in (-0.1, 0.1):
            m.prism(bolt, depth=0.04, color="neon_blue", rot=(90, 0, 0), loc=(0, y, 2.3), scale=(0.3, 0.9, 1))
        for s in (-1, 1):
            m.prism(bolt, depth=0.08, color="plastic_yellow", rot=(90, 0, 0), loc=(s * 0.75, 0, 0.6), scale=0.35)
    elif name == "Shadow":
        for s in (-1, 1):
            m.pyramid(w=0.16, h=0.6, color="amethyst", loc=(s * 0.6, 0, 0.62), rot=(0, s * 60, 0))
            m.pyramid(w=0.12, h=0.35, color="amethyst", loc=(s * 0.25, 0, 1.4), rot=(0, s * 70, 0))
    elif name == "Nature":
        for i in range(6):
            z = 1.0 + i * 0.45
            m.torus(R=0.2, r=0.035, seg=8, color="vine", loc=(0, 0, z), rot=(0, 0, 45), scale=(1.4, 0.5, 1))
        for s in (-1, 1):
            m.leaf(length=0.6, width=0.3, thick=0.05, color="leaf_light", loc=(s * 0.55, 0, 0.62), rot=(90, 0, -s * 70))
    elif name == "Crystal":
        for i, (x, z, h) in enumerate(((0.2, 1.4, 0.6), (-0.22, 2.1, 0.5), (0.2, 2.8, 0.45))):
            m.crystal(r=0.1, h=h, color="amethyst" if i % 2 else "diamond_light", loc=(x, 0, z),
                      rot=(0, (1 if x > 0 else -1) * 55, 0))


for _e, _E in ELEMENTS.items():
    add(f"{_e}Sword", CAT, (lambda m, e=_e, E=_E: legend_sword(m, e, E)), sub="Legendary", origin=(0, 0, 0),
        tags=["legendary", _e.lower()])
