import bpy
import math

# Nombre del Armature
armature_name = "Armature"
armature = bpy.data.objects[armature_name]

def add_ik_constraint(bone_name, target_bone, pole_bone=None, pole_angle=None, chain_length=2):
    """
    Crea un constraint IK en el hueso especificado con los parámetros dados.
    """
    pb = armature.pose.bones.get(bone_name)
    if not pb:
        print(f"⚠️ Hueso {bone_name} no encontrado")
        return

    ik = pb.constraints.new('IK')
    ik.target = armature
    ik.subtarget = target_bone

    if pole_bone:
        ik.pole_target = armature
        ik.pole_subtarget = pole_bone

    if pole_angle is not None:
        ik.pole_angle = pole_angle

    ik.chain_count = chain_length

    print(f"✅ IK agregado a {bone_name} -> Target {target_bone}, Pole {pole_bone}, Chain {chain_length}, Angle {pole_angle}")

def add_copy_rotation_constraint(bone_name, target_bone, target_space='LOCAL', owner_space='LOCAL', influence=1.0):
    """
    Crea un constraint Copy Rotation en el hueso especificado.
    """
    pb = armature.pose.bones.get(bone_name)
    if not pb:
        print(f"⚠️ Hueso {bone_name} no encontrado")
        return

    cr = pb.constraints.new('COPY_ROTATION')
    cr.target = armature
    cr.subtarget = target_bone
    cr.target_space = target_space
    cr.owner_space = owner_space
    cr.influence = influence

    print(f"✅ Copy Rotation agregado a {bone_name} -> Target {target_bone}, Space {target_space}/{owner_space}, Influence {influence}")

# --- Restricciones IK ---
add_ik_constraint("cf_j_forearm01_R", "cf_j_hand_R", "cf_j_arm_Pole_R", pole_angle=0.0, chain_length=2)
add_ik_constraint("cf_j_forearm01_L", "cf_j_hand_L", "cf_j_arm_Pole_L", pole_angle=math.pi, chain_length=2)
add_ik_constraint("cf_j_leg01_R", "cf_j_foot_Ctrl_R", "cf_j_thigh_Pole_R", pole_angle=-math.pi/2, chain_length=2)
add_ik_constraint("cf_j_leg01_L", "cf_j_foot_Ctrl_L", "cf_j_thigh_Pole_L", pole_angle=-math.pi/2, chain_length=2)

# --- Restricciones Copy Rotation ---
# Manos en World Space
add_copy_rotation_constraint("cf_s_hand_R", "cf_j_hand_R", target_space='WORLD', owner_space='WORLD')
add_copy_rotation_constraint("cf_s_hand_L", "cf_j_hand_L", target_space='WORLD', owner_space='WORLD')

# Pies en World Space
add_copy_rotation_constraint("cf_j_foot_R", "cf_j_foot_Ctrl_R", target_space='WORLD', owner_space='WORLD')
add_copy_rotation_constraint("cf_j_foot_L", "cf_j_foot_Ctrl_L", target_space='WORLD', owner_space='WORLD')

# Waist con influencia 0.5 en Local Space Owner Orientation
add_copy_rotation_constraint("cf_j_waist02", "cf_j_thigh00_R", target_space='LOCAL_OWNER_ORIENT', owner_space='LOCAL', influence=0.5)
add_copy_rotation_constraint("cf_j_waist02", "cf_j_thigh00_L", target_space='LOCAL_OWNER_ORIENT', owner_space='LOCAL', influence=0.5)

# Piernas secundarias en Local Space Owner Orientation
add_copy_rotation_constraint("cf_s_leg_R", "cf_j_thigh00_R", target_space='LOCAL_OWNER_ORIENT', owner_space='LOCAL')
add_copy_rotation_constraint("cf_s_leg_L", "cf_j_thigh00_L", target_space='LOCAL_OWNER_ORIENT', owner_space='LOCAL')
