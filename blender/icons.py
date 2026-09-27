"""Render the UI icon set (512 px, transparent) from the stud-style models.

    python3 blender/icons.py                 # all icons -> ui/icons_src/<Name>.png
    python3 blender/icons.py --names Coin,Gem

Most icons are library assets (Coin, Diamond, Egg, Potion...) shot front-on with
brighter icon lighting and no ground; the rest (paw, rebirth arrows, lock, check,
arrows...) are small icon-only models defined below. ``ui/generate.py`` then adds
the outline, shine and shadow for each theme and packs the sprite sheets.
"""
import argparse
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "assets"))

import build  # noqa: E402
from studlib import output, registry, render  # noqa: E402
from studlib.font import text  # noqa: E402
from studlib.geo import Builder, heart_pts, star_pts  # noqa: E402

ROOT = os.path.dirname(HERE)

# icon name -> library asset
LIBRARY = {
    "Coin": "Coin", "Gem": "Diamond", "Cash": "CashStack", "MoneyBag": "MoneyBag", "GoldBars": "GoldBarStack",
    "Star": "Star", "Heart": "Heart", "Energy": "LightningBolt", "Key": "Key", "Gift": "GiftBox", "Crown": "Crown",
    "Trophy": "Trophy", "Medal": "GoldMedal", "PotionRed": "HealthPotion", "PotionBlue": "ManaPotion",
    "PotionGreen": "LuckPotion", "PotionYellow": "SpeedPotion", "Egg": "CommonEgg", "GoldenEgg": "GoldenEgg",
    "RainbowEgg": "RainbowEgg", "Chest": "GoldChest", "Backpack": "DiamondBackpack", "Settings": "Gear",
    "Codes": "Ticket", "Quests": "Scroll", "Timer": "Hourglass", "Index": "Spellbook", "Shop": "ShoppingCart",
    "Pickaxe": "DiamondPickaxe", "Sword": "DiamondSword", "Shield": "DiamondShield", "FishingRod": "GoldFishingRod",
    "Teleport": "Portal", "World": "Globe", "Map": "TreasureMap", "Boost": "Firework",
    "Dice": "Dice", "Battery": "Battery", "Magnet": "GoldCoinMagnet", "Skull": "Skull", "Pet": "Corgi",
    "Bomb": "CartoonBomb", "Fire": "Campfire",
    "Hammer": "IronHammer", "Bat": "BaseballBat", "Helicopter": "Helicopter", "UFO": "UFO",
    "Mushroom": "Mushroom", "Crate": "GoldLootCrate", "Clock": "WallClock", "Taco": "Taco",
    "Basket": "EggBasket",
}


def _paw(m):
    m.box((2.0, 0.8, 1.7), color="fur_brown", bevel=0.35, loc=(0, 0, 1.0))
    for x, z in ((-1.1, 2.3), (-0.4, 2.8), (0.4, 2.8), (1.1, 2.3)):
        m.box((0.7, 0.8, 0.9), color="fur_brown", bevel=0.22, loc=(x, 0, z))
    m.box((1.4, 0.2, 1.1), color="pink_inner", bevel=0.2, loc=(0, -0.42, 1.0))


def _rebirth(m):
    m.torus(R=1.4, r=0.32, seg=12, rseg=4, arc=280, color="plastic_green", rot=(90, 0, 50), loc=(0, 0, 1.6))
    m.prism([(-0.75, 0), (0.75, 0), (0, 1.0)], depth=0.64, color="plastic_green", rot=(90, 0, 0),
            loc=(1.25, 0, 2.55), scale=1.0)
    m.prism(star_pts(0.45, 0.2, 5), depth=0.6, color="gold_light", rot=(90, 0, 0), loc=(0, 0, 1.6))


def _trade(m):
    for z, s, col in ((2.1, 1, "plastic_green"), (0.9, -1, "plastic_blue")):
        m.box((2.2, 0.6, 0.45), color=col, bevel=0.1, loc=(-0.3 * s, 0, z))
        m.prism([(0, -0.6), (0.9, 0), (0, 0.6)] if s > 0 else [(0, -0.6), (0, 0.6), (-0.9, 0)], depth=0.6, color=col,
                rot=(90, 0, 0), loc=(0.8 * s, 0, z))


