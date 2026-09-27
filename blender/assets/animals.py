"""Rigged animals & mythical creatures in the blocky AnimalBundle style.

Chunky chamfered boxes, square pixel eyes, flat shading and the stud overlay.
Every body part is built inside ``with m.group(<bone>)`` so it follows one bone
rigidly; the rig gets Idle / Walk (+ Fly / Swim) actions. Animals face -Y.
None of these duplicate the 115 animals already in AnimalBundle.
"""
import math
import random

from studlib.geo import star_pts
from studlib.registry import add

CAT = "Animals"


def cube(m, size, loc, color, bev=None, **kw):
    b = min(size) * 0.14 if bev is None else bev
    return m.box(size, color=color, bevel=b, loc=loc, **kw)


def patches(m, center, size, col, n=8, seed=1, s=0.22, top=True, sides=True):
    """Pixel-style square patches stuck on the top / side faces of a box."""
    rnd = random.Random(seed)
    W, L, H = size
    cx, cy, cz = center
    faces = (["top"] if top else []) + (["left", "right"] if sides else [])
    for _ in range(n):
        f = rnd.choice(faces)
        w = s * rnd.choice([1.0, 1.0, 1.5, 2.0])
        d = s * rnd.choice([1.0, 1.5])
        if f == "top":
            x = cx + rnd.uniform(-W / 2 + w / 2 + 0.1, W / 2 - w / 2 - 0.1)
            y = cy + rnd.uniform(-L / 2 + d / 2 + 0.12, L / 2 - d / 2 - 0.12)
            cube(m, (w, d, 0.05), (x, y, cz + H / 2 + 0.005), col, bev=0.012)
        else:
            sx = 1 if f == "left" else -1
            y = cy + rnd.uniform(-L / 2 + d / 2 + 0.12, L / 2 - d / 2 - 0.12)
            z = cz + rnd.uniform(-H / 2 + w / 2 + 0.1, H / 2 - w / 2 - 0.1)
            cube(m, (0.05, d, w), (cx + sx * (W / 2 + 0.005), y, z), col, bev=0.012)


def reg(name, fn, kind="quadruped", sub="Pets", tags=()):
    add(name, CAT, fn, sub=sub, rig=kind, tags=list(tags) + ["animal", "rigged"])


# ============================================================================
# four-legged beast template
# ============================================================================
def beast(m, *, W=1.6, L=2.3, H=1.4, leg_h=0.6, leg_w=0.42, body="fur_brown", legc=None, belly=None, paw=None,
          head=(1.5, 1.3, 1.3), head_col=None, head_fwd=0.35, head_up=0.25, neck=0.0,
          muzzle=(0.8, 0.4, 0.5), muzzle_col=None, nose="black", nose_w=0.34,
          eye_r=0.14, eye_x=0.3, eye_z=0.14, ears="square", ear_col=None, ear_in="pink_inner", ear_s=1.0,
          tail="stub", tail_col=None, tail_tip=None, tail_len=1.0, spots=None, cheeks=None, mouth=None,
          extras=None):
    head_col = head_col or body
    ear_col = ear_col or head_col
    tail_col = tail_col or body
    legc = legc or body
    cz = leg_h + H / 2
    hw, hd, hh = head
    fy = -L / 2 - head_fwd
    hy = fy + hd / 2
    hz = cz + H / 2 + head_up + neck
    ty, tz = L / 2, cz + H * 0.25
    d = dict(W=W, L=L, H=H, cz=cz, hy=hy, hz=hz, fy=fy, hw=hw, hd=hd, hh=hh, leg_h=leg_h, ty=ty, tz=tz)

    m.bone("Body", (0, L * 0.3, cz), (0, -L * 0.3, cz))
    m.bone("Head", (0, -L / 2 + 0.2, cz + H / 2 - 0.1), (0, hy, hz + hh / 2), parent="Body")
    lx, ly = W / 2 - leg_w / 2 - 0.04, L / 2 - leg_w / 2 - 0.08
    legs = (("LegFL", 1, -1), ("LegFR", -1, -1), ("LegBL", 1, 1), ("LegBR", -1, 1))
    for nm, sx, sy in legs:
        m.bone(nm, (sx * lx, sy * ly, leg_h + 0.15), (sx * lx, sy * ly, 0.02), parent="Body")
    if tail != "none":
        m.bone("Tail", (0, ty - 0.1, tz), (0, ty + 0.6 * tail_len, tz + 0.5 * tail_len), parent="Body")

    with m.group("Body"):
        cube(m, (W, L, H), (0, 0, cz), body)
        if belly:
            cube(m, (W * 0.74, L * 0.72, 0.06), (0, 0, cz - H / 2 - 0.004), belly, bev=0.02)
            cube(m, (W * 0.58, 0.06, H * 0.55), (0, -L / 2 - 0.004, cz - H * 0.12), belly, bev=0.02)
        if spots:
            col, n, seed = spots
            patches(m, (0, 0, cz), (W, L, H), col, n=n, seed=seed)
    for nm, sx, sy in legs:
        with m.group(nm):
            x, y = sx * lx, sy * ly
            cube(m, (leg_w, leg_w, leg_h + 0.25), (x, y, (leg_h + 0.25) / 2), legc)
            if paw:
                cube(m, (leg_w * 1.08, leg_w * 1.14, max(0.14, leg_h * 0.28)), (x, y - 0.02, max(0.07, leg_h * 0.14)),
                     paw)
    with m.group("Head"):
        if neck > 0:
            nw = min(hw, W) * 0.5
            cube(m, (nw, nw, neck + H * 0.6), (0, fy + hd * 0.55, cz + H / 2 + neck / 2 - H * 0.05), body)
        cube(m, head, (0, hy, hz), head_col)
        m.eye((eye_x * hw, fy - 0.01, hz + eye_z * hh), r=eye_r, mirror=True)
        if muzzle:
            mw, md, mh = muzzle
            mtop = hz - hh / 2 + mh + 0.04
            cube(m, (mw, md, mh), (0, fy - md / 2 + 0.1, hz - hh / 2 + mh / 2 + 0.04), muzzle_col or head_col)
            if nose:
                nh = nose_w * 0.55
                cube(m, (nose_w, 0.14, nh), (0, fy - md + 0.1 - 0.05, mtop - nh / 2 - 0.02), nose, bev=0.03)
            if mouth:
                cube(m, (mw * 0.36, 0.04, 0.05), (0, fy - md + 0.08, hz - hh / 2 + 0.16), mouth, bev=0.01)
        if cheeks:
            cube(m, (0.22, 0.04, 0.14), (hw * 0.36, fy - 0.01, hz - hh * 0.16), cheeks, bev=0.02, mirror=True)
        s = ear_s
        ex, ey, ez = hw * 0.32, hy + hd * 0.12, hz + hh / 2
        if ears == "square":
            cube(m, (hw * 0.26 * s, hd * 0.2, hh * 0.26 * s), (ex, ey, ez + hh * 0.1 * s), ear_col, mirror=True)
            cube(m, (hw * 0.13 * s, 0.04, hh * 0.13 * s), (ex, ey - hd * 0.1 - 0.02, ez + hh * 0.1 * s), ear_in,
                 bev=0.01, mirror=True)
        elif ears == "pointy":
            m.pyramid(w=hw * 0.3 * s, h=hh * 0.5 * s, color=ear_col, loc=(ex, ey, ez - 0.04), scale=(1, 0.55, 1),
                      mirror=True)
            m.pyramid(w=hw * 0.17 * s, h=hh * 0.32 * s, color=ear_in, loc=(ex, ey - hd * 0.09, ez - 0.02),
                      scale=(1, 0.3, 1), mirror=True)
        elif ears == "floppy":
            cube(m, (0.16, hd * 0.45, hh * 0.72 * s), (hw / 2 + 0.06, hy + hd * 0.05, hz - hh * 0.08), ear_col,
                 rot=(0, 8, 0), mirror=True)
        elif ears == "long":
            cube(m, (hw * 0.2 * s, 0.16, hh * 1.05 * s), (hw * 0.24, ey, ez + hh * 0.45 * s), ear_col, mirror=True)
            cube(m, (hw * 0.1 * s, 0.04, hh * 0.8 * s), (hw * 0.24, ey - 0.09, ez + hh * 0.45 * s), ear_in, bev=0.01,
                 mirror=True)
        elif ears == "side":
            cube(m, (0.42 * s, 0.16, 0.24 * s), (hw / 2 + 0.17 * s, hy, hz + hh * 0.2), ear_col, mirror=True)
        elif ears == "tiny":
            cube(m, (0.2 * s, 0.12, 0.16 * s), (ex, ey, ez + 0.06), ear_col, mirror=True)
    if tail != "none":
        with m.group("Tail"):
            tl = tail_len
            tip = tail_tip or tail_col
            if tail == "stub":
                cube(m, (0.32, 0.3, 0.32), (0, ty + 0.1, tz), tail_col)
            elif tail == "long":
                m.tube([(0, ty - 0.1, tz), (0, ty + 0.5 * tl, tz + 0.2 * tl), (0, ty + 0.8 * tl, tz + 0.7 * tl)],
                       [0.12, 0.1, 0.08], seg=8, color=tail_col)
                cube(m, (0.2, 0.2, 0.25), (0, ty + 0.82 * tl, tz + 0.8 * tl), tip)
            elif tail == "fluffy":
                cube(m, (0.36, 0.55, 0.36), (0, ty + 0.18, tz + 0.08), tail_col, rot=(-20, 0, 0))
                cube(m, (0.6, 0.6, 0.6), (0, ty + 0.55 * tl, tz + 0.45 * tl), tail_col, rot=(-35, 0, 0))
                cube(m, (0.52, 0.5, 0.5), (0, ty + 0.72 * tl, tz + 0.95 * tl), tip, rot=(-55, 0, 0))
            elif tail == "curly":
                m.torus(R=0.16, r=0.06, seg=8, arc=300, color=tail_col, rot=(0, 90, 0), loc=(0, ty + 0.16, tz + 0.05))
            elif tail == "flat":
                cube(m, (0.7 * tl, 1.0 * tl, 0.14), (0, ty + 0.5 * tl, cz - H * 0.3), tail_col, rot=(12, 0, 0))
            elif tail == "tuft":
                m.tube([(0, ty - 0.05, tz), (0, ty + 0.2, tz - 0.3 * tl), (0, ty + 0.25, tz - 0.65 * tl)], [0.06] * 3,
                       seg=4, color=tail_col)
                cube(m, (0.2, 0.2, 0.3), (0, ty + 0.25, tz - 0.8 * tl), tip)
            elif tail == "thin":
                m.tube([(0, ty - 0.1, tz), (0, ty + 0.6 * tl, tz - 0.25), (0, ty + 1.2 * tl, tz + 0.05),
                        (0, ty + 1.5 * tl, tz + 0.45)], [0.06, 0.05, 0.04, 0.03], seg=4, color=tail_col)
            elif tail == "ringed":
                for i in range(5):
                    t = i / 4
                    cube(m, (0.36 - 0.05 * t, 0.36, 0.36 - 0.05 * t),
                         (0, ty + 0.1 + 0.55 * tl * t, tz + 0.05 + 0.9 * tl * t * t), tip if i % 2 else tail_col,
                         rot=(-40 * t, 0, 0))
    if extras:
        extras(m, d)
    return d


