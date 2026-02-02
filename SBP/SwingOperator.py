import bpy
import copy
import bpy_extras
import addon_utils
import json

from .SwingProp import *
from .SwingUtils import *

##############################
# DRB
##############################

def AddDRBOprSanityChecks(self, context):
    scene = context.scene
    #check if there are several bones selected
    if len(context.selected_pose_bones)>1 and not scene.bSwMultiSelectChain:
        self.report({'ERROR'}, "Only select the first bone of the chain!")
        return False  

    if scene.bSwMultiSelectChain:
        pbs = [pb for pb in context.selected_pose_bones]
    else:
        pbs=[context.active_pose_bone]
        for cpb in context.active_pose_bone.children_recursive:
            pbs.append(cpb)
    #check if a bone is already in a chain
    bIsInChainAlready = False
    #check if the root or a child has a collider attached
    bHasCollider = False
    #check if the root or a child has more than two children
    bHasMoreThanOneChild = False
    #check if there's one child not connected
    bIsNotConnected = False
    #check if the multiple selection bone chain is a valid one (no hole and all linked bones)
    bIsNotValidMulti = False
    for i,pb in enumerate(pbs):
        if pb.bIsDRB:
            bIsInChainAlready = True
            break
        if pb.name.startswith("SRB_Collider_"):
            bHasCollider = True
            break
        if (len(pb.bone.children) > 1 and not scene.bSwMultiSelectChain) or (scene.bSwMultiSelectChain and i < len(pbs)-1 and len(pb.bone.children)>1):
            bHasMoreThanOneChild = True
            break
        if i and not pb.bone.use_connect:
            bIsNotConnected = True
            break
        if scene.bSwMultiSelectChain and i < len(pbs)-1 and pb.children[0] != pbs[i+1]:
            bIsNotValidMulti = True
            break
    if bIsInChainAlready:
        self.report({'ERROR'}, "One of the bones is already in a chain.")
        return False
    if bHasCollider:
        self.report({'ERROR'}, "One of the bones in the chain has a collider")
        return False  
    if bHasMoreThanOneChild:
        if scene.bSwMultiSelectChain:
            self.report({'ERROR'}, "A middle bone has more than one child.")
        else:
            self.report({'ERROR'}, "One of the bones has more than one child.")
        return False
    if bIsNotConnected:
        self.report({'ERROR'}, "One of the bones in the chain is not connected.")
        return False 
    if bIsNotValidMulti:
        self.report({'ERROR'}, "The multi bone chain is not valid.")
        return False 
    return True

class SW_OT_DRBAddOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbadd"
    bl_label = "Create bone chain"
    bl_description = "Create a bone chain starting from this bone"

    bHasKfs: bpy.props.BoolProperty(name='bHasKfs', default=False,options={'HIDDEN'})
    bArmNotNormed: bpy.props.BoolProperty(name='bArmNotNormed', default=False,options={'HIDDEN'})

    @classmethod
    def poll(self, context):
        if bpy.app.version[0] < 5:
            return context.active_pose_bone is not None and context.active_pose_bone.bone.select and context.mode == "POSE" and context.object.override_library is None
        else:
            return context.active_pose_bone is not None and context.active_pose_bone.select and context.mode == "POSE" and context.object.override_library is None
    
    def draw(self, context):
        layout = self.layout
        if self.bHasKfs:
            layout.label(text="Some bone(s) in the chain have keyframes that are going to be deleted.")            
        if self.bArmNotNormed:
            layout.label(text="The armature doesn't have scale applied, it will be applied now.")
        layout.label(text="Proceed?")
    
    def invoke(self, context, event):
        scene = context.scene
        pbs=[context.active_pose_bone]
        if scene.bSwMultiSelectChain:
            pbs += [pb for pb in context.selected_pose_bones if pb != context.active_pose_bone]
        else:
            for cpb in context.active_pose_bone.children_recursive:
                pbs.append(cpb)
        #check if there is any keyframe for a bone
        self.bHasKfs = False
        self.bArmNotNormed = False
        actionName = None   
        
        if bpy.app.version[0] < 5:
            if context.object.animation_data is not None and context.object.animation_data.action is not None:
                actionName = context.object.animation_data.action.name  
            if actionName is not None:
                for pb in pbs:                      
                    for group in bpy.data.actions[actionName].groups:
                        if group.name == pb.name or group.name == "SWExtraChildBone_" + pb.id_data.name + "_" + pb.name:
                            self.bHasKfs = True
        else:
            actionSlotName = None
            if context.object.animation_data is not None and context.object.animation_data.action is not None and context.object.animation_data.action_slot is not None:
                actionName = context.object.animation_data.action.name  
                actionSlotName = context.object.animation_data.action_slot.name_display
            if actionName is not None and actionSlotName is not None:
                for pb in pbs:        
                    # channelbag = bpy_extras.anim_utils.action_get_channelbag_for_slot(context.object.animation_data.action, context.object.animation_data.action_slot)
                    # foundGroup = channelbag.groups.find(pb.name)   
                    # if foundGroup < 0:
                    #     foundGroup = channelbag.groups.find("SWExtraChildBone_" + pb.id_data.name + "_" + pb.name)
                    # if foundGroup >= 0:
                    #     self.bHasKfs = True
                    channelbag = bpy_extras.anim_utils.action_get_channelbag_for_slot(context.object.animation_data.action, context.object.animation_data.action_slot)
                    for fcurve in channelbag.fcurves:
                        if pb.name in fcurve.data_path.split("\"") or "SWExtraChildBone_" in fcurve.data_path:
                            self.bHasKfs = True                  
                    

        scale = context.active_pose_bone.id_data.scale
        if scale != Vector((1.0, 1.0, 1.0)):
            self.bArmNotNormed = True
        if self.bHasKfs or self.bArmNotNormed:            
            return context.window_manager.invoke_props_dialog(self,width=500)
        return self.execute(context)
    
    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList

        bpy.ops.object.mode_set(mode='POSE')

        #Bone specific checks
        if not AddDRBOprSanityChecks(self, context):
            return {'FINISHED'}  
        pbs = []
        if scene.bSwMultiSelectChain:
            pbs = [pb for pb in context.selected_pose_bones]
        else:
            pbs=[context.active_pose_bone]
            for cpb in context.active_pose_bone.children_recursive:
                pbs.append(cpb)
        #Remove keyframes if relevant, user has been prompted in invoke to make sure he wants to
        if self.bHasKfs: 
            if bpy.app.version[0] < 5:   
                actionName =  None     
                if context.object.animation_data is not None and context.object.animation_data.action is not None:
                    actionName = context.object.animation_data.action.name    
                if actionName is not None:
                    for pb in pbs:       
                        for group in bpy.data.actions[actionName].groups:
                            if group.name == pb.name  or group.name == "SWExtraChildBone_" + pb.id_data.name + "_" + pb.name:
                                for fcurve in group.channels:
                                    bpy.data.actions[actionName].fcurves.remove(fcurve)
            else:
                # actionName =  None     
                # actionSlotName = None
                # if context.object.animation_data is not None and context.object.animation_data.action is not None and context.object.animation_data.action_slot is not None:
                #     actionName = context.object.animation_data.action.name  
                #     actionSlotName = context.object.animation_data.action_slot.name_display
                # if actionName is not None and actionSlotName is not None:
                #     for pb in pbs:        
                #         channelbag = bpy_extras.anim_utils.action_get_channelbag_for_slot(context.object.animation_data.action, context.object.animation_data.action_slot)
                #         foundGroup = channelbag.groups.find(pb.name)   
                #         if foundGroup < 0:
                #             foundGroup = channelbag.groups.find("SWExtraChildBone_" + pb.id_data.name + "_" + pb.name)
                #         if foundGroup >= 0:
                #             group = channelbag.groups[foundGroup]
                #             for fcurve in group.channels:
                #                 channelbag.fcurves.remove(fcurve)     

                actionName =  None     
                actionSlotName = None
                if context.object.animation_data is not None and context.object.animation_data.action is not None and context.object.animation_data.action_slot is not None:
                    actionName = context.object.animation_data.action.name  
                    actionSlotName = context.object.animation_data.action_slot.name_display
                if actionName is not None and actionSlotName is not None:  
                    toRemove = []
                    channelbag = bpy_extras.anim_utils.action_get_channelbag_for_slot(arm.animation_data.action, arm.animation_data.action_slot)
                    for pb in pbs:                        
                        for fcurve in channelbag.fcurves:
                            if pb.name in fcurve.data_path.split("\"") or "SWExtraChildBone_" in fcurve.data_path:
                                # channelbag.fcurves.remove(fcurve)   
                                toRemove.append(fcurve)
                    for fcurve in toRemove:
                        channelbag.fcurves.remove(fcurve)         
                
        if self.bArmNotNormed:
           #Apply scale, user has been prompted in invoke to make sure he wants to
           bpy.ops.object.mode_set(mode='OBJECT')
           bpy.ops.object.transform_apply(scale=True)
           bpy.ops.object.mode_set(mode='POSE')

        #Add the bone chain
        boneChain = drbList.boneChainCollection.add()
        boneChain.name = "Bone Chain " + str(len(drbList.boneChainCollection) - 1)
        # boneChain.rootName = pbs[0].name
        # boneChain.armName = pbs[0].id_data.name

        bg = getDRBBGroup(self, context, bpy.context.object)
        createSphereShape(self, context,bpy.context.object)

        #Percentages
        if len(pbs) > 1:
            totalLength = 0            
            for c in pbs[1:]:
                totalLength += (c.matrix.translation - c.parent.matrix.translation).length
            totalTemp = 0
            for c in pbs[1:]:
                totalTemp += (c.matrix.translation - c.parent.matrix.translation).length
                c.cuSwDrbChainPercentage = totalTemp/totalLength
                
        #Add the root
        pbs[0].bIsDRB = True
        pbs[0].bIsDRBRoot = True
        if bpy.app.version[0] > 3:
            bg.assign(pbs[0])
            pbs[0].bone.color.palette = 'CUSTOM'
        else:   
            pbs[0].bone_group = bg
        pbs[0].soSwPrevPos = pbs[0].matrix.translation
        pbs[0].soSwUpdatedPos = Vector(pbs[0].bone.matrix_local.translation)
        pbs[0].soSwPrevFriction = 0.0
        pbs[0].custom_shape = bpy.data.objects.get("SW_Shape_Sphere")
        pbs[0].use_custom_shape_bone_size = False
        height = (pbs[0].tail - pbs[0].head).length
        pbs[0].pSwDrbRadius = height * 0.43
        pbs[0].custom_shape_scale_xyz = [pbs[0].pSwDrbRadius for _ in range(3)]
        pbs[0].custom_shape_rotation_euler[0] = -1.57
        pbs[0].bone.show_wire = True
        pbs[0].lock_scale = [True, True, True]

        bone = boneChain.boneCollection.add()
        bone.boneName = pbs[0].name
        bone.chainPercentage = pbs[0].cuSwDrbChainPercentage
        # bone.armName = pbs[0].id_data.name
        #Add the children and select them
        if len(pbs)>1:
            for c in pbs[1:]:
                if bpy.app.version[0] < 5:
                    c.bone.select = True
                else:
                    c.select = True
                c.bIsDRB = True
                bone = boneChain.boneCollection.add()
                bone.boneName = c.bone.name
                bone.chainPercentage = c.cuSwDrbChainPercentage
                # bone.armName = pbs[0].id_data.name
                if bpy.app.version[0] > 3:
                    bg.assign(c)
                    c.bone.color.palette = 'CUSTOM'
                else:
                    c.bone_group = bg
                c.soSwPrevPos = c.matrix.translation
                c.soSwUpdatedPos = Vector(c.bone.matrix_local.translation)
                c.soSwPrevFriction = 0.0
                c.custom_shape = bpy.data.objects.get("SW_Shape_Sphere")
                height = (c.tail - c.head).length
                c.pSwDrbRadius = height * 0.43
                c.use_custom_shape_bone_size = False
                c.custom_shape_scale_xyz = [c.pSwDrbRadius for _ in range(3)]    
                c.custom_shape_rotation_euler[0] = -1.57  
                c.bone.show_wire = True
                c.lock_scale = [True, True, True]
        
        #Set the active indices to the first bone (root of the chain) and last added chain        
        boneChain.activeBoneIndex = 0
        drbList.activeBoneChainIndex = len(drbList.boneChainCollection)-1

        #Update colors if relevant
        if bpy.app.version[0]>3:
            updateColors(self, context, ['DRB','regular'])
            updateColors(self, context, ['DRB','select'])
            updateColors(self, context, ['DRB','active'])        
        return {'FINISHED'}

