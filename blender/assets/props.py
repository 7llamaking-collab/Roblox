"""Simulator props: pet eggs, chests, currency, backpacks, pickups, potions,
trophies, signs, fences, lights, pads & portals, farm and town props."""
import math
import random

from studlib.geo import (RAINBOW, by_height, by_normal, circle_pts, heart_pts, jitter, rainbow,
                         star_pts)
from studlib.registry import add, asset
from studlib.tiers import ORDER, TIERS, paint, solid

CAT = "Props"

EGG_PROFILE = [(0, 0), (0.62, 0.08), (0.95, 0.5), (1.05, 1.05), (0.95, 1.6), (0.65, 2.1), (0.3, 2.42), (0, 2.5)]


def egg_shape(m, base, band=None, spots=None, band_z=(1.0, 1.35), zigzag=False, seed=1):
    kw = {}
    if band:
        z0, z1 = band_z
        if zigzag:
            def col(c, n):
                a = math.degrees(math.atan2(c.y, c.x))
                off = 0.18 * (1 if int((a + 360) / 22.5) % 2 else -1)
                return band if z0 + off < c.z < z1 + off else base
            kw["cuts"] = {"z": [z0 - 0.18, z0, z0 + 0.18, z1 - 0.18, z1, z1 + 0.18]}
        else:
            col = by_height(base, z0, band, z1, base)
            kw["cuts"] = {"z": [z0, z1]}
    else:
        col = base
    prof = []
    for r, z in EGG_PROFILE:
        prof.append((r, z))
    m.lathe(prof, seg=16, color=col, angle=50, **kw)
    if spots:
        rnd = random.Random(seed)
        for i in range(9):
            a = rnd.uniform(0, 2 * math.pi)
            z = rnd.uniform(0.35, 2.2)
            # radius of the egg at height z (linear interpolate the profile)
            r = 0.0
            for (r0, z0_), (r1, z1_) in zip(EGG_PROFILE[:-1], EGG_PROFILE[1:]):
                if z0_ <= z <= z1_:
                    r = r0 + (r1 - r0) * (z - z0_) / (z1_ - z0_)
            s = rnd.uniform(0.14, 0.24)
            m.sphere(r=s, seg=8, rings=5, color=spots, loc=(math.cos(a) * r * 0.97, math.sin(a) * r * 0.97, z),
                     scale=(0.4, 1, 1), rot=(0, 0, math.degrees(a)))


EGGS = [
    ("CommonEgg", dict(base="offwhite", spots="fur_tan")),
    ("UncommonEgg", dict(base="leaf_light", band="leaf_dark", zigzag=True)),
    ("RareEgg", dict(base="sapphire", spots="diamond_light")),
    ("EpicEgg", dict(base="amethyst", band="amethyst_dark", zigzag=True)),
    ("LegendaryEgg", dict(base="gold", band="gold_light", spots="gold_dark")),
    ("MythicEgg", dict(base="ruby", band="obsidian", zigzag=True)),
    ("SpottedEgg", dict(base="fur_cream", spots="fur_brown")),
    ("FarmEgg", dict(base="fur_tan", band="leaf", zigzag=True)),
    ("OceanEgg", dict(base="water", band="white", spots="water_dark")),
    ("JungleEgg", dict(base="leaf", spots="leaf_deep")),
    ("DesertEgg", dict(base="sand", band="clay", zigzag=True)),
    ("SnowEgg", dict(base="ice", spots="snow")),
    ("LavaEgg", dict(base="obsidian", band="lava", zigzag=True, spots="fire")),
    ("CandyEgg", dict(base="candy_pink", band="white", spots="candy_blue")),
    ("SpaceEgg", dict(base="penguin_black", spots="glow")),
    ("DiamondEgg", dict(base="diamond", band="diamond_light")),
    ("EmeraldEgg", dict(base="emerald", band="emerald_light")),
    ("RubyEgg", dict(base="ruby", band="ruby_light")),
]
for _i, (_n, _kw) in enumerate(EGGS):
    add(_n, CAT, (lambda m, kw=_kw, s=_i: egg_shape(m, seed=s + 3, **kw)), sub="PetEggs", tags=["simulator", "pets"])


@asset("RainbowEgg", CAT, sub="PetEggs", tags=["simulator", "pets"])
def rainbow_egg(m):
    m.lathe(EGG_PROFILE, seg=16, color=rainbow("z", 0.0, 2.5), cuts={"z": [2.5 * k / 8 for k in range(1, 8)]},
            angle=50)


@asset("GoldenEgg", CAT, sub="PetEggs", tags=["simulator", "pets"])
def golden_egg(m):
    egg_shape(m, "gold", band="gold_dark", zigzag=True)
    for a in (0, 120, 240):
        m.gem(r=0.14, h=0.14, seg=6, color="ruby", rot=(90, 0, a),
              loc=(math.sin(math.radians(a)) * 1.02, -math.cos(math.radians(a)) * 1.02, 1.17))


