"""Rigged animals / pets that complement the 115 animals already in AnimalBundle.

Each animal is one skinned mesh + armature with Idle / Walk (and Fly / Swim)
animations. Body parts are built inside ``with m.group(<bone>)`` so they follow
their bone rigidly. Animals face -Y (Roblox front after export).
"""
import math

from studlib.geo import by_height, by_normal, jitter, star_pts
from studlib.registry import add

CAT = "Animals"


def _v(*a):
    return tuple(a)


# ============================================================================
# quadruped template
# ============================================================================
def quad(m, *, L=2.4, W=1.5, H=1.3, leg=0.8, leg_r=0.22, body="fur_brown", belly=None, legc=None, paw=None,
         head_r=0.72, head=None, head_up=0.55, head_fwd=0.15, snout=0.42, snout_col=None, snout_len=1.1,
         snout_drop=0.32, snout_shape="round", nose="black", nose_s=1.0, ears="round", ear=None,
         ear_in="pink_inner", ear_s=1.0, tail="short", tail_col=None, tail_tip=None, tail_s=1.0, eye_s=1.0,
         neck=0.0, cheeks=None, extras=None, kind="quadruped"):
    head = head or body
    ear = ear or head
    legc = legc or body
    tail_col = tail_col or body
    cz = leg + H * 0.42
    hy = -L / 2 - head_fwd
    hz = cz + H * 0.25 + head_up * head_r + neck
    r = head_r
    d = dict(L=L, W=W, H=H, leg=leg, cz=cz, hy=hy, hz=hz, r=r)

    m.bone("Body", (0, L * 0.3, cz), (0, -L * 0.3, cz))
    m.bone("Head", (0, -L * 0.32, cz + H * 0.2), (0, hy, hz + r), parent="Body")
    legs = (("LegFL", 1, -1), ("LegFR", -1, -1), ("LegBL", 1, 1), ("LegBR", -1, 1))
    for nm, sx, sy in legs:
        x, y = sx * W * 0.28, sy * L * 0.3
        m.bone(nm, (x, y, cz - H * 0.12), (x, y, 0.02), parent="Body")
    if tail != "none":
        m.bone("Tail", (0, L * 0.42, cz + H * 0.1), (0, L * 0.5 + 0.5 * tail_s, cz + H * 0.35 + 0.3 * tail_s),
               parent="Body")

    with m.group("Body"):
        col = (lambda c, n: belly if n.z < -0.35 or (n.y < -0.75 and c.z < cz + H * 0.1) else body) if belly else body
        m.sphere(r=1, seg=14, rings=10, color=col, loc=(0, 0, cz), scale=(W / 2, L / 2, H / 2))
        if neck > 0:
            m.tube([(0, -L * 0.35, cz + H * 0.1), (0, hy + r * 0.2, hz - r * 0.3)], [W * 0.26, r * 0.5], seg=10,
                   color=body)

    for nm, sx, sy in legs:
        with m.group(nm):
            x, y = sx * W * 0.28, sy * L * 0.3
            top = cz - H * 0.05
            kw = dict(cuts={"z": [leg * 0.25]}) if paw else {}
            m.cyl(r=leg_r, r2=leg_r * 1.08, h=top, seg=10, loc=(x, y, top / 2), bevel=leg_r * 0.45,
                  color=by_height(paw, leg * 0.25, legc) if paw else legc, **kw)

    with m.group("Head"):
        m.sphere(r=r, seg=14, rings=10, color=head, loc=(0, hy, hz), scale=(1, 0.95, 0.92))
        sn_y = hy - r * 0.72
        sn_z = hz - r * snout_drop
        tip_y = sn_y
        if snout and snout_shape == "round":
            m.sphere(r=r * snout, seg=12, rings=8, color=snout_col or head, loc=(0, sn_y, sn_z),
                     scale=(1.1, snout_len, 0.8))
            tip_y = sn_y - r * snout * snout_len * 0.95
            m.sphere(r=r * 0.13 * nose_s, seg=8, rings=5, color=nose, loc=(0, tip_y + r * 0.04, sn_z + r * snout * 0.35),
                     scale=(1.3, 0.8, 0.9))
        elif snout and snout_shape == "disc":
            m.cyl(r=r * snout, h=r * 0.5, seg=12, color=snout_col or head, rot=(90, 0, 0), loc=(0, sn_y - r * 0.1, sn_z),
                  bevel=r * 0.08)
            tip_y = sn_y - r * 0.36
            for s in (-1, 1):
                m.sphere(r=r * 0.07, seg=6, rings=4, color=nose, loc=(s * r * 0.14, tip_y, sn_z), scale=(1, 0.5, 1.3))
        ex, ey, ez = r * 0.42, hy - r * 0.76, hz + r * 0.2
        m.eye((ex, ey, ez), r=r * 0.15 * eye_s, mirror=True)
        if cheeks:
            m.sphere(r=r * 0.14, seg=8, rings=5, color=cheeks, loc=(r * 0.62, hy - r * 0.62, hz - r * 0.12),
                     scale=(1, 0.5, 0.7), mirror=True)
        es = ear_s * r
        if ears == "round":
            m.sphere(r=es * 0.34, seg=10, rings=6, color=ear, loc=(r * 0.62, hy + r * 0.05, hz + r * 0.7),
                     scale=(1, 0.45, 1), rot=(0, -20, 0), mirror=True)
            m.sphere(r=es * 0.22, seg=8, rings=5, color=ear_in, loc=(r * 0.62, hy - r * 0.06, hz + r * 0.7),
                     scale=(1, 0.3, 1), rot=(0, -20, 0), mirror=True)
        elif ears == "pointy":
            m.cone(r=es * 0.3, h=es * 0.62, seg=6, color=ear, loc=(r * 0.5, hy + r * 0.05, hz + r * 0.6),
                   rot=(0, 18, 0), scale=(1, 0.5, 1), mirror=True, smooth=False)
            m.cone(r=es * 0.18, h=es * 0.42, seg=6, color=ear_in, loc=(r * 0.5, hy - r * 0.07, hz + r * 0.64),
                   rot=(0, 18, 0), scale=(1, 0.3, 1), mirror=True, smooth=False)
        elif ears == "floppy":
            m.sphere(r=es * 0.45, seg=10, rings=7, color=ear, loc=(r * 0.88, hy + r * 0.05, hz - r * 0.05),
                     scale=(0.35, 0.55, 1.0), rot=(0, 18, 0), mirror=True)
        elif ears == "long":
            m.sphere(r=es * 0.8, seg=10, rings=7, color=ear, loc=(r * 0.35, hy + r * 0.05, hz + r * 1.35),
                     scale=(0.28, 0.14, 1.0), rot=(0, 12, 0), mirror=True)
            m.sphere(r=es * 0.6, seg=8, rings=6, color=ear_in, loc=(r * 0.35, hy - r * 0.06, hz + r * 1.35),
                     scale=(0.2, 0.08, 1.0), rot=(0, 12, 0), mirror=True)
        elif ears == "small":
            m.sphere(r=es * 0.2, seg=8, rings=5, color=ear, loc=(r * 0.55, hy + r * 0.1, hz + r * 0.72),
                     scale=(1, 0.5, 1), mirror=True)
        elif ears == "side":
            m.sphere(r=es * 0.3, seg=8, rings=6, color=ear, loc=(r * 0.95, hy + r * 0.1, hz + r * 0.25),
                     scale=(0.35, 0.6, 1.0), rot=(0, 60, 0), mirror=True)

    if tail != "none":
        with m.group("Tail"):
            ty, tz = L * 0.44, cz + H * 0.12
            ts = tail_s
            if tail == "short":
                m.sphere(r=0.22 * ts, seg=8, rings=6, color=tail_col, loc=(0, ty + 0.05, tz + 0.1))
            elif tail == "long":
                m.tube([(0, ty - 0.1, tz), (0, ty + 0.45 * ts, tz + 0.25 * ts), (0, ty + 0.8 * ts, tz + 0.7 * ts),
                        (0, ty + 0.85 * ts, tz + 1.0 * ts)], [0.12 * ts, 0.1 * ts, 0.08 * ts, 0.04 * ts], seg=8,
                       color=tail_col if not tail_tip else
                       (lambda c, n: tail_tip if c.z > tz + 0.75 * ts else tail_col), cuts={"z": [tz + 0.75 * ts]})
            elif tail == "fluffy":
                pts = [(0, ty - 0.1, tz), (0, ty + 0.5 * ts, tz + 0.35 * ts), (0, ty + 0.85 * ts, tz + 0.9 * ts),
                       (0, ty + 0.8 * ts, tz + 1.35 * ts), (0, ty + 0.65 * ts, tz + 1.55 * ts)]
                tipz = tz + 1.2 * ts
                m.tube(pts, [0.16 * ts, 0.34 * ts, 0.36 * ts, 0.24 * ts, 0.0], seg=10,
                       color=(lambda c, n: tail_tip if c.z > tipz else tail_col) if tail_tip else tail_col,
                       cuts={"z": [tipz]} if tail_tip else None)
            elif tail == "curly":
                m.torus(R=0.15 * ts, r=0.06 * ts, seg=10, rseg=5, arc=300, color=tail_col, rot=(0, 90, 0),
                        loc=(0, ty + 0.12, tz + 0.1))
            elif tail == "flat":
                m.box((0.7 * ts, 1.1 * ts, 0.14), color=tail_col, bevel=0.1, loc=(0, ty + 0.6 * ts, cz - H * 0.35),
                      rot=(15, 0, 0))
            elif tail == "tuft":
                m.tube([(0, ty - 0.05, tz), (0, ty + 0.25, tz - 0.3 * ts), (0, ty + 0.3, tz - 0.7 * ts)],
                       [0.05, 0.05, 0.05], seg=5, color=tail_col)
                m.sphere(r=0.13 * ts, seg=8, rings=5, color=tail_tip or "fur_darkbrown",
                         loc=(0, ty + 0.3, tz - 0.8 * ts), scale=(1, 1, 1.4))
            elif tail == "thin":
                m.tube([(0, ty - 0.1, tz), (0, ty + 0.6 * ts, tz - 0.2), (0, ty + 1.2 * ts, tz + 0.1),
                        (0, ty + 1.6 * ts, tz + 0.5)], [0.06, 0.05, 0.04, 0.02], seg=6, color=tail_col)
            elif tail == "ringed":
                pts = [(0, ty - 0.1, tz), (0, ty + 0.5 * ts, tz + 0.2 * ts), (0, ty + 0.95 * ts, tz + 0.55 * ts),
                       (0, ty + 1.2 * ts, tz + 1.0 * ts)]
                band = 0.18 * ts
                m.tube(pts, [0.16 * ts, 0.24 * ts, 0.2 * ts, 0.05 * ts], seg=10,
                       color=lambda c, n: tail_tip if int((c.y + c.z) / band) % 2 else tail_col)
    if extras:
        extras(m, d)
    return d