def spikes_row(m, y0, y1, z_of_y, n, col, w=0.2, h=0.35, x=0.0):
    for i in range(n):
        y = y0 + (y1 - y0) * (i + 0.5) / n
        m.pyramid(w=w, h=h, color=col, loc=(x, y, z_of_y(y)))


# ----------------------------------------------------------------------------
# farm & pets
# ----------------------------------------------------------------------------
def _pig_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            cube(m, (0.12, 0.04, 0.16), (s * 0.15, d["fy"] - 0.38, d["hz"] - d["hh"] / 2 + 0.3), "brick_dark", bev=0.02)


reg("Pig", lambda m: beast(m, W=1.7, L=2.2, H=1.35, leg_h=0.42, body="pig", paw="pig_dark", head=(1.5, 1.25, 1.3),
                           head_fwd=0.25, head_up=0.05, muzzle=(0.75, 0.3, 0.5), muzzle_col="pig_dark", nose=None,
                           ears="pointy", ear_in="pig_dark", tail="curly", cheeks="pink_nose",
                           extras=_pig_extras), sub="Farm")


def _sheep_extras(m, d):
    with m.group("Body"):
        rnd = random.Random(3)
        for i in range(12):
            x = rnd.uniform(-0.55, 0.55)
            y = rnd.uniform(-0.9, 0.9)
            cube(m, (0.55, 0.55, 0.4), (x, y, d["cz"] + d["H"] / 2), "fur_white")
    with m.group("Head"):
        cube(m, (d["hw"] * 1.05, d["hd"] * 0.7, 0.4), (0, d["hy"] + 0.1, d["hz"] + d["hh"] / 2), "fur_white")


reg("Sheep", lambda m: beast(m, W=1.9, L=2.4, H=1.5, leg_h=0.6, leg_w=0.34, body="fur_white", legc="charcoal",
                             head=(1.0, 1.0, 1.1), head_col="charcoal", head_fwd=0.35, head_up=0.1,
                             muzzle=(0.6, 0.25, 0.4), nose="black", nose_w=0.25, ears="side", ear_col="charcoal",
                             tail="stub", tail_col="fur_white", eye_r=0.12, extras=_sheep_extras), sub="Farm")


def _donkey_extras(m, d):
    with m.group("Head"):
        for i in range(4):
            cube(m, (0.14, 0.3, 0.32), (0, d["hy"] + 0.35 + i * 0.22, d["hz"] + d["hh"] * 0.45 - i * 0.28),
                 "fur_darkgray")


reg("Donkey", lambda m: beast(m, W=1.4, L=2.8, H=1.3, leg_h=1.3, leg_w=0.34, body="fur_gray", belly="fur_lightgray",
                              paw="hoof", head=(1.0, 1.5, 1.0), head_fwd=0.7, head_up=0.1, neck=0.7,
                              muzzle=(0.8, 0.35, 0.55), muzzle_col="fur_lightgray", nose="charcoal", nose_w=0.3,
                              ears="long", ear_s=0.8, ear_in="fur_darkgray", tail="tuft", tail_tip="fur_darkgray",
                              extras=_donkey_extras), sub="Farm")


reg("Corgi", lambda m: beast(m, W=1.3, L=2.4, H=1.1, leg_h=0.35, leg_w=0.34, body="fur_orange", belly="fur_white",
                             paw="fur_white", head=(1.3, 1.15, 1.15), head_fwd=0.3, head_up=0.15,
                             muzzle=(0.7, 0.35, 0.45), muzzle_col="fur_white", ears="pointy", ear_s=1.25,
                             ear_in="fur_cream", tail="stub", tail_col="fur_white"), sub="Pets")


reg("Dalmatian", lambda m: beast(m, W=1.2, L=2.4, H=1.2, leg_h=0.9, leg_w=0.34, body="fur_white",
                                 head=(1.15, 1.2, 1.1), head_fwd=0.4, head_up=0.2, muzzle=(0.7, 0.45, 0.45),
                                 ears="floppy", ear_col="black", tail="long", tail_len=0.9,
                                 spots=("black", 12, 4)), sub="Pets")


reg("Husky", lambda m: beast(m, W=1.4, L=2.5, H=1.3, leg_h=0.9, leg_w=0.36, body="fur_gray", belly="fur_white",
                             paw="fur_white", head=(1.3, 1.2, 1.2), head_fwd=0.4, head_up=0.2,
                             muzzle=(0.75, 0.45, 0.45), muzzle_col="fur_white", ears="pointy", ear_s=1.1,
                             ear_in="fur_white", tail="fluffy", tail_len=0.9, tail_tip="fur_white"), sub="Pets")


reg("Mouse", lambda m: beast(m, W=1.0, L=1.4, H=0.85, leg_h=0.18, leg_w=0.24, body="fur_lightgray", belly="fur_white",
                             head=(1.0, 0.9, 0.9), head_fwd=0.3, head_up=-0.1, muzzle=(0.45, 0.3, 0.3),
                             muzzle_col="fur_white", nose="pink_nose", nose_w=0.2, ears="square", ear_s=1.6,
                             ear_in="pink_inner", tail="thin", tail_col="pink_skin", eye_r=0.11), sub="Pets")


def _hedgehog_extras(m, d):
    with m.group("Body"):
        for i in range(5):
            for j in range(4):
                x = -0.55 + j * 0.37
                y = -0.55 + i * 0.3
                m.pyramid(w=0.3, h=0.42, color="fur_darkbrown" if (i + j) % 2 else "fur_brown",
                          loc=(x, y + 0.1, d["cz"] + d["H"] / 2 - 0.05), rot=(-20, 0, 0))
        for s in (-1, 1):
            for i in range(3):
                m.pyramid(w=0.26, h=0.36, color="fur_darkbrown", loc=(s * d["W"] / 2, -0.4 + i * 0.4, d["cz"] + 0.15),
                          rot=(0, s * 70, 0))


reg("Hedgehog", lambda m: beast(m, W=1.5, L=1.7, H=1.0, leg_h=0.18, leg_w=0.26, body="fur_brown", belly="fur_cream",
                                head=(1.0, 0.85, 0.85), head_col="fur_cream", head_fwd=0.3, head_up=-0.3,
                                muzzle=(0.4, 0.35, 0.3), nose="black", nose_w=0.18, ears="tiny", ear_col="fur_tan",
                                tail="none", eye_r=0.1, extras=_hedgehog_extras), sub="Pets")


reg("Squirrel", lambda m: beast(m, W=0.9, L=1.3, H=0.95, leg_h=0.28, leg_w=0.26, body="fur_ginger", belly="fur_cream",
                                head=(0.95, 0.85, 0.85), head_fwd=0.2, head_up=0.1, muzzle=(0.45, 0.25, 0.3),
                                muzzle_col="fur_cream", nose_w=0.18, ears="pointy", ear_s=0.9, tail="fluffy",
                                tail_len=1.25, eye_r=0.11), sub="Pets")


reg("Otter", lambda m: beast(m, W=1.1, L=2.4, H=0.9, leg_h=0.3, leg_w=0.28, body="fur_brown", belly="fur_tan",
                             head=(1.0, 0.9, 0.85), head_fwd=0.35, head_up=0.05, muzzle=(0.6, 0.3, 0.35),
                             muzzle_col="fur_tan", nose_w=0.22, ears="tiny", tail="long", tail_len=1.1,
                             eye_r=0.11), sub="Wild")


def _beaver_extras(m, d):
    with m.group("Head"):
        cube(m, (0.22, 0.06, 0.18), (0, d["fy"] - 0.35, d["hz"] - d["hh"] / 2 + 0.02), "white", bev=0.02)


reg("Beaver", lambda m: beast(m, W=1.5, L=1.9, H=1.3, leg_h=0.25, leg_w=0.32, body="fur_brown", legc="fur_darkbrown",
                              belly="fur_tan", head=(1.2, 1.0, 1.05), head_fwd=0.3, head_up=0.0,
                              muzzle=(0.6, 0.3, 0.35), muzzle_col="fur_tan", nose_w=0.22, ears="tiny",
                              tail="flat", tail_col="bark_dark", extras=_beaver_extras), sub="Wild")


def _skunk_extras(m, d):
    with m.group("Body"):
        cube(m, (0.3, d["L"] * 0.9, 0.06), (0, 0, d["cz"] + d["H"] / 2 + 0.005), "fur_white", bev=0.02)
    with m.group("Head"):
        cube(m, (0.16, 0.06, d["hh"] * 0.55), (0, d["fy"] - 0.01, d["hz"] + d["hh"] * 0.15), "fur_white", bev=0.02)


reg("Skunk", lambda m: beast(m, W=1.2, L=1.8, H=1.0, leg_h=0.3, leg_w=0.28, body="fur_black", head=(1.05, 0.95, 0.95),
                             head_fwd=0.25, head_up=0.0, muzzle=(0.45, 0.3, 0.35), nose_w=0.2, ears="tiny",
                             tail="fluffy", tail_len=1.2, tail_tip="fur_white", extras=_skunk_extras), sub="Wild")


reg("Fox", lambda m: beast(m, W=1.2, L=2.3, H=1.15, leg_h=0.75, leg_w=0.3, body="fur_orange", belly="fur_white",
                           paw="fur_darkbrown", head=(1.2, 1.05, 1.0), head_fwd=0.4, head_up=0.15,
                           muzzle=(0.55, 0.55, 0.4), muzzle_col="fur_white", ears="pointy", ear_s=1.3,
                           ear_in="fur_white", tail="fluffy", tail_len=1.1, tail_tip="fur_white"), sub="Wild")


def _raccoon_extras(m, d):
    with m.group("Head"):
        cube(m, (d["hw"] * 0.9, 0.05, 0.3), (0, d["fy"] - 0.02, d["hz"] + 0.14 * d["hh"]), "fur_black", bev=0.02)


reg("Raccoon", lambda m: beast(m, W=1.3, L=2.0, H=1.15, leg_h=0.45, leg_w=0.3, body="fur_gray", belly="fur_lightgray",
                               paw="fur_black", head=(1.2, 1.0, 1.0), head_fwd=0.3, head_up=0.1,
                               muzzle=(0.5, 0.35, 0.35), muzzle_col="fur_white", nose_w=0.2, ears="pointy",
                               ear_in="fur_white", tail="ringed", tail_col="fur_gray", tail_tip="fur_black",
                               extras=_raccoon_extras), sub="Wild")


def _panda_extras(m, d):
    with m.group("Body"):
        cube(m, (d["W"] * 1.02, d["L"] * 0.32, d["H"] * 1.02), (0, -d["L"] * 0.2, d["cz"]), "fur_black")
    with m.group("Head"):
        cube(m, (0.36, 0.05, 0.4), (d["hw"] * 0.28, d["fy"] - 0.005, d["hz"] + 0.1), "fur_black", bev=0.03, mirror=True)


reg("Panda", lambda m: beast(m, W=1.9, L=2.3, H=1.6, leg_h=0.5, leg_w=0.5, body="fur_white", legc="fur_black",
                             head=(1.7, 1.4, 1.5), head_fwd=0.3, head_up=0.1, muzzle=(0.75, 0.35, 0.45),
                             muzzle_col="fur_white", ears="square", ear_col="fur_black", ear_in="fur_black",
                             tail="stub", eye_r=0.13, extras=_panda_extras), sub="Wild")


