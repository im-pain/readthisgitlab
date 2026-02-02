import bpy
from bpy.props import (BoolProperty, BoolVectorProperty, CollectionProperty,
                       EnumProperty, FloatProperty, FloatVectorProperty,
                       IntProperty, PointerProperty, StringProperty)
from bpy.types import PropertyGroup
from mathutils import Matrix, Vector

from .SwingUtils import (addAmplitudePrimitive, addWindPrimitive, evaluateWind, removeBone,
                         removeAmplitudePrimitive, removeWindPrimitive,
                         updateAmplitudePrimitive, updateWindPrimitive, getDRBBGroup, selectArmatureByName, updateColors, createSphereShape)

##############################
# Update Props
##############################

def pSwDrbPropUpdate(self, context, prop):
    apb = bpy.context.active_pose_bone
    if self != apb:
        return
    for pb in bpy.context.selected_pose_bones:
        if not pb.bIsDRB:
            continue
        if not pb == apb:
            if prop == "pSwDrbDamping":
                pb.pSwDrbDamping = apb.pSwDrbDamping
            elif prop == "pSwDrbWindFactor":
                pb.pSwDrbWindFactor = apb.pSwDrbWindFactor
            elif prop == "pSwDrbGravityFactor":
                pb.pSwDrbGravityFactor = apb.pSwDrbGravityFactor
            elif prop == "pSwDrbDrag":
                pb.pSwDrbDrag = apb.pSwDrbDrag
            elif prop == "pSwDrbStiffness":
                pb.pSwDrbStiffness = apb.pSwDrbStiffness
            elif prop == "pSwDrbRadius":
                pb.pSwDrbRadius = apb.pSwDrbRadius
            elif prop == "pSwDrbAmplitude":
                pb.pSwDrbAmplitude = apb.pSwDrbAmplitude
            elif prop == "pSwDrbAmplitude2":
                pb.pSwDrbAmplitude2 = apb.pSwDrbAmplitude2
            elif prop == "pSwDrbFriction":
                pb.pSwDrbFriction = apb.pSwDrbFriction
            elif prop == "pSwDrbCollLayer":
                pb.pSwDrbCollLayer = apb.pSwDrbCollLayer
            elif prop == "pSwDrbUseAmplitude":
                pb.pSwDrbUseAmplitude = apb.pSwDrbUseAmplitude
            elif prop == "pSwDrbLockRoll":
                pb.pSwDrbLockRoll = apb.pSwDrbLockRoll
            elif prop == "pSwDrbShowAmplitude":
                pb.pSwDrbShowAmplitude = apb.pSwDrbShowAmplitude
            elif prop == "pSwDrbCollIntra":
                pb.pSwDrbCollIntra = apb.pSwDrbCollIntra
            elif prop == "pSwDrbAmplitudeType":
                pb.pSwDrbAmplitudeType = apb.pSwDrbAmplitudeType
            elif prop == "bHasColliderXAxis":
                pb.bHasColliderXAxis = apb.bHasColliderXAxis
            elif prop == "bHasColliderZAxis":
                pb.bHasColliderZAxis = apb.bHasColliderZAxis
            # elif prop == "bHasColliderPosAxis":
            #     pb.bHasColliderPosAxis = apb.bHasColliderPosAxis
            # elif prop == "bHasColliderNegAxis":
            #     pb.bHasColliderNegAxis = apb.bHasColliderNegAxis
            elif prop == "cupSwDrbDamping":
                pb.cupSwDrbDamping = apb.cupSwDrbDamping
            elif prop == "cupSwDrbDrag":
                pb.cupSwDrbDrag = apb.cupSwDrbDrag
            elif prop == "cupSwDrbWindFactor":
                pb.cupSwDrbWindFactor = apb.cupSwDrbWindFactor
            elif prop == "cupSwDrbGravityFactor":
                pb.cupSwDrbGravityFactor = apb.cupSwDrbGravityFactor
            elif prop == "cupSwDrbStiffness":
                pb.cupSwDrbStiffness = apb.cupSwDrbStiffness
        if prop == "pSwDrbRadius":
            pb.custom_shape_scale_xyz = [pb.pSwDrbRadius for _ in range(3)]
        elif prop == "pSwDrbAmplitude" or prop == "pSwDrbAmplitude2" or prop == "pSwDrbAmplitudeType":
            # if pb.pSwDrbAmplitudeType == 'C' and (prop == "pSwDrbAmplitude" or prop == "pSwDrbAmplitudeType"):
            #     pb.pSwDrbAmplitude2 = pb.pSwDrbAmplitude
            ampPrimPb = context.object.pose.bones.get("SW_AMPPRIM_" + pb.name)
            if ampPrimPb is not None:
                updateAmplitudePrimitive(pb, ampPrimPb)
        elif prop == "pSwDrbShowAmplitude": #needed to use once and restore proper selection
            ampPrimPb = pb.id_data.pose.bones.get("SW_AMPPRIM_" + pb.name)
            if ampPrimPb is not None:
                if bpy.app.version[0] < 5:
                    ampPrimPb.bone.hide = not pb.pSwDrbShowAmplitude
                else:
                    ampPrimPb.hide = not pb.pSwDrbShowAmplitude
                if pb.pSwDrbShowAmplitude:
                    updateAmplitudePrimitive(pb, ampPrimPb)
        elif prop == "pSwDrbUseAmplitude":
            # pb.pSwDrbShowAmplitude = pb.pSwDrbUseAmplitude
            if pb.pSwDrbUseAmplitude: 
                addAmplitudePrimitive(self, context)
                pb.pSwDrbShowAmplitude = True
            else:
                removeAmplitudePrimitive(self, context, context.object)

