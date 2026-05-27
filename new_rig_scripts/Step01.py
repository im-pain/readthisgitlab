import bpy

asset_kk = r"C:\Users\Julian\AppData\Roaming\Blender Foundation\Blender\5.0\extensions\user_default\sklx_studio\assets\KK_Template_Shader.blend"

Bone_Shape = "BONE_Root"
if Bone_Shape not in bpy.data.objects:
    bpy.ops.wm.append(directory=str(asset_kk / 'Object'), filename=Template, link=False)
else:
    print("Object already imported!")