def _redpanda_extras(m, d):
    with m.group("Head"):
        cube(m, (0.3, 0.05, 0.18), (d["hw"] * 0.3, d["fy"] - 0.005, d["hz"] + 0.34), "fur_white", bev=0.02, mirror=True)


reg("RedPanda", lambda m: beast(m, W=1.2, L=2.0, H=1.1, leg_h=0.4, leg_w=0.3, body="fur_red", legc="fur_black",
                                head=(1.2, 1.0, 1.0), head_fwd=0.3, head_up=0.1, muzzle=(0.5, 0.3, 0.35),
                                muzzle_col="fur_white", nose_w=0.2, ears="pointy", ear_in="fur_white", tail="ringed",
                                tail_len=1.2, tail_col="fur_red", tail_tip="fur_darkbrown",
                                extras=_redpanda_extras), sub="Wild")


def antlers(m, d, col="antler", big=1.0):
    with m.group("Head"):
        base = (d["hw"] * 0.3, d["hy"] + 0.1, d["hz"] + d["hh"] / 2)
        top = (d["hw"] * 0.3 + 0.55 * big, d["hy"] + 0.3, d["hz"] + d["hh"] / 2 + 1.1 * big)
        m.tube([base, top], [0.08, 0.05], seg=4, color=col, mirror=True)
        for f in (0.45, 0.8):
            p = tuple(b + (t - b) * f for b, t in zip(base, top))
            m.tube([p, (p[0] + 0.05, p[1] - 0.3 * big, p[2] + 0.35 * big)], [0.05, 0.03], seg=4, color=col, mirror=True)


def _deer_extras(m, d):
    with m.group("Body"):
        patches(m, (0, 0, d["cz"]), (d["W"], d["L"], d["H"]), "fur_white", n=7, seed=5, s=0.14, sides=False)


reg("Deer", lambda m: beast(m, W=1.2, L=2.4, H=1.15, leg_h=1.3, leg_w=0.28, body="deer", belly="fur_cream", paw="hoof",
                            head=(0.95, 1.2, 0.9), head_fwd=0.6, head_up=0.1, neck=0.6, muzzle=(0.65, 0.35, 0.4),
                            muzzle_col="fur_cream", nose_w=0.24, ears="pointy", ear_s=1.4, ear_in="fur_cream",
                            tail="stub", tail_col="fur_white", extras=_deer_extras), sub="Wild")


reg("Reindeer", lambda m: beast(m, W=1.5, L=2.8, H=1.4, leg_h=1.3, leg_w=0.34, body="moose", belly="fur_cream",
                                paw="hoof", head=(1.05, 1.3, 1.0), head_fwd=0.6, head_up=0.1, neck=0.5,
                                muzzle=(0.75, 0.4, 0.45), muzzle_col="fur_cream", nose="plastic_red", nose_w=0.34,
                                ears="pointy", ear_in="fur_cream", tail="stub", tail_col="fur_white",
                                extras=lambda m, d: antlers(m, d, big=1.1)), sub="Wild")


reg("Cheetah", lambda m: beast(m, W=1.1, L=2.6, H=1.05, leg_h=1.1, leg_w=0.28, body="fur_gold", belly="fur_cream",
                               head=(1.0, 0.95, 0.9), head_fwd=0.35, head_up=0.1, muzzle=(0.55, 0.3, 0.35),
                               muzzle_col="fur_cream", nose_w=0.22, ears="square", ear_s=0.8, ear_in="fur_black",
                               tail="long", tail_len=1.3, tail_tip="fur_black", spots=("fur_black", 18, 7)), sub="Wild")


def _hippo_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            cube(m, (0.16, 0.06, 0.12), (s * 0.45, d["fy"] - 0.52, d["hz"] - d["hh"] / 2 + 0.88), "charcoal", bev=0.02)


reg("Hippo", lambda m: beast(m, W=2.8, L=3.8, H=2.2, leg_h=0.6, leg_w=0.75, body="hippo", belly="hippo_belly",
                             head=(2.2, 1.8, 1.7), head_fwd=0.6, head_up=-0.3, muzzle=(2.0, 0.6, 0.9),
                             muzzle_col="hippo", nose=None, ears="tiny", ear_s=1.4, tail="stub", eye_r=0.18,
                             cheeks="pink_nose", extras=_hippo_extras), sub="Wild")


def _rhino_extras(m, d):
    with m.group("Head"):
        m.pyramid(w=0.42, h=0.9, color="horn", loc=(0, d["fy"] - 0.45, d["hz"] - d["hh"] / 2 + 0.55), rot=(-15, 0, 0))
        m.pyramid(w=0.28, h=0.45, color="horn", loc=(0, d["fy"] - 0.05, d["hz"] + 0.2), rot=(-10, 0, 0))


reg("Rhino", lambda m: beast(m, W=2.2, L=3.6, H=1.9, leg_h=0.9, leg_w=0.6, body="rhino", head=(1.5, 1.8, 1.3),
                             head_fwd=0.7, head_up=-0.2, muzzle=(1.1, 0.5, 0.7), muzzle_col="rhino", nose=None,
                             ears="pointy", ear_in="rhino", tail="tuft", tail_len=0.8, extras=_rhino_extras),
    sub="Wild")


def _camel_extras(m, d):
    with m.group("Body"):
        for y in (-0.55, 0.55):
            cube(m, (1.0, 1.0, 0.8), (0, y, d["cz"] + d["H"] / 2 + 0.3), "camel")
            cube(m, (0.7, 0.7, 0.35), (0, y, d["cz"] + d["H"] / 2 + 0.8), "camel")


reg("Camel", lambda m: beast(m, W=1.5, L=3.0, H=1.3, leg_h=1.8, leg_w=0.34, body="camel", paw="fur_tan",
                             head=(0.9, 1.4, 0.85), head_fwd=1.1, head_up=0.1, neck=1.2, muzzle=(0.8, 0.4, 0.45),
                             muzzle_col="fur_tan", nose_w=0.24, nose="wood_dark", ears="tiny", tail="tuft",
                             extras=_camel_extras), sub="Wild")


def _axolotl_extras(m, d):
    with m.group("Head"):
        for k, a in enumerate((35, 0, -35)):
            z = d["hz"] + 0.2 - k * 0.2
            cube(m, (0.55, 0.12, 0.12), (d["hw"] / 2 + 0.25, d["hy"] + 0.15, z), "axolotl_gill", rot=(0, a, 0),
                 mirror=True)
        cube(m, (0.4, 0.04, 0.05), (0, d["fy"] - 0.01, d["hz"] - 0.2), "octopus_dark", bev=0.01)


reg("Axolotl", lambda m: beast(m, W=1.2, L=2.1, H=0.8, leg_h=0.22, leg_w=0.24, body="axolotl",
                               head=(1.3, 1.0, 0.8), head_fwd=0.35, head_up=-0.25, muzzle=None, ears="none",
                               tail="long", tail_len=1.2, eye_r=0.11, extras=_axolotl_extras), sub="Sea")


def _walrus_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            cube(m, (0.1, 0.1, 0.7), (s * 0.2, d["fy"] - 0.35, d["hz"] - d["hh"] / 2 - 0.2), "ceramic", bev=0.02)


reg("Walrus", lambda m: beast(m, W=2.2, L=2.8, H=1.8, leg_h=0.25, leg_w=0.55, body="fur_tan", belly="clay",
                              head=(1.6, 1.3, 1.3), head_fwd=0.3, head_up=-0.2, muzzle=(1.1, 0.45, 0.55),
                              muzzle_col="clay", nose=None, ears="none", tail="none", extras=_walrus_extras),
    sub="Sea")


# ----------------------------------------------------------------------------
# mythical four-legged
# ----------------------------------------------------------------------------
reg("Jackalope", lambda m: beast(m, W=1.1, L=1.5, H=1.1, leg_h=0.3, leg_w=0.3, body="fur_tan", belly="fur_white",
                                 head=(1.1, 1.0, 1.0), head_fwd=0.25, head_up=0.15, muzzle=(0.5, 0.25, 0.35),
                                 muzzle_col="fur_white", nose="pink_nose", nose_w=0.2, ears="long", ear_s=0.9,
                                 tail="stub", tail_col="fur_white", extras=lambda m, d: antlers(m, d, big=0.6)),
    sub="Mythical", tags=["mythical"])


def _salamander_extras(m, d):
    with m.group("Body"):
        spikes_row(m, -d["L"] / 2 + 0.2, d["L"] / 2 - 0.1, lambda y: d["cz"] + d["H"] / 2 - 0.02, 5, "fire", w=0.3,
                   h=0.5)
    with m.group("Head"):
        for i, (x, h) in enumerate(((-0.25, 0.45), (0, 0.7), (0.25, 0.45))):
            m.pyramid(w=0.26, h=h, color="fire_light" if i == 1 else "fire", loc=(x, d["hy"] + 0.1, d["hz"] + d["hh"] / 2))
    with m.group("Tail"):
        m.pyramid(w=0.3, h=0.55, color="fire", loc=(0, d["ty"] + 1.05, d["tz"] + 0.75), rot=(-40, 0, 0))


reg("Salamander", lambda m: beast(m, W=1.1, L=2.2, H=0.7, leg_h=0.25, leg_w=0.26, body="lava", belly="fire_light",
                                  head=(1.0, 1.1, 0.7), head_fwd=0.45, head_up=-0.2, muzzle=None, ears="none",
                                  tail="long", tail_len=1.3, tail_col="lava", tail_tip="fire", eye_r=0.1,
                                  spots=("black", 8, 11), extras=_salamander_extras), sub="Mythical",
    tags=["mythical"])


def _frostwolf_extras(m, d):
    with m.group("Body"):
        for i, y in enumerate((-0.8, -0.3, 0.2, 0.7)):
            m.crystal(r=0.14, h=0.6 - 0.08 * i, color="diamond" if i % 2 else "diamond_light",
                      loc=(0, y, d["cz"] + d["H"] / 2 - 0.05), rot=(-15, 0, 0))
    with m.group("Head"):
        m.crystal(r=0.1, h=0.45, color="diamond", loc=(0, d["hy"] + 0.2, d["hz"] + d["hh"] / 2 - 0.02), rot=(-25, 0, 0))


reg("FrostWolf", lambda m: beast(m, W=1.4, L=2.6, H=1.3, leg_h=1.0, leg_w=0.36, body="ice", belly="fur_white",
                                 paw="diamond", head=(1.3, 1.3, 1.15), head_fwd=0.45, head_up=0.2,
                                 muzzle=(0.7, 0.55, 0.45), muzzle_col="fur_white", nose="sapphire", ears="pointy",
                                 ear_s=1.2, ear_col="ice", ear_in="diamond", tail="fluffy", tail_col="ice",
                                 tail_tip="diamond", extras=_frostwolf_extras), sub="Mythical", tags=["mythical"])


