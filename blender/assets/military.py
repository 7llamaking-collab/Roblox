"""Military: cannons & artillery, turrets, launchers, tanks & military vehicles,
siege weapons (catapult, ballista, trebuchet), ammo & battlefield props.

Blocky stud style. Turrets, barrels, wheels and rotors are separate parts
(origin at their centre) so they can rotate in Roblox. Everything faces -Y.
"""
import math

from studlib.registry import add

from vehicles import car, cube, four_wheels, glass_box, truck, wheel, _helicopter

CAT = "Military"


def reg(name, fn, sub="Artillery", split=True, tags=()):
    add(name, CAT, fn, sub=sub, split=split, tags=list(tags) + ["military"])


# ----------------------------------------------------------------------------
# artillery & emplacements
# ----------------------------------------------------------------------------
def spoked_wheel(m, name, x, y, r=1.2, w=0.35, rim="iron_dark", spoke="wood"):
    with m.group(name):
        m.torus(R=r - 0.12, r=0.14, seg=10, rot=(0, 90, 0), loc=(x, y, r), color=rim)
        m.cyl(r=0.3, h=w + 0.2, seg=8, rot=(0, 90, 0), loc=(x, y, r), color=rim)
        for a in range(0, 180, 30):
            cube(m, (0.12, 0.14, (r - 0.2) * 2), (x, y, r), spoke, rot=(a, 0, 0), bev=0.02)


def _cannon(m):
    cube(m, (1.8, 3.4, 0.9), (0, 0.4, 1.1), "wood", bev=0.12, rot=(-8, 0, 0))
    cube(m, (1.6, 0.9, 0.5), (0, 2.3, 0.4), "wood_dark", bev=0.1)
    with m.group("Barrel"):
        m.lathe([(0.55, 0), (0.62, 0.3), (0.5, 0.5), (0.45, 3.2), (0.55, 3.35), (0.55, 3.6), (0.35, 3.6),
                 (0.3, 1.0), (0, 1.0)], seg=8, color="gunmetal", rot=(100, 0, 0), loc=(0, 0.9, 1.75))
        m.sphere(round=True, r=0.35, color="gunmetal", loc=(0, 1.55, 1.95))
        for y in (0.2, -1.0):
            m.torus(R=0.5, r=0.08, seg=8, rot=(100, 0, 0), color="bronze", loc=(0, y, 1.6 + (0.2 - y) * 0.18))
    spoked_wheel(m, "WheelL", 1.15, -0.1, 1.2)
    spoked_wheel(m, "WheelR", -1.15, -0.1, 1.2)


reg("Cannon", _cannon)


def _cannonballs(m):
    k = 0
    for layer, (n, z) in enumerate(((3, 0.5), (2, 1.3), (1, 2.1))):
        for i in range(n):
            for j in range(n):
                x = (i - (n - 1) / 2) * 0.95
                y = (j - (n - 1) / 2) * 0.95
                m.sphere(round=True, r=0.48, color="gunmetal" if k % 2 else "charcoal", loc=(x, y, z))
                k += 1


reg("Cannonballs", _cannonballs, sub="Ammo", split=False)


def _howitzer(m):
    for s in (-1, 1):
        m.tube([(s * 0.6, 0, 1.0), (s * 1.8, 4.2, 0.25)], [(0.25, 0.25), (0.2, 0.2)], seg=4, color="army_green")
        cube(m, (0.8, 0.9, 0.2), (s * 1.8, 4.3, 0.1), "army_dark", bev=0.05)
    cube(m, (2.4, 1.6, 0.9), (0, 0, 1.4), "army_green", bev=0.15)
    cube(m, (3.8, 0.3, 2.2), (0, -1.0, 2.4), "army_green", bev=0.08)
    with m.group("Barrel"):
        cube(m, (1.2, 2.6, 1.0), (0, 0.4, 2.3), "army_dark", bev=0.12, rot=(-15, 0, 0))
        m.cyl(r=0.28, h=6.5, seg=8, color="army_green", rot=(75, 0, 0), loc=(0, -2.3, 3.1))
        m.cyl(r=0.4, h=0.7, seg=8, color="army_dark", rot=(75, 0, 0), loc=(0, -5.3, 3.9))
    four_wheels(m, 4.2, -0.2, 0.9, r=0.95, w=0.6)


