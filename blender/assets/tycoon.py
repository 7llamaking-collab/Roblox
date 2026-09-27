"""Tycoon & simulator game builds: tycoon plots, droppers, conveyors, upgraders,
furnaces and buy buttons; steal-style bases with numbered pedestal slots, laser
doors and a lock button; simulator shops (sell, eggs, upgrades, rebirth), a
leaderboard and zone gates.

Moving / scriptable bits are separate parts: ``_Belt`` (conveyor belts),
``_Ore`` (the block a dropper drops), ``_Laser`` / ``_Lasers``, ``_Button``,
``_Slot1``..``_SlotN`` (pedestals), ``_Barrier``. Everything faces -Y.
"""
import math
import random

from studlib.geo import by_normal, star_pts
from studlib.registry import add
from studlib.tiers import ORDER, TIERS, paint, solid

from commercial import (FL, T, blk, booth, counter, fridge_c, fryer, grill, register, sign, stool, stove, table2,
                        table4, text, text_width, prep_table, sink_c, soda_fountain, menu_board, potted_plant)

CAT = "Tycoon"


def reg(name, fn, sub="Tycoon", split=True, tags=()):
    add(name, CAT, fn, sub=sub, split=split, tags=list(tags) + ["tycoon"])


# ----------------------------------------------------------------------------
# tycoon pieces
# ----------------------------------------------------------------------------
def conveyor(m, L=12.0, w=4.0, h=2.4, belt="rubber", frame="stainless", arrows="neon_yellow"):
    """Straight conveyor along +Y (items travel towards +Y); belt is its own part."""
    for s in (-1, 1):
        blk(m, (0.4, L, 1.2), (s * (w / 2 + 0.2), 0, h - 0.2), frame, bev=0.05)
        blk(m, (0.3, L, 0.6), (s * (w / 2 + 0.25), 0, h + 0.7), "plastic_yellow")
        for y in (-L / 2 + 1.0, L / 2 - 1.0):
            blk(m, (0.4, 0.4, h - 0.8), (s * (w / 2 + 0.2), y, (h - 0.8) / 2), "charcoal")
    for k in range(int(L / 1.5)):
        m.cyl(r=0.35, h=w, seg=6, color="steel", rot=(0, 90, 0), loc=(0, -L / 2 + 0.75 + k * 1.5, h - 0.35))
    with m.group("Belt"):
        blk(m, (w, L, 0.25), (0, 0, h), belt)
        for k in range(int(L / 3.0)):
            m.prism([(-0.8, 0), (0, 0.9), (0.8, 0), (0.45, 0), (0, 0.45), (-0.45, 0)], depth=0.05, color=arrows,
                    loc=(0, -L / 2 + 1.2 + k * 3.0, h + 0.15))


def conveyor_corner(m, w=4.0, h=2.4):
    """Quarter turn: in from -Y, out towards +X."""
    R = w / 2 + 2.0
    with m.group("Belt"):
        m.torus(R=R, r=w / 2, seg=6, rseg=4, arc=90, color="rubber", loc=(-R + w / 2 + 2.0, 0, h),
                scale=(1, 1, 0.06), rot=(0, 0, -90))
    for k in range(7):
        a = math.radians(-90 + k * 15)
        blk(m, (0.4, 0.8, 1.2), (-R + w / 2 + 2.0 + (R + w / 2 + 0.2) * math.cos(a), (R + w / 2 + 0.2) * math.sin(a),
                                 h - 0.2), "stainless", rot=(0, 0, math.degrees(a)))
    blk(m, (0.5, 0.5, h - 0.8), (-R + w / 2 + 2.0 + R * 0.7, -R * 0.7, (h - 0.8) / 2), "charcoal")