@asset("CrackedEgg", CAT, sub="PetEggs", tags=["simulator", "pets"])
def cracked_egg(m):
    zig = lambda co: co.__class__((co.x, co.y, min(co.z, 1.4 + 0.2 * math.sin(6 * math.atan2(co.y, co.x)))))
    m.lathe([(0, 0), (0.62, 0.08), (0.95, 0.5), (1.05, 1.05), (0.97, 1.5), (0.9, 1.5), (0.95, 1.05),
             (0.85, 0.5), (0, 0.15)], seg=18, color="offwhite", deform=zig)
    m.lathe([(0.65, 0), (0.3, 0.32), (0, 0.4), (0, 0)], seg=12, color="offwhite", loc=(0.4, -0.2, 2.1), rot=(30, -20, 0),
            caps=True)


@asset("EggStand", CAT, sub="PetEggs", tags=["simulator", "pets"])
def egg_stand(m):
    m.cyl(r=2.0, h=0.5, seg=16, color="stone_light", bevel=0.12, loc=(0, 0, 0.25))
    m.cyl(r=1.6, h=0.6, seg=16, color="stone", bevel=0.1, loc=(0, 0, 0.75))
    m.torus(R=1.25, r=0.14, seg=16, rseg=6, color="gold", loc=(0, 0, 1.08))
    for i in range(8):
        a = math.radians(45 * i)
        m.sphere(r=0.12, seg=6, rings=4, color="gold", loc=(math.cos(a) * 1.85, math.sin(a) * 1.85, 0.52))


# --- chests (tiered) ------------------------------------------------------------------
def chest(m, T, tier):
    m.box((3.0, 2.0, 1.6), bevel=0.08, loc=(0, 0, 0.8), **paint(T, "main", "x", -1.5, 1.5))
    m.cyl(r=1.0, h=3.0, seg=12, rot=(0, 90, 0), loc=(0, 0, 1.6),
          deform=lambda co: co.__class__((min(co.x, 0.02), co.y, co.z)), **paint(T, "main", "x", -1.5, 1.5))
    band = T["accent"] if tier != "Wood" else "iron_dark"
    for x in (-1.25, 0, 1.25):
        m.box((0.25, 2.1, 1.64), color=band, loc=(x, 0, 0.8))
        m.torus(R=1.03, r=0.1, seg=12, rseg=4, arc=180, color=band, rot=(90, 0, 90), loc=(x, 0, 1.6))
    m.box((3.1, 2.1, 0.18), color=T["dark"], bevel=0.04, loc=(0, 0, 1.6))
    m.box((0.6, 0.25, 0.7), color="gold" if tier != "Gold" else "gold_dark", bevel=0.06, loc=(0, -1.08, 1.5))
    m.cyl(r=0.09, h=0.1, seg=6, color="charcoal", rot=(90, 0, 0), loc=(0, -1.22, 1.42))
    if tier in ("Diamond", "Emerald", "Ruby", "Rainbow", "Gold"):
        for x in (-0.65, 0.65):
            m.gem(r=0.16, h=0.16, seg=6, color=solid(T, "gem" if tier != "Gold" else "light"), rot=(90, 0, 0),
                  loc=(x, -1.04, 0.8))


for _tier in ORDER:
    add(f"{_tier}Chest", CAT, (lambda m, t=_tier: chest(m, TIERS[t], t)), sub="Chests",
        tags=["simulator", "tiered", _tier.lower()])


# --- backpacks (tiered capacity upgrades) ------------------------------------------------
def backpack(m, T, tier):
    m.box((2.2, 1.2, 2.6), bevel=0.5, bseg=3, loc=(0, 0, 1.3), angle=60, **paint(T, "main", "z", 0, 2.6))
    m.box((1.6, 0.5, 1.0), bevel=0.22, bseg=2, color=T["dark"], loc=(0, -0.62, 0.8))
    m.box((1.2, 0.06, 0.07), color=T["accent"], loc=(0, -0.88, 1.12))
    m.box((2.3, 1.3, 0.4), bevel=0.18, bseg=2, color=T["dark"], loc=(0, 0, 2.45))
    m.box((2.0, 0.24, 1.0), bevel=0.12, bseg=2, color=T["dark"], loc=(0, -0.55, 2.05))
    m.box((0.3, 0.1, 0.34), color=T["accent"], bevel=0.04, loc=(0, -0.7, 1.65))
    for x in (-1.12, 1.12):
        m.cyl(r=0.34, h=1.0, seg=10, color=T["dark"], loc=(x, 0.0, 0.85), bevel=0.1)
    for x in (-0.55, 0.55):
        m.box((0.3, 0.18, 2.2), color=T["grip"], bevel=0.06, loc=(x, 0.66, 1.35))
    m.torus(R=0.3, r=0.07, seg=10, rseg=4, arc=180, color=T["grip"], rot=(90, 0, 0), loc=(0, 0.1, 2.62))
    m.sphere(r=0.1, seg=8, rings=5, color=solid(T, "gem", "gold"), loc=(0, -0.78, 1.65))


