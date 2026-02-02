from math import pi, tan

import bmesh
import bpy
import gpu
from mathutils import Matrix, Vector
from bpy.app.handlers import persistent
from gpu_extras.batch import batch_for_shader

def updateColors(self, context, prop):
    armO = bpy.context.object
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            arm = obj
            if not selectArmatureByName(self, context, obj.name, True, False):
                continue
            bgName, bgType = prop
            if bpy.app.version[0] > 3:
                if bgName not in arm.data.collections:
                    continue
                clct = arm.data.collections.get(bgName)
                if clct is None:
                    return
                for b in clct.bones:
                    if bgName == "DRB":
                        if bgType == "regular":
                            b.color.custom.normal = context.scene.drbColors.regular
                        elif bgType == "select":
                            b.color.custom.select = context.scene.drbColors.select
                        elif bgType == "active":
                            b.color.custom.active = context.scene.drbColors.active
                    elif bgName == "SRB":
                        if bgType == "regular":
                            b.color.custom.normal = context.scene.srbColors.regular
                        elif bgType == "select":
                            b.color.custom.select = context.scene.srbColors.select
                        elif bgType == "active":
                            b.color.custom.active = context.scene.srbColors.active
                    elif bgName == "AMPPRIM":
                        if bgType == "regular":
                            b.color.custom.normal = context.scene.ampPrimColors.regular
                    elif bgName == "SWWIND":
                        if bgType == "regular":
                            b.color.custom.normal = arm.windColor.regular
                        elif bgType == "select":
                            b.color.custom.select = arm.windColor.select
                        elif bgType == "active":
                            b.color.custom.active = arm.windColor.active
            else:    
                if bgName not in arm.pose.bone_groups:
                    continue
                bg = arm.pose.bone_groups.get(bgName)
                if bg is None:
                    return
                if bgName == "DRB":
                    if bgType == "regular":
                        bg.colors.normal = context.scene.drbColors.regular
                    elif bgType == "select":
                        bg.colors.select = context.scene.drbColors.select
                    elif bgType == "active":
                        bg.colors.active = context.scene.drbColors.active
                elif bgName == "SRB":
                    if bgType == "regular":
                        bg.colors.normal = context.scene.srbColors.regular
                    elif bgType == "select":
                        bg.colors.select = context.scene.srbColors.select
                    elif bgType == "active":
                        bg.colors.active = context.scene.srbColors.active
                elif bgName == "AMPPRIM":
                    if bgType == "regular":
                        bg.colors.normal = context.scene.ampPrimColors.regular
                elif bgName == "SWWIND":
                    if bgType == "regular":
                        bg.colors.normal = arm.windColor.regular
                    elif bgType == "select":
                        bg.colors.select = arm.windColor.select
                    elif bgType == "active":
                        bg.colors.active = arm.windColor.active
    selectArmatureByName(self, context, armO.name, True)

def getDRBBGroup(self, context, arm):
    #Create the bone group if not already present
    if bpy.app.version[0] > 3:
        if not arm.data.collections.get("DRB"):
            arm.data.collections.new(name="DRB")
        return arm.data.collections.get("DRB")   
    else:
        if not arm.pose.bone_groups.get("DRB"):
            bg = arm.pose.bone_groups.new(name="DRB")
            bg.color_set = "CUSTOM"
            bg.colors.normal = context.scene.drbColors.regular
            bg.colors.select = context.scene.drbColors.select
            bg.colors.active = context.scene.drbColors.active
        return arm.pose.bone_groups.get("DRB") 

def getSRBBGroup(self, context, arm):
    #Create the bone group if not already present
    if bpy.app.version[0] > 3:
        if not arm.data.collections.get("SRB"):
            arm.data.collections.new(name="SRB")
        return arm.data.collections.get("SRB")
    else:
        if not arm.pose.bone_groups.get("SRB"):
            bg = arm.pose.bone_groups.new(name="SRB")
            bg.color_set = "CUSTOM"
            bg.colors.normal = context.scene.srbColors.regular
            bg.colors.select = context.scene.srbColors.select
            bg.colors.active = context.scene.srbColors.active
        return arm.pose.bone_groups.get("SRB")