def dropper(m, T, tier, h=10.0):
    """A tycoon dropper on a tower; the block it spits out is the separate ``_Ore`` part."""
    blk(m, (4.0, 4.0, 1.0), (0, 0, 0.5), "charcoal", bev=0.1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            blk(m, (0.6, 0.6, h - 2.0), (sx * 1.4, sy * 1.4, (h - 2.0) / 2 + 1.0), T["dark"])
    for z in (3.0, 6.0):
        blk(m, (3.4, 3.4, 0.3), (0, 0, z), T["dark"])
    m.box((4.4, 4.4, 3.0), bevel=0.2, loc=(0, 0, h), **paint(T, "main", "z", h - 1.5, h + 1.5))
    m.lathe([(1.8, h - 1.5), (0.7, h - 3.0), (0.6, h - 3.6), (0, h - 3.6)], seg=4, color=T["dark"], rot=(0, 0, 45))
    blk(m, (1.2, 1.2, 0.4), (0, 0, h - 3.7), T["accent"])
    text(m, tier[0], 0, -2.22, h, px=0.35, depth=0.1, col=solid(T, "light", "white"))
    blk(m, (4.6, 4.6, 0.4), (0, 0, h + 1.7), T["accent"], bev=0.08)
    with m.group("Ore"):
        blk(m, (1.0, 1.0, 1.0), (0, 0, h - 5.0), solid(T, "gem", "gold"), bev=0.15)


def upgrader(m, mult="X2", col="neon_blue", frame="plastic_purple"):
    for s in (-1, 1):
        blk(m, (1.2, 2.0, 7.0), (s * 3.0, 0, 3.5), frame, bev=0.12)
    blk(m, (7.2, 2.0, 1.4), (0, 0, 7.4), frame, bev=0.12)
    text(m, mult, 0, -1.02, 7.4, px=0.3, depth=0.1, col="white")
    with m.group("Laser"):
        blk(m, (4.8, 0.2, 3.8), (0, 0, 4.4), col)
        for z in (3.0, 4.4, 5.8):
            blk(m, (4.8, 0.3, 0.12), (0, 0, z), "white")


def furnace(m):
    blk(m, (6.0, 5.0, 5.0), (0, 0, 2.5), "brick_dark", bev=0.15)
    blk(m, (4.4, 0.4, 2.4), (0, -2.4, 2.8), "lava")
    blk(m, (3.6, 0.5, 1.6), (0, -2.5, 2.6), "fire")
    blk(m, (6.4, 5.4, 0.6), (0, 0, 5.2), "stone_dark", bev=0.1)
    blk(m, (1.6, 1.6, 4.0), (1.5, 1.0, 7.4), "brick_dark")
    blk(m, (2.0, 2.0, 0.4), (1.5, 1.0, 9.5), "stone_dark")
    text(m, "SELL", 0, -2.62, 4.6, px=0.22, depth=0.1, col="gold_light")


def cash_collector(m, col="cash"):
    blk(m, (3.0, 3.0, 0.6), (0, 0, 0.3), "charcoal", bev=0.1)
    with m.group("Button"):
        blk(m, (2.6, 2.6, 0.3), (0, 0, 0.75), col, bev=0.08)
        text(m, "$", 0, 0.0, 0.95, px=0.25, depth=0.05, col="white")
    blk(m, (1.0, 1.0, 3.6), (0, 2.0, 1.8), "charcoal", bev=0.1)
    blk(m, (3.4, 0.6, 2.2), (0, 2.0, 4.4), "charcoal", bev=0.1)
    blk(m, (3.0, 0.1, 1.8), (0, 1.66, 4.4), "black")
    text(m, "$0", 0, 1.6, 4.4, px=0.25, depth=0.05, col="neon_green")


def buy_button(m, price="$100", col="plastic_green", label=None):
    m.cyl(r=2.0, h=0.5, seg=8, color="charcoal", loc=(0, 0, 0.25))
    with m.group("Button"):
        m.cyl(r=1.6, h=0.35, seg=8, color=col, loc=(0, 0, 0.65))
    blk(m, (0.25, 0.25, 4.0), (0, 1.6, 2.0), "charcoal")
    w = max(text_width(price, 0.3), text_width(label, 0.2) if label else 0) + 1.0
    blk(m, (w, 0.4, 2.8 if label else 2.0), (0, 1.6, 4.6), col, bev=0.1)
    text(m, price, 0, 1.38, 4.3 if label else 4.6, px=0.3, depth=0.08, col="white")
    if label:
        text(m, label, 0, 1.38, 5.4, px=0.2, depth=0.08, col="white")


def owner_door(m, W=14.0):
    for s in (-1, 1):
        blk(m, (2.0, 2.0, 10.0), (s * (W / 2 + 1.0), 0, 5.0), "stone", bev=0.15)
        blk(m, (2.4, 2.4, 0.6), (s * (W / 2 + 1.0), 0, 10.2), "stone_dark", bev=0.1)
    blk(m, (W + 4.4, 2.0, 2.0), (0, 0, 11.4), "stone_dark", bev=0.15)
    sign(m, "OWNER", 0, -1.0, 11.4, board="wood_dark", letters="white", px=0.3, depth=0.3)
    with m.group("Laser"):
        for k in range(6):
            blk(m, (W, 0.15, 0.15), (0, 0, 1.2 + k * 1.6), "neon_red")
        blk(m, (W, 0.05, 9.4), (0, 0, 5.2), "neon_red")
    m.cyl(r=1.8, h=0.3, seg=8, color="neon_green", loc=(0, -4.0, 0.15))


for _i, _tier in enumerate(ORDER):
    reg(f"{_tier}Dropper", (lambda m, t=_tier: dropper(m, TIERS[t], t)), sub="Droppers",
        tags=["tiered", _tier.lower()])
reg("Conveyor", lambda m: conveyor(m, 12.0), sub="Conveyors")
reg("LongConveyor", lambda m: conveyor(m, 24.0), sub="Conveyors")
reg("ConveyorCorner", conveyor_corner, sub="Conveyors")
reg("Upgrader", lambda m: upgrader(m), sub="Upgraders")
reg("MegaUpgrader", lambda m: upgrader(m, "X5", "neon_pink", "gold"), sub="Upgraders")
reg("UltraUpgrader", lambda m: upgrader(m, "X10", "neon_green", "plastic_black"), sub="Upgraders")
reg("Furnace", furnace, sub="Collectors", split=False)
reg("CashCollector", cash_collector, sub="Collectors")
reg("BuyButton", lambda m: buy_button(m, "$100"), sub="Buttons")
reg("BuyButtonExpensive", lambda m: buy_button(m, "$5000", "plastic_blue"), sub="Buttons")
reg("BuyButtonLocked", lambda m: buy_button(m, "LOCKED", "plastic_red"), sub="Buttons")
reg("OwnerDoor", owner_door, sub="Tycoon")


def plot(m, S=80.0, grass="grass", edge="concrete"):
    blk(m, (S, S, 1.0), (0, 0, 0.5), edge)
    m.box((S - 2.0, S - 2.0, 0.1), color=lambda c, n: grass if (math.floor(c.x / 8) + math.floor(c.y / 8)) % 2 else "leaf_light",
          loc=(0, 0, 1.05), cuts={"x": 8.0, "y": 8.0})
    for s in (-1, 1):
        blk(m, (S, 1.0, 1.2), (0, s * (S / 2 - 0.5), 1.6), "stone_light")
        blk(m, (1.0, S, 1.2), (s * (S / 2 - 0.5), 0, 1.6), "stone_light")


def _dropper_tycoon(m):
    """A full starter layout: plot, owner door, droppers over a conveyor into a furnace, buy buttons."""
    S = 80.0
    plot(m, S)
    with m.at((0, -S / 2 + 2.0, 1.1)):
        owner_door(m, 12.0)
    with m.at((-6.0, 6.0, 1.1)):
        conveyor(m, 36.0)
    for i, tier in enumerate(("Wood", "Stone", "Iron", "Gold")):
        with m.group(f"Dropper{i + 1}"):
            with m.at((-10.2, -6.0 + i * 8.0, 1.1), 90):
                dropper(m, TIERS[tier], tier, h=9.0)
    with m.group("Upgrader"):
        with m.at((-6.0, 16.0, 1.1)):
            upgrader(m)
    with m.at((-6.0, 27.0, 1.1)):
        furnace(m)
    with m.group("Collector"):
        with m.at((6.0, 26.0, 1.1)):
            cash_collector(m)
    for i, (p, c) in enumerate((("$25", "plastic_green"), ("$100", "plastic_green"), ("$500", "plastic_blue"),
                                ("$2500", "plastic_purple"), ("$10000", "gold"))):
        with m.group(f"Button{i + 1}"):
            with m.at((12.0 + (i % 3) * 7.0, -18.0 + (i // 3) * 8.0, 1.1)):
                buy_button(m, p, c)


reg("DropperTycoonPlot", _dropper_tycoon, sub="Plots")


def _restaurant_tycoon(m):
    """Restaurant-tycoon style plot: open-top restaurant (low walls) with a kitchen, dining room,
    counter and a buy button for every station."""
    S = 80.0
    plot(m, S, grass="grass")
    W, D = 52.0, 40.0
    y0 = -4.0
    blk(m, (W, D, 0.4), (0, y0, 1.3), "tile_cream")
    m.box((W - 2.0, D - 2.0, 0.05), color=lambda c, n: "white" if (math.floor(c.x / 3) + math.floor(c.y / 3)) % 2 else "wall_red",
          loc=(0, y0, 1.52), cuts={"x": 3.0, "y": 3.0})
    for s in (-1, 1):
        blk(m, (1.0, D, 4.0), (s * (W / 2 - 0.5), y0, 3.5), "wall_cream", bev=0.05)
    blk(m, (W, 1.0, 4.0), (0, y0 + D / 2 - 0.5, 3.5), "wall_cream", bev=0.05)
    for s in (-1, 1):
        blk(m, (W / 2 - 4.0, 1.0, 4.0), (s * (W / 4 + 2.0), y0 - D / 2 + 0.5, 3.5), "wall_cream", bev=0.05)
    z = 1.5
    with m.group("Kitchen"):
        for i, (x, fn) in enumerate(((-20.0, stove), (-15.6, grill), (-11.8, fryer), (-8.0, lambda m: fridge_c(m, 4.0)),
                                     (-3.6, lambda m: sink_c(m, 4.0)))):
            with m.at((x, y0 + D / 2 - 2.4, z)):
                fn(m)
        with m.at((-12.0, y0 + 11.0, z)):
            prep_table(m, 6.0)
    with m.group("Counter"):
        with m.at((6.0, y0 + 6.0, z)):
            counter(m, 16.0, top="white", body="wall_red")
        register(m, 2.0, y0 + 6.2, z + 3.5)
        register(m, 9.0, y0 + 6.2, z + 3.5)
        with m.at((17.0, y0 + 6.0, z)):
            counter(m, 5.0, top="stainless", body="stainless")
            soda_fountain(m)
    with m.group("Dining"):
        for x in (-16.0, -6.0, 4.0, 14.0):
            with m.at((x, y0 - 10.0, z)):
                table4(m, top="white", seat="wall_red")
        for x in (-16.0, 14.0):
            with m.at((x, y0 - 2.0, z)):
                table2(m, top="white", seat="plastic_yellow")
    with m.at((0, -S / 2 + 2.0, 1.1)):
        owner_door(m, 12.0)
    labels = (("STOVE", "$50"), ("GRILL", "$150"), ("FRYER", "$300"), ("TABLES", "$500"), ("SODA", "$800"),
              ("REGISTER", "$1200"))
    for i, (lab, price) in enumerate(labels):
        with m.group(f"Button{i + 1}"):
            with m.at((-25.0 + i * 10.0, -S / 2 + 9.0, 1.1)):
                buy_button(m, price, "plastic_green", lab)


reg("RestaurantTycoonPlot", _restaurant_tycoon, sub="Plots")
reg("TycoonPlot", lambda m: (plot(m, 80.0), _plot_gate(m)), sub="Plots")


def _plot_gate(m):
    with m.at((0, -38.0, 1.1)):
        owner_door(m, 12.0)


# ----------------------------------------------------------------------------
# steal-style base: pedestal slots, laser door, lock button
# ----------------------------------------------------------------------------
def pedestal(m, col="neon_blue", top="white", base="charcoal"):
    blk(m, (4.4, 4.4, 1.0), (0, 0, 0.5), base, bev=0.1)
    blk(m, (3.6, 3.6, 1.6), (0, 0, 1.8), top, bev=0.12)
    blk(m, (3.8, 3.8, 0.3), (0, 0, 2.75), col)
    blk(m, (3.2, 3.2, 0.2), (0, 0, 3.0), top)
    blk(m, (2.6, 1.4, 0.2), (0, -3.2, 0.1), "cash")         # collect pad


def laser_door(m, W=12.0, h=9.0, col="neon_red"):
    for s in (-1, 1):
        blk(m, (1.6, 1.6, h + 1.0), (s * (W / 2 + 0.8), 0, (h + 1.0) / 2), "charcoal", bev=0.12)
        for k in range(5):
            blk(m, (0.4, 0.6, 0.4), (s * (W / 2 + 0.05), 0, 1.2 + k * 1.8), "stainless")
    with m.group("Lasers"):
        for k in range(5):
            blk(m, (W, 0.12, 0.12), (0, 0, 1.2 + k * 1.8), col)
        blk(m, (W, 0.04, h - 0.6), (0, 0, h / 2 + 0.3), col)


def lock_button(m):
    blk(m, (2.0, 2.0, 0.6), (0, 0, 0.3), "charcoal", bev=0.1)
    blk(m, (0.8, 0.8, 3.0), (0, 0, 2.1), "charcoal")
    blk(m, (3.0, 1.2, 1.6), (0, 0, 4.2), "charcoal", bev=0.1)
    blk(m, (2.6, 0.1, 1.2), (0, -0.62, 4.2), "black")
    text(m, "LOCK", 0, -0.66, 4.2, px=0.16, depth=0.05, col="neon_red")
    with m.group("Button"):
        m.cyl(r=0.9, h=0.5, seg=8, color="plastic_red", rot=(-35, 0, 0), loc=(0, -0.4, 3.1))


def carpet_conveyor(m, L=40.0, w=5.0):
    with m.group("Belt"):
        blk(m, (w, L, 0.3), (0, 0, 0.35), "velvet")
        for k in range(int(L / 4)):
            m.prism([(-0.8, 0), (0, 0.9), (0.8, 0), (0.45, 0), (0, 0.45), (-0.45, 0)], depth=0.05, color="brass",
                    loc=(0, -L / 2 + 2.0 + k * 4.0, 0.52))
    blk(m, (w + 1.0, L, 0.2), (0, 0, 0.1), "brass")
    for s in (-1, 1):
        for k in range(int(L / 4) + 1):
            y = -L / 2 + k * 4.0
            m.cyl(r=0.4, h=0.2, seg=8, color="brass", loc=(s * (w / 2 + 1.0), y, 0.1))
            m.cyl(r=0.12, h=3.0, seg=6, color="brass", loc=(s * (w / 2 + 1.0), y, 1.6))
            if k:
                m.tube([(s * (w / 2 + 1.0), y - 4.0, 2.9), (s * (w / 2 + 1.0), y - 2.0, 2.3), (s * (w / 2 + 1.0), y, 2.9)],
                       [0.1] * 3, seg=4, color="velvet")
    for s in (-1, 1):   # spawn arch at the start
        blk(m, (1.2, 1.2, 8.0), (s * (w / 2 + 2.0), -L / 2, 4.0), "gold", bev=0.1)
    blk(m, (w + 5.2, 1.2, 1.4), (0, -L / 2, 8.6), "gold", bev=0.1)


reg("DisplayPedestal", lambda m: pedestal(m), sub="StealBase", split=False)
reg("GoldPedestal", lambda m: pedestal(m, "gold_light", "gold", "gold_dark"), sub="StealBase", split=False)
reg("RainbowPedestal", lambda m: (pedestal(m, "rb_pink", "white", "charcoal"),
                                  m.box((3.8, 3.8, 0.3), color=lambda c, n: ["rb_red", "rb_orange", "rb_yellow", "rb_green",
                                                                             "rb_blue", "rb_purple"][int((c.x + 1.9) / 0.64) % 6],
                                        loc=(0, 0, 2.75), cuts={"x": 0.64})), sub="StealBase", split=False)
reg("LaserDoor", laser_door, sub="StealBase")
reg("LockButton", lock_button, sub="StealBase")
reg("RedCarpetConveyor", carpet_conveyor, sub="StealBase")


def _steal_base(m, floors=2, col="neon_blue", wall="wall_sky", trim="white"):
    """A steal-style base: walled plot, laser door + lock button at the entrance, numbered
    pedestal slots (each its own part) and an upper floor with more slots."""
    W, D = 40.0, 52.0
    blk(m, (W, D, 1.0), (0, 0, 0.5), "stone_dark", bev=0.1)
    m.box((W - 2.0, D - 2.0, 0.05), color=lambda c, n: "white" if (math.floor(c.x / 4) + math.floor(c.y / 4)) % 2 else "tile_gray",
          loc=(0, 0, 1.02), cuts={"x": 4.0, "y": 4.0})
    for s in (-1, 1):
        blk(m, (1.0, D, 6.0), (s * (W / 2 - 0.5), 0, 4.0), wall, bev=0.05)
        blk(m, (1.4, D + 0.4, 0.6), (s * (W / 2 - 0.5), 0, 7.2), trim, bev=0.05)
    blk(m, (W, 1.0, 6.0), (0, D / 2 - 0.5, 4.0), wall, bev=0.05)
    for s in (-1, 1):
        blk(m, (W / 2 - 7.0, 1.0, 6.0), (s * (W / 4 + 3.5), -D / 2 + 0.5, 4.0), wall, bev=0.05)
    with m.at((0, -D / 2 + 0.5, 1.0)):
        laser_door(m, 12.0, 8.0)
    with m.group("LockButton"):
        with m.at((10.0, -D / 2 + 4.0, 1.0)):
            lock_button(m)
    slot = 0
    rows = [(-W / 2 + 5.0, 90), (W / 2 - 5.0, -90)]
    for x, ang in rows:
        for k in range(5):
            slot += 1
            with m.group(f"Slot{slot}"):
                with m.at((x, -D / 2 + 10.0 + k * 7.5, 1.0), ang):
                    pedestal(m, col)
                    text(m, str(slot), 0, -2.22, 1.8, px=0.25, depth=0.05, col="charcoal")
    if floors > 1:
        z2 = 12.0
        with m.group("Floor2"):
            blk(m, (W, D * 0.55, 1.0), (0, D / 2 - D * 0.275, z2 - 0.5), "stone_dark", bev=0.1)
            for sx in (-1, 1):
                for sy in (0.05, 0.5, 0.95):
                    y = D / 2 - D * 0.55 * sy
                    blk(m, (1.4, 1.4, z2 - 1.0), (sx * (W / 2 - 1.5), y, (z2 - 1.0) / 2 + 0.5), trim)
            for s in (-1, 1):
                blk(m, (1.0, D * 0.55, 3.0), (s * (W / 2 - 0.5), D / 2 - D * 0.275, z2 + 1.5), wall)
            blk(m, (W, 1.0, 3.0), (0, D / 2 - 0.5, z2 + 1.5), wall)
            for s in (-1, 1):
                blk(m, (W / 2 - 3.5, 0.6, 1.2), (s * (W / 4 + 1.75), D / 2 - D * 0.55 + 0.3, z2 + 0.6), "glass")
            for k in range(12):   # stairs up to the front edge of the upper floor
                blk(m, (6.0, 1.4, 0.5), (0, -17.0 + k * 1.2, 1.25 + k * (z2 - 1.0) / 12), "stone_light")
        for k in range(4):
            slot += 1
            with m.group(f"Slot{slot}"):
                with m.at(((-15.0, -8.0, 8.0, 15.0)[k], D / 2 - 5.0, z2), 180):
                    pedestal(m, "neon_pink")
                    text(m, str(slot), 0, -2.22, 1.8, px=0.25, depth=0.05, col="charcoal")
    with m.at((0, -D / 2 - 26.0, 0)):
        carpet_conveyor(m, 40.0)
    blk(m, (8.0, 6.0, 0.3), (0, -D / 2 - 3.0, 0.15), "velvet")


reg("StealBase", lambda m: _steal_base(m), sub="StealBase")
reg("RedStealBase", lambda m: _steal_base(m, col="neon_red", wall="wall_red", trim="white"), sub="StealBase")
reg("GoldStealBase", lambda m: _steal_base(m, col="gold_light", wall="gold", trim="gold_dark"), sub="StealBase")


# ----------------------------------------------------------------------------
# simulator builds
# ----------------------------------------------------------------------------
def booth_hut(m, W=14.0, D=10.0, H=9.0, wall="wood_light", roof="roof_red", sign_txt="SHOP", board="wood_dark",
              letters="white", counter_col="wood_mid"):
    """Open-front shop hut with a counter (face -Y)."""
    blk(m, (W + 2.0, D + 2.0, 0.8), (0, 0, 0.4), "stone", bev=0.1)
    for s in (-1, 1):
        blk(m, (1.0, D, H), (s * (W / 2 - 0.5), 0, 0.8 + H / 2), wall, bev=0.05)
    blk(m, (W, 1.0, H), (0, D / 2 - 0.5, 0.8 + H / 2), wall, bev=0.05)
    m.prism([(-(D / 2 + 1.2), 0), (D / 2 + 1.2, 0), (0, 3.6)], depth=W + 2.0, color=roof, rot=(90, 0, 90),
            loc=(0, 0, 0.8 + H), smooth=False)
    with m.at((0, -D / 2 + 1.6, 0.8)):
        counter(m, W - 2.0, top="wood_light", body=counter_col)
    sign(m, sign_txt, 0, -D / 2 - 1.2, 0.8 + H + 1.0, board=board, letters=letters, px=0.5)
    return 0.8


def _sell_shop(m):
    z = booth_hut(m, 14.0, 10.0, 8.0, wall="gold_light", roof="roof_red", sign_txt="SELL", board="gold_dark")
    for x in (-3.0, 0.0, 3.0):
        with m.at((x, -3.4, z + 3.5)):
            for k in range(4):
                m.cyl(r=0.6, h=0.2, seg=8, color="gold", loc=(0, 0, 0.1 + k * 0.22))
    register(m, 4.5, -3.2, z + 3.5)
    with m.group("SellPad"):
        m.cyl(r=3.0, h=0.3, seg=8, color="gold", loc=(0, -10.0, 0.15))
        m.prism(star_pts(1.2, 0.5, 5), depth=0.2, color="gold_light", loc=(0, -10.0, 0.4))


def _egg_hatchery(m):
    blk(m, (22.0, 16.0, 1.0), (0, 0, 0.5), "stone", bev=0.1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            blk(m, (1.2, 1.2, 10.0), (sx * 10.0, sy * 7.0, 6.0), "white")
    blk(m, (24.0, 18.0, 1.0), (0, 0, 11.4), "roof_blue", bev=0.2)
    sign(m, "EGGS", 0, -9.1, 13.4, board="plastic_blue", letters="white", px=0.6)
    for i, (c, band) in enumerate((("white", "plastic_green"), ("plastic_blue", "white"), ("gold", "gold_light"))):
        x = -7.0 + i * 7.0
        with m.group(f"Egg{i + 1}"):
            blk(m, (4.0, 4.0, 1.4), (x, 1.0, 1.7), "charcoal", bev=0.1)
            m.lathe([(0, 0), (1.3, 0.2), (1.7, 1.3), (1.5, 2.6), (0.9, 3.5), (0, 3.8)], seg=8,
                    color=lambda cc, n, c=c, b=band: b if 1.5 < cc.z - 2.4 < 2.1 else c, loc=(x, 1.0, 2.4),
                    cuts={"z": [3.9, 4.5]})
        blk(m, (3.4, 0.4, 1.4), (x, -1.4, 7.6), "wood_dark", bev=0.08)
        text(m, ["$50", "$500", "$5K"][i], x, -1.62, 7.6, px=0.22, depth=0.06, col="white")
        blk(m, (0.2, 0.2, 3.8), (x, -1.4, 9.4), "charcoal")


def _upgrade_shop(m):
    z = booth_hut(m, 16.0, 10.0, 8.0, wall="plastic_purple", roof="roof_blue", sign_txt="UPGRADES", board="plastic_blue")
    for i, c in enumerate(("potion_red", "potion_blue", "potion_green", "potion_yellow", "potion_purple")):
        with m.at((-5.0 + i * 2.5, -3.4, z + 3.5)):
            m.lathe([(0, 0), (0.5, 0.05), (0.6, 0.6), (0.3, 1.0), (0.25, 1.4), (0, 1.4)], seg=6,
                    color=lambda cc, n, c=c: c if cc.z < 0.8 else "glass", cuts={"z": [0.8]})
            m.cyl(r=0.25, h=0.3, seg=6, color="cork", loc=(0, 0, 1.5))


def _rebirth_shrine(m):
    for k, (s, col) in enumerate(((16.0, "stone_dark"), (12.0, "stone"), (8.0, "stone_light"))):
        blk(m, (s, s, 1.0), (0, 0, 0.5 + k * 1.0), col, bev=0.1)
    with m.group("Portal"):
        m.torus(R=4.0, r=0.6, seg=8, rseg=4, color="gold", rot=(90, 0, 0), loc=(0, 0, 7.8))
        m.cyl(r=3.4, h=0.2, seg=8, color=lambda c, n: ["neon_purple", "amethyst", "neon_pink"][
            int((math.hypot(c.x, c.z - 7.8)) / 1.2) % 3], rot=(90, 0, 0), loc=(0, 0, 7.8))
    for s in (-1, 1):
        blk(m, (1.4, 1.4, 5.0), (s * 5.0, 0, 5.5), "gold", bev=0.1)
        m.crystal(r=0.6, h=2.0, color="amethyst", loc=(s * 5.0, 0, 8.0))
    sign(m, "REBIRTH", 0, -1.0, 14.0, board="plastic_purple", letters="gold_light", px=0.45)


def _leaderboard(m, rows=10):
    for s in (-1, 1):
        blk(m, (1.0, 1.0, 16.0), (s * 7.5, 0.6, 8.0), "charcoal", bev=0.1)
    with m.group("Board"):
        blk(m, (14.0, 0.6, 12.0), (0, 0, 10.0), "wall_navy", bev=0.15)
        blk(m, (14.4, 0.4, 12.4), (0, 0.2, 10.0), "gold", bev=0.1)
        text(m, "TOP 10", 0, -0.32, 14.9, px=0.3, depth=0.1, col="gold_light")
        for r in range(rows):
            z = 13.3 - r * 0.95
            col = ["gold", "silver", "bronze"][r] if r < 3 else "white"
            text(m, str(r + 1), -5.6, -0.32, z, px=0.13, depth=0.08, col=col)
            blk(m, (6.0 - r * 0.3, 0.1, 0.5), (-1.2 - r * 0.15, -0.34, z), "wall_sky" if r % 2 else "white")
            blk(m, (2.0, 0.1, 0.5), (4.8, -0.34, z), "neon_green")


def _zone_gate(m, price="$1000", col="neon_blue"):
    for s in (-1, 1):
        blk(m, (4.0, 4.0, 16.0), (s * 12.0, 0, 8.0), "stone", bev=0.2)
        blk(m, (4.8, 4.8, 1.2), (s * 12.0, 0, 16.4), "stone_dark", bev=0.12)
        blk(m, (4.4, 4.4, 1.0), (s * 12.0, 0, 0.5), "stone_dark", bev=0.12)
    blk(m, (28.0, 3.0, 3.0), (0, 0, 17.5), "stone_dark", bev=0.2)
    sign(m, price, 0, -1.5, 17.5, board="gold", letters="white", px=0.4, depth=0.3)
    with m.group("Barrier"):
        blk(m, (20.0, 0.3, 15.8), (0, 0, 8.0), col)
        for k in range(6):
            blk(m, (20.0, 0.4, 0.15), (0, 0, 1.5 + k * 2.6), "white")
    with m.at((0, -0.6, 8.0)):
        blk(m, (2.4, 0.4, 2.0), (0, 0, 0), "gold", bev=0.1)
        m.torus(R=0.8, r=0.2, seg=8, arc=180, color="gold", rot=(90, 0, 0), loc=(0, 0.1, 1.0))


def _daily_chest(m):
    blk(m, (8.0, 8.0, 1.2), (0, 0, 0.6), "stone", bev=0.12)
    blk(m, (6.0, 6.0, 1.0), (0, 0, 1.7), "gold_dark", bev=0.1)
    with m.at((0, 0, 2.2)):
        blk(m, (3.6, 2.6, 2.0), (0, 0, 1.0), "wood_mid", bev=0.1)
        m.cyl(r=1.3, h=3.6, seg=8, color="wood_mid", rot=(0, 90, 0), loc=(0, 0, 2.0),
              deform=lambda co: co.__class__((min(co.x, 0.02), co.y, co.z)))
        for x in (-1.4, 0, 1.4):
            blk(m, (0.3, 2.7, 2.1), (x, 0, 1.0), "gold")
        blk(m, (0.8, 0.3, 0.9), (0, -1.4, 1.9), "gold_light")
    sign(m, "DAILY", 0, -3.0, 9.0, board="plastic_red", letters="white", px=0.4)
    blk(m, (0.4, 0.4, 3.4), (0, -2.5, 5.9), "charcoal")


def _quest_board(m):
    for s in (-1, 1):
        blk(m, (0.8, 0.8, 9.0), (s * 5.0, 0, 4.5), "wood_dark", bev=0.08)
    blk(m, (10.8, 0.6, 6.0), (0, 0, 5.5), "wood_mid", bev=0.1)
    m.prism([(-6.0, 0), (6.0, 0), (0, 2.0)], depth=1.6, color="roof_red", rot=(90, 0, 0), loc=(0, 0, 9.0))
    text(m, "QUESTS", 0, -0.32, 7.9, px=0.22, depth=0.08, col="gold_light")
    rnd = random.Random(7)
    for i in range(3):
        for k in range(2):
            x, z = -3.4 + i * 3.4, 6.2 - k * 2.3
            blk(m, (2.4, 0.08, 1.9), (x, -0.34, z), "paper", rot=(0, rnd.uniform(-6, 6), 0))
            for j in range(3):
                blk(m, (1.6 - j * 0.3, 0.1, 0.12), (x, -0.4, z + 0.5 - j * 0.4), "charcoal")
            blk(m, (0.25, 0.12, 0.25), (x, -0.42, z + 0.9), "plastic_red")


def _shop_stand(m):
    booth_hut(m, 14.0, 10.0, 8.0, wall="plastic_blue", roof="roof_red", sign_txt="SHOP", board="plastic_green")
    for i, c in enumerate(("gold", "diamond", "emerald", "ruby")):
        with m.at((-4.5 + i * 3.0, -3.4, 4.3)):
            blk(m, (1.0, 1.0, 1.0), (0, 0, 0.6), c, rot=(45, 0, 45), bev=0.1)


reg("SellShop", _sell_shop, sub="Simulator")
reg("EggHatchery", _egg_hatchery, sub="Simulator")
reg("UpgradeShop", _upgrade_shop, sub="Simulator", split=False)
reg("RebirthShrine", _rebirth_shrine, sub="Simulator")
reg("Leaderboard", _leaderboard, sub="Simulator")
reg("ZoneGate", lambda m: _zone_gate(m), sub="Simulator")
reg("VIPZoneGate", lambda m: _zone_gate(m, "VIP", "gold_light"), sub="Simulator")
reg("DailyRewardChest", _daily_chest, sub="Simulator", split=False)
reg("QuestBoard", _quest_board, sub="Simulator", split=False)
reg("ShopStand", _shop_stand, sub="Simulator", split=False)