for _tier in ORDER:
    add(f"{_tier}Backpack", CAT, (lambda m, t=_tier: backpack(m, TIERS[t], t)), sub="Backpacks",
        tags=["simulator", "tiered", _tier.lower()])


# --- currency ------------------------------------------------------------------------------
def coin(m, face="gold", rim="gold_dark", loc=(0, 0, 0.12), rot=(0, 0, 0)):
    m.cyl(r=0.6, h=0.18, seg=16, color=rim, bevel=0.05, loc=loc, rot=rot)
    x, y, z = loc
    m.prism(star_pts(0.32, 0.14, 5), depth=0.22, color=face, loc=loc, rot=rot, bevel=0.02, bseg=1)


@asset("Coin", CAT, sub="Currency", origin="center")
def coin_asset(m):
    coin(m, rot=(90, 0, 0), loc=(0, 0, 0.6))


@asset("SilverCoin", CAT, sub="Currency", origin="center")
def silver_coin(m):
    coin(m, "silver", "iron_dark", rot=(90, 0, 0), loc=(0, 0, 0.6))


@asset("CoinStack", CAT, sub="Currency")
def coin_stack(m):
    for i in range(6):
        m.cyl(r=0.6, h=0.18, seg=16, color="gold" if i % 2 else "gold_dark", bevel=0.04,
              loc=(0.03 * math.sin(i * 2.1), 0.03 * math.cos(i * 1.7), 0.09 + i * 0.19))
    coin(m, loc=(0.0, 0.0, 1.24))


@asset("CoinPile", CAT, sub="Currency")
def coin_pile(m):
    m.sphere(r=1.4, seg=14, rings=8, color="gold", loc=(0, 0, 0), scale=(1, 1, 0.55),
             deform=lambda co: co.__class__((co.x, co.y, max(co.z, 0.0))))
    rnd = random.Random(3)
    for i in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.2, 1.3)
        z = 0.77 * math.sqrt(max(0.0, 1 - (r / 1.4) ** 2)) + 0.02
        m.cyl(r=0.32, h=0.1, seg=10, color="gold_dark" if i % 3 else "gold_light",
              loc=(math.cos(a) * r, math.sin(a) * r, z), rot=(rnd.uniform(-25, 25), rnd.uniform(-25, 25), 0))
    m.gem(r=0.25, h=0.3, seg=6, color="ruby", loc=(0.3, -0.3, 0.72))
    m.gem(r=0.22, h=0.26, seg=6, color="diamond", loc=(-0.5, 0.2, 0.62))


@asset("MoneyBag", CAT, sub="Currency")
def money_bag(m):
    m.lathe([(0, 0), (0.8, 0.05), (1.1, 0.6), (1.0, 1.2), (0.5, 1.6), (0.3, 1.75), (0.45, 2.1), (0.2, 2.2), (0, 2.2)],
            seg=14, color="fabric_cream")
    m.torus(R=0.33, r=0.08, seg=10, rseg=4, color="rope", loc=(0, 0, 1.72))
    coin(m, loc=(0, -1.02, 0.85), rot=(90, 0, 0))


@asset("CashStack", CAT, sub="Currency")
def cash_stack(m):
    for i in range(5):
        m.box((1.6, 0.8, 0.1), color="leaf_light" if i % 2 else "leaf", loc=(0.02 * i, 0, 0.05 + i * 0.1), bevel=0.02,
              bseg=1)
    m.box((0.3, 0.84, 0.54), color="paper", loc=(0.04, 0, 0.26))


GEMS = [("BlueGem", "diamond", "diamond_dark"), ("RedGem", "ruby", "ruby_dark"), ("GreenGem", "emerald", "emerald_dark"),
        ("PurpleGem", "amethyst", "amethyst_dark"), ("YellowGem", "topaz", "gold_dark")]


def gem_asset(m, a, b):
    m.gem(r=0.7, h=1.0, seg=8, color=lambda c, n: a if n.z > 0.2 else b, loc=(0, 0, 0))


for _n, _a, _b in GEMS:
    add(_n, CAT, (lambda m, a=_a, b=_b: gem_asset(m, a, b)), sub="Currency", tags=["simulator"])


# --- pickups & collectibles ----------------------------------------------------------------------
@asset("Star", CAT, sub="Pickups", origin="center")
def star(m):
    m.prism(star_pts(1.0, 0.45, 5), depth=0.35, color="gold", bevel=0.1, bseg=2, rot=(90, 0, 0), taper_to=None)


@asset("Heart", CAT, sub="Pickups", origin="center")
def heart(m):
    m.prism(heart_pts(2.0, 28), depth=0.45, color="plastic_red", bevel=0.14, bseg=2, rot=(90, 0, 0))


@asset("LightningBolt", CAT, sub="Pickups", origin="center")
def lightning(m):
    m.prism([(0.2, 1.0), (-0.5, -0.05), (0.0, -0.05), (-0.25, -1.0), (0.55, 0.2), (0.05, 0.2), (0.4, 1.0)],
            depth=0.3, color="plastic_yellow", bevel=0.06, bseg=1, rot=(90, 0, 0))