def getAMPPRIMBGroup(self, context, arm):
    #Create the bone group if not already present
    if bpy.app.version[0] > 3:
        if not arm.data.collections.get("AMPPRIM"):
            arm.data.collections.new(name="AMPPRIM")
        return arm.data.collections.get("AMPPRIM")
    else:
        if not arm.pose.bone_groups.get("AMPPRIM"):
            bg = arm.pose.bone_groups.new(name="AMPPRIM")
            bg.color_set = "CUSTOM"
            bg.colors.normal = context.scene.ampPrimColors.regular
            bg.colors.select = context.scene.ampPrimColors.select
            bg.colors.active = context.scene.ampPrimColors.active
        return arm.pose.bone_groups.get("AMPPRIM")

def getWindBGroup(self, context, arm):
    #Create the bone group if not already present
    if bpy.app.version[0] > 3:
        if not arm.data.collections.get("SWWIND"):
            arm.data.collections.new(name="SWWIND")
        return arm.data.collections.get("SWWIND")
    else:
        if not arm.pose.bone_groups.get("SWWIND"):
            bg = arm.pose.bone_groups.new(name="SWWIND")
            bg.color_set = "CUSTOM"
            bg.colors.normal = arm.windColor.regular
            bg.colors.select = arm.windColor.select
            bg.colors.active = arm.windColor.active
        return arm.pose.bone_groups.get("SWWIND")

def createCollection(self, context):
    if not bpy.data.collections.get("SW_Utils_Collection"):
        # Make sure that the current collection is the "big" one
        scene_collection = bpy.context.view_layer.layer_collection
        bpy.context.view_layer.active_layer_collection = scene_collection

        collection = bpy.data.collections.new("SW_Utils_Collection")
        collection.name = "SW_Utils_Collection"
        collection.hide_viewport = True
        collection.hide_render = True
        bpy.context.scene.collection.children.link(collection)

def createSphereShape(self, context, arm):
    # Collection
    createCollection(self, context)
    #   Create the UV sphere that will be used as the shape if not present
    if not bpy.data.objects.get("SW_Shape_Sphere"):
        # Make sure that the current collection is the "big" one
        scene_collection = bpy.context.view_layer.layer_collection
        bpy.context.view_layer.active_layer_collection = scene_collection

        mesh = bpy.data.meshes.new('SW_Shape_Sphere')
        basic_sphere = bpy.data.objects.new("SW_Shape_Sphere", mesh)
        basic_sphere.hide_render = True

        # Add the object into the scene, in the correct collection
        bpy.data.collections.get("SW_Utils_Collection").objects.link(basic_sphere)

        # Select the newly created object
        bpy.context.view_layer.objects.active = basic_sphere
        basic_sphere.select_set(True)

        # Construct the bmesh sphere and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius = 1)
        bm.to_mesh(mesh)
        bm.free()
        
        for o in bpy.context.selected_objects:
            o.select_set(False)
            o.hide_render = True

        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')

def createWindShape(self, context, arm):
    # Collection
    createCollection(self, context)
    #   Create the UV sphere that will be used as the shape if not present
    if not bpy.data.objects.get("SW_Shape_Wind"):
        # Make sure that the current collection is the "big" one
        scene_collection = bpy.context.view_layer.layer_collection
        bpy.context.view_layer.active_layer_collection = scene_collection

        arrow = bpy.data.objects.new("SW_Shape_Wind", None)
        arrow.hide_render = True

        # Add the object into the scene, in the correct collection
        bpy.data.collections.get("SW_Utils_Collection").objects.link(arrow)
        arrow.empty_display_type = 'SINGLE_ARROW'   
        
        for o in bpy.context.selected_objects:
            o.select_set(False)

        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')

def createCylinderShape(self, context, arm):
    # Collection
    createCollection(self, context)
    #   Create the cylinder that will be used as the shape if not present
    if not bpy.data.objects.get("SW_Shape_Cylinder"):
        # Make sure that the current collection is the "big" one
        scene_collection = bpy.context.view_layer.layer_collection
        bpy.context.view_layer.active_layer_collection = scene_collection

        mesh = bpy.data.meshes.new('SW_Shape_Cylinder')
        basic_cylinder = bpy.data.objects.new("SW_Shape_Cylinder", mesh)

        # Add the object into the scene, in the correct collection
        bpy.data.collections.get("SW_Utils_Collection").objects.link(basic_cylinder)

        # Select the newly created object
        bpy.context.view_layer.objects.active = basic_cylinder
        basic_cylinder.select_set(True)

        # Construct the bmesh sphere and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=1, radius2=1, depth=1)
        bm.to_mesh(mesh)
        bm.free()

        ob = bpy.data.objects['SW_Shape_Cylinder']
        ob.hide_render = True
        me = ob.data
        mw = ob.matrix_world
        local_verts = [Vector(v[:]) for v in ob.bound_box]
        o = sum(local_verts, Vector()) / 8
        o.z = min(v.z for v in local_verts)
        me.transform(Matrix.Translation(-o))

        mw.translation = mw @ o
        
        for o in bpy.context.selected_objects:
            o.select_set(False)

        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')
    
