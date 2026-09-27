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