@asset("Diamond", CAT, sub="Pickups", origin="center")
def diamond(m):
    m.gem(r=0.8, h=1.2, seg=8, color=lambda c, n: "diamond_light" if n.z > 0.3 else "diamond", loc=(0, 0, -0.6))


@asset("Key", CAT, sub="Pickups", origin="center")
def key(m):
    m.torus(R=0.45, r=0.12, seg=14, rseg=6, color="gold", rot=(90, 0, 0), loc=(-0.9, 0, 0))
    m.cyl(r=0.1, h=1.8, seg=8, color="gold", rot=(0, 90, 0), loc=(0.35, 0, 0))
    m.box((0.14, 0.14, 0.4), color="gold", loc=(0.95, 0, -0.18))
    m.box((0.14, 0.14, 0.3), color="gold", loc=(0.65, 0, -0.14))
    m.gem(r=0.14, h=0.14, seg=6, color="ruby", rot=(90, 0, 0), loc=(-0.9, -0.1, 0))


@asset("GiftBox", CAT, sub="Pickups")
def gift_box(m):
    m.box((1.8, 1.8, 1.5), color="plastic_red", bevel=0.05, loc=(0, 0, 0.75))
    m.box((1.95, 1.95, 0.4), color="plastic_red", bevel=0.05, loc=(0, 0, 1.55))
    m.box((0.3, 1.98, 1.95), color="plastic_yellow", loc=(0, 0, 0.98))
    m.box((1.98, 0.3, 1.95), color="plastic_yellow", loc=(0, 0, 0.98))
    for a in (45, 135):
        m.torus(R=0.35, r=0.1, seg=10, rseg=5, color="plastic_yellow", rot=(90, 0, a), loc=(0, 0, 2.05),
                scale=(1, 1, 0.7))


@asset("Balloon", CAT, sub="Pickups")
def balloon(m):
    m.lathe([(0, 0), (0.12, 0.05), (0.7, 0.55), (0.85, 1.1), (0.7, 1.65), (0.35, 1.95), (0, 2.0)], seg=14,
            color="plastic_red", loc=(0, 0, 2.6))
    m.cone(r=0.12, h=0.16, seg=6, color="plastic_red", loc=(0, 0, 2.48))
    m.tube([(0, 0, 2.5), (0.15, 0, 1.8), (-0.1, 0, 1.0), (0.05, 0, 0)], [0.015] * 4, seg=3, color="string",
           smooth=False)


@asset("Crown", CAT, sub="Pickups")
def crown(m):
    m.cyl(r=0.9, h=0.5, seg=16, color="gold", loc=(0, 0, 0.25), caps=True)
    for i in range(6):
        a = math.radians(60 * i)
        m.cone(r=0.3, h=0.7, seg=6, color="gold", loc=(math.cos(a) * 0.75, math.sin(a) * 0.75, 0.45), smooth=False)
        m.sphere(r=0.1, seg=6, rings=4, color="gold_light", loc=(math.cos(a) * 0.75, math.sin(a) * 0.75, 1.17))
        m.gem(r=0.1, h=0.1, seg=6, color=["ruby", "emerald", "sapphire"][i % 3], rot=(90, 0, 60 * i + 90),
              loc=(math.cos(a) * 0.92, math.sin(a) * 0.92, 0.25))


@asset("Trophy", CAT, sub="Awards")
def trophy(m):
    m.box((1.4, 1.4, 0.5), color="wood_dark", bevel=0.06, loc=(0, 0, 0.25))
    m.box((1.0, 0.1, 0.25), color="gold_light", loc=(0, -0.7, 0.25))
    m.lathe([(0.45, 0.5), (0.2, 0.7), (0.12, 1.2), (0.3, 1.4), (0.8, 2.0), (0.9, 2.6), (0.8, 2.6), (0.7, 2.05),
             (0, 1.6)], seg=14, color="gold")
    for s in (-1, 1):
        m.torus(R=0.35, r=0.07, seg=10, rseg=4, arc=200, color="gold", rot=(90, 0, s * 90 - 90 + (0 if s > 0 else 0)),
                loc=(s * 0.85, 0, 2.15), scale=(1, 1, 1))
    m.prism(star_pts(0.25, 0.11, 5), depth=0.06, color="gold_light", rot=(90, 0, 0), loc=(0, -0.83, 2.2))


def medal(m, face, ribbon):
    m.prism([(-0.5, 2.2), (-0.2, 0.6), (0.2, 0.6), (0.5, 2.2), (0.2, 2.2), (0, 1.1), (-0.2, 2.2)], depth=0.05,
            color=ribbon, rot=(90, 0, 0))
    m.cyl(r=0.55, h=0.12, seg=16, color=face, bevel=0.03, rot=(90, 0, 0), loc=(0, 0, 0.1))
    m.prism(star_pts(0.28, 0.12, 5), depth=0.16, color=face, rot=(90, 0, 0), loc=(0, -0.02, 0.1))