reg("Howitzer", _howitzer)


def _mortar(m):
    cube(m, (1.8, 1.8, 0.25), (0, 0.4, 0.12), "gunmetal", bev=0.06)
    with m.group("Tube"):
        m.cyl(r=0.28, h=3.2, seg=8, color="army_green", rot=(-40, 0, 0), loc=(0, -0.6, 1.4))
        m.cyl(r=0.34, h=0.3, seg=8, color="army_dark", rot=(-40, 0, 0), loc=(0, -1.6, 2.6))
    for s in (-1, 1):
        m.tube([(0, -0.8, 1.6), (s * 0.9, -1.4, 0.05)], [0.08, 0.08], seg=4, color="gunmetal")
    for i in range(3):
        m.lathe([(0, 0), (0.18, 0.1), (0.18, 0.8), (0.1, 1.0), (0, 1.05)], seg=6, color="army_dark",
                loc=(1.4 + i * 0.45, 0.8, 0))


reg("Mortar", _mortar)


def _mg_turret(m):
    for a in (0, 120, 240):
        r = math.radians(a + 90)
        m.tube([(0, 0, 1.6), (math.cos(r) * 1.2, math.sin(r) * 1.2, 0.05)], [0.08, 0.08], seg=4, color="gunmetal")
    with m.group("Gun"):
        cube(m, (0.5, 1.6, 0.5), (0, 0.1, 1.9), "gunmetal", bev=0.08)
        m.cyl(r=0.1, h=1.8, seg=6, color="charcoal", rot=(90, 0, 0), loc=(0, -1.5, 1.95))
        m.cyl(r=0.16, h=0.4, seg=6, color="charcoal", rot=(90, 0, 0), loc=(0, -2.4, 1.95))
        cube(m, (0.5, 0.5, 0.4), (0.45, 0.2, 1.75), "army_green", bev=0.06)
        cube(m, (0.12, 0.5, 0.5), (0, 0.8, 1.6), "charcoal", bev=0.03)
        cube(m, (1.4, 0.12, 1.0), (0, -0.4, 2.2), "army_green", bev=0.04)


reg("MachineGunTurret", _mg_turret)


def _aa_gun(m):
    m.cyl(r=1.8, h=0.6, seg=8, color="army_dark", loc=(0, 0, 0.3))
    with m.group("Turret"):
        m.cyl(r=1.3, h=0.8, seg=8, color="army_green", loc=(0, 0, 1.0))
        cube(m, (1.8, 1.6, 1.4), (0, 0.2, 2.0), "army_green", bev=0.15)
        for s in (-1, 1):
            m.cyl(r=0.14, h=3.6, seg=6, color="gunmetal", rot=(55, 0, 0), loc=(s * 0.45, -1.3, 3.5))
            m.cyl(r=0.22, h=0.5, seg=6, color="charcoal", rot=(55, 0, 0), loc=(s * 0.45, -2.6, 4.5))
        cube(m, (0.5, 0.5, 0.5), (1.1, 0.3, 2.4), "charcoal", bev=0.06)
        m.cyl(r=0.4, h=0.1, seg=8, color="lightgray", rot=(0, 90, 0), loc=(-0.95, 0.4, 2.3))


reg("AntiAirGun", _aa_gun)