def pSwSrbPropUpdate(self, context, prop):
    apb = bpy.context.active_pose_bone
    if self != apb:
        return
    for pb in bpy.context.selected_pose_bones:
        if not pb.bIsSRB:
            continue
        if not pb == apb:
            if prop == "pSwSrbRadius":
                pb.pSwSrbRadius = apb.pSwSrbRadius
            elif prop == "pSwSrbDepth":
                pb.pSwSrbDepth = apb.pSwSrbDepth
            elif prop == "pSwSrbFriction":
                pb.pSwSrbFriction = apb.pSwSrbFriction
            elif prop == "pSwSrbCollLayers":
                pb.pSwSrbCollLayers = apb.pSwSrbCollLayers
        if prop == "pSwSrbRadius" or prop == "pSwSrbDepth":
            pb.custom_shape_scale_xyz = [pb.pSwSrbRadius for _ in range(3)]
            if pb.custom_shape == bpy.data.objects.get("SW_Shape_Cylinder"):
                pb.custom_shape_scale_xyz[2] = pb.pSwSrbDepth
        

def updateSrbParent(self, context):
    if not context.active_pose_bone.bIsSRB:
        return
    editBoneName = context.active_pose_bone.name
    pBoneName = context.active_pose_bone.pSwSrbParentName
    arm = context.object
    pBone = arm.pose.bones.get(pBoneName)
    if pBone.bIsSRB or pBone.bIsDRB:
        return
    bpy.ops.object.mode_set(mode='EDIT')
    pBone = arm.data.edit_bones.get(pBoneName)
    editBone = arm.data.edit_bones.get(editBoneName )
    editBone.parent = pBone
    bpy.ops.object.mode_set(mode='POSE')



def pSwArmPropUpdate(self, context, prop):
    arm = context.object
    if prop == "bUseWind":
        if arm.data.bUseWind:
            addWindPrimitive(self, context)
        else:
            removeWindPrimitive(self, context, arm)
        # arm.data.bShowWind = arm.data.bUseWind 
    elif prop == "bShowWind":
        pb = arm.pose.bones.get("SW_Shape_Wind")
        if pb is not None:
            if bpy.app.version[0] < 5:
                pb.bone.hide = not arm.bShowWind
            else:
                pb.hide = not arm.bShowWind
    if prop =="swWind" or prop=="swWindArrowScale" or (prop == "bShowWind" and arm.bShowWind):
        windV = evaluateWind(arm)        
        updateWindPrimitive(arm, windV)
    if prop == "bSwDisplayShape":
        for pb in arm.pose.bones:
            if pb.bIsDRB:
                if arm.bSwDisplayShape:
                    bg = getDRBBGroup(self, context, bpy.context.object)
                    createSphereShape(self, context,bpy.context.object)
                    if bpy.app.version[0] > 3:
                        bg.assign(pb)
                        pb.bone.color.palette = 'CUSTOM'
                    else:   
                        pb.bone_group = bg                
                    pb.custom_shape = bpy.data.objects.get("SW_Shape_Sphere")                    
                else:
                    if bpy.app.version[0]>3:
                        bg = getDRBBGroup(self, context, bpy.context.object)
                        bg.unassign(pb)
                        pb.bone.color.palette = 'DEFAULT'
                    else:
                        pb.bone_group = None
                    pb.custom_shape = None
                    pb.pSwDrbShowAmplitude = False
            if pb.name.startswith("SW_AMPPRIM_") and not arm.bSwDisplayShape:
                if bpy.app.version[0]<5:
                    pb.bone.hide = True
                else:
                    pb.hide = True
            if pb.bIsSRB:
                if bpy.app.version[0]<5:
                    pb.bone.hide = not arm.bSwDisplayShape         
                else:
                    pb.hide = not arm.bSwDisplayShape    
    if prop == "bSwToggleSelect":
        for pb in arm.pose.bones:
            if pb.bIsDRB or pb.bIsSRB:                
                if bpy.app.version[0] < 5:                   
                    pb.bone.hide_select = not arm.bSwToggleSelect
                else:   
                    pb.bone.hide_select = not arm.bSwToggleSelect 
            
##############################
# Dynamic rigid bodies
##############################

class SW_DRBCOLORS_SceneProps(PropertyGroup):
    bcSet = bpy.context.preferences.themes[0].bone_color_sets[0]
    regular: FloatVectorProperty(default=bcSet.normal, subtype='COLOR_GAMMA',min = 0.0, max = 1.0, update=lambda s, c: updateColors(s, c, ['DRB','regular']))
    select: FloatVectorProperty(default=bcSet.select, subtype='COLOR_GAMMA',min = 0.0, max = 1.0, update=lambda s, c: updateColors(s, c, ['DRB','select']))
    active: FloatVectorProperty(default=bcSet.active, subtype='COLOR_GAMMA',min = 0.0, max = 1.0, update=lambda s, c: updateColors(s, c, ['DRB','active']))

class SW_DRBLIST_BoneProps(PropertyGroup):
    boneName: StringProperty()
    chainPercentage: FloatProperty(precision=2)

