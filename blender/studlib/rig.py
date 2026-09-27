"""Rig animals: armature from the Builder's bones, rigid skinning per body part,
and procedural Idle / Walk / Fly / Swim actions (30 fps, seamless loops).

Every face was built inside ``with m.group(<bone>)`` so each body part follows
exactly one bone (weight 1.0) -- clean low-poly deformation that imports into
Roblox as a skinned MeshPart with Bones.
"""
import math

import bpy
import numpy as np
from mathutils import Quaternion, Vector

FPS = 30


def rig(ob, bones, groups, kind, collection):
    name = ob.name
    off = Vector(ob["origin_offset"])
    ob.name = name + "Mesh"
    ob.data.name = name + "Mesh"
    arm_data = bpy.data.armatures.new(name + "Rig")
    arm_data.display_type = "STICK"
    arm = bpy.data.objects.new(name, arm_data)
    collection.objects.link(arm)
    arm["rig_kind"] = kind

    if "Root" not in bones:
        top = max(b["head"].z for b in bones.values()) if bones else 1.0
        bones = dict(Root=dict(head=off.copy(), tail=off + Vector((0, 0, max(0.3, top * 0.25))), parent=None),
                     **bones)
    for b in bones.values():
        if b["parent"] is None and b is not bones["Root"]:
            b["parent"] = "Root"

    view = bpy.context.view_layer
    view.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}

    def make(n):
        if n in made:
            return made[n]
        b = bones[n]
        if b["parent"]:
            make(b["parent"])
        eb = arm_data.edit_bones.new(n)
        eb.head = b["head"] - off
        eb.tail = b["tail"] - off
        if (eb.tail - eb.head).length < 1e-3:
            eb.tail = eb.head + Vector((0, 0, 0.2))
        if b["parent"]:
            eb.parent = made[b["parent"]]
        eb.use_connect = False
        made[n] = eb
        return eb

    for n in bones:
        make(n)
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.select_set(False)

    # rigid skin weights from the per-face group index
    me = ob.data
    npoly = len(me.polygons)
    grp = np.zeros(npoly, np.int32)
    me.attributes["grp"].data.foreach_get("value", grp)
    starts = np.zeros(npoly, np.int32)
    totals = np.zeros(npoly, np.int32)
    me.polygons.foreach_get("loop_start", starts)
    me.polygons.foreach_get("loop_total", totals)
    loop_vert = np.zeros(len(me.loops), np.int32)
    me.loops.foreach_get("vertex_index", loop_vert)
    vert_grp = np.zeros(len(me.vertices), np.int32)
    loop_grp = np.repeat(grp, totals)
    vert_grp[loop_vert] = loop_grp
    for gi, gname in enumerate(groups):
        target = gname if gname in bones else "Root"
        idx = np.nonzero(vert_grp == gi)[0].tolist()
        if not idx:
            continue
        vg = ob.vertex_groups.get(target) or ob.vertex_groups.new(name=target)
        vg.add(idx, 1.0, "REPLACE")
    for attr in ("grp", "pal"):
        if attr in me.attributes:
            me.attributes.remove(me.attributes[attr])

    ob.parent = arm
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm

    animate(arm, kind)
    return arm


# ---------------------------------------------------------------------------
def _key(arm, pb, frame, rot=None, loc=None, scale=None):
    rest = pb.bone.matrix_local.to_quaternion()
    if rot is not None:
        axis, deg = rot
        q = Quaternion(Vector(axis), math.radians(deg))
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = rest.inverted() @ q @ rest
        pb.keyframe_insert("rotation_quaternion", frame=frame)
    if loc is not None:
        pb.location = rest.inverted() @ Vector(loc)
        pb.keyframe_insert("location", frame=frame)
    if scale is not None:
        pb.scale = scale
        pb.keyframe_insert("scale", frame=frame)


def _side(name):
    """+1 for left (+X) parts, -1 for right."""
    n = name.upper()
    if n.endswith("L") or "FL" in n or "BL" in n:
        return 1
    return -1


