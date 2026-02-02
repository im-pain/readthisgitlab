from math import pow, tan, pi
from random import gauss

import bpy
from bpy.app.handlers import persistent
from mathutils import Matrix, Vector

from .SwingUtils import evaluateWind, getUpdatedPose, updateWindPrimitive

#"Writing to ID classes in this context is not allowed", using this hack instead
global gbIsRendering
gbIsRendering = False

@persistent
def SWBakeTrue(scene, depsgraph):
    global gbIsRendering
    gbIsRendering = True
@persistent
def SWBakeFalse(scene, depsgraph):
    global gbIsRendering
    gbIsRendering = False

@persistent
def SWTick(scene, depsgraph):
    

    #Get "accurate" delta time ? Fixed for now
    deltaTime = 1/bpy.context.scene.render.fps
    cylinder = bpy.data.objects.get("SW_Shape_Cylinder")
    if bpy.context.screen is not None and (not scene.bSwForceRendering or bpy.context.screen.is_scrubbing) and (not gbIsRendering and not scene.bSwIsBaking) and (bpy.context.screen.is_scrubbing or not bpy.context.screen.is_animation_playing):
        return
    paramScaleFactor = 30/bpy.context.scene.render.fps

    if scene.bSwIsBaking: #when baking, all view layers where the armature is are triggering the tick for some reason.
        if scene.frame_current == scene["FrameSeen"]:
            return
        else:
            scene["FrameSeen"] = scene.frame_current

    #solver
    armToUpdate = set()
    # simDrbs = []
    # cachedExtra = {}
    # nameToInfo = {}

    for arm in bpy.data.objects:
        simDrbs = []
        cachedExtra = {}
        nameToInfo = {}
        if arm.type != "ARMATURE":
            continue
        if arm.library is not None: #prevent taking into account the linked ones
            continue
        drbList = arm.data.drbList
        srbList = arm.data.srbList
        linkList = arm.data.swLinkList
        bBoneNotFound = False
        for i in range(len(drbList.boneChainCollection)):
            #arm = bpy.data.objects[drbList.boneChainCollection[i].armName]#.evaluated_get(depsgraph)
            if scene.armBakingName != "" and scene.armBakingName != arm.name:
                continue
            #cache some reused values 
            cachedRootP = None
            cachedRootPLInvMat = None
            cachedArmMWInv = arm.matrix_world.inverted_safe()
            if drbList.boneChainCollection[i].boneCollection[0].boneName not in arm.pose.bones:
                bpy.context.view_layer.objects.active = arm
                bpy.ops.sw.ot_drbrescanallchains("INVOKE_DEFAULT")
                bBoneNotFound = True
                continue
            if arm.pose.bones[drbList.boneChainCollection[i].boneCollection[0].boneName].parent is not None:
                cachedRootP = arm.pose.bones[drbList.boneChainCollection[i].boneCollection[0].boneName].parent
                cachedRootPLInvMat = cachedRootP.bone.matrix_local.inverted_safe()

            armEval = arm.evaluated_get(depsgraph)
            windVel = evaluateWind(arm)if armEval.data.bUseWind else Vector([0,0,0])        
            if armEval.data.bUseWind:
                updateWindPrimitive(arm,windVel)
                windVel.rotate(cachedArmMWInv)            
                windVel = windVel*gauss(armEval.swWindMean,armEval.swWindStd)*deltaTime 
            gravVel =  Vector(scene.gravity) * deltaTime
            gravVel.rotate(cachedArmMWInv)
            if arm.data.soArmPrevPos == Vector([0,0,0]):
                arm.data.soArmPrevPos = arm.matrix_world.translation
            worldTPos = Vector(arm.matrix_world.translation) - Vector(arm.data.soArmPrevPos)
            worldTPos.rotate(cachedArmMWInv)
            if not arm.bSwSimulate:
                continue
            armToUpdate.add(arm)

            for b in drbList.boneChainCollection[i].boneCollection:
                if b.boneName not in arm.pose.bones:
                    bpy.context.view_layer.objects.active = arm
                    bpy.ops.sw.ot_drbrescanallchains("INVOKE_DEFAULT")
                    bBoneNotFound = True
                else:
                    simDrbs.append([b, arm, armEval, windVel,gravVel,worldTPos, cachedRootP, cachedRootPLInvMat, cachedArmMWInv, i])
                    nameToInfo[arm.name + "|||" + b.boneName] = {}
        
        if bBoneNotFound:
            continue

    
        for simDrb in simDrbs:
            b, arm, armEval, windVel,gravVel,worldTPos, cachedRootP, cachedRootPLInvMat, cachedArmMWInv, chainIdx = simDrb
            drb = arm.pose.bones[b.boneName]
            drbEval = armEval.pose.bones[b.boneName]             
            preSimPos = Vector(drb.matrix.translation)
            postSimPos = Vector(drb.matrix.translation)  
            #For this to work, hierarchy must be gone through in the right order. Which is guaranteed by the parsing order
            parent = drb.parent
            if parent is None or not parent.bIsDRB:
                drb.soSwUpdatedPos = Vector(drb.matrix.translation)
                cachedExtra[drb] = [None, None, None, None]
                continue
            parentPreSimPos = Vector(parent.matrix.translation)
            parentPostSimPos = Vector(parent.matrix.translation)

            if scene.bSwIsBaking and scene.bSwDropBake: #special bake
                if scene.frame_current < scene["SwPrevFrame"]:
                    scene.bSwIsBaking = False
                    bpy.ops.screen.animation_play()
                    bpy.ops.sw.ot_drbclear()
                    
                    for entryName in scene["BoneKFMap"]:
                        armName, bName = entryName.split("|||")
                        pb = bpy.data.objects[armName].pose.bones[bName]
                        for kf in scene["BoneKFMap"][entryName]:
                            # kfMat = scene["BoneKFMap"][entryName][kf]
                            # mat = Matrix()
                            # for u in range(4):
                            #     for v in range(4):
                            #         mat[u][v] = kfMat[u][v]
                            # loc, rot, sca = mat.decompose()
                            loc, rot = scene["BoneKFMap"][entryName][kf]
                            pb.location = loc
                            pb.rotation_quaternion = rot
                            pb.keyframe_insert(data_path="location", frame=int(kf))
                            pb.keyframe_insert(data_path="rotation_quaternion", frame=int(kf))
                    del scene["BoneKFMap"]
                    return
                scene["SwPrevFrame"] = scene.frame_current   
                if arm.name + "|||" + parent.name not in scene["BoneKFMap"]:
                    scene["BoneKFMap"][arm.name + "|||" + parent.name] = {}
                # mat = Matrix(parent.matrix_basis)
                l, r, s = Matrix(parent.matrix_basis).decompose()
                # scene["BoneKFMap"][arm.name + "|||" + parent.name][str(scene.frame_current)] = mat
                scene["BoneKFMap"][arm.name + "|||" + parent.name][str(scene.frame_current)] = [l,r]

            if bpy.app.version[0] < 5:
                drbDamping = drb.cupSwDrbDamping.curve.evaluate(drb.cupSwDrbDamping.curve.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbDamping is not None else drbEval.pSwDrbDamping
                drbDrag = drb.cupSwDrbDrag.curve.evaluate(drb.cupSwDrbDrag.curve.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbDrag is not None else drbEval.pSwDrbDrag
                drbStiffness = drb.cupSwDrbStiffness.curve.evaluate(drb.cupSwDrbStiffness.curve.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbStiffness is not None else drbEval.pSwDrbStiffness
                drbWindFactor = drb.cupSwDrbWindFactor.curve.evaluate(drb.cupSwDrbWindFactor.curve.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbWindFactor is not None else drbEval.pSwDrbWindFactor
                drbGravFactor = drb.cupSwDrbGravityFactor.curve.evaluate(drb.cupSwDrbGravityFactor.curve.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbGravityFactor is not None else drbEval.pSwDrbGravityFactor
            else:
                drbDamping = drb.cupSwDrbDamping.curve_distance_falloff.evaluate(drb.cupSwDrbDamping.curve_distance_falloff.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbDamping is not None else drbEval.pSwDrbDamping
                drbDrag = drb.cupSwDrbDrag.curve_distance_falloff.evaluate(drb.cupSwDrbDrag.curve_distance_falloff.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbDrag is not None else drbEval.pSwDrbDrag
                drbStiffness = drb.cupSwDrbStiffness.curve_distance_falloff.evaluate(drb.cupSwDrbStiffness.curve_distance_falloff.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbStiffness is not None else drbEval.pSwDrbStiffness
                drbWindFactor = drb.cupSwDrbWindFactor.curve_distance_falloff.evaluate(drb.cupSwDrbWindFactor.curve_distance_falloff.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbWindFactor is not None else drbEval.pSwDrbWindFactor
                drbGravFactor = drb.cupSwDrbGravityFactor.curve_distance_falloff.evaluate(drb.cupSwDrbGravityFactor.curve_distance_falloff.curves[0], drb.cuSwDrbChainPercentage) if drb.cupSwDrbGravityFactor is not None else drbEval.pSwDrbGravityFactor
            drbRadius = drb.pSwDrbRadius
            #World space rotation contribution
            drbPrevRWPos = Vector(drb.soSwRWPos)
            rWPos = Vector(drb.matrix.translation @ cachedArmMWInv)
            drb.soSwRWPos = rWPos
            worldRPos = (rWPos - drbPrevRWPos) @ arm.matrix_world
            #Velocity computation
            drb.soSwPrevVel = Vector(drb.soSwPrevVel)* pow(1-drbDamping,paramScaleFactor) + (Vector(drb.soSwUpdatedPos)- preSimPos - worldTPos - worldRPos)/deltaTime* drbDrag + gravVel*drbGravFactor + windVel*drbWindFactor
            postSimPos = postSimPos + Vector(drb.soSwPrevVel) * (1-drb.soSwPrevFriction) * deltaTime 
            #stiffness
            v = drb.bone.matrix_local.translation - parent.bone.matrix_local.translation
            if cachedRootP is not None:
                t = arm.convert_space(pose_bone=cachedRootP,matrix=cachedArmMWInv @ cachedRootP.matrix @ cachedRootPLInvMat, from_space='POSE', to_space="WORLD")
                # t = arm.convert_space(pose_bone=cachedRootP,matrix=cachedRootP.matrix_basis, from_space='POSE', to_space="WORLD")
                # t = arm.convert_space(pose_bone=cachedRootP,matrix=cachedArmMWInv @t, from_space='POSE', to_space="WORLD")
                v.rotate(t)
            swingLessPos = parentPostSimPos + v
            postSimPos += (swingLessPos - postSimPos)  * drbStiffness #Need to find a proper way to scale with framerate, leads to unexpected behavior otherwise
            friction = 0
            cachedExtra[drb] = [preSimPos,postSimPos,parentPreSimPos,parentPostSimPos, friction] 
            nameToInfo[arm.name + "|||" + b.boneName]["cachedPos"] = postSimPos

        for link in linkList.linkCollection:
            link.lambdA = 0

        for link in linkList.linkCollection:
            if not link.bIsActive:
                continue
            
            b0, b1 = link.linkedBones[0], link.linkedBones[1]
            k0, k1 = arm.name + "|||" + b0.boneName, arm.name + "|||" + b1.boneName
            if k0 not in nameToInfo or k1 not in nameToInfo:
                continue
                
            for it in range(3):
                p0, p1 = nameToInfo[arm.name + "|||" + b0.boneName]["cachedPos"], nameToInfo[arm.name + "|||" + b1.boneName]["cachedPos"]
                delta = p1 - p0
                deltaL = delta.length

                l  = deltaL - link.l0
                delta = (delta / deltaL) * l; 

                nameToInfo[arm.name + "|||" + b0.boneName]["cachedPos"] += delta/2 
                nameToInfo[arm.name + "|||" + b1.boneName]["cachedPos"] -= delta/2

        for simDrb in simDrbs:
            b, arm, armEval, windVel,gravVel,worldTPos, cachedRootP, cachedRootPLInvMat, cachedArmMWInv,  chainIdx= simDrb
            
            drb = arm.pose.bones[b.boneName]
            drbEval = armEval.pose.bones[b.boneName] 
            drbRadius = drb.pSwDrbRadius 
            parent = drb.parent
            if parent is None or not parent.bIsDRB:
                continue
            preSimPos, postSimPos, parentPreSimPos, parentPostSimPos, friction = cachedExtra[drb]
            postSimPos = nameToInfo[arm.name + "|||" + b.boneName]["cachedPos"]

            #collision with SRBs
            collLayer = 0
            for i,l in enumerate(drb.pSwDrbCollLayer):
                if l:
                    collLayer = i
                    break
            for collider in srbList.colliderCollection:
                srbArm = arm
                if collider.name not in srbArm.pose.bones:
                    bpy.context.view_layer.objects.active = srbArm
                    bpy.ops.sw.ot_srbrescanallchains("INVOKE_DEFAULT")
                srb = srbArm.pose.bones[collider.name]
                if not srb.pSwSrbCollLayers[collLayer]:
                    continue
                if srb.custom_shape == cylinder:
                    postSimPos = (arm.matrix_world.translation + postSimPos @ cachedArmMWInv)
                    pTemp = (-srbArm.matrix_world.translation + postSimPos) @ srbArm.matrix_world
                    postSimPosLocal = (-srb.matrix.translation + pTemp) @ srb.matrix
                    threshold = drbRadius + srb.pSwSrbRadius
                    P = Vector([0,postSimPosLocal[1],0])
                    distance = (postSimPosLocal - P).length
                    if distance < threshold:
                        if not(postSimPosLocal[1] < 0 or postSimPosLocal[1] > srb.pSwSrbDepth):                      
                            postSimPosLocal += (threshold - distance) * (postSimPosLocal - P).normalized()
                        elif postSimPosLocal[1] < 0 and postSimPosLocal[1] > -drbRadius:                        
                            if distance > srb.pSwSrbRadius:
                                postSimPosLocal += (threshold - distance) * (postSimPosLocal - P).normalized()
                            else:
                                postSimPosLocal[1] = -drbRadius
                            
                        elif postSimPosLocal[1] > srb.pSwSrbDepth and postSimPosLocal[1] < drbRadius + srb.pSwSrbDepth:
                            if distance > srb.pSwSrbRadius:
                                postSimPosLocal += (threshold - distance) * (postSimPosLocal - P).normalized()
                            else:
                                postSimPosLocal[1] = drbRadius + srb.pSwSrbDepth
                        postSimPos = (postSimPosLocal @ srb.matrix.inverted_safe()+srb.matrix.translation)
                        postSimPos = (postSimPos @ srbArm.matrix_world.inverted_safe() + srbArm.matrix_world.translation)
                        friction = max(friction, srb.pSwSrbFriction)
                    postSimPos =  (postSimPos-arm.matrix_world.translation) @ arm.matrix_world
                else:
                    # threshold = drbRadius + srb.pSwSrbRadius
                    # postSimPos = (arm.matrix_world.translation + postSimPos @ cachedArmMWInv)
                    # srbPos = (srbArm.matrix_world.translation + srb.matrix.translation)
                    # distance = (postSimPos - srbPos).length
                    # if distance < threshold: 
                    #     postSimPos += (threshold - distance) * (postSimPos - srbPos).normalized()                    
                    # postSimPos =  (postSimPos-arm.matrix_world.translation) @ arm.matrix_world
                    if (drbEval.bHasColliderXAxis or drbEval.bHasColliderZAxis):
                        postSimPos = (arm.matrix_world.translation + postSimPos @ cachedArmMWInv)
                        pTemp = (-srbArm.matrix_world.translation + postSimPos) @ srbArm.matrix_world
                        postSimPosLocal = (-srb.matrix.translation + pTemp) @ srb.matrix
                        threshold = drbRadius + srb.pSwSrbRadius
                        distance = postSimPosLocal.length
                        if distance < threshold:
                            if drbEval.bHasColliderXAxis:
                                if drbEval.bHasColliderZAxis:
                                    postSimPosLocal += (threshold - distance) * postSimPosLocal.normalized()
                                else:
                                    P = Vector([0,0,postSimPosLocal[2]])
                                    postSimPosLocal += (threshold - distance) * (postSimPosLocal - P).normalized()
                            else:
                                # kl = sqrt(threshold * threshold - postSimPosLocal[0] * postSimPosLocal[0] - postSimPosLocal[1] * postSimPosLocal[1])
                                # if not drbEval.bHasColliderPosAxis:
                                #     postSimPosLocal[2] = -kl
                                # elif not drbEval.bHasColliderNegAxis:
                                #     postSimPosLocal[2] = kl
                                # else:
                                #     postSimPosLocal[2] = kl if (postSimPosLocal[2]-kl)**2<(postSimPosLocal[2]+kl)**2 else -kl
                                P = Vector([postSimPosLocal[0],0,0])
                                postSimPosLocal += (threshold - distance) * (postSimPosLocal - P).normalized()
                                
                            # postSimPosLocal += (threshold - distance) * postSimPosLocal.normalized()
                            postSimPos = (postSimPosLocal @ srb.matrix.inverted_safe()+srb.matrix.translation)
                            postSimPos = (postSimPos @ srbArm.matrix_world.inverted_safe() + srbArm.matrix_world.translation)
                            friction = max(friction, srb.pSwSrbFriction)
                        postSimPos =  (postSimPos-arm.matrix_world.translation) @ arm.matrix_world

            #collision with DRBs
            if drb.pSwDrbCollIntra:
                for i in range(len(drbList.boneChainCollection)):
                    if i == chainIdx:
                        continue
                    # armBis = bpy.data.objects[drbList.boneChainCollection[i].armName]
                    armBis = arm
                    for b in drbList.boneChainCollection[i].boneCollection:
                        drbBis = armBis.pose.bones[b.boneName]
                        if drbBis == drb or not drbBis.pSwDrbCollIntra or not drbBis.pSwDrbCollLayer[collLayer]:
                            continue
                        postSimPos = (arm.matrix_world.translation + postSimPos @ cachedArmMWInv)
                        pTemp = (-armBis.matrix_world.translation + postSimPos) @ armBis.matrix_world
                        postSimPosLocal = (-drbBis.matrix.translation + pTemp) @ drbBis.matrix
                        threshold = drbRadius + drbBis.pSwDrbRadius
                        distance = postSimPosLocal.length
                        if distance < threshold:
                            postSimPosLocal += (threshold - distance) * postSimPosLocal.normalized()
                            postSimPos = (postSimPosLocal @ drbBis.matrix.inverted_safe()+drbBis.matrix.translation)
                            postSimPos = (postSimPos @ armBis.matrix_world.inverted_safe() + armBis.matrix_world.translation)
                            postSimPos =  (postSimPos-arm.matrix_world.translation) @ arm.matrix_world
                            friction = max(friction, drbBis.pSwDrbFriction)

            cachedExtra[drb] = [preSimPos, postSimPos, parentPreSimPos, parentPostSimPos, friction]

            

        for simDrb in simDrbs:
            b, arm, armEval, windVel,gravVel,worldTPos, cachedRootP, cachedRootPLInvMat, cachedArmMWInv,  chainIdx= simDrb
            
            drb = arm.pose.bones[b.boneName]

            drbEval = armEval.pose.bones[b.boneName]  
            parent = drb.parent
            if parent is None or not parent.bIsDRB:
                continue
            
            preSimPos, postSimPos, parentPreSimPos, parentPostSimPos, friction = cachedExtra[drb]

            #bone length conservation
            bLength = (preSimPos- parentPreSimPos).length
            postSimPos = (postSimPos - parentPostSimPos).normalized() * bLength + parentPostSimPos

            #limit angle
            if parent.pSwDrbUseAmplitude:
                amplitude = parent.pSwDrbAmplitude 
                if amplitude == 0:
                    amplitude = 0.01
                postSimVec = (Vector(postSimPos) - parentPostSimPos)
                preSimVec = Vector([0,(preSimPos- parentPreSimPos).length,0])
                if parent.parent is not None and parent.parent.bIsDRB:
                    preSimVec.rotate(parent.bone.matrix_local @ parent.parent.bone.matrix_local.inverted_safe())
                    preSimVec.rotate(parent.parent.matrix)     
                                    
                else:
                    preSimVec.rotate(parent.bone.matrix_local)           
                
                if parent.pSwDrbAmplitudeType == 'C':
                    # Single amplitude (cone limit)
                    # quat = preSimVec.rotation_difference(postSimVec)
                    # extraDegrees = quat.angle * 180 / pi - parent.pSwDrbAmplitude
                    # if extraDegrees > 0:
                    #     postSimVec = postSimVec.normalized()
                    #     postSimVec.rotate(Quaternion(quat.axis, -extraDegrees / 180 * pi))
                    #     postSimPos = postSimVec * (postSimPos - parentPostSimPos).length + parentPostSimPos
                    axis , angle =  parent.bone.AxisRollFromMatrix(parent.bone.matrix, axis=parent.y_axis)
                    if parent.parent is not None and parent.parent.bIsDRB:
                        mat =  parent.bone.matrix_local @ parent.parent.bone.matrix_local.inverted_safe() @ parent.parent.matrix @ Matrix.Rotation(angle, 4, 'Y')
                    else:
                        mat = parent.bone.matrix_local
                    for _ in range(10):
                        postSimPosLocal = (-parentPostSimPos + postSimPos) @ mat                       
                        d = abs(postSimPosLocal[1])
                        a = d * tan(amplitude * pi / 180)
                        if a == 0:
                            continue
                        check = (postSimPosLocal[0]/a) ** 2 + (postSimPosLocal[2]/a)**2
                        if (check > 1) or postSimPosLocal[1] < 0: #update needed
                            if (check > 1):
                                s = 1 / check
                                postSimPosLocal[0] *= s
                                postSimPosLocal[2] *= s
                            if postSimPosLocal[1] < 0: 
                                postSimPosLocal[1] = - postSimPosLocal[1]
                            postSimPosLocal = postSimPosLocal.normalized() * (postSimPos - parentPostSimPos).length
                            postSimPos += (postSimPosLocal @ mat.inverted_safe())         
                            postSimPos = (postSimPos - parentPostSimPos).normalized() * bLength + parentPostSimPos                
                else:
                    # Dual amplitude (ellipsoid limit)     
                    mat = None
                    axis , angle =  parent.bone.AxisRollFromMatrix(parent.bone.matrix, axis=parent.y_axis)
                    if parent.parent is not None and parent.parent.bIsDRB:
                        mat =  parent.bone.matrix_local @ parent.parent.bone.matrix_local.inverted_safe() @ parent.parent.matrix @ Matrix.Rotation(angle, 4, 'Y')
                    else:
                        mat = parent.bone.matrix_local
                    for _ in range(10):    
                        postSimPosLocal = (-parentPostSimPos + postSimPos) @ mat                       
                        d = abs(postSimPosLocal[1])
                        a = d * tan(amplitude * pi / 180)
                        b = d * tan(parent.pSwDrbAmplitude2 * pi / 180)
                        check = (postSimPosLocal[0]/a) ** 2 + (postSimPosLocal[2]/b)**2
                        if (check > 1) or postSimPosLocal[1] < 0: #update needed
                            if (check > 1):
                                s = 1 / check
                                postSimPosLocal[0] *= s
                                postSimPosLocal[2] *= s
                            if postSimPosLocal[1] < 0: 
                                postSimPosLocal[1] = - postSimPosLocal[1]
                            postSimPosLocal = postSimPosLocal.normalized() * (postSimPos - parentPostSimPos).length
                            postSimPos += (postSimPosLocal @ mat.inverted_safe()) 
                            postSimPos = (postSimPos - parentPostSimPos).normalized() * bLength + parentPostSimPos     
                # Maybe later, hard width limit (both angles)
                # xVec = Vector([1,0,0])
                # zVec = Vector([0,0,1])
                # if parent.parent is not None:
                #     xVec.rotate(parent.parent.matrix)
                #     zVec.rotate(parent.parent.matrix)
                # else:
                #     xVec.rotate(parent.bone.matrix_local)
                #     zVec.rotate(parent.bone.matrix_local)
                # #first angle check
                # xproj = postSimVec.project(xVec)
                # zproj = postSimVec.project(zVec)
                # quatX = preSimVec.rotation_difference(preSimVec + xproj)
                # quatZ = preSimVec.rotation_difference(preSimVec + zproj)
                # extraDegreesX = quatX.angle * 180 / pi - parent.pSwDrbAmplitude
                # extraDegreesZ = quatZ.angle * 180 / pi - parent.pSwDrbAmplitude2
                # postSimVec = postSimVec.normalized()
                # if extraDegreesX > 0:                        
                #     postSimVec.rotate(Quaternion(quatX.axis, -extraDegreesX / 180 * pi))
                # if extraDegreesZ > 0:                        
                #     postSimVec.rotate(Quaternion(quatZ.axis, -extraDegreesZ / 180 * pi))
                # postSimPos = postSimVec * (postSimPos - parentPostSimPos).length + parentPostSimPos        


            drb.soSwUpdatedPos = postSimPos
            #velocity update
            drb.soSwPrevVel = (postSimPos - preSimPos)/deltaTime
            drb.soSwPrevFriction =  friction
            
        for armt in armToUpdate:
            armt.data.soArmPrevPos = armt.matrix_world.translation
        #update parent rotation to reflect changes accordingly
        for i in range(len(drbList.boneChainCollection)):
            pTrans = None
            drbTrans = None
            pMat = None
            # arm = bpy.data.objects[drbList.boneChainCollection[i].armName]
            if not arm.bSwSimulate:
                continue
            for b in drbList.boneChainCollection[i].boneCollection:
                drb = arm.pose.bones[b.boneName]
                parent = drb.parent
                if parent is None or not parent.bIsDRB:
                    continue
                #Initstep
                if pTrans is None:
                    pTrans = parent.matrix.translation
                    drbTrans = drb.matrix.translation
                    pMat = parent.matrix            
                
                v = Vector(drb.soSwUpdatedPos) - pTrans
                bv = drbTrans - pTrans # implicit connection assumption
                rd = bv.rotation_difference(v)

                M = (
                    Matrix.Translation(pTrans) @
                    rd.to_matrix().to_4x4() @
                    Matrix.Translation(-pTrans)
                    )
                    
                parent.matrix = M @ parent.matrix
                pMat = getUpdatedPose(drb,  M @ pMat)
                pTrans = pMat.translation
                if len(drb.children):
                    childMat = getUpdatedPose(drb.children[0], pMat)
                    drbTrans = childMat.translation
                parent.lock_scale = [False for _ in range(3)]
                parent.scale = [1,1,1]
                parent.lock_scale = [True for _ in range(3)]
                if parent.pSwDrbLockRoll:
                    parent.rotation_mode = "YXZ"
                    parent.rotation_euler[1] = 0
                    parent.rotation_mode = "QUATERNION"
                # if scene.bSwIsBaking and scene.bSwDropBake:
                #     mat = Matrix(parent.matrix )
                #     scene["BoneKFMap"][arm.name + "_" + parent.name][str(scene.frame_current)] = mat