def _launcher(m):
    cube(m, (3.0, 3.0, 0.8), (0, 0, 0.4), "army_dark", bev=0.12)
    with m.group("Launcher"):
        m.cyl(r=0.9, h=0.8, seg=8, color="army_green", loc=(0, 0, 1.2))
        cube(m, (3.0, 4.2, 1.8), (0, -0.2, 2.9), "army_green", bev=0.15, rot=(-25, 0, 0))
        for i in range(3):
            for j in range(2):
                x, z = -0.9 + i * 0.9, 2.6 + j * 0.8
                m.cyl(r=0.32, h=0.1, seg=8, color="black", rot=(65, 0, 0), loc=(x, -2.1, z + 0.9))
                m.cone(r=0.22, h=0.5, seg=8, color="fire_red", rot=(65, 0, 0), loc=(x, -2.05, z + 0.9))


reg("MissileLauncher", _launcher)


def _rocket_launcher(m):
    m.cyl(r=0.3, h=3.6, seg=8, color="army_green", rot=(90, 0, 0), loc=(0, 0, 0.6))
    m.cyl(r=0.36, h=0.4, seg=8, color="army_dark", rot=(90, 0, 0), loc=(0, -1.8, 0.6))
    m.cyl(r=0.36, h=0.4, seg=8, color="army_dark", rot=(90, 0, 0), loc=(0, 1.8, 0.6))
    cube(m, (0.2, 0.4, 0.7), (0, 0.2, 0.1), "charcoal", bev=0.04)
    cube(m, (0.2, 0.4, 0.5), (0, -0.6, 0.15), "charcoal", bev=0.04)
    cube(m, (0.25, 0.5, 0.3), (0.3, -0.3, 1.0), "gunmetal", bev=0.05)
    m.cone(r=0.28, h=0.8, seg=8, color="fire_red", rot=(90, 0, 0), loc=(0, -2.0, 0.6))


reg("RocketLauncher", _rocket_launcher, sub="Weapons", split=False)


def _missile(m):
    m.lathe([(0, 0), (0.35, 0.3), (0.35, 3.6), (0.18, 4.2), (0, 4.5)], seg=8,
            color=lambda c, n: "fire_red" if c.z > 3.6 else "plastic_white", cuts={"z": [3.6]})
    for a in range(0, 360, 90):
        m.prism([(0, 0), (0.7, 0), (0.1, 1.0)], depth=0.08, color="gunmetal", rot=(90, 0, a),
                loc=(0, 0, 0.1), deform=lambda co: co.__class__((co.x + 0.33, co.y, co.z)))


reg("Missile", _missile, sub="Ammo", split=False)


# ----------------------------------------------------------------------------
# siege weapons
# ----------------------------------------------------------------------------
def _catapult(m):
    for s in (-1, 1):
        cube(m, (0.4, 5.0, 0.4), (s * 1.3, 0, 0.9), "wood", bev=0.06)
        m.tube([(s * 1.3, 1.0, 1.0), (s * 1.3, 0.2, 3.2), (s * 1.3, -0.6, 1.0)], [0.18, 0.18, 0.18], seg=4,
               color="wood_dark")
    cube(m, (3.0, 0.4, 0.4), (0, 0.2, 3.2), "wood_dark", bev=0.06)
    cube(m, (3.0, 0.4, 0.4), (0, -1.8, 0.9), "wood_dark", bev=0.06)
    cube(m, (3.0, 0.4, 0.4), (0, 1.8, 0.9), "wood_dark", bev=0.06)
    with m.group("Arm"):
        m.tube([(0, 1.6, 1.2), (0, -0.5, 3.6)], [0.18, 0.16], seg=4, color="wood")
        m.lathe([(0, 0), (0.6, 0.1), (0.7, 0.4), (0.55, 0.45), (0.4, 0.2), (0, 0.15)], seg=8, color="wood_dark",
                loc=(0, -0.6, 3.6))
        m.sphere(round=True, r=0.4, color="stone", loc=(0, -0.6, 4.0))
    spoked_wheel(m, "WheelFL", 1.7, -1.6, 0.7, spoke="wood_dark", rim="wood")
    spoked_wheel(m, "WheelFR", -1.7, -1.6, 0.7, spoke="wood_dark", rim="wood")
    spoked_wheel(m, "WheelBL", 1.7, 1.6, 0.7, spoke="wood_dark", rim="wood")
    spoked_wheel(m, "WheelBR", -1.7, 1.6, 0.7, spoke="wood_dark", rim="wood")


