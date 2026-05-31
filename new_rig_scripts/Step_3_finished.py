import bpy
from mathutils import Vector


ARMATURE_NAME = "Armature"

arm = bpy.data.objects[ARMATURE_NAME]
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
edit_bones = arm.data.edit_bones


def side_chain(side, names):
    return [f"{name}_{side}" for name in names]


def process_chain(chain, connected=False):
    for bone_name, next_bone_name in zip(chain, chain[1:]):
        bone = edit_bones[bone_name]
        next_bone = edit_bones[next_bone_name]
        bone.tail = next_bone.head
        if connected:
            next_bone.use_connect = True
            next_bone.parent = bone


def copy_position(src_bone_name, dst_bone_name, src_part="tail", dst_part="tail"):
    src = edit_bones.get(src_bone_name)
    dst = edit_bones.get(dst_bone_name)

    if not src:
        print(f"⚠️ Origen no encontrado: {src_bone_name}")
        return
    if not dst:
        print(f"⚠️ Destino no encontrado: {dst_bone_name}")
        return

    source_value = src.tail.copy() if src_part == "tail" else src.head.copy()

    if dst_part == "tail":
        dst.tail = source_value
    else:
        dst.head = source_value


def move_head_keep_length(src_bone_name, dst_bone_name):
    src = edit_bones.get(src_bone_name)
    dst = edit_bones.get(dst_bone_name)

    if not src:
        print(f"⚠️ Origen no encontrado: {src_bone_name}")
        return
    if not dst:
        print(f"⚠️ Destino no encontrado: {dst_bone_name}")
        return

    length = (dst.tail - dst.head).length
    if length == 0:
        print(f"⚠️ {dst_bone_name} tiene longitud cero.")
        return

    direction = src.tail - src.head
    if direction.length == 0:
        print(f"⚠️ {src_bone_name} no tiene dirección válida.")
        return

    direction.normalize()
    dst.head = src.head.copy()
    dst.tail = dst.head + direction * length


def move_tail_local(bone_name, delta):
    bone = edit_bones.get(bone_name)
    if not bone:
        print(f"⚠️ Hueso no encontrado: {bone_name}")
        return

    bone_matrix = bone.matrix.to_3x3()
    bone.tail += bone_matrix @ delta


CHAIN_CONNECTED = {
    "boob_R": side_chain("R", [
        "cf_s_bust00", "cf_s_bust01", "cf_s_bust02", "cf_s_bust03",
        "cf_s_bnip01", "cf_s_bnip015", "cf_s_bnip025", "cf_j_bnip02",
    ]),
    "boob_L": side_chain("L", [
        "cf_s_bust00", "cf_s_bust01", "cf_s_bust02", "cf_s_bust03",
        "cf_s_bnip01", "cf_s_bnip015", "cf_s_bnip025", "cf_j_bnip02",
    ]),
    "siri_R": side_chain("R", [
        "cf_d_siri", "cf_d_siri01", "cf_j_siri", "cf_s_siri",
    ]),
    "siri_L": side_chain("L", [
        "cf_d_siri", "cf_d_siri01", "cf_j_siri", "cf_s_siri",
    ]),
}

CHAIN_LOOSE = {
    "arm_R": side_chain("R", [
        "cf_s_shoulder02", "cf_s_arm01", "cf_s_arm02", "cf_s_arm03",
        "cf_s_forearm01", "cf_s_forearm02", "cf_s_wrist", "cf_d_hand", "cf_s_hand",
    ]),
    "arm_L": side_chain("L", [
        "cf_s_shoulder02", "cf_s_arm01", "cf_s_arm02", "cf_s_arm03",
        "cf_s_forearm01", "cf_s_forearm02", "cf_s_wrist", "cf_d_hand", "cf_s_hand",
    ]),
    "ctrl_arm_R": side_chain("R", [
        "cf_j_arm00", "cf_j_forearm01", "cf_j_hand",
    ]),
    "ctrl_arm_L": side_chain("L", [
        "cf_j_arm00", "cf_j_forearm01", "cf_j_hand",
    ]),
    "leg_R": side_chain("R", [
        "cf_j_thigh00", "cf_j_leg01", "cf_j_foot",
    ]),
    "leg_L": side_chain("L", [
        "cf_j_thigh00", "cf_j_leg01", "cf_j_foot",
    ]),
    "spine": [
        "cf_j_hips", "cf_j_spine01", "cf_j_spine02",
        "cf_j_spine03", "cf_j_neck", "cf_j_head",
    ],
    "spine_s": [
        "cf_s_spine01", "cf_s_spine02", "cf_s_spine03", "cf_s_neck",
    ],
    "waist": [
        "cf_j_waist01", "cf_j_waist02",
    ],
    "waist_s": [
        "cf_s_waist01", "cf_s_waist02",
    ],
}


FINGER_ROOTS = ["cf_j_little01_", "cf_j_ring01_", "cf_j_middle01_", "cf_j_index01_"]
FINGER_NEXTS = ["cf_j_little02_", "cf_j_ring02_", "cf_j_middle02_", "cf_j_index02_"]

DELTA_Z = Vector((0, 0, 0.001))
DELTA_THUMB = {
    "R": Vector((-0.001, -0.001, 0)),
    "L": Vector((-0.001,  0.001, 0)),
}


for chain in CHAIN_CONNECTED.values():
    process_chain(chain, connected=True)

for chain in CHAIN_LOOSE.values():
    process_chain(chain)


for side in ("R", "L"):
    siri = edit_bones[f"cf_d_siri_{side}"]
    siri01 = edit_bones[f"cf_d_siri01_{side}"]
    hand = edit_bones[f"cf_j_hand_{side}"]
    support_hand = edit_bones[f"cf_s_hand_{side}"]

    siri.head = edit_bones["cf_j_waist02"].tail.copy()
    siri.tail = siri01.head.copy()

    hand.tail[2] = hand.head[2]
    hand.tail[1] = hand.head[1]
    hand.tail[0] = support_hand.tail[0]
    hand.length = 0.03
    hand.parent = None

    copy_position(f"cf_j_leg01_{side}", f"cf_s_leg02_{side}", "tail", "tail")

    copy_position(f"cf_s_thigh03_{side}", f"cf_s_thigh02_{side}", "head", "tail")
    copy_position(f"cf_j_thigh00_{side}", f"cf_s_thigh03_{side}", "tail", "tail")
    copy_position(f"cf_s_thigh02_{side}", f"cf_s_thigh01_{side}", "head", "tail")
    copy_position(f"cf_s_thigh01_{side}", f"cf_j_thigh00_{side}", "head", "head")
    move_head_keep_length(f"cf_s_thigh01_{side}", f"cf_d_thigh01_{side}")

    for root in FINGER_ROOTS:
        move_tail_local(root + side, DELTA_Z)

    move_tail_local(f"cf_j_thumb01_{side}", DELTA_THUMB[side])

    for root, nxt in zip(FINGER_ROOTS, FINGER_NEXTS):
        copy_position(root + side, nxt + side, "tail", "head")

    copy_position(f"cf_j_thumb01_{side}", f"cf_j_thumb02_{side}", "tail", "head")


edit_bones["cf_J_Vagina_root"].length = 0.03

fix_y_spine = edit_bones["cf_s_spine02"].head[1]
edit_bones["cf_j_spine02"].head[1] = fix_y_spine
edit_bones["cf_j_spine01"].tail[1] = fix_y_spine

copy_position("cf_s_waist01", "cf_j_waist01", "head", "head")
copy_position("cf_s_spine01", "cf_j_spine01", "head", "head")

bpy.ops.object.mode_set(mode="OBJECT")