def boneDRBIndexChanged(self, context):
    scene = context.scene
    arm = context.object
    drbList = arm.data.drbList
    if drbList.activeBoneChainIndex < 0:
        return 
    bColl = drbList.boneChainCollection[drbList.activeBoneChainIndex]
    b = bColl.boneCollection[bColl.activeBoneIndex]
    if context.selected_pose_bones is not None:
        for c in context.selected_pose_bones:
            if bpy.app.version[0] < 5:
                c.bone.select = False
            else:
                c.select = False            
    arm = context.object
    if context.selected_pose_bones is not None:
        for c in context.selected_pose_bones:
            if bpy.app.version[0] < 5:
                c.bone.select = False
            else:
                c.select = False    
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode='POSE')
    if bpy.app.version[0] < 5:
        if b.boneName in arm.data.bones:
            bone = arm.data.bones[b.boneName]
            bpy.context.object.data.bones.active =  bone
            bone.select = True
    else:
        if b.boneName in arm.pose.bones:
            bone = arm.pose.bones[b.boneName]
            bpy.context.object.data.bones.active =  bpy.context.object.data.bones[bone.name]
            bone.select = True
    

def boneChainHiddenChanged(self, context):
    scene = context.scene
    for b in self.boneCollection:
        arm = context.object
        pb = arm.pose.bones[b.boneName]
        if bpy.app.version[0] < 5:
            pb.bone.hide = self.bHidden
            if bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name) is not None:
                bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name).bone.hide = self.bHidden
        else:
            pb.hide = self.bHidden
            if bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name) is not None:
                bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name).hide = self.bHidden

def boneChainExtraChildChanged(self, context):
    scene = context.scene
    arm = context.object

    for b in self.boneCollection:
        if b.boneName not in arm.pose.bones:
            bpy.ops.sw.ot_drbrescanallchains()
        pb = arm.pose.bones[b.boneName]        
        if len(pb.bone.children) == 0:              
            if self.bExtraChild: #add the extra child if not already here  
                if context.selected_pose_bones is not None:
                    for c in context.selected_pose_bones:
                        if bpy.app.version[0] < 5:
                            c.bone.select = False
                            
                        else:
                            c.select = False   
                if bpy.app.version[0] < 5:
                    bone = arm.data.edit_bones[b.boneName]
                    bpy.context.object.data.bones.active =  bone
                    bone.select = True
                    bpy.ops.object.mode_set(mode='EDIT') 
                    refB = arm.data.edit_bones[b.boneName]
                    copy_bone = arm.data.edit_bones.new(refB.name)
                else:
                    bone = arm.pose.bones[b.boneName]
                    bpy.context.object.data.bones.active =  arm.data.bones[b.boneName]
                    bone.select = True
                    bpy.ops.object.mode_set(mode='EDIT') 
                    refB = arm.data.edit_bones[b.boneName]
                    copy_bone = arm.data.edit_bones.new(refB.name)
                
                copy_bone.matrix = refB.matrix.copy()
                copy_bone.length = refB.length
                copy_bone.translate(arm.data.bones[b.boneName].tail_local - arm.data.bones[b.boneName].head_local) 
                copy_bone.parent = refB
                copy_bone.use_connect = True
                
                bpy.ops.object.mode_set(mode='POSE')
                bpy.context.view_layer.update()
                if bpy.app.version[0] < 5:
                    bone = arm.data.edit_bones[pb.name]
                else:
                    bone = arm.data.bones[pb.name]
                editBone = bone.children[0]
                editBone.name = "SWExtraChildBone_" + arm.name + "_" + pb.name
                bpy.ops.object.mode_set(mode='POSE')
                c = arm.pose.bones.get(editBone.name)
                if bpy.app.version[0] < 5:
                    c.bone.select = True
                else:
                    c.select = True
                c.bIsDRB = True
                bone = self.boneCollection.add()
                bone.boneName = editBone.name
                bone.chainPercentage = 0
                bone.armName = pb.id_data.name

                bg = getDRBBGroup(self, context, bpy.context.object)        
                if bpy.app.version[0] > 3:
                    bg.assign(c)
                    c.bone.color.palette = 'CUSTOM'
                else:
                    c.bone_group = bg
                c.soSwPrevPos = c.matrix.translation
                c.soSwUpdatedPos = Vector(c.bone.matrix_local.translation)
                c.custom_shape = bpy.data.objects.get("SW_Shape_Sphere")
                height = (c.tail - c.head).length
                c.pSwDrbRadius = pb.pSwDrbRadius
                c.use_custom_shape_bone_size = False
                c.custom_shape_scale_xyz = [c.pSwDrbRadius for _ in range(3)]    
                c.custom_shape_rotation_euler[0] = -1.57  
                c.bone.show_wire = True
                c.lock_scale = [True, True, True]
                if bpy.app.version[0]>3:
                    updateColors(self, context, ['DRB','regular'])
                    updateColors(self, context, ['DRB','select'])
                    updateColors(self, context, ['DRB','active']) 

                #copy all custom properties
                for k, v in pb.items():
                    if k.startswith("pSw"):
                        setattr(c,k,v)       
                # return
            else:
                if pb.name.startswith("SWExtraChildBone_"):

                    if bpy.context.object.pose.bones.get("SW_AMPPRIM_" + pb.name) is not None:
                        removeBone(self, context, bpy.context.object, "SW_AMPPRIM_" + pb.name)

                    bpy.ops.object.mode_set(mode='EDIT') 
                    arm.data.edit_bones.remove(arm.data.edit_bones.get(pb.name))
                    self.boneCollection.remove(len(self.boneCollection)-1)
                    bpy.ops.object.mode_set(mode='POSE')
            #Percentages update
            totalLength = 0
            rBone = arm.pose.bones[self.boneCollection[0].boneName]
            for c in rBone.children_recursive:
                totalLength += (c.matrix.translation - c.parent.matrix.translation).length
            totalTemp = 0
            for c in rBone.children_recursive:
                totalTemp += (c.matrix.translation - c.parent.matrix.translation).length
                c.cuSwDrbChainPercentage = totalTemp/totalLength
                for cBone in self.boneCollection:
                    if cBone.boneName == c.name:
                        cBone.chainPercentage = c.cuSwDrbChainPercentage
            return

