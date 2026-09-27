"""Tools: tiered simulator tools (8 tiers each) plus everyday / farming tools.

Tools stand upright (+Z) with the head at the top; the origin sits on the grip,
where a Roblox Tool's hand holds it.
"""
import math

from studlib.geo import by_height, circle_pts, jitter
from studlib.registry import add, asset
from studlib.tiers import ORDER, TIERS, paint, solid

CAT = "Tools"


def handle(m, T, z0, z1, r=0.1, grip=None, pommel=True, seg=8):
    m.cyl(r=r, r2=r * 0.92, h=z1 - z0, seg=seg, color=T["handle"], loc=(0, 0, (z0 + z1) / 2))
    if grip:
        ga, gb = grip
        m.cyl(r=r * 1.28, h=gb - ga, seg=seg, color=T["grip"], loc=(0, 0, (ga + gb) / 2),
              bevel=0.02, bseg=1)
        n = max(2, int((gb - ga) / 0.22))
        for i in range(n + 1):
            z = ga + (gb - ga) * i / n
            m.torus(R=r * 1.3, r=0.028, seg=seg, rseg=4, color=T["grip2"], loc=(0, 0, z), rot=(8, 0, 0))
    if pommel:
        m.cyl(r=r * 1.55, h=0.14, seg=seg, color=T["accent"], loc=(0, 0, z0 + 0.05), bevel=0.04)


def stoneify(tier):
    return jitter(0.025, 5) if tier == "Stone" else None


# --- tiered tools -----------------------------------------------------------
def pickaxe(m, T, tier):
    top = 3.1
    handle(m, T, 0.0, top + 0.1, r=0.1, grip=(0.25, 1.0))
    pts, rad = [], []
    n = 10
    for i in range(n + 1):
        t = i / n
        x = -1.35 + 2.7 * t
        pts.append((x, 0, top - 0.34 * (abs(x) / 1.35) ** 1.7))
        f = (1 - abs(2 * t - 1) ** 1.6)
        rad.append((0.13 * f, 0.19 * f) if 0 < i < n else 0)
    m.tube(pts, rad, seg=6, up=(0, 0, 1), deform=stoneify(tier), **paint(T, "main", "x", -1.35, 1.35), angle=35)
    # brighter tips
    for s in (-1, 1):
        m.tube([pts[1 if s < 0 else -2], pts[0 if s < 0 else -1]], [(0.05, 0.07), 0], seg=4, up=(0, 0, 1),
               color=solid(T, "light", "white"))
    # reinforced collar with bands and rivets
    m.box((0.4, 0.36, 0.56), bevel=0.06, color=T["accent"], loc=(0, 0, top - 0.02))
    for z in (top - 0.22, top + 0.18):
        m.box((0.46, 0.42, 0.08), bevel=0.02, color=T["dark"], loc=(0, 0, z))
    for s in (-1, 1):
        m.box((0.36, 0.3, 0.3), bevel=0.05, color=T["dark"], loc=(s * 0.32, 0, top - 0.03))
        m.box((0.08, 0.08, 0.08), bevel=0.02, color=solid(T, "light", "white"), loc=(s * 0.12, -0.19, top - 0.02))
    m.box((0.24, 0.24, 0.12), bevel=0.03, color=T["accent"], loc=(0, 0, top + 0.3))
    if tier in ("Gold", "Diamond", "Emerald", "Ruby", "Rainbow"):
        m.gem(r=0.1, h=0.1, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.21, top - 0.02))


def axe(m, T, tier):
    top = 3.0
    handle(m, T, 0.0, top + 0.15, r=0.1, grip=(0.25, 1.0))
    cz = top - 0.35
    blade = [(-0.28, -0.24), (0.3, -0.2), (0.72, -0.6), (0.9, -0.34), (0.97, 0.0), (0.9, 0.34),
             (0.72, 0.6), (0.3, 0.2), (-0.28, 0.24)]
    thin = lambda co: co.__class__((co.x, co.y, co.z * (1.0 - 0.55 * max(0.0, co.x - 0.25) / 0.72)))
    m.prism(blade, depth=0.2, bevel=0.03, bseg=1, rot=(90, 0, 0), loc=(0, 0, cz),
            deform=thin if tier != "Stone" else (lambda co: jitter(0.02, 3)(thin(co))),
            **paint(T, "main", "x", -0.3, 1.0))
    edge = [(0.82, -0.52), (0.93, -0.3), (0.99, 0.0), (0.93, 0.3), (0.82, 0.52), (0.86, 0.0)]
    m.prism(edge, depth=0.1, color=solid(T, "light", "white"), rot=(90, 0, 0), loc=(0, 0, cz))
    m.box((0.3, 0.3, 0.6), bevel=0.05, color=T["accent"], loc=(0, 0, cz))
    m.cyl(r=0.13, h=0.1, seg=8, color=T["dark"], loc=(0, 0, top + 0.12), bevel=0.03)