for _n, _f, _r in (("GoldMedal", "gold", "fabric_red"), ("SilverMedal", "silver", "fabric_blue"),
                   ("BronzeMedal", "bronze", "fabric_green")):
    add(_n, CAT, (lambda m, f=_f, r=_r: medal(m, f, r)), sub="Awards", origin="center")


# --- potions ---------------------------------------------------------------------------------------
def potion(m, liquid, shape="round"):
    if shape == "round":
        prof = [(0, 0), (0.45, 0.02), (0.65, 0.35), (0.62, 0.8), (0.25, 1.1), (0.2, 1.5), (0, 1.5)]
        level = 0.75
    else:
        prof = [(0, 0), (0.5, 0), (0.5, 1.0), (0.25, 1.2), (0.2, 1.5), (0, 1.5)]
        level = 0.8
    m.lathe(prof, seg=12, color=lambda c, n: liquid if c.z < level else "glass", cuts={"z": [level]})
    m.cyl(r=0.24, h=0.3, seg=8, color="cork", loc=(0, 0, 1.55), bevel=0.04)
    m.sphere(r=0.1, seg=6, rings=4, color="white", loc=(-0.3, -0.5, 0.6), scale=(0.6, 0.4, 1.3))


for _n, _c, _s in (("HealthPotion", "potion_red", "round"), ("ManaPotion", "potion_blue", "round"),
                   ("SpeedPotion", "potion_yellow", "tall"), ("LuckPotion", "potion_green", "tall"),
                   ("MagicPotion", "potion_purple", "round")):
    add(_n, CAT, (lambda m, c=_c, s=_s: potion(m, c, s)), sub="Potions", tags=["simulator", "boost"])


# --- pads, buttons & portals -------------------------------------------------------------------------
@asset("SellPad", CAT, sub="Pads", tags=["simulator"])
def sell_pad(m):
    m.cyl(r=3.0, h=0.4, seg=20, color="gold_dark", bevel=0.1, loc=(0, 0, 0.2))
    m.cyl(r=2.6, h=0.1, seg=20, color="gold", loc=(0, 0, 0.42))
    m.cyl(r=1.3, h=0.2, seg=16, color="gold_dark", bevel=0.05, loc=(0, 0, 0.55))
    m.prism(star_pts(0.8, 0.35, 5), depth=0.2, color="gold_light", loc=(0, 0, 0.6), bevel=0.04, bseg=1)


@asset("SpawnPad", CAT, sub="Pads")
def spawn_pad(m):
    m.cyl(r=3.0, h=0.4, seg=20, color="stone", bevel=0.1, loc=(0, 0, 0.2))
    m.cyl(r=2.5, h=0.1, seg=20, color="neon_blue", loc=(0, 0, 0.42))
    m.torus(R=2.0, r=0.12, seg=20, rseg=5, color="white", loc=(0, 0, 0.5))


@asset("UpgradePad", CAT, sub="Pads", tags=["simulator"])
def upgrade_pad(m):
    m.cyl(r=3.0, h=0.4, seg=20, color="leaf_deep", bevel=0.1, loc=(0, 0, 0.2))
    m.cyl(r=2.6, h=0.1, seg=20, color="leaf_light", loc=(0, 0, 0.42))
    m.prism([(0, 1.1), (1.0, 0.0), (0.4, 0.0), (0.4, -1.1), (-0.4, -1.1), (-0.4, 0.0), (-1.0, 0.0)], depth=0.1,
            color="white", loc=(0, 0, 0.5), smooth=False)


@asset("BigButton", CAT, sub="Pads", tags=["simulator", "rebirth"])
def big_button(m):
    m.box((3.0, 3.0, 1.0), color="charcoal", bevel=0.15, loc=(0, 0, 0.5))
    m.cyl(r=1.2, h=0.25, seg=16, color="iron", bevel=0.06, loc=(0, 0, 1.1))
    m.lathe([(1.0, 0), (1.0, 0.3), (0.8, 0.55), (0, 0.62)], seg=16, color="plastic_red", loc=(0, 0, 1.2))


@asset("Portal", CAT, sub="Pads")
def portal(m):
    m.torus(R=3.2, r=0.6, seg=24, rseg=8, color="stone", rot=(90, 0, 0), loc=(0, 0, 4.0), arc=360)
    m.cyl(r=2.7, h=0.2, seg=24, rot=(90, 0, 0), loc=(0, 0, 4.0),
          color=lambda c, n: ["amethyst", "plastic_purple", "neon_pink"][
              int((math.degrees(math.atan2(c.z - 4.0, c.x)) + math.hypot(c.x, c.z - 4.0) * 60 + 720) / 40) % 3])
    for s in (-1, 1):
        m.box((1.6, 1.6, 1.0), color="stone_dark", bevel=0.1, loc=(s * 3.0, 0, 0.5))
    for i in range(8):
        a = math.radians(45 * i + 22.5)
        m.crystal(r=0.25, h=0.8, color="amethyst", loc=(math.cos(a) * 3.2, 0, 4.0 + math.sin(a) * 3.2),
                  rot=(0, -math.degrees(a) + 90, 0))


