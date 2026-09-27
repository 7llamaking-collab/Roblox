"""Buildings: city, shops & market stalls, street signs, farm, landmarks, military bases.

Blocky stud style at character scale (doors ~7 studs, floors ~6 studs).
Moving bits (windmill blades, radar dish, barrier arm) are separate parts.
Buildings face -Y (front door towards -Y).
"""
import math

from studlib.registry import add

CAT = "Buildings"


def cube(m, size, loc, color, bev=None, **kw):
    b = min(size) * 0.12 if bev is None else bev
    return m.box(size, color=color, bevel=b, loc=loc, **kw)


def window(m, x, y, z, w=1.8, h=2.2, face="front", frame="plastic_white", glass="window_blue", sill=True):
    """A framed window stuck on a wall. face: front(-Y) back(+Y) left(+X) right(-X)."""
    rot = {"front": 0, "back": 180, "left": 90, "right": -90}[face]
    nx, ny = {"front": (0, -1), "back": (0, 1), "left": (1, 0), "right": (-1, 0)}[face]
    cube(m, (w + 0.3, 0.16, h + 0.3), (x + nx * 0.04, y + ny * 0.04, z), frame, bev=0.04, rot=(0, 0, rot))
    cube(m, (w, 0.2, h), (x + nx * 0.08, y + ny * 0.08, z), glass, bev=0.03, rot=(0, 0, rot))
    cube(m, (0.12, 0.24, h), (x + nx * 0.1, y + ny * 0.1, z), frame, bev=0.02, rot=(0, 0, rot))
    cube(m, (w, 0.24, 0.12), (x + nx * 0.1, y + ny * 0.1, z), frame, bev=0.02, rot=(0, 0, rot))
    if sill:
        cube(m, (w + 0.5, 0.4, 0.18), (x + nx * 0.15, y + ny * 0.15, z - h / 2 - 0.18), frame, bev=0.04,
             rot=(0, 0, rot))


def door(m, x, y, z0=0.0, w=2.6, h=4.6, col="wood_dark", frame="plastic_white", face="front", knob="gold"):
    rot = {"front": 0, "back": 180, "left": 90, "right": -90}[face]
    nx, ny = {"front": (0, -1), "back": (0, 1), "left": (1, 0), "right": (-1, 0)}[face]
    cube(m, (w + 0.4, 0.2, h + 0.2), (x + nx * 0.05, y + ny * 0.05, z0 + h / 2 + 0.1), frame, bev=0.04, rot=(0, 0, rot))
    cube(m, (w, 0.3, h), (x + nx * 0.08, y + ny * 0.08, z0 + h / 2), col, bev=0.05, rot=(0, 0, rot))
    cube(m, (w * 0.7, 0.34, h * 0.3), (x + nx * 0.09, y + ny * 0.09, z0 + h * 0.7), "window_blue", bev=0.03,
         rot=(0, 0, rot))
    cube(m, (0.22, 0.4, 0.22), (x + nx * 0.12 + (w * 0.35 if face in ("front", "back") else 0),
                                y + ny * 0.12 + (w * 0.35 if face in ("left", "right") else 0), z0 + h * 0.45), knob,
         bev=0.04)


def gable_roof(m, W, D, z, h, col="roof_red", over=0.8, trim="plastic_white", x=0.0, y=0.0):
    """Gable roof with the ridge along X."""
    m.prism([(-(D / 2 + over), 0), (D / 2 + over, 0), (0, h)], depth=W + over * 2, color=col, rot=(90, 0, 90),
            loc=(x, y, z), smooth=False)
    m.prism([(-(D / 2), 0), (D / 2, 0), (0, h * (D / 2) / (D / 2 + over))], depth=W + 0.02, color=trim,
            rot=(90, 0, 90), loc=(x, y, z - 0.01), smooth=False)


def flat_roof(m, W, D, z, col="concrete_dark", parapet="concrete"):
    cube(m, (W + 0.4, D + 0.4, 0.4), (0, 0, z + 0.2), parapet, bev=0.08)
    cube(m, (W - 0.6, D - 0.6, 0.12), (0, 0, z + 0.42), col, bev=0.03)


def awning(m, W, y, z, a="awning_red", b="awning_white", depth=2.0, tilt=20):
    m.box((W, depth, 0.2), color=lambda c, n: a if int((c.x + 50) / 0.8) % 2 else b, bevel=0.05,
          loc=(0, y - depth / 2, z), rot=(tilt, 0, 0), cuts={"x": 0.8})
    for i in range(int(W / 0.8)):
        x = -W / 2 + 0.4 + i * 0.8
        m.pyramid(w=0.8, h=0.35, color=a if int((x + 50) / 0.8) % 2 else b, loc=(x, y - depth, z - 0.25 - depth * 0.3),
                  rot=(180, 0, 0), scale=(1, 0.2, 1))


def sign_board(m, W, y, z, col="plastic_white", text="plastic_red", h=1.4):
    cube(m, (W, 0.3, h), (0, y - 0.15, z), col, bev=0.08)
    n = max(3, int(W / 0.9))
    for i in range(n):
        cube(m, (0.5, 0.1, h * 0.5), (-(n - 1) * 0.35 + i * 0.7, y - 0.33, z), text, bev=0.04)


def reg(name, fn, sub="City", split=False, tags=()):
    add(name, CAT, fn, sub=sub, split=split, tags=list(tags) + ["building"])


# ----------------------------------------------------------------------------
# homes
# ----------------------------------------------------------------------------
def house(m, W=12.0, D=10.0, H=7.0, wall="wood_pale", roof="roof_red", trim="plastic_white", floors=1):
    cube(m, (W + 0.4, D + 0.4, 0.6), (0, 0, 0.3), "stone", bev=0.1)
    cube(m, (W, D, H), (0, 0, 0.6 + H / 2), wall, bev=0.15)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(m, (0.5, 0.5, H), (sx * W / 2, sy * D / 2, 0.6 + H / 2), trim, bev=0.08)
    door(m, 0, -D / 2, 0.6, frame=trim)
    fh = H / floors
    for f in range(floors):
        z = 0.6 + fh * (f + 0.55)
        for x in (-W * 0.3, W * 0.3):
            window(m, x, -D / 2, z, frame=trim)
        if f > 0:
            window(m, 0, -D / 2, z, frame=trim)
        for face, xs in (("left", W / 2), ("right", -W / 2)):
            window(m, xs, 0, z, face=face, frame=trim)
    gable_roof(m, W, D, 0.6 + H, D * 0.45, col=roof, trim=trim)
    cube(m, (1.4, 1.4, 3.0), (W * 0.3, D * 0.2, 0.6 + H + 2.2), "brick", bev=0.08)
    cube(m, (1.7, 1.7, 0.3), (W * 0.3, D * 0.2, 0.6 + H + 3.8), "brick_dark", bev=0.05)
    cube(m, (3.6, 1.6, 0.4), (0, -D / 2 - 0.8, 0.2), "stone_light", bev=0.08)
    for x in (-W * 0.3, W * 0.3):
        cube(m, (2.2, 0.6, 0.5), (x, -D / 2 - 0.35, 0.6 + fh * 0.55 - 1.55), "wood_mid", bev=0.06)
        for k in range(3):
            cube(m, (0.4, 0.4, 0.4), (x - 0.6 + k * 0.6, -D / 2 - 0.35, 0.6 + fh * 0.55 - 1.15),
                 ["plastic_red", "plastic_yellow", "plastic_pink"][k], bev=0.06)


reg("House", lambda m: house(m), sub="Homes")
reg("BlueHouse", lambda m: house(m, wall="tile_blue", roof="roof_blue"), sub="Homes")
reg("TwoStoryHouse", lambda m: house(m, W=14, D=11, H=12, wall="sandstone", roof="roof_green", floors=2), sub="Homes")


def apartment(m, W=16.0, D=14.0, floors=4, wall="brick", trim="concrete"):
    fh = 5.5
    H = floors * fh
    cube(m, (W, D, H), (0, 0, H / 2), wall, bev=0.2)
    for f in range(floors):
        z = f * fh + fh * 0.55
        cube(m, (W + 0.2, D + 0.2, 0.3), (0, 0, f * fh), trim, bev=0.05)
        for i in range(4):
            x = -W / 2 + W * (i + 0.5) / 4
            if f == 0 and i in (1, 2):
                continue
            window(m, x, -D / 2, z, w=2.0, h=2.6, frame=trim, sill=False)
            window(m, x, D / 2, z, w=2.0, h=2.6, face="back", frame=trim, sill=False)
        for i in range(3):
            y = -D / 2 + D * (i + 0.5) / 3
            window(m, W / 2, y, z, w=2.0, h=2.6, face="left", frame=trim, sill=False)
            window(m, -W / 2, y, z, w=2.0, h=2.6, face="right", frame=trim, sill=False)
    door(m, 0, -D / 2, 0, w=3.4, h=4.4, col="window_blue", frame=trim)
    cube(m, (5.0, 2.2, 0.3), (0, -D / 2 - 1.1, 5.0), "awning_green", bev=0.05)
    flat_roof(m, W, D, H)
    for x in (-4, 3):
        cube(m, (2.0, 1.6, 1.2), (x, 2, H + 1.0), "lightgray", bev=0.1)
        m.cyl(r=0.5, h=0.1, seg=8, color="charcoal", loc=(x, 2, H + 1.62))


reg("ApartmentBuilding", lambda m: apartment(m), sub="City")


def _skyscraper(m):
    W, H = 16.0, 48.0
    cube(m, (W, W, H), (0, 0, H / 2), "window_blue", bev=0.2)
    for i in range(9):
        x = -W / 2 + i * W / 8
        for face in range(4):
            a = face * 90
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            cube(m, (0.35, 0.4, H), (c * x - s * (-W / 2 - 0.1), s * x + c * (-W / 2 - 0.1), H / 2), "concrete",
                 bev=0.05, rot=(0, 0, a))
    for z in range(0, int(H), 6):
        cube(m, (W + 0.3, W + 0.3, 0.35), (0, 0, z + 0.2), "concrete", bev=0.05)
    cube(m, (W * 0.7, W * 0.7, 6.0), (0, 0, H + 3.0), "window_blue", bev=0.15)
    cube(m, (W * 0.72, W * 0.72, 0.4), (0, 0, H + 6.2), "concrete", bev=0.06)
    cube(m, (W + 0.4, W + 0.4, 0.5), (0, 0, H + 0.25), "concrete", bev=0.08)
    m.cyl(r=0.2, h=6, seg=6, color="silver", loc=(0, 0, H + 9.4))
    m.sphere(r=0.35, color="neon_red", loc=(0, 0, H + 12.5))
    door(m, 0, -W / 2, 0, w=4.0, h=5.0, col="window_blue", frame="concrete")