def shovel(m, T, tier):
    handle(m, T, 0.9, 3.4, r=0.09, grip=None, pommel=False)
    # D-grip
    m.torus(R=0.26, r=0.06, seg=12, rseg=5, color=T["grip"], rot=(90, 0, 0), loc=(0, 0, 3.62), arc=180)
    m.cyl(r=0.07, h=0.56, seg=6, color=T["grip"], rot=(0, 90, 0), loc=(0, 0, 3.62))
    m.cyl(r=0.11, h=0.35, seg=8, color=T["accent"], loc=(0, 0, 1.0), bevel=0.03)
    spade = [(-0.42, 0.9), (-0.44, 0.35), (-0.3, 0.1), (0.0, -0.05), (0.3, 0.1), (0.44, 0.35), (0.42, 0.9)]
    spade = list(reversed(spade))
    curve = lambda co: co.__class__((co.x, co.y, co.z + 0.12 * (co.x / 0.44) ** 2))
    m.prism(spade, depth=0.07, bevel=0.025, bseg=1, rot=(90, 0, 0), loc=(0, 0, 0.0),
            deform=curve, **paint(T, "main", "z", -0.05, 0.9))
    m.box((0.86, 0.12, 0.08), bevel=0.03, color=T["dark"], loc=(0, 0, 0.9))


def hammer(m, T, tier):
    top = 2.8
    handle(m, T, 0.0, top, r=0.1, grip=(0.25, 1.0))
    m.box((1.15, 0.5, 0.5), bevel=0.08, bseg=2, loc=(0, 0, top + 0.1), deform=stoneify(tier),
          **paint(T, "main", "x", -0.58, 0.58))
    for s in (-1, 1):
        m.box((0.12, 0.56, 0.56), bevel=0.04, color=T["dark"], loc=(s * 0.46, 0, top + 0.1))
    m.box((0.3, 0.54, 0.54), bevel=0.04, color=T["accent"], loc=(0, 0, top + 0.1))


def hoe(m, T, tier):
    top = 3.2
    handle(m, T, 0.0, top, r=0.09, grip=(0.25, 0.9))
    m.cyl(r=0.12, h=0.3, seg=8, color=T["accent"], loc=(0, 0, top - 0.05), bevel=0.03)
    m.tube([(0, 0, top), (0, -0.25, top + 0.2), (0, -0.55, top + 0.12)], [0.07, 0.07, 0.06], seg=6,
           color=T["dark"])
    blade = [(-0.35, 0.0), (0.35, 0.0), (0.3, -0.55), (-0.3, -0.55)]
    m.prism(blade, depth=0.06, bevel=0.02, bseg=1, rot=(90, 0, 0), loc=(0, -0.6, top + 0.15),
            **paint(T, "main", "x", -0.35, 0.35))


def scythe(m, T, tier):
    top = 3.6
    m.tube([(0, 0, 0), (0.08, 0, 1.2), (0.05, 0, 2.4), (0, 0, top)], [0.09, 0.09, 0.085, 0.08], seg=8,
           color=T["handle"])
    m.tube([(0.07, 0, 1.5), (0.07, -0.45, 1.6)], [0.06, 0.06], seg=6, color=T["grip"])
    m.cyl(r=0.13, h=0.14, seg=8, color=T["accent"], loc=(0, 0, 0.05), bevel=0.03)
    m.box((0.28, 0.26, 0.3), bevel=0.05, color=T["accent"], loc=(0, 0, top - 0.05))
    upper, lower = [], []
    n = 10
    for i in range(n + 1):
        t = i / n
        a = math.radians(95 - 105 * t)
        R = 1.25
        cx, cz = 0.05 + R * math.cos(a) - R * math.cos(math.radians(95)), top - 0.05 + 0.5 * math.sin(a) - 0.5
        w = 0.34 * (1 - t) ** 0.8
        upper.append((cx, cz + w * 0.25))
        lower.append((cx, cz - w))
    outline = lower + list(reversed(upper[:-1]))
    m.prism([(x, z) for x, z in outline], depth=0.07, bevel=0.02, bseg=1, rot=(90, 0, 0), loc=(0, 0, 0),
            **paint(T, "main", "x", 0.0, 1.5))