def createAmplitudeShape(self, context, arm):
    # Collection
    createCollection(self, context)
    #   Create the Cone that will be used as the shape if not present
    if not bpy.data.objects.get("SW_Shape_Amplitude"):
        # Make sure that the current collection is the "big" one
        scene_collection = bpy.context.view_layer.layer_collection
        bpy.context.view_layer.active_layer_collection = scene_collection

        mesh = bpy.data.meshes.new('SW_Shape_Amplitude')
        basic_cone = bpy.data.objects.new("SW_Shape_Amplitude", mesh)

        # Add the object into the scene, in the correct collection
        bpy.data.collections.get("SW_Utils_Collection").objects.link(basic_cone)

        # Select the newly created object
        bpy.context.view_layer.objects.active = basic_cone
        basic_cone.select_set(True)

        # Construct the bmesh sphere and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, depth=1, segments=16, radius1=1, radius2=0)
        bm.to_mesh(mesh)
        bm.free()

        ob = bpy.data.objects['SW_Shape_Amplitude']
        me = ob.data
        mw = ob.matrix_world
        local_verts = [Vector(v[:]) for v in ob.bound_box]
        o = sum(local_verts, Vector()) / 8
        o.z = max(v.z for v in local_verts)
        me.transform(Matrix.Translation(-o))

        mw.translation = mw @ o
        
        for o in bpy.context.selected_objects:
            o.select_set(False)

        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')

def addBone(self, context, arm, name, refBoneName, hideSelect = False, locLock = False, rotLock = False, scaleLock = True, inheritRot = True, parentOverride = False, parentIsNone = False, inheritScale = True, copyMat = True):
    bAddConstraintPrim = False
    bpy.ops.object.mode_set(mode='EDIT')
    refBone = arm.data.edit_bones.get(refBoneName)
    parentRefBone = None
    if parentOverride:
        parentRefBone = refBone.parent
        if refBone.parent is None:
            parentRefBone = refBone
        elif not arm.pose.bones[parentRefBone.name].bIsDRB:
            bAddConstraintPrim = True
    editBone = arm.data.edit_bones.new(name)
    editBone.length = refBone.length
    if copyMat:
        editBone.matrix = refBone.matrix.copy()
    if not parentIsNone:
        editBone.parent = refBone if not parentOverride else parentRefBone
    else:
        editBone.parent = None
    editBone.hide = True
    editBone.hide_select = hideSelect
    editBone.use_inherit_rotation = inheritRot
    if not inheritScale:
        editBone.inherit_scale = 'NONE'
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='POSE')
    pbone = arm.pose.bones[name]
    pbone.lock_scale = [scaleLock for _ in range(3)] # radius issues otherwise
    pbone.lock_rotation = [rotLock for _ in range(3)]
    pbone.lock_location = [locLock for _ in range(3)]
    if bAddConstraintPrim:
        constraint = pbone.constraints.new('COPY_LOCATION')
        constraint.target = pbone.id_data
        constraint.subtarget = refBone.name
    return pbone

def removeBone(self, context, arm, bName):
    bpy.ops.object.mode_set(mode='EDIT')
    if arm.data.edit_bones.get(bName):
        arm.data.edit_bones.remove(arm.data.edit_bones.get(bName))
    bpy.ops.object.mode_set(mode='POSE')

