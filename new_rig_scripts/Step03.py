import bpy

bone_chain_boob_R = [
    "cf_s_bust00_R",
    "cf_s_bust01_R",
    "cf_s_bust02_R",
    "cf_s_bust03_R",
    "cf_s_bnip01_R",
    "cf_s_bnip015_R",
    "cf_s_bnip025_R",
    "cf_j_bnip02_R"
]

# Cadena izquierda
bone_chain_boob_L = [
    "cf_s_bust00_L",
    "cf_s_bust01_L",
    "cf_s_bust02_L",
    "cf_s_bust03_L",
    "cf_s_bnip01_L",
    "cf_s_bnip015_L",
    "cf_s_bnip025_L",
    "cf_j_bnip02_L"
]

# Cadena derecha
bone_chain_arm_R = [
    "cf_s_shoulder02_R",
    "cf_s_arm01_R",
    "cf_s_arm02_R",
    "cf_s_arm02_R",
    "cf_s_arm03_R",
    "cf_s_forearm01_R",
    "cf_s_forearm02_R",
    "cf_s_wrist_R",
    "cf_d_hand_R",
    "cf_s_hand_R"
]

bone_chain_arm_L = [
    "cf_s_shoulder02_L",
    "cf_s_arm01_L",
    "cf_s_arm02_L",
    "cf_s_arm02_L",
    "cf_s_arm03_L",
    "cf_s_forearm01_L",
    "cf_s_forearm02_L",
    "cf_s_wrist_L",
    "cf_d_hand_L",
    "cf_s_hand_L"
]

bone_chain_ctrl_arm_R = [
    "cf_j_arm00_R",
    "cf_j_forearm01_R",
    "cf_j_hand_R"
]

bone_chain_ctrl_arm_L = [
    "cf_j_arm00_L",
    "cf_j_forearm01_L",
    "cf_j_hand_L"
]

bone_chain_leg_R = [
    "cf_j_thigh00_R",
    "cf_j_leg01_R",
    "cf_j_foot_R"
]

bone_chain_leg_L = [
    "cf_j_thigh00_L",
    "cf_j_leg01_L",
    "cf_j_foot_L"
]

bone_chain_spine = [
    "cf_j_hips",
    "cf_j_spine01",
    "cf_j_spine02",
    "cf_j_spine03",
    "cf_j_neck",
    "cf_j_head",
]

bone_chain_spine_s = [
    "cf_s_spine01",
    "cf_s_spine02",
    "cf_s_spine03",
    "cf_s_neck"
]

bone_chain_waist = [
    "cf_j_waist01",
    "cf_j_waist02"
]

bone_chain_waist_s = [
    "cf_s_waist01",
    "cf_s_waist02"
]

bone_chain_siri_L = [
    "cf_d_siri_L",
    "cf_d_siri01_L",
    "cf_j_siri_L",
    "cf_s_siri_L",
]

bone_chain_siri_R = [
    "cf_d_siri_R",
    "cf_d_siri01_R",
    "cf_j_siri_R",
    "cf_s_siri_R",
]

bone_chain_thigh_R = [
    "cf_s_thigh01_R",
    "cf_d_siri01_R"  
]

bone_chain_thigh_L = [
    "cf_s_thigh01_L",
    "cf_d_siri01_L"  
]

# Entrar en modo edición
arm = bpy.data.objects['Armature']
bpy.ops.object.mode_set(mode='EDIT')
edit_bones = arm.data.edit_bones

# Función para procesar una cadena
def process_chain(chain):
    for i in range(len(chain) - 1):
        bone = edit_bones[chain[i]]
        next_bone = edit_bones[chain[i+1]]
        bone.tail = next_bone.head
        #next_bone.use_connect = True
        #next_bone.parent = bone

def process_chain_connected(chain):
    for i in range(len(chain) - 1):
        bone = edit_bones[chain[i]]
        next_bone = edit_bones[chain[i+1]]
        bone.tail = next_bone.head
        next_bone.use_connect = True
        next_bone.parent = bone

# Procesar ambas cadenas por separado
process_chain_connected(bone_chain_boob_R)
process_chain_connected(bone_chain_boob_L)
process_chain(bone_chain_arm_R)
process_chain(bone_chain_arm_L)
process_chain(bone_chain_ctrl_arm_R)
process_chain(bone_chain_ctrl_arm_L)
process_chain(bone_chain_leg_R)
process_chain(bone_chain_leg_L)
process_chain(bone_chain_spine)
process_chain(bone_chain_spine_s)
process_chain(bone_chain_waist)
process_chain(bone_chain_waist_s)

edit_bones['cf_j_hand_R'].tail[2] = edit_bones['cf_j_hand_R'].head[2]
edit_bones['cf_j_hand_R'].tail[1] = edit_bones['cf_j_hand_R'].head[1]
edit_bones['cf_j_hand_R'].length = 0.13

edit_bones['cf_j_hand_L'].tail[2] = edit_bones['cf_j_hand_L'].head[2]
edit_bones['cf_j_hand_L'].tail[1] = edit_bones['cf_j_hand_L'].head[1]
edit_bones['cf_j_hand_L'].length = 0.13

edit_bones['cf_J_Vagina_root'].length = 0.03

edit_bones['cf_d_siri_R'].head[0] = edit_bones['cf_j_waist02'].tail[0]
edit_bones['cf_d_siri_R'].head[1] = edit_bones['cf_j_waist02'].tail[1]
edit_bones['cf_d_siri_R'].head[2] = edit_bones['cf_j_waist02'].tail[2]

edit_bones['cf_d_siri_L'].head[0] = edit_bones['cf_j_waist02'].tail[0]
edit_bones['cf_d_siri_L'].head[1] = edit_bones['cf_j_waist02'].tail[1]
edit_bones['cf_d_siri_L'].head[2] = edit_bones['cf_j_waist02'].tail[2]

edit_bones['cf_d_siri_R'].tail[0] = edit_bones['cf_d_siri01_R'].head[0]
edit_bones['cf_d_siri_R'].tail[1] = edit_bones['cf_d_siri01_R'].head[1]
edit_bones['cf_d_siri_R'].tail[2] = edit_bones['cf_d_siri01_R'].head[2]

edit_bones['cf_d_siri_L'].tail[0] = edit_bones['cf_d_siri01_L'].head[0]
edit_bones['cf_d_siri_L'].tail[1] = edit_bones['cf_d_siri01_L'].head[1]
edit_bones['cf_d_siri_L'].tail[2] = edit_bones['cf_d_siri01_L'].head[2]

process_chain_connected(bone_chain_siri_R)
process_chain_connected(bone_chain_siri_L)

process_chain(bone_chain_thigh_R)
process_chain(bone_chain_thigh_L)

fix_y_spine = edit_bones['cf_s_spine02'].head[1]

edit_bones['cf_j_spine02'].head[1] = fix_y_spine
edit_bones['cf_j_spine01'].tail[1] = fix_y_spine

edit_bones['cf_j_hand_R'].tail[0] = edit_bones['cf_s_hand_R'].tail[0]
edit_bones['cf_j_hand_L'].tail[0] = edit_bones['cf_s_hand_L'].tail[0]

edit_bones['cf_j_hand_R'].parent = None
edit_bones['cf_j_hand_L'].parent = None

edit_bones['cf_j_hand_R'].length = 0.03

bpy.ops.object.mode_set(mode='OBJECT')
