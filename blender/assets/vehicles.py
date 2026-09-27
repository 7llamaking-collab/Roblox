"""Vehicles: cars, trucks, service vehicles, bikes, boats and aircraft.

Blocky stud style. Wheels, rotors and propellers are built in their own groups
and exported as separate MeshParts (origin at their centre) so they can spin on
HingeConstraints / be used with any Roblox chassis. Vehicles face -Y.
Roughly Roblox scale: a car is ~9 studs long and fits a 5-stud character.
"""
import math

from studlib.registry import add

CAT = "Vehicles"


def cube(m, size, loc, color, bev=None, **kw):
    b = min(size) * 0.14 if bev is None else bev
    return m.box(size, color=color, bevel=b, loc=loc, **kw)


def wheel(m, name, x, y, r=0.85, w=0.7, tire="rubber", hub="iron", spokes=True):
    with m.group(name):
        m.cyl(r=r, h=w, seg=10, rot=(0, 90, 0), loc=(x, y, r), color=tire, bevel=0.1)
        s = 1 if x > 0 else -1
        m.cyl(r=r * 0.55, h=0.08, seg=8, rot=(0, 90, 0), loc=(x + s * w / 2, y, r), color=hub, bevel=0.02)
        if spokes:
            cube(m, (0.1, r * 0.2, r * 0.2), (x + s * (w / 2 + 0.06), y, r), "charcoal", bev=0.02)


def four_wheels(m, W, y_front, y_back, r=0.85, w=0.7, tire="rubber", hub="iron", inset=0.1):
    x = W / 2 - w / 2 + inset
    wheel(m, "WheelFL", x, y_front, r, w, tire, hub)
    wheel(m, "WheelFR", -x, y_front, r, w, tire, hub)
    wheel(m, "WheelBL", x, y_back, r, w, tire, hub)
    wheel(m, "WheelBR", -x, y_back, r, w, tire, hub)


def lights(m, W, y_front, y_back, z, head="glow", tail="neon_red", plate=True):
    for s in (-1, 1):
        cube(m, (0.6, 0.1, 0.32), (s * (W / 2 - 0.55), y_front - 0.03, z), head, bev=0.04)
        cube(m, (0.5, 0.1, 0.3), (s * (W / 2 - 0.5), y_back + 0.03, z), tail, bev=0.04)
    if plate:
        cube(m, (1.0, 0.08, 0.36), (0, y_front - 0.05, z - 0.45), "white", bev=0.03)
        cube(m, (1.0, 0.08, 0.36), (0, y_back + 0.05, z - 0.45), "white", bev=0.03)


def glass_box(m, w, l, h, loc):
    """Windows on a cabin: one glass slab across the sides, one across front/back."""
    x, y, z = loc
    cube(m, (w + 0.06, l * 0.82, h * 0.62), (x, y, z + h * 0.08), "window_blue", bev=0.03)
    cube(m, (w * 0.84, l + 0.06, h * 0.62), (x, y, z + h * 0.08), "window_blue", bev=0.03)


def car(m, *, L=9.0, W=4.4, body_h=1.5, clear=0.55, col="plastic_red", col2=None, cab_l=4.2, cab_h=1.5,
        cab_y=0.4, roof=None, r=0.85, extras=None, bumper="charcoal"):
    col2 = col2 or col
    z0 = clear + r * 0.2
    bz = z0 + body_h / 2
    top = z0 + body_h
    yf, yb = -L / 2, L / 2
    cube(m, (W, L, body_h), (0, 0, bz), col, bev=0.3)
    cube(m, (W * 0.9, cab_l, cab_h), (0, cab_y, top + cab_h / 2 - 0.05), col2, bev=0.25)
    glass_box(m, W * 0.9, cab_l, cab_h, (0, cab_y, top + cab_h / 2 - 0.05))
    if roof:
        cube(m, (W * 0.8, cab_l * 0.7, 0.14), (0, cab_y, top + cab_h), roof, bev=0.04)
    for y in (yf, yb):
        cube(m, (W + 0.1, 0.4, 0.5), (0, y + (0.1 if y > 0 else -0.1), z0 + 0.2), bumper, bev=0.1)
    cube(m, (W * 0.4, 0.08, 0.5), (0, yf - 0.03, bz + 0.1), "charcoal", bev=0.03)
    lights(m, W, yf, yb, bz + 0.2)
    for s in (-1, 1):
        cube(m, (0.1, 0.3, 0.1), (s * (W / 2 + 0.05), cab_y - cab_l / 2 + 0.2, top + 0.1), "charcoal", bev=0.02)
        cube(m, (0.25, 0.25, 0.2), (s * (W / 2 + 0.15), cab_y - cab_l / 2 + 0.25, top + 0.25), col2, bev=0.04)
    four_wheels(m, W, yf + L * 0.22, yb - L * 0.22, r=r)
    d = dict(L=L, W=W, top=top, cab_y=cab_y, cab_l=cab_l, cab_h=cab_h, yf=yf, yb=yb, bz=bz, z0=z0)
    if extras:
        extras(m, d)
    return d


def reg(name, fn, sub="Cars", tags=()):
    add(name, CAT, fn, sub=sub, split=True, tags=list(tags) + ["vehicle"])


reg("Car", lambda m: car(m, col="plastic_red"))
reg("BlueCar", lambda m: car(m, col="plastic_blue"))
reg("SportsCar", lambda m: car(m, L=9.5, W=4.6, body_h=1.1, clear=0.35, col="plastic_yellow", cab_l=3.2,
                               cab_h=1.1, cab_y=0.6, r=0.8,
                               extras=lambda m, d: [cube(m, (d["W"] * 0.9, 0.9, 0.12), (0, d["yb"] - 0.5, d["top"] + 0.5),
                                                         "charcoal", bev=0.03),
                                                    [cube(m, (0.15, 0.15, 0.5), (s * 1.4, d["yb"] - 0.5, d["top"] + 0.2),
                                                          "charcoal", bev=0.03) for s in (-1, 1)],
                                                    cube(m, (0.6, 1.8, 0.04), (0, -1.8, d["top"] + 0.01), "charcoal",
                                                         bev=0.01)]))


def _police(m, d):
    cube(m, (1.8, 0.5, 0.3), (0, d["cab_y"], d["top"] + d["cab_h"] + 0.1), "charcoal", bev=0.05)
    cube(m, (0.8, 0.46, 0.24), (0.45, d["cab_y"], d["top"] + d["cab_h"] + 0.3), "plastic_blue", bev=0.05)
    cube(m, (0.8, 0.46, 0.24), (-0.45, d["cab_y"], d["top"] + d["cab_h"] + 0.3), "neon_red", bev=0.05)
    cube(m, (d["W"] + 0.04, 3.0, 0.5), (0, 0.4, d["bz"]), "police_blue", bev=0.05)


reg("PoliceCar", lambda m: car(m, col="plastic_white", extras=_police), sub="Service")


def _taxi(m, d):
    cube(m, (1.4, 0.5, 0.5), (0, d["cab_y"], d["top"] + d["cab_h"] + 0.2), "plastic_white", bev=0.08)
    m.box((d["W"] + 0.04, 6.0, 0.35), color=lambda c, n: "black" if int((c.y + 10) / 0.35) % 2 else "white",
          loc=(0, 0, d["bz"] + 0.3), cuts={"y": 0.35}, bevel=0.04)


reg("Taxi", lambda m: car(m, col="taxi_yellow", extras=_taxi), sub="Service")


def _jeep(m, d):
    cube(m, (0.9, 0.4, 0.9), (0, d["yb"] + 0.25, d["bz"] + 0.3), "rubber", bev=0.15)
    for s in (-1, 1):
        cube(m, (0.2, d["L"] * 0.6, 0.18), (s * (d["W"] / 2 + 0.1), 0, d["z0"] + 0.1), "charcoal", bev=0.04)


reg("Jeep", lambda m: car(m, W=4.6, body_h=1.6, clear=0.9, col="leaf_dark", cab_l=4.6, cab_h=1.7, cab_y=0.8,
                          roof="charcoal", r=1.05, extras=_jeep))


def _pickup(m, d):
    y0 = d["cab_y"] + d["cab_l"] / 2
    for s in (-1, 1):
        cube(m, (0.25, d["yb"] - y0, 0.8), (s * (d["W"] / 2 - 0.12), (y0 + d["yb"]) / 2, d["top"] + 0.35),
             "plastic_orange", bev=0.06)
    cube(m, (d["W"], 0.25, 0.8), (0, d["yb"] - 0.12, d["top"] + 0.35), "plastic_orange", bev=0.06)
    cube(m, (1.3, 1.0, 0.9), (0.6, y0 + 1.4, d["top"] + 0.45), "wood", bev=0.08)


reg("PickupTruck", lambda m: car(m, L=10.0, W=4.6, body_h=1.6, clear=0.8, col="plastic_orange", cab_l=3.2, cab_h=1.7,
                                 cab_y=-1.2, r=1.0, extras=_pickup), sub="Trucks")


def van(m, *, col="plastic_white", L=10.0, W=4.6, H=4.2, stripe=None, cross=False, extras=None, r=0.9):
    z0 = 0.55 + r * 0.2
    cube(m, (W, L, H), (0, 0.4, z0 + H / 2), col, bev=0.35)
    cube(m, (W, 1.6, H * 0.5), (0, -L / 2 - 0.3, z0 + H * 0.25), col, bev=0.35)
    cube(m, (W * 0.84, 0.1, H * 0.35), (0, -L / 2 + 0.43, z0 + H * 0.68), "window_blue", bev=0.03)
    cube(m, (W + 0.06, 1.5, H * 0.3), (0, -L / 2 + 1.3, z0 + H * 0.7), "window_blue", bev=0.03)
    if stripe:
        cube(m, (W + 0.04, L - 1.5, 0.5), (0, 0.9, z0 + H * 0.4), stripe, bev=0.04)
    if cross:
        for s in (-1, 1):
            cube(m, (0.06, 1.4, 0.4), (s * (W / 2 + 0.02), 1.5, z0 + H * 0.68), "fire_red", bev=0.02)
            cube(m, (0.06, 0.4, 1.4), (s * (W / 2 + 0.02), 1.5, z0 + H * 0.68), "fire_red", bev=0.02)
    yf, yb = -L / 2 - 1.1, L / 2 + 0.4
    for y in (yf, yb):
        cube(m, (W + 0.1, 0.4, 0.5), (0, y + (0.1 if y > 0 else -0.1), z0 + 0.2), "charcoal", bev=0.1)
    lights(m, W, yf, yb, z0 + 0.8)
    four_wheels(m, W, yf + 1.8, yb - 1.8, r=r)
    d = dict(W=W, L=L, H=H, z0=z0, yf=yf, yb=yb)
    if extras:
        extras(m, d)


def _ambulance(m, d):
    cube(m, (1.8, 0.5, 0.3), (0, -d["L"] / 2 + 0.6, d["z0"] + d["H"] + 0.1), "charcoal", bev=0.05)
    cube(m, (0.8, 0.46, 0.24), (0.45, -d["L"] / 2 + 0.6, d["z0"] + d["H"] + 0.3), "neon_red", bev=0.05)
    cube(m, (0.8, 0.46, 0.24), (-0.45, -d["L"] / 2 + 0.6, d["z0"] + d["H"] + 0.3), "plastic_blue", bev=0.05)


reg("Van", lambda m: van(m, col="plastic_blue"), sub="Trucks")
reg("Ambulance", lambda m: van(m, col="plastic_white", stripe="fire_red", cross=True, extras=_ambulance), sub="Service")


def _icecream(m, d):
    z = d["z0"] + d["H"]
    m.cone(r=0.7, h=1.5, seg=8, color="cone", rot=(180, 0, 0), loc=(0, 1.0, z + 1.6))
    m.sphere(round=True, r=0.75, color="icecream_straw", loc=(0, 1.0, z + 1.9))
    m.sphere(round=True, r=0.6, color="icecream_mint", loc=(0, 1.0, z + 2.6))
    cube(m, (0.1, 3.0, 1.4), (d["W"] / 2 + 0.02, 1.0, d["z0"] + d["H"] * 0.62), "charcoal", bev=0.03)
    m.box((0.3, 3.4, 0.5), color=lambda c, n: "awning_white" if int((c.y + 10) / 0.5) % 2 else "candy_pink",
          loc=(d["W"] / 2 + 0.3, 1.0, d["z0"] + d["H"] * 0.95), rot=(0, -25, 0), cuts={"y": 0.5}, bevel=0.04)


reg("IceCreamTruck", lambda m: van(m, col="icecream_van", stripe="candy_pink", extras=_icecream), sub="Service")