def _motion(kind, clip, bname, t, pos):
    """Return dict(rot=(axis, deg), loc=vec, scale=vec) for bone at phase t in [0,1)."""
    s = math.sin(2 * math.pi * t)
    s2 = math.sin(4 * math.pi * t)
    c = math.cos(2 * math.pi * t)
    out = {}
    walk = clip in ("Walk", "Swim")
    fly = clip == "Fly"
    if bname == "Body":
        if kind == "blob":
            k = 0.1 * (s2 if walk else s)
            out["scale"] = (1 + k * 0.6, 1 + k * 0.6, 1 - k)
            if walk:
                out["loc"] = (0, 0, abs(s) * 0.6)
        elif kind == "fish":
            out["rot"] = ((0, 0, 1), (8 if walk else 4) * s)
        elif kind == "float":
            out["loc"] = (0, 0, 0.15 * s)
        elif fly:
            out["loc"] = (0, 0, 0.12 * s2)
        elif walk:
            out["loc"] = (0, 0, 0.05 * abs(s2))
            if kind == "bird":
                out["rot"] = ((0, 1, 0), 6 * s)
        else:
            out["loc"] = (0, 0, 0.025 * s)
    elif bname == "Head":
        if walk:
            out["rot"] = ((1, 0, 0), 4 * s2)
        elif not fly:
            out["rot"] = ((0, 0, 1), 12 * s)
    elif bname.startswith("Leg"):
        if kind in ("fish", "blob", "float"):
            return out
        amp = 26 if kind == "quadruped" else 30
        if kind == "bug":
            amp = 12
        if bname in ("LegFL", "LegBR", "LegL"):
            ph = 0.0
        else:
            ph = 0.5
        if walk:
            out["rot"] = ((1, 0, 0), amp * math.sin(2 * math.pi * (t + ph)))
        elif fly and kind == "bird":
            out["rot"] = ((1, 0, 0), -35)
    elif bname.startswith("Arm") and not bname[3:].isdigit():
        ph = 0.5 if bname == "ArmL" else 0.0
        if walk:
            out["rot"] = ((1, 0, 0), 30 * math.sin(2 * math.pi * (t + ph)))
        else:
            out["rot"] = ((0, 1, 0), -_side(bname) * 6 * (1 + s))
    elif bname.startswith("Wing"):
        sd = _side(bname)
        if fly:
            amp = 55 if kind != "bug" else 45
            speed = 1 if kind != "bug" else 3
            out["rot"] = ((0, 1, 0), -sd * amp * math.sin(2 * math.pi * t * speed))
        else:
            amp = 8 if kind != "bug" else 30
            speed = 1 if kind != "bug" else 3
            out["rot"] = ((0, 1, 0), -sd * amp * (0.5 + 0.5 * math.sin(2 * math.pi * t * speed)))
    elif bname.startswith("Fin"):
        sd = _side(bname)
        out["rot"] = ((0, 1, 0), -sd * (18 if walk else 10) * s)
    elif bname.startswith("Tail"):
        if kind == "fish":
            out["rot"] = ((0, 0, 1), -(28 if walk else 14) * s)
        elif kind == "sea":
            out["rot"] = ((1, 0, 0), (20 if walk else 10) * s)
        else:
            out["rot"] = ((0, 0, 1), (22 if walk else 14) * (s2 if walk else s))
    elif bname.startswith("Arm") or bname.startswith("Tentacle"):
        idx = int("".join(ch for ch in bname if ch.isdigit()) or 0)
        out["rot"] = ((1, 0, 0), (18 if walk else 10) * math.sin(2 * math.pi * (t + idx / 8)))
    elif bname.startswith("Ear"):
        out["rot"] = ((0, 1, 0), _side(bname) * 6 * max(0.0, math.sin(2 * math.pi * t * 2)) ** 4)
    return out


def animate(arm, kind):
    clips = {"Idle": 60, "Walk": 30}
    if kind in ("fish", "sea"):
        clips = {"Idle": 60, "Swim": 40}
    if kind in ("bird", "bug", "dragon"):
        clips["Fly"] = 24
    if kind == "dragon":
        kind_m = "quadruped"
    else:
        kind_m = kind
    arm.animation_data_create()
    actions = []
    for clip, n in clips.items():
        act = bpy.data.actions.new(f"{arm.name}_{clip}")
        act.use_fake_user = True
        arm.animation_data.action = act
        step = 3
        for f in range(0, n + 1, step):
            t = (f % n) / n
            for pb in arm.pose.bones:
                mo = _motion(kind_m, clip, pb.name, t, pb.bone.head_local)
                if mo:
                    _key(arm, pb, f + 1, rot=mo.get("rot"), loc=mo.get("loc"), scale=mo.get("scale"))
        for fc in _fcurves(act):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
        act["frames"] = n
        actions.append(act)
        for pb in arm.pose.bones:
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.location = (0, 0, 0)
            pb.scale = (1, 1, 1)
    arm.animation_data.action = actions[0]
    arm["clips"] = list(clips.keys())
    return actions


def _fcurves(act):
    try:
        return list(act.fcurves)
    except AttributeError:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out.extend(bag.fcurves)
        return out
