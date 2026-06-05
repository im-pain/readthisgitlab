import bpy
from mathutils import Vector
import mathutils

# --------------------------
# Preparar Armature
# --------------------------
arm = bpy.data.objects["Armature"]
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')

# --------------------------
# Creación de huesos Ctrl y Pole (genéricos)
# --------------------------
def create_ctrl_bone(arm, src_name, ctrl_name, parent_name, length=0.01):
    ebones = arm.data.edit_bones
    if src_name not in ebones:
        print(f"[create_ctrl_bone] Hueso fuente no encontrado: {src_name}")
        return
    src = ebones[src_name]
    if ctrl_name in ebones:
        print(f"[create_ctrl_bone] Hueso de control ya existe: {ctrl_name}")
        return
    new_bone = ebones.new(ctrl_name)
    new_bone.head = src.head.copy()
    new_bone.tail = src.head + (src.tail - src.head).normalized() * length
    new_bone.roll = src.roll
    if parent_name in ebones:
        new_bone.parent = ebones[parent_name]
        new_bone.use_connect = False

def create_pole_bone(arm, src_name, pole_name, parent_name, offset_vec, length=0.01):
    ebones = arm.data.edit_bones
    if src_name not in ebones:
        print(f"[create_pole_bone] Hueso fuente no encontrado: {src_name}")
        return
    src = ebones[src_name]
    if pole_name in ebones:
        print(f"[create_pole_bone] Hueso Pole ya existe: {pole_name}")
        return
    new_bone = ebones.new(pole_name)
    new_bone.head = src.head + offset_vec
    new_bone.tail = new_bone.head + (src.tail - src.head).normalized() * length
    new_bone.roll = src.roll
    if parent_name and parent_name in ebones:
        new_bone.parent = ebones[parent_name]
        new_bone.use_connect = False

# --------------------------
# Arm Pole
# --------------------------
def create_arm_pole(arm, src_name, pole_name, offset=0.4, length=0.1):
    ebones = arm.data.edit_bones
    if src_name not in ebones:
        print(f"[create_arm_pole] Hueso fuente no encontrado: {src_name}")
        return
    src = ebones[src_name]
    if pole_name in ebones:
        print(f"[create_arm_pole] Hueso Arm Pole ya existe: {pole_name}")
        return
    offset_vec = Vector((0, offset, 0))
    new_bone = ebones.new(pole_name)
    new_bone.head = src.tail + offset_vec
    new_bone.tail = new_bone.head + Vector((0, length, 0))
    new_bone.roll = 0.0
    new_bone.parent = None

# --------------------------
# Thigh Pole
# --------------------------
def create_thigh_pole(arm, src_name, pole_name, offset=-0.4, length=0.1):
    ebones = arm.data.edit_bones
    if src_name not in ebones:
        print(f"[create_thigh_pole] Hueso fuente no encontrado: {src_name}")
        return
    src = ebones[src_name]
    if pole_name in ebones:
        print(f"[create_thigh_pole] Hueso Thigh Pole ya existe: {pole_name}")
        return
    offset_vec = Vector((0, offset, 0))
    new_bone = ebones.new(pole_name)
    new_bone.head = src.tail + offset_vec
    new_bone.tail = new_bone.head + Vector((0, -length, 0))
    new_bone.roll = 0.0
    new_bone.parent = None

# --------------------------
# Foot Ctrl
# --------------------------
def create_foot_ctrl(arm, src_name, ctrl_name, parent_name, length=0.13):
    ebones = arm.data.edit_bones
    if src_name not in ebones:
        print(f"[create_foot_ctrl] Hueso fuente no encontrado: {src_name}")
        return
    src = ebones[src_name]
    if ctrl_name in ebones:
        print(f"[create_foot_ctrl] Hueso ya existe: {ctrl_name}")
        return
    new_bone = ebones.new(ctrl_name)
    new_bone.head = src.head.copy()
    dir_vec = (src.tail - src.head)
    if dir_vec.length == 0:
        dir_vec = Vector((0, 1, 0))
    new_bone.tail = new_bone.head + dir_vec.normalized() * length
    new_bone.roll = 0.0
    if parent_name in ebones:
        new_bone.parent = ebones[parent_name]
        new_bone.use_connect = False