def reg(name, fn, kind="quadruped", sub="Pets", tags=()):
    add(name, CAT, fn, sub=sub, rig=kind, tags=list(tags) + ["animal", "rigged"])


# ----------------------------------------------------------------------------
# farm & pets
# ----------------------------------------------------------------------------
reg("Pig", lambda m: quad(m, L=2.6, W=1.9, H=1.7, leg=0.55, leg_r=0.25, body="pig", paw="pig_dark", head_r=0.85,
                          snout=0.34, snout_shape="disc", snout_col="pig_dark", nose="brick_dark", ears="pointy",
                          ear_in="pig_dark", tail="curly", cheeks="pink_nose", head_fwd=0.05), sub="Farm")


def _sheep_extras(m, d):
    with m.group("Body"):
        L, W, H, cz = d["L"], d["W"], d["H"], d["cz"]
        for i in range(10):
            a = i * 137.5
            x = math.cos(math.radians(a)) * W * 0.42
            y = (-0.4 + 0.8 * ((i * 0.37) % 1)) * L
            z = cz + math.sin(math.radians(a)) * H * 0.3 + H * 0.12
            m.sphere(r=0.42, seg=8, rings=6, color="fur_white", loc=(x, y, z))
    with m.group("Head"):
        m.sphere(r=d["r"] * 0.45, seg=8, rings=6, color="fur_white", loc=(0, d["hy"] + 0.05, d["hz"] + d["r"] * 0.75))


reg("Sheep", lambda m: quad(m, L=2.6, W=1.9, H=1.7, leg=0.7, leg_r=0.16, body="fur_white", legc="charcoal",
                            head_r=0.62, head="charcoal", snout=0.4, snout_len=1.0, nose="black", ears="side",
                            ear="charcoal", tail="short", tail_col="fur_white", extras=_sheep_extras, head_up=0.7),
    sub="Farm")


def _donkey_extras(m, d):
    with m.group("Head"):
        for i in range(4):
            m.box((0.12, 0.28, 0.3), color="fur_darkgray", loc=(0, d["hy"] + 0.4 + i * 0.25, d["hz"] + d["r"] * 0.6 - i * 0.2),
                  rot=(30, 0, 0))


reg("Donkey", lambda m: quad(m, L=3.2, W=1.6, H=1.5, leg=1.4, leg_r=0.2, body="fur_gray", belly="fur_lightgray",
                             paw="hoof", head_r=0.62, snout=0.6, snout_len=1.3, snout_col="fur_lightgray", nose="charcoal",
                             ears="long", ear_s=0.85, ear_in="fur_darkgray", tail="tuft", tail_tip="fur_darkgray",
                             neck=0.5, head_fwd=0.6, extras=_donkey_extras), sub="Farm")


reg("Corgi", lambda m: quad(m, L=2.8, W=1.4, H=1.2, leg=0.45, leg_r=0.17, body="fur_orange", belly="fur_white",
                            paw="fur_white", head_r=0.72, snout=0.42, snout_col="fur_white", nose="black",
                            ears="pointy", ear_s=1.35, ear_in="fur_cream", tail="short", tail_col="fur_white",
                            cheeks=None, head_up=0.6), sub="Pets")


def _dalmatian_extras(m, d):
    with m.group("Body"):
        for i in range(12):
            a = i * 137.5
            z = d["cz"] + math.sin(math.radians(a * 1.3)) * d["H"] * 0.3
            x = math.cos(math.radians(a)) * d["W"] * 0.48
            y = (-0.38 + 0.76 * ((i * 0.618) % 1)) * d["L"]
            m.sphere(r=0.13, seg=6, rings=4, color="black", loc=(x, y, z), scale=(0.5, 1, 1),
                     rot=(0, 0, math.degrees(math.atan2(math.sin(math.radians(a)) * 0, 1))))
    with m.group("Head"):
        m.sphere(r=0.12, seg=6, rings=4, color="black", loc=(d["r"] * 0.5, d["hy"] - d["r"] * 0.5, d["hz"] + d["r"] * 0.55),
                 scale=(1, 0.5, 1))


reg("Dalmatian", lambda m: quad(m, L=2.8, W=1.3, H=1.3, leg=1.0, leg_r=0.17, body="fur_white", head_r=0.7,
                                snout=0.45, snout_len=1.2, nose="black", ears="floppy", ear="black", tail="long",
                                tail_s=0.8, extras=_dalmatian_extras, head_fwd=0.3), sub="Pets")


reg("Husky", lambda m: quad(m, L=2.9, W=1.5, H=1.4, leg=1.0, leg_r=0.19, body="fur_gray", belly="fur_white",
                            paw="fur_white", head_r=0.74, head="fur_gray", snout=0.45, snout_len=1.15,
                            snout_col="fur_white", nose="black", ears="pointy", ear_s=1.1, ear_in="fur_white",
                            tail="fluffy", tail_s=0.8, tail_tip="fur_white", head_fwd=0.25), sub="Pets")


reg("Mouse", lambda m: quad(m, L=1.6, W=1.1, H=1.0, leg=0.2, leg_r=0.12, body="fur_lightgray", belly="fur_white",
                            head_r=0.55, snout=0.45, snout_len=1.2, nose="pink_nose", ears="round", ear_s=1.7,
                            ear_in="pink_inner", tail="thin", tail_col="pink_skin", tail_s=0.9, head_fwd=0.0,
                            head_up=0.3), sub="Pets")


def _hedgehog_extras(m, d):
    with m.group("Body"):
        for i in range(34):
            a = i * 137.5
            t = (i + 0.5) / 34
            phi = math.acos(1 - t * 1.4)
            dx = math.sin(phi) * math.cos(math.radians(a))
            dy = math.sin(phi) * math.sin(math.radians(a))
            dz = math.cos(phi)
            if dy < -0.55:
                continue
            p = (dx * d["W"] / 2 * 0.95, dy * d["L"] / 2 * 0.95, d["cz"] + dz * d["H"] / 2 * 0.95)
            tilt = math.degrees(math.acos(max(-1, min(1, dz))))
            m.cone(r=0.12, h=0.42, seg=4, color="fur_darkbrown" if i % 2 else "fur_brown", loc=p,
                   rot=(tilt, 0, math.degrees(math.atan2(dy, dx)) + 90), smooth=False)