class SW_DRBLIST_BoneChainProps(PropertyGroup):
    activeBoneIndex: IntProperty(update=boneDRBIndexChanged)
    boneCollection: CollectionProperty(
        name = "Bone Collection",
        type = SW_DRBLIST_BoneProps)
    bHidden: BoolProperty(name="Hidden", description="Hide/Unhide the bone chain", default=False, update=boneChainHiddenChanged)
    bReset: BoolProperty(name="Reset", description="Reset or not when using the \"Reset All\" operator", default=True)
    bExtraChild: BoolProperty(name="Extra Child", description="Add an extra child to control the last bone's rotation", default=False, update=boneChainExtraChildChanged)
    

def boneChainDRBIndexChanged(self, context):
    scene = context.scene
    arm = context.object
    drbList = arm.data.drbList
    if drbList.activeBoneChainIndex < 0:
        return     
    boneChain = drbList.boneChainCollection[drbList.activeBoneChainIndex]
    arm = context.object
    if arm is not None and arm.visible_get():
        bpy.ops.object.mode_set(mode='OBJECT')
        arm.select_set(False)
    arm = context.object  
    
    for c in arm.pose.bones:
        if bpy.app.version[0] < 5:
            c.bone.select = False
        else:
            c.select = False    
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode='POSE')
    if bpy.app.version[0] < 5:
        for b in boneChain.boneCollection:
            if b.boneName not in arm.data.bones:
                bpy.ops.sw.ot_drbrescanallchains()
            arm.data.bones[b.boneName].select = True
        arm.data.bones.active =  arm.data.bones[boneChain.boneCollection[0].boneName]
    else:
        for b in boneChain.boneCollection:
            if b.boneName not in arm.pose.bones:
                bpy.ops.sw.ot_drbrescanallchains()
            arm.pose.bones[b.boneName].select = True
        arm.data.bones.active =  arm.data.bones[boneChain.boneCollection[0].boneName]

def curveParamNameFilter(self, object):
    return object.swName.startswith("SWParam")

def curveWindNameFilter(self, object):
    return object.swName.startswith("SWWind")

class SW_DRBLIST_ArmProps(PropertyGroup):
    activeBoneChainIndex: IntProperty(update=boneChainDRBIndexChanged)
    boneChainCollection: CollectionProperty(
        name = "Bone Chain Collection",
        type = SW_DRBLIST_BoneChainProps)

##############################
# Static rigid bodies
##############################

class SW_SRBCOLORS_SceneProps(PropertyGroup):
    bcSet = bpy.context.preferences.themes[0].bone_color_sets[2]
    regular: FloatVectorProperty(default=bcSet.normal, subtype='COLOR_GAMMA',min = 0.0, max = 1.0,update=lambda s, c: updateColors(s, c, ['SRB','regular']))
    select: FloatVectorProperty(default=bcSet.select, subtype='COLOR_GAMMA',min = 0.0, max = 1.0,update=lambda s, c: updateColors(s, c, ['SRB','select']))
    active: FloatVectorProperty(default=bcSet.active, subtype='COLOR_GAMMA',min = 0.0, max = 1.0,update=lambda s, c: updateColors(s, c, ['SRB','active']))

class SW_SRBLIST_ColliderProps(PropertyGroup):
    boneName: StringProperty()
    armName: StringProperty()
    colliderName: StringProperty()
    type: StringProperty()

def colliderSRBIndexChanged(self, context):
    scene = context.scene
    arm = context.object
    srbList = arm.data.srbList
    if srbList.activeColliderIndex < 0:
        return 
    collider = srbList.colliderCollection[srbList.activeColliderIndex]
    
    if arm is not None:
        bpy.ops.object.mode_set(mode='OBJECT')
        arm.select_set(False)
    # if not selectArmatureByName(self, context, collider.armName, True):
    #     if context.selected_pose_bones is not None:
    #         for c in context.selected_pose_bones:
    #             if bpy.app.version[0] < 5:
    #                 c.bone.select = False
    #             else:
    #                 c.select = False    
    #     return
    arm = context.object
    if context.selected_pose_bones is not None:
        for c in context.selected_pose_bones:
            if bpy.app.version[0] < 5:
                c.bone.select = False
            else:
                c.select = False    
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode='POSE')
    if bpy.app.version[0] < 5:
        if collider.name in arm.data.bones:
            bone = arm.data.bones[collider.name]
            arm.data.bones.active =  bone
            bone.select = True        
    else:
        if collider.name in arm.pose.bones:
            bone = arm.pose.bones[collider.name]
            arm.data.bones.active =  arm.data.bones[bone.name]
            bone.select = True