reg("Catapult", _catapult, sub="Siege")


def _ballista(m):
    for a in (0, 120, 240):
        r = math.radians(a + 90)
        m.tube([(0, 0, 1.8), (math.cos(r) * 1.4, math.sin(r) * 1.4, 0.05)], [0.14, 0.12], seg=4, color="wood_dark")
    with m.group("Bow"):
        cube(m, (0.5, 4.2, 0.4), (0, -0.4, 2.1), "wood", bev=0.08)
        pts = [(math.sin(math.radians(a)) * 2.4, -2.0 + (1 - math.cos(math.radians(a))) * 1.2, 2.2)
               for a in range(-70, 71, 20)]
        m.tube(pts, [0.12] * len(pts), seg=4, color="wood_dark")
        m.tube([pts[0], (0, 0.8, 2.3), pts[-1]], [0.03] * 3, seg=4, color="rope")
        m.cyl(r=0.08, h=4.0, seg=6, color="wood_light", rot=(90, 0, 0), loc=(0, -1.0, 2.4))
        m.pyramid(w=0.3, h=0.6, color="iron", rot=(90, 0, 0), loc=(0, -3.0, 2.4))
        for s in (-1, 1):
            m.cyl(r=0.2, h=0.6, seg=8, color="iron_dark", loc=(s * 0.4, 0.6, 2.2))


reg("Ballista", _ballista, sub="Siege")


def _trebuchet(m):
    for s in (-1, 1):
        cube(m, (0.4, 6.0, 0.4), (s * 1.6, 0, 0.3), "wood", bev=0.06)
        for y in (-1.2, 1.2):
            m.tube([(s * 1.6, y * 1.6, 0.4), (s * 1.4, 0, 6.0)], [0.2, 0.18], seg=4, color="wood_dark")
    for y in (-2.6, 2.6):
        cube(m, (3.6, 0.4, 0.4), (0, y, 0.3), "wood", bev=0.06)
    cube(m, (3.4, 0.35, 0.35), (0, 0, 6.0), "iron_dark", bev=0.05)
    with m.group("Arm"):
        m.tube([(0, 2.2, 4.4), (0, -4.2, 8.6)], [0.22, 0.14], seg=4, color="wood")
        cube(m, (1.6, 1.6, 1.4), (0, 2.4, 3.4), "wood_dark", bev=0.12)
        cube(m, (1.2, 1.2, 0.6), (0, 2.4, 2.4), "stone", bev=0.1)
        m.tube([(0, -4.2, 8.6), (0, -4.6, 6.8)], [0.03, 0.03], seg=4, color="rope")
        cube(m, (0.6, 0.6, 0.3), (0, -4.6, 6.6), "leather", bev=0.08)


reg("Trebuchet", _trebuchet, sub="Siege")


# ----------------------------------------------------------------------------
# military vehicles
# ----------------------------------------------------------------------------
def _tank(m, col="army_green", dark="army_dark"):
    cube(m, (4.6, 8.0, 1.6), (0, 0, 1.6), col, bev=0.3)
    cube(m, (4.0, 1.2, 0.8), (0, -4.0, 1.2), col, bev=0.2, rot=(35, 0, 0))
    for s in (-1, 1):
        cube(m, (1.2, 8.6, 1.5), (s * 2.6, 0, 0.95), "charcoal", bev=0.3)
        for y in (-3.0, -1.5, 0.0, 1.5, 3.0):
            m.cyl(r=0.55, h=1.26, seg=8, color="gunmetal", rot=(0, 90, 0), loc=(s * 2.6, y, 0.75))
        cube(m, (1.4, 8.8, 0.2), (s * 2.6, 0, 1.75), dark, bev=0.05)
    with m.group("Turret"):
        cube(m, (3.4, 3.8, 1.4), (0, 0.6, 3.0), col, bev=0.3)
        m.cyl(r=0.6, h=0.5, seg=8, color=dark, loc=(0.9, 1.2, 3.9))
        cube(m, (1.0, 0.8, 0.8), (0, -1.4, 3.0), dark, bev=0.12)
        m.cyl(r=0.26, h=5.5, seg=8, color=col, rot=(90, 0, 0), loc=(0, -4.2, 3.05))
        m.cyl(r=0.36, h=0.8, seg=8, color=dark, rot=(90, 0, 0), loc=(0, -6.6, 3.05))
        m.cyl(r=0.06, h=1.4, seg=6, color="charcoal", loc=(-1.1, 1.8, 4.3))


