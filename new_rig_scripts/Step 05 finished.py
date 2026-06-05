import bpy
import math
import mathutils

# Nombre del armature
armature_name = "Armature"
arm_obj = bpy.data.objects[armature_name]
arm = bpy.data.armatures[armature_name]

# --- Función para crear restricción IK ---
def add_ik_constraint(bone_name, ctrl_name, pole_name, pole_angle):
    pb = arm_obj.pose.bones[bone_name]
    ik_constraint = pb.constraints.new('IK')
    ik_constraint.target = arm_obj
    ik_constraint.subtarget = ctrl_name
    ik_constraint.pole_target = arm_obj
    ik_constraint.pole_subtarget = pole_name
    ik_constraint.pole_angle = pole_angle
    ik_constraint.iterations = 500
    ik_constraint.chain_count = 3
    ik_constraint.use_tail = True
    ik_constraint.use_stretch = True
    ik_constraint.use_location = True   # Weight Position habilitado
    ik_constraint.use_rotation = True   # Rotation habilitado

# --- Crear restricciones IK para cada dedo (lado R) ---
add_ik_constraint("cf_j_index03_R", "cf_j_index_Ctrl_R", "cf_j_index_Pole_R", math.pi/2)
add_ik_constraint("cf_j_middle03_R", "cf_j_middle_Ctrl_R", "cf_j_middle_Pole_R", math.pi/2)
add_ik_constraint("cf_j_ring03_R", "cf_j_ring_Ctrl_R", "cf_j_ring_Pole_R", math.pi/2)
add_ik_constraint("cf_j_little03_R", "cf_j_little_Ctrl_R", "cf_j_little_Pole_R", math.pi/2)
add_ik_constraint("cf_j_thumb03_R", "cf_j_thumb_Ctrl_R", "cf_j_thumb_Pole_R", math.pi)  # 180°

# --- Crear restricciones IK para cada dedo (lado L) ---
add_ik_constraint("cf_j_index03_L", "cf_j_index_Ctrl_L", "cf_j_index_Pole_L", math.pi/2)
add_ik_constraint("cf_j_middle03_L", "cf_j_middle_Ctrl_L", "cf_j_middle_Pole_L", math.pi/2)
add_ik_constraint("cf_j_ring03_L", "cf_j_ring_Ctrl_L", "cf_j_ring_Pole_L", math.pi/2)
add_ik_constraint("cf_j_little03_L", "cf_j_little_Ctrl_L", "cf_j_little_Pole_L", math.pi/2)
add_ik_constraint("cf_j_thumb03_L", "cf_j_thumb_Ctrl_L", "cf_j_thumb_Pole_L", math.pi)  # 180°

bpy.ops.object.mode_set(mode='EDIT')
# --- Offsets específicos para cada Ctrl (positivos en ambos lados) ---
ctrl_bones = {
    "cf_j_index_Ctrl_R": arm.edit_bones['cf_j_index03_R'].length,
    "cf_j_middle_Ctrl_R": arm.edit_bones['cf_j_middle03_R'].length,
    "cf_j_ring_Ctrl_R": arm.edit_bones['cf_j_ring03_R'].length,
    "cf_j_little_Ctrl_R": arm.edit_bones['cf_j_little03_R'].length,
    "cf_j_thumb_Ctrl_R": arm.edit_bones['cf_j_thumb03_R'].length,
    "cf_j_index_Ctrl_L": arm.edit_bones['cf_j_index03_L'].length,
    "cf_j_middle_Ctrl_L": arm.edit_bones['cf_j_middle03_L'].length,
    "cf_j_ring_Ctrl_L": arm.edit_bones['cf_j_ring03_L'].length,
    "cf_j_little_Ctrl_L": arm.edit_bones['cf_j_little03_L'].length,
    "cf_j_thumb_Ctrl_L": arm.edit_bones['cf_j_thumb03_L'].length,
}

# --- Aplicar offsets ---
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

for bone_name, offset_y in ctrl_bones.items():
    if bone_name in arm_obj.data.edit_bones:
        edit_bone = arm_obj.data.edit_bones[bone_name]
        offset = mathutils.Vector((0, offset_y, 0))
        edit_bone.head += edit_bone.matrix.to_3x3() @ offset
        edit_bone.tail += edit_bone.matrix.to_3x3() @ offset

# Volver a modo objeto
bpy.ops.object.mode_set(mode='OBJECT')