class SW_OT_DRBDelOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbdel"
    bl_label = "Delete bone chain"
    bl_description = "Delete the selected bone chain"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.mode != "POSE":
            return False
        arm = context.object
        drbList = arm.data.drbList
        return drbList.activeBoneChainIndex >= 0 and len(drbList.boneChainCollection) and bpy.context.view_layer.objects.get(arm.name) is not None and context.object.override_library is None

    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList
        cachedName = ""

        # remove the physics property
        for b in drbList.boneChainCollection[drbList.activeBoneChainIndex].boneCollection:
            # if arm.name != b.armName:
            #     selectArmatureByName(self, context, b.armName, True)
            #     arm = context.object
            cachedName = copy.copy(arm.name)
            bone = arm.pose.bones[b.boneName]
            for (propName, _) in SwPoseBoneProps:
                bone.property_unset(propName)
            if bpy.app.version[0]>3:
                bg = getDRBBGroup(self, context, bpy.context.object)
                bg.unassign(bone)
                bone.bone.color.palette = 'DEFAULT'
            else:
                bone.bone_group = None
            bone.custom_shape = None
            bone.use_custom_shape_bone_size = True
            bone.custom_shape_scale_xyz = [1.0 for _ in range(3)]
            bone.custom_shape_rotation_euler[0] = -1.57
            bone.bone.show_wire = True

            # clear the amplitude primitives if relevant
            if bpy.context.object.pose.bones.get("SW_AMPPRIM_" + bone.name) is not None:
                removeBone(self, context, bpy.context.object, "SW_AMPPRIM_" + bone.name)
            
            # if it's an extra child, clear it
            if bone.name.startswith("SWExtraChildBone_"):
                bpy.ops.object.mode_set(mode='EDIT') 
                arm.data.edit_bones.remove(arm.data.edit_bones.get(bone.name))
                bpy.ops.object.mode_set(mode='POSE')

        # clear the UI lists and correct the indices
        drbList.boneChainCollection[drbList.activeBoneChainIndex].boneCollection.clear()
        drbList.boneChainCollection.remove(drbList.activeBoneChainIndex)
        drbList.activeBoneChainIndex -= 1
        if drbList.activeBoneChainIndex == -1 and len(drbList.boneChainCollection):
            drbList.activeBoneChainIndex = 0

        # Clear the wind primitive if relevant
        bOtherChainLeftInArmature = False
        for coll in drbList.boneChainCollection:
            if arm.name == cachedName:
                bOtherChainLeftInArmature = True
        if not len(drbList.boneChainCollection) or not bOtherChainLeftInArmature:            
            removeWindPrimitive(self, context, context.object)
        
        return {'FINISHED'}

class SW_OT_DRBClearOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbclear"
    bl_label = "Clear all bone chains"
    bl_description = "Clear all the bone chains"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if not (context.object is not None and context.object.type == "ARMATURE"):
            return False
        arm = context.object
        drbList = arm.data.drbList
        return drbList.activeBoneChainIndex >= 0 and len(drbList.boneChainCollection) and bpy.context.view_layer.objects.get(arm.name) is not None and context.object.override_library is None

    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList

        #view layer sanity check
        for i in range(len(drbList.boneChainCollection)):
            if bpy.context.view_layer.objects.get(arm.name) is None:
                self.report({'ERROR'}, "A chain is not in this view layer!")
                return {'FINISHED'}                
        obj = arm  
        for bone in obj.pose.bones:
            # clear the amplitude primitives if relevant
            if bone.name.startswith("SW_AMPPRIM_"):
                removeBone(self, context, obj, bone.name)
            # clear the extra child if relevant
            if bone.name.startswith("SWExtraChildBone_"):
                bpy.ops.object.mode_set(mode='EDIT') 
                obj.data.edit_bones.remove(obj.data.edit_bones.get(bone.name))
                bpy.ops.object.mode_set(mode='POSE')
        # Clear the wind primitive if relevant
        removeWindPrimitive(self, context, context.object)
        for bone in obj.pose.bones:
            if not bone.bIsDRB:
                continue
            for (propName, _) in SwPoseBoneProps:
                bone.property_unset(propName)
            if bpy.app.version[0]>3:
                bg = getDRBBGroup(self, context, bpy.context.object)
                bg.unassign(bone)
                bone.bone.color.palette = 'DEFAULT'
            else:   
                bone.bone_group = None
            bone.custom_shape = None
            bone.use_custom_shape_bone_size = True
            bone.custom_shape_scale_xyz = [1.0 for _ in range(3)]
            bone.custom_shape_rotation_euler[0] = -1.57
            bone.bone.show_wire = True

        drbList.boneChainCollection.clear()
        drbList.activeBoneChainIndex = -1
        
        return {'FINISHED'}

class SW_OT_DRBSelectAllOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbselectall"
    bl_label = "Select all bone chains"
    bl_description = "Select all the bone chains"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.mode != "POSE":
            return False
        arm = context.object
        drbList = arm.data.drbList
        return drbList.activeBoneChainIndex >= 0 and len(drbList.boneChainCollection)

    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList
        bFirst = True
        for i in range(len(drbList.boneChainCollection)):
            # if arm.name != drbList.boneChainCollection[i].armName:
            #     if not selectArmatureByName(self, context, drbList.boneChainCollection[i].armName, True, False):
            #         continue
            #     arm = context.object
            for b in drbList.boneChainCollection[i].boneCollection:
                if b.boneName not in arm.pose.bones:
                    bpy.ops.sw.ot_drbrescanallchains()
                pb = arm.pose.bones[b.boneName]
                if bpy.app.version[0] < 5:
                    pb.bone.select = True
                else:
                    pb.select = True
                if bFirst:                
                    arm.data.bones.active = pb.bone
                    bFirst = False       
        return {'FINISHED'}