def heavy_pickaxe(m, T, tier):
    top = 3.3
    handle(m, T, 0.0, top + 0.1, r=0.12, grip=(0.25, 1.2))
    m.box((0.9, 0.55, 0.7), bevel=0.1, loc=(0, 0, top), deform=stoneify(tier), **paint(T, "main", "x", -0.45, 0.45))
    for s in (-1, 1):
        m.tube([(s * 0.4, 0, top), (s * 1.0, 0, top - 0.05), (s * 1.55, 0, top - 0.45)],
               [(0.24, 0.28), (0.18, 0.2), 0], seg=4, up=(0, 0, 1), **paint(T, "main", "x", -1.55, 1.55))
        m.box((0.12, 0.6, 0.76), bevel=0.03, color=T["dark"], loc=(s * 0.45, 0, top))
        m.box((0.09, 0.09, 0.09), bevel=0.02, color=solid(T, "light", "white"), loc=(s * 0.25, -0.29, top + 0.2))
        m.box((0.09, 0.09, 0.09), bevel=0.02, color=solid(T, "light", "white"), loc=(s * 0.25, -0.29, top - 0.2))
    m.box((0.5, 0.6, 0.12), bevel=0.03, color=T["accent"], loc=(0, 0, top + 0.4))
    m.box((0.36, 0.36, 0.36), bevel=0.06, color=T["accent"], loc=(0, 0, top - 0.5))
    if tier in ("Gold", "Diamond", "Emerald", "Ruby", "Rainbow"):
        m.gem(r=0.16, h=0.14, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.3, top))


def drill(m, T, tier):
    m.box((0.36, 0.5, 1.1), bevel=0.1, color=T["grip"], loc=(0, 0.3, 0.55), rot=(-10, 0, 0))
    m.box((0.9, 1.5, 0.8), bevel=0.16, color=T["dark"], loc=(0, -0.2, 1.35))
    m.box((0.95, 0.9, 0.5), bevel=0.1, loc=(0, -0.3, 1.35), **paint(T, "main", "y", -0.75, 0.15))
    for y in (0.15, 0.3, 0.45):
        m.box((0.97, 0.06, 0.4), color="charcoal", bevel=0.02, loc=(0, y, 1.35))
    m.cyl(r=0.34, h=0.3, seg=8, color=T["accent"], rot=(90, 0, 0), loc=(0, -1.05, 1.35), bevel=0.05)

    def spiral(c, n):
        a = math.degrees(math.atan2(c.z - 1.35, c.x)) + (-c.y) * 300
        return T["main"] if T["main"] != "RAINBOW" and int((a + 3600) / 45) % 2 else solid(T, "light", "white")
    m.lathe([(0.3, 0), (0.22, 0.4), (0.14, 0.8), (0.0, 1.2)], seg=8, color=spiral, rot=(90, 0, 0),
            loc=(0, -1.2, 1.35), smooth=False)
    m.box((0.1, 0.2, 0.1), color="plastic_red", bevel=0.02, loc=(0, 0.05, 1.05))
    m.box((0.5, 0.08, 0.2), color="neon_green" if tier != "Wood" else "wood_pale", bevel=0.02, loc=(0, 0.55, 1.5))


TIERED_TOOLS = [("Pickaxe", pickaxe, (0, 0, 0.6)), ("HeavyPickaxe", heavy_pickaxe, (0, 0, 0.7)),
                ("Drill", drill, (0, 0.3, 0.5)), ("Axe", axe, (0, 0, 0.6)), ("Shovel", shovel, (0, 0, 3.0)),
                ("Hammer", hammer, (0, 0, 0.6)), ("Hoe", hoe, (0, 0, 0.6)), ("Scythe", scythe, (0, 0, 1.4))]

for _name, _fn, _grip in TIERED_TOOLS:
    for _tier in ORDER:
        add(f"{_tier}{_name}", CAT, (lambda m, f=_fn, t=_tier: f(m, TIERS[t], t)), sub=_name,
            origin=_grip, tags=["tiered", _tier.lower()])


# --- everyday & farming tools --------------------------------------------------
W = TIERS["Wood"]


@asset("WateringCan", CAT, sub="Farming")
def watering_can(m):
    m.lathe([(0, 0), (0.55, 0), (0.6, 0.08), (0.6, 0.85), (0.5, 0.95), (0, 0.95)], seg=14,
            color=by_height("plastic_green", 0.18, "plastic_green", 0.8, "plastic_green"))
    m.torus(R=0.61, r=0.04, seg=14, rseg=4, color="plastic_yellow", loc=(0, 0, 0.45))
    m.tube([(0.45, 0, 0.25), (0.95, 0, 0.7), (1.2, 0, 0.95)], [0.09, 0.07, 0.07], seg=8, color="plastic_green")
    m.lathe([(0.07, 0), (0.16, 0.12), (0.16, 0.16), (0, 0.16)], seg=10, color="plastic_yellow",
            loc=(1.2, 0, 0.95), rot=(0, 50, 0))
    m.torus(R=0.36, r=0.06, seg=12, rseg=5, arc=180, color="plastic_yellow", rot=(90, 0, 0), loc=(-0.1, 0, 0.95))
    m.cyl(r=0.2, h=0.06, seg=12, color="plastic_yellow", loc=(0.1, 0, 0.98))


