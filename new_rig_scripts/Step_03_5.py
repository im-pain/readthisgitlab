import bpy
import mathutils

# --- Función para mover tail en espacio local ---
def move_tail_local(bone, delta):
    """
    Mueve el tail de un hueso en coordenadas locales.
    delta: mathutils.Vector con desplazamiento en espacio local del hueso.
    """
    arm = bpy.context.object
    bone_matrix = bone.matrix.to_3x3()
    local_delta = bone_matrix @ delta
    bone.tail += local_delta

# --- Función para alinear head al tail de otro hueso ---
def align_head_to_tail(bone, target_bone):
    bone.head = target_bone.tail.copy()

# --- Script principal ---
arm = bpy.context.object
if arm is None or arm.type != 'ARMATURE':
    raise Exception("Selecciona un Armature en modo edición.")

bpy.ops.object.mode_set(mode='EDIT')
edit_bones = arm.data.edit_bones

# Definiciones de desplazamientos
delta_z = mathutils.Vector((0, 0, 0.001))
delta_thumb_R = mathutils.Vector((-0.001, -0.001, 0))
delta_thumb_L = mathutils.Vector((-0.001,  0.001, 0))

# Listas de huesos
finger_roots = ["cf_j_little01_", "cf_j_ring01_", "cf_j_middle01_", "cf_j_index01_"]
finger_nexts = ["cf_j_little02_", "cf_j_ring02_", "cf_j_middle02_", "cf_j_index02_"]

# Procesar lados R y L
for side in ["R", "L"]:
    # Mover tails de los huesos principales
    for root in finger_roots:
        name = root + side
        if name in edit_bones:
            move_tail_local(edit_bones[name], delta_z)

    thumb_root = "cf_j_thumb01_" + side
    if thumb_root in edit_bones:
        if side == "R":
            move_tail_local(edit_bones[thumb_root], delta_thumb_R)
        else:
            move_tail_local(edit_bones[thumb_root], delta_thumb_L)

    # Heads de los huesos sucesores al tail de sus predecesores
    for root, nxt in zip(finger_roots, finger_nexts):
        root_name = root + side
        nxt_name = nxt + side
        if root_name in edit_bones and nxt_name in edit_bones:
            align_head_to_tail(edit_bones[nxt_name], edit_bones[root_name])

    thumb_next = "cf_j_thumb02_" + side
    if thumb_root in edit_bones and thumb_next in edit_bones:
        align_head_to_tail(edit_bones[thumb_next], edit_bones[thumb_root])

bpy.ops.object.mode_set(mode='OBJECT')
print("✅ Ajustes de huesos completados en lados R y L.")