reg("Hedgehog", lambda m: quad(m, L=1.8, W=1.5, H=1.2, leg=0.2, leg_r=0.13, body="fur_brown", belly="fur_cream",
                               head_r=0.5, head="fur_cream", snout=0.5, snout_len=1.3, nose="black", ears="small",
                               ear="fur_cream", tail="none", head_fwd=0.05, head_up=0.1,
                               extras=_hedgehog_extras), sub="Pets")


reg("Squirrel", lambda m: quad(m, L=1.6, W=1.0, H=1.1, leg=0.35, leg_r=0.12, body="fur_ginger", belly="fur_cream",
                               head_r=0.55, snout=0.4, snout_col="fur_cream", nose="black", ears="pointy",
                               ear_s=0.9, tail="fluffy", tail_s=1.3, head_up=0.8, head_fwd=0.0), sub="Pets")


reg("Otter", lambda m: quad(m, L=2.8, W=1.2, H=1.0, leg=0.35, leg_r=0.14, body="fur_brown", belly="fur_tan",
                            head_r=0.58, head="fur_brown", snout=0.5, snout_len=0.9, snout_col="fur_tan",
                            nose="black", ears="small", tail="long", tail_s=1.1, head_fwd=0.1, head_up=0.4), sub="Wild")


def _beaver_extras(m, d):
    with m.group("Head"):
        m.box((0.2, 0.08, 0.2), color="white", loc=(0, d["hy"] - d["r"] * 1.12, d["hz"] - d["r"] * 0.52), bevel=0.03)


reg("Beaver", lambda m: quad(m, L=2.2, W=1.6, H=1.4, leg=0.3, leg_r=0.16, body="fur_brown", belly="fur_tan",
                             legc="fur_darkbrown", head_r=0.66, snout=0.42, snout_col="fur_tan", nose="black",
                             ears="small", tail="flat", tail_col="bark_dark", head_fwd=0.0,
                             extras=_beaver_extras), sub="Wild")


def _skunk_extras(m, d):
    with m.group("Body"):
        m.tube([(0, -d["L"] * 0.45, d["cz"] + d["H"] * 0.3), (0, 0, d["cz"] + d["H"] * 0.5),
                (0, d["L"] * 0.45, d["cz"] + d["H"] * 0.32)], [(0.15, 0.06), (0.25, 0.06), (0.18, 0.06)], seg=6,
               color="fur_white", up=(0, 0, 1))
    with m.group("Head"):
        m.box((0.12, 0.2, 0.5), color="fur_white", loc=(0, d["hy"] - d["r"] * 0.75, d["hz"] + d["r"] * 0.35),
              bevel=0.05, rot=(30, 0, 0))


reg("Skunk", lambda m: quad(m, L=2.0, W=1.3, H=1.2, leg=0.35, leg_r=0.14, body="fur_black", head_r=0.6,
                            snout=0.38, nose="black", ears="small", tail="fluffy", tail_col="fur_black",
                            tail_tip="fur_white", tail_s=1.2, extras=_skunk_extras, head_fwd=0.05), sub="Wild")


def _fox_extras(m, d):
    with m.group("Head"):
        m.sphere(r=d["r"] * 0.45, seg=8, rings=6, color="fur_white", loc=(d["r"] * 0.45, d["hy"] - d["r"] * 0.45,
                                                                           d["hz"] - d["r"] * 0.3),
                 scale=(0.9, 0.8, 0.8), mirror=True)


reg("Fox", lambda m: quad(m, L=2.6, W=1.3, H=1.3, leg=0.8, leg_r=0.15, body="fur_orange", belly="fur_white",
                          paw="fur_darkbrown", head_r=0.66, snout=0.4, snout_len=1.5, snout_col="fur_orange",
                          nose="black", ears="pointy", ear_s=1.35, ear_in="fur_white", tail="fluffy", tail_s=1.1,
                          tail_tip="fur_white", extras=_fox_extras, head_fwd=0.25), sub="Wild")


def _raccoon_extras(m, d):
    with m.group("Head"):
        m.sphere(r=d["r"] * 0.32, seg=8, rings=6, color="fur_black",
                 loc=(d["r"] * 0.4, d["hy"] - d["r"] * 0.66, d["hz"] + d["r"] * 0.18), scale=(1.4, 0.5, 0.8), mirror=True)
        m.sphere(r=d["r"] * 0.3, seg=8, rings=6, color="fur_white",
                 loc=(d["r"] * 0.25, d["hy"] - d["r"] * 0.7, d["hz"] + d["r"] * 0.52), scale=(1.6, 0.4, 0.5), mirror=True)


reg("Raccoon", lambda m: quad(m, L=2.2, W=1.4, H=1.3, leg=0.5, leg_r=0.15, body="fur_gray", belly="fur_lightgray",
                              paw="fur_black", head_r=0.64, snout=0.38, snout_len=1.2, snout_col="fur_white",
                              nose="black", ears="pointy", ear_in="fur_white", tail="ringed", tail_s=1.2,
                              tail_col="fur_gray", tail_tip="fur_black", extras=_raccoon_extras,
                              eye_s=1.1), sub="Wild")


def _panda_extras(m, d):
    with m.group("Body"):
        m.sphere(r=1, seg=12, rings=8, color="fur_black", loc=(0, -d["L"] * 0.18, d["cz"] + d["H"] * 0.05),
                 scale=(d["W"] / 2 * 1.02, d["L"] * 0.16, d["H"] / 2 * 1.02))
    with m.group("Head"):
        m.sphere(r=d["r"] * 0.26, seg=8, rings=6, color="fur_black",
                 loc=(d["r"] * 0.4, d["hy"] - d["r"] * 0.72, d["hz"] + d["r"] * 0.15), scale=(1, 0.45, 1.3),
                 rot=(0, -25, 0), mirror=True)


reg("Panda", lambda m: quad(m, L=2.6, W=2.0, H=1.8, leg=0.55, leg_r=0.3, body="fur_white", legc="fur_black",
                            head_r=0.9, snout=0.35, snout_len=0.9, nose="black", ears="round", ear="fur_black",
                            ear_in="fur_black", tail="short", extras=_panda_extras, head_fwd=0.05, eye_s=0.9),
    sub="Wild")


def _redpanda_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            m.sphere(r=d["r"] * 0.22, seg=8, rings=5, color="fur_white",
                     loc=(s * d["r"] * 0.42, d["hy"] - d["r"] * 0.72, d["hz"] + d["r"] * 0.42), scale=(1.2, 0.4, 0.7))


reg("RedPanda", lambda m: quad(m, L=2.2, W=1.3, H=1.2, leg=0.45, leg_r=0.16, body="fur_red", legc="fur_black",
                               head_r=0.66, snout=0.36, snout_col="fur_white", nose="black", ears="pointy",
                               ear_in="fur_white", tail="ringed", tail_s=1.3, tail_col="fur_red",
                               tail_tip="fur_darkbrown", extras=_redpanda_extras), sub="Wild")


def _deer_spots(m, d):
    with m.group("Body"):
        for i in range(9):
            a = i * 137.5
            m.sphere(r=0.09, seg=6, rings=4, color="fur_white",
                     loc=(math.cos(math.radians(a)) * d["W"] * 0.3, (-0.3 + 0.6 * ((i * 0.618) % 1)) * d["L"],
                          d["cz"] + d["H"] * 0.45), scale=(1, 1, 0.5))


def _antlers(m, d, col="antler", big=1.0):
    with m.group("Head"):
        for s in (-1, 1):
            b = (s * d["r"] * 0.4, d["hy"] + d["r"] * 0.1, d["hz"] + d["r"] * 0.8)
            t = (s * d["r"] * 1.3 * big, d["hy"] + d["r"] * 0.3, d["hz"] + d["r"] * 2.2 * big)
            mid = ((b[0] + t[0]) / 2, (b[1] + t[1]) / 2, (b[2] + t[2]) / 2)
            m.tube([b, mid, t], [0.07, 0.06, 0.03], seg=5, color=col)
            for f in (0.45, 0.75):
                p = (b[0] + (t[0] - b[0]) * f, b[1] + (t[1] - b[1]) * f, b[2] + (t[2] - b[2]) * f)
                m.tube([p, (p[0] + s * 0.05, p[1] - 0.35 * big, p[2] + 0.45 * big)], [0.05, 0.02], seg=5, color=col)