class SW_SRBLIST_ArmProps(PropertyGroup):
    activeColliderIndex: IntProperty(update=colliderSRBIndexChanged)
    colliderCollection: CollectionProperty(
        name = "Collider Collection",
        type = SW_SRBLIST_ColliderProps)

##############################
# Curves
##############################

def curveIndexChanged(self, context):
    scene = context.scene
    arm = context.object
    if arm.activeCurveIndex < 0:
        return
    curveList = arm.data.curveList
    curve = curveList.curveCollection[arm.activeCurveIndex]
    # curveList = arm.data.curveList
    # if curveList.activeCurveIndex < 0:
    #     return 
    # curve = curveList.curveCollection[curveList.activeCurveIndex]
    if bpy.app.version[0] < 5:
        bpy.context.tool_settings.image_paint.brush = curve.brush

class SW_CURVELIST_CurveProps(PropertyGroup):
    brush: PointerProperty(name="Brush",type=bpy.types.Brush)

class SW_CURVELIST_ArmProps(PropertyGroup):
    # activeCurveIndex: IntProperty(update=curveIndexChanged)
    curveCollection: CollectionProperty(
        name = "Curve Collection",
        type = SW_CURVELIST_CurveProps)

##############################
# Amplitude primitives
##############################

class SW_AMPPRIMCOLORS_SceneProps(PropertyGroup):
    bcSet = bpy.context.preferences.themes[0].bone_color_sets[10]
    regular: FloatVectorProperty(default=bcSet.normal, subtype='COLOR_GAMMA',min = 0.0, max = 1.0, update=lambda s, c: updateColors(s, c, ['AMPPRIM','regular']))
    select: FloatVectorProperty(default=bcSet.select, subtype='COLOR_GAMMA',min = 0.0, max = 1.0)
    active: FloatVectorProperty(default=bcSet.active, subtype='COLOR_GAMMA',min = 0.0, max = 1.0)

class SW_AMPPRIMLIST_AMPPRIMProps(PropertyGroup):
    primName: StringProperty()

class SW_AMPPRIMLIST_SceneProps(PropertyGroup):
    ampPrimCollection: CollectionProperty(
        name = "Amplitude Primitives",
        type = SW_AMPPRIMLIST_AMPPRIMProps)

##############################
# Wind primitives
##############################

class SW_WINDCOLORS_ArmProps(PropertyGroup):
    bcSet = bpy.context.preferences.themes[0].bone_color_sets[8]
    regular: FloatVectorProperty(default=bcSet.normal, subtype='COLOR_GAMMA',min = 0.0, max = 1.0,update=lambda s, c: updateColors(s, c, ['SWWIND','regular']))
    select: FloatVectorProperty(default=bcSet.select, subtype='COLOR_GAMMA',min = 0.0, max = 1.0,update=lambda s, c: updateColors(s, c, ['SWWIND','select']))
    active: FloatVectorProperty(default=bcSet.active, subtype='COLOR_GAMMA',min = 0.0, max = 1.0,update=lambda s, c: updateColors(s, c, ['SWWIND','active']))

##############################
# Links
##############################

def swLinkBoneIndexChanged(self, context):
    scene = context.scene
    arm = context.object
    linkList = arm.data.swLinkList
    if linkList.activeLinkIndex < 0:
        return 
    link = linkList.linkCollection[linkList.activeLinkIndex]
    b = link.linkedBones[link.activeBoneIndex]
    if context.selected_pose_bones is not None:
        for c in context.selected_pose_bones:
            if bpy.app.version[0] < 5:
                c.bone.select = False
            else:
                c.select = False    
    # if not selectArmatureByName(self, context, b.armName, True):
    #     return
    # arm = context.object
    if context.selected_pose_bones is not None:
        for c in context.selected_pose_bones:
            if bpy.app.version[0] < 5:
                c.bone.select = False
            else:
                c.select = False    
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode='POSE')
    if bpy.app.version[0] < 5:
        bone = arm.data.bones[b.boneName]
        bpy.context.object.data.bones.active =  bone
        bone.select = True
    else:
        bone = arm.pose.bones[b.boneName]
        bpy.context.object.data.bones.active =  bpy.context.object.data.bones[bone.name]
        bone.select = True
    # bone = arm.data.edit_bones[b.boneName]
    # bpy.context.object.data.bones.active =  bone
    # bone.select = True

def swLinkIndexChanged(self, context):
    scene = context.scene
    arm = context.object
    linkList = arm.data.swLinkList
    if linkList.activeLinkIndex < 0 or scene.swLinkLock:
        return 
    
    link = linkList.linkCollection[linkList.activeLinkIndex]
    b = link.linkedBones[link.activeBoneIndex]
    if context.selected_pose_bones is not None:
        for c in context.selected_pose_bones:
            if bpy.app.version[0] < 5:
                c.bone.select = False
            else:
                c.select = False    
    # if not selectArmatureByName(self, context, b.armName, True):
    #     return
    # arm = context.object
    if context.selected_pose_bones is not None:
        for c in context.selected_pose_bones:
            if bpy.app.version[0] < 5:
                c.bone.select = False
            else:
                c.select = False    
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode='POSE')
    if bpy.app.version[0] < 5:
        bone = arm.data.bones[b.boneName]
        bpy.context.object.data.bones.active =  bone
        bone.select = True
    else:
        bone = arm.pose.bones[b.boneName]
        bpy.context.object.data.bones.active =  bpy.context.object.data.bones[bone.name]
        bone.select = True
    for b in link.linkedBones:
        if bpy.app.version[0] < 5:
            bone = arm.data.bones[b.boneName]            
            bone.select = True
        else:
            bone = arm.pose.bones[b.boneName]
            bone.select = True
            