def _babydragon_extras(m, d):
    L, W, H, cz = d["L"], d["W"], d["H"], d["cz"]
    m.bone("WingL", (W * 0.4, -L * 0.1, cz + H * 0.4), (W * 1.5, L * 0.1, cz + H * 1.1), parent="Body")
    m.bone("WingR", (-W * 0.4, -L * 0.1, cz + H * 0.4), (-W * 1.5, L * 0.1, cz + H * 1.1), parent="Body")
    with m.group("WingL"):
        s = (W / 2 - 0.05, -0.3, cz + H * 0.35)
        w = (W / 2 + 1.1, -0.1, cz + H + 0.6)
        m.tube([s, w], [0.07, 0.05], seg=4, color="scale_dark", mirror="WingR")
        m.panel([s, w, (W / 2 + 1.3, 0.3, cz + H * 0.4), (W / 2 + 0.5, 0.5, cz + H * 0.3)], 0.05, "amethyst",
                mirror="WingR")
    with m.group("Body"):
        spikes_row(m, -L / 2 + 0.2, L / 2 - 0.2, lambda y: cz + H / 2 - 0.02, 4, "amethyst", w=0.22, h=0.3)
    with m.group("Head"):
        for s in (-1, 1):
            m.pyramid(w=0.2, h=0.5, color="horn", loc=(s * 0.35, d["hy"] + 0.2, d["hz"] + d["hh"] / 2 - 0.02),
                      rot=(-30, 0, 0))


reg("BabyDragon", lambda m: beast(m, W=1.4, L=2.0, H=1.25, leg_h=0.45, leg_w=0.38, body="scale_green", belly="bee",
                                  head=(1.35, 1.25, 1.2), head_fwd=0.35, head_up=0.2, muzzle=(0.8, 0.5, 0.45),
                                  muzzle_col="scale_green", nose=None, ears="none", tail="long", tail_len=1.2,
                                  tail_tip="amethyst", eye_r=0.16, extras=_babydragon_extras),
    kind="dragon", sub="Mythical", tags=["mythical", "fantasy"])


# ============================================================================
# dragons (detailed, faceted like the bundle's CLASSICDRAGON)
# ============================================================================
def dragon(m, *, body="apple_red", belly="peach", dark="ruby_dark", horn="horn", membrane="ruby_dark",
           spike="horn", eye="gold", claw="white", crystals=None):
    cz = 1.55
    L, W, H = 2.6, 1.6, 1.4
    m.bone("Body", (0, 1.0, cz), (0, -1.0, cz + 0.2))
    m.bone("Head", (0, -1.1, cz + 0.6), (0, -2.6, 4.0), parent="Body")
    legs = (("LegFL", 1, -0.85), ("LegFR", -1, -0.85), ("LegBL", 1, 0.85), ("LegBR", -1, 0.85))
    for nm, sx, y in legs:
        m.bone(nm, (sx * 0.62, y, cz), (sx * 0.72, y - 0.2, 0.05), parent="Body")
    m.bone("WingL", (0.7, -0.6, cz + 0.6), (3.2, 0.2, cz + 2.0), parent="Body")
    m.bone("WingR", (-0.7, -0.6, cz + 0.6), (-3.2, 0.2, cz + 2.0), parent="Body")
    m.bone("Tail", (0, 1.2, cz + 0.2), (0, 3.4, cz - 0.4), parent="Body")

    with m.group("Body"):
        cube(m, (W, L, H), (0, 0, cz), body)
        cube(m, (W * 1.05, 1.0, H * 1.05), (0, -0.85, cz + 0.12), body)
        for i in range(5):
            cube(m, (W * 0.75, 0.42, 0.08), (0, -1.0 + i * 0.48, cz - H / 2 - 0.03), belly, bev=0.02)
        for i in range(6):
            y = -1.2 + i * 0.5
            if crystals:
                m.crystal(r=0.16, h=0.7 - abs(i - 2) * 0.08, color=crystals[i % 2], loc=(0, y, cz + H / 2 - 0.05),
                          rot=(-15, 0, 0))
            else:
                m.pyramid(w=0.34, h=0.5 - abs(i - 2) * 0.05, color=spike, loc=(0, y, cz + H / 2 - 0.02), rot=(-20, 0, 0))
    for nm, sx, y in legs:
        with m.group(nm):
            x = sx * 0.62
            cube(m, (0.62, 0.8, 1.0), (x + sx * 0.05, y, cz - 0.15), body, rot=(10 if y < 0 else -10, 0, 0))
            cube(m, (0.44, 0.44, 1.0), (x + sx * 0.08, y - 0.12, 0.6), body)
            cube(m, (0.6, 0.7, 0.24), (x + sx * 0.08, y - 0.28, 0.12), dark)
            for k in (-0.2, 0.0, 0.2):
                m.pyramid(w=0.1, h=0.22, color=claw, loc=(x + sx * 0.08 + k, y - 0.66, 0.1), rot=(90, 0, 0))
    with m.group("Head"):
        pts = [(0, -1.0, cz + 0.5), (0, -1.6, cz + 1.3), (0, -2.0, cz + 2.0)]
        m.tube(pts, [0.5, 0.42, 0.36], seg=8, color=body)
        for i, t in enumerate((0.25, 0.55, 0.85)):
            p = [a + (b - a) * t for a, b in zip(pts[0], pts[2])]
            cube(m, (0.5, 0.16, 0.36), (0, p[1] - 0.32, p[2] - 0.1), belly, rot=(-40, 0, 0), bev=0.03)
        hz, hy = cz + 2.35, -2.3
        cube(m, (1.0, 1.0, 0.8), (0, hy, hz), body)
        cube(m, (0.72, 0.9, 0.42), (0, hy - 0.8, hz - 0.12), body)
        cube(m, (0.62, 0.8, 0.18), (0, hy - 0.7, hz - 0.46), belly, rot=(8, 0, 0))
        for s in (-1, 1):
            for k in range(3):
                m.pyramid(w=0.08, h=0.16, color="white", loc=(s * 0.28, hy - 1.1 + k * 0.2, hz - 0.32), rot=(180, 0, 0))
            cube(m, (0.1, 0.06, 0.1), (s * 0.2, hy - 1.26, hz + 0.02), dark, bev=0.02)
        for s in (-1, 1):
            cube(m, (0.08, 0.28, 0.2), (s * 0.5, hy - 0.2, hz + 0.08), eye, bev=0.02)
            cube(m, (0.09, 0.06, 0.18), (s * 0.505, hy - 0.2, hz + 0.08), "black", bev=0.01)
            cube(m, (0.2, 0.4, 0.14), (s * 0.4, hy - 0.2, hz + 0.3), dark, rot=(0, s * 12, 0))
            m.tube([(s * 0.35, hy + 0.2, hz + 0.3), (s * 0.55, hy + 0.7, hz + 0.6), (s * 0.6, hy + 1.2, hz + 0.6)],
                   [0.14, 0.09, 0.0], seg=4, color=horn)
            m.tube([(s * 0.5, hy + 0.1, hz - 0.05), (s * 0.85, hy + 0.5, hz - 0.1)], [0.08, 0.0], seg=4, color=horn)
        m.pyramid(w=0.2, h=0.35, color=spike, loc=(0, hy + 0.3, hz + 0.38), rot=(-30, 0, 0))
    with m.group("WingL"):
        S = (0.75, -0.7, cz + 0.55)
        E = (1.6, -0.45, cz + 2.0)
        Wr = (2.5, 0.1, cz + 2.9)
        tips = [(3.8, 0.5, cz + 2.3), (3.6, 1.1, cz + 1.3), (2.6, 1.45, cz + 0.6)]
        m.tube([S, E, Wr], [0.13, 0.11, 0.08], seg=4, color=body, mirror="WingR")
        for t in tips:
            m.tube([Wr, t], [0.07, 0.02], seg=4, color=dark, mirror="WingR")
        m.pyramid(w=0.14, h=0.35, color=claw, loc=Wr, rot=(-60, 0, -30), mirror="WingR")
        for i, t in enumerate(tips):
            nxt = tips[i + 1] if i + 1 < len(tips) else (1.0, 0.9, cz + 0.45)
            mid = ((t[0] + nxt[0]) / 2 - 0.25, (t[1] + nxt[1]) / 2 - 0.1, (t[2] + nxt[2]) / 2 + 0.25)
            m.panel([Wr, t, mid, nxt], 0.05, membrane, mirror="WingR")
        m.panel([S, E, Wr, (1.0, 0.9, cz + 0.45)], 0.05, membrane, mirror="WingR")
    with m.group("Tail"):
        tp = [(0, 1.1, cz + 0.1), (0, 2.0, cz - 0.2), (0, 2.8, cz - 0.6), (0, 3.5, cz - 0.7)]
        m.tube(tp, [0.45, 0.34, 0.22, 0.12], seg=8, color=body)
        for i in range(4):
            y = 1.4 + i * 0.5
            z = cz + 0.25 - (y - 1.1) * 0.4
            m.pyramid(w=0.24, h=0.36 - i * 0.05, color=spike if not crystals else crystals[0], loc=(0, y, z),
                      rot=(-30, 0, 0))
        m.panel([(0, 3.4, cz - 0.7), (0.45, 3.8, cz - 0.55), (0, 4.3, cz - 0.7), (-0.45, 3.8, cz - 0.55)], 0.08, dark)


DRAGONS = [
    ("FireDragon", dict(body="apple_red", belly="peach", dark="ruby_dark", membrane="ruby_dark", eye="gold")),
    ("IceDragon", dict(body="ice", belly="white", dark="diamond_dark", horn="diamond_light", membrane="diamond",
                       spike="diamond_light", eye="neon_blue", claw="white")),
    ("ShadowDragon", dict(body="obsidian", belly="amethyst_dark", dark="black", horn="charcoal", membrane="amethyst_dark",
                          spike="amethyst", eye="neon_pink", claw="amethyst")),
    ("CrystalDragon", dict(body="amethyst", belly="crystal_pink", dark="amethyst_dark", horn="crystal_pink",
                           membrane="crystal_pink", eye="glow", crystals=("crystal_pink", "diamond_light"))),
    ("GoldenDragon", dict(body="gold", belly="gold_light", dark="gold_dark", horn="white", membrane="gold_dark",
                          spike="ruby", eye="ruby", claw="white")),
    ("ForestDragon", dict(body="leaf", belly="lime", dark="leaf_deep", horn="wood_light", membrane="leaf_dark",
                          spike="wood_light", eye="gold")),
]
for _n, _kw in DRAGONS:
    reg(_n, (lambda m, kw=_kw: dragon(m, **kw)), kind="dragon", sub="Mythical", tags=["mythical", "dragon"])