def _lock(m, open_=False):
    m.box((2.2, 1.0, 1.8), color="gold", bevel=0.25, loc=(0, 0, 1.0))
    m.torus(R=0.72, r=0.18, seg=10, rseg=4, arc=180, color="silver", rot=(90, 0, 0),
            loc=(0.5 if open_ else 0, 0, 1.9 + (0.3 if open_ else 0)))
    for s in (-1, 1):
        if not open_ or s > 0:
            m.box((0.36, 0.36, 0.5), color="silver", loc=(s * 0.72 + (0.5 if open_ else 0), 0, 1.9 + (0.3 if open_ else 0)))
    m.cyl(r=0.22, h=0.2, seg=8, color="black", rot=(90, 0, 0), loc=(0, -0.5, 1.15))
    m.box((0.16, 0.2, 0.4), color="black", loc=(0, -0.5, 0.85))


def _check(m):
    m.prism([(-1.2, 0.2), (-0.6, 0.8), (-0.2, 0.3), (1.0, 1.7), (1.6, 1.1), (-0.2, -0.9)], depth=0.7,
            color="plastic_green", rot=(90, 0, 0), bevel=0.08, loc=(0, 0, 1.0))


def _cross(m):
    for a in (45, -45):
        m.box((2.8, 0.7, 0.75), color="plastic_red", bevel=0.15, rot=(0, a, 0), loc=(0, 0, 1.5))


def _plus(m, minus=False):
    m.box((2.6, 0.7, 0.8), color="plastic_green" if not minus else "plastic_red", bevel=0.15, loc=(0, 0, 1.5))
    if not minus:
        m.box((0.8, 0.7, 2.6), color="plastic_green", bevel=0.15, loc=(0, 0, 1.5))


def _arrow(m, rot=0.0, col="plastic_yellow"):
    with m.at((0, 0, 1.5)):
        m.prism([(-0.5, -1.4), (0.5, -1.4), (0.5, 0.1), (1.2, 0.1), (0, 1.5), (-1.2, 0.1), (-0.5, 0.1)], depth=0.7,
                color=col, rot=(90, rot, 0), bevel=0.08)


def _dumbbell(m):
    m.cyl(r=0.2, h=3.6, seg=8, color="chrome", rot=(0, 90, 0), loc=(0, 0, 1.2))
    for s in (-1, 1):
        m.box((0.5, 1.4, 1.8), color="plastic_black", bevel=0.12, loc=(s * 1.2, 0, 1.2))
        m.box((0.35, 1.1, 1.3), color="plastic_red", bevel=0.1, loc=(s * 1.6, 0, 1.2))


def _music(m):
    for x in (-0.8, 0.9):
        m.box((0.9, 0.6, 0.7), color="plastic_purple", bevel=0.2, loc=(x, 0, 0.6), rot=(0, -20, 0))
        m.box((0.22, 0.4, 2.4), color="plastic_purple", loc=(x + 0.35, 0, 1.8))
    m.box((1.95, 0.4, 0.45), color="plastic_purple", loc=(0.2, 0, 3.0), rot=(0, -10, 0))


def _speaker(m):
    m.box((0.9, 0.9, 1.2), color="charcoal", bevel=0.12, loc=(-0.9, 0, 1.5))
    m.lathe([(0.55, 0), (1.3, 1.0), (0, 1.0)], seg=4, color="charcoal", rot=(0, 90, 0), loc=(-0.5, 0, 1.5))
    for r in (0.8, 1.35):
        m.torus(R=r, r=0.12, seg=8, arc=100, color="plastic_blue", rot=(90, 0, -50), loc=(0.6, 0, 1.5))


def _home(m):
    m.box((2.2, 1.0, 1.6), color="wall_cream", bevel=0.12, loc=(0, 0, 0.8))
    m.prism([(-1.6, 0), (1.6, 0), (0, 1.4)], depth=1.2, color="plastic_red", rot=(90, 0, 0), loc=(0, 0, 1.55))
    m.box((0.6, 0.2, 1.0), color="wood_dark", loc=(0, -0.5, 0.5))
    m.box((0.5, 0.5, 0.8), color="brick", loc=(0.8, 0, 2.4))


def _friends(m):
    for x, col, s in ((-0.7, "plastic_blue", 0.85), (0.6, "plastic_green", 1.0)):
        m.box((0.9 * s, 0.8 * s, 0.9 * s), color="pink_skin", bevel=0.25 * s, loc=(x, 0.2 * (x < 0), 2.1 * s))
        m.box((1.6 * s, 0.9 * s, 1.3 * s), color=col, bevel=0.3 * s, loc=(x, 0.2 * (x < 0), 0.8 * s))


def _glyph(ch, col):
    def f(m):
        text(m, ch, 0, 0, 1.5, px=0.55, depth=0.7, col=col)
    return f


def _search(m):
    m.torus(R=0.9, r=0.22, seg=10, rseg=4, color="charcoal", rot=(90, 0, 0), loc=(-0.3, 0, 1.9))
    m.cyl(r=0.72, h=0.1, seg=10, color="glass", rot=(90, 0, 0), loc=(-0.3, 0, 1.9))
    m.box((0.45, 0.5, 1.4), color="charcoal", bevel=0.1, rot=(0, 45, 0), loc=(0.75, 0, 0.8))