@asset("FishingRod", CAT, sub="Farming", origin=(0, 0, 0.5))
def fishing_rod(m):
    m.tube([(0, 0, 0), (0, 0, 2), (0.15, 0, 3.4), (0.45, 0, 4.4)], [0.08, 0.055, 0.04, 0.025], seg=6,
           color="wood_mid")
    m.cyl(r=0.1, h=0.8, seg=8, color="leather", loc=(0, 0, 0.5), bevel=0.02)
    m.cyl(r=0.18, h=0.12, seg=10, color="iron", rot=(0, 90, 0), loc=(0.12, 0, 1.0), bevel=0.03)
    m.cyl(r=0.04, h=0.22, seg=6, color="iron_dark", rot=(0, 90, 0), loc=(0.24, 0, 1.0))
    m.tube([(0.45, 0, 4.4), (0.5, 0, 3.2)], [0.008, 0.008], seg=3, color="string", smooth=False)
    m.sphere(r=0.1, seg=8, rings=6, color=by_height("plastic_white", 3.18, "plastic_red"), loc=(0.5, 0, 3.15),
             cuts={"z": [3.15]})


@asset("BugNet", CAT, sub="Farming", origin=(0, 0, 0.5))
def bug_net(m):
    handle(m, W, 0.0, 3.2, r=0.07, grip=(0.2, 0.8))
    m.torus(R=0.5, r=0.05, seg=16, rseg=5, color="iron_dark", loc=(0, 0, 3.7), rot=(90, 0, 0))
    m.lathe([(0.48, 0), (0.42, -0.4), (0.25, -0.75), (0, -0.85)], seg=12, color="fabric_white",
            rot=(90, 0, 0), loc=(0, 0, 3.7), caps=False)


@asset("Rake", CAT, sub="Farming", origin=(0, 0, 0.6))
def rake(m):
    handle(m, W, 0.0, 3.4, r=0.08, grip=(0.2, 0.8))
    m.box((1.1, 0.12, 0.12), bevel=0.03, color="iron_dark", loc=(0, 0, 3.45))
    for i in range(7):
        x = -0.48 + i * 0.16
        m.tube([(x, 0, 3.45), (x, -0.12, 3.3), (x, -0.25, 3.18)], [0.03, 0.03, 0.02], seg=4, color="iron")


@asset("Pitchfork", CAT, sub="Farming", origin=(0, 0, 0.6))
def pitchfork(m):
    handle(m, W, 0.0, 3.4, r=0.08, grip=(0.2, 0.8))
    m.box((0.6, 0.1, 0.1), bevel=0.03, color="iron_dark", loc=(0, 0, 3.45))
    for x in (-0.25, 0.0, 0.25):
        m.tube([(x, 0, 3.45), (x, 0, 4.1), (x, -0.05, 4.3)], [0.03, 0.03, 0.0], seg=4, color="iron")


@asset("Trowel", CAT, sub="Farming", origin=(0, 0, 0.4))
def trowel(m):
    m.cyl(r=0.1, h=0.8, seg=8, color="plastic_green", loc=(0, 0, 0.4), bevel=0.05)
    m.cyl(r=0.03, h=0.3, seg=5, color="iron", loc=(0, 0, 0.95))
    blade = [(0, 1.1), (-0.25, 0.8), (-0.28, 0.35), (-0.2, 0.05), (0.2, 0.05), (0.28, 0.35), (0.25, 0.8)]
    m.prism(list(reversed(blade)), depth=0.05, bevel=0.02, bseg=1, color="steel", rot=(90, 0, 0), loc=(0, 0, 1.05),
            deform=lambda co: co.__class__((co.x, co.y, co.z + 0.2 * (co.x / 0.28) ** 2)))


@asset("Wrench", CAT, sub="Workshop", origin="center")
def wrench(m):
    m.box((0.24, 0.1, 1.5), bevel=0.04, color="steel", loc=(0, 0, 0.95))
    m.torus(R=0.24, r=0.1, seg=12, rseg=5, arc=260, color="steel", rot=(90, -140, 0), loc=(0, 0, 1.9),
            scale=(1, 0.5, 1))
    m.torus(R=0.18, r=0.07, seg=12, rseg=5, color="steel", rot=(90, 0, 0), loc=(0, 0, 0.1), scale=(1, 0.7, 1))
    m.box((0.28, 0.14, 0.6), bevel=0.05, color="plastic_red", loc=(0, 0, 0.75))