def truck(m, *, cab="plastic_red", box="plastic_white", L=14.0, W=4.8, box_h=5.0, extras=None, r=1.0, six=True):
    z0 = 0.6 + r * 0.2
    yf = -L / 2
    cube(m, (W, 3.2, 3.6), (0, yf + 1.6, z0 + 1.8), cab, bev=0.35)
    cube(m, (W * 0.86, 0.1, 1.3), (0, yf + 0.02, z0 + 2.5), "window_blue", bev=0.03)
    cube(m, (W + 0.06, 1.6, 1.2), (0, yf + 1.6, z0 + 2.55), "window_blue", bev=0.03)
    cube(m, (W * 0.5, 0.08, 0.8), (0, yf - 0.02, z0 + 1.1), "chrome", bev=0.03)
    cube(m, (W, L - 3.6, 1.0), (0, 1.6, z0 + 0.5), "charcoal", bev=0.1)
    d = dict(W=W, L=L, z0=z0, yf=yf, box_y=1.8, box_l=L - 3.8, box_h=box_h)
    if box:
        cube(m, (W, L - 3.8, box_h), (0, 1.8, z0 + 1.0 + box_h / 2), box, bev=0.2)
    cube(m, (W + 0.1, 0.4, 0.5), (0, yf - 0.1, z0 + 0.2), "charcoal", bev=0.1)
    lights(m, W, yf, L / 2, z0 + 1.0, plate=False)
    xw = W / 2 - 0.3
    wheel(m, "WheelFL", xw, yf + 1.7, r, 0.8)
    wheel(m, "WheelFR", -xw, yf + 1.7, r, 0.8)
    wheel(m, "WheelBL", xw, L / 2 - 2.0, r, 0.8)
    wheel(m, "WheelBR", -xw, L / 2 - 2.0, r, 0.8)
    if six:
        wheel(m, "WheelML", xw, L / 2 - 4.2, r, 0.8)
        wheel(m, "WheelMR", -xw, L / 2 - 4.2, r, 0.8)
    if extras:
        extras(m, d)


def _delivery(m, d):
    for s in (-1, 1):
        cube(m, (0.06, 4.0, 1.4), (s * (d["W"] / 2 + 0.02), 2.0, d["z0"] + 3.6), "plastic_orange", bev=0.04)
        cube(m, (0.08, 1.2, 1.2), (s * (d["W"] / 2 + 0.03), 3.5, d["z0"] + 3.6), "wood_light",
             bev=0.04)


reg("DeliveryTruck", lambda m: truck(m, cab="plastic_orange", box="plastic_white", extras=_delivery), sub="Trucks")


def _firetruck(m, d):
    z = d["z0"] + 1.0
    cube(m, (d["W"], d["L"] - 3.8, 2.4), (0, 1.8, z + 1.2), "fire_red", bev=0.2)
    for s in (-1, 1):
        for k in range(3):
            cube(m, (0.08, 2.0, 1.4), (s * (d["W"] / 2 + 0.02), -0.8 + k * 2.4, z + 1.2), "silver", bev=0.03)
    for s in (-1, 1):
        cube(m, (0.18, d["L"] - 3.0, 0.18), (s * 0.7, 1.4, z + 2.9), "silver", bev=0.03)
    for i in range(10):
        cube(m, (1.4, 0.12, 0.12), (0, -2.8 + i * 1.0, z + 2.9), "silver", bev=0.02)
    cube(m, (1.8, 0.5, 0.3), (0, d["yf"] + 1.6, d["z0"] + 3.75), "charcoal", bev=0.05)
    cube(m, (1.5, 0.46, 0.28), (0, d["yf"] + 1.6, d["z0"] + 3.95), "neon_red", bev=0.05)
    m.cyl(r=0.35, h=0.6, seg=8, color="silver", rot=(0, 90, 0), loc=(d["W"] / 2 + 0.3, 4.5, z + 0.6))


reg("FireTruck", lambda m: truck(m, cab="fire_red", box=None, extras=_firetruck), sub="Service")


def bus(m, col="school_yellow", L=16.0, W=4.8, H=4.6, stripe="black"):
    r = 1.0
    z0 = 0.6 + r * 0.2
    cube(m, (W, L, H), (0, 0, z0 + H / 2), col, bev=0.4)
    cube(m, (W, 1.6, H * 0.45), (0, -L / 2 - 0.6, z0 + H * 0.22), col, bev=0.35)
    cube(m, (W * 0.86, 0.1, H * 0.38), (0, -L / 2 + 0.03, z0 + H * 0.68), "window_blue", bev=0.03)
    for i in range(7):
        cube(m, (W + 0.06, 1.5, H * 0.3), (0, -L / 2 + 2.0 + i * 1.95, z0 + H * 0.7), "window_blue", bev=0.03)
    cube(m, (W + 0.04, L - 0.4, 0.18), (0, 0.1, z0 + H * 0.45), stripe, bev=0.03)
    cube(m, (0.08, 1.2, H * 0.75), (-W / 2 - 0.02, -L / 2 + 1.2, z0 + H * 0.45), "window_blue", bev=0.03)
    yf, yb = -L / 2 - 1.4, L / 2
    for y in (yf, yb):
        cube(m, (W + 0.1, 0.4, 0.5), (0, y + (0.1 if y > 0 else -0.1), z0 + 0.2), "charcoal", bev=0.1)
    lights(m, W, yf, yb, z0 + 0.9)
    four_wheels(m, W, yf + 2.3, yb - 2.8, r=r, w=0.8)


reg("SchoolBus", lambda m: bus(m), sub="Trucks")
reg("CityBus", lambda m: bus(m, col="plastic_green", stripe="plastic_white"), sub="Trucks")


def _tractor(m):
    z = 1.2
    cube(m, (2.2, 5.0, 1.6), (0, -0.6, z + 0.8), "plastic_green", bev=0.25)
    cube(m, (2.0, 1.0, 1.2), (0, -3.0, z + 0.5), "charcoal", bev=0.1)
    cube(m, (3.2, 2.4, 2.8), (0, 1.3, z + 2.6), "plastic_green", bev=0.2)
    glass_box(m, 3.2, 2.4, 2.4, (0, 1.3, z + 2.8))
    cube(m, (3.4, 2.6, 0.2), (0, 1.3, z + 4.1), "plastic_yellow", bev=0.05)
    m.cyl(r=0.18, h=1.6, seg=8, color="charcoal", loc=(0.6, -2.2, z + 2.2))
    wheel(m, "WheelFL", 1.35, -2.2, 0.9, 0.7)
    wheel(m, "WheelFR", -1.35, -2.2, 0.9, 0.7)
    wheel(m, "WheelBL", 1.9, 1.3, 1.7, 1.1, hub="plastic_yellow")
    wheel(m, "WheelBR", -1.9, 1.3, 1.7, 1.1, hub="plastic_yellow")
    for s in (-1, 1):
        cube(m, (1.2, 2.6, 0.18), (s * 1.9, 1.3, 3.5), "plastic_green", bev=0.05)


reg("Tractor", _tractor, sub="Farm")


def _monster(m):
    z = 2.8
    cube(m, (4.4, 8.0, 1.5), (0, 0, z + 0.75), "plastic_purple", bev=0.3)
    cube(m, (3.8, 3.4, 1.6), (0, 0.6, z + 2.2), "plastic_purple", bev=0.25)
    glass_box(m, 3.8, 3.4, 1.6, (0, 0.6, z + 2.2))
    for i, s in enumerate((-1, 1)):
        m.prism([(0, 0), (1.5, 0.4), (0.3, 0.9)], depth=0.06, color="fire", loc=(s * 2.23, -2.0, z + 0.7),
                rot=(90, 0, 90))
    cube(m, (4.0, 3.0, 0.6), (0, 0, 2.3), "charcoal", bev=0.1)
    for y in (-2.7, 2.7):
        cube(m, (0.4, 0.4, 1.4), (1.2, y, 2.0), "chrome", bev=0.08)
        cube(m, (0.4, 0.4, 1.4), (-1.2, y, 2.0), "chrome", bev=0.08)
    four_wheels(m, 5.6, -2.8, 2.8, r=1.9, w=1.5, inset=0.2)
    lights(m, 4.4, -4.0, 4.0, z + 0.9, plate=False)


reg("MonsterTruck", _monster, sub="Cars")


def _golfcart(m):
    z = 0.7
    cube(m, (3.0, 5.0, 0.9), (0, 0, z + 0.45), "plastic_white", bev=0.2)
    cube(m, (2.6, 1.0, 0.6), (0, 0.5, z + 1.2), "fabric_green", bev=0.15)
    cube(m, (2.6, 0.4, 1.2), (0, 1.1, z + 1.8), "fabric_green", bev=0.12)
    for x in (-1.3, 1.3):
        for y in (-1.6, 1.4):
            cube(m, (0.12, 0.12, 2.6), (x, y, z + 2.2), "silver", bev=0.02)
    cube(m, (3.2, 3.8, 0.2), (0, -0.1, z + 3.5), "plastic_white", bev=0.06)
    cube(m, (2.4, 0.1, 1.0), (0, -1.65, z + 2.6), "window_blue", bev=0.03)
    m.cyl(r=0.35, h=0.1, seg=8, color="charcoal", rot=(70, 0, 0), loc=(0.6, -1.3, z + 1.4))
    cube(m, (1.4, 1.2, 0.9), (0, 2.1, z + 1.3), "plastic_black", bev=0.1)
    four_wheels(m, 3.0, -1.6, 1.6, r=0.55, w=0.5)


reg("GolfCart", _golfcart, sub="Cars")


def _gokart(m):
    z = 0.35
    cube(m, (2.4, 4.0, 0.3), (0, 0, z + 0.15), "plastic_red", bev=0.1)
    cube(m, (1.6, 1.4, 0.5), (0, -1.5, z + 0.5), "plastic_red", bev=0.15)
    cube(m, (1.2, 1.0, 0.4), (0, 0.6, z + 0.5), "charcoal", bev=0.12)
    cube(m, (1.2, 0.3, 1.0), (0, 1.1, z + 0.9), "charcoal", bev=0.1)
    m.cyl(r=0.1, h=0.9, seg=6, color="charcoal", rot=(-40, 0, 0), loc=(0, -0.5, z + 0.9))
    m.torus(R=0.35, r=0.07, seg=8, color="charcoal", rot=(-40, 0, 0), loc=(0, -0.2, z + 1.25))
    cube(m, (1.0, 0.8, 0.6), (0, 1.8, z + 0.5), "iron_dark", bev=0.1)
    m.cyl(r=0.12, h=0.6, seg=6, color="chrome", rot=(90, 0, 0), loc=(0.4, 2.3, z + 0.6))
    wheel(m, "WheelFL", 1.35, -1.3, 0.45, 0.5)
    wheel(m, "WheelFR", -1.35, -1.3, 0.45, 0.5)
    wheel(m, "WheelBL", 1.4, 1.4, 0.55, 0.7)
    wheel(m, "WheelBR", -1.4, 1.4, 0.55, 0.7)


reg("GoKart", _gokart, sub="Cars")


def _motorcycle(m):
    z = 1.0
    cube(m, (0.8, 3.2, 0.9), (0, 0, z + 0.9), "plastic_black", bev=0.2)
    cube(m, (1.0, 1.4, 0.8), (0, -0.7, z + 1.4), "plastic_red", bev=0.25)
    cube(m, (0.8, 1.4, 0.3), (0, 0.6, z + 1.5), "leather_dark", bev=0.1)
    m.tube([(0, -1.4, z + 1.4), (0, -1.9, z + 0.2)], [0.12, 0.1], seg=4, color="chrome")
    m.tube([(0, -1.2, z + 1.8), (0, -1.5, z + 2.3)], [0.1, 0.1], seg=4, color="chrome")
    cube(m, (1.8, 0.16, 0.16), (0, -1.5, z + 2.3), "charcoal", bev=0.04)
    cube(m, (0.5, 0.2, 0.4), (0, -1.75, z + 1.7), "glow", bev=0.06)
    m.cyl(r=0.15, h=1.4, seg=6, color="chrome", rot=(90, 0, 0), loc=(0.45, 1.0, z + 0.5))
    with m.group("WheelF"):
        m.cyl(r=0.95, h=0.4, seg=10, rot=(0, 90, 0), loc=(0, -1.9, 0.95), color="rubber", bevel=0.08)
        m.cyl(r=0.5, h=0.45, seg=8, rot=(0, 90, 0), loc=(0, -1.9, 0.95), color="iron")
    with m.group("WheelB"):
        m.cyl(r=0.95, h=0.5, seg=10, rot=(0, 90, 0), loc=(0, 1.6, 0.95), color="rubber", bevel=0.08)
        m.cyl(r=0.5, h=0.55, seg=8, rot=(0, 90, 0), loc=(0, 1.6, 0.95), color="iron")