def addWindPrimitive(self, context):
    #Add the primitive
    scene = context.scene
    arm = bpy.context.object
    if arm.pose.bones.get("SW_Shape_Wind") is not None:
        return
    activePbCache = bpy.context.active_pose_bone
    selectedPbCache = []
    for pb in bpy.context.selected_pose_bones:
        selectedPbCache.append(pb)

    bg = getWindBGroup(self, context, bpy.context.object)
    createWindShape(self, context, bpy.context.object)
    pBone = addBone(self, context, bpy.context.object, "SW_Shape_Wind", bpy.context.active_pose_bone.name, parentIsNone=True,hideSelect=True, copyMat=False)
    if bpy.app.version[0] > 3:
        bg.assign(pBone.bone)
        pBone.bone.color.palette = 'CUSTOM'
        updateColors(self, context, ['SWWIND','regular'])
        updateColors(self, context, ['SWWIND','select'])
        updateColors(self, context, ['SWWIND','active'])
    else:
        pBone.bone_group = bg
    pBone.custom_shape = bpy.data.objects.get("SW_Shape_Wind")
    pBone.use_custom_shape_bone_size = False
    pBone.custom_shape_scale_xyz = [1 for _ in range(3)]
    pBone.bone.show_wire = True
    pBone.bone.use_deform = False

    if bpy.app.version[0] < 5:
        pBone.bone.hide = not arm.bShowWind
    else:
        pBone.hide = not arm.bShowWind

    for pb in selectedPbCache:
        if bpy.app.version[0] < 5:
            pb.bone.select = True
        else:
            pb.select = True
    if bpy.app.version[0] < 5:
        activePbCache.bone.select = True
    else:
        activePbCache.select = True

def selectArmatureByName(self, context, armName, bSwitchToPoseMode, bPreObjectMode = True):
    if bpy.context.view_layer.objects.get(armName) is None or not bpy.context.view_layer.objects.get(armName).visible_get():
        return False
    if bpy.context.view_layer.objects.active is None or not bpy.context.view_layer.objects.active.visible_get():        
        bpy.context.view_layer.objects.active = bpy.data.objects[armName]
    if bPreObjectMode: 
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    objectToSelect = bpy.data.objects[armName]
    objectToSelect.select_set(True)    
    bpy.context.view_layer.objects.active = objectToSelect
    if bSwitchToPoseMode:
        bpy.ops.object.mode_set(mode='POSE')
    return True

def removeWindPrimitive(self, context, arm):
    if arm.pose.bones.get("SW_Shape_Wind") is not None:
        removeBone(self, context, arm, "SW_Shape_Wind")
        arm.data.bUseWind=False

def evaluateWind(arm):
    w = Vector([arm.swWind[0],arm.swWind[1],arm.swWind[2]])
    t = (bpy.context.scene.frame_current - bpy.context.scene.frame_start)
    if arm.cupSwWindX is not None:
        if bpy.app.version[0] < 5:
            cx, Tx, Ax = arm.cupSwWindX.curve, arm.cupSwWindX.cupSwPeriod, arm.cupSwWindX.cupSwAmplitude
        else:
            cx, Tx, Ax = arm.cupSwWindX.curve_distance_falloff, arm.cupSwWindX.cupSwPeriod, arm.cupSwWindX.cupSwAmplitude
        w[0] =  cx.evaluate(cx.curves[0], t%Tx/Tx) * Ax
    if arm.cupSwWindY is not None:
        if bpy.app.version[0] < 5:
            cy, Ty, Ay = arm.cupSwWindY.curve, arm.cupSwWindY.cupSwPeriod, arm.cupSwWindY.cupSwAmplitude
        else:
            cy, Ty, Ay = arm.cupSwWindY.curve_distance_falloff, arm.cupSwWindY.cupSwPeriod, arm.cupSwWindY.cupSwAmplitude
        w[1] = cy.evaluate(cy.curves[0], t%Ty/Ty) * Ay
    if arm.cupSwWindZ is not None:
        if bpy.app.version[0] < 5:
            cz, Tz, Az = arm.cupSwWindZ.curve, arm.cupSwWindZ.cupSwPeriod, arm.cupSwWindZ.cupSwAmplitude
        else:
            cz, Tz, Az = arm.cupSwWindZ.curve_distance_falloff, arm.cupSwWindZ.cupSwPeriod, arm.cupSwWindZ.cupSwAmplitude
        w[2] = cz.evaluate(cz.curves[0], t%Tz/Tz) * Az
    return w

