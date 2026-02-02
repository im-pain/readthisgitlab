import bpy

from .SwingOperator import *
from .SwingProp import *

##############################
# DRB
##############################

class SW_UL_DRB_MAIN(bpy.types.UIList):    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.row().prop(item, "name", text="", emboss=False, translate=False, icon="LINK_BLEND")
        row = layout.row()
        row.split(factor=0.0)
        icon = 'HIDE_ON' if item.bHidden else 'HIDE_OFF'
        row.prop(item,'bHidden',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        icon = 'FILE_REFRESH' if item.bReset else 'PANEL_CLOSE'
        row.prop(item,'bReset',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        icon = 'CON_TRACKTO' if item.bExtraChild else 'PANEL_CLOSE'
        row.prop(item,'bExtraChild',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
            
    def invoke(self, context, event):
        pass   

class SW_UL_DRB_SUB(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.6)        
        # split.prop(item, "boneName", text="", emboss=False, translate=False, icon="BONE_DATA")
        # prop_search(apb, "pSwSrbParentName", context.object.pose, "bones", text="Parent") 
        split.enabled = False  
        # if item.boneName not in context.object.pose.bones:
        #     split.enabled = True
        # if item.boneName in context.object.pose.bones and not context.object.pose.bones[item.boneName].bIsDRB:
        #     split.enabled = True
        split.prop_search(item, "boneName", context.object.pose, "bones", text="",  icon="BONE_DATA")
        split.label(text="{0:.2f}".format(item.chainPercentage))
            
    def invoke(self, context, event):
        pass

class SW_PT_DRBLIST(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Bone chains"
    bl_category = "Swingy Bone"

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object is not None and bpy.context.active_object.type == "ARMATURE"

    def draw(self, context):
        layout = self.layout
        
        scene = context.scene
        arm = bpy.context.active_object
        armData = arm.data
        drbList = arm.data.drbList        
        minRows = 10
        drawFac = 0
        boneChain = None
        
        row = layout.row()
        row.operator(SW_OT_DRBRescanAllChainsOpr.bl_idname, text="Refresh chains", icon="GROUP_BONE") 

        if len(drbList.boneChainCollection) > 0 and drbList.activeBoneChainIndex != -1:
            row = layout.row()
            row.prop(arm,"bSwSimulate", text="Disable Simulation" if arm.bSwSimulate else "Enable Simulation", icon="CANCEL" if arm.bSwSimulate else "PHYSICS")            
            row = layout.row()
            row.prop(arm,"bSwDisplayShape", text="Display Collision Volumes" if arm.bSwDisplayShape else "Display Bones", icon="SPHERE" if arm.bSwDisplayShape else "BONE_DATA", emboss=True)
            row = layout.row()
            row.prop(arm,"bSwToggleSelect", text="Disable Selection" if arm.bSwToggleSelect else "Enable Selection", icon="RESTRICT_SELECT_ON" if arm.bSwToggleSelect else "RESTRICT_SELECT_OFF")


        row = layout.row()
        split = layout.split(factor=drawFac)
        
        split.template_list(
            listtype_name = "SW_UL_DRB_MAIN", 
            list_id  = "", 
            dataptr = drbList, 
            propname = "boneChainCollection", 
            active_dataptr = drbList, 
            active_propname = "activeBoneChainIndex",
            rows = minRows
            )   
        
        if len(drbList.boneChainCollection) > 0 and drbList.activeBoneChainIndex != -1:            
            drawFac = 0.5
            boneChain = drbList.boneChainCollection[drbList.activeBoneChainIndex]                
            split.template_list(
                listtype_name = "SW_UL_DRB_SUB",
                list_id = "", 
                dataptr = boneChain,
                propname = "boneCollection",
                active_dataptr = boneChain,
                active_propname = "activeBoneIndex",
                rows = minRows
                )

        OperatorSpecs = [
            (SW_OT_DRBAddOpr,"Create Bone Chain","ADD"),
            (SW_OT_DRBSelectAllOpr, "Select All", "CHECKMARK"),
            (SW_OT_DRBResetChainOpr, "Reset Bone Chain", "FILE_REFRESH"),
            (SWT_OT_Bake, "Bake All", "DECORATE_KEYFRAME"),
            (SW_OT_DRBDelOpr, "Delete Bone Chain", "REMOVE"),
            (SW_OT_DRBHideAllOpr, "Hide/Unhide All", "HIDE_OFF"),
            (SW_OT_DRBResetAllChainsOpr, "Reset All Bone Chains","RECOVER_LAST"),
            (SW_OT_DRBClearOpr,"Clear All","CANCEL"),
        ]
        row = layout.row()
        row.prop(scene,"bSwMultiSelectChain", text="Multi selection chain mode")
        row.prop(scene,"bSwForceRendering", text="Force Animation Rendering")
        row.prop(scene,"bSwClearOnBake", text="Clear After Bake")
        row.prop(scene,"bSwForceDropBake", text="Force Special Bake")  

        for i, spec in enumerate(OperatorSpecs):
            if not i%4:
                row = layout.row()
            row.operator(spec[0].bl_idname, text=spec[1], icon=spec[2])               

        apb = context.active_pose_bone
        if apb is not None:
            select = apb.bone.select if bpy.app.version[0] < 5 else apb.select
        if apb is not None and select and context.mode == "POSE" and apb.bIsDRB:
            layout.use_property_split = False
            row = layout.row(align=True)
            row.label(text="Bone Chains Colors")
            drbColors = ["regular", "select","active"]
            for drbColor in drbColors:
                row.prop(scene.drbColors,drbColor, text="")
            row.operator(SW_OT_SceneResetDRBColorsOpr.bl_idname, icon='FILE_REFRESH', text='')            
            layout.use_property_split = True
            col = layout.column()  
            names = ",".join([n.name for n in context.selected_pose_bones] )
            col.label(text="Selected : " +names)
            specialPList = ["pSwDrbCollLayer","pSwDrbShowAmplitude","pSwDrbAmplitude", "pSwDrbAmplitudeType","pSwDrbAmplitude2","pSwDrbLockRoll", "pSwDrbCollIntra" ]
            curvePList = ["pSwDrbDamping", "pSwDrbDrag", "pSwDrbStiffness", "pSwDrbWindFactor"]
            allKfPList = curvePList + ["pSwDrbGravityFactor"]
            for (propName, _) in SwPoseBoneProps:
                if propName.startswith("pSwDrb"):
                    if propName in specialPList:
                        continue
                    if propName == "pSwDrbUseAmplitude":
                        # Place lock roll just before
                        col = layout.column()
                        row = col.row()
                        row.prop(apb,"pSwDrbLockRoll", text="Lock bone roll")
                        
                        row = col.row()
                        row.prop(apb, propName)
                        if apb.pSwDrbUseAmplitude:
                            row.prop(apb, "pSwDrbShowAmplitude")
                            row = col.row()
                            row.prop(apb, "pSwDrbAmplitudeType")
                            row = col.row()
                            row.prop(apb, "pSwDrbAmplitude")
                            if apb.pSwDrbAmplitudeType == 'E':
                                row = col.row()
                                row.prop(apb, "pSwDrbAmplitude2")
                                row.operator(SW_OT_DRBResetAmp2Opr.bl_idname, icon='FILE_REFRESH', text='')                                           
                    else:
                        row = col.row()
                        row.prop(apb, propName)
                        if propName in curvePList:
                            if bpy.app.version[0] < 5:
                                row.prop(apb, "cu" + propName, icon="SMOOTHCURVE",text="")
                            else:
                                row.prop(apb, "cu" + propName, icon="SMOOTHCURVE",text="", placeholder="Parameter Curve")                                
                        if propName in allKfPList:
                            op = row.operator(SWT_OT_KFAllProps.bl_idname, icon='KEY_HLT', text='')
                            op.propName = propName

            if(apb.pSwDrbShowAmplitude):                
                row = col.row(align=True)
                row.prop(scene.ampPrimColors,"regular", text="Amplitude color")
                row.operator(SW_OT_SceneResetAMPPRIMColorsOpr.bl_idname, icon='FILE_REFRESH', text='')
          
            col = layout.column()
            row = col.row()
            row.prop(armData,"bUseWind", text="Use Wind")
            if armData.bUseWind:
                row.prop(arm, "bShowWind")
                col.prop(arm,"swWind", text="Wind")
                col.prop(arm, "swWindMean")
                col.prop(arm, "swWindStd")
                for coord in ["X","Y","Z"]:
                    if bpy.app.version[0] < 5:
                        col.prop(arm,"cupSwWind"+coord, text="Wind "+coord+" curve", icon="FORCE_WIND")
                    else:
                        col.prop(arm,"cupSwWind"+coord, text="Wind "+coord+" curve", icon="FORCE_WIND", placeholder="Wind Curve")
            if armData.bUseWind and arm.bShowWind:
                col.prop(arm,"swWindArrowScale", text="Wind arrow scale")
                row = col.row(align=True)
                row.prop(arm.windColor,"regular", text="Wind Color")
                row.operator(SW_OT_ArmResetWindColorOpr.bl_idname, icon='FILE_REFRESH', text='')          
            layout.use_property_split = False
            col = layout.column()  
            col.prop(apb, "pSwDrbCollIntra")
            col.prop(apb, "pSwDrbCollLayer")            
            layout.use_property_split = False
            row = layout.row(heading="Sphere Colliders Axes", align=True)
            # row.prop(apb, "bHasColliderPosAxis", toggle=True,  icon="ADD", icon_only=True)
            # row.prop(apb, "bHasColliderNegAxis", toggle=True,  icon="REMOVE", icon_only=True)
            row.prop(apb, "bHasColliderXAxis", text="X", toggle=True)
            op = row.operator(SWT_OT_KFAllProps.bl_idname, icon='KEY_HLT', text='')
            op.propName = "bHasColliderXAxis"
            row.prop(apb, "bHasColliderZAxis", text="Z", toggle=True)
            op = row.operator(SWT_OT_KFAllProps.bl_idname, icon='KEY_HLT', text='')
            op.propName = "bHasColliderXAxis"

##############################
# SRB
##############################

class SW_UL_SRB_MAIN(bpy.types.UIList):    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.row().prop(item, "colliderName", text="", emboss=False, translate=False, icon='MESH_UVSPHERE' if item.type == 'S' else 'MESH_CYLINDER')
            
    def invoke(self, context, event):
        pass   

class SW_PT_SRBLIST(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Colliders"
    bl_category = "Swingy Bone"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object is not None and bpy.context.active_object.type == "ARMATURE"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        arm = bpy.context.active_object
        srbList = arm.data.srbList
        
        minRows = 6
        drawFac = 0

        row = layout.row()
        row.operator(SW_OT_SRBRescanAllOpr.bl_idname, text="Refresh colliders", icon="GROUP_BONE") 
        
        row = layout.row()
        split = layout.split(factor=drawFac)
        
        split.template_list(
            listtype_name = "SW_UL_SRB_MAIN", 
            list_id  = "", 
            dataptr = srbList, 
            propname = "colliderCollection", 
            active_dataptr = srbList, 
            active_propname = "activeColliderIndex",
            rows = minRows
            )

        OperatorSpecs = [
            (SW_OT_SRBAddOpr,"Add Collider","ADD"),
            (SW_OT_SRBDelOpr,"Delete Collider", "REMOVE"),
            (SW_OT_SRBSelectAllOpr, "Select All", "CHECKMARK"),
            (SW_OT_SRBHideAllOpr, "Hide/Unhide All","HIDE_OFF"),
            (SW_OT_SRBClearOpr,"Clear All", "CANCEL"),
        ]
        row = layout.row()
        for i, spec in enumerate(OperatorSpecs):
            if i==2:
                row = layout.row()
            row.operator(spec[0].bl_idname, text=spec[1], icon=spec[2])
        
        apb = context.active_pose_bone
        if apb is not None:
            select = apb.bone.select if bpy.app.version[0] < 5 else apb.select
        if apb is not None and select and context.mode == "POSE" and apb.bIsSRB:
            row = layout.row(align=True) 
            row.label(text="Colliders Colors")
            srbColors = ["regular", "select","active"]
            for srbColor in srbColors:
                row.prop(scene.srbColors,srbColor, text="")
            row.operator(SW_OT_SceneResetSRBColorsOpr.bl_idname, icon='FILE_REFRESH', text='')
            layout.use_property_split = True
            col = layout.column()            
            col.prop_search(apb, "pSwSrbParentName", context.object.pose, "bones", text="Parent")            
            # col.prop(bpy.data.armatures[arm.name].bones[apb.name], "parent")            
            col.prop(apb, "pSwSrbRadius")
            if apb.custom_shape == bpy.data.objects.get("SW_Shape_Cylinder"):
                col.prop(apb, "pSwSrbDepth")
            col.prop(apb, "pSwSrbFriction")
            layout.use_property_split = False
            col = layout.column()    
            col.prop(apb, "pSwSrbCollLayers")

##############################
# Links
##############################

class SW_UL_LINK_MAIN(bpy.types.UIList):    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.row().prop(item, "name", text="", emboss=False, translate=False, icon="CONSTRAINT")
        row = layout.row()
        row.split(factor=0.0)
        icon = 'HIDE_ON' if item.bHidden else 'HIDE_OFF'
        row.prop(item,'bHidden',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        icon = 'PLAY' if not item.bIsActive else 'SNAP_FACE'
        row.prop(item,'bIsActive',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        # icon = 'LOOP_BACK' if item.bSolveBefore else 'PANEL_CLOSE'
        # row.prop(item,'bSolveBefore',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        # icon = 'LOOP_FORWARDS' if item.bSolveAfter else 'PANEL_CLOSE'
        # row.prop(item,'bSolveAfter',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
            
    def invoke(self, context, event):
        pass   

class SW_UL_LINK_SUB(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.6)
        split.enabled = False
        split.prop(item, "boneName", text="", emboss=False, translate=False, icon="BONE_DATA")
            
    def invoke(self, context, event):
        pass

class SW_PT_LINKLIST(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Bone Links (Beta)"
    bl_category = "Swingy Bone"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object is not None and bpy.context.active_object.type == "ARMATURE"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        arm = bpy.context.active_object
        linkList = arm.data.swLinkList        
        minRows = 10
        drawFac = 0

        #Make sure we have a draw handler if relevant when opening a new file. Is there a better, non invasive way to do this?
        if len(linkList.linkCollection) and gSwDrawInstance.handle is None:
            gSwDrawInstance.set(bpy.context)
        
        row = layout.row()
        split = layout.split(factor=drawFac)
        
        split.template_list(
            listtype_name = "SW_UL_LINK_MAIN", 
            list_id  = "", 
            dataptr = linkList, 
            propname = "linkCollection", 
            active_dataptr = linkList, 
            active_propname = "activeLinkIndex",
            rows = minRows
            )   
        
        if len(linkList.linkCollection) > 0 and linkList.activeLinkIndex != -1:            
            drawFac = 0.5
            link = linkList.linkCollection[linkList.activeLinkIndex]                
            split.template_list(
                listtype_name = "SW_UL_LINK_SUB",
                list_id = "", 
                dataptr = link,
                propname = "linkedBones",
                active_dataptr = link,
                active_propname = "activeBoneIndex",
                rows = minRows
                )
        row = layout.row()
        row.operator(SW_OT_LinkAddOpr.bl_idname, text="Add Link", icon="ADD")
        row.operator(SW_OT_LinkAddByChainOpr.bl_idname, text="Add Link By Chain", icon="ADD")
        row.operator(SW_OT_LinkDelOpr.bl_idname, text="Delete Link", icon="REMOVE")
        row = layout.row()
        row.operator(SW_OT_LinkResetOpr.bl_idname, text="Reset Links", icon="FILE_REFRESH") 
        row.operator(SW_OT_LinkHideAllOpr.bl_idname, text="Hide/Unhide All", icon="HIDE_OFF")  
        row.operator(SW_OT_LinkClearOpr.bl_idname, text="Clear All", icon="CANCEL")
        layout.use_property_split = True
        col = layout.column()
        row = col.row()
        row.prop(scene, "swLinkLineWidth", text="Line width")               
        col = layout.column()
        row = col.row()
        row = col.row(align=True)
        row.prop(scene.swLinkColor,"regular", text="Active Link color")
        row.operator(SW_OT_SceneResetLinkColorsOpr.bl_idname, icon='FILE_REFRESH', text='')
        row = col.row(align=True)
        row.prop(scene.swLinkColor,"maxL", text="Overshoot Link color")
        row.operator(SW_OT_SceneResetMaxLLinkColorsOpr.bl_idname, icon='FILE_REFRESH', text='')
        row = col.row(align=True)
        row.prop(scene.swLinkColor,"inactive", text="Inactive Link color")
        row.operator(SW_OT_SceneResetInactiveLinkColorsOpr.bl_idname, icon='FILE_REFRESH', text='')
        layout.use_property_split = True
        row = layout.row()
        row.label(text="Resources:")
        row = layout.row()
        op = row.operator(
            'wm.url_open',
            text='Wiki page',
            icon='URL'
            )
        op.url = 'https://swingy-bone-physics.github.io/wiki/blink/basics/'
        op = row.operator(
            'wm.url_open',
            text='Video tutorial',
            icon='URL'
            )
        op.url = 'https://youtu.be/UI_DXDz4sEY'

##############################
# Curves
##############################

class SW_UL_CURVE_MAIN(bpy.types.UIList):    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.row().prop(item.brush, "name", text="", emboss=False, translate=False, icon='FORCE_WIND' if item.brush.cupSwType == 'W' else 'MOD_HUE_SATURATION')
            
    def invoke(self, context, event):
        pass   

class SW_PT_CURVELIST(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Curves"
    bl_category = "Swingy Bone"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object is not None and bpy.context.active_object.type == "ARMATURE"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        arm = context.object
        curveList = arm.data.curveList
        
        minRows = 6
        drawFac = 0
        
        row = layout.row()
        split = layout.split(factor=drawFac)
        
        split.template_list(
            listtype_name = "SW_UL_CURVE_MAIN", 
            list_id  = "", 
            dataptr = curveList, 
            propname = "curveCollection", 
            active_dataptr = arm, 
            active_propname = "activeCurveIndex",
            rows = minRows
            )
        
        row = layout.row()    
        row.operator(SW_OT_CURVEAddOpr.bl_idname, text="Add Curve", icon="ADD")
        row.operator(SW_OT_CURVEDelOpr.bl_idname, text="Delete Curve", icon="REMOVE")
        row.operator(SW_OT_CURVEClearOpr.bl_idname, text="Clear All", icon="CANCEL")

        if len(curveList.curveCollection) > 0 and arm.activeCurveIndex != -1:
            layout.use_property_split = True         
            # curve = curveList.curveCollection[curveList.activeCurveIndex]
            curve = curveList.curveCollection[arm.activeCurveIndex]
            if bpy.app.version[0] < 5:
                layout.template_curve_mapping(curve.brush, "curve")            
                row = layout.row(align=True)
                row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
                row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
                row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
                row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
                row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
                row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'
            else:
                layout.template_curve_mapping(curve.brush, "curve_distance_falloff", brush=True,
                                          use_negative_slope=True, show_presets=True)
            if curve.brush.cupSwType == "W":
                row = layout.row()
                col = row.column()
                col.prop(curve.brush, "cupSwAmplitude")
                col.prop(curve.brush, "cupSwPeriod")

##############################
# Misc
##############################

class SW_PT_MISC_MAIN(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Misc"
    bl_category = "Swingy Bone"   

    def draw(self, context):        
        layout = self.layout
        scene = context.scene        
        row = layout.row()
        row.operator(SWT_OT_LinkAppend.bl_idname,text="Link data",icon="BLENDER")
        row = layout.row()
        row.prop(scene,"swParamPath", text="Parameter path")
        row = layout.row()
        row.operator(SWT_OT_LoadParameters.bl_idname, text="Load parameters")
        row.operator(SWT_OT_SaveParameters.bl_idname, text="Save parameters")

        
        

        