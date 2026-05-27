import bpy

bpy.ops.object.mode_set(mode='OBJECT')

eye_x_move = bpy.data.materials['cf_m_hitomi_00_L'].node_tree.nodes['Eye Controls'].inputs[3]#.default_value
eye_x_move_fcurve = eye_x_move.driver_add("default_value")
eye_x_move_driver = eye_x_move_fcurve.driver
eye_x_move_driver.type = "SCRIPTED"

eye_x_move_driver.expression = "location + location_L"

eye_x_move_control = eye_x_move_driver.variables.new()
eye_x_move_control.name = "location"

copy_x_move = eye_x_move_control.targets[0]
copy_x_move.id_type = 'OBJECT'
copy_x_move.id = bpy.data.objects['Armature']
copy_x_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].location[0]'

eye_x_move_control = eye_x_move_driver.variables.new()
eye_x_move_control.name = "location_L"

copy_x_move = eye_x_move_control.targets[0]
copy_x_move.id_type = 'OBJECT'
copy_x_move.id = bpy.data.objects['Armature']
copy_x_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_L"].location[0]'

###############################################################

eye_y_move = bpy.data.materials['cf_m_hitomi_00_L'].node_tree.nodes['Eye Controls'].inputs[4]#.default_value
eye_y_move_fcurve = eye_y_move.driver_add("default_value")
eye_y_move_driver = eye_y_move_fcurve.driver
eye_y_move_driver.type = "SCRIPTED"

eye_y_move_driver.expression = "-location + -location_L"

eye_y_move_control = eye_y_move_driver.variables.new()
eye_y_move_control.name = "location"

copy_y_move = eye_y_move_control.targets[0]
copy_y_move.id_type = 'OBJECT'
copy_y_move.id = bpy.data.objects['Armature']
copy_y_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].location[2]'

eye_y_move_control = eye_y_move_driver.variables.new()
eye_y_move_control.name = "location_L"

copy_y_move = eye_y_move_control.targets[0]
copy_y_move.id_type = 'OBJECT'
copy_y_move.id = bpy.data.objects['Armature']
copy_y_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_L"].location[2]'

###############################################################

eye_x_scale = bpy.data.materials['cf_m_hitomi_00_L'].node_tree.nodes['Eye Controls'].inputs[1]#.default_value
eye_x_scale_fcurve = eye_x_scale.driver_add("default_value")
eye_x_scale_driver = eye_x_scale_fcurve.driver
eye_x_scale_driver.type = "SCRIPTED"

eye_x_scale_control = eye_x_scale_driver.variables.new()
eye_x_scale_control.name = "scale"

eye_x_scale_driver.expression = "(-scale+2)*(-all_scale+2)"
copy_x_scale = eye_x_scale_control.targets[0]
copy_x_scale.id_type = 'OBJECT'
copy_x_scale.id = bpy.data.objects['Armature']
copy_x_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_L"].scale[0]'

eye_x_all_scale_control = eye_x_scale_driver.variables.new()
eye_x_all_scale_control.name = "all_scale"

copy_x_all_scale = eye_x_all_scale_control.targets[0]
copy_x_all_scale.id_type = 'OBJECT'
copy_x_all_scale.id = bpy.data.objects['Armature']
copy_x_all_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].scale[0]'

###############################################################

eye_y_scale = bpy.data.materials['cf_m_hitomi_00_L'].node_tree.nodes['Eye Controls'].inputs[2]#.default_value
eye_y_scale_fcurve = eye_y_scale.driver_add("default_value")
eye_y_scale_driver = eye_y_scale_fcurve.driver
eye_y_scale_driver.type = "SCRIPTED"

eye_y_scale_control = eye_y_scale_driver.variables.new()
eye_y_scale_control.name = "scale"

eye_y_scale_driver.expression = "(-scale+2)*(-all_scale+2)"
copy_y_scale = eye_y_scale_control.targets[0]
copy_y_scale.id_type = 'OBJECT'
copy_y_scale.id = bpy.data.objects['Armature']
copy_y_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_L"].scale[2]'

eye_y_all_scale_control = eye_y_scale_driver.variables.new()
eye_y_all_scale_control.name = "all_scale"

copy_y_all_scale = eye_y_all_scale_control.targets[0]
copy_y_all_scale.id_type = 'OBJECT'
copy_y_all_scale.id = bpy.data.objects['Armature']
copy_y_all_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].scale[2]'

###############################################################

eye_x_move = bpy.data.materials['cf_m_hitomi_00_R'].node_tree.nodes['Eye Controls'].inputs[3]#.default_value
eye_x_move_fcurve = eye_x_move.driver_add("default_value")
eye_x_move_driver = eye_x_move_fcurve.driver
eye_x_move_driver.type = "SCRIPTED"

eye_x_move_driver.expression = "location + location_R"