@asset("Podium", CAT, sub="Awards")
def podium(m):
    for x, h, c, t in ((0, 2.4, "gold", "1"), (-2.6, 1.6, "silver", "2"), (2.6, 1.0, "bronze", "3")):
        m.box((2.6, 2.4, h), color="plastic_white", bevel=0.08, loc=(x, 0, h / 2))
        m.box((2.62, 2.42, 0.25), color=c, bevel=0.04, loc=(x, 0, h - 0.12))


# --- town & farm props -----------------------------------------------------------------------------
@asset("SignPost", CAT, sub="Town")
def sign_post(m):
    m.box((0.35, 0.35, 5.0), color="wood_mid", bevel=0.05, loc=(0, 0, 2.5))
    m.prism([(-1.4, -0.45), (1.2, -0.45), (1.6, 0.0), (1.2, 0.45), (-1.4, 0.45)], depth=0.2, color="wood_light",
            bevel=0.05, rot=(90, 0, 0), loc=(0.3, -0.25, 4.2))
    m.prism([(1.4, -0.45), (-1.2, -0.45), (-1.6, 0.0), (-1.2, 0.45), (1.4, 0.45)], depth=0.2, color="wood",
            bevel=0.05, rot=(90, 0, 0), loc=(-0.3, -0.25, 3.1))


@asset("Mailbox", CAT, sub="Town")
def mailbox(m):
    m.box((0.3, 0.3, 3.0), color="wood_mid", loc=(0, 0, 1.5))
    m.box((1.0, 1.8, 0.8), color="plastic_blue", bevel=0.05, loc=(0, 0, 3.2))
    m.cyl(r=0.5, h=1.8, seg=12, rot=(90, 0, 0), color="plastic_blue", loc=(0, 0, 3.6),
          deform=lambda co: co.__class__((co.x, max(co.y, -0.02), co.z)))
    m.box((0.1, 0.12, 0.8), color="plastic_red", loc=(0.55, 0.3, 3.8))
    m.box((0.1, 0.4, 0.3), color="plastic_red", loc=(0.55, 0.45, 4.1))


@asset("StreetLamp", CAT, sub="Town")
def street_lamp(m):
    m.cyl(r=0.6, h=0.5, seg=10, color="charcoal", bevel=0.1, loc=(0, 0, 0.25))
    m.cyl(r=0.18, r2=0.14, h=8.0, seg=8, color="charcoal", loc=(0, 0, 4.4))
    m.lathe([(0.3, 8.3), (0.7, 8.6), (0.6, 9.6), (0.9, 9.7), (0.3, 10.1), (0, 10.2)], seg=8, color="charcoal",
            smooth=False)
    m.cyl(r=0.5, h=0.9, seg=8, color="glow", loc=(0, 0, 9.1))


@asset("Lantern", CAT, sub="Town")
def lantern(m):
    m.box((1.0, 1.0, 0.2), color="charcoal", bevel=0.04, loc=(0, 0, 0.1))
    for x in (-0.42, 0.42):
        for y in (-0.42, 0.42):
            m.box((0.12, 0.12, 1.2), color="charcoal", loc=(x, y, 0.8))
    m.box((0.78, 0.78, 1.1), color="glow", loc=(0, 0, 0.8))
    m.cone(r=0.8, h=0.5, seg=4, color="charcoal", rot=(0, 0, 45), loc=(0, 0, 1.4), smooth=False)
    m.torus(R=0.2, r=0.05, seg=8, rseg=4, color="charcoal", rot=(90, 0, 0), loc=(0, 0, 2.05))


@asset("Fence", CAT, sub="Farm")
def fence(m):
    for x in (-2.0, 0.0, 2.0):
        m.box((0.35, 0.35, 2.6), color="wood", bevel=0.05, loc=(x, 0, 1.3))
        m.cone(r=0.25, h=0.3, seg=4, color="wood", rot=(0, 0, 45), loc=(x, 0, 2.6), smooth=False)
    for z in (0.9, 1.9):
        m.box((4.4, 0.18, 0.35), color="wood_light", bevel=0.04, loc=(0, 0.05, z))


@asset("PicketFence", CAT, sub="Farm")
def picket_fence(m):
    for i in range(7):
        x = -1.8 + i * 0.6
        m.box((0.36, 0.12, 2.0), color="plastic_white", bevel=0.03, loc=(x, 0, 1.0))
        m.prism([(-0.18, 0), (0.18, 0), (0, 0.25)], depth=0.12, color="plastic_white", rot=(90, 0, 0), loc=(x, 0, 2.0))
    for z in (0.6, 1.5):
        m.box((4.2, 0.1, 0.25), color="plastic_white", loc=(0, 0.1, z))