# --------------------------
# Alineación de dirección sin cambiar roll
# --------------------------
def align_bone_direction_to_source(arm, src_name, target_name):
    ebones = arm.data.edit_bones
    if src_name not in ebones:
        print(f"[align] Hueso fuente no encontrado: {src_name}")
        return
    if target_name not in ebones:
        print(f"[align] Hueso objetivo no encontrado: {target_name}")
        return
    src = ebones[src_name]
    tgt = ebones[target_name]
    dir_vec = (src.tail - src.head)
    if dir_vec.length == 0:
        print(f"[align] Dirección inválida en fuente {src_name} (longitud 0).")
        return
    dir_norm = dir_vec.normalized()
    tgt_length = (tgt.tail - tgt.head).length
    tgt.head = src.head.copy()
    tgt.tail = tgt.head + dir_norm * (tgt_length if tgt_length > 0 else 0.01)

def reparent_bone_keep_offset(arm, bone_name, new_parent_name):
    ebones = arm.data.edit_bones
    if bone_name not in ebones:
        print(f"[reparent] Hueso no encontrado: {bone_name}")
        return
    if new_parent_name not in ebones:
        print(f"[reparent] Nuevo padre no encontrado: {new_parent_name}")
        return
    bone = ebones[bone_name]
    bone.parent = ebones[new_parent_name]
    bone.use_connect = False

# --------------------------
# Eye Ctrl bones
# --------------------------
def create_eye_ctrl_bone(arm, src_bone_name, new_bone_name, offset_y=-0.15, length=0.01):
    ebones = arm.data.edit_bones

    if src_bone_name not in ebones:
        print(f"⚠️ No se encontró el hueso {src_bone_name}")
        return None

    src_bone = ebones[src_bone_name]
    base_pos = src_bone.tail.copy()
    base_pos.y += offset_y
    direction = mathutils.Vector((0.0, -1.0, 0.0))

    if new_bone_name in ebones:
        print(f"⚠️ El hueso {new_bone_name} ya existe, se omite.")
        return ebones[new_bone_name]

    new_bone = ebones.new(new_bone_name)
    new_bone.head = base_pos
    new_bone.tail = base_pos + direction * length
    new_bone.use_connect = False
    new_bone.parent = None

    print(f"✅ Creado hueso {new_bone_name} desde {src_bone_name}")
    return new_bone

# ==================================================
# STEP_04
# ==================================================

right_bones = {
    "cf_j_little03_R": "cf_j_little_Ctrl_R",
    "cf_j_ring03_R":   "cf_j_ring_Ctrl_R",
    "cf_j_middle03_R": "cf_j_middle_Ctrl_R",
    "cf_j_index03_R":  "cf_j_index_Ctrl_R",
    "cf_j_thumb03_R":  "cf_j_thumb_Ctrl_R",
}
left_bones = {
    "cf_j_little03_L": "cf_j_little_Ctrl_L",
    "cf_j_ring03_L":   "cf_j_ring_Ctrl_L",
    "cf_j_middle03_L": "cf_j_middle_Ctrl_L",
    "cf_j_index03_L":  "cf_j_index_Ctrl_L",
    "cf_j_thumb03_L":  "cf_j_thumb_Ctrl_L",
}

for src, ctrl in right_bones.items():
    create_ctrl_bone(arm, src, ctrl, "cf_s_hand_R")
for src, ctrl in left_bones.items():
    create_ctrl_bone(arm, src, ctrl, "cf_s_hand_L")

create_pole_bone(arm, "cf_j_little02_R", "cf_j_little_Pole_R", "cf_s_hand_R", Vector((0, 0, 0.025)))
create_pole_bone(arm, "cf_j_ring02_R",   "cf_j_ring_Pole_R",   "cf_s_hand_R", Vector((0, 0, 0.025)))
create_pole_bone(arm, "cf_j_middle02_R", "cf_j_middle_Pole_R", "cf_s_hand_R", Vector((0, 0, 0.025)))
create_pole_bone(arm, "cf_j_index02_R",  "cf_j_index_Pole_R",  "cf_s_hand_R", Vector((0, 0, 0.025)))
src_thumb_R = arm.data.edit_bones.get("cf_j_thumb02_R")
if src_thumb_R:
    x_axis_R = (src_thumb_R.tail - src_thumb_R.head).normalized().cross(Vector((0, 0, 1))).normalized()
    create_pole_bone(arm, "cf_j_thumb02_R", "cf_j_thumb_Pole_R", "cf_s_hand_R", x_axis_R * -0.025)