class SW_OT_DRBHideAllOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbhideall"
    bl_label = "Hide/Unhide all bone chains"
    bl_description = "Hide/Unhide all the bone chains"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if not (context.mode == "POSE" or (context.mode == "OBJECT" and context.object is not None and context.object.type == "ARMATURE")):
            return False
        arm = context.object
        drbList = arm.data.drbList
        return drbList.activeBoneChainIndex >= 0 and len(drbList.boneChainCollection)

    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList
        
        if bpy.app.version[0]>3: #make sure that the collection is visible if we go from 3.x to 4.x
            if "DRB" in arm.data.collections: #should always be true by construction
                arm.data.collections["DRB"].is_visible = True
            if "AMPPRIM" in arm.data.collections: #should always be true by construction
                arm.data.collections["AMPPRIM"].is_visible = True
        
        #Grab the drbs and check if there's at least one hidden
        bHide = True
        for i in range(len(drbList.boneChainCollection)):
            # if arm.name != drbList.boneChainCollection[i].armName:
            #     if not selectArmatureByName(self, context, drbList.boneChainCollection[i].armName, True):
            #         continue
            #     arm = context.object
            for b in drbList.boneChainCollection[i].boneCollection:
                if b.boneName not in arm.pose.bones:
                    bpy.ops.sw.ot_drbrescanallchains()
                pb = arm.pose.bones[b.boneName]
                if bpy.app.version[0] < 5:
                    if pb.bone.hide:
                        bHide = False
                        break
                else:
                    if pb.hide:
                        bHide = False
                        break
        for i in range(len(drbList.boneChainCollection)):
            # if arm.name != drbList.boneChainCollection[i].armName:
            #     if not selectArmatureByName(self, context, drbList.boneChainCollection[i].armName, True):
            #         continue
            #     arm = context.object
            drbList.boneChainCollection[i].bHidden = bHide
            for b in drbList.boneChainCollection[i].boneCollection:                
                pb = arm.pose.bones[b.boneName]
                if bpy.app.version[0] < 5:
                    pb.bone.hide = bHide
                    if bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name) is not None:
                        bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name).bone.hide = bHide    
                else:
                    pb.hide = bHide
                    if bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name) is not None:
                        bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name).hide = bHide    
        return {'FINISHED'}

class SW_OT_DRBResetChainOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbresetchain"
    bl_label = "Reset the selected bone chain"
    bl_description = "Reset the selected bone chain"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.mode != "POSE":
            return False
        arm = context.object
        drbList = arm.data.drbList
        return drbList.activeBoneChainIndex >= 0 and len(drbList.boneChainCollection) and bpy.context.view_layer.objects.get(arm.name) is not None

    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList
        
        boneChain = drbList.boneChainCollection[drbList.activeBoneChainIndex]
        if context.selected_pose_bones is not None:
            for c in context.selected_pose_bones:
                if bpy.app.version[0] < 5:
                    c.bone.select = False
                else:
                    c.select = False   
        for b in boneChain.boneCollection:
            # if arm.name != b.armName:
            #     selectArmatureByName(self, context, b.armName, True)
            #     arm = context.object
            if b.boneName not in arm.pose.bones:
                bpy.ops.sw.ot_drbrescanallchains()
            if bpy.app.version[0] < 5:
                drb = arm.data.bones[b.boneName]
            else:
                drb = arm.pose.bones[b.boneName]
            
            drb.select = True
            drb = arm.pose.bones[b.boneName]
            drb.soSwPrevVel = Vector()
            drb.soSwUpdatedPos = Vector(drb.bone.matrix_local.translation)
            drb.matrix_basis = Matrix()
            drb.soSwPrevFriction = 0.0
        if bpy.app.version[0] < 5:
            bpy.context.object.data.bones.active =  arm.data.bones[boneChain.boneCollection[0].boneName]
        else:
            bpy.context.object.data.bones.active =  arm.data.bones[boneChain.boneCollection[0].boneName]
        
        bpy.context.view_layer.update() 
        return {'FINISHED'}
    

class SW_OT_DRBResetAllChainsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbresetallchains"
    bl_label = "Reset all bone chains"
    bl_description = "Reset all the bone chains"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if not (context.mode == "POSE" or (context.mode == "OBJECT" and context.object is not None and context.object.type == "ARMATURE")):
            return False
        arm = context.object
        drbList = arm.data.drbList
        return drbList.activeBoneChainIndex >= 0 and len(drbList.boneChainCollection)

    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList
        
        # prevAct = None
        # if arm is None: #try getting an armature in the layer
        #     for obj in bpy.data.objects:
        #         if obj.type == 'ARMATURE' and bpy.context.view_layer.objects.get(obj.name) is not None:
        #             bpy.context.view_layer.objects.active = obj
        #             arm = context.object
        # else:
        prevAct = arm
        # if arm is None:
        #     return {'FINISHED'}     
        prevMode = bpy.context.object.mode

        for i in range(len(drbList.boneChainCollection)): 
            if not drbList.boneChainCollection[i].bReset:
                continue     
            for b in drbList.boneChainCollection[i].boneCollection:
                # if arm is None or arm.name != b.armName:
                #     if not selectArmatureByName(self, context, b.armName, True):
                #         continue
                #     arm = context.object
                if b.boneName not in arm.pose.bones:
                    bpy.ops.sw.ot_drbrescanallchains()
                drb = arm.pose.bones[b.boneName]
                drb.soSwPrevVel = Vector()
                drb.soSwUpdatedPos = Vector(drb.bone.matrix_local.translation)
                drb.matrix_basis = Matrix()
                drb.soSwPrevFriction = 0.0
        bpy.ops.object.mode_set(mode="OBJECT")
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        if prevAct is not None:
            bpy.context.view_layer.objects.active = prevAct  
            prevAct.select_set(True)
        if prevAct.visible_get():
            bpy.ops.object.mode_set(mode=prevMode)
        bpy.context.view_layer.update()
        
        return {'FINISHED'}     



class SW_OT_DRBResetAmp2Opr(bpy.types.Operator):
    bl_idname = "sw.ot_drbresetamp2"
    bl_label = "Reset the amplitude"
    bl_description = "Reset the amplitude"

    def execute(self, context):
        context.active_pose_bone.pSwDrbAmplitude2 = context.active_pose_bone.pSwDrbAmplitude        
        return {'FINISHED'}

class SW_OT_DRBRescanAllChainsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_drbrescanallchains"
    bl_label = "Rescan all bone chains"
    bl_description = "Rescan all the bone chains"

    bDisplayWarning: bpy.props.BoolProperty(name='bDisplayWarning', default=False,options={'HIDDEN'})

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.object is not None and context.object.type == "ARMATURE" and (context.mode == "POSE" or context.mode == "OBJECT"):
            return True
        

    def draw(self, context):
        if self.bDisplayWarning:
            self.layout.label(text="Some bones in the chain(s) couldn't be found, refresh the chain(s)?")            
    
    def invoke(self, context, event):
        if context.object.override_library is not None:
            return {'FINISHED'}     
        self.bDisplayWarning = False
        if context.screen.is_animation_playing:
            self.bDisplayWarning = True
            bpy.ops.screen.animation_play()
        if self.bDisplayWarning:          
            return context.window_manager.invoke_props_dialog(self,width=500)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList
        pbRoots = set()

        if context.object.override_library is not None:
            return

        removeAmplitudePrimitiveFromAllBones(self, context, arm, arm.pose.bones)

        #First, check if the existing entries are all valid
        for i,bChainColl in reversed(list(enumerate(drbList.boneChainCollection))): #reverse here for easier index management if deleted
            bHasAtLeastOneInvalid = False
            validBone = None
            for b in bChainColl.boneCollection:
                if b.boneName not in arm.pose.bones:
                    bHasAtLeastOneInvalid = True
                else:
                    validBone = arm.pose.bones[b.boneName]
            if validBone is None: #no valid one to get it from, need to create it again from scratch
                drbList.activeBoneChainIndex = i
                drbList.boneChainCollection[drbList.activeBoneChainIndex].boneCollection.clear()
                drbList.boneChainCollection.remove(drbList.activeBoneChainIndex)
                drbList.activeBoneChainIndex -= 1
                if drbList.activeBoneChainIndex == -1 and len(drbList.boneChainCollection):
                    drbList.activeBoneChainIndex = 0
            elif bHasAtLeastOneInvalid:
                bChainColl.boneCollection.clear()
                while(validBone.parent is not None and validBone.parent.bIsDRB):
                    validBone = validBone.parent
                pbs = [validBone]
                while(validBone.children is not None and len(validBone.children) == 1 and validBone.children[0].bIsDRB):
                    validBone = validBone.children[0]
                    pbs.append(validBone)

                if len(pbs) > 1:
                    totalLength = 0            
                    for c in pbs[1:]:
                        totalLength += (c.matrix.translation - c.parent.matrix.translation).length
                    totalTemp = 0
                    for c in pbs[1:]:
                        totalTemp += (c.matrix.translation - c.parent.matrix.translation).length
                        c.cuSwDrbChainPercentage = totalTemp/totalLength 
                
                bone = bChainColl.boneCollection.add()
                bone.boneName = pbs[0].name
                bone.chainPercentage = pbs[0].cuSwDrbChainPercentage
                
                if len(pbs)>1:
                    for c in pbs[1:]:                        
                        bone = bChainColl.boneCollection.add()
                        bone.boneName = c.bone.name
                        bone.chainPercentage = c.cuSwDrbChainPercentage   
            if validBone is not None: #A valid bone was found somewhere, so we were able to update the chain
                pbRoots.add(bChainColl.boneCollection[0].boneName)        

        #Then, check if unregistered chains exist, if so create them
        for pBone in arm.pose.bones:
            if pBone.bIsDRB and (pBone.parent is None or not pBone.parent.bIsDRB) and pBone.name not in pbRoots: #we found a root unassigned
                bChainColl = drbList.boneChainCollection.add()
                bChainColl.name = "Bone Chain " + str(len(drbList.boneChainCollection) - 1)
                validBone = pBone
                while(validBone.parent is not None and validBone.parent.bIsDRB):
                    validBone = validBone.parent
                pbs = [validBone]
                while(validBone.children is not None and len(validBone.children) == 1 and validBone.children[0].bIsDRB):
                    validBone = validBone.children[0]
                    pbs.append(validBone)

                if len(pbs) > 1:
                    totalLength = 0            
                    for c in pbs[1:]:
                        totalLength += (c.matrix.translation - c.parent.matrix.translation).length
                    totalTemp = 0
                    for c in pbs[1:]:
                        totalTemp += (c.matrix.translation - c.parent.matrix.translation).length
                        c.cuSwDrbChainPercentage = totalTemp/totalLength 
                
                bone = bChainColl.boneCollection.add()
                bone.boneName = pbs[0].name
                bone.chainPercentage = pbs[0].cuSwDrbChainPercentage
                
                if len(pbs)>1:
                    for c in pbs[1:]:                        
                        bone = bChainColl.boneCollection.add()
                        bone.boneName = c.bone.name
                        bone.chainPercentage = c.cuSwDrbChainPercentage

        addAmplitudePrimitiveForAllBones(self, context, arm, arm.pose.bones)
        if self.bDisplayWarning:
            bpy.ops.screen.animation_play()
        return {'FINISHED'}     