class SW_LINKCOLOR_SceneProps(PropertyGroup):
    bcSet = bpy.context.preferences.themes[0].bone_color_sets[8]
    bcSet2 = bpy.context.preferences.themes[0].bone_color_sets[9]
    bcSet3 = bpy.context.preferences.themes[0].bone_color_sets[0]
    regular: FloatVectorProperty(default=bcSet.normal, subtype='COLOR_GAMMA',min = 0.0, max = 1.0, options={'HIDDEN'})
    inactive: FloatVectorProperty(default=bcSet2.normal, subtype='COLOR_GAMMA',min = 0.0, max = 1.0, options={'HIDDEN'})
    maxL: FloatVectorProperty(default=bcSet3.active, subtype='COLOR_GAMMA',min = 0.0, max = 1.0, options={'HIDDEN'})

class SW_LINKLIST_BoneLinkedProps(PropertyGroup):
    boneName: StringProperty()
    armName: StringProperty()

class SW_LINKLIST_LinkProps(PropertyGroup):
    activeBoneIndex: IntProperty(update=swLinkBoneIndexChanged)
    linkedBones: CollectionProperty(
        name = "Linked Bones",
        type = SW_LINKLIST_BoneLinkedProps)
    linkName: StringProperty()
    l0: FloatProperty()
    lambdA: FloatProperty()
    # minL: FloatProperty(min = 0.0)
    # maxL: FloatProperty(min = 0.0)
    bHidden: BoolProperty(name="Hidden", description="Hide/Unhide the link", default=False)
    bIsActive: BoolProperty(name="Hidden", description="Activate/Deactivate the link", default=True)
    # bSolveBefore: BoolProperty(name="Hidden", description="Solve before collision", default=True)
    # bSolveAfter: BoolProperty(name="Hidden", description="Solve after collision", default=True)


class SW_LINKLIST_ArmProps(PropertyGroup):
    activeLinkIndex: IntProperty(update=swLinkIndexChanged)
    linkCollection: CollectionProperty(
        name = "Link Collection",
        type = SW_LINKLIST_LinkProps)

##############################
# Props
##############################