@asset("Screwdriver", CAT, sub="Workshop", origin=(0, 0, 0.4))
def screwdriver(m):
    m.lathe([(0, 0), (0.14, 0.02), (0.17, 0.2), (0.15, 0.7), (0.1, 0.85), (0, 0.86)], seg=8,
            color="plastic_yellow", smooth=False)
    m.cyl(r=0.04, h=1.0, seg=6, color="steel", loc=(0, 0, 1.3))
    m.box((0.12, 0.02, 0.1), color="steel", loc=(0, 0, 1.82))


@asset("HandSaw", CAT, sub="Workshop", origin=(0, 0, 0.3))
def hand_saw(m):
    blade = [(-0.35, 0.0), (0.35, 0.0), (0.18, 2.2), (-0.08, 2.2)]
    m.prism(blade, depth=0.03, color="steel", rot=(90, 0, 0), loc=(0, 0, 0.55))
    for i in range(12):
        z = 0.6 + i * 0.18
        x = 0.35 - (i / 11) * 0.18
        m.prism([(0, 0), (0.1, 0.06), (0, 0.12)], depth=0.03, color="steel", rot=(90, 0, 0), loc=(x - 0.01, 0, z),
                smooth=False)
    m.box((0.6, 0.14, 0.55), bevel=0.08, color="wood", loc=(-0.08, 0, 0.3))
    m.box((0.3, 0.2, 0.25), color="wood_dark", loc=(-0.08, 0, 0.26))


@asset("Flashlight", CAT, sub="Workshop", origin=(0, 0, 0.4))
def flashlight(m):
    m.cyl(r=0.15, h=1.1, seg=10, color="plastic_black", loc=(0, 0, 0.55), bevel=0.03)
    m.lathe([(0.15, 1.05), (0.26, 1.35), (0.26, 1.45), (0, 1.45)], seg=10, color="plastic_yellow")
    m.cyl(r=0.22, h=0.02, seg=10, color="glow", loc=(0, 0, 1.46))
    m.box((0.08, 0.06, 0.16), color="plastic_red", loc=(0, -0.15, 0.8), bevel=0.02)


@asset("Bucket", CAT, sub="Farming")
def bucket(m):
    m.lathe([(0, 0.02), (0.38, 0.0), (0.5, 0.85), (0.46, 0.85), (0.34, 0.08), (0, 0.08)], seg=14,
            color="iron")
    m.torus(R=0.5, r=0.035, seg=14, rseg=4, color="iron_dark", loc=(0, 0, 0.84))
    m.torus(R=0.44, r=0.03, seg=14, rseg=4, color="iron_dark", loc=(0, 0, 0.35), scale=(1, 1, 1))
    m.torus(R=0.5, r=0.025, seg=12, rseg=4, arc=180, color="iron_dark", rot=(90, 0, 0), loc=(0, 0, 0.85))
    m.cyl(r=0.44, h=0.02, seg=14, color="water", loc=(0, 0, 0.7))


@asset("Magnet", CAT, sub="Simulator")
def magnet(m):
    m.torus(R=0.55, r=0.2, seg=14, rseg=8, arc=180, color="plastic_red", rot=(90, 0, 0), loc=(0, 0, 1.05),
            scale=(1, 1, 1))
    for s in (-1, 1):
        m.box((0.4, 0.4, 0.5), color="plastic_red", loc=(s * 0.55, 0, 0.6), bevel=0.04)
        m.box((0.42, 0.42, 0.3), color="silver", loc=(s * 0.55, 0, 0.18), bevel=0.04)


@asset("Torch", CAT, sub="Adventure", origin=(0, 0, 0.3))
def torch(m):
    m.cyl(r=0.08, r2=0.11, h=1.5, seg=8, color="wood_mid", loc=(0, 0, 0.75))
    m.cyl(r=0.16, h=0.35, seg=8, color="cork", loc=(0, 0, 1.55), bevel=0.04)
    m.cone(r=0.2, h=0.55, seg=7, color="fire", loc=(0, 0, 1.65), smooth=False)
    m.cone(r=0.12, h=0.35, seg=6, color="fire_light", loc=(0.02, -0.04, 1.72), smooth=False)


@asset("Broom", CAT, sub="Home", origin=(0, 0, 1.5))
def broom(m):
    m.cyl(r=0.07, h=3.4, seg=8, color="wood", loc=(0, 0, 2.3))
    m.lathe([(0.12, 0.62), (0.4, 0.3), (0.52, 0.0), (0, 0.0)], seg=10, color="rope",
            deform=jitter(0.02, 4), scale=(1, 0.55, 1))
    m.torus(R=0.14, r=0.04, seg=8, rseg=4, color="plastic_red", loc=(0, 0, 0.58), scale=(1, 0.8, 1))