# ============================================================================
# birds (cube birds like the bundle's chicken / parrot / owl)
# ============================================================================
def fowl(m, *, body=(1.2, 1.3, 1.2), col="fur_white", belly=None, head=None, head_col=None, neck=0.0,
         beak="wedge", beak_col="beak", beak_len=0.4, comb=None, wattle=None, wing_col=None, tail="wedge",
         tail_col=None, leg_col="beak", leg_h=0.45, eye_r=0.12, extras=None):
    bw, bd, bh = body
    wing_col = wing_col or col
    tail_col = tail_col or wing_col
    head_col = head_col or col
    cz = leg_h + bh / 2
    d = dict(bw=bw, bd=bd, bh=bh, cz=cz)
    m.bone("Body", (0, bd * 0.3, cz), (0, -bd * 0.3, cz))
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        m.bone(nm, (sx * bw * 0.22, 0.05, leg_h + 0.1), (sx * bw * 0.22, 0.05, 0.02), parent="Body")
    for nm, sx in (("WingL", 1), ("WingR", -1)):
        m.bone(nm, (sx * bw / 2, -bd * 0.2, cz + bh * 0.25), (sx * bw * 0.55, bd * 0.4, cz - bh * 0.1), parent="Body")
    m.bone("Tail", (0, bd / 2 - 0.1, cz), (0, bd / 2 + 0.5, cz + 0.4), parent="Body")
    if head:
        hw, hd, hh = head
        hy = -bd / 2 + hd * 0.4
        hz = cz + bh / 2 + neck + hh * 0.35
        fy = hy - hd / 2
        m.bone("Head", (0, hy + 0.1, cz + bh / 2 - 0.1), (0, hy, hz + hh / 2), parent="Body")
    else:
        hw, hd, hh = bw, bd, bh
        hy, hz, fy = 0, cz + bh * 0.12, -bd / 2
    d.update(hy=hy, hz=hz, fy=fy, hw=hw, hh=hh)
    with m.group("Body"):
        cube(m, body, (0, 0, cz), col)
        if belly:
            cube(m, (bw * 0.7, 0.06, bh * 0.6), (0, -bd / 2 - 0.004, cz - bh * 0.15), belly, bev=0.02)
    with m.group("Head" if head else "Body"):
        if head:
            if neck > 0:
                cube(m, (hw * 0.5, hd * 0.5, neck + 0.4), (0, hy + 0.05, cz + bh / 2 + neck / 2), head_col)
            cube(m, head, (0, hy, hz), head_col)
        ez = hz + hh * 0.18
        m.eye((hw * 0.3, fy - 0.01, ez), r=eye_r, mirror=True)
        bz = hz - hh * 0.08
        if beak == "wedge":
            m.pyramid(w=hw * 0.3, h=beak_len, color=beak_col, loc=(0, fy + 0.02, bz), rot=(90, 0, 0))
        elif beak == "flat":
            cube(m, (hw * 0.5, beak_len, 0.16), (0, fy - beak_len / 2 + 0.05, bz), beak_col, bev=0.04)
        elif beak == "big":
            m.tube([(0, fy + 0.05, bz + 0.05), (0, fy - beak_len * 0.6, bz), (0, fy - beak_len, bz - 0.2)],
                   [(0.22, 0.24), (0.18, 0.18), (0.06, 0.06)], seg=4, color=beak_col, up=(0, 0, 1))
            cube(m, (0.12, 0.12, 0.12), (0, fy - beak_len + 0.02, bz - 0.2), "black", bev=0.02)
        elif beak == "hook":
            cube(m, (hw * 0.28, beak_len, 0.22), (0, fy - beak_len / 2 + 0.05, bz), beak_col, bev=0.04)
            cube(m, (hw * 0.2, 0.12, 0.2), (0, fy - beak_len + 0.03, bz - 0.14), beak_col, bev=0.03)
        if comb:
            for y, h in ((-0.15, 0.25), (0.05, 0.35), (0.25, 0.22)):
                cube(m, (0.16, 0.2, h), (0, hy + y - hd * 0.1, hz + hh / 2 + h / 2 - 0.02), comb, bev=0.03)
        if wattle:
            cube(m, (0.16, 0.1, 0.24), (0, fy - 0.06, bz - 0.26), wattle, bev=0.03)
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        with m.group(nm):
            x = sx * bw * 0.22
            cube(m, (0.1, 0.1, leg_h + 0.1), (x, 0.05, (leg_h + 0.1) / 2), leg_col, bev=0.02)
            cube(m, (0.3, 0.38, 0.06), (x, -0.06, 0.03), leg_col, bev=0.02)
    with m.group("WingL"):
        cube(m, (0.14, bd * 0.66, bh * 0.58), (bw / 2 + 0.05, 0.08, cz + 0.02), wing_col, mirror="WingR")
    with m.group("Tail"):
        if tail == "wedge":
            cube(m, (bw * 0.55, 0.4, 0.55), (0, bd / 2 + 0.1, cz + bh * 0.22), tail_col, rot=(-30, 0, 0))
        elif tail == "short":
            cube(m, (bw * 0.4, 0.3, 0.3), (0, bd / 2 + 0.08, cz), tail_col)
    if extras:
        extras(m, d)
    return d


def breg(name, fn, sub="Birds", tags=()):
    reg(name, fn, kind="bird", sub=sub, tags=tags)


def _penguin_belly(m, d):
    with m.group("Body"):
        cube(m, (d["bw"] * 0.8, 0.06, d["bh"] * 0.75), (0, -d["bd"] / 2 - 0.008, d["cz"] - 0.08), "fur_white", bev=0.03)


breg("Duck", lambda m: fowl(m, body=(1.1, 1.5, 1.0), col="fur_white", head=(0.85, 0.85, 0.85), neck=0.15,
                             beak="flat", beak_len=0.45, tail="wedge", leg_h=0.35))
breg("Chick", lambda m: fowl(m, body=(1.0, 1.0, 1.0), col="bee", beak="wedge", beak_len=0.25, comb="beak",
                              tail="short", leg_h=0.25, eye_r=0.1))
breg("Penguin", lambda m: fowl(m, body=(1.3, 1.1, 1.9), col="penguin_black", beak="wedge", beak_len=0.3,
                                tail="short", leg_h=0.12, eye_r=0.11, extras=_penguin_belly))
breg("Flamingo", lambda m: fowl(m, body=(0.9, 1.3, 0.8), col="flamingo", head=(0.5, 0.55, 0.5), neck=1.3,
                                 beak="hook", beak_col="fur_white", beak_len=0.4, tail="short", leg_col="flamingo",
                                 leg_h=2.3, eye_r=0.07))
breg("Toucan", lambda m: fowl(m, body=(0.95, 1.1, 1.2), col="penguin_black", belly="fur_white", beak="big",
                               beak_col="orange", beak_len=1.0, tail="wedge", leg_col="sapphire", leg_h=0.3,
                               eye_r=0.1))
breg("Swan", lambda m: fowl(m, body=(1.1, 1.8, 0.9), col="fur_white", head=(0.5, 0.6, 0.5), neck=1.1, beak="wedge",
                             beak_len=0.35, tail="wedge", leg_col="charcoal", leg_h=0.2, eye_r=0.07))


def _peacock_extras(m, d):
    with m.group("Tail"):
        for i in range(9):
            a = math.radians(-80 + i * 20)
            base = (0, d["bd"] / 2, d["cz"])
            tip = (math.sin(a) * 2.1, d["bd"] / 2 + 0.4, d["cz"] + math.cos(a) * 2.1)
            m.tube([base, tip], [0.06, 0.04], seg=4, color="feather_teal")
            cube(m, (0.5, 0.1, 0.6), tip, "feather_green", rot=(0, -math.degrees(a), 0))
            cube(m, (0.26, 0.06, 0.3), (tip[0], tip[1] - 0.05, tip[2]), "feather_blue", rot=(0, -math.degrees(a), 0),
                 bev=0.02)
            cube(m, (0.12, 0.04, 0.12), (tip[0], tip[1] - 0.08, tip[2]), "gold", rot=(0, -math.degrees(a), 0), bev=0.01)
    with m.group("Head"):
        for i in range(3):
            m.tube([(0, d["hy"], d["hz"] + d["hh"] / 2), (0, d["hy"] + 0.1 * i - 0.1, d["hz"] + d["hh"] / 2 + 0.45)],
                   [0.03, 0.03], seg=4, color="feather_blue")
            cube(m, (0.1, 0.1, 0.1), (0, d["hy"] + 0.1 * i - 0.1, d["hz"] + d["hh"] / 2 + 0.47), "feather_blue",
                 bev=0.02)


breg("Peacock", lambda m: fowl(m, body=(0.95, 1.3, 1.0), col="feather_blue", wing_col="feather_teal",
                                head=(0.55, 0.6, 0.55), neck=0.5, beak="wedge", beak_col="fur_tan", beak_len=0.25,
                                tail="none", leg_col="fur_tan", leg_h=0.5, eye_r=0.07, extras=_peacock_extras))


def _phoenix_extras(m, d):
    with m.group("Tail"):
        for i, a in enumerate((-30, 0, 30)):
            r = math.radians(a)
            m.panel([(0, d["bd"] / 2 - 0.1, d["cz"] + 0.1), (math.sin(r) * 0.5, d["bd"] / 2 + 1.0, d["cz"] + 0.6),
                     (math.sin(r) * 0.2, d["bd"] / 2 + 1.3, d["cz"] + 1.1)], 0.06, "fire" if i != 1 else "fire_light")
    with m.group("Body"):
        for i, (x, h) in enumerate(((-0.2, 0.35), (0, 0.55), (0.2, 0.35))):
            m.pyramid(w=0.2, h=h, color="fire_light" if i == 1 else "fire", loc=(x, -0.1, d["cz"] + d["bh"] / 2 - 0.02))


breg("PhoenixChick", lambda m: fowl(m, body=(1.0, 1.0, 1.0), col="lava", wing_col="fire", beak="wedge",
                                     beak_col="gold", beak_len=0.3, tail="none", leg_col="gold", leg_h=0.3,
                                     extras=_phoenix_extras), sub="Mythical", tags=["mythical"])


# ============================================================================
# fish & sea
# ============================================================================
def fin_yz(m, pts_yz, depth, color, loc, **kw):
    m.prism([(-z, y) for y, z in pts_yz], depth=depth, color=color, rot=kw.pop("rot", (0, 90, 0)), loc=loc, **kw)


def fishy(m, *, W=0.7, L=1.7, H=1.2, col="fish_orange", belly=None, fin=None, stripes=None, stripe_col="white",
          eye_r=0.13):
    fin = fin or col
    cz = H / 2 + 0.15
    m.bone("Body", (0, L * 0.1, cz), (0, -L * 0.45, cz))
    m.bone("Tail", (0, L * 0.35, cz), (0, L * 0.5 + 0.6, cz), parent="Body")
    m.bone("FinL", (W / 2, -L * 0.1, cz - H * 0.1), (W / 2 + 0.4, L * 0.05, cz - H * 0.25), parent="Body")
    m.bone("FinR", (-W / 2, -L * 0.1, cz - H * 0.1), (-W / 2 - 0.4, L * 0.05, cz - H * 0.25), parent="Body")
    with m.group("Body"):
        kw = {}
        if stripes:
            def c(cc, n):
                for y0, y1 in stripes:
                    if y0 < cc.y < y1:
                        return stripe_col
                return col
            kw["cuts"] = {"y": [v for pair in stripes for v in pair]}
        else:
            c = col
        cube(m, (W, L, H), (0, 0, cz), c, **kw)
        cube(m, (W * 0.8, 0.3, H * 0.7), (0, -L / 2 - 0.1, cz - H * 0.05), col)
        if belly:
            cube(m, (W * 0.7, L * 0.7, 0.06), (0, 0, cz - H / 2 - 0.004), belly, bev=0.02)
        fin_yz(m, [(-0.3 * L, 0), (0.3 * L, 0), (0.15 * L, 0.45 * H)], 0.08, fin, (0, 0, cz + H / 2 - 0.02))
        m.eye((W / 2 + 0.01, -L * 0.25, cz + H * 0.15), r=eye_r, look=(1, 0, 0), mirror=True)
        cube(m, (W * 0.45, 0.06, 0.1), (0, -L / 2 - 0.26, cz - H * 0.15), "black", bev=0.02)
    with m.group("Tail"):
        fin_yz(m, [(0, 0), (0.5 * L * 0.55, 0.5 * H), (0.38 * L * 0.55, 0), (0.5 * L * 0.55, -0.5 * H)], 0.08, fin,
               (0, L / 2 - 0.05, cz))
    with m.group("FinL"):
        cube(m, (0.4, 0.45, 0.08), (W / 2 + 0.18, -L * 0.02, cz - H * 0.2), fin, rot=(0, -25, 0), mirror="FinR")


