import bpy
from mathutils import Vector

arm = bpy.data.objects['Armature']

def copy_tail(src_bone_name: str, dst_bone_name: str):
    """Copia el tail de src al tail de dst."""
    arm = bpy.context.object
    if arm is None or arm.type != 'ARMATURE':
        print("⚠️ Selecciona un Armature en modo edición.")
        return
    
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm.data.edit_bones
    src, dst = ebones.get(src_bone_name), ebones.get(dst_bone_name)

    if src and dst:
        dst.tail = src.tail.copy()
        print(f"✅ Tail de {src_bone_name} → {dst_bone_name}")
    else:
        if not src: print(f"⚠️ Origen no encontrado: {src_bone_name}")
        if not dst: print(f"⚠️ Destino no encontrado: {dst_bone_name}")


def copy_head_to_tail(src_bone_name: str, dst_bone_name: str):
    """Copia el head de src al tail de dst."""
    arm = bpy.context.object
    if arm is None or arm.type != 'ARMATURE':
        print("⚠️ Selecciona un Armature en modo edición.")
        return
    
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm.data.edit_bones
    src, dst = ebones.get(src_bone_name), ebones.get(dst_bone_name)

    if src and dst:
        dst.tail = src.head.copy()
        print(f"✅ Head de {src_bone_name} → tail de {dst_bone_name}")
    else:
        if not src: print(f"⚠️ Origen no encontrado: {src_bone_name}")
        if not dst: print(f"⚠️ Destino no encontrado: {dst_bone_name}")


def copy_head_to_head(src_bone_name: str, dst_bone_name: str):
    """Copia el head de src al head de dst."""
    arm = bpy.context.object
    if arm is None or arm.type != 'ARMATURE':
        print("⚠️ Selecciona un Armature en modo edición.")
        return
    
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm.data.edit_bones
    src, dst = ebones.get(src_bone_name), ebones.get(dst_bone_name)

    if src and dst:
        dst.head = src.head.copy()
        print(f"✅ Head de {src_bone_name} → head de {dst_bone_name}")
    else:
        if not src: print(f"⚠️ Origen no encontrado: {src_bone_name}")
        if not dst: print(f"⚠️ Destino no encontrado: {dst_bone_name}")


def move_head_keep_length(src_bone_name: str, dst_bone_name: str):
    """
    Coloca el head del hueso destino en el head del hueso origen,
    mantiene la longitud original del destino y orienta el hueso
    en la dirección del origen.
    """
    arm = bpy.context.object
    if arm is None or arm.type != 'ARMATURE':
        print("⚠️ Selecciona un Armature en modo edición.")
        return
    
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm.data.edit_bones
    src, dst = ebones.get(src_bone_name), ebones.get(dst_bone_name)

    if src and dst:
        length = (dst.tail - dst.head).length
        if length == 0:
            print(f"⚠️ {dst_bone_name} tiene longitud cero.")
            return

        direction = (src.tail - src.head)
        if direction.length == 0:
            print(f"⚠️ {src_bone_name} no tiene dirección válida.")
            return
        direction = direction.normalized()

        dst.head = src.head.copy()
        dst.tail = dst.head + direction * length

        print(f"✅ {dst_bone_name} ajustado con head de {src_bone_name}, longitud {length:.4f}")
    else:
        if not src: print(f"⚠️ Origen no encontrado: {src_bone_name}")
        if not dst: print(f"⚠️ Destino no encontrado: {dst_bone_name}")


# --- Operaciones solicitadas ---
# Piernas
copy_tail("cf_j_leg01_R", "cf_s_leg02_R")
copy_tail("cf_j_leg01_L", "cf_s_leg02_L")

# Muslos (head → tail)
copy_head_to_tail("cf_s_thigh03_R", "cf_s_thigh02_R")
copy_head_to_tail("cf_s_thigh03_L", "cf_s_thigh02_L")

# Muslos (tail → tail)
copy_tail("cf_j_thigh00_R", "cf_s_thigh03_R")
copy_tail("cf_j_thigh00_L", "cf_s_thigh03_L")

# Muslos (head → tail)
copy_head_to_tail("cf_s_thigh02_R", "cf_s_thigh01_R")
copy_head_to_tail("cf_s_thigh02_L", "cf_s_thigh01_L")

# Muslos (head → head)
copy_head_to_head("cf_s_thigh01_R", "cf_j_thigh00_R")
copy_head_to_head("cf_s_thigh01_L", "cf_j_thigh00_L")

# Dirección y longitud (src = cf_s_thigh01_*, dst = cf_d_thigh01_*)
move_head_keep_length("cf_s_thigh01_R", "cf_d_thigh01_R")
move_head_keep_length("cf_s_thigh01_L", "cf_d_thigh01_L")

# Waist y Spine (head → head)
copy_head_to_head("cf_s_waist01", "cf_j_waist01")
copy_head_to_head("cf_s_spine01", "cf_j_spine01")

## Piernas Trasero (head → tail)
#copy_head_to_tail("cf_s_thigh01_R", "cf_s_leg_R")
#copy_head_to_tail("cf_s_thigh01_L", "cf_s_leg_L")

# Volver a modo objeto
bpy.ops.object.mode_set(mode='OBJECT')