eye_x_move_control = eye_x_move_driver.variables.new()
eye_x_move_control.name = "location"

copy_x_move = eye_x_move_control.targets[0]
copy_x_move.id_type = 'OBJECT'
copy_x_move.id = bpy.data.objects['Armature']
copy_x_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].location[0]'

eye_x_move_control = eye_x_move_driver.variables.new()
eye_x_move_control.name = "location_R"

copy_x_move = eye_x_move_control.targets[0]
copy_x_move.id_type = 'OBJECT'
copy_x_move.id = bpy.data.objects['Armature']
copy_x_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_R"].location[0]'

###############################################################

eye_y_move = bpy.data.materials['cf_m_hitomi_00_R'].node_tree.nodes['Eye Controls'].inputs[4]#.default_value
eye_y_move_fcurve = eye_y_move.driver_add("default_value")
eye_y_move_driver = eye_y_move_fcurve.driver
eye_y_move_driver.type = "SCRIPTED"

eye_y_move_driver.expression = "-location + -location_R"

eye_y_move_control = eye_y_move_driver.variables.new()
eye_y_move_control.name = "location"

copy_y_move = eye_y_move_control.targets[0]
copy_y_move.id_type = 'OBJECT'
copy_y_move.id = bpy.data.objects['Armature']
copy_y_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].location[2]'

eye_y_move_control = eye_y_move_driver.variables.new()
eye_y_move_control.name = "location_R"

copy_y_move = eye_y_move_control.targets[0]
copy_y_move.id_type = 'OBJECT'
copy_y_move.id = bpy.data.objects['Armature']
copy_y_move.data_path = 'pose.bones["cf_J_Eye_Ctrl_R"].location[2]'

###############################################################

eye_x_scale = bpy.data.materials['cf_m_hitomi_00_R'].node_tree.nodes['Eye Controls'].inputs[1]#.default_value
eye_x_scale_fcurve = eye_x_scale.driver_add("default_value")
eye_x_scale_driver = eye_x_scale_fcurve.driver
eye_x_scale_driver.type = "SCRIPTED"

eye_x_scale_control = eye_x_scale_driver.variables.new()
eye_x_scale_control.name = "scale"

eye_x_scale_driver.expression = "(-scale+2)*(-all_scale+2)"
copy_x_scale = eye_x_scale_control.targets[0]
copy_x_scale.id_type = 'OBJECT'
copy_x_scale.id = bpy.data.objects['Armature']
copy_x_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_R"].scale[0]'

eye_x_all_scale_control = eye_x_scale_driver.variables.new()
eye_x_all_scale_control.name = "all_scale"

copy_x_all_scale = eye_x_all_scale_control.targets[0]
copy_x_all_scale.id_type = 'OBJECT'
copy_x_all_scale.id = bpy.data.objects['Armature']
copy_x_all_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].scale[0]'

###############################################################

eye_y_scale = bpy.data.materials['cf_m_hitomi_00_R'].node_tree.nodes['Eye Controls'].inputs[2]#.default_value
eye_y_scale_fcurve = eye_y_scale.driver_add("default_value")
eye_y_scale_driver = eye_y_scale_fcurve.driver
eye_y_scale_driver.type = "SCRIPTED"

eye_y_scale_control = eye_y_scale_driver.variables.new()
eye_y_scale_control.name = "scale"

eye_y_scale_driver.expression = "(-scale+2)*(-all_scale+2)"
copy_y_scale = eye_y_scale_control.targets[0]
copy_y_scale.id_type = 'OBJECT'
copy_y_scale.id = bpy.data.objects['Armature']
copy_y_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_R"].scale[2]'

eye_y_all_scale_control = eye_y_scale_driver.variables.new()
eye_y_all_scale_control.name = "all_scale"

copy_y_all_scale = eye_y_all_scale_control.targets[0]
copy_y_all_scale.id_type = 'OBJECT'
copy_y_all_scale.id = bpy.data.objects['Armature']
copy_y_all_scale.data_path = 'pose.bones["cf_J_Eye_Ctrl_Main"].scale[2]'

#####
#bpy.ops.object.mode_set(mode='POSE')
#bpy.ops.pose.select_all(action='DESELECT')
######
#bpy.data.objects['Armature'].pose.bones['cf_J_Eye_Ctrl_Main'].bone.select = True
##bpy.ops.pose.group_assign(type=3)

#bpy.ops.pose.select_all(action='DESELECT')

#bpy.data.objects['Armature'].pose.bones['cf_J_Eye_Ctrl_L'].bone.select = True
#bpy.data.objects['Armature'].pose.bones['cf_J_Eye_Ctrl_R'].bone.select = True
##bpy.ops.pose.group_assign(type=5)

#bpy.ops.pose.select_all(action='DESELECT')

bpy.ops.object.mode_set(mode='OBJECT')