reg("Skyscraper", _skyscraper, sub="City")


def shop(m, W=14.0, D=10.0, H=9.0, wall="brick", awn=("awning_red", "awning_white"), sign=("plastic_white", "plastic_red"),
         icon=None):
    cube(m, (W, D, H), (0, 0, H / 2), wall, bev=0.15)
    cube(m, (W - 1.0, 0.3, 4.4), (0, -D / 2 - 0.02, 2.6), "concrete", bev=0.05)
    for x in (-W * 0.28, W * 0.28):
        cube(m, (W * 0.34, 0.4, 3.6), (x, -D / 2 - 0.06, 2.6), "window_blue", bev=0.04)
    door(m, 0, -D / 2, 0.2, w=2.4, h=4.2, col="window_blue", frame="concrete")
    awning(m, W - 0.6, -D / 2, 5.4, *awn)
    sign_board(m, W * 0.7, -D / 2, 7.4, *sign)
    flat_roof(m, W, D, H, parapet=wall)
    if icon:
        icon(m, D, H)


def _cup(m, D, H):
    m.cyl(r=0.9, r2=1.1, h=1.8, seg=8, color="plastic_white", loc=(0, -D / 2 + 0.5, H + 1.4))
    m.torus(R=0.5, r=0.15, seg=8, color="plastic_white", rot=(90, 0, 0), loc=(1.1, -D / 2 + 0.5, H + 1.5))
    m.cyl(r=0.85, h=0.1, seg=8, color="chocolate", loc=(0, -D / 2 + 0.5, H + 2.3))


def _pizza_icon(m, D, H):
    m.prism([(-1.2, 0), (1.2, 0), (0, 2.4)], depth=0.3, color="cheese", rot=(90, 0, 180), loc=(0, -D / 2 + 0.5, H + 3.2))
    for x, z in ((-0.3, H + 2.6), (0.35, H + 2.2), (0, H + 1.6)):
        m.cyl(r=0.25, h=0.35, seg=8, color="pepperoni", rot=(90, 0, 0), loc=(x, -D / 2 + 0.5, z))


reg("Shop", lambda m: shop(m), sub="Shops")
reg("Cafe", lambda m: shop(m, wall="wood_light", awn=("awning_green", "awning_white"),
                            sign=("sign_green", "plastic_white"), icon=_cup), sub="Shops")
reg("PizzaShop", lambda m: shop(m, wall="plastic_white", awn=("awning_red", "awning_green"),
                                 sign=("plastic_red", "plastic_white"), icon=_pizza_icon), sub="Shops")
reg("ToyStore", lambda m: shop(m, wall="plastic_purple", awn=("awning_blue", "plastic_yellow"),
                                sign=("plastic_yellow", "plastic_blue")), sub="Shops")


def _gas_station(m):
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(m, (0.8, 0.8, 7.0), (sx * 6, sy * 3.5, 3.5), "concrete", bev=0.1)
    cube(m, (15.0, 9.0, 1.2), (0, 0, 7.6), "plastic_white", bev=0.2)
    cube(m, (15.1, 9.1, 0.5), (0, 0, 7.3), "fire_red", bev=0.08)
    for x in (-3, 3):
        cube(m, (3.0, 1.2, 0.4), (x, 0, 0.2), "concrete", bev=0.06)
        cube(m, (1.4, 0.9, 3.0), (x, 0, 1.9), "fire_red", bev=0.12)
        cube(m, (1.0, 0.1, 0.9), (x, -0.46, 2.6), "screen_glow", bev=0.03)
        m.tube([(x + 0.7, 0, 2.5), (x + 1.2, -0.3, 1.2), (x + 0.9, -0.5, 1.0)], [0.08, 0.08, 0.08], seg=4,
               color="charcoal")
    cube(m, (10.0, 7.0, 6.0), (0, 11.0, 3.0), "concrete", bev=0.15)
    cube(m, (7.0, 0.3, 3.0), (0, 7.4, 2.6), "window_blue", bev=0.05)
    sign_board(m, 7.0, 7.5, 5.2, "fire_red", "plastic_white")
    cube(m, (0.6, 0.6, 9.0), (-9.5, -3, 4.5), "charcoal", bev=0.06)
    cube(m, (3.0, 0.5, 3.2), (-9.5, -3, 9.6), "plastic_white", bev=0.1)
    for k in range(3):
        cube(m, (2.2, 0.1, 0.6), (-9.5, -3.28, 10.6 - k * 0.9), "black", bev=0.03)


reg("GasStation", _gas_station, sub="City")


def civic(m, W, D, H, wall, trim, band, sign_col, text_col, extras=None):
    cube(m, (W, D, H), (0, 0, H / 2), wall, bev=0.2)
    cube(m, (W + 0.2, D + 0.2, 0.8), (0, 0, H * 0.5), band, bev=0.08)
    for f in range(2):
        z = H * (0.28 + 0.44 * f)
        for i in range(4):
            x = -W / 2 + W * (i + 0.5) / 4
            if f == 0 and i in (1, 2):
                continue
            window(m, x, -D / 2, z, w=2.2, h=2.4, frame=trim, sill=False)
    door(m, 0, -D / 2, 0, w=4.0, h=4.6, col="window_blue", frame=trim)
    sign_board(m, W * 0.5, -D / 2, H * 0.5 + 1.6, sign_col, text_col, h=1.2)
    flat_roof(m, W, D, H, parapet=trim)
    if extras:
        extras(m, W, D, H)


def _police_ex(m, W, D, H):
    cube(m, (1.2, 1.2, 0.6), (0, -D / 2 + 1, H + 1.0), "charcoal", bev=0.1)
    cube(m, (0.9, 0.9, 0.6), (0, -D / 2 + 1, H + 1.5), "neon_blue", bev=0.1)
    m.prism([(0, 0.8), (0.7, 0.3), (0.5, -0.7), (-0.5, -0.7), (-0.7, 0.3)], depth=0.2, color="gold", rot=(90, 0, 0),
            loc=(W * 0.35, -D / 2 - 0.2, H * 0.72))


def _hospital_ex(m, W, D, H):
    cube(m, (3.0, 0.3, 1.0), (0, -D / 2 - 0.2, H + 2.2), "fire_red", bev=0.06)
    cube(m, (1.0, 0.3, 3.0), (0, -D / 2 - 0.2, H + 2.2), "fire_red", bev=0.06)
    cube(m, (4.0, 0.4, 4.0), (0, -D / 2 + 0.2, H + 2.2), "plastic_white", bev=0.1)
    cube(m, (7.0, 3.0, 0.4), (0, -D / 2 - 1.5, 5.2), "plastic_white", bev=0.08)


reg("PoliceStation", lambda m: civic(m, 18, 12, 11, "plastic_white", "police_blue", "police_blue", "police_blue",
                                     "plastic_white", _police_ex), sub="City")
reg("Hospital", lambda m: civic(m, 22, 14, 14, "plastic_white", "concrete", "tile_blue", "plastic_white", "fire_red",
                                _hospital_ex), sub="City")
reg("School", lambda m: civic(m, 22, 12, 11, "brick", "plastic_white", "brick_dark", "plastic_white", "sign_green",
                              lambda m, W, D, H: [m.cyl(r=1.3, h=0.3, seg=8, color="plastic_white", rot=(90, 0, 0),
                                                        loc=(0, -D / 2 - 0.2, H + 1.6)),
                                                  cube(m, (4.0, 0.5, 3.6), (0, -D / 2 + 0.2, H + 1.6), "brick"),
                                                  cube(m, (0.12, 0.12, 0.9), (0, -D / 2 - 0.4, H + 1.9), "black",
                                                       bev=0.02)]), sub="City")


def _fire_station(m):
    W, D, H = 18.0, 12.0, 10.0
    cube(m, (W, D, H), (0, 0, H / 2), "brick", bev=0.2)
    for x in (-4.5, 4.5):
        cube(m, (6.0, 0.3, 6.5), (x, -D / 2 - 0.05, 3.25), "plastic_white", bev=0.1)
        for k in range(5):
            cube(m, (5.4, 0.36, 0.9), (x, -D / 2 - 0.08, 0.7 + k * 1.2), "fire_red", bev=0.06)
    sign_board(m, 10.0, -D / 2, 8.4, "plastic_white", "fire_red", h=1.2)
    flat_roof(m, W, D, H, parapet="brick_dark")
    cube(m, (4.0, 4.0, 8.0), (W / 2 - 2.0, D / 2 - 2.0, H + 4.0), "brick", bev=0.12)
    gable_roof(m, 4.0, 4.0, H + 8.0, 2.0, col="roof_red", over=0.4, x=W / 2 - 2.0, y=D / 2 - 2.0)


reg("FireStation", _fire_station, sub="City")


def _bank(m):
    W, D, H = 18.0, 12.0, 10.0
    cube(m, (W, D, H), (0, 0, H / 2 + 1.2), "marble", bev=0.15)
    for k in range(3):
        cube(m, (W + 2.0 - k * 0.6, D + 3.0 - k * 1.0, 0.4), (0, -0.8 + k * 0.4, 0.2 + k * 0.4), "marble_dark", bev=0.06)
    for i in range(6):
        x = -W / 2 + 1.2 + i * (W - 2.4) / 5
        m.cyl(r=0.6, h=H, seg=8, color="marble", loc=(x, -D / 2 - 1.5, H / 2 + 1.2))
        cube(m, (1.6, 1.6, 0.4), (x, -D / 2 - 1.5, H + 1.0), "marble_dark", bev=0.06)
    cube(m, (W + 1.0, 4.0, 0.8), (0, -D / 2 - 1.0, H + 1.6), "marble", bev=0.1)
    m.prism([(-(W / 2 + 0.5), 0), (W / 2 + 0.5, 0), (0, 3.0)], depth=4.0, color="marble", rot=(90, 0, 0),
            loc=(0, -D / 2 - 1.0, H + 2.0))
    cube(m, (5.0, 0.2, 1.0), (0, -D / 2 - 3.05, H + 2.8), "gold", bev=0.05)
    door(m, 0, -D / 2, 1.2, w=3.4, h=5.0, col="gold_dark", frame="marble_dark")