reg("Deer", lambda m: quad(m, L=2.8, W=1.3, H=1.3, leg=1.4, leg_r=0.13, body="deer", belly="fur_cream", paw="hoof",
                           head_r=0.6, snout=0.45, snout_len=1.2, nose="black", ears="pointy", ear_s=1.4,
                           ear_in="fur_cream", tail="short", tail_col="fur_white", neck=0.6, head_fwd=0.5,
                           extras=_deer_spots), sub="Wild")


def _reindeer_extras(m, d):
    _antlers(m, d, big=1.1)


reg("Reindeer", lambda m: quad(m, L=3.2, W=1.6, H=1.6, leg=1.4, leg_r=0.16, body="moose", belly="fur_cream",
                               paw="hoof", head_r=0.66, snout=0.5, snout_len=1.2, snout_col="fur_cream",
                               nose="plastic_red", nose_s=1.6, ears="pointy", ear_in="fur_cream", tail="short",
                               tail_col="fur_white", neck=0.5, head_fwd=0.5, extras=_reindeer_extras), sub="Wild")


def _cheetah_extras(m, d):
    with m.group("Body"):
        for i in range(22):
            a = i * 137.5
            phi = math.acos(1 - 2 * ((i + 0.5) / 22) * 0.8)
            x = math.sin(phi) * math.cos(math.radians(a)) * d["W"] / 2
            y = math.sin(phi) * math.sin(math.radians(a)) * d["L"] / 2
            z = d["cz"] + math.cos(phi) * d["H"] / 2
            m.sphere(r=0.08, seg=6, rings=4, color="fur_black", loc=(x * 1.0, y * 1.0, z))


reg("Cheetah", lambda m: quad(m, L=3.0, W=1.2, H=1.2, leg=1.2, leg_r=0.14, body="fur_gold", belly="fur_cream",
                              head_r=0.58, snout=0.38, snout_col="fur_cream", nose="black", ears="round", ear_s=0.8,
                              ear_in="fur_black", tail="long", tail_s=1.3, tail_tip="fur_black", head_fwd=0.35,
                              extras=_cheetah_extras), sub="Wild")


reg("Hippo", lambda m: quad(m, L=4.4, W=3.0, H=2.6, leg=0.8, leg_r=0.45, body="hippo", belly="hippo_belly",
                            head_r=1.2, snout=0.8, snout_len=0.9, snout_col="hippo", snout_drop=0.2, nose="charcoal",
                            ears="small", ear_s=1.2, tail="short", head_fwd=0.4, head_up=0.3, cheeks="pink_nose"),
    sub="Wild")


def _rhino_extras(m, d):
    with m.group("Head"):
        m.cone(r=0.25, h=0.9, seg=6, color="horn", loc=(0, d["hy"] - d["r"] * 1.15, d["hz"] - d["r"] * 0.05),
               rot=(-18, 0, 0), smooth=False)
        m.cone(r=0.16, h=0.45, seg=6, color="horn", loc=(0, d["hy"] - d["r"] * 0.75, d["hz"] + d["r"] * 0.45),
               rot=(-10, 0, 0), smooth=False)


reg("Rhino", lambda m: quad(m, L=4.4, W=2.4, H=2.3, leg=1.0, leg_r=0.4, body="rhino", head_r=1.0, snout=0.62,
                            snout_len=1.1, nose="charcoal", nose_s=0.1, ears="pointy", ear_in="rhino", tail="tuft",
                            tail_s=0.8, head_fwd=0.5, head_up=0.1, extras=_rhino_extras), sub="Wild")


def _camel_extras(m, d):
    with m.group("Body"):
        for y in (-0.35, 0.35):
            m.sphere(r=0.65, seg=10, rings=7, color="camel", loc=(0, y * d["L"] * 0.6, d["cz"] + d["H"] * 0.42),
                     scale=(1, 1, 0.9))


reg("Camel", lambda m: quad(m, L=3.6, W=1.7, H=1.6, leg=2.0, leg_r=0.2, body="camel", paw="fur_tan", head_r=0.6,
                            snout=0.55, snout_len=1.3, nose="wood_dark", nose_s=0.5, ears="small", tail="tuft",
                            neck=1.1, head_fwd=0.9, extras=_camel_extras), sub="Wild")


def _axolotl_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            for k, a in enumerate((25, 0, -25)):
                m.tube([(s * d["r"] * 0.85, d["hy"] + 0.1, d["hz"] + 0.1 * (1 - k)),
                        (s * (d["r"] * 0.85 + 0.45), d["hy"] + 0.3, d["hz"] + 0.1 * (1 - k) + math.sin(math.radians(a)) * 0.45)],
                       [0.08, 0.03], seg=5, color="axolotl_gill")
        m.torus(R=0.18, r=0.03, seg=8, rseg=3, arc=160, color="octopus_dark", rot=(90, 0, 190),
                loc=(0, d["hy"] - d["r"] * 0.9, d["hz"] - d["r"] * 0.15))


reg("Axolotl", lambda m: quad(m, L=2.4, W=1.2, H=0.9, leg=0.28, leg_r=0.1, body="axolotl", head_r=0.62,
                              snout=0.0, ears="none", tail="long", tail_s=1.2, head_fwd=0.1, head_up=0.1,
                              extras=_axolotl_extras, eye_s=0.9), sub="Sea")


def _walrus_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            m.cone(r=0.08, h=0.7, seg=6, color="ceramic", loc=(s * 0.18, d["hy"] - d["r"] * 0.9, d["hz"] - d["r"] * 0.4),
                   rot=(180 + 10, 0, 0), smooth=False)
            m.sphere(r=d["r"] * 0.3, seg=8, rings=6, color="fur_tan",
                     loc=(s * d["r"] * 0.2, d["hy"] - d["r"] * 0.85, d["hz"] - d["r"] * 0.3))


reg("Walrus", lambda m: quad(m, L=3.4, W=2.4, H=2.0, leg=0.3, leg_r=0.3, body="fur_tan", belly="clay", head_r=0.9,
                             snout=0.0, ears="none", tail="none", head_fwd=0.1, head_up=0.5, extras=_walrus_extras),
    sub="Sea")


def _dragon_extras(m, d):
    L, W, H, cz = d["L"], d["W"], d["H"], d["cz"]
    m.bone("WingL", (W * 0.3, -L * 0.1, cz + H * 0.35), (W * 1.6, L * 0.1, cz + H * 0.9), parent="Body")
    m.bone("WingR", (-W * 0.3, -L * 0.1, cz + H * 0.35), (-W * 1.6, L * 0.1, cz + H * 0.9), parent="Body")
    for nm, s in (("WingL", 1), ("WingR", -1)):
        with m.group(nm):
            pts = [(0, 0), (1.8, 0.9), (1.5, 0.2), (1.1, -0.1), (0.6, -0.2)]
            pts = [(s * x, y) for x, y in pts]
            if s < 0:
                pts = list(reversed(pts))
            m.prism(pts, depth=0.06, color="amethyst", loc=(s * W * 0.28, -L * 0.1, cz + H * 0.4), rot=(90, 0, 0))
            m.tube([(s * W * 0.28, -L * 0.1, cz + H * 0.45), (s * (W * 0.28 + 1.8), -L * 0.1, cz + H * 0.4 + 0.9)],
                   [0.07, 0.04], seg=5, color="scale_dark")
    with m.group("Body"):
        for i in range(5):
            y = -L * 0.35 + i * L * 0.18
            m.cone(r=0.14, h=0.32, seg=4, color="amethyst", loc=(0, y, cz + H / 2 - 0.08), smooth=False)
    with m.group("Head"):
        for s in (-1, 1):
            m.cone(r=0.12, h=0.55, seg=6, color="horn", loc=(s * d["r"] * 0.45, d["hy"] + d["r"] * 0.2, d["hz"] + d["r"] * 0.6),
                   rot=(-35, s * 12, 0), smooth=False)
    with m.group("Tail"):
        ty, tz = L * 0.44, cz + H * 0.12
        m.prism([(0, 0.35), (0.25, 0), (0, -0.2), (-0.25, 0)], depth=0.08, color="amethyst", rot=(0, 0, 0),
                loc=(0, ty + 1.2, tz + 0.95))