reg("Tank", lambda m: _tank(m), sub="Vehicles")
reg("DesertTank", lambda m: _tank(m, col="army_tan", dark="camo_brown"), sub="Vehicles")


def _armored_car(m):
    cube(m, (4.6, 8.4, 2.4), (0, 0, 2.2), "army_green", bev=0.4)
    cube(m, (4.0, 0.2, 0.9), (0, -4.2, 2.8), "window_blue", bev=0.04)
    for s in (-1, 1):
        cube(m, (0.2, 1.2, 0.6), (s * 2.3, -2.6, 2.9), "window_blue", bev=0.04)
    with m.group("Turret"):
        m.cyl(r=1.0, h=0.7, seg=8, color="army_dark", loc=(0, 0.6, 3.75))
        m.cyl(r=0.12, h=2.2, seg=6, color="gunmetal", rot=(90, 0, 0), loc=(0, -0.8, 3.9))
    cube(m, (4.8, 0.5, 0.6), (0, -4.3, 1.2), "army_dark", bev=0.1)
    for s in (-1, 1):
        cube(m, (0.6, 0.12, 0.3), (s * 1.6, -4.25, 2.2), "glow", bev=0.04)
    x = 2.3 - 0.4
    for y, n in ((-2.6, "F"), (0.0, "M"), (2.6, "B")):
        wheel(m, f"Wheel{n}L", x + 0.05, y, 1.0, 0.8)
        wheel(m, f"Wheel{n}R", -x - 0.05, y, 1.0, 0.8)


reg("ArmoredCar", _armored_car, sub="Vehicles")


def _mil_jeep(m, d):
    cube(m, (0.9, 0.4, 0.9), (0, d["yb"] + 0.25, d["bz"] + 0.3), "rubber", bev=0.15)
    cube(m, (1.2, 0.6, 0.8), (-1.2, d["yb"] - 1.0, d["top"] + 0.4), "army_dark", bev=0.1)
    m.prism([(0, 0.5), (0.45, -0.3), (-0.45, -0.3)], depth=0.06, color="white", rot=(90, 0, 90),
            loc=(d["W"] / 2 + 0.02, 0.3, d["bz"]), scale=1.0)


reg("MilitaryJeep", lambda m: car(m, W=4.6, body_h=1.5, clear=0.9, col="army_green", col2="army_green", cab_l=4.4,
                                  cab_h=1.5, cab_y=0.8, roof="army_dark", r=1.05, extras=_mil_jeep, bumper="army_dark"),
    sub="Vehicles")


def _mil_truck(m, d):
    z = d["z0"] + 1.0
    cube(m, (d["W"], d["box_l"], 1.2), (0, d["box_y"], z + 0.6), "army_green", bev=0.1)
    m.cyl(r=d["W"] / 2, h=d["box_l"], seg=8, color="army_tan", rot=(90, 0, 0), loc=(0, d["box_y"], z + 1.2),
          deform=lambda co: co.__class__((co.x, max(co.y, 0.0) * 0.9, co.z)))
    for i in range(4):
        m.torus(R=d["W"] / 2 - 0.02, r=0.06, seg=8, arc=180, color="army_dark", rot=(90, 0, 0),
                loc=(0, d["box_y"] - d["box_l"] / 2 + 0.6 + i * (d["box_l"] - 1.2) / 3, z + 1.2),
                scale=(1, 1, 0.9))


