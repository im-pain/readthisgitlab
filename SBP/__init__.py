bl_info = {
    "name": "Swingy Bone Physics",
    "version": (1, 9, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Swingy Bone Panel",
    "description": "An easy-to-use, artist friendly bone chain physics solver.",
    "warning": "",
    "category": "Animation",
    "doc_url": "https://swingy-bone-physics.github.io/wiki/",
}

import bpy

from .SwingOperator import *
from .SwingProp import *
from .SwingSolver import *
from .SwingUI import *

SwUIClasses = (
    SW_PT_DRBLIST,
    SW_UL_DRB_MAIN,
    SW_UL_DRB_SUB,      

    SW_PT_SRBLIST,
    SW_UL_SRB_MAIN,

    SW_PT_LINKLIST,
    SW_UL_LINK_MAIN,
    SW_UL_LINK_SUB,  

    SW_PT_CURVELIST,
    SW_UL_CURVE_MAIN, 

    # SW_PT_MISC_MAIN,
)

SwOprClasses = (
    SW_OT_DRBAddOpr,
    SW_OT_DRBDelOpr,
    SW_OT_DRBClearOpr,
    SW_OT_DRBSelectAllOpr,
    SW_OT_DRBHideAllOpr,
    SW_OT_DRBRescanAllChainsOpr,

    SW_OT_SRBAddOpr,
    SW_OT_SRBDelOpr,
    SW_OT_SRBClearOpr,
    SW_OT_SRBSelectAllOpr,
    SW_OT_SRBHideAllOpr,
    SW_OT_SRBRescanAllOpr,

    SW_OT_CURVEAddOpr,
    SW_OT_CURVEDelOpr,
    SW_OT_CURVEClearOpr,

    SW_OT_LinkAddOpr,
    SW_OT_LinkAddByChainOpr,
    SW_OT_LinkDelOpr,
    SW_OT_LinkClearOpr,
    SW_OT_LinkResetOpr,
    SW_OT_LinkHideAllOpr,

    SW_OT_SceneResetDRBColorsOpr,
    SW_OT_SceneResetLinkColorsOpr,
    SW_OT_SceneResetInactiveLinkColorsOpr,
    SW_OT_SceneResetMaxLLinkColorsOpr,
    SW_OT_SceneResetSRBColorsOpr,
    SW_OT_SceneResetAMPPRIMColorsOpr,
    SW_OT_DRBResetAmp2Opr,
    SWT_OT_Bake,
    SWT_OT_LinkAppend,
    SWT_OT_KFAllProps,
    SWT_OT_LoadParameters,
    SWT_OT_SaveParameters,


    SW_OT_ArmResetWindColorOpr,
    SW_OT_DRBResetChainOpr,
    SW_OT_DRBResetAllChainsOpr,
)

SwSceneClasses = (
    SW_DRBCOLORS_SceneProps,
    SW_LINKCOLOR_SceneProps,
    SW_SRBCOLORS_SceneProps,
    SW_AMPPRIMCOLORS_SceneProps,
    SW_WINDCOLORS_ArmProps,

    SW_DRBLIST_BoneProps, 
    SW_DRBLIST_BoneChainProps, 
    SW_DRBLIST_ArmProps, 

    SW_SRBLIST_ColliderProps, 
    SW_SRBLIST_ArmProps,

    SW_CURVELIST_CurveProps,
    SW_CURVELIST_ArmProps,    

    SW_AMPPRIMLIST_AMPPRIMProps,
    SW_AMPPRIMLIST_SceneProps,


    SW_LINKLIST_BoneLinkedProps,
    SW_LINKLIST_LinkProps,
    SW_LINKLIST_ArmProps,


)

klassLists = [SwUIClasses, SwOprClasses, SwSceneClasses]

propLists = [
    (bpy.types.PoseBone, SwPoseBoneProps),
    (bpy.types.Armature, SwArmatureProps),
    (bpy.types.Scene, SwSceneProps),
    (bpy.types.Brush, SwBrushProps),
    (bpy.types.Object, SwObjectProps)
]

def register():
    for klasses in klassLists:
        for klass in klasses:
            bpy.utils.register_class(klass)
    for bType, propList in propLists:
        for (propName, propValue) in propList:
            setattr(bType, propName, propValue)
    bpy.app.handlers.frame_change_post.append(SWTick)
    bpy.app.handlers.render_pre.append(SWBakeTrue)
    bpy.app.handlers.render_post.append(SWBakeFalse)
    bpy.app.handlers.render_complete.append(SWBakeFalse)
    bpy.app.handlers.render_cancel.append(SWBakeFalse)

def unregister():
    for klasses in klassLists:
        for klass in klasses:
            bpy.utils.unregister_class(klass)
    for bType, propList in propLists:
        for (propName, _) in propList:
            delattr(bType, propName)
    bpy.app.handlers.frame_change_post.remove(SWTick)
    bpy.app.handlers.render_pre.remove(SWBakeTrue)
    bpy.app.handlers.render_post.remove(SWBakeFalse)
    bpy.app.handlers.render_complete.remove(SWBakeFalse)
    bpy.app.handlers.render_cancel.remove(SWBakeFalse)
    

if __name__ == "__main__":
    register()
    