@asset("HayBale", CAT, sub="Farm")
def hay_bale(m):
    m.box((2.4, 1.4, 1.4), color="corn", bevel=0.15, loc=(0, 0, 0.7), deform=jitter(0.03, 2))
    for x in (-0.6, 0.6):
        m.box((0.1, 1.44, 1.44), color="autumn_orange", loc=(x, 0, 0.7))


@asset("Wheelbarrow", CAT, sub="Farm")
def wheelbarrow(m):
    m.lathe([(0, 0), (1.2, 0), (1.5, 0.8), (1.4, 0.8), (1.1, 0.1), (0, 0.1)], seg=4, color="plastic_green",
            rot=(0, 0, 45), scale=(1.0, 1.4, 1), loc=(0, 0, 0.7), smooth=False)
    m.cyl(r=0.5, h=0.25, seg=12, color="rubber", rot=(0, 90, 0), loc=(0, -1.6, 0.5))
    for x in (-0.6, 0.6):
        m.box((0.12, 3.2, 0.12), color="wood", loc=(x, 0.2, 0.75), rot=(-8, 0, 0))
        m.box((0.12, 0.12, 0.7), color="charcoal", loc=(x, 0.9, 0.35))


@asset("MineCart", CAT, sub="Mining", tags=["mining"])
def mine_cart(m):
    m.lathe([(0, 0.4), (1.1, 0.4), (1.4, 1.8), (1.3, 1.8), (1.0, 0.5), (0, 0.5)], seg=4, rot=(0, 0, 45),
            scale=(1.3, 0.9, 1), color="iron_dark", smooth=False)
    m.box((1.9, 1.3, 0.2), color="coal", loc=(0, 0, 1.55), deform=jitter(0.1, 3))
    for x in (-0.9, 0.9):
        for y in (-0.8, 0.8):
            m.cyl(r=0.35, h=0.15, seg=10, color="charcoal", rot=(90, 0, 0), loc=(x, y, 0.35))
    m.gem(r=0.25, h=0.3, seg=6, color="diamond", loc=(0.3, 0.1, 1.6))
    m.ico(r=0.3, sub=0, color="gold", loc=(-0.4, -0.1, 1.75))


@asset("Anvil", CAT, sub="Crafting")
def anvil(m):
    m.box((1.2, 1.0, 0.3), color="iron_dark", bevel=0.05, loc=(0, 0, 0.15))
    m.box((0.6, 0.6, 0.9), color="iron_dark", loc=(0, 0, 0.7))
    m.box((2.0, 1.0, 0.5), color="iron_dark", bevel=0.05, loc=(0.1, 0, 1.35))
    m.cone(r=0.5, h=1.0, seg=4, color="iron_dark", rot=(0, 90, 45), loc=(1.05, 0, 1.35), scale=(1, 1, 1),
           smooth=False)


@asset("Cauldron", CAT, sub="Crafting")
def cauldron(m):
    m.lathe([(0, 0.3), (0.9, 0.35), (1.3, 0.9), (1.25, 1.6), (1.1, 1.8), (1.05, 1.7), (1.1, 1.5), (1.1, 0.95),
             (0.8, 0.5), (0, 0.45)], seg=14, color="charcoal")
    m.cyl(r=1.05, h=0.05, seg=14, color="slime", loc=(0, 0, 1.55))
    for i in range(3):
        a = math.radians(120 * i)
        m.cyl(r=0.14, h=0.5, seg=6, color="charcoal", loc=(math.cos(a) * 0.8, math.sin(a) * 0.8, 0.2))
    for x, y in ((0.3, 0.2), (-0.3, -0.25), (0.1, -0.4)):
        m.sphere(r=0.15, seg=6, rings=4, color="neon_green", loc=(x, y, 1.62))


@asset("Well", CAT, sub="Farm")
def well(m):
    m.lathe([(1.4, 0), (1.4, 1.6), (1.1, 1.6), (1.1, 0.3), (0, 0.3)], seg=12, color="stone",
            cuts={"z": 0.4}, smooth=False)
    m.cyl(r=1.15, h=0.05, seg=12, color="water", loc=(0, 0, 1.2))
    for x in (-1.25, 1.25):
        m.box((0.25, 0.25, 2.6), color="wood_mid", loc=(x, 0, 2.6))
    m.cyl(r=0.15, h=2.6, seg=8, color="wood", rot=(0, 90, 0), loc=(0, 0, 3.2))
    m.prism([(-1.9, 0), (1.9, 0), (0, 1.1)], depth=2.4, color="roof_red", rot=(90, 0, 0), loc=(0, 1.2, 3.8))
    m.lathe([(0, 0), (0.3, 0), (0.35, 0.5), (0, 0.5)], seg=8, color="wood", loc=(0.4, 0, 2.2))