reg("Motorcycle", _motorcycle, sub="Bikes")


def _scooter(m):
    cube(m, (0.8, 2.6, 0.2), (0, 0, 0.55), "plastic_pink", bev=0.06)
    m.tube([(0, -1.2, 0.6), (0, -1.4, 2.8)], [0.1, 0.1], seg=4, color="silver")
    cube(m, (1.4, 0.14, 0.14), (0, -1.4, 2.85), "charcoal", bev=0.04)
    with m.group("WheelF"):
        m.cyl(r=0.4, h=0.3, seg=10, rot=(0, 90, 0), loc=(0, -1.3, 0.4), color="rubber", bevel=0.05)
    with m.group("WheelB"):
        m.cyl(r=0.4, h=0.3, seg=10, rot=(0, 90, 0), loc=(0, 1.2, 0.4), color="rubber", bevel=0.05)


reg("Scooter", _scooter, sub="Bikes")


# --- boats & aircraft --------------------------------------------------------------------
def _speedboat(m):
    m.box((4.2, 9.0, 1.6), color=lambda c, n: "plastic_white" if c.z > 0.9 else "plastic_blue", bevel=0.3,
          loc=(0, 0.5, 0.9), cuts={"z": [0.9]},
          deform=lambda co: co.__class__((co.x * (1.0 - max(0.0, -co.y - 1.5) / 3.5 * 0.9), co.y,
                                          co.z + max(0.0, -co.y - 2.5) * 0.25)))
    cube(m, (3.4, 1.0, 1.0), (0, -0.8, 2.1), "window_blue", bev=0.1, rot=(-25, 0, 0))
    cube(m, (3.0, 2.4, 0.6), (0, 1.6, 1.9), "fabric_cream", bev=0.15)
    cube(m, (1.4, 1.2, 1.4), (0, 4.4, 1.6), "charcoal", bev=0.15)
    with m.group("Propeller"):
        m.cyl(r=0.1, h=0.6, seg=6, color="silver", rot=(90, 0, 0), loc=(0, 5.2, 0.8))
        for a in (0, 120, 240):
            cube(m, (0.18, 0.06, 0.55), (0, 5.4, 0.8), "silver", rot=(0, a, 0), bev=0.02,
                 deform=lambda co: co.__class__((co.x, co.y, co.z + 0.3)))


reg("Speedboat", _speedboat, sub="Boats")


def _rowboat(m):
    m.box((2.6, 6.0, 1.0), color="wood", bevel=0.3, loc=(0, 0, 0.5),
          deform=lambda co: co.__class__((co.x * (1.0 - (abs(co.y) / 3.0) ** 2 * 0.7), co.y, co.z)))
    cube(m, (2.1, 5.2, 0.1), (0, 0, 0.85), "wood_dark", bev=0.02,
         deform=lambda co: co.__class__((co.x * (1.0 - (abs(co.y) / 2.6) ** 2 * 0.7), co.y, co.z)))
    for y in (-1.0, 1.2):
        cube(m, (2.2, 0.6, 0.12), (0, y, 0.9), "wood_light", bev=0.03)
    for s in (-1, 1):
        m.tube([(s * 0.8, 0.1, 1.0), (s * 2.3, 0.4, 0.3)], [0.06, 0.06], seg=4, color="wood_light")
        cube(m, (0.3, 0.8, 0.06), (s * 2.4, 0.45, 0.25), "wood_light", bev=0.02, rot=(0, s * 30, 0))


reg("Rowboat", _rowboat, sub="Boats")


def _helicopter(m, col="plastic_red", mil=False):
    cube(m, (3.0, 5.0, 3.0), (0, 0, 2.6), col, bev=0.6)
    cube(m, (2.4, 1.6, 1.8), (0, -2.4, 2.4), "window_blue", bev=0.5)
    m.tube([(0, 2.2, 2.9), (0, 5.5, 3.3), (0, 7.0, 3.6)], [0.6, 0.35, 0.3], seg=8, color=col)
    m.prism([(0, 0), (1.2, 0.3), (1.2, 0.9), (0, 0.5)], depth=0.12, color=col, loc=(0, 6.7, 3.5), rot=(0, 90, 0))
    for s in (-1, 1):
        cube(m, (0.18, 5.0, 0.18), (s * 1.3, 0, 0.2), "charcoal", bev=0.04)
        for y in (-1.2, 1.2):
            cube(m, (0.14, 0.14, 1.0), (s * 1.2, y, 0.7), "charcoal", bev=0.03)
    if mil:
        for s in (-1, 1):
            cube(m, (1.6, 0.8, 0.2), (s * 2.0, 0.3, 2.3), col, bev=0.05)
            m.cyl(r=0.25, h=1.8, seg=8, color="gunmetal", rot=(90, 0, 0), loc=(s * 2.4, 0.2, 2.0))
        m.cyl(r=0.08, h=1.2, seg=6, color="gunmetal", rot=(90, 0, 0), loc=(0, -3.4, 1.5))
    cube(m, (0.8, 0.8, 0.5), (0, 0, 4.3), "charcoal", bev=0.1)
    with m.group("Rotor"):
        m.cyl(r=0.3, h=0.3, seg=8, color="charcoal", loc=(0, 0, 4.7))
        for a in (0, 90):
            cube(m, (9.0, 0.5, 0.08), (0, 0, 4.8), "charcoal", rot=(0, 0, a), bev=0.02)
    with m.group("TailRotor"):
        for a in (0, 90):
            cube(m, (0.08, 2.0, 0.3), (0.35, 7.0, 3.6), "charcoal", rot=(a, 0, 0), bev=0.02)


reg("Helicopter", lambda m: _helicopter(m), sub="Aircraft")


def _plane(m, col="plastic_white", accent="plastic_red"):
    m.tube([(0, -4.0, 2.2), (0, -3.0, 2.3), (0, 2.0, 2.4), (0, 4.5, 2.8)], [0.9, 1.1, 0.9, 0.35], seg=8, color=col)
    cube(m, (1.8, 1.6, 0.9), (0, -1.4, 3.1), "window_blue", bev=0.3)
    cube(m, (11.0, 2.0, 0.25), (0, -0.8, 2.3), accent, bev=0.08)
    cube(m, (4.0, 1.2, 0.2), (0, 4.2, 2.9), accent, bev=0.06)
    m.prism([(0, 0), (1.4, 0.4), (1.4, 1.1), (0, 0.6)], depth=0.2, color=accent, loc=(0, 3.9, 2.9), rot=(0, 90, 0),
            scale=(1, 1, 1))
    for s in (-1, 1):
        m.tube([(s * 1.0, -1.0, 2.0), (s * 1.0, -1.0, 0.8)], [0.08, 0.08], seg=4, color="charcoal")
    wheel(m, "WheelL", 1.0, -1.0, 0.45, 0.35)
    wheel(m, "WheelR", -1.0, -1.0, 0.45, 0.35)
    m.cyl(r=0.5, h=0.4, seg=8, color=accent, rot=(90, 0, 0), loc=(0, -4.2, 2.2))
    with m.group("Propeller"):
        m.cyl(r=0.2, h=0.3, seg=6, color="charcoal", rot=(90, 0, 0), loc=(0, -4.5, 2.2))
        cube(m, (3.2, 0.1, 0.35), (0, -4.55, 2.2), "charcoal", bev=0.03)


reg("Airplane", lambda m: _plane(m), sub="Aircraft")