create_pole_bone(arm, "cf_j_little02_L", "cf_j_little_Pole_L", "cf_s_hand_L", Vector((0, 0, 0.025)))
create_pole_bone(arm, "cf_j_ring02_L",   "cf_j_ring_Pole_L",   "cf_s_hand_L", Vector((0, 0, 0.025)))
create_pole_bone(arm, "cf_j_middle02_L", "cf_j_middle_Pole_L", "cf_s_hand_L", Vector((0, 0, 0.025)))
create_pole_bone(arm, "cf_j_index02_L",  "cf_j_index_Pole_L",  "cf_s_hand_L", Vector((0, 0, 0.025)))
src_thumb_L = arm.data.edit_bones.get("cf_j_thumb02_L")
if src_thumb_L:
    x_axis_L = (src_thumb_L.tail - src_thumb_L.head).normalized().cross(Vector((0, 0, 1))).normalized()
    create_pole_bone(arm, "cf_j_thumb02_L", "cf_j_thumb_Pole_L", "cf_s_hand_L", x_axis_L * 0.025)

create_arm_pole(arm, "cf_j_arm00_R", "cf_j_arm_Pole_R", offset=0.4, length=0.1)
create_arm_pole(arm, "cf_j_arm00_L", "cf_j_arm_Pole_L", offset=0.4, length=0.1)

create_thigh_pole(arm, "cf_j_thigh00_R", "cf_j_thigh_Pole_R", offset=-0.55, length=0.1)
create_thigh_pole(arm, "cf_j_thigh00_L", "cf_j_thigh_Pole_L", offset=-0.55, length=0.1)

align_bone_direction_to_source(arm, "cf_j_hand_R", "cf_s_hand_R")
align_bone_direction_to_source(arm, "cf_j_hand_L", "cf_s_hand_L")

reparent_bone_keep_offset(arm, "cf_j_hand_R", "cf_j_root")
reparent_bone_keep_offset(arm, "cf_j_hand_L", "cf_j_root")
reparent_bone_keep_offset(arm, "cf_j_arm_Pole_R", "cf_j_root")
reparent_bone_keep_offset(arm, "cf_j_arm_Pole_L", "cf_j_root")
reparent_bone_keep_offset(arm, "cf_j_thigh_Pole_R", "cf_j_root")
reparent_bone_keep_offset(arm, "cf_j_thigh_Pole_L", "cf_j_root")

reparent_bone_keep_offset(arm, "cf_s_hand_R", "cf_j_forearm01_R")
reparent_bone_keep_offset(arm, "cf_s_hand_L", "cf_j_forearm01_L")

create_foot_ctrl(arm, "cf_j_foot_R", "cf_j_foot_Ctrl_R", "cf_j_root", length=0.13)
create_foot_ctrl(arm, "cf_j_foot_L", "cf_j_foot_Ctrl_L", "cf_j_root", length=0.13)

print("✅ Step_04 completado")

# ==================================================
# STEP_04_5
# ==================================================

bone_R = create_eye_ctrl_bone(arm, "cf_J_Eye_rz_R", "cf_J_Eye_Ctrl_R")
bone_L = create_eye_ctrl_bone(arm, "cf_J_Eye_rz_L", "cf_J_Eye_Ctrl_L")

if bone_R and bone_L:
    ebones = arm.data.edit_bones

    mid_head = (bone_R.head + bone_L.head) / 2.0
    mid_tail = mid_head + mathutils.Vector((0.0, -1.0, 0.0)) * 0.02

    if "cf_J_Eye_Ctrl_Main" not in ebones:
        main_bone = ebones.new("cf_J_Eye_Ctrl_Main")
        main_bone.head = mid_head
        main_bone.tail = mid_tail
        main_bone.use_connect = False
        main_bone.parent = None
        print("✅ Creado hueso cf_J_Eye_Ctrl_Main")
    else:
        main_bone = ebones["cf_J_Eye_Ctrl_Main"]
        print("⚠️ El hueso cf_J_Eye_Ctrl_Main ya existe, se reutiliza.")

    bone_R.parent = main_bone
    bone_R.use_connect = False
    bone_L.parent = main_bone
    bone_L.use_connect = False
    print("🔗 Parentados cf_J_Eye_Ctrl_R y cf_J_Eye_Ctrl_L al cf_J_Eye_Ctrl_Main (Keep Offset)")

    main_bone.parent = ebones["cf_j_head"]
    main_bone.use_connect = False
    print("🔗 Parentado cf_J_Eye_Ctrl_Main a cf_j_head (Keep Offset)")

bpy.ops.object.mode_set(mode='OBJECT')
print("✅ Script combinado completado: Step_04 + Step_04_5")