@asset("Campfire", CAT, sub="Adventure")
def campfire(m):
    for i in range(8):
        a = math.radians(45 * i)
        m.ico(r=0.35, sub=0, color="stone", loc=(math.cos(a) * 1.1, math.sin(a) * 1.1, 0.2), smooth=False)
    for a in (0, 60, 120):
        m.cyl(r=0.18, h=1.8, seg=6, color="wood_mid", rot=(0, 90, a), loc=(0, 0, 0.3))
    m.cone(r=0.6, h=1.4, seg=7, color="fire", loc=(0, 0, 0.3), smooth=False)
    m.cone(r=0.35, h=0.9, seg=6, color="fire_light", loc=(0.1, -0.1, 0.35), smooth=False)


@asset("Tent", CAT, sub="Adventure")
def tent(m):
    m.prism([(-2.0, 0), (2.0, 0), (0, 3.0)], depth=4.0, color="fabric_orange", rot=(90, 0, 0), smooth=False)
    m.prism([(-0.9, 0), (0.9, 0), (0, 1.8)], depth=0.1, color="fabric_brown", rot=(90, 0, 0), loc=(0, -2.02, 0),
            smooth=False)
    m.cyl(r=0.06, h=3.4, seg=5, color="wood", loc=(0, -2.1, 1.6))


@asset("Flag", CAT, sub="Town")
def flag(m):
    m.cyl(r=0.1, h=6.0, seg=8, color="silver", loc=(0, 0, 3.0))
    m.sphere(r=0.18, seg=8, rings=5, color="gold", loc=(0, 0, 6.1))
    wave = lambda co: co.__class__((co.x, co.y, co.z + 0.15 * math.sin(co.x * 2.5)))
    m.box((2.6, 1.6, 0.06), color=lambda c, n: "plastic_red" if c.z > 5.2 else "white", rot=(90, 0, 0),
          loc=(1.4, 0, 5.1), deform=wave, cuts={"z": [5.2], "x": 0.4})


@asset("TrafficCone", CAT, sub="Town")
def traffic_cone(m):
    m.box((1.2, 1.2, 0.15), color="plastic_orange", bevel=0.05, loc=(0, 0, 0.075))
    m.lathe([(0.45, 0.15), (0.12, 1.6), (0, 1.62)], seg=12,
            color=by_height("plastic_orange", 0.6, "white", 0.95, "plastic_orange"), cuts={"z": [0.6, 0.95]})


@asset("FireHydrant", CAT, sub="Town")
def fire_hydrant(m):
    m.cyl(r=0.5, h=0.2, seg=10, color="plastic_red", bevel=0.05, loc=(0, 0, 0.1))
    m.cyl(r=0.38, h=1.2, seg=10, color="plastic_red", loc=(0, 0, 0.8))
    m.lathe([(0.45, 1.35), (0.4, 1.6), (0.15, 1.75), (0, 1.8)], seg=10, color="plastic_red")
    m.cyl(r=0.45, h=0.12, seg=10, color="plastic_yellow", loc=(0, 0, 1.4))
    for a in (0, 180):
        m.cyl(r=0.16, h=0.3, seg=8, color="plastic_yellow", rot=(0, 90, a), loc=(math.cos(math.radians(a)) * 0.45, 0, 1.0))


@asset("Scarecrow", CAT, sub="Farm")
def scarecrow(m):
    m.box((0.25, 0.25, 5.0), color="wood_mid", loc=(0, 0.1, 2.5))
    m.box((3.2, 0.2, 0.2), color="wood_mid", loc=(0, 0.1, 3.4))
    m.box((1.2, 0.7, 1.6), color="fabric_blue", bevel=0.15, loc=(0, 0, 3.0))
    for s in (-1, 1):
        m.box((1.1, 0.5, 0.45), color="fabric_red", bevel=0.12, loc=(s * 1.1, 0.05, 3.4))
        m.cone(r=0.25, h=0.35, seg=5, color="corn", rot=(0, s * 90, 0), loc=(s * 1.65, 0.05, 3.4), smooth=False)
    m.sphere(r=0.55, seg=10, rings=7, color="fabric_cream", loc=(0, 0, 4.2))
    m.lathe([(1.0, 0), (1.0, 0.08), (0.5, 0.1), (0.45, 0.7), (0, 0.72)], seg=10, color="corn", loc=(0, 0, 4.55))
    for x in (-0.2, 0.2):
        m.box((0.12, 0.05, 0.12), color="charcoal", loc=(x, -0.52, 4.3))


@asset("Beehive", CAT, sub="Farm")
def beehive(m):
    for i, (r, z) in enumerate(((0.8, 0.3), (1.0, 0.8), (0.95, 1.3), (0.75, 1.75), (0.45, 2.1))):
        m.torus(R=r * 0.7, r=0.3, seg=12, rseg=6, color="honey" if i % 2 else "caramel", loc=(0, 0, z),
                scale=(1, 1, 0.9))
    m.cyl(r=0.2, h=0.1, seg=8, color="chocolate_dark", rot=(90, 0, 0), loc=(0, -0.95, 0.8))
    for x, z in ((0.9, 2.2), (-1.0, 1.6)):
        m.sphere(r=0.14, seg=6, rings=4, color="bee", loc=(x, -0.4, z), scale=(1.3, 1, 1))