def _balloon(m):
    cols = ["plastic_red", "plastic_yellow", "plastic_blue", "plastic_yellow"]
    m.lathe([(0, 3.4), (1.8, 3.9), (3.0, 5.2), (3.4, 6.8), (3.0, 8.4), (1.8, 9.4), (0, 9.7)], seg=8,
            color=lambda c, n: cols[int((math.degrees(math.atan2(c.y, c.x)) + 382.5) / 45) % 4])
    cube(m, (1.8, 1.8, 1.4), (0, 0, 0.7), "wood", bev=0.12)
    cube(m, (1.9, 1.9, 0.2), (0, 0, 1.35), "wood_dark", bev=0.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.tube([(sx * 0.8, sy * 0.8, 1.4), (sx * 1.6, sy * 1.6, 3.6)], [0.03, 0.03], seg=4, color="rope")
    m.cone(r=0.35, h=0.8, seg=6, color="fire", loc=(0, 0, 2.3))


reg("HotAirBalloon", _balloon, sub="Aircraft")


def _rocket(m):
    m.lathe([(0, 0.6), (1.2, 0.8), (1.3, 4.0), (1.2, 6.5), (0.8, 8.2), (0.3, 9.2), (0, 9.5)], seg=8,
            color=lambda c, n: "plastic_red" if c.z > 7.0 else "plastic_white", cuts={"z": [7.0]})
    for a in range(0, 360, 90):
        m.prism([(0, 0), (1.4, 0), (0.2, 2.2), (0, 2.4)], depth=0.2, color="plastic_red", loc=(0, 0, 0.6),
                rot=(90, 0, a), deform=lambda co: co.__class__((co.x + 1.1, co.y, co.z)))
    m.cyl(r=0.5, h=0.12, seg=8, color="window_blue", rot=(90, 0, 0), loc=(0, -1.26, 5.2))
    m.torus(R=0.5, r=0.1, seg=8, color="silver", rot=(90, 0, 0), loc=(0, -1.28, 5.2))
    m.cone(r=0.8, h=0.6, seg=8, color="gunmetal", rot=(180, 0, 0), loc=(0, 0, 0.7))


reg("Rocket", _rocket, sub="Aircraft")


def _train(m):
    z = 1.2
    cube(m, (3.6, 11.0, 0.8), (0, 0, z), "charcoal", bev=0.15)
    m.cyl(r=1.5, h=6.0, seg=8, color="plastic_green", rot=(90, 0, 0), loc=(0, -2.2, z + 1.9), bevel=0.2)
    for y in (-4.6, -3.2, -1.6):
        m.torus(R=1.5, r=0.12, seg=8, color="gold", rot=(90, 0, 0), loc=(0, y, z + 1.9))
    m.cyl(r=0.45, h=1.6, seg=8, color="charcoal", loc=(0, -4.0, z + 3.8))
    m.cyl(r=0.65, h=0.3, seg=8, color="charcoal", loc=(0, -4.0, z + 4.7))
    m.sphere(r=0.4, color="gold", loc=(0, -1.8, z + 3.4))
    cube(m, (3.6, 3.6, 3.8), (0, 3.4, z + 2.3), "plastic_green", bev=0.2)
    glass_box(m, 3.6, 3.6, 2.4, (0, 3.4, z + 2.6))
    cube(m, (4.0, 4.0, 0.3), (0, 3.4, z + 4.3), "plastic_red", bev=0.08)
    m.prism([(-1.8, 0), (1.8, 0), (0, 1.4)], depth=0.3, color="plastic_red", rot=(90, 0, 0), loc=(0, -5.6, z - 0.2))
    cube(m, (0.6, 0.2, 0.6), (0, -5.25, z + 1.9), "glow", bev=0.08)
    for i, y in enumerate((-3.8, -1.6, 0.6, 3.4)):
        r = 0.9 if i < 3 else 0.7
        wheel(m, f"WheelL{i + 1}", 1.75, y, r, 0.4, tire="plastic_red", hub="charcoal")
        wheel(m, f"WheelR{i + 1}", -1.75, y, r, 0.4, tire="plastic_red", hub="charcoal")


reg("Train", _train, sub="Trains")


# ============================================================================
# batch 2: colour variants + construction, fun & sci-fi vehicles
# ============================================================================
COLORS = {"Red": "plastic_red", "Blue": "plastic_blue", "Green": "plastic_green", "Yellow": "plastic_yellow",
          "Black": "plastic_black", "White": "plastic_white", "Purple": "plastic_purple", "Orange": "plastic_orange",
          "Pink": "plastic_pink", "Tan": "sandstone"}


def motorcycle(m, col="plastic_red", seat="leather_dark"):
    r = 0.9
    cube(m, (0.8, 1.2, 0.9), (0, 0.1, 1.05), "charcoal", bev=0.15)
    cube(m, (0.5, 3.2, 0.4), (0, 0.0, 1.5), "plastic_black", bev=0.1)
    cube(m, (1.0, 1.4, 0.8), (0, -0.55, 2.0), col, bev=0.25)
    cube(m, (0.8, 1.5, 0.3), (0, 0.75, 1.95), seat, bev=0.1)
    cube(m, (0.9, 1.1, 0.35), (0, 1.75, 2.05), col, bev=0.12)
    cube(m, (0.5, 0.12, 0.25), (0, 2.3, 1.95), "neon_red", bev=0.04)
    m.tube([(0, -1.3, 2.4), (0, -1.9, r)], [0.12, 0.1], seg=4, color="chrome")
    m.tube([(0, -1.25, 2.4), (0, -1.45, 2.8)], [0.1, 0.1], seg=4, color="chrome")
    cube(m, (1.8, 0.16, 0.16), (0, -1.45, 2.85), "charcoal", bev=0.04)
    cube(m, (0.9, 0.9, 0.25), (0, -1.9, 1.95), col, bev=0.08)
    cube(m, (0.5, 0.2, 0.4), (0, -1.6, 2.35), "glow", bev=0.06)
    m.cyl(r=0.15, h=1.6, seg=6, color="chrome", rot=(90, 0, 0), loc=(0.5, 1.0, 0.8))
    with m.group("WheelF"):
        m.cyl(r=r, h=0.4, seg=10, rot=(0, 90, 0), loc=(0, -1.9, r), color="rubber", bevel=0.08)
        m.cyl(r=0.45, h=0.45, seg=8, rot=(0, 90, 0), loc=(0, -1.9, r), color="iron")
    with m.group("WheelB"):
        m.cyl(r=r, h=0.5, seg=10, rot=(0, 90, 0), loc=(0, 1.7, r), color="rubber", bevel=0.08)
        m.cyl(r=0.45, h=0.55, seg=8, rot=(0, 90, 0), loc=(0, 1.7, r), color="iron")


def gokart(m, col="plastic_red"):
    z = 0.35
    cube(m, (2.4, 4.0, 0.3), (0, 0, z + 0.15), col, bev=0.1)
    cube(m, (1.6, 1.4, 0.5), (0, -1.5, z + 0.5), col, bev=0.15)
    cube(m, (1.2, 1.0, 0.4), (0, 0.6, z + 0.5), "charcoal", bev=0.12)
    cube(m, (1.2, 0.3, 1.0), (0, 1.1, z + 0.9), "charcoal", bev=0.1)
    m.cyl(r=0.1, h=0.9, seg=6, color="charcoal", rot=(-40, 0, 0), loc=(0, -0.5, z + 0.9))
    m.torus(R=0.35, r=0.07, seg=8, color="charcoal", rot=(-40, 0, 0), loc=(0, -0.2, z + 1.25))
    cube(m, (1.0, 0.8, 0.6), (0, 1.8, z + 0.5), "iron_dark", bev=0.1)
    cube(m, (2.6, 0.5, 0.15), (0, 2.1, z + 1.1), col, bev=0.05)
    wheel(m, "WheelFL", 1.35, -1.3, 0.45, 0.5)
    wheel(m, "WheelFR", -1.35, -1.3, 0.45, 0.5)
    wheel(m, "WheelBL", 1.4, 1.4, 0.55, 0.7)
    wheel(m, "WheelBR", -1.4, 1.4, 0.55, 0.7)


def scooter(m, col="plastic_pink"):
    cube(m, (0.8, 2.6, 0.2), (0, 0, 0.55), col, bev=0.06)
    m.tube([(0, -1.2, 0.6), (0, -1.4, 2.8)], [0.1, 0.1], seg=4, color="silver")
    cube(m, (1.4, 0.14, 0.14), (0, -1.4, 2.85), "charcoal", bev=0.04)
    with m.group("WheelF"):
        m.cyl(r=0.4, h=0.3, seg=10, rot=(0, 90, 0), loc=(0, -1.3, 0.4), color="rubber", bevel=0.05)
    with m.group("WheelB"):
        m.cyl(r=0.4, h=0.3, seg=10, rot=(0, 90, 0), loc=(0, 1.2, 0.4), color="rubber", bevel=0.05)


def sportscar(m, col):
    def ex(m, d):
        cube(m, (d["W"] * 0.9, 0.9, 0.12), (0, d["yb"] - 0.5, d["top"] + 0.5), "charcoal", bev=0.03)
        for s in (-1, 1):
            cube(m, (0.15, 0.15, 0.5), (s * 1.4, d["yb"] - 0.5, d["top"] + 0.2), "charcoal", bev=0.03)
        cube(m, (0.6, 1.8, 0.04), (0, -1.8, d["top"] + 0.01), "charcoal", bev=0.01)
    car(m, L=9.5, W=4.6, body_h=1.1, clear=0.35, col=col, cab_l=3.2, cab_h=1.1, cab_y=0.6, r=0.8, extras=ex)


VARIANTS = [
    ("Car", lambda col: (lambda m: car(m, col=col)), ["Green", "Yellow", "Black", "White", "Purple", "Orange", "Pink"],
     "Cars"),
    ("SportsCar", lambda col: (lambda m: sportscar(m, col)), ["Red", "Blue", "Black", "White", "Green", "Purple"],
     "Cars"),
    ("Jeep", lambda col: (lambda m: car(m, W=4.6, body_h=1.6, clear=0.9, col=col, cab_l=4.6, cab_h=1.7, cab_y=0.8,
                                        roof="charcoal", r=1.05, extras=_jeep)), ["Tan", "Black", "Red", "White"],
     "Cars"),
    ("PickupTruck", lambda col: (lambda m: car(m, L=10.0, W=4.6, body_h=1.6, clear=0.8, col=col, cab_l=3.2, cab_h=1.7,
                                               cab_y=-1.2, r=1.0, extras=_pickup)), ["Red", "Blue", "Black", "White"],
     "Trucks"),
    ("Van", lambda col: (lambda m: van(m, col=col)), ["White", "Red", "Green", "Yellow"], "Trucks"),
    ("Motorcycle", lambda col: (lambda m: motorcycle(m, col)), ["Blue", "Green", "Yellow", "Black"], "Bikes"),
    ("GoKart", lambda col: (lambda m: gokart(m, col)), ["Blue", "Green", "Yellow", "Purple"], "Cars"),
    ("Scooter", lambda col: (lambda m: scooter(m, col)), ["Blue", "Green", "Yellow"], "Bikes"),
]
for _model, _mk, _cols, _sub in VARIANTS:
    for _c in _cols:
        reg(f"{_c}{_model}", _mk(COLORS[_c]), sub=_sub, tags=["color-variant"])


def _limo(m):
    car(m, L=14.0, W=4.6, body_h=1.3, clear=0.5, col="plastic_black", cab_l=9.0, cab_h=1.3, cab_y=0.6, r=0.85)
    cube(m, (0.12, 0.12, 0.6), (0, -6.9, 1.7), "chrome", bev=0.03)


reg("Limousine", _limo)


def _racecar(m):
    z = 0.45
    cube(m, (2.2, 7.0, 0.7), (0, 0.3, z + 0.35), "plastic_red", bev=0.2)
    cube(m, (1.2, 2.0, 0.5), (0, -3.6, z + 0.3), "plastic_red", bev=0.15)
    cube(m, (4.6, 0.9, 0.14), (0, -4.3, z + 0.1), "plastic_black", bev=0.03)
    for s in (-1, 1):
        cube(m, (0.12, 1.0, 0.5), (s * 2.3, -4.3, z + 0.3), "plastic_red", bev=0.03)
    cube(m, (1.2, 1.6, 0.6), (0, 0.4, z + 1.0), "plastic_black", bev=0.15)
    cube(m, (0.8, 0.8, 0.7), (0, 0.6, z + 1.4), "plastic_yellow", bev=0.3)
    cube(m, (0.7, 0.12, 0.3), (0, 0.19, z + 1.45), "black", bev=0.03)
    cube(m, (3.8, 0.8, 0.15), (0, 3.9, z + 1.9), "plastic_red", bev=0.04)
    for s in (-1, 1):
        cube(m, (0.12, 0.8, 1.4), (s * 1.8, 3.9, z + 1.2), "plastic_black", bev=0.03)
        cube(m, (0.9, 2.6, 0.5), (s * 1.3, 1.2, z + 0.5), "plastic_red", bev=0.15)
    for s in (-1, 1):
        cube(m, (0.06, 0.6, 0.6), (s * 1.12, -0.6, z + 0.45), "white", bev=0.02)
    wheel(m, "WheelFL", 1.7, -2.8, 0.6, 0.6)
    wheel(m, "WheelFR", -1.7, -2.8, 0.6, 0.6)
    wheel(m, "WheelBL", 1.8, 2.6, 0.75, 0.9)
    wheel(m, "WheelBR", -1.8, 2.6, 0.75, 0.9)


reg("RaceCar", _racecar)
reg("Hatchback", lambda m: car(m, L=7.6, W=4.2, body_h=1.5, clear=0.55, col="plastic_green", cab_l=4.2, cab_h=1.6,
                               cab_y=0.8, r=0.8))


def _convertible(m):
    z0 = 0.55 + 0.17
    L, W = 9.0, 4.4
    cube(m, (W, L, 1.5), (0, 0, z0 + 0.75), "plastic_blue", bev=0.3)
    cube(m, (W * 0.84, 0.12, 0.8), (0, -0.9, z0 + 1.85), "window_blue", bev=0.03, rot=(-25, 0, 0))
    for x in (-0.9, 0.9):
        cube(m, (1.4, 1.2, 0.4), (x, 0.4, z0 + 1.6), "leather", bev=0.1)
        cube(m, (1.4, 0.3, 1.0), (x, 1.0, z0 + 2.0), "leather", bev=0.1)
    cube(m, (3.2, 1.2, 0.3), (0, 2.8, z0 + 1.55), "plastic_blue", bev=0.08)
    m.torus(R=0.35, r=0.06, seg=8, color="charcoal", rot=(-70, 0, 0), loc=(0.9, -0.3, z0 + 2.0))
    for y in (-L / 2, L / 2):
        cube(m, (W + 0.1, 0.4, 0.5), (0, y + (0.1 if y > 0 else -0.1), z0 + 0.2), "charcoal", bev=0.1)
    lights(m, W, -L / 2, L / 2, z0 + 0.95)
    four_wheels(m, W, -L / 2 + 2.0, L / 2 - 2.0, r=0.85)


reg("Convertible", _convertible)


def _garbage(m, d):
    z = d["z0"] + 1.0
    cube(m, (d["W"], d["box_l"], 4.6), (0, d["box_y"], z + 2.3), "plastic_green", bev=0.3)
    cube(m, (d["W"] * 0.9, 1.6, 3.6), (0, d["box_y"] + d["box_l"] / 2 + 0.5, z + 1.8), "charcoal", bev=0.3)
    for s in (-1, 1):
        cube(m, (0.06, 5.0, 0.4), (s * (d["W"] / 2 + 0.02), d["box_y"], z + 1.0), "plastic_white", bev=0.02)
    m.prism([(0, 0.45), (0.4, -0.2), (-0.4, -0.2)], depth=0.06, color="plastic_white", rot=(90, 0, 90),
            loc=(d["W"] / 2 + 0.03, d["box_y"], z + 3.0))


reg("GarbageTruck", lambda m: truck(m, cab="plastic_white", box=None, extras=_garbage), sub="Construction")


def _mixer(m, d):
    z = d["z0"] + 1.0
    with m.group("Drum"):
        m.lathe([(0.8, 0), (2.1, 1.4), (2.2, 3.4), (1.2, 5.6), (0.8, 5.8)], seg=8, rot=(-75, 0, 0),
                loc=(0, d["box_y"] - 2.4, z + 1.8),
                color=lambda c, n: "plastic_orange" if int((c.y + c.z * 0.3 + 20) / 0.8) % 2 else "plastic_white")
    cube(m, (1.2, 1.4, 2.0), (0, d["box_y"] + 4.2, z + 1.0), "iron_dark", bev=0.1)
    m.tube([(0, d["box_y"] + 4.4, z + 1.6), (0, d["box_y"] + 5.4, z + 0.6)], [(0.3, 0.1), (0.3, 0.1)], seg=4,
           color="iron", up=(1, 0, 0))


reg("CementMixer", lambda m: truck(m, cab="plastic_orange", box=None, extras=_mixer), sub="Construction")


def _dump(m, d):
    z = d["z0"] + 1.0
    with m.group("Bed"):
        cube(m, (d["W"] + 0.3, d["box_l"], 0.4), (0, d["box_y"], z + 0.3), "plastic_yellow", bev=0.1)
        for s in (-1, 1):
            cube(m, (0.3, d["box_l"], 2.4), (s * (d["W"] / 2 + 0.05), d["box_y"], z + 1.5), "plastic_yellow", bev=0.1)
        cube(m, (d["W"] + 0.3, 0.3, 2.4), (0, d["box_y"] - d["box_l"] / 2 + 0.15, z + 1.5), "plastic_yellow", bev=0.1)
        cube(m, (d["W"] - 0.3, d["box_l"] - 0.8, 0.8), (0, d["box_y"] + 0.2, z + 1.0), "dirt", bev=0.3)


reg("DumpTruck", lambda m: truck(m, cab="plastic_yellow", box=None, extras=_dump, r=1.2), sub="Construction")


def _tow(m, d):
    z = d["z0"] + 1.0
    cube(m, (d["W"], d["box_l"], 0.5), (0, d["box_y"], z + 0.25), "charcoal", bev=0.08)
    with m.group("Boom"):
        m.tube([(0, d["box_y"] - 1.0, z + 0.6), (0, d["box_y"] + 2.6, z + 3.4)], [(0.3, 0.3), (0.25, 0.25)], seg=4,
               color="plastic_yellow")
        m.tube([(0, d["box_y"] + 2.6, z + 3.3), (0, d["box_y"] + 2.9, z + 1.0)], [0.03, 0.03], seg=4, color="charcoal")
        m.torus(R=0.25, r=0.07, seg=8, arc=270, color="iron", rot=(0, 90, 0), loc=(0, d["box_y"] + 2.9, z + 0.8))
    cube(m, (1.8, 0.5, 0.3), (0, d["yf"] + 1.6, d["z0"] + 3.75), "plastic_orange", bev=0.05)


reg("TowTruck", lambda m: truck(m, cab="plastic_red", box=None, extras=_tow, six=False), sub="Construction")


def tracks(m, W, L, h=1.2, col="charcoal", wheel_col="gunmetal"):
    for s in (-1, 1):
        cube(m, (0.9, L, h), (s * W / 2, 0, h / 2), col, bev=0.3)
        for k in range(int(L / 1.2)):
            y = -L / 2 + 0.7 + k * 1.2
            m.cyl(r=0.4, h=0.96, seg=8, color=wheel_col, rot=(0, 90, 0), loc=(s * W / 2, y, 0.55))


def _excavator(m):
    tracks(m, 3.4, 6.0)
    cube(m, (2.4, 4.0, 0.6), (0, 0, 1.4), "charcoal", bev=0.1)
    with m.group("Cab"):
        cube(m, (3.6, 4.2, 1.6), (0, 0.6, 2.5), "plastic_yellow", bev=0.25)
        cube(m, (1.6, 1.8, 2.0), (-0.9, -0.6, 4.2), "plastic_yellow", bev=0.2)
        glass_box(m, 1.6, 1.8, 1.8, (-0.9, -0.6, 4.3))
        cube(m, (2.4, 1.2, 1.2), (0, 2.8, 2.9), "charcoal", bev=0.15)
        cube(m, (0.9, 1.2, 1.0), (0.9, -1.3, 3.2), "gunmetal", bev=0.1)
        m.tube([(0.9, -1.3, 3.4), (0.9, -3.8, 6.4)], [(0.4, 0.5), (0.35, 0.45)], seg=4, color="plastic_yellow",
               up=(1, 0, 0))
        m.cyl(r=0.4, h=1.0, seg=8, color="gunmetal", rot=(0, 90, 0), loc=(0.9, -3.8, 6.4))
        m.tube([(0.9, -3.8, 6.4), (0.9, -5.6, 2.8)], [(0.3, 0.4), (0.25, 0.35)], seg=4, color="plastic_yellow",
               up=(1, 0, 0))
        m.cyl(r=0.3, h=0.9, seg=8, color="gunmetal", rot=(0, 90, 0), loc=(0.9, -5.6, 2.8))
        cube(m, (1.8, 1.4, 1.3), (0.9, -5.9, 2.0), "gunmetal", bev=0.2)
        cube(m, (1.8, 0.2, 0.8), (0.9, -6.65, 1.7), "gunmetal", bev=0.05, rot=(20, 0, 0))
        for k in range(4):
            m.pyramid(w=0.26, h=0.4, color="silver", loc=(0.3 + k * 0.4, -6.8, 1.35), rot=(180, 0, 0))


reg("Excavator", _excavator, sub="Construction")


def _bulldozer(m):
    tracks(m, 3.6, 5.6)
    cube(m, (3.0, 4.6, 1.8), (0, 0.3, 2.1), "plastic_yellow", bev=0.25)
    cube(m, (2.6, 2.2, 2.2), (0, 1.0, 4.0), "plastic_yellow", bev=0.2)
    glass_box(m, 2.6, 2.2, 2.0, (0, 1.0, 4.1))
    m.cyl(r=0.2, h=1.4, seg=6, color="charcoal", loc=(0.9, -1.2, 3.6))
    for s in (-1, 1):
        m.tube([(s * 1.5, -0.5, 1.5), (s * 1.6, -3.4, 1.0)], [0.2, 0.2], seg=4, color="charcoal")
    with m.group("Blade"):
        m.box((5.2, 0.5, 1.8), color="plastic_yellow", bevel=0.1, loc=(0, -3.8, 1.0),
              deform=lambda co: co.__class__((co.x, co.y - 0.3 * (co.z / 0.9) ** 2, co.z)))
        cube(m, (5.2, 0.4, 0.3), (0, -4.1, 0.1), "silver", bev=0.05)


reg("Bulldozer", _bulldozer, sub="Construction")


def _forklift(m):
    cube(m, (2.4, 3.0, 1.4), (0, 0.4, 1.3), "plastic_orange", bev=0.25)
    cube(m, (2.4, 1.0, 1.6), (0, 1.6, 1.8), "charcoal", bev=0.2)
    for x in (-1.0, 1.0):
        for y in (-0.8, 1.2):
            cube(m, (0.12, 0.12, 2.6), (x, y, 3.3), "charcoal", bev=0.03)
    cube(m, (2.4, 2.4, 0.15), (0, 0.2, 4.6), "charcoal", bev=0.05)
    cube(m, (1.0, 0.8, 0.9), (0, 0.8, 2.3), "leather_dark", bev=0.12)
    for x in (-0.7, 0.7):
        cube(m, (0.12, 0.12, 4.6), (x, -1.3, 2.4), "gunmetal", bev=0.03)
    with m.group("Forks"):
        cube(m, (1.8, 0.2, 1.2), (0, -1.5, 1.0), "gunmetal", bev=0.04)
        for x in (-0.55, 0.55):
            cube(m, (0.3, 2.2, 0.12), (x, -2.6, 0.5), "silver", bev=0.03)
    wheel(m, "WheelFL", 1.2, -0.6, 0.6, 0.5)
    wheel(m, "WheelFR", -1.2, -0.6, 0.6, 0.5)
    wheel(m, "WheelBL", 1.2, 1.4, 0.5, 0.45)
    wheel(m, "WheelBR", -1.2, 1.4, 0.5, 0.45)


reg("Forklift", _forklift, sub="Construction")


def _snowmobile(m):
    cube(m, (2.0, 4.4, 1.0), (0, 0.2, 1.0), "plastic_blue", bev=0.3)
    cube(m, (1.8, 1.8, 0.8), (0, -1.6, 1.3), "plastic_blue", bev=0.3, rot=(15, 0, 0))
    cube(m, (1.6, 0.12, 0.8), (0, -1.0, 2.0), "window_blue", bev=0.03, rot=(-30, 0, 0))
    cube(m, (1.0, 2.0, 0.4), (0, 1.0, 1.7), "plastic_black", bev=0.12)
    m.tube([(0, -0.5, 1.8), (0, -0.7, 2.3)], [0.08, 0.08], seg=4, color="charcoal")
    cube(m, (1.4, 0.12, 0.12), (0, -0.7, 2.3), "charcoal", bev=0.03)
    cube(m, (1.4, 3.0, 0.6), (0, 1.3, 0.35), "charcoal", bev=0.2)
    for s in (-1, 1):
        m.tube([(s * 0.8, -1.4, 0.8), (s * 0.9, -1.8, 0.2)], [0.08, 0.08], seg=4, color="charcoal")
        m.box((0.3, 2.4, 0.12), color="silver", loc=(s * 0.9, -2.2, 0.08), bevel=0.04,
              deform=lambda co: co.__class__((co.x, co.y, co.z + max(0.0, -co.y - 0.8) * 0.4)))


reg("Snowmobile", _snowmobile, sub="Bikes")


def _atv(m):
    cube(m, (2.2, 3.4, 0.9), (0, 0, 1.4), "plastic_red", bev=0.3)
    cube(m, (2.6, 1.2, 0.3), (0, -1.6, 1.9), "plastic_black", bev=0.08)
    cube(m, (2.6, 1.2, 0.3), (0, 1.6, 1.9), "plastic_black", bev=0.08)
    cube(m, (0.9, 1.4, 0.4), (0, 0.5, 2.0), "leather_dark", bev=0.12)
    m.tube([(0, -0.9, 1.8), (0, -1.1, 2.5)], [0.08, 0.08], seg=4, color="charcoal")
    cube(m, (1.6, 0.12, 0.12), (0, -1.1, 2.5), "charcoal", bev=0.03)
    cube(m, (0.5, 0.12, 0.3), (0, -1.75, 1.5), "glow", bev=0.04)
    four_wheels(m, 3.0, -1.4, 1.4, r=0.8, w=0.8, inset=0.2)


reg("ATV", _atv, sub="Bikes")


def _bicycle(m):
    for nm, y in (("WheelF", -1.5), ("WheelB", 1.5)):
        with m.group(nm):
            m.torus(R=0.9, r=0.1, seg=12, rot=(0, 90, 0), loc=(0, y, 1.0), color="rubber")
            m.cyl(r=0.15, h=0.2, seg=6, rot=(0, 90, 0), loc=(0, y, 1.0), color="silver")
            for a in (0, 60, 120):
                cube(m, (0.04, 0.04, 1.7), (0, y, 1.0), "silver", rot=(a, 0, 0), bev=0.01)
    for a, b in (((0, 1.5, 1.0), (0, 0.2, 2.2)), ((0, 0.2, 2.2), (0, -1.1, 2.2)), ((0, -1.1, 2.2), (0, -1.5, 1.0)),
                 ((0, 0.2, 2.2), (0, 0.0, 1.0)), ((0, 0.0, 1.0), (0, 1.5, 1.0)), ((0, 0.0, 1.0), (0, -1.1, 2.2))):
        m.tube([a, b], [0.07, 0.07], seg=4, color="plastic_blue")
    cube(m, (0.4, 0.8, 0.15), (0, 0.3, 2.5), "black", bev=0.05)
    m.tube([(0, -1.1, 2.2), (0, -1.2, 2.8)], [0.06, 0.06], seg=4, color="silver")
    cube(m, (1.4, 0.1, 0.1), (0, -1.2, 2.8), "charcoal", bev=0.03)


reg("Bicycle", _bicycle, sub="Bikes")


def _skateboard(m):
    m.box((0.9, 3.0, 0.1), color="wood_light", bevel=0.04, loc=(0, 0, 0.45),
          deform=lambda co: co.__class__((co.x, co.y, co.z + max(0.0, abs(co.y) - 1.1) * 0.35)))
    m.box((0.85, 2.2, 0.02), color="plastic_purple", bevel=0.01, loc=(0, 0, 0.51))
    for y in (-0.95, 0.95):
        cube(m, (0.6, 0.2, 0.15), (0, y, 0.33), "silver", bev=0.03)
    for nm, x, y in (("WheelFL", 0.35, -0.95), ("WheelFR", -0.35, -0.95), ("WheelBL", 0.35, 0.95),
                     ("WheelBR", -0.35, 0.95)):
        with m.group(nm):
            m.cyl(r=0.16, h=0.18, seg=8, rot=(0, 90, 0), loc=(x, y, 0.16), color="plastic_yellow")


reg("Skateboard", _skateboard, sub="Bikes")


def _hoverboard(m):
    cube(m, (1.2, 3.2, 0.25), (0, 0, 0.9), "plastic_white", bev=0.1)
    cube(m, (1.0, 2.8, 0.08), (0, 0, 0.75), "neon_blue", bev=0.03)
    for y in (-1.0, 1.0):
        m.cyl(r=0.35, h=0.3, seg=8, color="charcoal", loc=(0, y, 0.55))
        m.cyl(r=0.28, h=0.05, seg=8, color="neon_blue", loc=(0, y, 0.38))


reg("Hoverboard", _hoverboard, sub="Bikes", tags=["sci-fi"])


def _ufo(m):
    m.lathe([(0, 1.0), (2.0, 1.1), (3.6, 1.6), (4.0, 1.9), (3.6, 2.2), (2.0, 2.5), (0, 2.6)], seg=8, color="silver")
    m.lathe([(1.6, 2.5), (1.5, 3.2), (0.9, 3.8), (0, 4.0)], seg=8, color="window_blue")
    m.sphere(round=True, r=0.35, color="slime", loc=(0, 0, 3.1))
    with m.group("Ring"):
        for a in range(0, 360, 45):
            r = math.radians(a)
            cube(m, (0.4, 0.4, 0.3), (math.cos(r) * 3.3, math.sin(r) * 3.3, 1.55), "glow", bev=0.08)
    m.cone(r=1.4, h=1.0, seg=8, color="neon_green", rot=(180, 0, 0), loc=(0, 0, 1.0))


reg("UFO", _ufo, sub="Aircraft", tags=["sci-fi"])


def _spaceship(m):
    m.tube([(0, -4.5, 2.0), (0, -3.0, 2.1), (0, 2.0, 2.1), (0, 3.2, 2.0)], [0.2, 1.0, 1.1, 0.9], seg=8,
           color="plastic_white")
    cube(m, (1.2, 2.0, 0.9), (0, -1.8, 2.9), "window_blue", bev=0.3)
    for s in (-1, 1):
        m.prism([(0, -1.0), (3.6, 1.6), (3.6, 2.6), (0, 2.4)], depth=0.25, color="plastic_blue", loc=(0, 0, 1.8),
                scale=(s, 1, 1))
        m.cyl(r=0.5, h=2.2, seg=8, color="gunmetal", rot=(90, 0, 0), loc=(s * 3.4, 2.2, 1.8))
        m.cyl(r=0.4, h=0.2, seg=8, color="neon_blue", rot=(90, 0, 0), loc=(s * 3.4, 3.35, 1.8))
        m.pyramid(w=0.2, h=0.6, color="plastic_red", loc=(s * 3.6, 0.6, 1.9), rot=(90, 0, 0))
    m.cyl(r=0.8, h=0.3, seg=8, color="fire", rot=(90, 0, 0), loc=(0, 3.35, 2.0))
    m.prism([(0, 0), (1.4, 0.3), (1.4, 1.2), (0, 0.6)], depth=0.2, color="plastic_blue", rot=(0, 90, 0),
            loc=(0, 1.6, 2.9))
    for x, y in ((0, -2.8), (1.6, 1.0), (-1.6, 1.0)):
        m.tube([(x, y, 1.5), (x, y, 0.2)], [0.07, 0.07], seg=4, color="charcoal")
        cube(m, (0.5, 0.5, 0.12), (x, y, 0.1), "charcoal", bev=0.03)


reg("Spaceship", _spaceship, sub="Aircraft", tags=["sci-fi", "space"])


def _submarine(m):
    m.tube([(0, -4.5, 1.8), (0, -3.5, 1.9), (0, 3.0, 1.9), (0, 4.5, 1.8)], [0.4, 1.6, 1.5, 0.5], seg=8,
           color="plastic_yellow")
    cube(m, (1.2, 2.4, 1.6), (0, -0.6, 3.8), "plastic_yellow", bev=0.3)
    m.tube([(0.3, -1.0, 4.5), (0.3, -1.0, 5.6), (0.3, -1.5, 5.6)], [0.1, 0.1, 0.1], seg=4, color="gunmetal")
    for y in (-2.6, -1.3, 0.0, 1.3):
        m.cyl(r=0.4, h=0.1, seg=8, color="window_blue", rot=(0, 90, 0), loc=(1.52, y, 2.0))
        m.torus(R=0.42, r=0.08, seg=8, color="gunmetal", rot=(0, 90, 0), loc=(1.54, y, 2.0))
    for s in (-1, 1):
        m.prism([(0, 0), (1.2, 0.4), (1.2, 0.8), (0, 0.8)], depth=0.12, color="plastic_yellow",
                loc=(s * 0.8, 3.4, 1.8), scale=(s, 1, 1))
    with m.group("Propeller"):
        m.cyl(r=0.15, h=0.5, seg=6, color="gunmetal", rot=(90, 0, 0), loc=(0, 4.9, 1.8))
        for a in (0, 120, 240):
            cube(m, (0.2, 0.06, 0.8), (0, 5.1, 1.8), "bronze", rot=(0, a, 0), bev=0.02,
                 deform=lambda co: co.__class__((co.x, co.y, co.z + 0.4)))


reg("Submarine", _submarine, sub="Boats")


def _sailboat(m):
    m.box((3.0, 8.0, 1.4), color=lambda c, n: "plastic_white" if c.z > 0.8 else "plastic_red", bevel=0.3,
          loc=(0, 0, 0.7), cuts={"z": [0.8]},
          deform=lambda co: co.__class__((co.x * (1.0 - max(0.0, -co.y - 1.0) / 3.0 * 0.95), co.y, co.z)))
    cube(m, (2.4, 5.0, 0.1), (0, 0.8, 1.42), "wood_light", bev=0.02)
    m.cyl(r=0.12, h=9.0, seg=6, color="wood", loc=(0, 0.0, 5.9))
    m.cyl(r=0.08, h=4.0, seg=6, color="wood", rot=(90, 0, 0), loc=(0, 1.9, 2.6))
    m.panel([(0, 0.1, 10.2), (0, 0.1, 2.8), (0, 3.8, 2.8)], 0.06, "white")
    m.panel([(0, -0.1, 9.8), (0, -3.6, 1.6), (0, -0.1, 1.6)], 0.06, "fabric_cream")
    m.box((0.06, 0.8, 0.5), color="plastic_red", loc=(0, 0.3, 10.4), bevel=0.01)


reg("Sailboat", _sailboat, sub="Boats")


def _jetski(m):
    m.box((1.6, 4.0, 0.9), color=lambda c, n: "plastic_white" if c.z > 0.5 else "plastic_blue", bevel=0.25,
          loc=(0, 0, 0.45), cuts={"z": [0.5]},
          deform=lambda co: co.__class__((co.x * (1.0 - max(0.0, -co.y - 0.8) / 1.4 * 0.7), co.y, co.z)))
    cube(m, (0.8, 1.6, 0.4), (0, 0.6, 1.1), "plastic_black", bev=0.12)
    m.tube([(0, -0.6, 0.9), (0, -0.8, 1.5)], [0.08, 0.08], seg=4, color="charcoal")
    cube(m, (1.2, 0.1, 0.1), (0, -0.8, 1.5), "charcoal", bev=0.03)
    cube(m, (1.0, 0.6, 0.3), (0, -1.2, 1.0), "plastic_blue", bev=0.1, rot=(-20, 0, 0))


reg("JetSki", _jetski, sub="Boats")


def _blimp(m):
    m.lathe([(0, -5.0), (1.6, -4.0), (2.4, -2.0), (2.5, 1.0), (2.0, 3.6), (0.9, 5.2), (0, 5.6)], seg=8,
            color=lambda c, n: "plastic_white" if abs(c.x) > 0.6 or c.z < 5.6 else "plastic_red", rot=(-90, 0, 0),
            loc=(0, 0, 6.0))
    for a in (0, 90, 180, 270):
        m.prism([(0, 0), (1.6, 0), (1.6, 1.0), (0.2, 2.2)], depth=0.15, color="plastic_red", rot=(90, 0, a),
                loc=(0, 3.4, 6.0), deform=lambda co: co.__class__((co.x + 1.5, co.y, co.z)), scale=(1, 1, 1))
    cube(m, (1.4, 2.8, 1.0), (0, -0.4, 3.2), "plastic_red", bev=0.2)
    cube(m, (1.46, 2.0, 0.5), (0, -0.4, 3.35), "window_blue", bev=0.05)
    with m.group("Propeller"):
        for s in (-1, 1):
            m.cyl(r=0.2, h=0.6, seg=6, color="charcoal", rot=(0, 90, 0), loc=(s * 1.0, 0.6, 3.2))
            cube(m, (0.06, 0.2, 1.2), (s * 1.35, 0.6, 3.2), "charcoal", bev=0.02)


reg("Blimp", _blimp, sub="Aircraft")


# ============================================================================
# Batch 4: supercars, muscle cars, SUVs, minivans, compacts, classics (in colours)
# and specials: police SUV, interceptor, rally, drift, buggy, lowrider, hot rod...
# ============================================================================
from studlib.font import text  # noqa: E402


def side_text(m, s, W, y, z, col="white", px=0.14):
    """Pixel lettering on both flanks of a vehicle."""
    for sx, ang in ((1, 90), (-1, -90)):
        with m.at((sx * (W / 2 + 0.02), y, z), ang):
            text(m, s, 0, 0, 0, px=px, depth=0.08, col=col)


def supercar(m, col, trim="charcoal", police=False, stripe=None):
    L, W, r = 10.4, 4.8, 0.8
    z0 = 0.35 + r * 0.2
    zt = z0 + 1.0
    cube(m, (W, L, 1.0), (0, 0, z0 + 0.5), col, bev=0.3)
    m.wedge((W - 0.2, 3.2, 0.6), color=col, loc=(0, -L / 2 + 1.7, zt + 0.3), rot=(0, 0, 180))
    cube(m, (W * 0.78, 3.2, 0.9), (0, 0.9, zt + 0.45), col, bev=0.35)
    glass_box(m, W * 0.78, 3.2, 0.9, (0, 0.9, zt + 0.42))
    m.wedge((W * 0.76, 1.4, 0.88), color="window_blue", loc=(0, -1.4, zt + 0.44), rot=(0, 0, 180))
    m.wedge((W * 0.8, 2.2, 0.7), color=col, loc=(0, 3.4, zt + 0.35))
    cube(m, (W + 0.2, 1.1, 0.16), (0, L / 2 - 0.6, zt + 1.35), trim, bev=0.04)
    for s in (-1, 1):
        cube(m, (0.2, 0.3, 1.0), (s * 1.5, L / 2 - 0.6, zt + 0.8), trim, bev=0.04)
        cube(m, (0.12, 1.8, 0.55), (s * (W / 2 + 0.02), 1.9, z0 + 0.6), "black", bev=0.03)
        cube(m, (0.9, 0.12, 0.2), (s * (W / 2 - 0.7), -L / 2 - 0.02, z0 + 0.75), "glow", bev=0.03)
        cube(m, (1.2, 0.12, 0.2), (s * (W / 2 - 0.8), L / 2 + 0.02, z0 + 0.75), "neon_red", bev=0.03)
        m.cyl(r=0.18, h=0.4, seg=6, color="chrome", rot=(90, 0, 0), loc=(s * 0.5, L / 2 + 0.1, z0 + 0.25))
    cube(m, (W * 0.6, 0.12, 0.3), (0, -L / 2 - 0.02, z0 + 0.3), "black", bev=0.03)
    if stripe:
        for s in (-1, 1):
            cube(m, (0.45, L * 0.55, 0.05), (s * 0.45, 0.4, zt + 0.93), stripe, bev=0.01)
    if police:
        cube(m, (1.8, 0.5, 0.3), (0, 0.9, zt + 1.0), "charcoal", bev=0.05)
        cube(m, (0.8, 0.46, 0.24), (0.45, 0.9, zt + 1.2), "plastic_blue", bev=0.05)
        cube(m, (0.8, 0.46, 0.24), (-0.45, 0.9, zt + 1.2), "neon_red", bev=0.05)
        side_text(m, "POLICE", W, 0.4, z0 + 0.55, "white", 0.13)
    four_wheels(m, W, -L / 2 + 2.2, L / 2 - 2.3, r=r, w=0.8, hub="chrome")


def muscle(m, col, stripe="white"):
    def ex(m, d):
        for s in (-1, 1):
            cube(m, (0.5, d["L"] + 0.02, 0.05), (s * 0.45, 0, d["top"] + 0.01), stripe, bev=0.01)
            cube(m, (0.5, d["cab_l"] * 0.95, 0.05), (s * 0.45, d["cab_y"], d["top"] + d["cab_h"] - 0.03), stripe, bev=0.01)
            m.cyl(r=0.2, h=0.5, seg=6, color="chrome", rot=(90, 0, 0), loc=(s * 1.4, d["yb"] + 0.2, d["z0"] + 0.25))
        cube(m, (1.4, 1.6, 0.45), (0, d["yf"] + 2.0, d["top"] + 0.2), "charcoal", bev=0.1)
        cube(m, (1.2, 0.1, 0.3), (0, d["yf"] + 1.2, d["top"] + 0.25), "black")
        cube(m, (d["W"] * 0.9, 0.5, 0.14), (0, d["yb"] - 0.3, d["top"] + 0.1), col, bev=0.04)
        cube(m, (d["W"] * 0.6, 0.1, 0.5), (0, d["yf"] - 0.04, d["bz"]), "chrome", bev=0.03)
    car(m, L=10.6, W=4.6, body_h=1.35, clear=0.45, col=col, cab_l=3.2, cab_h=1.3, cab_y=1.4, r=0.9, extras=ex,
        bumper="chrome")


def suv(m, col, police=False):
    def ex(m, d):
        for s in (-1, 1):
            cube(m, (0.2, d["cab_l"] * 0.9, 0.2), (s * (d["W"] * 0.38), d["cab_y"], d["top"] + d["cab_h"] + 0.15),
                 "charcoal", bev=0.04)
        m.cyl(r=0.85, h=0.5, seg=10, color="rubber", rot=(90, 0, 0), loc=(0, d["yb"] + 0.35, d["bz"] + 0.6), bevel=0.08)
        cube(m, (d["W"] * 0.55, 0.1, 0.8), (0, d["yf"] - 0.03, d["bz"] + 0.1), "chrome", bev=0.03)
        if police:
            _police(m, d)
            side_text(m, "POLICE", d["W"], 0.4, d["bz"] + 0.05, "white", 0.14)
    car(m, L=10.6, W=4.8, body_h=2.0, clear=0.9, col=col, cab_l=6.6, cab_h=1.8, cab_y=0.9, r=1.0, extras=ex,
        roof="charcoal" if not police else None)


def minivan(m, col):
    def ex(m, d):
        for s in (-1, 1):
            cube(m, (0.06, 0.1, d["cab_h"] + 1.2), (s * (d["W"] / 2 + 0.01), 0.6, d["top"] + 0.1), "charcoal", bev=0.01)
            cube(m, (0.1, 0.8, 0.14), (s * (d["W"] / 2 + 0.05), 1.0, d["bz"] + 0.5), "charcoal", bev=0.03)
    car(m, L=10.4, W=4.6, body_h=1.8, clear=0.6, col=col, cab_l=7.4, cab_h=2.0, cab_y=1.0, r=0.85, extras=ex)


def compact(m, col):
    def ex(m, d):
        for s in (-1, 1):
            m.cyl(r=0.32, h=0.12, seg=8, color="glow", rot=(90, 0, 0), loc=(s * 1.3, d["yf"] - 0.05, d["bz"] + 0.2))
        cube(m, (d["W"] * 0.7, d["cab_l"] * 0.7, 0.1), (0, d["cab_y"], d["top"] + d["cab_h"] + 0.02), "white", bev=0.03)
    car(m, L=7.4, W=4.0, body_h=1.4, clear=0.5, col=col, cab_l=4.2, cab_h=1.7, cab_y=0.5, r=0.75, extras=ex)


def classic(m, col, trim="chrome"):
    L, W, r = 10.0, 4.0, 0.95
    z0 = 0.9
    cube(m, (W - 0.6, L - 1.0, 1.4), (0, 0.2, z0 + 0.7), col, bev=0.25)
    cube(m, (W * 0.85, 3.8, 1.8), (0, 1.2, z0 + 2.3), col, bev=0.3)
    glass_box(m, W * 0.85, 3.8, 1.8, (0, 1.2, z0 + 2.3))
    cube(m, (W * 0.9, 0.2, 0.3), (0, 1.2, z0 + 3.25), "black", bev=0.05)
    cube(m, (1.8, 0.3, 1.5), (0, -L / 2 + 0.6, z0 + 0.9), trim, bev=0.06)
    for k in range(5):
        cube(m, (0.1, 0.34, 1.2), (-0.6 + k * 0.3, -L / 2 + 0.55, z0 + 0.9), "charcoal", bev=0.02)
    for s in (-1, 1):
        for y in (-L / 2 + 2.0, L / 2 - 2.2):
            m.cyl(r=r + 0.3, h=1.0, seg=8, color=col, rot=(0, 90, 0), loc=(s * (W / 2 - 0.1), y, r + 0.2),
                  deform=lambda co: co.__class__((co.x, co.y, max(co.z, -0.1))))
        cube(m, (0.8, 4.6, 0.15), (s * (W / 2 - 0.1), 0.0, z0 - 0.1), "charcoal", bev=0.03)
        m.cyl(r=0.35, h=0.3, seg=8, color="glow", rot=(90, 0, 0), loc=(s * (W / 2 - 0.4), -L / 2 + 1.6, z0 + 1.5))
        m.cyl(r=0.4, h=0.1, seg=8, color=trim, rot=(90, 0, 0), loc=(s * (W / 2 - 0.4), -L / 2 + 1.5, z0 + 1.5))
    m.cyl(r=0.9, h=0.4, seg=10, color="rubber", rot=(90, 0, 0), loc=(0, L / 2 - 0.1, z0 + 1.2), bevel=0.08)
    m.cyl(r=0.5, h=0.45, seg=8, color="white", rot=(90, 0, 0), loc=(0, L / 2 - 0.1, z0 + 1.2))
    for y in (-L / 2 + 0.2, L / 2 - 0.4):
        cube(m, (W - 0.2, 0.3, 0.3), (0, y, z0 + 0.1), trim, bev=0.08)
    four_wheels(m, W + 0.5, -L / 2 + 2.0, L / 2 - 2.2, r=r, w=0.6, hub="white")


CAR_VARIANTS = [
    ("Supercar", lambda c: (lambda m: supercar(m, c)), ["Red", "Yellow", "Orange", "Black", "White", "Green", "Blue",
                                                         "Purple"], "Supercars"),
    ("MuscleCar", lambda c: (lambda m: muscle(m, c, "white" if c != "plastic_white" else "plastic_red")),
     ["Red", "Blue", "Black", "Orange", "Green", "White"], "Cars"),
    ("SUV", lambda c: (lambda m: suv(m, c)), ["Black", "White", "Red", "Blue", "Green", "Tan"], "Cars"),
    ("Minivan", lambda c: (lambda m: minivan(m, c)), ["White", "Blue", "Red", "Green"], "Cars"),
    ("CompactCar", lambda c: (lambda m: compact(m, c)), ["Yellow", "Pink", "Blue", "Green", "Orange", "Purple"], "Cars"),
    ("ClassicCar", lambda c: (lambda m: classic(m, c)), ["Red", "Black", "Blue", "White", "Tan"], "Classics"),
]
for _model, _mk, _cols, _sub in CAR_VARIANTS:
    for _c in _cols:
        reg(f"{_c}{_model}", _mk(COLORS[_c]), sub=_sub, tags=["color-variant"])


# --- specials ------------------------------------------------------------------------
reg("PoliceSUV", lambda m: suv(m, "plastic_white", police=True), sub="Service")
reg("PoliceInterceptor", lambda m: supercar(m, "plastic_black", police=True, stripe="plastic_white"), sub="Service")
reg("StripedSupercar", lambda m: supercar(m, "plastic_blue", stripe="plastic_white"), sub="Supercars")


def _rally(m):
    def ex(m, d):
        m.box((d["W"] + 0.04, d["L"] * 0.8, 0.5), color=lambda c, n: "plastic_red" if c.y < 0.5 else "plastic_yellow",
              loc=(0, 0.3, d["bz"]), cuts={"y": [0.5]}, bevel=0.04)
        for sx, ang in ((1, 90), (-1, -90)):
            with m.at((sx * (d["W"] / 2 + 0.03), -0.3, d["bz"] + 0.45), ang):
                m.cyl(r=0.6, h=0.06, seg=8, color="white", rot=(90, 0, 0))
                text(m, "7", 0, -0.04, 0, px=0.16, depth=0.06, col="black")
        cube(m, (1.0, 1.2, 0.35), (0, d["cab_y"] - 0.4, d["top"] + d["cab_h"] + 0.1), "charcoal", bev=0.08)
        for x in (-1.2, -0.4, 0.4, 1.2):
            m.cyl(r=0.28, h=0.2, seg=8, color="glow", rot=(90, 0, 0), loc=(x, d["yf"] - 0.2, d["bz"] + 0.6))
        for s in (-1, 1):
            cube(m, (0.8, 0.1, 0.7), (s * (d["W"] / 2 - 0.5), d["yb"] - 1.3, d["z0"] + 0.2), "black", bev=0.02)
        cube(m, (d["W"] * 0.85, 0.7, 0.12), (0, d["yb"] - 0.4, d["top"] + 0.7), "charcoal", bev=0.03)
    car(m, L=8.6, W=4.4, body_h=1.4, clear=0.8, col="plastic_white", cab_l=4.4, cab_h=1.6, cab_y=0.6, r=0.85, extras=ex)


def _drift(m):
    def ex(m, d):
        for s in (-1, 1):
            for y in (d["yf"] + d["L"] * 0.22, d["yb"] - d["L"] * 0.22):
                cube(m, (0.6, 2.6, 0.9), (s * (d["W"] / 2 + 0.1), y, d["bz"] + 0.1), "plastic_purple", bev=0.2)
        cube(m, (d["W"] + 0.6, 1.1, 0.14), (0, d["yb"] - 0.5, d["top"] + 1.0), "charcoal", bev=0.04)
        for s in (-1, 1):
            cube(m, (0.15, 0.3, 0.9), (s * 1.6, d["yb"] - 0.5, d["top"] + 0.5), "charcoal", bev=0.03)
        cube(m, (d["W"] - 0.4, d["L"] - 1.0, 0.1), (0, 0, d["z0"] - 0.15), "neon_blue")
    car(m, L=9.6, W=4.6, body_h=1.1, clear=0.3, col="plastic_purple", col2="plastic_purple", cab_l=3.4, cab_h=1.1,
        cab_y=0.6, r=0.8, extras=ex)


def _dune_buggy(m):
    W, L, r = 4.6, 8.6, 1.1
    z0 = 1.4
    cube(m, (W - 1.2, L - 2.0, 0.4), (0, 0, z0), "charcoal", bev=0.08)
    for s in (-1, 1):
        m.tube([(s * 1.6, -2.8, z0 + 0.2), (s * 1.5, -1.0, z0 + 3.2), (s * 1.5, 1.6, z0 + 3.2), (s * 1.7, 3.2, z0 + 0.2)],
               [0.12] * 4, seg=4, color="plastic_orange")
        m.tube([(s * 1.6, -2.8, z0 + 0.2), (s * 1.8, -4.0, z0 + 0.6)], [0.1, 0.1], seg=4, color="plastic_orange")
    for y in (-1.0, 1.6):
        m.tube([(-1.5, y, z0 + 3.2), (1.5, y, z0 + 3.2)], [0.12, 0.12], seg=4, color="plastic_orange")
    for x in (-0.7, 0.7):
        cube(m, (1.1, 1.2, 0.4), (x, 0.6, z0 + 0.4), "charcoal", bev=0.1)
        cube(m, (1.1, 0.3, 1.4), (x, 1.2, z0 + 1.2), "charcoal", bev=0.1)
    cube(m, (1.8, 1.6, 1.2), (0, 2.8, z0 + 0.8), "iron_dark", bev=0.1)
    m.cyl(r=0.1, h=0.8, seg=6, color="charcoal", rot=(-40, 0, 0), loc=(-0.7, -0.6, z0 + 1.2))
    m.torus(R=0.35, r=0.06, seg=8, color="charcoal", rot=(-40, 0, 0), loc=(-0.7, -0.35, z0 + 1.55))
    cube(m, (W - 1.0, 1.2, 0.3), (0, -L / 2 + 0.6, z0 + 0.3), "plastic_orange", bev=0.06)
    wheel(m, "WheelFL", W / 2, -L / 2 + 1.8, 0.95, 0.8)
    wheel(m, "WheelFR", -W / 2, -L / 2 + 1.8, 0.95, 0.8)
    wheel(m, "WheelBL", W / 2 + 0.1, L / 2 - 1.6, r, 1.1)
    wheel(m, "WheelBR", -W / 2 - 0.1, L / 2 - 1.6, r, 1.1)


def _lowrider(m):
    def ex(m, d):
        for s in (-1, 1):
            cube(m, (0.06, d["L"] * 0.8, 0.12), (s * (d["W"] / 2 + 0.02), 0, d["bz"] + 0.3), "chrome", bev=0.01)
        cube(m, (d["W"] * 0.7, 0.1, 0.6), (0, d["yf"] - 0.04, d["bz"]), "chrome", bev=0.03)
    car(m, L=12.0, W=4.6, body_h=1.1, clear=0.2, col="plastic_purple", cab_l=4.2, cab_h=1.3, cab_y=1.0, r=0.8,
        extras=ex, bumper="chrome")


def _hot_rod(m):
    L, W = 9.6, 4.0
    z0 = 1.0
    cube(m, (W - 1.0, L - 1.5, 0.5), (0, 0.4, z0), "charcoal", bev=0.1)
    cube(m, (W - 0.6, 3.6, 1.6), (0, 1.8, z0 + 1.0), "plastic_red", bev=0.25)
    cube(m, (W - 0.8, 2.6, 1.2), (0, 2.0, z0 + 2.3), "plastic_red", bev=0.25)
    glass_box(m, W - 0.8, 2.6, 1.2, (0, 2.0, z0 + 2.3))
    cube(m, (2.0, 3.0, 1.2), (0, -1.6, z0 + 0.9), "plastic_red", bev=0.2)
    cube(m, (1.6, 2.2, 1.0), (0, -2.2, z0 + 1.9), "chrome", bev=0.1)
    cube(m, (1.2, 1.0, 0.8), (0, -2.2, z0 + 2.7), "iron_dark", bev=0.1)
    for s in (-1, 1):
        for k in range(4):
            m.tube([(s * 0.9, -3.0 + k * 0.5, z0 + 1.6), (s * 1.6, -2.8 + k * 0.5, z0 + 0.9), (s * 1.8, 0.8, z0 + 0.4)],
                   [0.09] * 3, seg=4, color="chrome")
        for k, (y, h, c) in enumerate(((1.0, 1.0, "fire"), (1.8, 0.8, "fire_light"), (2.6, 0.6, "fire"))):
            m.prism([(-0.3, 0), (0.3, 0), (0, h)], depth=0.06, color=c, rot=(90, 0, 90), loc=(s * (W / 2 - 0.28), y - 1.2,
                                                                                          z0 + 0.6))
    cube(m, (1.8, 0.2, 1.2), (0, -3.6, z0 + 1.0), "chrome", bev=0.05)
    wheel(m, "WheelFL", W / 2 - 0.2, -L / 2 + 1.4, 0.75, 0.5, hub="chrome")
    wheel(m, "WheelFR", -W / 2 + 0.2, -L / 2 + 1.4, 0.75, 0.5, hub="chrome")
    wheel(m, "WheelBL", W / 2 + 0.2, L / 2 - 1.8, 1.2, 1.2, hub="chrome")
    wheel(m, "WheelBR", -W / 2 - 0.2, L / 2 - 1.8, 1.2, 1.2, hub="chrome")


def _offroad(m):
    def ex(m, d):
        _pickup(m, d)
        cube(m, (d["W"] * 0.8, 0.4, 0.3), (0, d["cab_y"] - d["cab_l"] / 2 + 0.3, d["top"] + d["cab_h"] + 0.2), "charcoal",
             bev=0.05)
        for x in (-1.2, -0.4, 0.4, 1.2):
            cube(m, (0.6, 0.2, 0.25), (x, d["cab_y"] - d["cab_l"] / 2 + 0.1, d["top"] + d["cab_h"] + 0.2), "glow",
                 bev=0.04)
        cube(m, (d["W"] * 0.8, 0.4, 1.2), (0, d["yf"] - 0.4, d["bz"]), "charcoal", bev=0.08)
        for s in (-1, 1):
            cube(m, (0.2, 0.4, 1.6), (s * 1.3, d["yf"] - 0.5, d["bz"] + 0.2), "charcoal", bev=0.04)
    car(m, L=11.0, W=5.0, body_h=1.7, clear=2.0, col="plastic_green", cab_l=3.4, cab_h=1.7, cab_y=-1.0, r=1.6,
        extras=ex)


def _armored_truck(m):
    def ex(m, d):
        z = d["z0"] + 1.0
        cube(m, (d["W"], d["box_l"], d["box_h"]), (0, d["box_y"], z + d["box_h"] / 2), "vault", bev=0.2)
        for s in (-1, 1):
            for y in (-1.0, 2.0, 5.0):
                cube(m, (0.1, 0.9, 0.25), (s * (d["W"] / 2 + 0.02), y, z + 3.4), "black", bev=0.02)
            for k in range(6):
                cube(m, (0.1, 0.18, 0.18), (s * (d["W"] / 2 + 0.03), -2.4 + k * 1.8, z + d["box_h"] - 0.4), "stainless")
        side_text(m, "SECURE", d["W"], d["box_y"], z + 1.8, "gold", 0.2)
        cube(m, (d["W"] * 0.9, 0.2, d["box_h"] - 0.6), (0, d["box_y"] + d["box_l"] / 2 + 0.05, z + d["box_h"] / 2),
             "steel", bev=0.05)
        with m.at((0, d["box_y"] + d["box_l"] / 2 + 0.16, z + 2.8), 180):
            text(m, "$", 0, 0, 0, px=0.3, depth=0.08, col="gold")
    truck(m, cab="vault", box=None, L=13.0, box_h=4.6, extras=ex, six=False)


def _food_truck(m):
    def ex(m, d):
        z = d["z0"]
        cube(m, (0.1, 4.0, 1.6), (d["W"] / 2 + 0.02, 1.4, z + d["H"] * 0.6), "charcoal", bev=0.03)
        cube(m, (0.6, 4.0, 0.3), (d["W"] / 2 + 0.3, 1.4, z + d["H"] * 0.6 - 0.9), "stainless", bev=0.03)
        m.box((0.3, 4.6, 1.4), color=lambda c, n: "plastic_yellow" if int((c.y + 10) / 0.6) % 2 else "plastic_red",
              loc=(d["W"] / 2 + 0.7, 1.4, z + d["H"] * 0.95), rot=(0, -30, 0), cuts={"y": 0.6}, bevel=0.04)
        with m.at((0, 1.4, z + d["H"] + 1.2)):
            cube(m, (4.2, 0.5, 1.8), (0, 0, 0), "plastic_yellow", bev=0.1)
            text(m, "TACOS", 0, -0.26, 0, px=0.2, depth=0.08, col="plastic_red")
        cube(m, (0.1, 2.0, 1.4), (d["W"] / 2 + 0.03, -1.4, z + d["H"] * 0.6), "menu_black", bev=0.03)
    van(m, col="plastic_orange", L=11.0, H=4.6, stripe="plastic_yellow", extras=ex)


def _camper(m):
    def ex(m, d):
        z = d["z0"]
        for s in (-1, 1):
            for y in (0.5, 3.0, 5.5):
                cube(m, (0.08, 1.6, 1.0), (s * (d["W"] / 2 + 0.02), y, z + d["H"] * 0.68), "window_blue", bev=0.03)
        cube(m, (0.08, 1.2, 3.0), (d["W"] / 2 + 0.02, -1.4, z + 1.9), "wood_mid", bev=0.03)
        cube(m, (2.2, 1.8, 0.8), (0, 2.5, z + d["H"] + 0.4), "lightgray", bev=0.1)
        for k in range(6):
            cube(m, (0.1, 0.1, 0.8), (-d["W"] / 2 + 0.6 + k * 0.1, d["yb"] - 0.1, z + 1.0 + k * 0.5), "chrome")
        m.box((0.3, 6.0, 0.4), color=lambda c, n: "awning_green" if int((c.y + 20) / 0.8) % 2 else "white",
              loc=(-d["W"] / 2 - 0.3, 2.5, z + d["H"] * 0.95), cuts={"y": 0.8}, bevel=0.04)
    van(m, col="plastic_white", L=16.0, H=5.0, stripe="wood_mid", extras=ex, r=1.0)


def _mail_truck(m):
    def ex(m, d):
        side_text(m, "MAIL", d["W"], 1.2, d["z0"] + d["H"] * 0.55, "plastic_blue", 0.22)
        cube(m, (d["W"] + 0.04, d["L"] - 1.5, 0.3), (0, 0.9, d["z0"] + d["H"] * 0.28), "plastic_red", bev=0.03)
    van(m, col="plastic_white", L=8.0, H=4.4, stripe="plastic_blue", extras=ex, r=0.8)


def _tuk_tuk(m):
    z0 = 0.9
    cube(m, (3.6, 5.2, 1.0), (0, 0.4, z0 + 0.5), "plastic_green", bev=0.2)
    cube(m, (1.6, 1.4, 1.6), (0, -2.4, z0 + 1.2), "plastic_green", bev=0.25)
    cube(m, (3.4, 2.2, 0.8), (0, 1.6, z0 + 1.4), "leather", bev=0.15)
    cube(m, (3.4, 0.5, 1.6), (0, 2.5, z0 + 2.2), "leather", bev=0.15)
    for x in (-1.6, 1.6):
        for y in (-1.6, 2.8):
            cube(m, (0.15, 0.15, 3.2), (x, y, z0 + 2.6), "charcoal", bev=0.03)
    cube(m, (4.0, 5.4, 0.3), (0, 0.6, z0 + 4.3), "plastic_yellow", bev=0.12)
    cube(m, (3.0, 0.12, 1.4), (0, -1.65, z0 + 3.1), "window_blue", bev=0.03)
    cube(m, (2.4, 0.1, 0.12), (0, -2.1, z0 + 2.2), "charcoal")
    m.cyl(r=0.3, h=0.12, seg=8, color="glow", rot=(90, 0, 0), loc=(0, -3.15, z0 + 1.5))
    with m.group("WheelF"):
        m.cyl(r=0.75, h=0.5, seg=10, rot=(0, 90, 0), loc=(0, -2.6, 0.75), color="rubber", bevel=0.08)
    wheel(m, "WheelBL", 1.9, 2.0, 0.75, 0.5)
    wheel(m, "WheelBR", -1.9, 2.0, 0.75, 0.5)


def _hover_car(m):
    L, W = 9.6, 4.6
    z0 = 1.6
    cube(m, (W, L, 1.0), (0, 0, z0 + 0.5), "plastic_white", bev=0.35)
    m.wedge((W - 0.4, 2.8, 0.8), color="plastic_white", loc=(0, -L / 2 + 1.5, z0 + 1.4), rot=(0, 0, 180))
    cube(m, (W * 0.7, 3.4, 1.1), (0, 0.8, z0 + 1.5), "neon_blue", bev=0.45)
    cube(m, (W * 0.72, 2.4, 0.8), (0, 0.6, z0 + 1.6), "window_blue", bev=0.3)
    for s in (-1, 1):
        m.prism([(0, 0), (1.6, 0.4), (1.6, 0.9), (0, 1.2)], depth=0.15, color="plastic_white", rot=(0, 90, 0),
                loc=(s * 1.2, L / 2 - 1.4, z0 + 1.0), scale=(1, 1, 1))
        cube(m, (0.1, L - 1.0, 0.2), (s * (W / 2 + 0.02), 0, z0 + 0.6), "neon_blue", bev=0.02)
    with m.group("Hover"):
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.cyl(r=0.9, h=0.4, seg=8, color="charcoal", loc=(sx * (W / 2 - 0.9), sy * (L / 2 - 1.8), z0 - 0.1))
                m.cyl(r=0.7, h=0.1, seg=8, color="neon_blue", loc=(sx * (W / 2 - 0.9), sy * (L / 2 - 1.8), z0 - 0.35))
    for s in (-1, 1):
        cube(m, (1.0, 0.12, 0.25), (s * 1.3, -L / 2 + 0.2, z0 + 0.8), "glow", bev=0.03)
        cube(m, (1.2, 0.12, 0.25), (s * 1.3, L / 2 + 0.02, z0 + 0.8), "neon_red", bev=0.03)


def _delivery_scooter(m):
    scooter(m, "plastic_red")
    cube(m, (1.6, 1.6, 1.4), (0, 1.2, 1.4), "plastic_red", bev=0.12)
    with m.at((0, 0.38, 1.6)):
        text(m, "PIZZA", 0, 0, 0, px=0.12, depth=0.05, col="white")
    cube(m, (0.8, 2.0, 0.5), (0, 0.8, 0.8), "leather_dark", bev=0.1)


reg("RallyCar", _rally, sub="Supercars")
reg("DriftCar", _drift, sub="Supercars")
reg("DuneBuggy", _dune_buggy, sub="Offroad")
reg("Lowrider", _lowrider, sub="Classics")
reg("HotRod", _hot_rod, sub="Classics")
reg("OffroadTruck", _offroad, sub="Offroad")
reg("ArmoredTruck", _armored_truck, sub="Trucks")
reg("FoodTruck", _food_truck, sub="Trucks")
reg("CamperRV", _camper, sub="Trucks")
reg("MailTruck", _mail_truck, sub="Service")
reg("TukTuk", _tuk_tuk, sub="Bikes")
reg("HoverCar", _hover_car, sub="SciFi")
reg("DeliveryScooter", _delivery_scooter, sub="Bikes")