reg("Clownfish", lambda m: fishy(m, W=0.7, L=1.6, H=1.0, col="fish_orange",
                                 stripes=[(-0.62, -0.46), (-0.08, 0.1), (0.52, 0.68)]), kind="fish", sub="Sea")
reg("Bluefish", lambda m: fishy(m, W=0.55, L=1.8, H=1.4, col="sapphire", fin="bee", belly="bee"), kind="fish",
    sub="Sea")


def cetacean(m, *, col="dolphin", belly="dolphin_belly", snout=True, dorsal=0.8, spot=None):
    cz = 0.9
    m.bone("Body", (0, 0.4, cz), (0, -1.6, cz))
    m.bone("Tail", (0, 0.9, cz), (0, 2.6, cz), parent="Body")
    m.bone("FinL", (0.6, -0.8, cz - 0.3), (1.2, -0.5, cz - 0.6), parent="Body")
    m.bone("FinR", (-0.6, -0.8, cz - 0.3), (-1.2, -0.5, cz - 0.6), parent="Body")
    with m.group("Body"):
        cube(m, (1.3, 2.2, 1.25), (0, -0.2, cz), col)
        cube(m, (1.1, 0.9, 1.05), (0, -1.6, cz - 0.02), col)
        cube(m, (1.0, 1.7, 0.06), (0, -0.5, cz - 0.64), belly, bev=0.02)
        if snout:
            cube(m, (0.5, 0.6, 0.35), (0, -2.3, cz - 0.25), col)
        fin_yz(m, [(-0.35, 0), (0.45, 0), (0.35, dorsal)], 0.12, col, (0, 0.0, cz + 0.6))
        m.eye((0.56, -1.7, cz + 0.12), r=0.11, look=(1, 0, 0), mirror=True)
        if spot:
            cube(m, (0.06, 0.5, 0.3), (0.57, -1.3, cz + 0.3), spot, bev=0.02, mirror=True)
    with m.group("Tail"):
        cube(m, (0.9, 0.9, 0.85), (0, 1.3, cz - 0.02), col)
        cube(m, (0.55, 0.8, 0.5), (0, 2.0, cz - 0.05), col)
        m.prism([(0, 0), (0.3, 0.15), (0.85, 0.5), (0.55, 0.55), (0, 0.3), (-0.55, 0.55), (-0.85, 0.5), (-0.3, 0.15)],
                depth=0.1, color=col, loc=(0, 2.35, cz - 0.05))
    with m.group("FinL"):
        cube(m, (0.7, 0.35, 0.08), (0.9, -0.7, cz - 0.45), col, rot=(0, -25, 15), mirror="FinR")


reg("Dolphin", lambda m: cetacean(m), kind="sea", sub="Sea")
reg("Orca", lambda m: cetacean(m, col="penguin_black", belly="fur_white", snout=False, dorsal=1.2, spot="fur_white"),
    kind="sea", sub="Sea")


def _octopus(m):
    m.bone("Body", (0, 0, 0.6), (0, 0, 2.6))
    with m.group("Body"):
        cube(m, (1.7, 1.6, 1.8), (0, 0, 1.55), "octopus")
        cube(m, (1.4, 1.3, 0.35), (0, 0, 2.5), "octopus")
        m.eye((0.38, -0.81, 1.35), r=0.18, mirror=True)
        patches(m, (0, 0, 1.55), (1.7, 1.6, 1.8), "octopus_dark", n=6, seed=2, s=0.18)
    for i in range(8):
        a = math.radians(45 * i + 22.5)
        c, s = math.cos(a), math.sin(a)
        nm = f"Tentacle{i + 1}"
        m.bone(nm, (c * 0.5, s * 0.5, 0.7), (c * 1.8, s * 1.8, 0.2), parent="Body")
        with m.group(nm):
            m.tube([(c * 0.45, s * 0.45, 0.8), (c * 1.0, s * 1.0, 0.25), (c * 1.6, s * 1.6, 0.18), (c * 2.0, s * 2.0, 0.4),
                    (c * 1.9, s * 1.9, 0.62)], [0.2, 0.16, 0.12, 0.08, 0.04], seg=8, color="octopus")


reg("Octopus", _octopus, kind="float", sub="Sea")


def _starfish(m):
    m.bone("Body", (0, 0, 0.1), (0, -0.8, 0.1))
    with m.group("Body"):
        m.prism(star_pts(1.3, 0.5, 5), depth=0.35, color="plastic_orange", bevel=0.05, loc=(0, 0, 0.2))
        for i in range(5):
            a = math.radians(90 + 72 * i)
            for k in (0.45, 0.75):
                cube(m, (0.1, 0.1, 0.06), (math.cos(a) * 1.2 * k, math.sin(a) * 1.2 * k, 0.39), "peach", bev=0.02)
        for s in (-1, 1):
            cube(m, (0.2, 0.2, 0.06), (s * 0.18, -0.15, 0.4), "eye_black", bev=0.02)
            cube(m, (0.08, 0.08, 0.04), (s * 0.18 + 0.05, -0.2, 0.44), "eye_white", bev=0.01)


reg("Starfish", _starfish, kind="blob", sub="Sea")


def _seaserpent(m):
    pts = [(0, -3.0, 2.2), (0, -2.8, 1.4), (0, -2.0, 0.6), (0, -1.0, 0.4), (0, 0.0, 1.0), (0, 1.0, 1.3), (0, 2.0, 0.7),
           (0, 3.0, 0.4), (0, 3.9, 0.5)]
    m.bone("Body", (0, 0.2, 1.0), (0, -2.2, 0.6))
    m.bone("Head", (0, -2.6, 1.2), (0, -3.2, 2.8), parent="Body")
    m.bone("Tail", (0, 0.5, 1.2), (0, 3.9, 0.5), parent="Body")
    with m.group("Body"):
        m.tube(pts[1:6], [0.42, 0.5, 0.55, 0.52, 0.48], seg=8, color="sapphire")
        for i in range(4):
            p = pts[2 + i]
            fin_yz(m, [(-0.3, 0), (0.35, 0), (0.25, 0.5)], 0.08, "potion_blue", (0, p[1], p[2] + 0.55))
    with m.group("Tail"):
        m.tube(pts[5:], [0.48, 0.4, 0.28, 0.1], seg=8, color="sapphire")
        m.prism([(0, 0), (0.6, 0.5), (0, 0.9), (-0.6, 0.5)], depth=0.08, color="potion_blue", loc=(0, 3.8, 0.5),
                rot=(0, 90, 0))
    with m.group("Head"):
        cube(m, (0.9, 1.1, 0.8), (0, -3.1, 2.4), "sapphire")
        cube(m, (0.7, 0.6, 0.4), (0, -3.85, 2.25), "sapphire")
        cube(m, (0.6, 0.55, 0.14), (0, -3.8, 1.98), "dolphin_belly")
        m.eye((0.46, -3.3, 2.55), r=0.12, look=(1, -0.4, 0), mirror=True)
        for s in (-1, 1):
            m.tube([(s * 0.3, -2.8, 2.8), (s * 0.5, -2.3, 3.3)], [0.1, 0.0], seg=4, color="diamond_light")


reg("SeaSerpent", _seaserpent, kind="sea", sub="Mythical", tags=["mythical"])


def _basilisk(m):
    pts = [(0, -1.6, 0.9), (0, -0.6, 0.35), (0.6, 0.5, 0.3), (-0.4, 1.6, 0.3), (0.3, 2.6, 0.25), (0, 3.4, 0.2)]
    m.bone("Body", (0, 0.2, 0.4), (0, -1.4, 0.8))
    m.bone("Head", (0, -1.5, 0.9), (0, -2.6, 2.0), parent="Body")
    m.bone("Tail", (0, 0.8, 0.3), (0, 3.4, 0.2), parent="Body")
    with m.group("Body"):
        m.tube(pts[:4], [0.4, 0.45, 0.42, 0.38], seg=8, color=lambda c, n: "bee" if n.z < -0.5 else "scale_green")
    with m.group("Tail"):
        m.tube(pts[3:], [0.38, 0.26, 0.08], seg=8, color="scale_green")
    with m.group("Head"):
        m.tube([(0, -1.6, 0.9), (0, -1.9, 1.6)], [0.4, 0.36], seg=8, color="scale_green")
        cube(m, (1.0, 1.1, 0.7), (0, -2.1, 1.95), "scale_green")
        cube(m, (0.75, 0.55, 0.35), (0, -2.8, 1.85), "scale_green")
        m.eye((0.51, -2.2, 2.05), r=0.13, look=(1, -0.3, 0), color="gold", mirror=True)
        cube(m, (0.04, 0.06, 0.2), (0.53, -2.18, 2.05), "black", bev=0.01, mirror=True)
        for s in (-1, 1):
            m.pyramid(w=0.08, h=0.25, color="white", loc=(s * 0.22, -3.0, 1.7), rot=(180, 0, 0))
        for i, a in enumerate((-50, -25, 0, 25, 50)):
            r = math.radians(a)
            m.panel([(0, -1.9, 2.25), (math.sin(r) * 0.7, -1.7, 2.3 + math.cos(r) * 0.8),
                     (math.sin(r) * 0.9, -1.5, 2.2 + math.cos(r) * 0.4)], 0.05, "ruby" if i % 2 else "gold")
        for i in range(3):
            m.pyramid(w=0.22, h=0.4, color="gold", loc=(-0.3 + i * 0.3, -1.9, 2.3), rot=(-20, 0, 0))


reg("Basilisk", _basilisk, kind="fish", sub="Mythical", tags=["mythical"])


# ============================================================================
# bugs
# ============================================================================
def _bee(m):
    cz = 1.0
    m.bone("Body", (0, 0.5, cz), (0, -0.6, cz))
    m.bone("WingL", (0.25, -0.1, cz + 0.45), (1.1, 0.2, cz + 0.9), parent="Body")
    m.bone("WingR", (-0.25, -0.1, cz + 0.45), (-1.1, 0.2, cz + 0.9), parent="Body")
    with m.group("Body"):
        cube(m, (1.2, 1.5, 1.2), (0, 0.2, cz), lambda c, n: "black" if int((c.y + 5) / 0.3) % 2 else "bee",
             cuts={"y": 0.3})
        cube(m, (0.95, 0.8, 0.95), (0, -0.85, cz + 0.05), "black")
        m.eye((0.25, -1.26, cz + 0.12), r=0.13, mirror=True)
        m.pyramid(w=0.2, h=0.35, color="black", loc=(0, 0.95, cz - 0.05), rot=(-90, 0, 0))
        for s in (-1, 1):
            m.tube([(s * 0.2, -1.0, cz + 0.45), (s * 0.35, -1.2, cz + 0.85)], [0.035, 0.035], seg=4, color="black")
            cube(m, (0.12, 0.12, 0.12), (s * 0.35, -1.2, cz + 0.88), "black", bev=0.02)
    with m.group("WingL"):
        cube(m, (1.0, 0.6, 0.05), (0.75, 0.1, cz + 0.75), "glass", rot=(0, -25, -15), bev=0.02, mirror="WingR")