reg("BabyDragon", lambda m: quad(m, L=2.4, W=1.5, H=1.4, leg=0.55, leg_r=0.2, body="scale_green", belly="bee",
                                 head_r=0.78, snout=0.5, snout_len=1.1, nose="scale_dark", nose_s=0.5, ears="none",
                                 tail="long", tail_s=1.3, eye_s=1.15, extras=_dragon_extras, head_up=0.7),
    kind="dragon", sub="Fantasy", tags=["fantasy"])


# ============================================================================
# birds
# ============================================================================
def bird(m, *, s=1.0, body="fur_white", belly=None, head=None, beak="beak", beak_type="cone", beak_len=0.5,
         legs="beak", wing=None, tail_col=None, upright=15, head_r=0.5, neck=0.0, leg_len=0.5, crest=None,
         eye_s=1.0, extras=None, W=1.2, L=1.6, H=1.2, tail="fan", neck_fwd=0.0):
    head = head or body
    wing = wing or body
    tail_col = tail_col or wing
    W, L, H, head_r, leg_len, neck = W * s, L * s, H * s, head_r * s, leg_len * s, neck * s
    cz = leg_len + H * 0.45
    up = math.radians(upright)
    fy = -math.cos(up) * L * 0.42
    fz = math.sin(up) * L * 0.42
    nb = (0, fy * 0.9, cz + fz * 0.9 + H * 0.2)
    hc = (0, nb[1] - head_r * 0.2 - neck_fwd * s, nb[2] + neck + head_r * 0.6)
    d = dict(W=W, L=L, H=H, cz=cz, hc=hc, r=head_r, s=s)
    m.bone("Body", (0, L * 0.3, cz), (0, -L * 0.3, cz + fz * 0.5))
    m.bone("Head", nb, (hc[0], hc[1], hc[2] + head_r), parent="Body")
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        m.bone(nm, (sx * W * 0.22, 0.05, cz - H * 0.2), (sx * W * 0.22, 0.05, 0.02), parent="Body")
    for nm, sx in (("WingL", 1), ("WingR", -1)):
        m.bone(nm, (sx * W * 0.42, -L * 0.15, cz + H * 0.18), (sx * W * 0.5, L * 0.35, cz - H * 0.05), parent="Body")
    m.bone("Tail", (0, L * 0.4, cz), (0, L * 0.4 + 0.6 * s, cz + 0.3 * s), parent="Body")

    with m.group("Body"):
        col = (lambda c, n: belly if (n.y < -0.3 or n.z < -0.5) else body) if belly else body
        m.sphere(r=1, seg=14, rings=10, color=col, loc=(0, 0, cz), scale=(W / 2, L / 2, H / 2), rot=(-upright, 0, 0))
        if neck > 0:
            m.tube([nb, (0, nb[1] - neck_fwd * s * 0.5, nb[2] + neck * 0.6), (hc[0], hc[1], hc[2] - head_r * 0.3)],
                   [head_r * 0.5, head_r * 0.45, head_r * 0.5], seg=10, color=head)
    with m.group("Head"):
        m.sphere(r=head_r, seg=12, rings=9, color=head, loc=hc)
        m.eye((head_r * 0.45, hc[1] - head_r * 0.72, hc[2] + head_r * 0.2), r=head_r * 0.17 * eye_s, mirror=True)
        by = hc[1] - head_r * 0.85
        bz = hc[2] - head_r * 0.12
        if beak_type == "cone":
            m.cone(r=head_r * 0.3, h=beak_len * s, seg=6, color=beak, rot=(90, 0, 0), loc=(0, by + 0.05, bz),
                   scale=(1, 1, 1), smooth=False)
        elif beak_type == "duck":
            m.sphere(r=head_r * 0.45, seg=10, rings=6, color=beak, loc=(0, by - head_r * 0.15, bz - head_r * 0.1),
                     scale=(1.0, 1.3, 0.35))
        elif beak_type == "big":
            m.tube([(0, by + 0.1, bz + head_r * 0.1), (0, by - beak_len * 0.5 * s, bz), (0, by - beak_len * s, bz - 0.25 * s)],
                   [(head_r * 0.35, head_r * 0.42), (head_r * 0.28, head_r * 0.3), 0], seg=8, color=beak, up=(0, 0, 1))
            m.sphere(r=0.06 * s, seg=6, rings=4, color="black", loc=(0, by - beak_len * s * 0.95, bz - 0.2 * s))
        elif beak_type == "bent":
            m.tube([(0, by + 0.05, bz), (0, by - beak_len * 0.5 * s, bz - 0.05), (0, by - beak_len * 0.8 * s, bz - 0.35 * s)],
                   [(head_r * 0.22, head_r * 0.25), (head_r * 0.18, head_r * 0.2), 0], seg=6,
                   color=lambda c, n: "black" if c.z < bz - 0.15 * s else beak, up=(0, 0, 1))
        if crest:
            for i in range(3):
                m.tube([(0, hc[1] + 0.05, hc[2] + head_r * 0.8), (0, hc[1] + 0.15 * s + i * 0.1 * s, hc[2] + head_r * 1.5 - i * 0.05)],
                       [0.04 * s, 0.02 * s], seg=4, color=crest)
                m.sphere(r=0.07 * s, seg=6, rings=4, color=crest,
                         loc=(0, hc[1] + 0.15 * s + i * 0.1 * s, hc[2] + head_r * 1.5 - i * 0.05))
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        with m.group(nm):
            x = sx * W * 0.22
            m.cyl(r=0.07 * s, h=leg_len + H * 0.1, seg=6, color=legs, loc=(x, 0.05, (leg_len + H * 0.1) / 2))
            m.prism([(0, 0.08), (-0.2, -0.25), (0, -0.12), (0.2, -0.25)], depth=0.05, color=legs,
                    loc=(x, 0.0, 0.025), scale=s * 1.2)
    for nm, sx in (("WingL", 1), ("WingR", -1)):
        with m.group(nm):
            m.sphere(r=1, seg=10, rings=7, color=wing, loc=(sx * W * 0.47, L * 0.08, cz + H * 0.05),
                     scale=(W * 0.1, L * 0.36, H * 0.3), rot=(-upright * 0.6 + 12, 0, sx * -6))
    with m.group("Tail"):
        if tail == "fan":
            m.prism([(0, 0), (0.35 * s, 0.6 * s), (0, 0.5 * s), (-0.35 * s, 0.6 * s)], depth=0.08 * s,
                    color=tail_col, loc=(0, L * 0.38, cz + H * 0.05 - fz * 0.3), rot=(-25 + upright * 0.4, 0, 0),
                    bevel=0.02, bseg=1)
        elif tail == "short":
            m.cone(r=0.25 * s, h=0.45 * s, seg=6, color=tail_col, rot=(-70, 0, 0), loc=(0, L * 0.38, cz),
                   scale=(1, 0.5, 1), smooth=False)
    if extras:
        extras(m, d)


def breg(name, fn, sub="Birds"):
    reg(name, fn, kind="bird", sub=sub)


breg("Duck", lambda m: bird(m, s=1.0, body="fur_white", beak="beak", beak_type="duck", legs="beak", upright=10,
                             head_r=0.48, neck=0.25, tail="short"))
breg("Chick", lambda m: bird(m, s=0.8, body="bee", beak="beak", legs="beak", upright=40, head_r=0.62, W=1.3, L=1.3,
                              H=1.3, leg_len=0.35, crest="beak_yellow", tail="short", eye_s=1.2))
breg("Penguin", lambda m: bird(m, s=1.0, body="penguin_black", belly="fur_white", head="penguin_black",
                                beak="beak", legs="beak", upright=80, head_r=0.55, W=1.4, L=2.0, H=1.4,
                                leg_len=0.25, tail="short", beak_len=0.35))
breg("Flamingo", lambda m: bird(m, s=1.0, body="flamingo", beak="fur_white", beak_type="bent", legs="flamingo",
                                 upright=5, head_r=0.36, neck=1.6, neck_fwd=0.2, leg_len=2.6, beak_len=0.6,
                                 tail="short"))
breg("Toucan", lambda m: bird(m, s=1.0, body="penguin_black", belly="fur_white", head="penguin_black",
                               beak="orange", beak_type="big", beak_len=1.1, legs="sapphire", upright=35,
                               head_r=0.52, tail="fan", leg_len=0.4))