def updateWindPrimitive(arm, windVel):
    if not arm.bShowWind:
        return
    windPb = arm.pose.bones.get("SW_Shape_Wind")
    if windPb is not None: #Should be the case if the param was touched
        if windVel.length:
            o = Vector([0, 0, 1])
            t = Vector([windVel[0], windVel[1], windVel[2]])
            rd = o.rotation_difference(t)            
            q = arm.matrix_world.inverted_safe().to_quaternion()
            windPb.matrix = q.to_matrix().to_4x4() @ rd.to_matrix().to_4x4()               
        windPb.custom_shape_scale_xyz =[windVel.length * arm.swWindArrowScale for _ in range(3)]

def addAmplitudePrimitive(self, context):

    #Add the primitive
    scene = context.scene
    # amprimList = scene.amprimList
    activePbCache = bpy.context.active_pose_bone
    selectedPbCache = []
    for pb in bpy.context.selected_pose_bones:
        if pb.id_data != bpy.context.object:
            if not selectArmatureByName(self, context, pb.id_data.name, True, False):
                continue
        if not pb.bIsDRB:
            continue
        selectedPbCache.append(pb)
        refBoneName = pb.name
        arm = bpy.context.object
        if arm.pose.bones.get("SW_AMPPRIM_" + refBoneName) is not None:
            continue
        # amprim = amprimList.ampPrimCollection.add()
        amprimName = "SW_AMPPRIM_" + refBoneName

        bg = getAMPPRIMBGroup(self, context, bpy.context.object)
        createAmplitudeShape(self, context, bpy.context.object)
        if pb.parent is None:
            pBone = addBone(self, context, bpy.context.object, amprimName, refBoneName, hideSelect=True, locLock=False, rotLock=True, scaleLock=True, inheritRot=False, parentOverride=True)
        elif not pb.parent.bIsDRB:
            pBone = addBone(self, context, bpy.context.object, amprimName, refBoneName, hideSelect=True, locLock=False, rotLock=True, scaleLock=True, inheritRot=False, parentOverride=True)
        else:
            pBone = addBone(self, context, bpy.context.object, amprimName, refBoneName, hideSelect=True, locLock=False, rotLock=True, scaleLock=True, inheritRot=True, parentOverride=True)
        if bpy.app.version[0] > 3:
            bg.assign(pBone.bone)
            pBone.bone.color.palette = 'CUSTOM'
            updateColors(self, context, ['AMPPRIM','regular'])
        else:
            pBone.bone_group = bg
        pBone.custom_shape = bpy.data.objects.get("SW_Shape_Amplitude")
        pBone.use_custom_shape_bone_size = False
        pBone.custom_shape_scale_xyz = [pb.pSwDrbRadius * 2 for _ in range(3)]
        updateAmplitudePrimitive(pb, pBone)
        #if len(pb.children):#ignore last one ?
        pBone.custom_shape_rotation_euler[0] = 1.57
        pBone.bone.show_wire = True
        pBone.bone.use_deform = False
        if bpy.app.version[0] < 5:
            pBone.bone.hide = not pb.pSwDrbShowAmplitude
        else:
            pBone.hide = not pb.pSwDrbShowAmplitude

    for pb in selectedPbCache:
        if pb.id_data != bpy.context.object:
            if not selectArmatureByName(self, context, pb.id_data.name, True, False):
                continue
        if bpy.app.version[0] < 5:
            pb.bone.select = True
        else:
            pb.select = True
    if bpy.app.version[0] < 5:
        activePbCache.bone.select = True
    else:
        activePbCache.select = True

def updateAmplitudePrimitive(pb, ampPrimPb):
    if pb.pSwDrbAmplitudeType == 'C':
        if pb.pSwDrbAmplitude <= 45:
            r = pb.pSwDrbRadius * 2 * tan(pb.pSwDrbAmplitude * pi / 180)
            for j in range(2):
                ampPrimPb.custom_shape_scale_xyz[j] = r
            ampPrimPb.custom_shape_scale_xyz[2] = pb.pSwDrbRadius * 2
        else:
            ampPrimPb.custom_shape_scale_xyz[2] = pb.pSwDrbRadius * 2 / tan(pb.pSwDrbAmplitude * pi / 180)
            for j in range(2):
                ampPrimPb.custom_shape_scale_xyz[j] = pb.pSwDrbRadius * 2
    elif pb.pSwDrbAmplitudeType == 'E':
        #Impose a hard limit on the two amplitudes right now due to the difficulty of the visual representations                        
        if pb.pSwDrbAmplitude < 5:
            pb.pSwDrbAmplitude = 5
        elif pb.pSwDrbAmplitude > 70:
            pb.pSwDrbAmplitude = 70
        ampPrimPb.custom_shape_scale_xyz[0] = pb.pSwDrbRadius * 2 * tan(pb.pSwDrbAmplitude * pi / 180)
        ampPrimPb.custom_shape_scale_xyz[1] = pb.pSwDrbRadius * 2 * tan(pb.pSwDrbAmplitude2 * pi / 180)
        ampPrimPb.custom_shape_scale_xyz[2] = pb.pSwDrbRadius * 2