reg("MilitaryTruck", lambda m: truck(m, cab="army_green", box=None, extras=_mil_truck), sub="Vehicles")
reg("AttackHelicopter", lambda m: _helicopter(m, col="army_green", mil=True), sub="Vehicles")


def _fighter_jet(m):
    m.tube([(0, -6.0, 2.4), (0, -4.5, 2.5), (0, 2.0, 2.5), (0, 5.0, 2.5)], [0.2, 0.9, 1.0, 0.8], seg=8,
           color="gunmetal")
    cube(m, (1.2, 2.2, 0.8), (0, -3.0, 3.3), "window_blue", bev=0.3)
    m.prism([(0, -1.5), (4.8, 2.4), (4.8, 3.2), (0, 2.6), (-4.8, 3.2), (-4.8, 2.4)], depth=0.25, color="gunmetal",
            loc=(0, 0, 2.3))
    m.prism([(0, 4.0), (2.2, 5.4), (2.2, 5.8), (0, 5.4), (-2.2, 5.8), (-2.2, 5.4)], depth=0.2, color="gunmetal",
            loc=(0, 0, 2.5))
    for s in (-1, 1):
        m.prism([(0, 0), (1.6, 0.6), (1.6, 1.4), (0, 1.0)], depth=0.15, color="gunmetal", rot=(0, 90 + s * 15, 0),
                loc=(s * 0.7, 3.6, 3.2))
        m.cyl(r=0.15, h=2.4, seg=6, color="plastic_white", rot=(90, 0, 0), loc=(s * 3.4, 1.8, 2.05))
        m.cone(r=0.15, h=0.4, seg=6, color="fire_red", rot=(90, 0, 0), loc=(s * 3.4, 0.6, 2.05))
    m.cyl(r=0.7, h=0.4, seg=8, color="charcoal", rot=(90, 0, 0), loc=(0, 5.2, 2.5))
    m.cone(r=0.55, h=0.9, seg=8, color="fire", rot=(-90, 0, 0), loc=(0, 5.4, 2.5))
    for x, y in ((0, -4.0), (1.4, 1.2), (-1.4, 1.2)):
        m.tube([(x, y, 1.9), (x, y, 0.6)], [0.07, 0.07], seg=4, color="charcoal")
    wheel(m, "WheelF", 0.15, -4.0, 0.35, 0.3)
    wheel(m, "WheelL", 1.55, 1.2, 0.45, 0.35)
    wheel(m, "WheelR", -1.55, 1.2, 0.45, 0.35)


reg("FighterJet", _fighter_jet, sub="Vehicles")


# ----------------------------------------------------------------------------
# ammo & battlefield props
# ----------------------------------------------------------------------------
def _ammo_crate(m):
    cube(m, (2.4, 1.4, 1.2), (0, 0, 0.6), "army_green", bev=0.1)
    cube(m, (2.5, 1.5, 0.2), (0, 0, 1.15), "army_dark", bev=0.05)
    for x in (-0.8, 0.8):
        cube(m, (0.3, 1.5, 1.24), (x, 0, 0.6), "army_dark", bev=0.04)
    for i in range(4):
        cube(m, (0.18, 0.06, 0.4), (-0.45 + i * 0.3, -0.72, 0.6), "road_yellow", bev=0.02)
    for s in (-1, 1):
        cube(m, (0.12, 0.5, 0.12), (s * 1.26, 0, 0.8), "charcoal", bev=0.02)


reg("AmmoCrate", _ammo_crate, sub="Ammo", split=False)


def _explosive_barrel(m):
    m.cyl(r=0.9, h=2.4, seg=8, color=lambda c, n: "road_yellow" if 0.9 < c.z < 1.5 else "fire_red",
          loc=(0, 0, 1.2), cuts={"z": [0.9, 1.5]}, bevel=0.08)
    for z in (0.5, 1.9):
        m.torus(R=0.92, r=0.06, seg=8, color="charcoal", loc=(0, 0, z))
    m.prism([(0, 0.35), (0.3, -0.2), (-0.3, -0.2)], depth=0.06, color="black", rot=(90, 0, 0), loc=(0, -0.92, 1.2))


