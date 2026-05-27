import bpy
import mathutils

def create_eye_ctrl_bone(src_bone_name, new_bone_name, offset_y=-0.15, length=0.01):
    arm = bpy.context.object
    if arm is None or arm.type != 'ARMATURE':
        raise RuntimeError("Selecciona un objeto Armature en modo edición.")

    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm.data.edit_bones

    if src_bone_name not in ebones:
        print(f"⚠️ No se encontró el hueso {src_bone_name}")
        return None

    src_bone = ebones[src_bone_name]

    # Posición base: tail del hueso fuente
    base_pos = src_bone.tail.copy()
    base_pos.y += offset_y

    # Dirección hacia -Y
    direction = mathutils.Vector((0.0, -1.0, 0.0))

    # Crear hueso nuevo
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

# Crear huesos de los ojos
bone_R = create_eye_ctrl_bone("cf_J_Eye_rz_R", "cf_J_Eye_Ctrl_R")
bone_L = create_eye_ctrl_bone("cf_J_Eye_rz_L", "cf_J_Eye_Ctrl_L")

# Crear hueso central entre ambos
if bone_R and bone_L:
    arm = bpy.context.object
    ebones = arm.data.edit_bones

    # Punto medio en X entre ambos heads
    mid_head = (bone_R.head + bone_L.head) / 2.0
    mid_tail = mid_head + mathutils.Vector((0.0, -1.0, 0.0)) * 0.02  # longitud 0.02

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

    # Parentar los huesos R y L al Main en modo Keep Offset
    bone_R.parent = main_bone
    bone_R.use_connect = False
    bone_L.parent = main_bone
    bone_L.use_connect = False
    print("🔗 Parentados cf_J_Eye_Ctrl_R y cf_J_Eye_Ctrl_L al cf_J_Eye_Ctrl_Main (Keep Offset)")

    # Parentar el Main al hueso cf_j_head en Keep Offset
    if "cf_j_head" in ebones:
        main_bone.parent = ebones["cf_j_head"]
        main_bone.use_connect = False
        print("🔗 Parentado cf_J_Eye_Ctrl_Main a cf_j_head (Keep Offset)")
    else:
        print("⚠️ No se encontró el hueso cf_j_head, no se pudo parentar el Main.")

bpy.ops.object.mode_set(mode='OBJECT')