reg("Bank", _bank, sub="City")


# ----------------------------------------------------------------------------
# market stalls & stands
# ----------------------------------------------------------------------------
def stall(m, W=6.0, D=3.0, awn=("awning_red", "awning_white"), goods=None, counter="wood", roof_h=5.0):
    cube(m, (W, D, 2.6), (0, 0, 1.3), counter, bev=0.12)
    cube(m, (W + 0.4, D + 0.4, 0.3), (0, 0, 2.75), "wood_dark", bev=0.06)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(m, (0.3, 0.3, roof_h), (sx * (W / 2 - 0.1), sy * (D / 2 - 0.1), roof_h / 2), "wood_dark", bev=0.05)
    m.box((W + 1.2, D + 2.0, 0.3), color=lambda c, n: awn[0] if int((c.x + 50) / 1.0) % 2 else awn[1],
          loc=(0, -0.4, roof_h + 0.2), rot=(12, 0, 0), cuts={"x": 1.0}, bevel=0.05)
    for i in range(int(W + 1.2)):
        x = -(W + 1.2) / 2 + 0.5 + i
        m.pyramid(w=1.0, h=0.4, color=awn[0] if int((x + 50) / 1.0) % 2 else awn[1],
                  loc=(x, -D / 2 - 1.35, roof_h - 0.15), rot=(180, 0, 0), scale=(1, 0.2, 1))
    for i in range(3):
        cube(m, (0.2, 0.1, 0.6), (-1.0 + i, -D / 2 - 0.05, 1.8), "plastic_white", bev=0.03)
    if goods:
        goods(m, W, D)