def removeAmplitudePrimitive(self, context, arm):
    selectedPbCache = []
    for pb in bpy.context.selected_pose_bones:
        if pb.id_data != bpy.context.object:
            if not selectArmatureByName(self, context, pb.id_data.name, True, False):
                continue
        refBoneName = pb.name
        if arm.pose.bones.get("SW_AMPPRIM_" + refBoneName) is None:
            continue
        removeBone(self, context, arm, "SW_AMPPRIM_" + refBoneName)
    for pb in selectedPbCache:
        if pb.id_data != bpy.context.object:
            if not selectArmatureByName(self, context, pb.id_data.name, True, False):
                continue
        if bpy.app.version[0] < 5:
            pb.bone.select = True
        else:
            pb.select = True

def removeAmplitudePrimitiveFromAllBones(self, context, arm, pbs):
    # amprimList = bpy.context.scene.amprimList
    for pb in pbs:
        if pb.id_data != bpy.context.object:
            if not selectArmatureByName(self, context, pb.id_data.name, True, False):
                continue
        if pb.name.startswith("SW_AMPPRIM_"):
            removeBone(self, context, arm, pb.name)

def addAmplitudePrimitiveForAllBones(self, context, arm, pbs):
    # amprimList = bpy.context.scene.amprimList
    for pb in pbs:
        if pb.id_data != bpy.context.object:
            if not selectArmatureByName(self, context, pb.id_data.name, True, False):
                continue
        if not pb.bIsDRB or not pb.pSwDrbShowAmplitude or not pb.pSwDrbUseAmplitude:
            continue
        refBoneName = pb.name
        arm = bpy.context.object
        if arm.pose.bones.get("SW_AMPPRIM_" + refBoneName) is not None:
            continue

        # amprim = amprimList.ampPrimCollection.add()
        amprimName = "SW_AMPPRIM_" + refBoneName

        bg = getAMPPRIMBGroup(self, context, bpy.context.object)
        createAmplitudeShape(self, context, bpy.context.object)
        if pb.parent is None:
            pBone = addBone(self, context, bpy.context.object, amprimName, refBoneName, hideSelect=True, locLock=False, rotLock=True, scaleLock=True, inheritRot=False, parentOverride=True)
        elif not pb.parent.bIsDRB:
            pBone = addBone(self, context, bpy.context.object, amprimName, refBoneName, hideSelect=True, locLock=False, rotLock=True, scaleLock=True, inheritRot=False, parentOverride=True)
        else:
            pBone = addBone(self, context, bpy.context.object, amprimName, refBoneName, hideSelect=True, locLock=False, rotLock=True, scaleLock=True, inheritRot=True, parentOverride=True)
        if bpy.app.version[0] > 3:
            bg.assign(pBone.bone)
            pBone.bone.color.palette = 'CUSTOM'
            updateColors(self, context, ['AMPPRIM','regular'])
        else:
            pBone.bone_group = bg
        pBone.custom_shape = bpy.data.objects.get("SW_Shape_Amplitude")
        pBone.use_custom_shape_bone_size = False
        pBone.custom_shape_scale_xyz = [pb.pSwDrbRadius * 2 for _ in range(3)]
        updateAmplitudePrimitive(pb, pBone)
        #if len(pb.children):#ignore last one ?
        pBone.custom_shape_rotation_euler[0] = 1.57
        pBone.bone.show_wire = True
        pBone.bone.use_deform = False

def getUpdatedPose(pb, parentPoseMat):
    restPosMat = None
    if pb.parent:
        mat = pb.bone.matrix.to_4x4()
        mat.translation = pb.bone.head
        mat.translation.y += pb.bone.parent.length
        restPosMat = parentPoseMat @ mat
    else:
        restPosMat = pb.bone.matrix_local
    poseMat = restPosMat @ pb.matrix_basis
    poseMat.translation = restPosMat @ pb.matrix_basis.translation
    return poseMat