breg("Swan", lambda m: bird(m, s=1.1, body="fur_white", beak="beak", beak_type="cone", legs="charcoal", upright=5,
                             head_r=0.36, neck=1.3, neck_fwd=-0.2, leg_len=0.3, tail="short", beak_len=0.45))


def _peacock_extras(m, d):
    s = d["s"]
    with m.group("Tail"):
        for i in range(9):
            a = -80 + i * 20
            ang = math.radians(a)
            base = (0, d["L"] * 0.35, d["cz"] + 0.1)
            tip = (math.sin(ang) * 2.2 * s, d["L"] * 0.35 + 0.5 * s, d["cz"] + math.cos(ang) * 2.2 * s + 0.1)
            m.tube([base, tip], [0.05 * s, 0.03 * s], seg=4, color="feather_teal")
            m.sphere(r=0.36 * s, seg=8, rings=5, color="feather_green", loc=tip, scale=(1, 0.2, 1.3), rot=(0, -a, 0))
            m.sphere(r=0.16 * s, seg=6, rings=4, color="feather_blue", loc=(tip[0], tip[1] - 0.06, tip[2]),
                     scale=(1, 0.3, 1.2), rot=(0, -a, 0))
            m.sphere(r=0.07 * s, seg=6, rings=4, color="gold", loc=(tip[0], tip[1] - 0.1, tip[2]), scale=(1, 0.4, 1.2))


breg("Peacock", lambda m: bird(m, s=1.0, body="feather_blue", wing="feather_teal", beak="fur_tan", legs="fur_tan",
                                upright=30, head_r=0.42, neck=0.4, crest="feather_blue", tail="none",
                                extras=_peacock_extras))


# ============================================================================
# fish & sea
# ============================================================================
def fin_yz(m, pts_yz, depth, color, loc, **kw):
    """Fin in the YZ plane (thin along X). pts are (y, z) offsets."""
    m.prism([(-z, y) for y, z in pts_yz], depth=depth, color=color, rot=(0, 90, 0), loc=loc, **kw)


def fish(m, *, L=2.0, H=1.2, W=0.6, body="fish_orange", belly=None, fin="fish_orange", stripes=None,
         stripe_col="white", eye_s=1.0, extras=None):
    cz = H / 2 + 0.1
    m.bone("Body", (0, L * 0.1, cz), (0, -L * 0.45, cz))
    m.bone("Tail", (0, L * 0.3, cz), (0, L * 0.5 + 0.6, cz), parent="Body")
    m.bone("FinL", (W * 0.4, -L * 0.1, cz - H * 0.1), (W * 0.9, L * 0.05, cz - H * 0.25), parent="Body")
    m.bone("FinR", (-W * 0.4, -L * 0.1, cz - H * 0.1), (-W * 0.9, L * 0.05, cz - H * 0.25), parent="Body")
    d = dict(L=L, H=H, W=W, cz=cz)
    with m.group("Body"):
        if stripes:
            def col(c, n):
                for y0, y1 in stripes:
                    if y0 < c.y < y1:
                        return stripe_col
                return belly if belly and n.z < -0.5 else body
            cuts = {"y": [v for pair in stripes for v in pair]}
        else:
            col = (lambda c, n: belly if n.z < -0.4 else body) if belly else body
            cuts = None
        m.sphere(r=1, seg=14, rings=10, color=col, loc=(0, 0, cz), scale=(W / 2, L / 2, H / 2), cuts=cuts)
        fin_yz(m, [(-0.2 * L, 0), (0.25 * L, 0), (0.1 * L, 0.4 * H)], 0.06, fin, (0, 0, cz + H * 0.42), bevel=0.02, bseg=1)
        m.eye((W * 0.36, -L * 0.3, cz + H * 0.12), r=H * 0.12 * eye_s, look=(1, -0.3, 0), mirror=True)
        m.sphere(r=H * 0.07, seg=6, rings=4, color="black", loc=(0, -L * 0.49, cz - H * 0.05), scale=(1.4, 0.6, 0.8))
    with m.group("Tail"):
        fin_yz(m, [(0, 0), (0.55 * L * 0.5, 0.45 * H), (0.42 * L * 0.5, 0), (0.55 * L * 0.5, -0.45 * H)], 0.06, fin,
               (0, L * 0.45, cz), bevel=0.02, bseg=1)
    for nm, sx in (("FinL", 1), ("FinR", -1)):
        with m.group(nm):
            m.sphere(r=1, seg=8, rings=5, color=fin, loc=(sx * W * 0.55, -L * 0.02, cz - H * 0.18),
                     scale=(0.04, L * 0.14, H * 0.14), rot=(0, sx * 30, 0))
    if extras:
        extras(m, d)


def _clown(m):
    fish(m, L=1.8, H=1.0, W=0.6, body="fish_orange", fin="fish_orange",
         stripes=[(-0.5, -0.36), (-0.08, 0.1), (0.55, 0.64)], stripe_col="white")


reg("Clownfish", _clown, kind="fish", sub="Sea")
reg("Bluefish", lambda m: fish(m, L=2.0, H=1.4, W=0.5, body="sapphire", belly="bee", fin="bee"), kind="fish", sub="Sea")


def sea_mammal(m, *, L=4.0, body="dolphin", belly="dolphin_belly", snout=True, dorsal=0.7, eye_s=1.0, spot=None):
    cz = 0.9
    pts = [(0, -L * 0.5, cz - 0.05), (0, -L * 0.35, cz), (0, -L * 0.05, cz + 0.05), (0, L * 0.3, cz), (0, L * 0.5, cz - 0.05)]
    rad = [(0.15, 0.12), (0.55, 0.55), (0.75, 0.75), (0.45, 0.4), (0.14, 0.1)]
    m.bone("Body", (0, L * 0.05, cz), (0, -L * 0.4, cz))
    m.bone("Tail", (0, L * 0.3, cz), (0, L * 0.62, cz), parent="Body")
    m.bone("FinL", (0.5, -L * 0.18, cz - 0.3), (1.1, -L * 0.05, cz - 0.6), parent="Body")
    m.bone("FinR", (-0.5, -L * 0.18, cz - 0.3), (-1.1, -L * 0.05, cz - 0.6), parent="Body")
    with m.group("Body"):
        m.tube(pts[:4], rad[:4], seg=12, color=lambda c, n: belly if n.z < -0.25 else body, up=(0, 0, 1))
        if snout:
            m.tube([(0, -L * 0.45, cz - 0.1), (0, -L * 0.58, cz - 0.15)], [(0.22, 0.16), (0.14, 0.1)], seg=8,
                   color=body, up=(0, 0, 1))
        fin_yz(m, [(-0.3, 0), (0.45, 0), (0.35, dorsal)], 0.1, body, (0, 0.0, cz + 0.68), bevel=0.03, bseg=1)
        m.eye((0.44, -L * 0.36, cz + 0.15), r=0.11 * eye_s, look=(1, -0.5, 0), mirror=True)
        if spot:
            m.sphere(r=0.25, seg=8, rings=5, color=spot, loc=(0.5, -L * 0.3, cz + 0.2), scale=(0.4, 1.3, 0.6),
                     mirror=True)
    with m.group("Tail"):
        m.tube(pts[3:], rad[3:], seg=12, color=body, up=(0, 0, 1))
        m.prism([(0, 0), (0.3, 0.15), (0.85, 0.5), (0.55, 0.55), (0, 0.3), (-0.55, 0.55), (-0.85, 0.5), (-0.3, 0.15)],
                depth=0.08, color=body,
                loc=(0, L * 0.5, cz - 0.05), bevel=0.02, bseg=1)
    for nm, sx in (("FinL", 1), ("FinR", -1)):
        with m.group(nm):
            m.sphere(r=1, seg=8, rings=5, color=body, loc=(sx * 0.75, -L * 0.14, cz - 0.4), scale=(0.35, 0.18, 0.05),
                     rot=(0, sx * -25, sx * 20))


reg("Dolphin", lambda m: sea_mammal(m), kind="sea", sub="Sea")
reg("Orca", lambda m: sea_mammal(m, L=4.6, body="penguin_black", belly="fur_white", snout=False, dorsal=1.1,
                                  spot="fur_white"), kind="sea", sub="Sea")