def _bell(m):
    m.lathe([(0, 0.4), (1.3, 0.4), (1.2, 0.7), (0.9, 1.3), (0.8, 2.3), (0.4, 2.8), (0, 2.9)], seg=8, color="gold")
    m.box((0.4, 0.4, 0.4), color="gold_dark", bevel=0.12, loc=(0, 0, 0.3))
    m.box((0.3, 0.3, 0.4), color="gold_dark", loc=(0, 0, 3.05))


def _calendar(m):
    m.box((2.4, 0.5, 2.4), color="white", bevel=0.15, loc=(0, 0, 1.3))
    m.box((2.45, 0.55, 0.7), color="plastic_red", bevel=0.12, loc=(0, 0, 2.25))
    for x in (-0.6, 0.6):
        m.box((0.2, 0.3, 0.6), color="charcoal", loc=(x, 0, 2.7))
    for i in range(3):
        for j in range(2):
            m.box((0.45, 0.1, 0.4), color="plastic_red" if (i, j) == (2, 1) else "lightgray",
                  loc=(-0.65 + i * 0.65, -0.27, 1.4 - j * 0.6))


def _clover(m):
    """Four heart-shaped leaves with their tips to the middle, and a stem."""
    for a in (45, 135, 225, 315):
        r = math.radians(a)
        m.prism(heart_pts(1.55), depth=0.5, color="leaf", bevel=0.12, rot=(90, 90 - a, 0),
                loc=(0.62 * math.cos(r), 0, 2.0 + 0.62 * math.sin(r)))
    m.box((0.28, 0.3, 1.3), color="leaf_dark", bevel=0.08, rot=(0, -30, 0), loc=(0.35, 0.1, 0.95))
    m.box((0.5, 0.56, 0.5), color="leaf_light", bevel=0.14, loc=(0, -0.05, 2.0))


CUSTOM = {
    "Luck": _clover, "Paw": _paw, "Rebirth": _rebirth, "Trade": _trade, "Lock": _lock, "Unlock": lambda m: _lock(m, True),
    "Check": _check, "Close": _cross, "Plus": _plus, "Minus": lambda m: _plus(m, True),
    "ArrowUp": lambda m: _arrow(m, 0), "ArrowRight": lambda m: _arrow(m, 90),
    "ArrowLeft": lambda m: _arrow(m, -90), "ArrowDown": lambda m: _arrow(m, 180),
    "Upgrade": lambda m: _arrow(m, 0, "plastic_green"), "Strength": _dumbbell, "Music": _music, "Sound": _speaker,
    "Home": _home, "Friends": _friends, "Info": _glyph("I", "plastic_blue"), "Question": _glyph("?", "plastic_blue"),
    "Alert": _glyph("!", "plastic_red"), "Search": _search, "Bell": _bell, "Daily": _calendar,
    "VIP": _glyph("VIP", "gold"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", default="")
    ap.add_argument("--out", default=os.path.join(ROOT, "ui", "icons_src"))
    ap.add_argument("--res", type=int, default=512)
    ap.add_argument("--samples", type=int, default=32)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    build.reset()
    tex_dir = os.path.join(ROOT, "textures")
    output.init(tex_dir)
    build.load_modules()
    by_name = {a["name"]: a for a in registry.ASSETS}
    stage = render.Stage(res=args.res, samples=args.samples)
    stage.ground.hide_render = True
    fill = bpy.data.lights.new("IconFill", "SUN")
    fill.energy = 1.6
    fo = bpy.data.objects.new("IconFill", fill)
    fo.rotation_euler = (math.radians(70), 0, math.radians(20))
    stage.col.objects.link(fo)
    stud_png = os.path.join(tex_dir, "Stud.png")
    studs_mat = render.preview_material(stud_png, 2.0, 0.5)
    wanted = [n.strip() for n in args.names.split(",") if n.strip()]
    items = list(LIBRARY.items()) + [(k, None) for k in CUSTOM]
    for name, src in items:
        if wanted and name not in wanted:
            continue
        b = Builder(name)
        if src:
            by_name[src]["fn"](b)
        else:
            CUSTOM[name](b)
        ob = output.finish(b, origin="center")
        p = os.path.join(args.out, name + ".png")
        stage.shoot([ob], p, direction=(0.42, -1.5, 0.55), studs_mat=studs_mat)
        bpy.data.objects.remove(ob)
        print("icon", name, flush=True)
    print("done icons", flush=True)


if __name__ == "__main__":
    main()