##############################
# SRB
##############################

def AddSRBOprSanityChecks(self, context):

    bHasADrb = False
    bIsAnSrb = False
    for pb in context.selected_pose_bones:
        if pb.bIsDRB:
            bHasADrb = True
            break
        if pb.bIsSRB:
            bIsAnSrb = True
            break
    if bHasADrb:
        self.report({'ERROR'}, "A bone selected is in a bone chain")
        return False        
    if bIsAnSrb:
        self.report({'ERROR'}, "A bone selected is a collider")
        return False
    return True


class SW_OT_SRBAddOpr(bpy.types.Operator):
    bl_idname = "sw.ot_srbadd"
    bl_label = "Create collider"
    bl_description = "Create a collider for all selected bones"

    colliderType : bpy.props.EnumProperty(
        name="Collider type",
        description="The shape of the collider",
        items= [
            ('S', "Sphere", "Add a sphere collider", 'MESH_UVSPHERE',0),
            ('C', "Cylinder", "Add a cylinder collider", 'MESH_CYLINDER',1)
        ]
    )

    @classmethod
    def poll(self, context):
        if bpy.app.version[0] < 5:
            return context.active_pose_bone is not None and context.active_pose_bone.bone.select and context.mode == "POSE" and context.object.override_library is None
        else:
            return context.active_pose_bone is not None and context.active_pose_bone.select and context.mode == "POSE" and context.object.override_library is None

    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "colliderType")

    def execute(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        

        #Checks
        if not AddSRBOprSanityChecks(self, context):
            return {'FINISHED'}
        collBones = []
        #Add the collider
        for pb in bpy.context.selected_pose_bones:
            if pb is not None:
                collider = srbList.colliderCollection.add()
                collider.colliderName = "Collider_" + pb.name
                collider.name = "SRB_Collider_" + str(len(srbList.colliderCollection) - 1)
                collider.type = self.colliderType
                collider.armName = context.active_pose_bone.id_data.name

                bg = getSRBBGroup(self, context, bpy.context.object)
                if self.colliderType == 'S':
                    createSphereShape(self, context, bpy.context.object)
                elif self.colliderType == 'C':
                    createCylinderShape(self, context, bpy.context.object)
            
                height = (pb.tail - pb.head).length
                refBoneName = pb.name
                pBone = addBone(self, context, bpy.context.object, collider.name,refBoneName, inheritScale=False)
                pBone.bIsSRB = True
                pBone.pSwSrbParentName = pBone.parent.name
                if bpy.app.version[0] > 3:
                    bg.assign(pBone)
                    pBone.bone.color.palette = 'CUSTOM'
                else:
                    pBone.bone_group = bg
                if self.colliderType == 'S':
                    pBone.custom_shape = bpy.data.objects.get("SW_Shape_Sphere")
                    pBone.pSwSrbRadius = height * 0.3
                    pBone.custom_shape_scale_xyz = [pBone.pSwSrbRadius for _ in range(3)]
                elif self.colliderType == 'C':
                    pBone.custom_shape = bpy.data.objects.get("SW_Shape_Cylinder")
                    pBone.pSwSrbDepth = height
                    pBone.pSwSrbRadius = height * 0.3
                    pBone.custom_shape_scale_xyz = [pBone.pSwSrbRadius for _ in range(3)]
                    pBone.custom_shape_scale_xyz[2] = pBone.pSwSrbDepth         
                pBone.use_custom_shape_bone_size = False                
                pBone.custom_shape_rotation_euler[0] = -1.57
                pBone.bone.show_wire = True
                pBone.bone.use_deform = False      
                collBones.append(pBone)  

        #Set the active index to the last added collider
        srbList.activeColliderIndex = len(srbList.colliderCollection)-1

        for collBone in collBones:
            if bpy.app.version[0] < 5:
                collBone.bone.select = True
            else:
                collBone.select = True

        #Update colors if relevant
        if bpy.app.version[0]>3:
            updateColors(self, context, ['SRB','regular'])
            updateColors(self, context, ['SRB','select'])
            updateColors(self, context, ['SRB','active'])
        
        return {'FINISHED'}

class SW_OT_SRBDelOpr(bpy.types.Operator):
    bl_idname = "sw.ot_srbdel"
    bl_label = "Delete collider"
    bl_description = "Delete the selected collider"

    @classmethod
    def poll(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        
        return srbList.activeColliderIndex >= 0 and len(srbList.colliderCollection) and context.mode == "POSE" and bpy.context.view_layer.objects.get(arm.name) is not None and context.object.override_library is None

    def execute(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        

        collider = srbList.colliderCollection[srbList.activeColliderIndex]
        # if arm.name != collider.armName:
        #     selectArmatureByName(self, context, collider.armName, True)
        #     arm = context.object
        removeBone(self, context, bpy.context.object, collider.name)
        srbList.colliderCollection.remove(srbList.activeColliderIndex)
        srbList.activeColliderIndex -= 1 
        if srbList.activeColliderIndex == -1 and len(srbList.colliderCollection):
            srbList.activeColliderIndex = 0
        
        return {'FINISHED'}

class SW_OT_SRBClearOpr(bpy.types.Operator):
    bl_idname = "sw.ot_srbclear"
    bl_label = "Clear all colliders"
    bl_description = "Clear all the colliders"

    @classmethod
    def poll(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        
        return srbList.activeColliderIndex >= 0 and len(srbList.colliderCollection) and context.mode == "POSE" and context.object.override_library is None

    def execute(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        

        #view layer sanity check
        for collider in srbList.colliderCollection:
            if bpy.context.view_layer.objects.get(collider.armName) is None:
                self.report({'ERROR'}, "A collider is not in this view layer!")
                return {'FINISHED'}

        # for obj in bpy.data.objects:
        #     if obj.type == 'ARMATURE':
        #         selectArmatureByName(self, context, obj.name, True)
        obj = arm
        for bone in obj.pose.bones:
            if not bone.bIsSRB:
                continue
            removeBone(self, context, obj, bone.name)
        # selectArmatureByName(self, context, arm.name, True)
        # for collider in srbList.colliderCollection:
        #     removeBone(self, context, bpy.context.object, collider.name)

        srbList.colliderCollection.clear()
        srbList.activeColliderIndex = -1
        
        return {'FINISHED'}

class SW_OT_SRBSelectAllOpr(bpy.types.Operator):
    bl_idname = "sw.ot_srbselectall"
    bl_label = "Select all colliders"
    bl_description = "Select all the colliders"

    @classmethod
    def poll(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        
        return srbList.activeColliderIndex >= 0 and len(srbList.colliderCollection) and context.mode == "POSE"

    def execute(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        
        bFirst = True
        for collider in srbList.colliderCollection:
            # if arm.name != collider.armName:
            #     if not selectArmatureByName(self, context, collider.armName, True, False):
            #         continue
            #     arm = context.object
            if collider.name not in arm.pose.bones:
                bpy.ops.sw.ot_srbrescanallchains()
            pb = arm.pose.bones[collider.name]
            if bpy.app.version[0] < 5:
                pb.bone.select = True
            else:
                pb.select = True
            if bFirst:                
                context.object.data.bones.active = pb.bone
                bFirst = False
        return {'FINISHED'}

class SW_OT_SRBHideAllOpr(bpy.types.Operator):
    bl_idname = "sw.ot_srbhideall"
    bl_label = "Hide/Unhide all colliders"
    bl_description = "Hide/Unhide all the colliders"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if not (context.mode == "POSE" or (context.mode == "OBJECT" and context.object is not None and context.object.type == "ARMATURE")):
            return False
        arm = context.object        
        srbList = arm.data.srbList        
        return srbList.activeColliderIndex >= 0 and len(srbList.colliderCollection)

    def execute(self, context):
        scene = context.scene
        arm = context.object
        srbList = arm.data.srbList        

        if bpy.app.version[0]>3: #make sure that the collection is visible if we go from 3.x to 4.x
            if "SRB" in arm.data.collections: #should always be true by construction
                arm.data.collections["SRB"].is_visible = True
        
        #Grab the drbs and check if there's at least one hidden
        bHide = True
        for collider in srbList.colliderCollection:
            # if arm.name != collider.armName:
            #     if not selectArmatureByName(self, context, collider.armName, True):
            #         continue
            #     arm = context.object
            #     if bpy.app.version[0]>3: #make sure that the collection is visible if we go from 3.x to 4.x
            #         arm.data.collections["SRB"].is_visible = True
            if collider.name not in arm.pose.bones:
                bpy.ops.sw.ot_srbrescanallchains()
            if bpy.app.version[0] < 5:                
                pb = arm.pose.bones[collider.name]
                if pb.bone.hide:
                    bHide = False
                    break
            else:
                pb = arm.pose.bones[collider.name]
                if pb.hide:
                    bHide = False
                    break
        arm = context.object
        for collider in srbList.colliderCollection:            
            pb = arm.pose.bones[collider.name]
            if bpy.app.version[0] < 5:
                pb.bone.hide = bHide
            else:
                pb.hide = bHide
        return {'FINISHED'}

class SW_OT_SRBRescanAllOpr(bpy.types.Operator):
    bl_idname = "sw.ot_srbrescanallchains"
    bl_label = "Rescan all colliders"
    bl_description = "Rescan all the colliders"

    bDisplayWarning: bpy.props.BoolProperty(name='bDisplayWarning', default=False,options={'HIDDEN'})

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.object is not None and context.object.type == "ARMATURE" and (context.mode == "POSE" or context.mode == "OBJECT"):
            return True        

    def draw(self, context):
        if self.bDisplayWarning:
            self.layout.label(text="Some colliders couldn't be found, refresh the collider list?")            
    
    def invoke(self, context, event):
        if context.object.override_library is not None:
            return
        self.bDisplayWarning = False
        if context.screen.is_animation_playing:
            self.bDisplayWarning = True
            bpy.ops.screen.animation_play()
        if self.bDisplayWarning:          
            return context.window_manager.invoke_props_dialog(self,width=500)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        arm = context.object
        if context.object.override_library is not None:
            return {'FINISHED'}     
        srbList = arm.data.srbList
        seenSrbs = set()
        #First, check if the existing entries are all valid
        for i, collider in reversed(list(enumerate(srbList.colliderCollection))):#reverse here for easier index management if deleted
            if collider.name not in arm.pose.bones:
                srbList.activeColliderIndex = i
                srbList.colliderCollection.remove(srbList.activeColliderIndex)
                srbList.activeColliderIndex -= 1 
                if srbList.activeColliderIndex == -1 and len(srbList.colliderCollection):
                    srbList.activeColliderIndex = 0   
            else:
                seenSrbs.add(collider.name)    

        if self.bDisplayWarning:
            bpy.ops.screen.animation_play()

        #Then, check if unregistered chains exist, if so create them
        for pb in arm.pose.bones:
            if pb.bIsSRB and pb.parent is not None and pb.name not in seenSrbs:
                collider = srbList.colliderCollection.add()
                collider.colliderName = "Collider_" + pb.parent.name
                collider.name = pb.name
                collider.type = 'C' if pb.custom_shape == "SW_Shape_Cylinder" else 'S'
                collider.armName = context.active_pose_bone.id_data.name
                pb.pSwSrbParentName = pb.parent.name
                srbList.activeColliderIndex = len(srbList.colliderCollection)-1
        return {'FINISHED'}

##############################
# Curve
##############################

class SW_OT_CURVEAddOpr(bpy.types.Operator):
    bl_idname = "sw.ot_curveadd"
    bl_label = "Create Curve"
    bl_description = "Create a new curve"

    curveType : bpy.props.EnumProperty(
        name="Curve type",
        items= [
            ('P', "Parameter", "Add a parameter curve", 'MOD_HUE_SATURATION',0),
            ('W', "Wind", "Add a wind curve", 'FORCE_WIND',1)
        ]
    )

    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "curveType")

    @classmethod
    def poll(self, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def execute(self, context):
        scene = context.scene
        arm = context.object
        curveList = arm.data.curveList

        #Add the curve
        curve = curveList.curveCollection.add()
        curve.name = "Curve " + str(len(curveList.curveCollection) - 1)
        arm.activeCurveIndex = len(curveList.curveCollection) - 1

        #bpy.ops.brush.add()
        curve.brush = bpy.data.brushes.new("SwingyBrush")

        if self.curveType == "P":
            curve.brush.name = "ParamCurve"
            curve.brush.swName = "SWParamCurve"
            curve.brush.cupSwType = 'P'
        elif self.curveType == "W":
            curve.brush.name = "WindCurve"
            curve.brush.cupSwPeriod = bpy.context.scene.frame_end - bpy.context.scene.frame_start
            curve.brush.swName = "SWWindCurve"
            curve.brush.cupSwType = 'W'
            if bpy.app.version[0] < 5:
                curve.brush.curve.clip_min_y = -1
                curve.brush.curve.clip_max_y = 1
                curve.brush.curve.update()
                curve.brush.curve.reset_view()
            else:
                curve.brush.curve_distance_falloff.clip_min_y = -1
                curve.brush.curve_distance_falloff.clip_max_y = 1
                curve.brush.curve_distance_falloff.update()
                curve.brush.curve_distance_falloff.reset_view()

        return {'FINISHED'}

class SW_OT_CURVEDelOpr(bpy.types.Operator):
    bl_idname = "sw.ot_curvedel"
    bl_label = "Delete Curve"
    bl_description = "Delete the selected curve"

    @classmethod
    def poll(self, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def execute(self, context):
        scene = context.scene
        arm = context.object
        curveList = arm.data.curveList

        if curveList.curveCollection[arm.activeCurveIndex].brush is not None:
            bpy.data.brushes.remove(curveList.curveCollection[arm.activeCurveIndex].brush)
        curveList.curveCollection.remove(arm.activeCurveIndex)       
        arm.activeCurveIndex -= 1
        if arm.activeCurveIndex == -1 and len(curveList.curveCollection):
            arm.activeCurveIndex = 0
        return {'FINISHED'}

class SW_OT_CURVEClearOpr(bpy.types.Operator):
    bl_idname = "sw.ot_curveclear"
    bl_label = "Clear all curves"
    bl_description = "Clear all the curves"

    @classmethod
    def poll(self, context):
        scene = context.scene
        return context.object is not None and context.object.type == "ARMATURE"

    def execute(self, context):
        scene = context.scene
        arm = context.object
        curveList = arm.data.curveList
        while(len(curveList.curveCollection)):
            if curveList.curveCollection[0].brush is not None:
                bpy.data.brushes.remove(curveList.curveCollection[0].brush)
            curveList.curveCollection.remove(0)
        arm.activeCurveIndex = -1
        return {'FINISHED'}

##############################
# Scene params
##############################

class SW_OT_SceneResetDRBColorsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_sceneresetdrbcolors"
    bl_label = "Reset the color scheme"
    bl_description = "Reset the color scheme"

    def execute(self, context):
        scene = context.scene
        arm = context.object
        scene.drbColors.property_unset("regular")
        scene.drbColors.property_unset("select")
        scene.drbColors.property_unset("active")
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                arm = obj
                # if not selectArmatureByName(self, context, obj.name, True):
                #     continue
                if bpy.app.version[0]>3:
                    updateColors(self, context, ['DRB','regular'])
                    updateColors(self, context, ['DRB','select'])
                    updateColors(self, context, ['DRB','active'])
                else:
                    if "DRB" not in arm.pose.bone_groups:
                        continue                
                    bg = arm.pose.bone_groups.get("DRB")
                    bg.colors.normal = scene.drbColors.regular
                    bg.colors.select = scene.drbColors.select
                    bg.colors.active = scene.drbColors.active
        #select all
        arm = context.object
        drbList = arm.data.drbList
        bFirst = True        
        for i in range(len(drbList.boneChainCollection)):
            # if arm.name != drbList.boneChainCollection[i].armName:
            #     if not selectArmatureByName(self, context, drbList.boneChainCollection[i].armName, True, False):
            #         continue
            #     arm = context.object
            for b in drbList.boneChainCollection[i].boneCollection:  
                if b.boneName in arm.pose.bones:              
                    pb = arm.pose.bones[b.boneName]
                    if bpy.app.version[0] < 5:
                        pb.bone.select = True
                    else:
                        pb.select = True
                    if bFirst:                
                        arm.data.bones.active = pb.bone
                        bFirst = False       
        return {'FINISHED'}
    
class SW_OT_SceneResetLinkColorsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_sceneresetlinkcolors"
    bl_label = "Reset the color scheme"
    bl_description = "Reset the color scheme"

    def execute(self, context):
        context.scene.swLinkColor.property_unset("regular")  
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}
    
class SW_OT_SceneResetInactiveLinkColorsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_sceneresetinactivelinkcolors"
    bl_label = "Reset the color scheme"
    bl_description = "Reset the color scheme"

    def execute(self, context):
        context.scene.swLinkColor.property_unset("inactive")  
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}

class SW_OT_SceneResetMaxLLinkColorsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_sceneresetmaxllinkcolors"
    bl_label = "Reset the color scheme"
    bl_description = "Reset the color scheme"

    def execute(self, context):
        context.scene.swLinkColor.property_unset("maxL")  
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}

class SW_OT_SceneResetSRBColorsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_sceneresetsrbcolors"
    bl_label = "Reset the color scheme"
    bl_description = "Reset the color scheme"

    def execute(self, context):
        scene = context.scene
        arm = context.object
        scene.srbColors.property_unset("regular")
        scene.srbColors.property_unset("select")
        scene.srbColors.property_unset("active")  
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                arm = obj
                # if not selectArmatureByName(self, context, obj.name, True):
                #     continue
                if bpy.app.version[0]>3:
                    updateColors(self, context, ['SRB','regular'])
                    updateColors(self, context, ['SRB','select'])
                    updateColors(self, context, ['SRB','active'])
                else:
                    if "SRB" not in arm.pose.bone_groups:
                        continue                
                    bg = arm.pose.bone_groups.get("SRB")  
                    bg.colors.normal = scene.srbColors.regular
                    bg.colors.select = scene.srbColors.select
                    bg.colors.active = scene.srbColors.active   
        #select all 
        arm = context.object
        srbList = arm.data.srbList        
        bFirst = True
        for collider in srbList.colliderCollection:
            # if arm.name != collider.armName:
            #     if not selectArmatureByName(self, context, collider.armName, True, False):
            #         continue
            #     arm = context.object
            if collider.name in arm.pose.bones:
                pb = arm.pose.bones[collider.name]
                if bpy.app.version[0] < 5:
                    pb.bone.select = True
                else:
                    pb.select = True
                if bFirst:                
                    context.object.data.bones.active = pb.bone
                    bFirst = False
        return {'FINISHED'}

class SW_OT_SceneResetAMPPRIMColorsOpr(bpy.types.Operator):
    bl_idname = "sw.ot_sceneresetampprimcolors"
    bl_label = "Reset the color scheme"
    bl_description = "Reset the color scheme"

    def execute(self, context):
        scene = context.scene
        arm = context.object
        scene.ampPrimColors.property_unset("regular")
        scene.ampPrimColors.property_unset("select")
        scene.ampPrimColors.property_unset("active")  
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                arm = obj
                # if not selectArmatureByName(self, context, obj.name, True, False):
                #     continue
                if bpy.app.version[0]>3:
                    updateColors(self, context, ['AMPPRIM','regular'])
                else:
                    if "AMPPRIM" not in arm.pose.bone_groups:
                        continue                
                    bg = arm.pose.bone_groups.get("AMPPRIM")
                    bg.colors.normal = scene.ampPrimColors.regular      
        return {'FINISHED'}

class SW_OT_ArmResetWindColorOpr(bpy.types.Operator):
    bl_idname = "sw.ot_armresetwindcolor"
    bl_label = "Reset the color scheme"
    bl_description = "Reset the color scheme"

    def execute(self, context):
        scene = context.scene
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                arm = obj
                # if not selectArmatureByName(self, context, obj.name, True, False):
                #     continue
                if bpy.app.version[0]>3:
                    if "SWWIND" not in arm.data.collections:
                        continue
                else:
                    if "SWWIND" not in arm.pose.bone_groups:
                        continue
                arm.windColor.property_unset("regular")
                arm.windColor.property_unset("select")
                arm.windColor.property_unset("active")
                if bpy.app.version[0]>3:
                    updateColors(self, context, ['SWWIND','regular'])
                else:               
                    bg = arm.pose.bone_groups.get("SWWIND")
                    bg.colors.normal = arm.windColor.regular
                    bg.colors.select = arm.windColor.select
                    bg.colors.active = arm.windColor.active
        return {'FINISHED'}

class SWT_OT_Bake(bpy.types.Operator):
    bl_idname = "sw.bake"
    bl_label = "Special bake"
    bl_description = "Bake the bone chains' movement to keyframes"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        if context.mode != "POSE":
            return False
        arm = context.object
        drbList = arm.data.drbList
        return drbList.activeBoneChainIndex >= 0 and len(drbList.boneChainCollection)
    
    def draw(self, context):
        layout = self.layout
        if context.scene.sync_mode != 'NONE' or context.scene.bSwForceDropBake:
            if context.scene.sync_mode != 'NONE':
                layout.label(text="The playback mode is currently not set to \"play every frame\". ")
            layout.label(text="Do you want to bake the simulation as it is played in the viewport? ")          
            layout.label(text="IMPORTANT: Don't touch anything before the full simulation has played and keyframes have been baked!")
    
    def invoke(self, context, event):
        if context.scene.sync_mode != 'NONE' or context.scene.bSwForceDropBake: 
            return context.window_manager.invoke_props_dialog(self,width=600)
        return self.execute(context)

    def execute(self,context):
        scene = context.scene
        arm = context.object
        drbList = arm.data.drbList

        drbPropsToKeep = ['pSwDrbDamping', 'pSwDrbDrag', 'pSwDrbStiffness', 'pSwDrbWindFactor', 'pSwDrbGravityFactor', 'pSwDrbFriction', 
                          'pSwDrbRadius', 'pSwDrbLockRoll', 'pSwDrbAmplitude', 'pSwDrbAmplitude2', 'pSwDrbCollLayer', 'pSwDrbCollIntra', 
                          'cupSwDrbDamping', 'cupSwDrbDrag', 'cupSwDrbStiffness', 'cupSwDrbWindFactor', 'cupSwDrbGravityFactor']
        # scene.bSwIsBaking = True #Baking handle doesn't seem to catch, using this hack... Cancelling issue?   
        # scene.armBakingName = context.object.data.bones.active.id_data.name
        # bpy.ops.nla.bake(frame_start=scene.frame_start,frame_end=scene.frame_end,step=1,use_current_action=True, only_selected=True, visual_keying=True)
        # scene.bSwIsBaking = False
        # scene.armBakingName = ""
        # return {'FINISHED'}

        #view layer sanity check
        if bpy.context.view_layer.objects.get(arm.name) is None:
            self.report({'ERROR'}, "The armature is not in this view layer!")
            return {'FINISHED'}

        actionName =  None 
        if arm.animation_data is not None and arm.animation_data.action is not None:
            actionName = arm.animation_data.action.name
        if bpy.app.version[0] >= 5:
            actionSlotName = None
            if arm.animation_data is not None and arm.animation_data.action is not None and arm.animation_data.action_slot is not None:
                actionSlotName = arm.animation_data.action_slot.name_display

        if bpy.app.version[0]>3:
            if "DRB" in arm.data.collections: #should always be true by construction
                arm.data.collections["DRB"].is_visible = True
        bHasOneDrb = False
        for pb in arm.pose.bones:
            if not pb.bIsDRB:
                if bpy.app.version[0] < 5:
                    pb.bone.select = False
                else:
                    pb.select = False
                continue
            context.object.data.bones.active = context.object.data.bones[pb.name]
            bHasOneDrb = True
            pb.bone.hide = False    
            if bpy.app.version[0] < 5:
                pb.bone.select = True
            else:
                pb.select = True

            if bpy.app.version[0] < 5:    
                if actionName is not None:
                    for group in bpy.data.actions[actionName].groups:
                        if group.name == pb.name:
                            for fcurve in group.channels:
                                bpy.data.actions[actionName].fcurves.remove(fcurve)
            else:
                toRemove = []
                if actionName is not None and actionSlotName is not None:      
                    channelbag = bpy_extras.anim_utils.action_get_channelbag_for_slot(arm.animation_data.action, arm.animation_data.action_slot)
                    for fcurve in channelbag.fcurves:
                        if pb.name in fcurve.data_path.split("\""):
                            toRemove.append(fcurve)
                    for fcurve in toRemove:
                        channelbag.fcurves.remove(fcurve)       


        if bHasOneDrb:
            scene.bSwIsBaking = True #Baking handle doesn't seem to catch, using this hack... Cancelling issue?   
            scene.armBakingName = arm.name
            scene["FrameSeen"] = None
            scene.bSwDropBake = False if scene.sync_mode == 'NONE' and not scene.bSwForceDropBake else True
            if scene.bSwDropBake:
                scene["BoneKFMap"] = {}
                scene["SwPrevFrame"] = -9999
                if bpy.context.screen.is_animation_playing:
                    bpy.ops.screen.animation_play() 
                bpy.context.scene.frame_set(bpy.context.scene.frame_start)
                bpy.ops.screen.animation_play() 
                scene.armBakingName = ""
                return {'FINISHED'}                    
            bpy.ops.nla.bake(frame_start=scene.frame_start,frame_end=scene.frame_end,step=1,use_current_action=True, only_selected=True, visual_keying=True)
            scene.bSwIsBaking = False
            scene.armBakingName = ""

        if scene.bSwClearOnBake and context.object.override_library is None:       
            obj = arm
            for bone in obj.pose.bones:
                # clear the amplitude primitives if relevant
                if bone.name.startswith("SW_AMPPRIM_"):
                    removeBone(self, context, obj, bone.name)
                # clear the extra child if relevant
                if bone.name.startswith("SWExtraChildBone_"):
                    bpy.ops.object.mode_set(mode='EDIT') 
                    obj.data.edit_bones.remove(obj.data.edit_bones.get(bone.name))
                    bpy.ops.object.mode_set(mode='POSE')
            # Clear the wind primitive if relevant
            removeWindPrimitive(self, context, context.object)
            for bone in obj.pose.bones:
                if not bone.bIsDRB:
                    continue
                for (propName, _) in SwPoseBoneProps:
                    if propName not in drbPropsToKeep:
                        bone.property_unset(propName)
                if bpy.app.version[0]>3:
                    bg = getDRBBGroup(self, context, bpy.context.object)
                    bg.unassign(bone)
                    bone.bone.color.palette = 'DEFAULT'
                else:
                    bone.bone_group = None
                bone.custom_shape = None
                bone.use_custom_shape_bone_size = True
                bone.custom_shape_scale_xyz = [1.0 for _ in range(3)]
                bone.custom_shape_rotation_euler[0] = -1.57
                bone.bone.show_wire = True
            selectArmatureByName(self, context, arm.name, True)
            drbList.boneChainCollection.clear()
            drbList.activeBoneChainIndex = -1

        return {'FINISHED'}


class SWT_OT_LinkAppend(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "sw.linkappend"
    bl_label = "Chain/collider data linker"
    bl_description = "Update the bone chains/colliders from another .blend file"

    filter_glob: StringProperty( default='*.blend', options={'HIDDEN'} )
    
    @classmethod
    def poll(cls, context):
        return context.mode == "POSE" and context.active_pose_bone is not None
    
    def execute(self,context):
        scene = context.scene
        drbList = scene.drbList  
        srbList = scene.srbList  
        linkList = scene.swLinkList    

        temp = set()
        #get the scenes from the other blend file (we will only get the first one, check which one has been added taking renaming into account)
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            for s in bpy.data.scenes:
                temp.add(s.name)
            data_to.scenes = data_from.scenes

        for s in bpy.data.scenes:
            if s.name not in temp:
                # Update the drbList
                for bChainExternal in bpy.data.scenes[s.name].drbList.boneChainCollection:
                    bChainNew = drbList.boneChainCollection.add()
                    for k, v in bChainExternal.items():
                        bChainNew[k] = v
                    bChainNew.name = "Bone Chain " + str(len(drbList.boneChainCollection) - 1)
                    bChainNew.armName = context.active_pose_bone.id_data.name
                    for b in bChainNew.boneCollection:
                        b.armName = context.active_pose_bone.id_data.name
                # Update the srbList
                for colliderExternal in bpy.data.scenes[s.name].srbList.colliderCollection:
                    colliderNew = srbList.colliderCollection.add()
                    for k, v in colliderExternal.items():
                        colliderNew[k] = v
                    
                    colliderNew.armName = context.active_pose_bone.id_data.name  
                # Update the link list
                for linkExternal in bpy.data.scenes[s.name].swLinkList.linkCollection:
                    linkNew = linkList.linkCollection.add()
                    for k, v in linkExternal.items():
                        linkNew[k] = v
                    linkNew.name = linkExternal.name
                    for b in linkNew.linkedBones:
                        b.armName = context.active_pose_bone.id_data.name
                # Remove added scene    
                for obj in bpy.data.scenes[s.name].objects:
                    bpy.data.objects.remove(obj, do_unlink=True)    
                bpy.data.scenes.remove(bpy.data.scenes[s.name], do_unlink=True)        

        return {'FINISHED'}

class SWT_OT_KFAllProps(bpy.types.Operator):
    bl_idname = "sw.keyframeallprops"
    bl_label = "Keyframe the property for all selected bones"
    bl_description = "Keyframe the property for all selected bones"
    
    propName: bpy.props.StringProperty(
        default=''
    )

    def execute(self,context):
        for pb in bpy.context.selected_pose_bones:
            pb.keyframe_insert(data_path=self.propName, frame=bpy.context.scene.frame_current)
        return {'FINISHED'}

class SWT_OT_LoadParameters(bpy.types.Operator):
    bl_idname = "sw.loadparams"
    bl_label = "Load parameters"
    bl_description = "Load the bone chains' parameters from file"

    def execute(self,context):
        scene = context.scene
        try:
            f = open(scene.swParamPath)
        except FileNotFoundError:
            self.report({'ERROR'}, "File not found.")
        else:
            with f:
                data = json.load(f)
                if "drbs" in data:
                    for pbName in data["drbs"]:
                        armN, pbN = pbName.split("|&|&")
                        if armN in bpy.data.objects:
                            if pbN in bpy.data.objects[armN].pose.bones:
                                pb = bpy.data.objects[armN].pose.bones[pbN]
                                for prm, val in data["drbs"][pbName].items():
                                    setattr(pb, prm, val)
        return {'FINISHED'}

class SWT_OT_SaveParameters(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "sw.saveparams"
    bl_label = "Save parameters"
    bl_description = "Save the current bone chains' parameters"

    filename_ext = ".swgbp"
    filter_glob: StringProperty(default="*.swgbp", options={'HIDDEN'})

    def execute(self,context):
        if not self.filepath:
            raise Exception("filepath not set")
        
        # saveParams = ["pSwDrbDamping","pSwDrbWindFactor","pSwDrbGravityFactor","pSwDrbDrag",\
        #             "pSwDrbStiffness", "pSwDrbRadius","pSwDrbAmplitude","pSwDrbAmplitude2",\
        #             "pSwDrbCollLayer","pSwDrbLockRoll","pSwDrbShowAmplitude","pSwDrbAmplitudeType",\
        #             "cupSwDrbDamping","cupSwDrbDrag","cupSwDrbWindFactor","cupSwDrbGravityFactor",\
        #             "cupSwDrbStiffness"]
        saveParams = ["pSwDrbDamping","pSwDrbWindFactor","pSwDrbGravityFactor","pSwDrbDrag",\
                    "pSwDrbStiffness", "pSwDrbRadius","pSwDrbAmplitude","pSwDrbAmplitude2"]

        swgParams = {}
        swgParams["addonVersion"] = [addon.bl_info.get('version', (-1,-1,-1)) for addon in addon_utils.modules() if addon.bl_info['name'] == "Swingy Bone Physics"][0]
        swgParams["drbs"] = {}
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                arm = obj
                for pb in arm.pose.bones:
                    if not pb.bIsDRB:
                        continue
                    swgParams["drbs"][arm.name + "|&|&" + pb.name] = {}
                    for prm in saveParams:
                        swgParams["drbs"][arm.name + "|&|&" + pb.name][prm] = getattr(pb, prm)
        json.dump(swgParams,open(self.filepath, "w"), indent=2)
        
        return {'FINISHED'}
    

##############################
# Links
##############################

class SW_OT_LinkAddOpr(bpy.types.Operator):
    bl_idname = "sw.ot_linkadd"
    bl_label = "Link swingy bones"
    bl_description = "Link the two swingy bones"

    @classmethod
    def poll(self, context):
        if bpy.app.version[0] < 5:
            return context.active_pose_bone is not None and context.active_pose_bone.bone.select and context.mode == "POSE"
        else:
            return context.active_pose_bone is not None and context.active_pose_bone.select and context.mode == "POSE"
    
    def execute(self, context):
        scene = context.scene
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList


        bpy.ops.object.mode_set(mode='POSE')        

        pbs = [pb for pb in context.selected_pose_bones]
        apb = context.active_pose_bone
        pairs = []
        if len(pbs) == 2:
            pairs = [[pbs[0], pbs[1]]]
        elif len(pbs) == 3:
            for pb in pbs:
                if pb == context.active_pose_bone:
                    continue
                pairs.append([apb, pb])
        else:
            self.report({'ERROR'}, "Only select two or three bones!")

        #validity check
        for pair in pairs:
            for pb in pair:
                if not pb.bIsDRB:
                    self.report({'ERROR'}, "One of the bones is not in a bone chain!")
                    return {'FINISHED'}
                if pb.parent is None or not pb.parent.bIsDRB:
                    self.report({'ERROR'}, "Bone chain root bones cannot be linked!")
                    return {'FINISHED'}
            if pair[0] in pair[1].children_recursive or pair[1] in pair[0].children_recursive:
                self.report({'ERROR'}, "Bones in the same chain cannot be linked!")
                return {'FINISHED'}
                
        for pair in pairs:
            #Does the constraint already exist?
            bExists = False
            for otherLink in linkList.linkCollection:
                o0, o1 = otherLink.linkedBones[0], otherLink.linkedBones[1]
                if (o0.boneName == pair[0].name and o0.armName == pair[0].id_data.name and o1.boneName == pair[1].name and o1.armName == pair[1].id_data.name) \
                or (o1.boneName == pair[0].name and o1.armName == pair[0].id_data.name and o0.boneName == pair[1].name and o0.armName == pair[1].id_data.name):
                    bExists = True
            if bExists:
                continue

            #Add the link
            link = linkList.linkCollection.add()

            for pb in pair:
                bone = link.linkedBones.add()
                bone.boneName = pb.name
                bone.armName = pb.id_data.name
            
            link.name = pair[1].name + "@" + pair[0].name
            
            #Set the active indices to the first bone (root of the chain) and last added chain        
            link.activeBoneIndex = 0
            linkList.activeLinkIndex = len(linkList.linkCollection)-1
            link.l0 = (pair[1].bone.matrix_local.translation - pair[0].bone.matrix_local.translation).length
            link.lambdA = 0
            if len(linkList.linkCollection) and gSwDrawInstance.handle is None:
                gSwDrawInstance.set(bpy.context)
    
        return {'FINISHED'}
    
class SW_OT_LinkAddByChainOpr(bpy.types.Operator):
    bl_idname = "sw.ot_linkaddbychain"
    bl_label = "Link swingy bone chains"
    bl_description = "Link the two swingy bone chains"

    @classmethod
    def poll(self, context):
        if bpy.app.version[0] < 5:
            return context.active_pose_bone is not None and context.active_pose_bone.bone.select and context.mode == "POSE"
        else:
            return context.active_pose_bone is not None and context.active_pose_bone.select and context.mode == "POSE"
    
    def execute(self, context):
        scene = context.scene
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList

        bpy.ops.object.mode_set(mode='POSE')        

        pbs = [pb for pb in context.selected_pose_bones]
        apb = context.active_pose_bone
        pairs = []
        if len(pbs) == 2:
            pairs = [[pbs[0], pbs[1]]]
        elif len(pbs) == 3:
            for pb in pbs:
                if pb == context.active_pose_bone:
                    continue
                pairs.append([apb, pb])
        else:
            self.report({'ERROR'}, "Only select two or three bones!")

        #validity check
        for pair in pairs:
            for pb in pair:
                if not pb.bIsDRB:
                    self.report({'ERROR'}, "One of the bones is not in a bone chain!")
                    return {'FINISHED'}
            if pair[0] in pair[1].children_recursive or pair[1] in pair[0].children_recursive:
                self.report({'ERROR'}, "Bones in the same chain cannot be linked!")
                return {'FINISHED'}
            
        #validity checks have been passed, constructing the "true" pairs, need to do this the horrible way to preserve backwards compatibility...
        #Get to the root of each of chain
        roots = []
        activeRootIndex = None
        for j, pb in enumerate(pbs):
            temp = pb.parent
            prevTemp = pb
            while temp is not None and temp.bIsDRB:
                prevTemp, temp = temp, temp.parent
            temp = prevTemp
            
            if pb == context.active_pose_bone:
                activeRootIndex = j
            roots.append(temp)
        
        pairs = []
        
        if len(pbs) == 2:
            p0, p1 = roots
            for _ in range(min(len(p0.children_recursive), len(p1.children_recursive))):
                #if we don't have any child, stop
                if not p0.children or not p1.children:
                    break                
                p0, p1 = p0.children[0], p1.children[0]
                #if one one them is not a drb somehow, stop
                if not p0.bIsDRB or not p1.bIsDRB:
                    break  
                pairs.append([p0, p1])
        elif len(pbs) == 3: #probably a smarter way to handle this one but I'm tired right now...
            p0, p1, p2 = roots
            itCount = min(len(p0.children_recursive), len(p1.children_recursive))
            for _ in range(min(itCount, len(p2.children_recursive))):
                #if we don't have any child, stop
                if not p0.children or not p1.children or not p2.children:
                    break
                p0, p1, p2 = p0.children[0], p1.children[0], p2.children[0]
                #if one one them is not a drb somehow, stop
                if not p0.bIsDRB or not p1.bIsDRB or not p2.bIsDRB:
                    break  
                if activeRootIndex == 0:
                    pairs.append([p0, p1])
                    pairs.append([p0, p2])
                elif activeRootIndex == 1:
                    pairs.append([p0, p1])
                    pairs.append([p1, p2])
                else:
                    pairs.append([p0, p2])
                    pairs.append([p1, p2])
                
        for pair in pairs:
            #Does the constraint already exist?
            bExists = False
            for otherLink in linkList.linkCollection:
                o0, o1 = otherLink.linkedBones[0], otherLink.linkedBones[1]
                if (o0.boneName == pair[0].name and o0.armName == pair[0].id_data.name and o1.boneName == pair[1].name and o1.armName == pair[1].id_data.name) \
                or (o1.boneName == pair[0].name and o1.armName == pair[0].id_data.name and o0.boneName == pair[1].name and o0.armName == pair[1].id_data.name):
                    bExists = True
            if bExists:
                continue

            #Add the link
            link = linkList.linkCollection.add()

            for pb in pair:
                bone = link.linkedBones.add()
                bone.boneName = pb.name
                bone.armName = pb.id_data.name
            
            link.name = pair[1].name + "@" + pair[0].name
            
            #Set the active indices to the first bone (root of the chain) and last added chain        
            link.activeBoneIndex = 0
            linkList.activeLinkIndex = len(linkList.linkCollection)-1
            link.l0 = (pair[1].bone.matrix_local.translation - pair[0].bone.matrix_local.translation).length
            link.lambdA = 0
            if len(linkList.linkCollection) and gSwDrawInstance.handle is None:
                gSwDrawInstance.set(bpy.context)
    
        return {'FINISHED'}
    
class SW_OT_LinkResetOpr(bpy.types.Operator):
    bl_idname = "sw.ot_linkreset"
    bl_label = "Reset links"
    bl_description = "Reset links after moving bones"

    @classmethod
    def poll(self, context):
        if bpy.app.version[0] < 5:
            return context.active_pose_bone is not None and context.active_pose_bone.bone.select and context.mode == "POSE"
        else:
            return context.active_pose_bone is not None and context.active_pose_bone.select and context.mode == "POSE"
    
    def execute(self, context):
        scene = context.scene
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList

        for link in linkList.linkCollection:  
            b0, b1 = link.linkedBones[0], link.linkedBones[1]
            p0 = bpy.data.objects[b0.armName].pose.bones[b0.boneName]
            p1 = bpy.data.objects[b1.armName].pose.bones[b1.boneName]
            link.l0 = (p1.bone.matrix_local.translation - p0.bone.matrix_local.translation).length
    
        return {'FINISHED'}
    
class SW_OT_LinkHideAllOpr(bpy.types.Operator):
    bl_idname = "sw.ot_linkhideall"
    bl_label = "Hide/Unhide all links"
    bl_description = "Hide/Unhide all the links"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.mode != "POSE":
            return False
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList
        return linkList.activeLinkIndex >= 0 and len(linkList.linkCollection)

    def execute(self, context):
        scene = context.scene
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList

        if len(linkList.linkCollection) and gSwDrawInstance.handle is None:
            gSwDrawInstance.set(bpy.context)

        bHasOneNotHidden = False
        for link in linkList.linkCollection:  
            if link.bHidden:
                bHasOneNotHidden = True
                break
        for link in linkList.linkCollection:  
            link.bHidden = not bHasOneNotHidden
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}
    
class SW_OT_LinkDelOpr(bpy.types.Operator):
    bl_idname = "sw.ot_linkdel"
    bl_label = "Delete link"
    bl_description = "Delete the selected link"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.mode != "POSE":
            return False
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList
        return linkList.activeLinkIndex >= 0 and len(linkList.linkCollection)
    
    def execute(self, context):
        scene = context.scene
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList

        link = linkList.linkCollection[linkList.activeLinkIndex]
        linkList.linkCollection.remove(linkList.activeLinkIndex)
        linkList.activeLinkIndex -= 1 
        if linkList.activeLinkIndex == -1 and len(linkList.linkCollection):
            linkList.activeLinkIndex = 0
        
        return {'FINISHED'}
    
class SW_OT_LinkClearOpr(bpy.types.Operator):
    bl_idname = "sw.ot_linkclear"
    bl_label = "Clear all links"
    bl_description = "Clear all the links"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if context.mode != "POSE":
            return False
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList
        return linkList.activeLinkIndex >= 0 and len(linkList.linkCollection)

    def execute(self, context):
        scene = context.scene
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList

        linkList.linkCollection.clear() #will automatically remove the handle during the next call
        linkList.activeLinkIndex = -1

        return {'FINISHED'}