def _octopus(m):
    m.bone("Body", (0, 0, 0.6), (0, 0, 2.4))
    with m.group("Body"):
        m.lathe([(0, 0.5), (0.8, 0.6), (1.05, 1.2), (0.95, 1.9), (0.6, 2.35), (0, 2.5)], seg=14, color="octopus")
        m.eye((0.38, -0.8, 1.15), r=0.18, mirror=True)
        for x, y, z in ((0.5, -0.45, 1.9), (-0.3, -0.55, 2.0), (0.1, 0.6, 2.2)):
            m.sphere(r=0.1, seg=6, rings=4, color="octopus_dark", loc=(x, y, z), scale=(1, 1, 0.5))
    for i in range(8):
        a = math.radians(45 * i + 22.5)
        c, s = math.cos(a), math.sin(a)
        nm = f"Tentacle{i + 1}"
        m.bone(nm, (c * 0.6, s * 0.6, 0.55), (c * 1.8, s * 1.8, 0.2), parent="Body")
        with m.group(nm):
            m.tube([(c * 0.5, s * 0.5, 0.7), (c * 1.0, s * 1.0, 0.25), (c * 1.6, s * 1.6, 0.15), (c * 2.0, s * 2.0, 0.4),
                    (c * 1.9, s * 1.9, 0.6)], [0.25, 0.2, 0.14, 0.08, 0.02], seg=8,
                   color=lambda cc, n: "octopus_dark" if n.z < -0.5 else "octopus")


reg("Octopus", _octopus, kind="float", sub="Sea")


def _starfish(m):
    m.bone("Body", (0, 0, 0.1), (0, -0.8, 0.1))
    with m.group("Body"):
        m.prism(star_pts(1.3, 0.5, 5), depth=0.35, color="plastic_orange", bevel=0.05, bseg=1, loc=(0, 0, 0.2))
        for i in range(5):
            a = math.radians(90 + 72 * i)
            for k in (0.35, 0.7):
                m.sphere(r=0.07, seg=6, rings=4, color="peach", loc=(math.cos(a) * 1.2 * k, math.sin(a) * 1.2 * k, 0.4))
        m.eye((0.2, -0.3, 0.42), r=0.12, mirror=True, look=(0, 0, 1))


reg("Starfish", _starfish, kind="blob", sub="Sea")


# ============================================================================
# bugs
# ============================================================================
def _bee(m):
    cz = 1.0
    m.bone("Body", (0, 0.5, cz), (0, -0.6, cz))
    m.bone("WingL", (0.25, -0.1, cz + 0.45), (1.1, 0.2, cz + 0.9), parent="Body")
    m.bone("WingR", (-0.25, -0.1, cz + 0.45), (-1.1, 0.2, cz + 0.9), parent="Body")
    with m.group("Body"):
        m.sphere(r=1, seg=14, rings=10, color=lambda c, n: "black" if int((c.y + 5) / 0.3) % 2 else "bee",
                 loc=(0, 0.15, cz), scale=(0.62, 0.8, 0.62), cuts={"y": 0.3})
        m.sphere(r=0.45, seg=12, rings=8, color="black", loc=(0, -0.72, cz + 0.1))
        m.eye((0.2, -1.08, cz + 0.2), r=0.1, mirror=True)
        m.cone(r=0.1, h=0.3, seg=6, color="black", rot=(-90, 0, 0), loc=(0, 0.92, cz - 0.05), smooth=False)
        for s in (-1, 1):
            m.tube([(s * 0.15, -0.95, cz + 0.45), (s * 0.3, -1.1, cz + 0.8)], [0.03, 0.03], seg=4, color="black")
            m.sphere(r=0.06, seg=6, rings=4, color="black", loc=(s * 0.3, -1.1, cz + 0.8))
    for nm, s in (("WingL", 1), ("WingR", -1)):
        with m.group(nm):
            m.sphere(r=1, seg=10, rings=6, color="glass", loc=(s * 0.7, 0.1, cz + 0.7), scale=(0.55, 0.3, 0.04),
                     rot=(0, s * -25, s * -20))


reg("Bee", _bee, kind="bug", sub="Bugs")


def _ladybug(m):
    cz = 0.55
    m.bone("Body", (0, 0.6, cz), (0, -0.8, cz))
    m.bone("WingL", (0.05, -0.5, cz + 0.4), (0.4, 0.8, cz + 0.4), parent="Body")
    m.bone("WingR", (-0.05, -0.5, cz + 0.4), (-0.4, 0.8, cz + 0.4), parent="Body")
    with m.group("Body"):
        m.sphere(r=1, seg=12, rings=8, color="black", loc=(0, 0, cz - 0.05), scale=(0.95, 1.05, 0.45))
        m.sphere(r=0.42, seg=10, rings=7, color="black", loc=(0, -0.95, cz))
        m.eye((0.18, -1.3, cz + 0.12), r=0.09, mirror=True, color="eye_white", shine=False)
        m.sphere(r=0.05, seg=6, rings=4, color="black", loc=(0.18, -1.38, cz + 0.12), mirror=True)
        for i in range(3):
            for s in (-1, 1):
                m.tube([(s * 0.5, -0.4 + i * 0.4, cz - 0.1), (s * 0.95, -0.5 + i * 0.45, 0.02)], [0.05, 0.04], seg=4,
                       color="black")
    for nm, s in (("WingL", 1), ("WingR", -1)):
        with m.group(nm):
            m.sphere(r=1, seg=12, rings=8, color="ladybug", loc=(s * 0.48, 0.05, cz + 0.12), scale=(0.52, 1.1, 0.62),
                     deform=lambda co, s=s: co.__class__((co.x if co.x * s > -0.02 else -0.02 * s, co.y, max(co.z, -0.1))))
            for (x, y) in ((0.45, -0.4), (0.6, 0.25), (0.3, 0.55), (0.25, -0.05)):
                m.sphere(r=0.13, seg=6, rings=4, color="black", loc=(s * x, y, cz + 0.62 - (x - 0.3) * 0.4),
                         scale=(1, 1, 0.4))


reg("Ladybug", _ladybug, kind="bug", sub="Bugs")


def _butterfly(m):
    cz = 1.2
    m.bone("Body", (0, 0.6, cz), (0, -0.6, cz))
    m.bone("WingL", (0.1, 0, cz), (1.5, 0, cz + 0.4), parent="Body")
    m.bone("WingR", (-0.1, 0, cz), (-1.5, 0, cz + 0.4), parent="Body")
    with m.group("Body"):
        m.tube([(0, 0.8, cz), (0, 0, cz + 0.05), (0, -0.6, cz + 0.1)], [0.1, 0.14, 0.12], seg=8, color="charcoal")
        m.sphere(r=0.2, seg=8, rings=6, color="charcoal", loc=(0, -0.72, cz + 0.12))
        m.eye((0.1, -0.88, cz + 0.18), r=0.06, mirror=True)
        for s in (-1, 1):
            m.tube([(s * 0.06, -0.8, cz + 0.28), (s * 0.3, -1.2, cz + 0.8)], [0.02, 0.02], seg=4, color="charcoal")
            m.sphere(r=0.05, seg=6, rings=4, color="charcoal", loc=(s * 0.3, -1.2, cz + 0.8))
    for nm, s in (("WingL", 1), ("WingR", -1)):
        with m.group(nm):
            fore = [(0.1, 0.0), (1.5, -0.9), (1.8, -0.4), (1.3, 0.2)]
            hind = [(0.1, 0.1), (1.2, 0.3), (1.1, 1.0), (0.4, 0.9)]
            for pts, c in ((fore, "butterfly_blue"), (hind, "butterfly_orange")):
                p2 = [(s * x, y) for x, y in pts]
                if s < 0:
                    p2 = list(reversed(p2))
                m.prism(p2, depth=0.04, color=c, loc=(0, 0, cz + 0.02), rot=(0, s * -12, 0), bevel=0.015, bseg=1)
            m.sphere(r=0.16, seg=6, rings=4, color="white", loc=(s * 1.35, -0.45, cz + 0.33), scale=(1, 1, 0.3),
                     rot=(0, s * -12, 0))


reg("Butterfly", _butterfly, kind="bug", sub="Bugs")