class DrawingClass:
    def __init__(self):
        self.handle = None
        self.shader = None

    def set(self, context):
        if self.handle is None:
            if bpy.app.version[0] > 3:
                self.shader =  gpu.shader.from_builtin('FLAT_COLOR')
            else:
                self.shader =  gpu.shader.from_builtin('3D_FLAT_COLOR')
            self.handle = bpy.types.SpaceView3D.draw_handler_add(
                    self.draw_links_callback,(context,),
                    'WINDOW', 'POST_VIEW')
            
            self.shader.bind()

    def draw_links_callback(self, context):
        if context.mode != "POSE":
            return
        scene = context.scene
        arm = context.active_object
        if not arm.bSwDisplayShape:
            return
        linkList = arm.data.swLinkList
        if not len(linkList.linkCollection):
            self.remove_handle()
            return
        coords = []
        cols = []
        toremove = []
        for idx, link in enumerate(linkList.linkCollection):  
            if link.bHidden:
                continue
            b0, b1 = link.linkedBones[0], link.linkedBones[1]
            p0 = bpy.data.objects.get(arm.name).pose.bones.get(b0.boneName)
            p1 = bpy.data.objects.get(arm.name).pose.bones.get(b1.boneName)            

            if p0 is None or p1 is None or not p0.bIsDRB or not p1.bIsDRB: #fast enough check to see if a bone has been baked/removed etc
                toremove.append(idx)
                continue

            if bpy.app.version[0] < 5:
                if p0.bone.hide or p1.bone.hide:
                    continue
            else:
                if p0.hide or p1.hide:
                    continue

            if bpy.context.view_layer.objects.get(arm.name) is None or bpy.context.view_layer.objects.get(arm.name) is None:
                continue
            if p0.bone.hide or p1.bone.hide:
                continue
            
            pos0 = p0.matrix.translation @ bpy.data.objects[arm.name].matrix_world.inverted_safe() + bpy.data.objects[arm.name].matrix_world.translation
            pos1 = p1.matrix.translation @ bpy.data.objects[arm.name].matrix_world.inverted_safe() + bpy.data.objects[arm.name].matrix_world.translation

            center = (pos1 - pos0)/2 + pos0

            maxA, maxB = (pos0 - center).normalized()*link.l0/2 + center, (pos1 - center).normalized()*link.l0/2 + center
            A, B = pos0, pos1
            # if link.minL < link.l0:
            #     minA, minB = (pos0 - center).normalized()*(link.l0/2 - link.minL/2) + center, (pos1 - center).normalized()*(link.l0/2 - link.minL/2) + center
            # else:
            #     minA, minB = center, center
            
            
            
            coords.append(tuple(pos0))
            coords.append(tuple(pos1)) 
            coords.append(tuple(maxA))
            coords.append(tuple(maxB))           
            col = scene.swLinkColor.regular if link.bIsActive else scene.swLinkColor.inactive 
            col2 = scene.swLinkColor.maxL if link.bIsActive else scene.swLinkColor.inactive          
            # cols.append(tuple((col.b, col.g, col.r, 1)))
            # cols.append(tuple((col.b, col.g, col.r, 1)))
            cols.append(tuple((col2.r, col2.g, col2.b, 1)))
            cols.append(tuple((col2.r, col2.g, col2.b, 1)))
            cols.append(tuple((col.r, col.g, col.b, 1)))
            cols.append(tuple((col.r, col.g, col.b, 1)))
        for idx in toremove:
            linkList.linkCollection.remove(idx)
        if toremove:
            scene.swLinkLock = True
            linkList.activeLinkIndex -= len(toremove)
            if linkList.activeLinkIndex == -1 and len(linkList.linkCollection):
                linkList.activeLinkIndex = 0  
            scene.swLinkLock = False
        gpu.state.line_width_set(scene.swLinkLineWidth)
        # col = scene.swLinkColor.regular if link.bIsActive else scene.swLinkColor.inactive
        self.shader.bind()
        # self.shader.uniform_float("color", (col.r, col.g, col.b, 1))
        batch = batch_for_shader(self.shader, 'LINES', {"pos": coords, "color": cols})
        
        batch.draw(self.shader)
        

    def remove_handle(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
        self.handle = None
        self.shader = None

#Only way to have something persisting through Blender sessions it seems
gSwDrawInstance = DrawingClass()
    