SwPoseBoneProps = [
    ('bIsDRBRoot', BoolProperty(name='DRB Root', default=False,options={'HIDDEN'})),
    ('bIsDRB', BoolProperty(name='Physics Bone', default=False,options={'HIDDEN'})),
    ('bIsRootBone', BoolProperty(name='Root Bone', default=False,options={'HIDDEN'})),
    ('bHasColliderXAxis', BoolProperty(name='Collider X Axis', default=True, update=lambda s, c: pSwDrbPropUpdate(s, c, 'bHasColliderXAxis'), override={"LIBRARY_OVERRIDABLE"})),
    ('bHasColliderZAxis', BoolProperty(name='Collider Z Axis', default=True, update=lambda s, c: pSwDrbPropUpdate(s, c, 'bHasColliderZAxis'), override={"LIBRARY_OVERRIDABLE"})),
    # ('bHasColliderPosAxis', BoolProperty(name='Collider Pos Axis', default=True, update=lambda s, c: pSwDrbPropUpdate(s, c, 'bHasColliderPosAxis'))),
    # ('bHasColliderNegAxis', BoolProperty(name='Collider Neg Axis', default=True, update=lambda s, c: pSwDrbPropUpdate(s, c, 'bHasColliderNegAxis'))),
    ('cuSwDrbChainPercentage', FloatProperty(name='Chain percentage', precision=2, default=0.0, min=0.0, max=1.0,options={'HIDDEN'})),
    ('pSwDrbDamping', FloatProperty(name='Angular Damping', default=0.1, min=0.0, max=1.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbDamping'),
    description="Amount of angular velocity lost over time", override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbDrag', FloatProperty(name='Drag factor', default=0.1, min=0.0, max=1.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbDrag'),
    description="Amount of opposition to translation", override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbStiffness', FloatProperty(name='Stiffness', default=0.0, min=0.0, max=1.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbStiffness'),
    description="Amount of pre-simulation pose to preserve", override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbWindFactor', FloatProperty(name='Wind factor', default=1.0, min=0.0, max=1.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbWindFactor'),
    description="Wind contribution", override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbGravityFactor', FloatProperty(name='Gravity factor', default=1.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbGravityFactor'),
    description="Gravity contribution", override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbFriction', FloatProperty(name='Friction', default=0.0, min=0.0,max = 1.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbFriction'),
    description="Friction", override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbRadius', FloatProperty(name='Radius', default=0.3, min=0.0, precision=3, step=0.3, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbRadius'),
    description="Bone collision radius",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbLockRoll', BoolProperty(name='Lock roll', default=True, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbLockRoll'),
    description="Use this to prevent the bone from rotating around its up axis during the simulation",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbUseAmplitude', BoolProperty(name='Use Amplitude', default=False, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbUseAmplitude'),
    description="Use an amplitude limit constraint",options={'HIDDEN'})),
    ('pSwDrbShowAmplitude', BoolProperty(name='Show Amplitude', default=True, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbShowAmplitude'),
    description="Show/hide the amplitude gizmo",options={'HIDDEN'})),
    ('pSwDrbAmplitudeType', EnumProperty(name="Amplitude type", description="Amplitude limit shape", update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbAmplitudeType'),
        items= [
            ('C', "Cone", "Cone limit",'CONE',0),
            ('E', "Ellipsoid", "Ellipsoid limit",'META_ELLIPSOID',1)
        ],
    options={'HIDDEN'})),
    ('pSwDrbAmplitude', FloatProperty(name='Amplitude', default=30.0, min=0.0,max = 90.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbAmplitude'),
    description="Local X axis amplitude",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbAmplitude2', FloatProperty(name='Amplitude 2', default=30.0, min=5.0,max = 70.0, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbAmplitude2'),
    description="Local Z axis amplitude",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),    
    ('pSwDrbCollLayer', BoolVectorProperty(name='Collision Layer',subtype="LAYER_MEMBER",default = [True if not i else False for i in range(10)], size = 10, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbCollLayer'),
    description="Collision layer of the bone",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('pSwDrbCollIntra', BoolProperty(name='Collide with other chains', default=False, update=lambda s, c: pSwDrbPropUpdate(s, c, 'pSwDrbCollIntra'),
    description="Collide with other bone chains", override={"LIBRARY_OVERRIDABLE"})),
    ('soSwPrevPos', FloatVectorProperty(name="Previous Position", default=[0,0,0],options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('soSwPrevFriction', FloatProperty(name="Previous Friction", default=0.0,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('soSwUpdatedPos', FloatVectorProperty(name="Updated Position", default=[0,0,0],options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('soSwPrevVel', FloatVectorProperty(name="Previous Velocity", default=[0,0,0],options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('soSwRWPos', FloatVectorProperty(name="World rotation pos", default=[0,0,0],options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    

    ('cupSwDrbDamping', PointerProperty(type=bpy.types.Brush,name='Curve', update=lambda s, c: pSwDrbPropUpdate(s, c, 'cupSwDrbDamping'),
    description="Damping curve",poll=curveParamNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('cupSwDrbDrag', PointerProperty(type=bpy.types.Brush,name='Curve', update=lambda s, c: pSwDrbPropUpdate(s, c, 'cupSwDrbDrag'),
    description="Linear acceleration curve",poll=curveParamNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('cupSwDrbStiffness', PointerProperty(type=bpy.types.Brush,name='Curve', update=lambda s, c: pSwDrbPropUpdate(s, c, 'cupSwDrbStiffness'),
    description="Stiffness curve",poll=curveParamNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('cupSwDrbWindFactor', PointerProperty(type=bpy.types.Brush,name='Curve', update=lambda s, c: pSwDrbPropUpdate(s, c, 'cupSwDrbWindFactor'),
    description="Wind factor curve",poll=curveParamNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('cupSwDrbGravityFactor', PointerProperty(type=bpy.types.Brush,name='Curve', update=lambda s, c: pSwDrbPropUpdate(s, c, 'cupSwDrbGravityFactor'),
    description="Gravity factor curve",poll=curveParamNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),

    ('bIsSRB', BoolProperty(name='Physics Bone', default=False,options={'HIDDEN'})),
    ('pSwSrbParentName', StringProperty(name='Parent', default="", update=updateSrbParent, 
    description="Collider bone parent",options={'HIDDEN'})),
    ('pSwSrbRadius', FloatProperty(name='Radius',precision=3, default=0.8, min=0.0, step=0.3, update=lambda s, c: pSwSrbPropUpdate(s, c, 'pSwSrbRadius'),
    description="Collider collision radius",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('pSwSrbDepth', FloatProperty(name='Depth',precision=3, default=1, min=0.0, step=0.3, update=lambda s, c: pSwSrbPropUpdate(s, c, 'pSwSrbDepth'),
    description="Collider collision depth",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('pSwSrbFriction', FloatProperty(name='Friction', default=0.0, min=0.0,max = 1.0, update=lambda s, c: pSwSrbPropUpdate(s, c, 'pSwSrbFriction'),
    description="Friction", override={"LIBRARY_OVERRIDABLE"})),
    ('pSwSrbCollLayers', BoolVectorProperty(name='Collision Layers',subtype="LAYER",default = [True if not i else False for i in range(10)], size = 10, update=lambda s, c: pSwSrbPropUpdate(s, c, 'pSwSrbCollLayers'),
    description="Collision layers of the collider",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
]

SwArmatureProps = [
    ('bUseWind', BoolProperty(name='Use Wind', default=False, update=lambda s, c: pSwArmPropUpdate(s, c, 'bUseWind'),
    description="Use a pseudo wind simulation")),    
    ('soArmPrevPos', FloatVectorProperty(name="Armature prev pose", default=[0,0,0], subtype="VELOCITY", options={'HIDDEN'})),
    

    ('drbList', PointerProperty(type=SW_DRBLIST_ArmProps,options={'HIDDEN'})),
    ('srbList', PointerProperty(type=SW_SRBLIST_ArmProps,options={'HIDDEN'})),
    ('swLinkList', PointerProperty(type=SW_LINKLIST_ArmProps,options={'HIDDEN'})),
    ('curveList', PointerProperty(type=SW_CURVELIST_ArmProps,options={'HIDDEN'})),
]

SwSceneProps = [   
    
    # ('amprimList', PointerProperty(type=SW_AMPPRIMLIST_SceneProps,options={'HIDDEN'})),
    ('drbColors', PointerProperty(type=SW_DRBCOLORS_SceneProps,
    description="Bone chain color scheme",options={'HIDDEN'})),
    ('srbColors', PointerProperty(type=SW_SRBCOLORS_SceneProps,
    description="Collider color scheme",options={'HIDDEN'})),
    ('ampPrimColors', PointerProperty(type=SW_AMPPRIMCOLORS_SceneProps,
    description="Amplitude gizmo color",options={'HIDDEN'})),
    ('swLinkColor', PointerProperty(type=SW_LINKCOLOR_SceneProps,
    description="Link color",options={'HIDDEN'})), 
    ('bSwIsBaking', BoolProperty(name='Sw Bake', options={'HIDDEN'})),
    ('bSwDropBake', BoolProperty(name='Sw Drop Bake',default=False, options={'HIDDEN'})),
    ('bSwMultiSelectChain', BoolProperty(name='Sw Multi Select Chain',default=False, options={'HIDDEN'})),
    ('bSwForceRendering', BoolProperty(name='Sw Bake',default=False, options={'HIDDEN'})),
    ('bSwForceDropBake', BoolProperty(name='Sw Force Drop Bake',default=False, options={'HIDDEN'})),
    ('bSwClearOnBake', BoolProperty(name='Sw Bake Clear',default=True)),
    ('swLinkLineWidth', FloatProperty(name='Link Line Width', default=3,min=0.0,max=10.0,options={'HIDDEN'})),
    ('swLinkLock', BoolProperty(default=False,options={'HIDDEN'})),
    ('armBakingName', StringProperty(name='arm baking name', default="",options={'HIDDEN'})),
    ('swParamPath', StringProperty(name='Sw Param path', subtype='FILE_PATH', default="",options={'HIDDEN'})),
]

SwObjectProps = [   
    ('bShowWind', BoolProperty(name='Show Wind', default=True, update=lambda s, c: pSwArmPropUpdate(s, c, 'bShowWind'),
    description="Show/hide the wind gizmo",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('swWind', FloatVectorProperty(name="Wind", default=[0,-1,0], subtype="VELOCITY", update=lambda s, c: pSwArmPropUpdate(s, c, 'swWind'),
    description="Wind vector", override={"LIBRARY_OVERRIDABLE"})),
    ('swWindMean', FloatProperty(name='Wind mean', default=1.5, override={"LIBRARY_OVERRIDABLE"})),
    ('swWindStd', FloatProperty(name='Wind standard deviation', default=0.6, override={"LIBRARY_OVERRIDABLE"})),
    ('bSwSimulate', BoolProperty(name='Enable Simulation', default=True, update=lambda s, c: pSwArmPropUpdate(s, c, 'bSwSimulate'),
    description="Enable the simulation for the armature", override={"LIBRARY_OVERRIDABLE"})),    
    ('cupSwWindX', PointerProperty(type=bpy.types.Brush,name='Curve', description="Wind X curve",poll=curveWindNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('cupSwWindY', PointerProperty(type=bpy.types.Brush,name='Curve', description="Wind Y curve",poll=curveWindNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('cupSwWindZ', PointerProperty(type=bpy.types.Brush,name='Curve', description="Wind Z curve",poll=curveWindNameFilter,options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('windColor', PointerProperty(type=SW_WINDCOLORS_ArmProps,
    description="Wind gizmo color",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),
    ('swWindArrowScale', FloatProperty(name='Wind arrow scale', default=1.0,min=0.0,update=lambda s, c: pSwArmPropUpdate(s, c, 'swWindArrowScale'),
    description="Wind gizmo relative scale",options={'HIDDEN'}, override={"LIBRARY_OVERRIDABLE"})),

    ('bSwDisplayShape', BoolProperty(default=True, update=lambda s, c: pSwArmPropUpdate(s, c, 'bSwDisplayShape'),
    description="Display the collision profiles of the chains", override={"LIBRARY_OVERRIDABLE"},options={'HIDDEN'})),
    ('bSwToggleSelect', BoolProperty(default=False, update=lambda s, c: pSwArmPropUpdate(s, c, 'bSwToggleSelect'),
    description="Makes the physics bones (un)selectable", override={"LIBRARY_OVERRIDABLE"},options={'HIDDEN'})),
    ('activeCurveIndex', IntProperty(update=curveIndexChanged, override={"LIBRARY_OVERRIDABLE"}))
]

SwBrushProps = [
    ('swName', StringProperty(name='swName', default="",options={'HIDDEN'})),
    ('cupSwAmplitude', FloatProperty(name='Amplitude', default=10, description="The amplitude of the curve, in m/s. Can be negative for convenience",options={'HIDDEN'})),
    ('cupSwPeriod', IntProperty(name='Period', default=50, min=0, description="The number of frames that this curve covers before looping, in frames",options={'HIDDEN'})),
    ('cupSwType',EnumProperty(
        name="Ctype",
        items= [
            ('P', "Parameter", "Parameter Curve", 0),
            ('W', "Wind", "Wind Curve", 1)
        ],
        options={'HIDDEN'}
    )),
]