# ============================================================================
# bipeds & fantasy blobs
# ============================================================================
def biped(m, *, body="fur_brown", belly="fur_tan", face=None, head_r=0.7, H=1.6, W=1.3, leg=0.5, arm_len=1.2,
          ears="round", ear="fur_brown", tail=None, extras=None, eye_s=1.0, snout=0.0):
    face = face or belly
    cz = leg + H / 2
    hz = leg + H + head_r * 0.7
    m.bone("Body", (0, 0, leg), (0, 0, leg + H))
    m.bone("Head", (0, 0, leg + H * 0.9), (0, 0, hz + head_r), parent="Body")
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        m.bone(nm, (sx * W * 0.25, 0, leg + 0.1), (sx * W * 0.25, 0, 0.02), parent="Body")
    for nm, sx in (("ArmL", 1), ("ArmR", -1)):
        m.bone(nm, (sx * W * 0.45, 0, leg + H * 0.82), (sx * W * 0.55, -0.1, leg + H * 0.82 - arm_len), parent="Body")
    d = dict(cz=cz, hz=hz, r=head_r, H=H, W=W, leg=leg)
    with m.group("Body"):
        m.sphere(r=1, seg=14, rings=10, color=lambda c, n: belly if n.y < -0.45 else body, loc=(0, 0, cz),
                 scale=(W / 2, W * 0.4, H / 2))
    with m.group("Head"):
        m.sphere(r=head_r, seg=14, rings=10, color=body, loc=(0, 0, hz))
        m.sphere(r=head_r * 0.72, seg=12, rings=8, color=face, loc=(0, -head_r * 0.42, hz - head_r * 0.08),
                 scale=(1, 0.6, 0.9))
        if snout:
            m.sphere(r=head_r * snout, seg=10, rings=6, color=face, loc=(0, -head_r * 0.9, hz - head_r * 0.3),
                     scale=(1.2, 0.8, 0.7))
        m.eye((head_r * 0.3, -head_r * 0.86, hz + head_r * 0.12), r=head_r * 0.14 * eye_s, mirror=True)
        m.sphere(r=head_r * 0.08, seg=6, rings=4, color="black", loc=(0, -head_r * (0.95 + snout * 0.6), hz - head_r * 0.15))
        if ears == "round":
            m.sphere(r=head_r * 0.3, seg=8, rings=6, color=ear, loc=(head_r * 0.95, 0, hz + head_r * 0.1),
                     scale=(0.5, 1, 1), mirror=True)
            m.sphere(r=head_r * 0.2, seg=8, rings=5, color=face, loc=(head_r * 1.02, -0.05, hz + head_r * 0.1),
                     scale=(0.4, 0.9, 0.9), mirror=True)
        elif ears == "small":
            m.sphere(r=head_r * 0.18, seg=8, rings=5, color=ear, loc=(head_r * 0.85, 0, hz + head_r * 0.3),
                     scale=(0.5, 1, 1), mirror=True)
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        with m.group(nm):
            m.cyl(r=0.2, h=leg + 0.2, seg=8, color=body, loc=(sx * W * 0.25, 0, (leg + 0.2) / 2), bevel=0.08)
            m.sphere(r=0.24, seg=8, rings=5, color=face, loc=(sx * W * 0.25, -0.15, 0.1), scale=(1, 1.4, 0.5))
    for nm, sx in (("ArmL", 1), ("ArmR", -1)):
        with m.group(nm):
            m.tube([(sx * W * 0.45, 0, leg + H * 0.82), (sx * W * 0.55, -0.1, leg + H * 0.82 - arm_len)], [0.16, 0.14],
                   seg=8, color=body)
            m.sphere(r=0.18, seg=8, rings=5, color=face, loc=(sx * W * 0.55, -0.1, leg + H * 0.82 - arm_len))
    if tail:
        m.bone("Tail", (0, W * 0.35, leg + 0.3), (0, W * 0.35 + 1.0, leg + 1.2), parent="Body")
        with m.group("Tail"):
            tail(m, d)
    if extras:
        extras(m, d)


def _monkey_tail(m, d):
    m.tube([(0, 0.45, d["leg"] + 0.3), (0, 1.1, d["leg"] + 0.2), (0, 1.5, d["leg"] + 0.8), (0, 1.3, d["leg"] + 1.3),
            (0, 1.0, d["leg"] + 1.2)], [0.1, 0.09, 0.08, 0.07, 0.05], seg=6, color="fur_brown")


reg("Monkey", lambda m: biped(m, body="fur_brown", belly="fur_tan", head_r=0.75, H=1.5, W=1.3, leg=0.45,
                               arm_len=1.3, ears="round", ear="fur_brown", tail=_monkey_tail, snout=0.35),
    kind="biped", sub="Wild")


def _meerkat_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            m.sphere(r=d["r"] * 0.2, seg=8, rings=5, color="fur_darkbrown",
                     loc=(s * d["r"] * 0.3, -d["r"] * 0.8, d["hz"] + d["r"] * 0.12), scale=(1.2, 0.5, 1.4))


def _meerkat_tail(m, d):
    m.tube([(0, 0.3, d["leg"] + 0.2), (0, 0.9, 0.15), (0, 1.5, 0.1)], [0.1, 0.08, 0.04], seg=6,
           color=lambda c, n: "fur_darkbrown" if c.y > 1.3 else "fur_tan")


reg("Meerkat", lambda m: biped(m, body="fur_tan", belly="fur_cream", head_r=0.5, H=2.0, W=0.95, leg=0.4, arm_len=0.8,
                                ears="small", ear="fur_darkbrown", tail=_meerkat_tail, snout=0.4,
                                extras=_meerkat_extras), kind="biped", sub="Wild")


def _slime(m, col="slime", dark="leaf_dark", crown=False):
    m.bone("Body", (0, 0, 0.05), (0, 0, 1.6))
    with m.group("Body"):
        m.lathe([(0, 0), (1.1, 0.02), (1.25, 0.35), (1.1, 0.9), (0.7, 1.35), (0.25, 1.6), (0, 1.62)], seg=16, color=col)
        m.sphere(r=0.35, seg=8, rings=5, color="white", loc=(-0.55, -0.5, 1.1), scale=(0.5, 0.3, 0.7), rot=(0, -30, 0))
        for s in (-1, 1):
            m.sphere(r=0.17, seg=10, rings=7, color="black", loc=(s * 0.38, -1.02, 0.78), scale=(0.8, 0.5, 1.2))
            m.sphere(r=0.06, seg=6, rings=4, color="white", loc=(s * 0.38 - 0.04, -1.12, 0.86))
        m.torus(R=0.18, r=0.04, seg=8, rseg=4, arc=180, color=dark, rot=(90, 0, 180), loc=(0, -1.08, 0.58))
        if crown:
            for i in range(5):
                a = math.radians(72 * i)
                m.cone(r=0.15, h=0.4, seg=4, color="gold", loc=(math.cos(a) * 0.3, math.sin(a) * 0.3, 1.5), smooth=False)
            m.cyl(r=0.4, h=0.18, seg=10, color="gold", loc=(0, 0, 1.55))


reg("Slime", lambda m: _slime(m), kind="blob", sub="Fantasy", tags=["fantasy"])
reg("KingSlime", lambda m: _slime(m, "potion_blue", "sapphire", crown=True), kind="blob", sub="Fantasy",
    tags=["fantasy"])


def _ghost(m):
    m.bone("Body", (0, 0, 0.6), (0, 0, 2.6))
    m.bone("ArmL", (0.8, 0, 1.6), (1.3, -0.2, 1.2), parent="Body")
    m.bone("ArmR", (-0.8, 0, 1.6), (-1.3, -0.2, 1.2), parent="Body")
    with m.group("Body"):
        prof = [(0, 2.8), (0.55, 2.7), (0.9, 2.3), (1.0, 1.7), (1.02, 1.0), (1.05, 0.6)]
        m.lathe(list(reversed(prof)) + [], seg=16, color="white", caps=True,
                deform=lambda co: co.__class__((co.x, co.y, co.z + (0.12 * math.sin(6 * math.atan2(co.y, co.x))
                                                                     if co.z < 0.62 else 0))))
        for s in (-1, 1):
            m.sphere(r=0.16, seg=8, rings=6, color="black", loc=(s * 0.35, -0.9, 2.05), scale=(0.8, 0.5, 1.3))
        m.sphere(r=0.16, seg=8, rings=6, color="black", loc=(0, -0.95, 1.6), scale=(1.0, 0.5, 1.2))
        m.sphere(r=0.12, seg=6, rings=4, color="pink_nose", loc=(0.62, -0.75, 1.75), scale=(1, 0.4, 0.6), mirror=True)
    for nm, s in (("ArmL", 1), ("ArmR", -1)):
        with m.group(nm):
            m.tube([(s * 0.8, 0, 1.6), (s * 1.3, -0.2, 1.2)], [0.2, 0.12], seg=8, color="white")


reg("Ghost", _ghost, kind="float", sub="Fantasy", tags=["fantasy"])