@asset("Paintbrush", CAT, sub="Home", origin=(0, 0, 0.4))
def paintbrush(m):
    m.lathe([(0, 0), (0.08, 0.02), (0.1, 0.6), (0.13, 1.0), (0.12, 1.05)], seg=8, color="plastic_red")
    m.box((0.3, 0.14, 0.3), bevel=0.03, color="silver", loc=(0, 0, 1.15))
    m.box((0.28, 0.12, 0.4), bevel=0.06, color="rope", loc=(0, 0, 1.45))
    m.box((0.28, 0.12, 0.14), bevel=0.05, color="plastic_blue", loc=(0, 0, 1.64))


@asset("Spyglass", CAT, sub="Adventure", origin="center")
def spyglass(m):
    for i, (r, z0, z1, c) in enumerate(((0.16, 0, 0.8, "leather"), (0.13, 0.8, 1.4, "gold"),
                                        (0.1, 1.4, 1.9, "gold_dark"))):
        m.cyl(r=r, h=z1 - z0, seg=10, color=c, loc=(0, 0, (z0 + z1) / 2))
        m.torus(R=r, r=0.03, seg=10, rseg=4, color="gold", loc=(0, 0, z1))
    m.cyl(r=0.12, h=0.02, seg=10, color="glass", loc=(0, 0, -0.01))


@asset("Crowbar", CAT, sub="Workshop", origin="center")
def crowbar(m):
    m.tube([(0, 0, 0), (0, 0, 2.2), (0, -0.1, 2.45), (0, -0.35, 2.5)], [0.06, 0.06, 0.06, 0.04], seg=6,
           color="plastic_red")
    m.tube([(0, 0, 0.0), (0, -0.2, -0.08)], [0.06, 0.04], seg=6, color="plastic_red")


@asset("PowerDrill", CAT, sub="Workshop", origin=(0, 0, 0.4))
def power_drill(m):
    m.box((0.3, 0.4, 0.95), bevel=0.1, color="plastic_orange", loc=(0, 0.05, 0.55), rot=(-12, 0, 0))
    m.box((0.36, 0.55, 0.22), bevel=0.06, color="plastic_black", loc=(0, 0.1, 0.1))
    m.box((0.36, 1.0, 0.4), bevel=0.14, color="plastic_orange", loc=(0, -0.15, 1.1))
    m.cyl(r=0.14, h=0.25, seg=10, color="plastic_black", rot=(90, 0, 0), loc=(0, -0.75, 1.1))
    m.cyl(r=0.04, h=0.5, seg=6, color="steel", rot=(90, 0, 0), loc=(0, -1.1, 1.1))
    m.box((0.1, 0.12, 0.18), color="plastic_black", loc=(0, -0.15, 0.8))


@asset("LeafBlower", CAT, sub="Simulator", origin=(0, 0, 0.6))
def leaf_blower(m):
    m.sphere(r=0.5, seg=12, rings=8, color="plastic_green", loc=(0, 0.2, 0.8), scale=(0.8, 1.0, 0.9))
    m.cyl(r=0.18, r2=0.12, h=1.6, seg=10, color="plastic_yellow", rot=(90, 0, 0), loc=(0, -0.9, 0.7))
    m.torus(R=0.35, r=0.07, seg=12, rseg=5, arc=180, color="plastic_black", rot=(90, 0, 90), loc=(0, 0.2, 1.3))
    m.cyl(r=0.3, h=0.1, seg=12, color="plastic_black", rot=(90, 0, 0), loc=(0, 0.6, 0.8))


@asset("Vacuum", CAT, sub="Simulator", origin=(0, 0, 0.6))
def vacuum(m):
    m.cyl(r=0.4, h=0.9, seg=12, color="plastic_purple", loc=(0, 0.5, 0.65), bevel=0.12)
    m.cyl(r=0.32, h=0.1, seg=12, color="glass", loc=(0, 0.5, 1.12))
    m.tube([(0, 0.2, 0.6), (0, -0.3, 0.55), (0, -0.9, 0.25), (0, -1.2, 0.08)], [0.1, 0.1, 0.09, 0.09], seg=8,
           color="plastic_black")
    m.box((0.8, 0.3, 0.14), bevel=0.05, color="plastic_purple", loc=(0, -1.25, 0.07))
    m.tube([(0, 0.8, 0.9), (0, 0.85, 1.5), (0, 0.6, 1.7)], [0.06, 0.06, 0.06], seg=6, color="plastic_black")