reg("Bee", _bee, kind="bug", sub="Bugs")


def _ladybug(m):
    cz = 0.5
    m.bone("Body", (0, 0.6, cz), (0, -0.8, cz))
    m.bone("WingL", (0.05, -0.5, cz + 0.4), (0.4, 0.8, cz + 0.4), parent="Body")
    m.bone("WingR", (-0.05, -0.5, cz + 0.4), (-0.4, 0.8, cz + 0.4), parent="Body")
    with m.group("Body"):
        cube(m, (1.6, 1.9, 0.5), (0, 0, cz - 0.1), "black")
        cube(m, (0.9, 0.6, 0.6), (0, -1.1, cz), "black")
        m.eye((0.22, -1.41, cz + 0.08), r=0.1, color="eye_white", shine=False, mirror=True)
        cube(m, (0.08, 0.05, 0.08), (0.24, -1.44, cz + 0.06), "black", bev=0.01, mirror=True)
        for i in range(3):
            m.tube([(0.7, -0.5 + i * 0.5, cz - 0.2), (1.0, -0.6 + i * 0.55, 0.03)], [0.05, 0.04], seg=4, color="black",
                   mirror=True)
    with m.group("WingL"):
        cube(m, (0.82, 1.9, 0.5), (0.42, 0.05, cz + 0.35), "ladybug", mirror="WingR")
        for x, y in ((0.42, -0.5), (0.55, 0.3), (0.3, 0.65)):
            cube(m, (0.26, 0.26, 0.05), (x, y, cz + 0.61), "black", bev=0.02, mirror="WingR")


reg("Ladybug", _ladybug, kind="bug", sub="Bugs")


def _butterfly(m):
    cz = 1.2
    m.bone("Body", (0, 0.6, cz), (0, -0.6, cz))
    m.bone("WingL", (0.1, 0, cz), (1.5, 0, cz + 0.4), parent="Body")
    m.bone("WingR", (-0.1, 0, cz), (-1.5, 0, cz + 0.4), parent="Body")
    with m.group("Body"):
        cube(m, (0.26, 1.4, 0.26), (0, 0.1, cz), "charcoal")
        cube(m, (0.4, 0.4, 0.4), (0, -0.75, cz + 0.05), "charcoal")
        m.eye((0.12, -0.96, cz + 0.1), r=0.07, mirror=True)
        for s in (-1, 1):
            m.tube([(s * 0.08, -0.9, cz + 0.2), (s * 0.3, -1.2, cz + 0.8)], [0.025, 0.025], seg=4, color="charcoal")
            cube(m, (0.08, 0.08, 0.08), (s * 0.3, -1.2, cz + 0.82), "charcoal", bev=0.01)
    with m.group("WingL"):
        m.panel([(0.12, -0.2, cz), (1.5, -1.0, cz + 0.2), (1.8, -0.4, cz + 0.25), (1.3, 0.1, cz + 0.15)], 0.04,
                "butterfly_blue", mirror="WingR")
        m.panel([(0.12, 0.1, cz), (1.2, 0.3, cz + 0.12), (1.1, 1.0, cz + 0.1), (0.4, 0.9, cz + 0.05)], 0.04,
                "butterfly_orange", mirror="WingR")
        cube(m, (0.28, 0.28, 0.05), (1.3, -0.5, cz + 0.22), "white", bev=0.02, rot=(0, -8, 0), mirror="WingR")
        cube(m, (0.2, 0.2, 0.05), (0.8, 0.6, cz + 0.12), "black", bev=0.02, mirror="WingR")


reg("Butterfly", _butterfly, kind="bug", sub="Bugs")


def _fairy(m):
    m.bone("Body", (0, 0, 0.6), (0, 0, 1.8))
    m.bone("WingL", (0.2, 0.2, 1.4), (1.1, 0.5, 2.0), parent="Body")
    m.bone("WingR", (-0.2, 0.2, 1.4), (-1.1, 0.5, 2.0), parent="Body")
    with m.group("Body"):
        cube(m, (0.6, 0.45, 0.8), (0, 0, 0.9), "leaf_light")
        m.pyramid(w=0.8, h=0.7, color="leaf", loc=(0, 0, 0.8), rot=(180, 0, 0), scale=(1, 0.8, 1))
        cube(m, (0.7, 0.65, 0.65), (0, 0, 1.65), "pink_skin")
        cube(m, (0.78, 0.72, 0.3), (0, 0.05, 2.0), "autumn_yellow")
        m.eye((0.15, -0.34, 1.7), r=0.07, mirror=True)
        cube(m, (0.1, 0.04, 0.06), (0.25, -0.33, 1.55), "pink_nose", bev=0.01, mirror=True)
        m.tube([(0.35, 0, 1.1), (0.55, -0.2, 0.9)], [0.06, 0.05], seg=4, color="pink_skin", mirror=True)
        m.tube([(0.5, -0.2, 0.9), (0.6, -0.25, 1.5)], [0.02, 0.02], seg=4, color="wood_light")
        m.prism(star_pts(0.14, 0.06, 5), depth=0.05, color="glow", rot=(90, 0, 0), loc=(0.6, -0.26, 1.55))
    with m.group("WingL"):
        m.panel([(0.2, 0.25, 1.4), (1.0, 0.45, 2.1), (1.1, 0.5, 1.6)], 0.03, "glass", mirror="WingR")
        m.panel([(0.2, 0.25, 1.3), (0.8, 0.4, 0.9), (0.5, 0.35, 0.7)], 0.03, "crystal_pink", mirror="WingR")


reg("Fairy", _fairy, kind="bug", sub="Mythical", tags=["mythical"])


# ============================================================================
# bipeds: monkey, meerkat, yeti, golems, treant
# ============================================================================
def biped(m, *, body=(1.3, 0.9, 1.4), col="fur_brown", belly=None, head=(1.2, 1.05, 1.05), head_col=None,
          face=None, face_size=(0.8, 0.6), leg=(0.42, 0.5), arm=(0.34, 1.2), hand=None, arm_col=None,
          ears="round", ear_col=None, eye_r=0.12, eye_col="eye_black", muzzle=None, extras=None, tail=None):
    bw, bd, bh = body
    lw, lh = leg
    aw, al = arm
    head_col = head_col or col
    ear_col = ear_col or col
    arm_col = arm_col or col
    hand = hand or face or col
    cz = lh + bh / 2
    hw, hd, hh = head
    hz = lh + bh + hh / 2 - 0.05
    fy = -hd / 2
    d = dict(bw=bw, bd=bd, bh=bh, cz=cz, hz=hz, hw=hw, hd=hd, hh=hh, fy=fy, lh=lh)
    m.bone("Body", (0, 0, lh), (0, 0, lh + bh))
    m.bone("Head", (0, 0, lh + bh - 0.1), (0, 0, hz + hh / 2), parent="Body")
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        m.bone(nm, (sx * bw * 0.25, 0, lh + 0.1), (sx * bw * 0.25, 0, 0.02), parent="Body")
    for nm, sx in (("ArmL", 1), ("ArmR", -1)):
        m.bone(nm, (sx * (bw / 2 + aw / 2), 0, lh + bh - 0.15), (sx * (bw / 2 + aw / 2), -0.05, lh + bh - al),
               parent="Body")
    with m.group("Body"):
        cube(m, body, (0, 0, cz), col)
        if belly:
            cube(m, (bw * 0.65, 0.06, bh * 0.65), (0, -bd / 2 - 0.004, cz - bh * 0.05), belly, bev=0.03)
    with m.group("Head"):
        cube(m, head, (0, 0, hz), head_col)
        if face:
            fw, fh = face_size
            cube(m, (hw * fw, 0.08, hh * fh), (0, fy - 0.01, hz - hh * (1 - fh) / 2 + 0.02), face, bev=0.03)
        m.eye((hw * 0.24, fy - 0.05, hz + hh * 0.12), r=eye_r, color=eye_col, mirror=True)
        if muzzle:
            mw, md, mh = muzzle
            cube(m, (mw, md, mh), (0, fy - md / 2, hz - hh * 0.22), face or head_col)
            cube(m, (mw * 0.35, 0.08, mh * 0.3), (0, fy - md - 0.01, hz - hh * 0.22 + mh * 0.2), "black", bev=0.02)
        if ears == "round":
            cube(m, (0.14, hd * 0.35, hh * 0.35), (hw / 2 + 0.06, 0, hz + 0.05), ear_col, mirror=True)
            cube(m, (0.04, hd * 0.2, hh * 0.2), (hw / 2 + 0.13, -0.02, hz + 0.05), face or ear_col, bev=0.01, mirror=True)
        elif ears == "small":
            cube(m, (0.1, 0.16, 0.18), (hw / 2 + 0.04, 0, hz + hh * 0.25), ear_col, bev=0.02, mirror=True)
    for nm, sx in (("LegL", 1), ("LegR", -1)):
        with m.group(nm):
            cube(m, (lw, lw * 1.05, lh + 0.2), (sx * bw * 0.25, 0, (lh + 0.2) / 2), col)
            cube(m, (lw * 1.05, lw * 1.35, 0.16), (sx * bw * 0.25, -0.08, 0.08), hand)
    for nm, sx in (("ArmL", 1), ("ArmR", -1)):
        with m.group(nm):
            x = sx * (bw / 2 + aw / 2 + 0.02)
            top = lh + bh - 0.05
            cube(m, (aw, aw, al), (x, 0, top - al / 2), arm_col)
            cube(m, (aw * 1.1, aw * 1.1, aw * 0.9), (x, -0.02, top - al), hand)
    if tail:
        m.bone("Tail", (0, bd / 2, lh + 0.3), (0, bd / 2 + 1.0, lh + 1.2), parent="Body")
        with m.group("Tail"):
            tail(m, d)
    if extras:
        extras(m, d)
    return d


def _monkey_tail(m, d):
    m.tube([(0, d["bd"] / 2, d["lh"] + 0.3), (0, d["bd"] / 2 + 0.6, d["lh"] + 0.2), (0, d["bd"] / 2 + 1.0, d["lh"] + 0.8),
            (0, d["bd"] / 2 + 0.8, d["lh"] + 1.3)], [0.08, 0.07, 0.06, 0.05], seg=4, color="fur_brown")


reg("Monkey", lambda m: biped(m, body=(1.2, 0.85, 1.3), col="fur_brown", belly="fur_tan", head=(1.2, 1.0, 1.05),
                               face="fur_tan", face_size=(0.8, 0.72), leg=(0.36, 0.45), arm=(0.3, 1.35),
                               muzzle=(0.6, 0.25, 0.35), ears="round", tail=_monkey_tail), kind="biped", sub="Wild")