def crates_of(m, cols, W, D, z=2.9):
    n = len(cols)
    for i, c in enumerate(cols):
        x = -W / 2 + W * (i + 0.5) / n
        cube(m, (W / n - 0.3, D * 0.7, 0.6), (x, 0.1, z + 0.3), "wood_light", bev=0.06)
        for k in range(4):
            cube(m, (0.4, 0.4, 0.4), (x - 0.35 + (k % 2) * 0.7, -0.2 + (k // 2) * 0.6, z + 0.75), c, bev=0.08)


reg("MarketStall", lambda m: stall(m, goods=lambda m, W, D: crates_of(m, ["plastic_red", "orange", "banana", "lime"],
                                                                         W, D)), sub="Stalls")
reg("FruitStall", lambda m: stall(m, awn=("awning_green", "awning_white"),
                                  goods=lambda m, W, D: crates_of(m, ["apple_red", "orange", "grape", "watermelon",
                                                                      "lemon"], W, D)), sub="Stalls")
reg("FishStall", lambda m: stall(m, awn=("awning_blue", "awning_white"),
                                 goods=lambda m, W, D: [cube(m, (W - 0.4, D * 0.7, 0.3), (0, 0.1, 3.05), "ice", bev=0.05),
                                                        [cube(m, (0.4, 1.0, 0.3), (-2.2 + i * 0.9, 0.1, 3.3),
                                                              ["fish_orange", "dolphin", "sapphire"][i % 3], bev=0.08)
                                                         for i in range(6)]]), sub="Stalls")


def _hotdog_stand(m):
    cube(m, (5.0, 2.6, 2.4), (0, 0, 1.6), "plastic_red", bev=0.2)
    cube(m, (5.2, 2.8, 0.2), (0, 0, 2.9), "silver", bev=0.05)
    for s in (-1, 1):
        m.cyl(r=0.6, h=0.3, seg=8, color="rubber", rot=(0, 90, 0), loc=(s * 1.8, 1.4, 0.6))
    m.cyl(r=0.1, h=4.0, seg=6, color="silver", loc=(0, 0, 4.6))
    m.lathe([(0, 6.6), (3.2, 5.8), (3.2, 5.6), (0, 6.3)], seg=8,
            color=lambda c, n: "awning_red" if int((math.degrees(math.atan2(c.y, c.x)) + 382.5) / 45) % 2 else "plastic_yellow")
    for x in (-1.2, 0.0, 1.2):
        cube(m, (0.8, 0.35, 0.3), (x, -0.4, 3.15), "bread", bev=0.08)
        cube(m, (0.9, 0.2, 0.2), (x, -0.4, 3.3), "meat_light", bev=0.06)
    sign_board(m, 3.0, -1.3, 1.6, "plastic_yellow", "plastic_red", h=0.9)


reg("HotDogStand", _hotdog_stand, sub="Stalls")


def _lemonade(m):
    cube(m, (4.0, 2.0, 2.4), (0, 0, 1.2), "wood_light", bev=0.1)
    cube(m, (4.3, 2.3, 0.25), (0, 0, 2.5), "wood", bev=0.05)
    for s in (-1, 1):
        cube(m, (0.25, 0.25, 4.2), (s * 1.9, 0.9, 2.1), "wood", bev=0.04)
    cube(m, (4.2, 0.3, 1.2), (0, 0.9, 4.0), "plastic_yellow", bev=0.1)
    for i in range(5):
        cube(m, (0.4, 0.1, 0.6), (-1.2 + i * 0.6, 0.72, 4.0), "leaf_dark", bev=0.03)
    m.lathe([(0, 0), (0.4, 0), (0.45, 0.9), (0.3, 1.0), (0, 1.0)], seg=8,
            color=lambda c, n: "lemon" if c.z < 3.3 else "glass", loc=(-0.8, 0, 2.62), cuts={"z": [3.3]})
    for x in (0.2, 0.8, 1.4):
        m.cyl(r=0.2, h=0.5, seg=6, color="lemon", loc=(x, -0.2, 2.9))
    for i in range(3):
        cube(m, (0.5, 0.1, 0.5), (-1.2 + i * 1.2, -1.02, 1.5), "plastic_yellow", bev=0.05)


reg("LemonadeStand", _lemonade, sub="Stalls")


def _ticket_booth(m):
    cube(m, (4.0, 4.0, 5.0), (0, 0, 2.5), "plastic_red", bev=0.2)
    cube(m, (3.0, 0.3, 1.8), (0, -2.05, 3.0), "window_blue", bev=0.05)
    cube(m, (3.2, 0.8, 0.2), (0, -2.3, 2.0), "wood", bev=0.05)
    m.pyramid(w=5.0, h=2.2, color="plastic_yellow", loc=(0, 0, 5.0))
    m.sphere(r=0.35, color="plastic_red", loc=(0, 0, 7.4))
    sign_board(m, 3.4, -2.0, 4.4, "plastic_yellow", "plastic_red", h=0.8)


reg("TicketBooth", _ticket_booth, sub="Stalls")


def _kiosk(m):
    m.cyl(r=2.2, h=4.4, seg=8, color="sign_green", loc=(0, 0, 2.2), bevel=0.1)
    for a in range(0, 360, 45):
        r = math.radians(a + 22.5)
        cube(m, (1.2, 0.1, 1.6), (math.cos(r) * 2.18, math.sin(r) * 2.18, 2.6),
             ["plastic_red", "plastic_blue", "paper", "plastic_yellow"][(a // 45) % 4], bev=0.03,
             rot=(0, 0, a + 22.5 + 90))
    m.cone(r=2.8, h=1.6, seg=8, color="sign_green", loc=(0, 0, 4.4))
    m.sphere(r=0.3, color="gold", loc=(0, 0, 6.1))


reg("NewsKiosk", _kiosk, sub="Stalls")


# ----------------------------------------------------------------------------
# street signs & furniture
# ----------------------------------------------------------------------------
def _stop_sign(m):
    m.cyl(r=0.12, h=7.0, seg=6, color="silver", loc=(0, 0, 3.5))
    m.cyl(r=1.3, h=0.15, seg=8, color="fire_red", rot=(90, 22.5, 0), loc=(0, -0.15, 6.2))
    m.cyl(r=1.15, h=0.17, seg=8, color="white", rot=(90, 22.5, 0), loc=(0, -0.14, 6.2))
    m.cyl(r=1.05, h=0.2, seg=8, color="fire_red", rot=(90, 22.5, 0), loc=(0, -0.13, 6.2))
    for i in range(4):
        cube(m, (0.3, 0.06, 0.6), (-0.6 + i * 0.4, -0.26, 6.2), "white", bev=0.03)


reg("StopSign", _stop_sign, sub="Signs")


def _street_sign(m):
    m.cyl(r=0.12, h=8.0, seg=6, color="silver", loc=(0, 0, 4.0))
    cube(m, (3.4, 0.12, 0.8), (1.4, 0, 7.4), "sign_green", bev=0.05)
    cube(m, (0.12, 3.4, 0.8), (0, 1.4, 6.5), "sign_green", bev=0.05)
    for i in range(4):
        cube(m, (0.4, 0.16, 0.4), (0.4 + i * 0.6, 0, 7.4), "white", bev=0.03)
        cube(m, (0.16, 0.4, 0.4), (0, 0.4 + i * 0.6, 6.5), "white", bev=0.03)


reg("StreetSign", _street_sign, sub="Signs")


def _traffic_light(m):
    m.cyl(r=0.2, h=9.0, seg=6, color="charcoal", loc=(0, 0, 4.5))
    cube(m, (0.3, 4.2, 0.3), (0, -2.0, 8.8), "charcoal", bev=0.05)
    cube(m, (1.2, 1.0, 3.2), (0, -4.0, 7.2), "plastic_yellow", bev=0.12)
    for k, c in enumerate(("neon_red", "plastic_orange", "neon_green")):
        cube(m, (0.7, 0.2, 0.7), (0, -4.52, 8.2 - k * 1.0), c, bev=0.08)
        cube(m, (0.9, 0.5, 0.12), (0, -4.7, 8.6 - k * 1.0), "charcoal", bev=0.02)
    cube(m, (1.4, 1.4, 0.4), (0, 0, 0.2), "concrete", bev=0.08)


reg("TrafficLight", _traffic_light, sub="Signs")


def _billboard(m):
    for x in (-4, 4):
        cube(m, (0.6, 0.6, 8.0), (x, 0.5, 4.0), "charcoal", bev=0.06)
    cube(m, (14.0, 0.6, 6.0), (0, 0.0, 10.0), "plastic_white", bev=0.15)
    cube(m, (13.0, 0.2, 5.0), (0, -0.35, 10.0), "tile_blue", bev=0.05)
    m.sphere(round=True, r=1.3, color="plastic_yellow", loc=(-4.0, -0.5, 10.8), scale=(1, 0.2, 1))
    for i in range(3):
        cube(m, (5.0 - i, 0.25, 0.6), (1.5, -0.5, 11.6 - i * 1.2), "plastic_white", bev=0.05)
    cube(m, (14.0, 1.4, 0.2), (0, -0.8, 6.9), "charcoal", bev=0.04)
    for x in (-5, 0, 5):
        m.tube([(x, -0.2, 13.0), (x, -1.4, 13.3)], [0.08, 0.08], seg=4, color="charcoal")
        cube(m, (0.6, 0.4, 0.3), (x, -1.5, 13.2), "glow", bev=0.05)


reg("Billboard", _billboard, sub="Signs")


def _hanging_sign(m):
    cube(m, (0.3, 0.3, 0.3), (0, 0.15, 6.0), "charcoal", bev=0.05)
    m.tube([(0, 0, 6.0), (0, -2.6, 6.0)], [0.1, 0.1], seg=4, color="charcoal")
    m.tube([(0, 0, 5.2), (0, -1.2, 6.0)], [0.07, 0.07], seg=4, color="charcoal")
    for y in (-0.6, -2.2):
        m.tube([(0, y, 5.95), (0, y, 5.4)], [0.03, 0.03], seg=4, color="charcoal")
    cube(m, (0.3, 2.2, 1.6), (0, -1.4, 4.6), "wood", bev=0.1)
    m.lathe([(0, 0), (0.35, 0.05), (0.45, 0.6), (0.2, 0.9), (0, 0.9)], seg=8, color="plastic_yellow",
            rot=(0, 90, 0), loc=(-0.18, -1.4, 4.6), scale=(1, 1, 1))


reg("HangingSign", _hanging_sign, sub="Signs")


def _bus_stop(m):
    cube(m, (7.0, 3.0, 0.3), (0, 0, 0.15), "concrete", bev=0.05)
    for x in (-3.2, 3.2):
        cube(m, (0.25, 0.25, 5.0), (x, 1.2, 2.8), "silver", bev=0.04)
    cube(m, (6.8, 0.15, 3.8), (0, 1.3, 2.6), "window_blue", bev=0.04)
    cube(m, (7.4, 3.2, 0.3), (0, 0.2, 5.35), "sign_green", bev=0.06)
    cube(m, (4.0, 1.0, 0.25), (0, 0.6, 1.9), "wood", bev=0.05)
    for x in (-1.6, 1.6):
        cube(m, (0.2, 0.8, 1.7), (x, 0.6, 1.0), "charcoal", bev=0.04)
    m.cyl(r=0.1, h=6.0, seg=6, color="silver", loc=(3.9, -1.0, 3.0))
    m.cyl(r=0.7, h=0.12, seg=8, color="sign_green", rot=(90, 0, 0), loc=(3.9, -1.08, 5.6))


reg("BusStop", _bus_stop, sub="Signs")


def _neon_sign(m):
    cube(m, (6.0, 0.4, 3.0), (0, 0, 1.5), "black", bev=0.1)
    m.torus(R=0.8, r=0.1, seg=8, color="neon_pink", rot=(90, 0, 0), loc=(-1.6, -0.3, 1.6))
    m.prism([(0, 0.8), (0.7, 0.2), (0.45, -0.7), (-0.45, -0.7), (-0.7, 0.2)], depth=0.1, color="neon_blue",
            rot=(90, 0, 0), loc=(0.4, -0.3, 1.6))
    m.tube([(1.5, -0.3, 0.8), (1.8, -0.3, 2.3), (2.2, -0.3, 0.9), (2.5, -0.3, 2.4)], [0.08] * 4, seg=4,
           color="neon_green")


reg("NeonSign", _neon_sign, sub="Signs")


def _road_barrier(m):
    for x in (-2.2, 2.2):
        cube(m, (0.3, 1.2, 0.2), (x, 0, 0.1), "charcoal", bev=0.04)
        cube(m, (0.2, 0.2, 2.2), (x, 0, 1.1), "charcoal", bev=0.04)
    m.box((5.0, 0.2, 0.6), color=lambda c, n: "plastic_orange" if int((c.x + 50) / 0.6) % 2 else "white",
          loc=(0, 0, 1.8), cuts={"x": 0.6}, bevel=0.05)
    m.box((5.0, 0.2, 0.6), color=lambda c, n: "plastic_orange" if int((c.x + 50.3) / 0.6) % 2 else "white",
          loc=(0, 0, 1.0), cuts={"x": 0.6}, bevel=0.05)
    cube(m, (0.4, 0.3, 0.4), (-2.2, 0, 2.4), "neon_red", bev=0.08)


reg("RoadBarrier", _road_barrier, sub="Signs")


# ----------------------------------------------------------------------------
# farm & landmarks
# ----------------------------------------------------------------------------
def _barn(m):
    W, D, H = 14.0, 18.0, 8.0
    cube(m, (W, D, H), (0, 0, H / 2), "plank_red", bev=0.15)
    pts = [(-W / 2 - 0.5, 0), (W / 2 + 0.5, 0), (W / 2 - 1.0, 3.4), (0, 5.8), (-W / 2 + 1.0, 3.4)]
    m.prism(pts, depth=D + 1.2, color="charcoal", rot=(90, 0, 0), loc=(0, D / 2 + 0.6, H), smooth=False)
    m.prism([(x * 0.93, y * 0.93) for x, y in pts], depth=D + 0.1, color="plank_red", rot=(90, 0, 0),
            loc=(0, D / 2 + 0.05, H - 0.02), smooth=False)
    cube(m, (6.0, 0.3, 6.0), (0, -D / 2 - 0.1, 3.0), "plank_red", bev=0.06)
    for a in (45, -45):
        cube(m, (0.4, 0.36, 8.0), (0, -D / 2 - 0.2, 3.0), "plastic_white", bev=0.04, rot=(0, a, 0))
    for x in (-3, 0, 3):
        cube(m, (0.4, 0.36, 6.2), (x, -D / 2 - 0.2, 3.0), "plastic_white", bev=0.04)
    for z in (0.1, 6.0):
        cube(m, (6.4, 0.36, 0.4), (0, -D / 2 - 0.2, z), "plastic_white", bev=0.04)
    window(m, 0, -D / 2, H + 2.4, w=2.0, h=2.0, frame="plastic_white", sill=False)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(m, (0.4, 0.4, H), (sx * W / 2, sy * D / 2, H / 2), "plastic_white", bev=0.06)


reg("Barn", _barn, sub="Farm")


def _silo(m):
    m.cyl(r=3.0, h=16.0, seg=8, color=lambda c, n: "concrete" if int(c.z / 2.0) % 2 else "concrete_dark",
          loc=(0, 0, 8.0), cuts={"z": 2.0})
    m.lathe([(3.2, 16.0), (2.8, 17.6), (1.6, 18.8), (0, 19.2)], seg=8, color="silver")
    for z in range(1, 16, 2):
        cube(m, (0.8, 0.12, 0.12), (0, -3.05, z), "iron_dark", bev=0.02)
    for s in (-1, 1):
        cube(m, (0.12, 0.2, 16.0), (s * 0.4, -3.05, 8.0), "iron_dark", bev=0.02)


reg("Silo", _silo, sub="Farm")


def _windmill(m):
    m.cyl(r=3.2, r2=2.2, h=12.0, seg=8, color="wood_pale", loc=(0, 0, 6.0))
    m.cone(r=3.0, h=3.4, seg=8, color="roof_red", loc=(0, 0, 12.0))
    door(m, 0, -3.1, 0, w=2.2, h=3.6)
    window(m, 0, -2.6, 8.0, w=1.2, h=1.6, sill=False)
    m.cyl(r=0.5, h=1.6, seg=8, color="wood_dark", rot=(90, 0, 0), loc=(0, -2.9, 11.2))
    with m.group("Blades"):
        m.cyl(r=0.7, h=0.6, seg=8, color="wood_dark", rot=(90, 0, 0), loc=(0, -3.8, 11.2))
        for a in (0, 90, 180, 270):
            r = math.radians(a)
            c, s = math.cos(r), math.sin(r)
            cube(m, (0.35, 0.2, 7.0), (c * 3.8, -3.9, 11.2 + s * 3.8), "wood", rot=(0, -a + 90, 0), bev=0.05)
            cube(m, (1.8, 0.1, 5.4), (c * 4.1 - s * 0.9, -3.95, 11.2 + s * 4.1 + c * 0.9), "wood_pale",
                 rot=(0, -a + 90, 0), bev=0.03)


reg("Windmill", _windmill, sub="Farm", split=True)


def _lighthouse(m):
    m.cyl(r=3.0, r2=2.2, h=16.0, seg=8, color=lambda c, n: "fire_red" if int(c.z / 3.2) % 2 else "plastic_white",
          loc=(0, 0, 8.0), cuts={"z": 3.2})
    m.cyl(r=3.2, h=0.6, seg=8, color="charcoal", loc=(0, 0, 16.3))
    m.cyl(r=1.8, h=2.6, seg=8, color="glow", loc=(0, 0, 17.9))
    for a in range(0, 360, 45):
        r = math.radians(a)
        cube(m, (0.15, 0.15, 2.6), (math.cos(r) * 1.85, math.sin(r) * 1.85, 17.9), "charcoal", bev=0.03)
    m.cone(r=2.3, h=1.8, seg=8, color="fire_red", loc=(0, 0, 19.2))
    door(m, 0, -2.95, 0, w=2.0, h=3.4, col="fire_red")
    cube(m, (8.0, 8.0, 0.6), (0, 0, 0.3), "stone", bev=0.1)


reg("Lighthouse", _lighthouse, sub="Landmarks")


def crenel(m, W, D, z, col):
    step = 1.2
    for sx in (-1, 1):
        for i in range(int(D / step)):
            y = -D / 2 + step / 2 + i * step
            if i % 2 == 0:
                cube(m, (0.9, 0.9, 1.0), (sx * (W / 2 - 0.45), y, z + 0.5), col, bev=0.06)
    for sy in (-1, 1):
        for i in range(int(W / step)):
            x = -W / 2 + step / 2 + i * step
            if i % 2 == 0:
                cube(m, (0.9, 0.9, 1.0), (x, sy * (D / 2 - 0.45), z + 0.5), col, bev=0.06)


def _castle_tower(m):
    m.cyl(r=4.0, h=16.0, seg=8, color="stone", loc=(0, 0, 8.0), cuts={"z": 1.6})
    m.cyl(r=4.6, h=1.4, seg=8, color="stone_dark", loc=(0, 0, 16.7))
    for a in range(0, 360, 45):
        r = math.radians(a + 22.5)
        cube(m, (1.4, 1.0, 1.2), (math.cos(r) * 4.2, math.sin(r) * 4.2, 18.0), "stone_dark", bev=0.08,
             rot=(0, 0, a + 22.5))
    for z in (6.0, 11.0):
        cube(m, (0.8, 0.5, 1.8), (0, -3.95, z), "black", bev=0.06)
    door(m, 0, -3.9, 0, w=2.6, h=4.2, col="wood_dark", frame="stone_dark")
    m.cyl(r=0.12, h=4.0, seg=6, color="wood_dark", loc=(0, 0, 19.5))
    m.box((2.0, 0.08, 1.2), color="fire_red", loc=(1.0, 0, 20.8), bevel=0.02)


reg("CastleTower", _castle_tower, sub="Landmarks")


def _castle_gate(m):
    W, D, H = 18.0, 4.0, 11.0
    cube(m, (W, D, H), (0, 0, H / 2), "stone", bev=0.15, cuts={"z": 1.8})
    cube(m, (5.0, D + 0.4, 7.0), (0, 0, 3.5), "black", bev=0.05)
    m.cyl(r=2.5, h=D + 0.4, seg=8, color="black", rot=(90, 0, 0), loc=(0, 0, 7.0))
    for i in range(5):
        cube(m, (0.2, 0.3, 8.8), (-2.0 + i, -D / 2 - 0.2, 4.4), "iron_dark", bev=0.03)
    for k in range(6):
        cube(m, (5.0, 0.3, 0.2), (0, -D / 2 - 0.2, 1.0 + k * 1.4), "iron_dark", bev=0.03)
    crenel(m, W, D, H, "stone_dark")
    for x in (-W / 2, W / 2):
        cube(m, (5.0, 6.0, 14.0), (x, 0, 7.0), "stone_dark", bev=0.12)
        crenel(m, 5.0, 6.0, 14.0, "stone")


reg("CastleGate", _castle_gate, sub="Landmarks")


def _fountain(m):
    m.cyl(r=5.0, h=1.2, seg=8, color="stone_light", loc=(0, 0, 0.6), bevel=0.1)
    m.torus(R=4.7, r=0.35, seg=8, color="stone", loc=(0, 0, 1.3))
    m.cyl(r=4.5, h=0.2, seg=8, color="water", loc=(0, 0, 1.28))
    m.cyl(r=0.8, h=3.0, seg=8, color="stone_light", loc=(0, 0, 2.5))
    m.cyl(r=2.4, r2=2.8, h=0.6, seg=8, color="stone_light", loc=(0, 0, 4.1))
    m.cyl(r=2.2, h=0.15, seg=8, color="water", loc=(0, 0, 4.4))
    m.cyl(r=0.4, h=1.6, seg=8, color="stone_light", loc=(0, 0, 5.2))
    m.cone(r=0.9, h=1.2, seg=8, color="water", loc=(0, 0, 6.0))
    for a in range(0, 360, 60):
        r = math.radians(a)
        m.tube([(math.cos(r) * 2.4, math.sin(r) * 2.4, 4.3), (math.cos(r) * 3.4, math.sin(r) * 3.4, 2.4),
                (math.cos(r) * 3.6, math.sin(r) * 3.6, 1.2)], [0.12, 0.1, 0.08], seg=4, color="water")


reg("Fountain", _fountain, sub="Landmarks")


# ----------------------------------------------------------------------------
# military bases
# ----------------------------------------------------------------------------
def _bunker(m):
    cube(m, (12.0, 9.0, 4.5), (0, 0, 2.25), "concrete", bev=0.8)
    cube(m, (8.0, 0.6, 0.6), (0, -4.5, 3.0), "black", bev=0.1)
    cube(m, (3.0, 0.3, 3.2), (4.0, -4.4, 1.6), "gunmetal", bev=0.08)
    for x in range(-5, 6, 2):
        cube(m, (1.6, 1.0, 0.7), (x * 1.0, -5.2, 0.35), "army_tan", bev=0.25)
        cube(m, (1.6, 1.0, 0.7), (x * 1.0 + 0.8, -5.2, 1.0), "army_tan", bev=0.25)
    m.cyl(r=0.15, h=1.4, seg=6, color="gunmetal", rot=(90, 0, 0), loc=(-1.0, -5.0, 3.0))


reg("Bunker", _bunker, sub="Military")


def _barracks(m):
    m.cyl(r=5.0, h=16.0, seg=8, color="army_green", rot=(90, 0, 0), loc=(0, 0, 0),
          deform=lambda co: co.__class__((co.x, max(co.y, 0.0), co.z)))
    for y in (-8.0, 8.0):
        cube(m, (10.2, 0.4, 0.6), (0, y, 0.3), "army_dark", bev=0.06)
    door(m, 0, -8.0, 0, w=2.6, h=4.0, col="army_dark", frame="army_tan")
    for s in (-1, 1):
        window(m, s * 3.0, -8.0, 2.4, w=1.4, h=1.4, frame="army_tan", sill=False)
        for y in (-4.0, 0.0, 4.0):
            window(m, s * 4.4, y, 2.4, w=1.4, h=1.2, face="left" if s > 0 else "right", frame="army_tan", sill=False)
    cube(m, (4.0, 0.2, 1.0), (0, -8.2, 4.6), "army_tan", bev=0.04)


reg("Barracks", _barracks, sub="Military")


def _watch_tower(m):
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.tube([(sx * 2.0, sy * 2.0, 0), (sx * 1.5, sy * 1.5, 10.0)], [0.25, 0.22], seg=4, color="wood_dark")
    for z in (3.0, 6.5):
        for a in (0, 90):
            cube(m, (3.6 if z > 5 else 4.0, 0.2, 0.2), (0, 0, z), "wood", bev=0.04, rot=(0, 0, a),
                 deform=lambda co: co.__class__((co.x, co.y + 1.8, co.z)))
    cube(m, (4.4, 4.4, 0.3), (0, 0, 10.0), "wood", bev=0.06)
    for sx in (-1, 1):
        cube(m, (0.2, 4.4, 1.2), (sx * 2.1, 0, 10.8), "wood", bev=0.04)
        cube(m, (4.4, 0.2, 1.2), (0, sx * 2.1, 10.8), "wood", bev=0.04)
        cube(m, (0.2, 0.2, 2.4), (sx * 2.1, 2.1, 12.4), "wood_dark", bev=0.03)
        cube(m, (0.2, 0.2, 2.4), (sx * 2.1, -2.1, 12.4), "wood_dark", bev=0.03)
    m.pyramid(w=5.4, h=2.0, color="army_green", loc=(0, 0, 13.6))
    for z in range(1, 10):
        cube(m, (1.0, 0.12, 0.12), (0, -1.9 + z * 0.02, z), "wood_light", bev=0.02)
    for s in (-1, 1):
        cube(m, (0.12, 0.12, 10.0), (s * 0.5, -1.8, 5.0), "wood_light", bev=0.02)
    cube(m, (0.8, 0.8, 0.6), (1.4, -1.6, 11.6), "gunmetal", bev=0.08)
    m.cyl(r=0.35, h=0.3, seg=8, color="glow", rot=(90, 0, 0), loc=(1.4, -2.05, 11.6))


reg("WatchTower", _watch_tower, sub="Military")


def _hangar(m):
    m.cyl(r=9.0, h=20.0, seg=8, color="gunmetal", rot=(90, 0, 0), loc=(0, 0, 0),
          deform=lambda co: co.__class__((co.x, max(co.y, 0.0), co.z)))
    cube(m, (12.0, 0.3, 7.0), (0, -10.1, 3.5), "army_dark", bev=0.08)
    for x in (-3.0, 0.0, 3.0):
        cube(m, (0.1, 0.4, 7.0), (x, -10.2, 3.5), "gunmetal", bev=0.02)
    cube(m, (22.0, 26.0, 0.2), (0, -3.0, 0.1), "asphalt", bev=0.04)
    for y in range(-14, 10, 4):
        cube(m, (0.6, 2.0, 0.05), (0, y, 0.22), "road_yellow", bev=0.01)


reg("Hangar", _hangar, sub="Military")


def _helipad(m):
    cube(m, (14.0, 14.0, 0.5), (0, 0, 0.25), "asphalt", bev=0.1)
    m.cyl(r=6.0, h=0.08, seg=8, color="road_yellow", loc=(0, 0, 0.52))
    m.cyl(r=5.4, h=0.1, seg=8, color="asphalt", loc=(0, 0, 0.53))
    for x in (-1.5, 1.5):
        cube(m, (0.8, 5.0, 0.08), (x, 0, 0.58), "white", bev=0.02)
    cube(m, (2.2, 0.8, 0.08), (0, 0, 0.58), "white", bev=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(m, (0.5, 0.5, 0.5), (sx * 6.6, sy * 6.6, 0.6), "neon_green", bev=0.1)


reg("Helipad", _helipad, sub="Military")


def _radar(m):
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.tube([(sx * 2.0, sy * 2.0, 0), (sx * 0.6, sy * 0.6, 8.0)], [0.2, 0.15], seg=4, color="gunmetal")
    cube(m, (2.2, 2.2, 1.8), (0, 0, 8.6), "army_green", bev=0.15)
    with m.group("Dish"):
        m.cyl(r=0.3, h=1.4, seg=6, color="gunmetal", loc=(0, 0, 10.0))
        m.lathe([(0, 0), (1.6, 0.4), (3.2, 1.4), (3.0, 1.5), (1.5, 0.55), (0, 0.15)], seg=8, color="lightgray",
                rot=(-70, 0, 0), loc=(0, -0.3, 11.2))
        m.cyl(r=0.08, h=2.0, seg=6, color="gunmetal", rot=(-70, 0, 0), loc=(0, -1.2, 11.5))


reg("RadarTower", _radar, sub="Military", split=True)


def _guard_post(m):
    cube(m, (3.4, 3.4, 4.6), (0, 0, 2.3), "army_tan", bev=0.15)
    cube(m, (2.4, 0.3, 1.4), (0, -1.75, 3.0), "window_blue", bev=0.05)
    cube(m, (0.3, 2.4, 1.4), (1.75, 0, 3.0), "window_blue", bev=0.05)
    cube(m, (4.0, 4.0, 0.4), (0, 0, 4.8), "army_dark", bev=0.08)
    door(m, -1.75, 0, 0, w=1.6, h=3.6, col="army_dark", frame="army_green", face="right")
    cube(m, (0.8, 0.8, 1.2), (2.8, -2.4, 0.6), "plastic_red", bev=0.1)
    with m.group("BarrierArm"):
        m.box((8.0, 0.25, 0.3), color=lambda c, n: "fire_red" if int((c.x + 50) / 0.8) % 2 else "white",
              loc=(6.8, -2.4, 1.3), cuts={"x": 0.8}, bevel=0.05)


reg("GuardPost", _guard_post, sub="Military", split=True)


def _command_tent(m):
    m.prism([(-4.0, 0), (4.0, 0), (3.0, 2.8), (0, 4.0), (-3.0, 2.8)], depth=8.0, color="army_green", rot=(90, 0, 0),
            loc=(0, 4.0, 0), smooth=False)
    m.prism([(-1.6, 0), (1.6, 0), (0, 3.0)], depth=0.1, color="army_dark", rot=(90, 0, 0), loc=(0, -4.02, 0),
            smooth=False)
    m.cyl(r=0.1, h=6.0, seg=6, color="wood_dark", loc=(4.8, -4.4, 3.0))
    m.box((2.0, 0.06, 1.2), color="army_tan", loc=(5.8, -4.4, 5.4), bevel=0.02)
    for x in (-1.5, 1.5):
        cube(m, (1.2, 1.0, 0.8), (x + 3.6, -5.2, 0.4), "army_dark", bev=0.1)


reg("CommandTent", _command_tent, sub="Military")


# ============================================================================
# batch 2: more shops, fun park, landmarks, street props, colour variants
# ============================================================================
for _n, _w, _r in (("GreenHouse", "leaf_light", "roof_green"), ("PinkHouse", "frosting_pink", "roof_red"),
                   ("PurpleHouse", "amethyst", "roof_blue"), ("BrickHouse", "brick", "stone_dark"),
                   ("WhiteHouse", "plastic_white", "roof_blue"), ("YellowHouse", "plastic_yellow", "roof_red")):
    reg(_n, (lambda m, w=_w, r=_r: house(m, wall=w, roof=r)), sub="Homes", tags=["color-variant"])
for _n, _w, _r in (("BlueTwoStoryHouse", "tile_blue", "roof_blue"), ("RedTwoStoryHouse", "brick", "stone_dark")):
    reg(_n, (lambda m, w=_w, r=_r: house(m, W=14, D=11, H=12, wall=w, roof=r, floors=2)), sub="Homes",
        tags=["color-variant"])
reg("WhiteApartment", lambda m: apartment(m, wall="plastic_white", trim="tile_blue"), sub="City")
reg("TallApartment", lambda m: apartment(m, wall="sandstone", trim="plastic_white", floors=6), sub="City")


def _bread_icon(m, D, H):
    m.box((2.4, 1.2, 1.0), color="bread", bevel=0.35, loc=(0, -D / 2 + 0.8, H + 1.0))
    for x in (-0.6, 0, 0.6):
        cube(m, (0.12, 0.8, 0.1), (x, -D / 2 + 0.8, H + 1.52), "bread_crust", bev=0.03, rot=(0, 0, 25))


def _candy_icon(m, D, H):
    m.cyl(r=0.1, h=1.6, seg=6, color="white", loc=(0, -D / 2 + 0.5, H + 1.0))
    m.cyl(r=1.0, h=0.3, seg=8, color="candy_pink", rot=(90, 0, 0), loc=(0, -D / 2 + 0.5, H + 2.4))
    m.cyl(r=0.6, h=0.34, seg=8, color="white", rot=(90, 0, 0), loc=(0, -D / 2 + 0.5, H + 2.4))
    m.cyl(r=0.3, h=0.38, seg=8, color="candy_blue", rot=(90, 0, 0), loc=(0, -D / 2 + 0.5, H + 2.4))


def _paw_icon(m, D, H):
    cube(m, (1.2, 0.3, 1.0), (0, -D / 2 + 0.5, H + 1.2), "fur_brown", bev=0.3)
    for x, z in ((-0.6, 1.95), (-0.2, 2.2), (0.2, 2.2), (0.6, 1.95)):
        cube(m, (0.35, 0.3, 0.4), (x, -D / 2 + 0.5, H + z), "fur_brown", bev=0.12)


def _burger_icon(m, D, H):
    for z, c, h in ((0.9, "bread", 0.4), (1.25, "meat", 0.3), (1.45, "lettuce", 0.12), (1.75, "bread", 0.5)):
        cube(m, (2.2, 1.4, h), (0, -D / 2 + 0.8, H + z), c, bev=min(0.2, h * 0.4))


def _game_icon(m, D, H):
    cube(m, (2.2, 0.4, 1.3), (0, -D / 2 + 0.5, H + 1.3), "plastic_black", bev=0.3)
    cube(m, (0.2, 0.44, 0.6), (-0.6, -D / 2 + 0.5, H + 1.3), "neon_green", bev=0.04)
    cube(m, (0.6, 0.44, 0.2), (-0.6, -D / 2 + 0.5, H + 1.3), "neon_green", bev=0.04)
    for x, z in ((0.5, 1.5), (0.8, 1.2)):
        cube(m, (0.26, 0.46, 0.26), (x, -D / 2 + 0.5, H + z), "neon_pink", bev=0.06)


reg("Bakery", lambda m: shop(m, wall="bread", awn=("awning_red", "cream"), sign=("chocolate", "cream"),
                              icon=_bread_icon), sub="Shops")
reg("CandyShop", lambda m: shop(m, wall="frosting_pink", awn=("candy_blue", "awning_white"),
                                 sign=("plastic_white", "candy_pink"), icon=_candy_icon), sub="Shops")
reg("PetShop", lambda m: shop(m, wall="tile_blue", awn=("awning_green", "plastic_yellow"),
                               sign=("plastic_yellow", "fur_brown"), icon=_paw_icon), sub="Shops")
reg("BurgerJoint", lambda m: shop(m, wall="plastic_red", awn=("plastic_yellow", "awning_red"),
                                   sign=("plastic_yellow", "plastic_red"), icon=_burger_icon), sub="Shops")
reg("ArcadeShop", lambda m: shop(m, wall="obsidian", awn=("neon_pink", "neon_blue"), sign=("black", "neon_green"),
                                  icon=_game_icon), sub="Shops")


def _cinema(m):
    W, D, H = 20.0, 14.0, 12.0
    cube(m, (W, D, H), (0, 0, H / 2), "ruby_dark", bev=0.2)
    cube(m, (W + 1.0, 4.0, 1.6), (0, -D / 2 - 1.8, 6.0), "gold", bev=0.2)
    for i in range(12):
        cube(m, (0.3, 0.2, 0.3), (-W / 2 + 0.5 + i * 1.8, -D / 2 - 3.85, 6.0), "glow", bev=0.06)
    cube(m, (12.0, 0.3, 2.4), (0, -D / 2 - 3.9, 8.4), "plastic_white", bev=0.1)
    for i in range(6):
        cube(m, (1.0, 0.2, 1.4), (-4.5 + i * 1.8, -D / 2 - 4.08, 8.4), "black", bev=0.05)
    for x in (-6, 6):
        cube(m, (3.0, 0.3, 4.0), (x, -D / 2 - 0.1, 2.6), "gold", bev=0.1)
        cube(m, (2.4, 0.4, 3.4), (x, -D / 2 - 0.18, 2.6), "plastic_yellow", bev=0.06)
    door(m, 0, -D / 2, 0, w=4.0, h=4.6, col="window_blue", frame="gold")
    flat_roof(m, W, D, H, parapet="ruby_dark")


reg("Cinema", _cinema, sub="City")


def _museum(m):
    W, D, H = 22.0, 14.0, 10.0
    cube(m, (W, D, H), (0, 0, H / 2 + 1.2), "sandstone", bev=0.15)
    for k in range(3):
        cube(m, (W + 2.0 - k * 0.6, D + 3.0 - k * 1.0, 0.4), (0, -0.8 + k * 0.4, 0.2 + k * 0.4), "stone_light", bev=0.06)
    for i in range(8):
        x = -W / 2 + 1.2 + i * (W - 2.4) / 7
        m.cyl(r=0.55, h=H, seg=8, color="marble", loc=(x, -D / 2 - 1.5, H / 2 + 1.2))
    m.prism([(-(W / 2 + 0.5), 0), (W / 2 + 0.5, 0), (0, 3.6)], depth=4.0, color="marble", rot=(90, 0, 0),
            loc=(0, -D / 2 - 1.0, H + 1.6))
    cube(m, (W + 1.0, 4.0, 0.6), (0, -D / 2 - 1.0, H + 1.5), "marble", bev=0.1)
    door(m, 0, -D / 2, 1.2, w=3.6, h=5.2, col="wood_dark", frame="marble_dark")
    m.box((2.0, 2.0, 2.4), color="gold", bevel=0.3, loc=(0, -D / 2 - 4.0, 2.2))
    m.sphere(round=True, r=0.9, color="gold", loc=(0, -D / 2 - 4.0, 4.1))


reg("Museum", _museum, sub="City")


def _castle_keep(m):
    W = 14.0
    cube(m, (W, W, 12.0), (0, 0, 6.0), "stone", bev=0.15, cuts={"z": 1.8})
    crenel(m, W, W, 12.0, "stone_dark")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.cyl(r=2.4, h=16.0, seg=8, color="stone_dark", loc=(sx * W / 2, sy * W / 2, 8.0))
            m.cone(r=3.0, h=4.0, seg=8, color="roof_blue", loc=(sx * W / 2, sy * W / 2, 16.0))
            m.cyl(r=0.08, h=2.0, seg=6, color="wood_dark", loc=(sx * W / 2, sy * W / 2, 20.5))
            m.box((1.2, 0.06, 0.8), color="fire_red", loc=(sx * W / 2 + 0.6, sy * W / 2, 21.0), bevel=0.02)
    cube(m, (4.0, 0.6, 5.0), (0, -W / 2 - 0.2, 2.5), "black", bev=0.05)
    m.cyl(r=2.0, h=0.6, seg=8, color="black", rot=(90, 0, 0), loc=(0, -W / 2 - 0.2, 5.0))
    for z in (7.0, 10.0):
        for x in (-4, 4):
            cube(m, (0.8, 0.4, 1.6), (x, -W / 2 - 0.05, z), "black", bev=0.05)


reg("CastleKeep", _castle_keep, sub="Landmarks")


def _treehouse(m):
    m.cyl(r=1.2, r2=0.9, h=14.0, seg=8, color="bark", loc=(0, 0, 7.0))
    cube(m, (7.0, 7.0, 0.5), (0, 0, 7.0), "wood", bev=0.1)
    cube(m, (5.0, 5.0, 4.0), (0, 0.6, 9.2), "wood_light", bev=0.12)
    gable_roof(m, 5.0, 5.0, 11.2, 2.4, col="roof_green", trim="wood")
    door(m, 0, -1.9, 7.25, w=1.8, h=3.0, col="wood_dark", frame="wood")
    window(m, 2.5, 0.6, 9.4, face="left", w=1.4, h=1.4, frame="wood", sill=False)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(m, (0.2, 0.2, 1.2), (sx * 3.3, sy * 3.3, 7.8), "wood_dark", bev=0.03)
    for i in range(10):
        cube(m, (1.2, 0.12, 0.12), (0, -1.4, 0.6 + i * 0.65), "wood_light", bev=0.02)
    for s in (-1, 1):
        cube(m, (0.12, 0.12, 6.8), (s * 0.55, -1.4, 3.4), "wood_light", bev=0.02)
    for x, y, z, s in ((0, 0, 15.0, 5.0), (2.5, 1.0, 14.0, 3.4), (-2.5, 0.5, 14.2, 3.6), (0.5, -2.0, 13.8, 3.0)):
        m.ico(r=s / 2, sub=1, color=lambda c, n: "leaf_light" if n.z > 0.3 else "leaf", loc=(x, y, z))


reg("Treehouse", _treehouse, sub="Homes")


def _igloo(m):
    m.lathe([(0, 0), (4.0, 0), (3.8, 1.6), (3.0, 3.0), (1.6, 3.9), (0, 4.1)], seg=8, color="snow",
            cuts={"z": 0.8})
    m.box((2.4, 2.6, 2.4), color="snow", bevel=0.4, loc=(0, -4.0, 1.2))
    m.box((1.6, 0.3, 1.8), color="black", bevel=0.2, loc=(0, -5.2, 0.9))


reg("Igloo", _igloo, sub="Homes")


def _log_cabin(m):
    W, D, H = 12.0, 10.0, 6.0
    for z in range(int(H / 0.6)):
        for s in (-1, 1):
            m.cyl(r=0.32, h=W + 1.0, seg=6, color="wood_mid" if z % 2 else "wood", rot=(0, 90, 0),
                  loc=(0, s * D / 2, 0.32 + z * 0.6))
            m.cyl(r=0.32, h=D + 1.0, seg=6, color="wood" if z % 2 else "wood_mid", rot=(90, 0, 0),
                  loc=(s * W / 2, 0, 0.62 + z * 0.6))
    cube(m, (W - 0.4, D - 0.4, H), (0, 0, H / 2 + 0.3), "wood_dark", bev=0.1)
    door(m, 0, -D / 2 - 0.2, 0.3, w=2.2, h=4.0, col="wood_deep", frame="wood_dark")
    for x in (-3.4, 3.4):
        window(m, x, -D / 2 - 0.3, 3.4, w=1.6, h=1.6, frame="wood_dark", sill=False)
    gable_roof(m, W, D, H + 0.4, D * 0.5, col="roof_green", trim="wood")
    cube(m, (1.6, 1.6, 4.0), (W / 2 - 1.5, D / 4, H + 2.6), "stone", bev=0.1)


reg("LogCabin", _log_cabin, sub="Homes")


def _beach_hut(m):
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(m, (0.4, 0.4, 2.0), (sx * 2.8, sy * 2.8, 1.0), "wood_dark", bev=0.06)
    cube(m, (7.0, 7.0, 0.4), (0, 0, 2.2), "wood", bev=0.08)
    cube(m, (5.6, 5.6, 4.0), (0, 0, 4.4), "wood_pale", bev=0.12)
    m.pyramid(w=8.4, h=3.4, color="corn_husk", loc=(0, 0, 6.3))
    door(m, 0, -2.8, 2.4, w=1.8, h=3.2, col="plastic_blue", frame="wood")
    for i in range(5):
        cube(m, (1.4, 0.3, 0.14), (0, -3.8 - i * 0.45, 2.0 - i * 0.42), "wood", bev=0.03)


reg("BeachHut", _beach_hut, sub="Homes")


def _pagoda(m):
    for i, (w, h) in enumerate(((10.0, 4.0), (8.0, 3.4), (6.0, 3.0))):
        z0 = sum(hh + 1.2 for _, hh in ((10.0, 4.0), (8.0, 3.4), (6.0, 3.0))[:i])
        cube(m, (w, w, h), (0, 0, z0 + h / 2), "fire_red", bev=0.12)
        m.pyramid(w=w + 3.0, h=1.4, color="obsidian", loc=(0, 0, z0 + h))
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.pyramid(w=0.4, h=0.8, color="gold", loc=(sx * (w / 2 + 1.3), sy * (w / 2 + 1.3), z0 + h - 0.2),
                          rot=(sy * -40, sx * 40, 0))
    m.cyl(r=0.2, h=3.0, seg=6, color="gold", loc=(0, 0, 16.5))
    door(m, 0, -5.0, 0, w=2.6, h=3.4, col="wood_deep", frame="gold")


reg("Pagoda", _pagoda, sub="Landmarks")


def _pyramid(m):
    for i in range(7):
        w = 20.0 - i * 2.8
        cube(m, (w, w, 1.6), (0, 0, 0.8 + i * 1.6), "sandstone" if i % 2 else "sand", bev=0.15)
    cube(m, (1.6, 1.6, 1.4), (0, 0, 11.9), "gold", bev=0.2)
    cube(m, (2.4, 0.4, 3.0), (0, -10.0, 1.5), "black", bev=0.05)


reg("Pyramid", _pyramid, sub="Landmarks")


def _temple(m):
    W, D = 16.0, 10.0
    for k in range(3):
        cube(m, (W + 2.0 - k * 0.8, D + 2.0 - k * 0.8, 0.4), (0, 0, 0.2 + k * 0.4), "marble_dark", bev=0.05)
    for i in range(6):
        for s in (-1, 1):
            m.cyl(r=0.55, h=7.0, seg=8, color="marble", loc=(-W / 2 + 1.0 + i * (W - 2.0) / 5, s * (D / 2 - 1.0), 4.7))
    cube(m, (W, D, 1.0), (0, 0, 8.7), "marble", bev=0.1)
    m.prism([(-(D / 2), 0), (D / 2, 0), (0, 2.6)], depth=W, color="marble", rot=(90, 0, 90), loc=(0, 0, 9.2))


reg("GreekTemple", _temple, sub="Landmarks")


def _mine_entrance(m):
    rock_col = lambda c, n: "stone_light" if n.z > 0.6 else "stone"
    m.box((14.0, 6.0, 9.0), color=rock_col, bevel=1.4, loc=(0, 1.0, 4.5))
    cube(m, (6.0, 1.0, 6.0), (0, -2.0, 3.0), "black", bev=0.1)
    for s in (-1, 1):
        cube(m, (0.8, 0.8, 6.4), (s * 3.2, -2.4, 3.2), "wood", bev=0.08)
    cube(m, (7.6, 0.9, 0.9), (0, -2.4, 6.6), "wood", bev=0.08)
    cube(m, (4.0, 0.3, 1.0), (0, -2.9, 7.6), "wood_light", bev=0.06)
    for x in (-0.8, 0.8):
        cube(m, (0.3, 12.0, 0.2), (x, -7.0, 0.1), "iron_dark", bev=0.04)
    for i in range(12):
        cube(m, (2.4, 0.4, 0.15), (0, -1.5 - i * 1.0, 0.05), "wood_dark", bev=0.03)
    m.lathe([(0, 0), (0.25, 0), (0.3, 0.6), (0, 0.6)], seg=6, color="glow", loc=(2.4, -3.0, 5.4))
    for i, (x, c) in enumerate(((-4.5, "gold"), (4.2, "diamond"), (-5.2, "emerald"))):
        m.crystal(r=0.3, h=0.9, color=c, loc=(x, -1.9, 2.0 + i * 1.5), rot=(-60, 0, 0))


reg("MineEntrance", _mine_entrance, sub="Landmarks", tags=["mining", "simulator"])


def _bridge(m):
    L = 16.0
    m.box((4.0, L, 0.5), color="wood", bevel=0.08, loc=(0, 0, 2.0), cuts={"y": 1.0},
          deform=lambda co: co.__class__((co.x, co.y, co.z + 1.2 * (1 - (co.y / (L / 2)) ** 2))))
    for s in (-1, 1):
        for i in range(9):
            y = -L / 2 + i * L / 8
            z = 2.0 + 1.2 * (1 - (y / (L / 2)) ** 2)
            cube(m, (0.25, 0.25, 1.4), (s * 1.9, y, z + 0.8), "wood_dark", bev=0.04)
        pts = [(s * 1.9, -L / 2 + i * L / 8, 2.0 + 1.2 * (1 - ((-L / 2 + i * L / 8) / (L / 2)) ** 2) + 1.4)
               for i in range(9)]
        m.tube(pts, [0.12] * 9, seg=4, color="wood_dark")
    for y in (-L / 2 + 0.6, L / 2 - 0.6):
        cube(m, (4.6, 1.2, 2.0), (0, y, 1.0), "stone", bev=0.15)


reg("Bridge", _bridge, sub="Landmarks")


def _water_tower(m):
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.tube([(sx * 2.4, sy * 2.4, 0), (sx * 1.8, sy * 1.8, 10.0)], [0.2, 0.18], seg=4, color="gunmetal")
    for z in (3.5, 7.0):
        cube(m, (4.6 - z * 0.12, 0.15, 0.15), (0, 2.3 - z * 0.06, z), "gunmetal", bev=0.03)
        cube(m, (4.6 - z * 0.12, 0.15, 0.15), (0, -2.3 + z * 0.06, z), "gunmetal", bev=0.03)
    m.cyl(r=3.0, h=4.0, seg=8, color="tile_blue", loc=(0, 0, 12.0))
    m.cone(r=3.3, h=2.0, seg=8, color="gunmetal", loc=(0, 0, 14.0))
    m.torus(R=3.1, r=0.12, seg=8, color="gunmetal", loc=(0, 0, 10.2))


reg("WaterTower", _water_tower, sub="City")


def _power_pole(m):
    m.cyl(r=0.3, h=14.0, seg=6, color="wood_dark", loc=(0, 0, 7.0))
    for z in (12.4, 13.4):
        cube(m, (5.0, 0.3, 0.3), (0, 0, z), "wood_dark", bev=0.05)
        for x in (-2.2, -0.8, 0.8, 2.2):
            m.cyl(r=0.12, h=0.4, seg=6, color="plastic_green", loc=(x, 0, z + 0.35))
    m.cyl(r=0.6, h=1.2, seg=8, color="gunmetal", loc=(0.7, 0, 10.5))


reg("PowerPole", _power_pole, sub="City")


def _phone_booth(m):
    cube(m, (2.4, 2.4, 6.0), (0, 0, 3.0), "fire_red", bev=0.12)
    for face, x, y in (("front", 0, -1.2), ("left", 1.2, 0), ("right", -1.2, 0)):
        for z in (2.2, 3.4, 4.6):
            window(m, x, y, z, w=1.5, h=0.9, face=face, frame="fire_red", sill=False)
    cube(m, (2.6, 2.6, 0.4), (0, 0, 6.2), "fire_red", bev=0.1)
    cube(m, (1.8, 0.2, 0.4), (0, -1.25, 5.6), "plastic_white", bev=0.04)


reg("PhoneBooth", _phone_booth, sub="Signs")


def _vending(m, col="plastic_blue"):
    cube(m, (2.4, 1.6, 4.8), (0, 0, 2.4), col, bev=0.12)
    cube(m, (1.5, 0.1, 3.2), (-0.3, -0.8, 2.8), "window_blue", bev=0.04)
    for r in range(4):
        for c in range(3):
            cube(m, (0.35, 0.12, 0.5), (-0.8 + c * 0.5, -0.86, 1.6 + r * 0.75),
                 ["plastic_red", "plastic_yellow", "plastic_green", "plastic_orange"][(r + c) % 4], bev=0.04)
    cube(m, (0.5, 0.12, 1.0), (0.85, -0.82, 3.2), "charcoal", bev=0.04)
    cube(m, (1.6, 0.14, 0.5), (-0.3, -0.83, 0.6), "charcoal", bev=0.04)


reg("VendingMachine", lambda m: _vending(m), sub="Signs")
reg("SnackMachine", lambda m: _vending(m, col="plastic_red"), sub="Signs")


def _atm(m):
    cube(m, (2.0, 1.6, 4.4), (0, 0, 2.2), "gunmetal", bev=0.12)
    cube(m, (1.4, 0.3, 1.0), (0, -0.85, 3.4), "screen_glow", bev=0.05, rot=(-10, 0, 0))
    cube(m, (1.4, 0.5, 0.6), (0, -0.95, 2.4), "charcoal", bev=0.06, rot=(20, 0, 0))
    cube(m, (0.8, 0.1, 0.12), (0, -0.82, 1.7), "black", bev=0.02)
    cube(m, (2.1, 0.6, 0.6), (0, -0.5, 4.5), "sign_green", bev=0.08)


reg("ATM", _atm, sub="Signs")


def _dumpster(m):
    cube(m, (5.0, 3.0, 2.6), (0, 0, 1.6), "sign_green", bev=0.15)
    cube(m, (5.2, 3.2, 0.2), (0, 0, 2.95), "charcoal", bev=0.05, rot=(-4, 0, 0))
    for x in (-2.0, 2.0):
        for y in (-1.1, 1.1):
            m.cyl(r=0.25, h=0.2, seg=6, color="charcoal", rot=(0, 90, 0), loc=(x, y, 0.25))
    cube(m, (0.3, 3.1, 0.3), (0, 0, 2.0), "charcoal", bev=0.05)


reg("Dumpster", _dumpster, sub="Signs")


# --- playground & fun park ------------------------------------------------------------------------
def _slide(m):
    for sx in (-1, 1):
        for y in (0.0, 2.0):
            cube(m, (0.3, 0.3, 5.0), (sx * 1.1, y, 2.5), "plastic_red", bev=0.05)
    cube(m, (2.6, 2.4, 0.3), (0, 1.0, 4.0), "plastic_yellow", bev=0.06)
    for i in range(6):
        cube(m, (1.8, 0.2, 0.14), (0, 2.4 + i * 0.1, 0.6 + i * 0.6), "plastic_blue", bev=0.03)
    m.box((1.8, 5.6, 0.2), color="plastic_green", bevel=0.05, loc=(0, -2.2, 2.2), rot=(-38, 0, 0))
    for s in (-1, 1):
        m.box((0.15, 5.6, 0.5), color="plastic_green", bevel=0.04, loc=(s * 0.95, -2.2, 2.4), rot=(-38, 0, 0))
    m.pyramid(w=3.0, h=1.6, color="plastic_blue", loc=(0, 1.0, 5.0))


reg("PlaygroundSlide", _slide, sub="FunPark")


def _swing(m):
    for s in (-1, 1):
        for y in (-1.0, 1.0):
            m.tube([(s * 3.0, y * 1.6, 0), (s * 3.0, 0, 5.0)], [0.15, 0.15], seg=4, color="plastic_blue")
    m.cyl(r=0.15, h=6.4, seg=6, color="plastic_blue", rot=(0, 90, 0), loc=(0, 0, 5.0))
    with m.group("SwingL"):
        for x in (1.0, 2.0):
            m.tube([(x, 0, 5.0), (x, 0, 1.2)], [0.03, 0.03], seg=4, color="silver")
        cube(m, (1.2, 0.6, 0.12), (1.5, 0, 1.1), "plastic_red", bev=0.03)
    with m.group("SwingR"):
        for x in (-1.0, -2.0):
            m.tube([(x, 0, 5.0), (x, 0, 1.2)], [0.03, 0.03], seg=4, color="silver")
        cube(m, (1.2, 0.6, 0.12), (-1.5, 0, 1.1), "plastic_yellow", bev=0.03)


reg("SwingSet", _swing, sub="FunPark", split=True)


def _ferris_wheel(m):
    for s in (-1, 1):
        for y in (-1.0, 1.0):
            m.tube([(s * 1.2, y * 4.0, 0), (s * 1.2, 0, 10.0)], [0.25, 0.2], seg=4, color="plastic_white")
    cube(m, (4.0, 10.0, 0.6), (0, 0, 0.3), "concrete", bev=0.1)
    with m.group("Wheel"):
        for s in (-1, 1):
            m.torus(R=8.0, r=0.18, seg=16, color="plastic_white", rot=(0, 90, 0), loc=(s * 0.8, 0, 10.0))
        m.cyl(r=0.6, h=2.8, seg=8, color="plastic_red", rot=(0, 90, 0), loc=(0, 0, 10.0))
        cols = ["plastic_red", "plastic_yellow", "plastic_blue", "plastic_green", "plastic_purple", "plastic_orange",
                "plastic_pink", "neon_blue"]
        for i in range(8):
            a = math.radians(i * 45)
            y, z = math.cos(a) * 8.0, 10.0 + math.sin(a) * 8.0
            for s in (-1, 1):
                m.tube([(s * 0.8, 0, 10.0), (s * 0.8, y, z)], [0.08, 0.08], seg=4, color="plastic_white")
            cube(m, (2.4, 1.6, 1.6), (0, y, z - 1.2), cols[i], bev=0.3)
            cube(m, (2.44, 1.2, 0.6), (0, y, z - 1.0), "window_blue", bev=0.05)


reg("FerrisWheel", _ferris_wheel, sub="FunPark", split=True)


def _carousel(m):
    m.cyl(r=6.0, h=0.8, seg=8, color="plastic_red", loc=(0, 0, 0.4))
    m.cyl(r=0.6, h=6.0, seg=8, color="gold", loc=(0, 0, 3.5))
    with m.group("Ride"):
        m.cyl(r=5.8, h=0.3, seg=8, color="plastic_white", loc=(0, 0, 0.95))
        for i in range(6):
            a = math.radians(i * 60 + 30)
            x, y = math.cos(a) * 4.2, math.sin(a) * 4.2
            m.cyl(r=0.1, h=5.6, seg=6, color="gold", loc=(x, y, 3.8))
            cube(m, (0.8, 2.0, 1.0), (x, y, 2.4), ["plastic_white", "fur_tan", "fur_black"][i % 3], bev=0.2,
                 rot=(0, 0, i * 60 + 30 + 90))
            cube(m, (0.6, 0.7, 0.9), (x + math.cos(a + 1.57) * 0.9, y + math.sin(a + 1.57) * 0.9, 3.0),
                 ["plastic_white", "fur_tan", "fur_black"][i % 3], bev=0.15, rot=(0, 0, i * 60 + 30 + 90))
        m.cone(r=6.6, h=2.6, seg=8, color=lambda c, n: "plastic_red" if int((math.degrees(math.atan2(c.y, c.x)) + 382.5) / 45) % 2
               else "plastic_yellow", loc=(0, 0, 6.6))
        m.sphere(round=True, r=0.5, color="gold", loc=(0, 0, 9.4))


reg("Carousel", _carousel, sub="FunPark", split=True)


def _stage(m):
    cube(m, (14.0, 8.0, 1.6), (0, 0, 0.8), "wood_dark", bev=0.1)
    cube(m, (14.0, 0.6, 8.0), (0, 3.7, 5.6), "black", bev=0.1)
    for s in (-1, 1):
        cube(m, (0.8, 0.8, 8.0), (s * 6.6, -3.6, 5.6), "gunmetal", bev=0.08)
        cube(m, (3.0, 0.3, 6.6), (s * 5.2, -3.2, 5.8), "rug_red", bev=0.1)
        cube(m, (1.4, 1.2, 2.2), (s * 5.4, 2.6, 2.7), "charcoal", bev=0.1)
        m.cyl(r=0.45, h=0.1, seg=8, color="gunmetal", rot=(90, 0, 0), loc=(s * 5.4, 2.0, 2.9))
    cube(m, (14.6, 0.8, 0.8), (0, -3.6, 9.6), "gunmetal", bev=0.08)
    for x in (-4.5, -1.5, 1.5, 4.5):
        cube(m, (0.6, 0.6, 0.7), (x, -3.6, 9.0), "charcoal", bev=0.08)
        m.cyl(r=0.25, h=0.1, seg=8, color="glow", loc=(x, -3.6, 8.6))
    m.cyl(r=0.06, h=3.0, seg=6, color="charcoal", loc=(0, -1.0, 3.1))


reg("ConcertStage", _stage, sub="FunPark")