@asset("Shears", CAT, sub="Farming", origin="center")
def shears(m):
    for s in (-1, 1):
        m.prism([(0, 0), (0.12, 0.1), (0.05, 1.3), (-0.02, 1.3)], depth=0.05, color="steel", rot=(90, 0, s * 8),
                loc=(0, s * 0.03, 0.6))
        m.tube([(0, 0, 0.6), (s * 0.12, 0, 0.3), (s * 0.18, 0, 0.0)], [0.06, 0.06, 0.06], seg=6,
               color="plastic_green")
    m.cyl(r=0.05, h=0.14, seg=6, color="iron_dark", rot=(90, 0, 0), loc=(0, 0, 0.62))


@asset("Compass", CAT, sub="Adventure", origin="center")
def compass(m):
    m.cyl(r=0.5, h=0.16, seg=16, color="gold", bevel=0.05, loc=(0, 0, 0.08))
    m.cyl(r=0.42, h=0.02, seg=16, color="paper", loc=(0, 0, 0.165))
    m.prism([(0, 0.34), (0.06, 0), (-0.06, 0)], depth=0.02, color="plastic_red", loc=(0, 0, 0.18))
    m.prism([(0, -0.34), (-0.06, 0), (0.06, 0)], depth=0.02, color="plastic_white", loc=(0, 0, 0.18))
    m.torus(R=0.1, r=0.035, seg=8, rseg=4, color="gold", rot=(90, 0, 0), loc=(0, 0.55, 0.08))


# --- legendary elemental pickaxes ---------------------------------------------------------
LEGEND_PICKS = {
    "Flame": dict(main="lava", light="fire_light", accent="gold", dark="obsidian", handle="obsidian", grip="rug_red",
                  grip2="gold", gem="fire"),
    "Frost": dict(main="ice", light="white", accent="silver", dark="diamond_dark", handle="diamond_dark",
                  grip="fabric_navy", grip2="silver", gem="diamond"),
    "Crystal": dict(main="amethyst", light="crystal_pink", accent="silver", dark="amethyst_dark", handle="stone_dark",
                    grip="fabric_purple", grip2="silver", gem="diamond_light"),
    "Void": dict(main="obsidian", light="neon_pink", accent="amethyst", dark="black", handle="charcoal",
                 grip="black", grip2="amethyst", gem="neon_pink"),
}


def legend_pickaxe(m, name, E):
    pickaxe(m, E, "Gold")
    top = 3.1
    if name == "Flame":
        for s in (-1, 1):
            for k in range(3):
                m.pyramid(w=0.16, h=0.35 - 0.06 * k, color="fire" if k % 2 else "fire_light",
                          loc=(s * (0.45 + 0.3 * k), 0, top + 0.1 - 0.06 * k * k), rot=(0, s * -10, 0))
    elif name == "Frost":
        for s in (-1, 1):
            m.crystal(r=0.09, h=0.5, color="diamond_light", loc=(s * 0.55, 0, top + 0.08), rot=(0, s * 20, 0))
            m.crystal(r=0.07, h=0.35, color="diamond", loc=(s * 0.85, 0, top), rot=(0, s * 35, 0))
    elif name == "Crystal":
        for s in (-1, 1):
            m.crystal(r=0.12, h=0.6, color="crystal_pink", loc=(s * 0.6, 0, top + 0.05), rot=(0, s * 15, 0))
        m.crystal(r=0.1, h=0.5, color="diamond_light", loc=(0, 0, top + 0.35))
    elif name == "Void":
        for s in (-1, 1):
            m.pyramid(w=0.18, h=0.45, color="amethyst", loc=(s * 0.7, 0, top + 0.02), rot=(0, s * -5, 0))
        m.torus(R=0.35, r=0.05, seg=8, color="neon_pink", rot=(90, 0, 0), loc=(0, -0.05, top))


for _e, _E in LEGEND_PICKS.items():
    add(f"{_e}Pickaxe", CAT, (lambda m, e=_e, E=_E: legend_pickaxe(m, e, E)), sub="Legendary", origin=(0, 0, 0.6),
        tags=["legendary", _e.lower()])