reg("ExplosiveBarrel", _explosive_barrel, sub="Ammo", split=False)


def _sandbags(m):
    for row in range(3):
        n = 5 - row
        for i in range(n):
            x = (i - (n - 1) / 2) * 1.35
            cube(m, (1.4, 0.9, 0.6), (x, (row % 2) * 0.05, 0.3 + row * 0.55), "army_tan", bev=0.25)
            cube(m, (0.1, 0.92, 0.62), (x + 0.5, (row % 2) * 0.05, 0.3 + row * 0.55), "camo_brown", bev=0.02)


reg("Sandbags", _sandbags, sub="Battlefield", split=False)


def _tank_trap(m):
    for rx, ry in ((45, 0), (-45, 0), (0, 90)):
        cube(m, (0.35, 0.35, 3.0), (0, 0, 1.05), "gunmetal", rot=(rx, ry, 45 if ry else 0), bev=0.05)


reg("TankTrap", _tank_trap, sub="Battlefield", split=False)


def _landmine(m):
    m.cyl(r=0.8, h=0.3, seg=8, color="army_green", loc=(0, 0, 0.15), bevel=0.06)
    m.cyl(r=0.3, h=0.2, seg=8, color="gunmetal", loc=(0, 0, 0.35))
    m.sphere(round=True, r=0.08, color="neon_red", loc=(0.45, 0, 0.32))


reg("Landmine", _landmine, sub="Battlefield", split=False)


def _grenade(m):
    m.lathe([(0, 0), (0.35, 0.05), (0.48, 0.35), (0.45, 0.7), (0.3, 0.9), (0, 0.95)], seg=8, color="army_green",
            cuts={"z": [0.3, 0.6]})
    m.cyl(r=0.18, h=0.25, seg=6, color="gunmetal", loc=(0, 0, 1.0))
    cube(m, (0.12, 0.2, 0.6), (0.22, 0, 0.8), "gunmetal", bev=0.03, rot=(0, 20, 0))
    m.torus(R=0.14, r=0.03, seg=6, color="silver", rot=(90, 0, 0), loc=(-0.2, 0, 1.12))


reg("Grenade", _grenade, sub="Weapons", split=False)


def _barbed_fence(m):
    for x in (-3.0, 0.0, 3.0):
        cube(m, (0.25, 0.25, 2.8), (x, 0, 1.4), "wood_dark", bev=0.04)
    for z in (0.8, 1.6, 2.4):
        m.tube([(-3.0, 0, z), (0, 0.05, z - 0.1), (3.0, 0, z)], [0.03] * 3, seg=4, color="iron")
        for i in range(12):
            x = -2.8 + i * 0.5
            cube(m, (0.18, 0.04, 0.04), (x, 0, z - 0.05), "iron", rot=(0, 45, 0), bev=0.01)


reg("BarbedWireFence", _barbed_fence, sub="Battlefield", split=False)


def _army_flag(m):
    m.cyl(r=0.1, h=6.0, seg=6, color="silver", loc=(0, 0, 3.0))
    m.box((2.6, 0.06, 1.6), color=lambda c, n: "army_green" if c.x < 1.1 else "army_dark", loc=(1.4, 0, 5.1),
          cuts={"x": [1.1]}, bevel=0.02)
    m.prism([(0, 0.4), (0.12, 0.12), (0.4, 0.12), (0.18, -0.06), (0.26, -0.35), (0, -0.18), (-0.26, -0.35),
             (-0.18, -0.06), (-0.4, 0.12), (-0.12, 0.12)], depth=0.1, color="plastic_white", rot=(90, 0, 0),
            loc=(1.8, -0.05, 5.1))
    m.cyl(r=0.8, h=0.4, seg=8, color="concrete", loc=(0, 0, 0.2))


reg("ArmyFlag", _army_flag, sub="Battlefield", split=False)