def _meerkat_extras(m, d):
    with m.group("Head"):
        cube(m, (0.26, 0.05, 0.34), (d["hw"] * 0.24, d["fy"] - 0.02, d["hz"] + 0.1), "fur_darkbrown", bev=0.02,
             mirror=True)


def _meerkat_tail(m, d):
    m.tube([(0, d["bd"] / 2, d["lh"] + 0.2), (0, d["bd"] / 2 + 0.6, 0.12), (0, d["bd"] / 2 + 1.1, 0.1)],
           [0.08, 0.06, 0.03], seg=4, color="fur_tan")


reg("Meerkat", lambda m: biped(m, body=(0.9, 0.75, 1.8), col="fur_tan", belly="fur_cream", head=(0.85, 0.8, 0.8),
                                leg=(0.3, 0.35), arm=(0.24, 0.8), muzzle=(0.45, 0.35, 0.3), ears="small",
                                ear_col="fur_darkbrown", eye_r=0.1, extras=_meerkat_extras, tail=_meerkat_tail),
    kind="biped", sub="Wild")


def _yeti_extras(m, d):
    with m.group("Head"):
        for s in (-1, 1):
            m.tube([(s * 0.5, 0.1, d["hz"] + 0.4), (s * 0.85, 0.2, d["hz"] + 0.75)], [0.12, 0.0], seg=4, color="horn")
        for i in range(5):
            cube(m, (0.3, 0.3, 0.3), (-0.6 + i * 0.3, 0.1, d["hz"] + d["hh"] / 2), "fur_white")
    with m.group("Body"):
        for i in range(6):
            cube(m, (0.35, 0.35, 0.35), ((-1) ** i * 0.55, -0.2 + (i // 2) * 0.3, d["cz"] - 0.2 + (i % 3) * 0.4),
                 "fur_white")


reg("Yeti", lambda m: biped(m, body=(2.0, 1.4, 2.0), col="fur_white", belly="ice", head=(1.5, 1.3, 1.35),
                             face="tile_blue", face_size=(0.72, 0.7), leg=(0.6, 0.8), arm=(0.55, 2.0), hand="tile_blue",
                             ears="none", eye_r=0.13, muzzle=(0.55, 0.2, 0.3), extras=_yeti_extras),
    kind="biped", sub="Mythical", tags=["mythical"])


def golem(m, stone="stone", dark="stone_dark", eye="glow", accent="moss", crystal=None, lava=False):
    def extras(m, d):
        with m.group("Head"):
            cube(m, (d["hw"] * 1.02, 0.16, 0.22), (0, d["fy"] - 0.02, d["hz"] + 0.34), dark, bev=0.04)
        with m.group("Body"):
            cube(m, (0.5, 0.06, 0.5), (0, -d["bd"] / 2 - 0.01, d["cz"] + 0.3), eye, bev=0.03)
            cube(m, (0.2, 0.08, 0.2), (0, -d["bd"] / 2 - 0.03, d["cz"] + 0.3), "white", bev=0.02)
            if crystal:
                for i, (x, y, r) in enumerate(((0.8, 0.3, -20), (-0.8, 0.3, 20), (0.3, 0.6, -10), (-0.4, 0.55, 15))):
                    m.crystal(r=0.22, h=1.1 - 0.15 * i, color=crystal[i % 2],
                              loc=(x, y, d["cz"] + d["bh"] / 2 - 0.1), rot=(20, r, 0))
            elif lava:
                for i in range(5):
                    cube(m, (0.06, 0.07, 0.6), (-0.7 + i * 0.35, -d["bd"] / 2 - 0.01, d["cz"] - 0.2 + (i % 2) * 0.3),
                         "lava", bev=0.01, rot=(0, 25 * (-1) ** i, 0))
            else:
                patches(m, (0, 0, d["cz"]), (d["bw"], d["bd"], d["bh"]), accent, n=8, seed=4, s=0.3, sides=True)
        for nm, sx in (("ArmL", 1), ("ArmR", -1)):
            with m.group(nm):
                x = sx * (d["bw"] / 2 + 0.34)
                cube(m, (0.9, 0.9, 0.8), (x, 0, d["lh"] + d["bh"] - 0.2), dark)
    return biped(m, body=(2.2, 1.4, 2.0), col=stone, head=(1.1, 1.0, 1.0), leg=(0.7, 0.7), arm=(0.62, 2.1),
                 hand=dark, ears="none", eye_col=eye, eye_r=0.13, extras=extras)


reg("StoneGolem", lambda m: golem(m), kind="biped", sub="Mythical", tags=["mythical"])
reg("CrystalGolem", lambda m: golem(m, stone="stone_light", dark="stone", eye="neon_pink",
                                    crystal=("amethyst", "crystal_pink")), kind="biped", sub="Mythical",
    tags=["mythical"])
reg("LavaGolem", lambda m: golem(m, stone="obsidian", dark="coal", eye="fire", lava=True), kind="biped",
    sub="Mythical", tags=["mythical"])


def _treant_extras(m, d):
    with m.group("Head"):
        rnd = random.Random(9)
        for i in range(9):
            x, y = rnd.uniform(-0.9, 0.9), rnd.uniform(-0.6, 0.7)
            s = rnd.uniform(0.7, 1.0)
            cube(m, (s, s, s), (x, y, d["hz"] + d["hh"] / 2 + 0.2 + rnd.uniform(0, 0.5)),
                 "leaf" if i % 3 else "leaf_dark")
        cube(m, (0.5, 0.06, 0.12), (0, d["fy"] - 0.02, d["hz"] - 0.3), "bark_dark", bev=0.02)
    for nm, sx in (("ArmL", 1), ("ArmR", -1)):
        with m.group(nm):
            x = sx * (d["bw"] / 2 + 0.25)
            base = (x, 0, d["lh"] + d["bh"] - 1.5)
            for dx, dz in ((0.35, -0.3), (0.1, -0.45), (-0.15, -0.35)):
                m.tube([base, (x + sx * dx, -0.1, base[2] + dz)], [0.08, 0.03], seg=4, color="bark")
            cube(m, (0.5, 0.5, 0.5), (x + sx * 0.2, 0.1, d["lh"] + d["bh"] - 0.1), "leaf")


reg("Treant", lambda m: biped(m, body=(1.5, 1.2, 2.6), col="bark", head=(1.4, 1.2, 1.1), head_col="bark",
                               leg=(0.55, 0.6), arm=(0.4, 1.6), hand="bark_dark", ears="none", eye_col="neon_green",
                               eye_r=0.13, extras=_treant_extras), kind="biped", sub="Mythical", tags=["mythical"])


# ============================================================================
# blobs & spooky
# ============================================================================
def _slime(m, col="slime", dark="leaf_dark", crown=False):
    m.bone("Body", (0, 0, 0.05), (0, 0, 1.6))
    with m.group("Body"):
        m.box((2.2, 2.0, 1.6), color=col, bevel=0.45, loc=(0, 0, 0.8))
        cube(m, (0.35, 0.05, 0.5), (-0.6, -1.01, 1.15), "white", bev=0.02)
        m.eye((0.4, -1.0, 0.95), r=0.17, mirror=True)
        cube(m, (0.4, 0.05, 0.08), (0, -1.0, 0.6), dark, bev=0.02)
        if crown:
            cube(m, (0.9, 0.9, 0.25), (0, 0, 1.72), "gold")
            for i in range(4):
                for s in (-1, 1):
                    m.pyramid(w=0.18, h=0.35, color="gold", loc=(s * 0.36, -0.36 + i * 0.24, 1.84))
            m.gem(r=0.12, h=0.12, seg=6, color="ruby", rot=(90, 0, 0), loc=(0, -0.46, 1.72))


reg("Slime", lambda m: _slime(m), kind="blob", sub="Mythical", tags=["fantasy"])
reg("KingSlime", lambda m: _slime(m, "potion_blue", "sapphire", crown=True), kind="blob", sub="Mythical",
    tags=["fantasy"])


def _ghost(m):
    m.bone("Body", (0, 0, 0.6), (0, 0, 2.6))
    m.bone("ArmL", (0.9, 0, 1.7), (1.4, -0.2, 1.3), parent="Body")
    m.bone("ArmR", (-0.9, 0, 1.7), (-1.4, -0.2, 1.3), parent="Body")
    with m.group("Body"):
        cube(m, (1.8, 1.6, 2.0), (0, 0, 1.6), "white")
        for i in range(4):
            for j in range(3):
                m.pyramid(w=0.4, h=0.35, color="white", loc=(-0.66 + i * 0.44, -0.5 + j * 0.5, 0.62), rot=(180, 0, 0))
        cube(m, (0.3, 0.05, 0.42), (0.35, -0.81, 1.85), "black", bev=0.03, mirror=True)
        cube(m, (0.4, 0.05, 0.3), (0, -0.81, 1.35), "black", bev=0.04)
        cube(m, (0.26, 0.04, 0.12), (0.62, -0.81, 1.5), "pink_nose", bev=0.02, mirror=True)
    with m.group("ArmL"):
        cube(m, (0.6, 0.4, 0.4), (1.1, -0.1, 1.5), "white", rot=(0, 25, 0), mirror="ArmR")


reg("Ghost", _ghost, kind="float", sub="Mythical", tags=["fantasy"])


def _mimic(m):
    m.bone("Body", (0, 0, 0.1), (0, 0, 1.3))
    m.bone("Head", (0, 0.9, 1.35), (0, -0.9, 2.2), parent="Body")
    with m.group("Body"):
        cube(m, (2.4, 1.8, 1.3), (0, 0, 0.75), "wood_mid")
        for x in (-1.0, 1.0):
            cube(m, (0.2, 1.86, 1.34), (x, 0, 0.75), "gold", bev=0.03)
        cube(m, (1.7, 1.2, 0.3), (0, 0.0, 1.3), "tongue")
        m.tube([(0, 0.2, 1.4), (0, -0.6, 1.55), (0, -1.3, 1.2)], [(0.35, 0.08), (0.3, 0.07), (0.2, 0.05)], seg=4,
               color="axolotl_gill", up=(0, 0, 1))
        for i in range(6):
            m.pyramid(w=0.18, h=0.3, color="white", loc=(-0.9 + i * 0.36, -0.82, 1.38))
        for s in (-1, 1):
            for i in range(3):
                m.pyramid(w=0.16, h=0.26, color="white", loc=(s * 1.08, -0.6 + i * 0.5, 1.38))
    with m.group("Head"):
        cube(m, (2.4, 1.8, 0.55), (0, 0.35, 2.05), "wood_mid", rot=(-35, 0, 0))
        for x in (-1.0, 1.0):
            cube(m, (0.2, 1.86, 0.6), (x, 0.35, 2.05), "gold", bev=0.03, rot=(-35, 0, 0))
        for i in range(6):
            m.pyramid(w=0.18, h=0.3, color="white", loc=(-0.9 + i * 0.36, -0.5, 1.4), rot=(145, 0, 0))
        m.eye((0.5, -0.46, 2.2), r=0.16, color="gold", mirror=True)
        cube(m, (0.08, 0.05, 0.26), (0.5, -0.5, 2.2), "black", bev=0.01, mirror=True)


reg("Mimic", _mimic, kind="blob", sub="Mythical", tags=["mythical"])