# =====================================================================================
# Batch 2: more tiered simulator tools (fishing rods, bug nets, coin magnets, chainsaws)
# =====================================================================================
def tier_fishing_rod(m, T, tier):
    m.tube([(0, 0, 0), (0, 0, 2.0), (0.15, 0, 3.4), (0.45, 0, 4.4)], [0.09, 0.065, 0.05, 0.035], seg=6,
           deform=stoneify(tier), **paint(T, "main", "z", 1.0, 4.4))
    m.cyl(r=0.12, h=0.9, seg=8, color=T["grip"], loc=(0, 0, 0.5), bevel=0.02)
    m.cyl(r=0.14, h=0.12, seg=8, color=T["accent"], loc=(0, 0, 0.02), bevel=0.03)
    m.cyl(r=0.22, h=0.16, seg=8, color=T["dark"], rot=(0, 90, 0), loc=(0.16, 0, 1.15), bevel=0.03)
    m.box((0.22, 0.06, 0.06), color=T["accent"], loc=(0.3, -0.12, 1.15))
    for z in (2.0, 3.0, 3.9):
        m.box((0.12, 0.12, 0.08), color=T["accent"], loc=(0.03 + (z - 2.0) * 0.2, 0, z))
    m.tube([(0.45, 0, 4.4), (0.5, 0, 3.0)], [0.012, 0.012], seg=3, color="string", smooth=False)
    m.box((0.2, 0.2, 0.2), color=by_height("plastic_white", 2.95, solid(T, "gem", "plastic_red")),
          loc=(0.5, 0, 2.95), cuts={"z": [2.95]}, bevel=0.04)


def tier_bug_net(m, T, tier):
    handle(m, T, 0.0, 3.2, r=0.08, grip=(0.2, 0.9))
    m.torus(R=0.55, r=0.07, seg=8, color=solid(T, "main", "gold"), loc=(0, 0, 3.8), rot=(90, 0, 0))
    m.box((0.2, 0.2, 0.3), color=T["accent"], bevel=0.04, loc=(0, 0, 3.2))
    m.lathe([(0.52, 0), (0.46, -0.4), (0.28, -0.8), (0, -0.9)], seg=8, color="fabric_white" if tier != "Rainbow"
            else "rb_pink", rot=(90, 0, 0), loc=(0, 0, 3.8), caps=False)
    if tier in ("Gold", "Diamond", "Emerald", "Ruby", "Rainbow"):
        m.gem(r=0.1, h=0.1, seg=6, color=solid(T, "gem"), rot=(90, 0, 0), loc=(0, -0.1, 3.24))


def tier_magnet(m, T, tier):
    handle(m, T, 0.0, 1.2, r=0.1, grip=(0.1, 1.0))
    m.box((0.5, 0.4, 0.3), color=T["dark"], bevel=0.05, loc=(0, 0, 1.3))
    m.torus(R=0.6, r=0.22, seg=8, rseg=4, arc=180, rot=(-90, 0, 0), loc=(0, 0, 2.05),
            **paint(T, "main", "x", -0.85, 0.85))
    for s in (-1, 1):
        m.box((0.46, 0.46, 0.6), color=T["main"] if T["main"] != "RAINBOW" else ("rb_red" if s < 0 else "rb_purple"),
              bevel=0.05, loc=(s * 0.6, 0, 2.3))
        m.box((0.48, 0.48, 0.3), color=solid(T, "light", "white"), bevel=0.04, loc=(s * 0.6, 0, 2.72))
    m.box((0.25, 0.1, 0.25), color=solid(T, "gem", "gold"), bevel=0.03, loc=(0, -0.22, 1.3))


def tier_chainsaw(m, T, tier):
    m.box((0.5, 1.6, 0.9), bevel=0.12, loc=(0, 0.4, 0.8), **paint(T, "main", "y", -0.4, 1.2))
    m.box((0.52, 0.5, 0.6), color=T["dark"], bevel=0.08, loc=(0, 0.2, 1.4))
    m.torus(R=0.38, r=0.06, seg=8, arc=180, color=T["grip"], rot=(90, 0, 90), loc=(0, 0.6, 1.3))
    m.box((0.26, 0.5, 0.2), color=T["grip"], bevel=0.04, loc=(0, 1.3, 0.9))
    m.box((0.12, 2.4, 0.5), color=solid(T, "light", "silver"), bevel=0.05, loc=(0, -1.6, 0.8))
    for k in range(10):
        y = -0.5 - k * 0.24
        for z in (0.52, 1.08):
            m.box((0.16, 0.14, 0.1), color="charcoal", loc=(0, y, z))
    m.box((0.14, 0.2, 0.5), color="charcoal", loc=(0, -2.8, 0.8))
    m.box((0.1, 0.4, 0.1), color="plastic_red" if tier != "Ruby" else "gold", loc=(0.26, 0.9, 1.1))


for _name, _fn, _grip in (("FishingRod", tier_fishing_rod, (0, 0, 0.5)), ("BugNet", tier_bug_net, (0, 0, 0.5)),
                          ("CoinMagnet", tier_magnet, (0, 0, 0.6)), ("Chainsaw", tier_chainsaw, (0, 1.3, 0.9))):
    for _tier in ORDER:
        add(f"{_tier}{_name}", CAT, (lambda m, f=_fn, t=_tier: f(m, TIERS[t], t)), sub=_name,
            origin=_grip, tags=["tiered", _tier.lower()])
