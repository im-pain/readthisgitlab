import bpy
from mathutils import Vector

# --------------------------
# Utilidades
# --------------------------
def ensure_armature_in_edit_mode():
    arm = bpy.context.object
    if arm is None or arm.type != 'ARMATURE':
        raise RuntimeError("Selecciona un objeto Armature activo antes de ejecutar el script.")
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    return arm

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
# Arm Pole (desde tail de cf_j_arm00_*)
# orientado hacia atrás (+Y), offset en +Y, sin parent
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
    offset_vec = Vector((0, offset, 0))            # offset desde tail en +Y
    new_bone = ebones.new(pole_name)
    new_bone.head = src.tail + offset_vec
    new_bone.tail = new_bone.head + Vector((0, length, 0))  # orientado hacia +Y (mirando atrás)
    new_bone.roll = 0.0
    new_bone.parent = None

# --------------------------
# Thigh Pole (desde tail de cf_j_thigh00_*)
# paralelos al eje Y con direccion -Y, offset -0.4 en Y, sin parent
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
    offset_vec = Vector((0, offset, 0))            # offset desde tail en -Y
    new_bone = ebones.new(pole_name)
    new_bone.head = src.tail + offset_vec
    new_bone.tail = new_bone.head + Vector((0, -length, 0))  # orientado hacia -Y
    new_bone.roll = 0.0
    new_bone.parent = None

# --------------------------
# Foot Ctrl (desde head de cf_j_foot_*)
# misma dirección que fuente pero SIN copiar roll, largo fijo, parent cf_j_root keep offset
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
    new_bone.head = src.head.copy()  # partir del head del hueso fuente
    dir_vec = (src.tail - src.head)
    if dir_vec.length == 0:
        dir_vec = Vector((0, 1, 0))
    new_bone.tail = new_bone.head + dir_vec.normalized() * length
    new_bone.roll = 0.0  # NO copiar roll, dejar en 0
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
    # NO modificar tgt.roll

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
# Ejecución principal (integrada)
# --------------------------
try:
    arm = ensure_armature_in_edit_mode()
except RuntimeError as e:
    print(e)
else:
    # ---- Ctrl dedos (R/L) ----
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

    # ---- Poles dedos R ----
    create_pole_bone(arm, "cf_j_little02_R", "cf_j_little_Pole_R", "cf_s_hand_R", Vector((0,0,0.025)))
    create_pole_bone(arm, "cf_j_ring02_R",   "cf_j_ring_Pole_R",   "cf_s_hand_R", Vector((0,0,0.025)))
    create_pole_bone(arm, "cf_j_middle02_R", "cf_j_middle_Pole_R", "cf_s_hand_R", Vector((0,0,0.025)))
    create_pole_bone(arm, "cf_j_index02_R",  "cf_j_index_Pole_R",  "cf_s_hand_R", Vector((0,0,0.025)))
    src_thumb_R = arm.data.edit_bones.get("cf_j_thumb02_R")
    if src_thumb_R:
        x_axis_R = (src_thumb_R.tail - src_thumb_R.head).normalized().cross(Vector((0,0,1))).normalized()
        create_pole_bone(arm, "cf_j_thumb02_R", "cf_j_thumb_Pole_R", "cf_s_hand_R", x_axis_R * -0.025)

    # ---- Poles dedos L ----
    create_pole_bone(arm, "cf_j_little02_L", "cf_j_little_Pole_L", "cf_s_hand_L", Vector((0,0,0.025)))
    create_pole_bone(arm, "cf_j_ring02_L",   "cf_j_ring_Pole_L",   "cf_s_hand_L", Vector((0,0,0.025)))
    create_pole_bone(arm, "cf_j_middle02_L", "cf_j_middle_Pole_L", "cf_s_hand_L", Vector((0,0,0.025)))
    create_pole_bone(arm, "cf_j_index02_L",  "cf_j_index_Pole_L",  "cf_s_hand_L", Vector((0,0,0.025)))
    src_thumb_L = arm.data.edit_bones.get("cf_j_thumb02_L")
    if src_thumb_L:
        x_axis_L = (src_thumb_L.tail - src_thumb_L.head).normalized().cross(Vector((0,0,1))).normalized()
        create_pole_bone(arm, "cf_j_thumb02_L", "cf_j_thumb_Pole_L", "cf_s_hand_L", x_axis_L * 0.025)

    # ---- Arm Poles (renombrados a cf_j_arm_Pole_*) ----
    create_arm_pole(arm, "cf_j_arm00_R", "cf_j_arm_Pole_R", offset=0.4, length=0.1)
    create_arm_pole(arm, "cf_j_arm00_L", "cf_j_arm_Pole_L", offset=0.4, length=0.1)

    # ---- Thigh Poles (desde tail de cf_j_thigh00_*, orientados -Y, offset -0.4) ----
    create_thigh_pole(arm, "cf_j_thigh00_R", "cf_j_thigh_Pole_R", offset=-0.55, length=0.1)
    create_thigh_pole(arm, "cf_j_thigh00_L", "cf_j_thigh_Pole_L", offset=-0.55, length=0.1)

    # ---- Alinear cf_s_hand_R/L a cf_j_hand_R/L sin cambiar roll ----
    align_bone_direction_to_source(arm, "cf_j_hand_R", "cf_s_hand_R")
    align_bone_direction_to_source(arm, "cf_j_hand_L", "cf_s_hand_L")
    
    # ---- Reparentar cf_j_hand_R/L a cf_j_root con keep offset ----
    if "cf_j_root" in arm.data.edit_bones:
        reparent_bone_keep_offset(arm, "cf_j_hand_R", "cf_j_root")
        reparent_bone_keep_offset(arm, "cf_j_hand_L", "cf_j_root")
        reparent_bone_keep_offset(arm, "cf_j_arm_Pole_R", "cf_j_root")
        reparent_bone_keep_offset(arm, "cf_j_arm_Pole_L", "cf_j_root")
        reparent_bone_keep_offset(arm, "cf_j_thigh_Pole_R", "cf_j_root")
        reparent_bone_keep_offset(arm, "cf_j_thigh_Pole_L", "cf_j_root")
    else:
        print("[reparent] Padre cf_j_root no encontrado, cf_j_hand_R/L no reparentados.")

    # ---- Reparentar cf_s_hand_R/L a cf_j_forearm01_R/L con keep offset ----
    if "cf_j_forearm01_R" in arm.data.edit_bones:
        reparent_bone_keep_offset(arm, "cf_s_hand_R", "cf_j_forearm01_R")
    else:
        print("[reparent] Padre cf_j_forearm01_R no encontrado, cf_s_hand_R no reparentado.")
    if "cf_j_forearm01_L" in arm.data.edit_bones:
        reparent_bone_keep_offset(arm, "cf_s_hand_L", "cf_j_forearm01_L")
    else:
        print("[reparent] Padre cf_j_forearm01_L no encontrado, cf_s_hand_L no reparentado.")

    # ---- Foot Ctrl (desde head de cf_j_foot_R/L), sin roll, largo 0.13, parent cf_j_root keep offset ----
    create_foot_ctrl(arm, "cf_j_foot_R", "cf_j_foot_Ctrl_R", "cf_j_root", length=0.13)
    create_foot_ctrl(arm, "cf_j_foot_L", "cf_j_foot_Ctrl_L", "cf_j_root", length=0.13)

    # Volver a modo objeto
    bpy.ops.object.mode_set(mode='OBJECT')
    print("✅ Script completado: Ctrl, Pole (dedos), Arm Poles, Thigh Poles, Foot Ctrls creados; cf_s_hand_R/L alineados y reparentados.")
