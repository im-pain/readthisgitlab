# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "my supporter addon",
    "author" : "mal", 
    "description" : "",
    "blender" : (4, 2, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "3D View" 
}


import bpy
import bpy.utils.previews
import sys
import os
import requests
import json
import webbrowser
from bpy.app.handlers import persistent
import bpy  # módulo de Blender




def string_to_type(value, to_type, default):
    try:
        value = to_type(value)
    except:
        value = default
    return value


addon_keymaps = {}
_icons = None
supportersui = {'sna_nombre': [], 'sna_imagen': [], 'sna_discord': [], 'sna_nota': [], 'sna_tier': [], 'sna_url': [], 'sna_tiers_optimized': [], 'sna_data_posincats': [], 'sna_imagen_paths': [], 'sna_imagen2download': [], }


def read_json_skd(*args):
    Argsz = []
    Data = []
    package_info = None
    # Check if we need to fetch from a URL or local file
    if args[0] is True:
        if args[1]:
            file_url = args[1]
            response = requests.get(file_url)
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON content
                package_info = response.json()
    else:
        file_url = args[1]
        if os.path.exists(file_url):
            with open(file_url, "r") as file:
                package_info = json.load(file)
    if package_info is None:
        return ["Error: Unable to load JSON data"], []
    # Handle dynamic fields from the JSON
    if len(args) > 2:
        for i, arg in enumerate(args[2:]):
            try:
                # Handle any name with ':' for nested field extraction
                if ":" in arg:
                    field_path = arg.split(":")
                    value = package_info
                    for key in field_path:
                        if isinstance(value, dict):
                            value = value.get(key, "Not in file")
                        elif isinstance(value, list):
                            value = [item.get(key, "Not in file") if isinstance(item, dict) else "Invalid structure" for item in value]
                        else:
                            value = "Invalid structure"
                            break
                    Argsz.append(arg)
                    Data.append(value)
                else:
                    if isinstance(package_info, list):
                        value = [item.get(arg, "Not in file") if isinstance(item, dict) else "Invalid structure" for item in package_info]
                    else:
                        value = package_info.get(arg, "Not in file")
                    Argsz.append(arg)
                    Data.append(value)
            except Exception as e:
                Argsz.append(arg)
                Data.append(f"Error: {e}")
    return Argsz, Data


def find_variable_in_list(my_list, my_checker):
    # Initialize variables to store results
    found_matches = []
    num_matches = 0
    # Iterate through the list and check for matches
    for i, item in enumerate(my_list):
        if item == my_checker:
            found_matches.append(i)
            num_matches += 1
    # Return the results
    return num_matches > 0, found_matches, num_matches


def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id


class SNA_PT_SKLX_CREATOR_69C58(bpy.types.Panel):
    bl_label = 'SKLX CREATOR'
    bl_idname = 'SNA_PT_SKLX_CREATOR_69C58'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'SKLX'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout


pfp_cache = None
pfp_cache = r"C:\Users\mapsh\OneDrive\Documentos\Blender\SKLX-VERSE\pfp_cache"
json_read_skd_2B136 = read_json_skd(False , os.path.join(os.path.dirname(__file__), 'assets', 'members-sklx.json') , 'nombre' , 'imagen' , 'discord' , 'nota' , 'tier' , 'url')
for i_EBC59 in range(len(json_read_skd_2B136[1])):
    if str(i_EBC59) == "0":
        supportersui['sna_nombre'] = json_read_skd_2B136[1][i_EBC59]
    elif str(i_EBC59) == "1":
        supportersui['sna_imagen'] = json_read_skd_2B136[1][i_EBC59]
    elif str(i_EBC59) == "2":
        supportersui['sna_discord'] = json_read_skd_2B136[1][i_EBC59]
    elif str(i_EBC59) == "3":
        supportersui['sna_nota'] = json_read_skd_2B136[1][i_EBC59]
    elif str(i_EBC59) == "4":
        supportersui['sna_tier'] = json_read_skd_2B136[1][i_EBC59]
    elif str(i_EBC59) == "5":
        supportersui['sna_url'] = json_read_skd_2B136[1][i_EBC59]
    else:
        pass
    for i_BBFFF in range(len(supportersui['sna_tier'])):
        if supportersui['sna_tier'][i_BBFFF] in supportersui['sna_tiers_optimized']:
            pass
        else:
            supportersui['sna_tiers_optimized'].append(supportersui['sna_tier'][i_BBFFF])
            supportersui['sna_data_posincats'].append(find_variable_in_list(supportersui['sna_tier'],supportersui['sna_tier'][i_BBFFF])[1])


class SNA_PT_PATREON_SUPPORTERS_7F269(bpy.types.Panel):
    bl_label = 'PATREON SUPPORTERS'
    bl_idname = 'SNA_PT_PATREON_SUPPORTERS_7F269'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'SKLX'
    bl_order = 2
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        col_CEDA9 = layout.column(heading='', align=True)
        col_CEDA9.alert = False
        col_CEDA9.enabled = True
        col_CEDA9.active = True
        col_CEDA9.use_property_split = False
        col_CEDA9.use_property_decorate = False
        col_CEDA9.scale_x = 1.0
        col_CEDA9.scale_y = 1.0
        col_CEDA9.alignment = 'Expand'.upper()
        col_CEDA9.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_C9C8E = col_CEDA9.row(heading='', align=True)
        row_C9C8E.alert = False
        row_C9C8E.enabled = True
        row_C9C8E.active = True
        row_C9C8E.use_property_split = False
        row_C9C8E.use_property_decorate = False
        row_C9C8E.scale_x = 1.0
        row_C9C8E.scale_y = 1.0
        row_C9C8E.alignment = 'Expand'.upper()
        row_C9C8E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        box_4EE14 = row_C9C8E.box()
        box_4EE14.alert = False
        box_4EE14.enabled = True
        box_4EE14.active = True
        box_4EE14.use_property_split = False
        box_4EE14.use_property_decorate = False
        box_4EE14.alignment = 'Expand'.upper()
        box_4EE14.scale_x = 1.0
        box_4EE14.scale_y = 1.0
        if not True: box_4EE14.operator_context = "EXEC_DEFAULT"
        box_4EE14.label(text='Support waifus!', icon_value=0)
        row_5C897 = row_C9C8E.row(heading='', align=False)
        row_5C897.alert = True
        row_5C897.enabled = True
        row_5C897.active = True
        row_5C897.use_property_split = False
        row_5C897.use_property_decorate = False
        row_5C897.scale_x = 1.0
        row_5C897.scale_y = 1.5
        row_5C897.alignment = 'Expand'.upper()
        row_5C897.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_5C897.operator('sn.dummy_button_operator', text='BECOME A PATREON', icon_value=0, emboss=True, depress=False)
        if (supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][5][0], int, 0)] != 'NOMBREDEREPUESTO'):
            box_BEF2B = col_CEDA9.box()
            box_BEF2B.alert = False
            box_BEF2B.enabled = True
            box_BEF2B.active = True
            box_BEF2B.use_property_split = False
            box_BEF2B.use_property_decorate = False
            box_BEF2B.alignment = 'Expand'.upper()
            box_BEF2B.scale_x = 1.0
            box_BEF2B.scale_y = 1.0
            if not True: box_BEF2B.operator_context = "EXEC_DEFAULT"
            grid_2B4A9 = box_BEF2B.grid_flow(columns=3, row_major=True, even_columns=False, even_rows=False, align=True)
            grid_2B4A9.enabled = True
            grid_2B4A9.active = True
            grid_2B4A9.use_property_split = False
            grid_2B4A9.use_property_decorate = False
            grid_2B4A9.alignment = 'Expand'.upper()
            grid_2B4A9.scale_x = 1.0
            grid_2B4A9.scale_y = 1.0
            if not True: grid_2B4A9.operator_context = "EXEC_DEFAULT"
            for i_35826 in range(len(supportersui['sna_data_posincats'][5])-1,-1,-1):
                row_6A721 = grid_2B4A9.row(heading='', align=False)
                row_6A721.alert = True
                row_6A721.enabled = True
                row_6A721.active = False
                row_6A721.use_property_split = False
                row_6A721.use_property_decorate = False
                row_6A721.scale_x = 1.0
                row_6A721.scale_y = 1.5
                row_6A721.alignment = 'Expand'.upper()
                row_6A721.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                op = row_6A721.operator('sna.sex_op_792ac', text=supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][5][i_35826], int, 0)], icon_value=supportersui['sna_imagen_paths'][string_to_type(supportersui['sna_data_posincats'][5][i_35826], int, 0)], emboss=True, depress=False)
                op.sna_sex_description = supportersui['sna_nota'][string_to_type(supportersui['sna_data_posincats'][5][i_35826], int, 0)]
                op.sna_sex_url = supportersui['sna_url'][string_to_type(supportersui['sna_data_posincats'][5][i_35826], int, 0)]
        if (supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][4][0], int, 0)] != 'NOMBREDEREPUESTO'):
            box_B2413 = col_CEDA9.box()
            box_B2413.alert = False
            box_B2413.enabled = True
            box_B2413.active = True
            box_B2413.use_property_split = False
            box_B2413.use_property_decorate = False
            box_B2413.alignment = 'Expand'.upper()
            box_B2413.scale_x = 1.0
            box_B2413.scale_y = 1.0
            if not True: box_B2413.operator_context = "EXEC_DEFAULT"
            grid_0120D = box_B2413.grid_flow(columns=3, row_major=True, even_columns=False, even_rows=False, align=True)
            grid_0120D.enabled = True
            grid_0120D.active = True
            grid_0120D.use_property_split = False
            grid_0120D.use_property_decorate = False
            grid_0120D.alignment = 'Expand'.upper()
            grid_0120D.scale_x = 1.0
            grid_0120D.scale_y = 1.0
            if not True: grid_0120D.operator_context = "EXEC_DEFAULT"
            for i_15DE9 in range(len(supportersui['sna_data_posincats'][4])-1,-1,-1):
                row_FD30B = grid_0120D.row(heading='', align=False)
                row_FD30B.alert = True
                row_FD30B.enabled = True
                row_FD30B.active = True
                row_FD30B.use_property_split = False
                row_FD30B.use_property_decorate = False
                row_FD30B.scale_x = 1.0
                row_FD30B.scale_y = 1.0
                row_FD30B.alignment = 'Expand'.upper()
                row_FD30B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                op = row_FD30B.operator('sna.horny_op_4473b', text=supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][4][i_15DE9], int, 0)], icon_value=supportersui['sna_imagen_paths'][string_to_type(supportersui['sna_data_posincats'][4][i_15DE9], int, 0)], emboss=True, depress=False)
                op.sna_horny_description = supportersui['sna_nota'][string_to_type(supportersui['sna_data_posincats'][4][i_15DE9], int, 0)]
                op.sna_horny_url = supportersui['sna_url'][string_to_type(supportersui['sna_data_posincats'][4][i_15DE9], int, 0)]
        if (supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][3][0], int, 0)] != 'NOMBREDEREPUESTO'):
            box_8EF5C = col_CEDA9.box()
            box_8EF5C.alert = False
            box_8EF5C.enabled = True
            box_8EF5C.active = True
            box_8EF5C.use_property_split = False
            box_8EF5C.use_property_decorate = False
            box_8EF5C.alignment = 'Expand'.upper()
            box_8EF5C.scale_x = 1.0
            box_8EF5C.scale_y = 1.0
            if not True: box_8EF5C.operator_context = "EXEC_DEFAULT"
            grid_1C5DB = box_8EF5C.grid_flow(columns=3, row_major=True, even_columns=False, even_rows=False, align=True)
            grid_1C5DB.enabled = True
            grid_1C5DB.active = True
            grid_1C5DB.use_property_split = False
            grid_1C5DB.use_property_decorate = False
            grid_1C5DB.alignment = 'Expand'.upper()
            grid_1C5DB.scale_x = 1.0
            grid_1C5DB.scale_y = 1.0
            if not True: grid_1C5DB.operator_context = "EXEC_DEFAULT"
            for i_E9239 in range(len(supportersui['sna_data_posincats'][3])-1,-1,-1):
                op = grid_1C5DB.operator('sna.lewd_op_6dbc7', text=supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][3][i_E9239], int, 0)], icon_value=supportersui['sna_imagen_paths'][string_to_type(supportersui['sna_data_posincats'][3][i_E9239], int, 0)], emboss=True, depress=False)
                op.sna_lewd_description = supportersui['sna_nota'][string_to_type(supportersui['sna_data_posincats'][3][i_E9239], int, 0)]
                op.sna_lewd_url = supportersui['sna_url'][string_to_type(supportersui['sna_data_posincats'][3][i_E9239], int, 0)]
        if (supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][2][0], int, 0)] != 'NOMBREDEREPUESTO'):
            box_60372 = col_CEDA9.box()
            box_60372.alert = False
            box_60372.enabled = True
            box_60372.active = True
            box_60372.use_property_split = False
            box_60372.use_property_decorate = False
            box_60372.alignment = 'Expand'.upper()
            box_60372.scale_x = 1.0
            box_60372.scale_y = 1.0
            if not True: box_60372.operator_context = "EXEC_DEFAULT"
            grid_B048D = box_60372.grid_flow(columns=3, row_major=True, even_columns=False, even_rows=False, align=True)
            grid_B048D.enabled = True
            grid_B048D.active = True
            grid_B048D.use_property_split = False
            grid_B048D.use_property_decorate = False
            grid_B048D.alignment = 'Expand'.upper()
            grid_B048D.scale_x = 1.0
            grid_B048D.scale_y = 1.0
            if not True: grid_B048D.operator_context = "EXEC_DEFAULT"
            for i_57995 in range(len(supportersui['sna_data_posincats'][2])-1,-1,-1):
                op = grid_B048D.operator('sna.super_op_6c998', text=supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][2][i_57995], int, 0)], icon_value=supportersui['sna_imagen_paths'][string_to_type(supportersui['sna_data_posincats'][2][i_57995], int, 0)], emboss=False, depress=False)
                op.sna_super_description = supportersui['sna_nota'][string_to_type(supportersui['sna_data_posincats'][2][i_57995], int, 0)]
        if (supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][1][0], int, 0)] != 'NOMBREDEREPUESTO'):
            box_7C0C5 = col_CEDA9.box()
            box_7C0C5.alert = False
            box_7C0C5.enabled = True
            box_7C0C5.active = True
            box_7C0C5.use_property_split = False
            box_7C0C5.use_property_decorate = False
            box_7C0C5.alignment = 'Expand'.upper()
            box_7C0C5.scale_x = 1.0
            box_7C0C5.scale_y = 1.0
            if not True: box_7C0C5.operator_context = "EXEC_DEFAULT"
            grid_088C3 = box_7C0C5.grid_flow(columns=3, row_major=True, even_columns=False, even_rows=False, align=True)
            grid_088C3.enabled = True
            grid_088C3.active = True
            grid_088C3.use_property_split = False
            grid_088C3.use_property_decorate = False
            grid_088C3.alignment = 'Expand'.upper()
            grid_088C3.scale_x = 1.0
            grid_088C3.scale_y = 1.0
            if not True: grid_088C3.operator_context = "EXEC_DEFAULT"
            for i_85DD2 in range(len(supportersui['sna_data_posincats'][1])-1,-1,-1):
                op = grid_088C3.operator('sna.blushed_op_6f8f5', text=supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][1][i_85DD2], int, 0)], icon_value=supportersui['sna_imagen_paths'][string_to_type(supportersui['sna_data_posincats'][1][i_85DD2], int, 0)], emboss=False, depress=False)
                op.sna_blushed_description = supportersui['sna_nota'][string_to_type(supportersui['sna_data_posincats'][1][i_85DD2], int, 0)]
        if (supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][0][0], int, 0)] != 'NOMBREDEREPUESTO'):
            box_01438 = col_CEDA9.box()
            box_01438.alert = False
            box_01438.enabled = True
            box_01438.active = True
            box_01438.use_property_split = False
            box_01438.use_property_decorate = False
            box_01438.alignment = 'Expand'.upper()
            box_01438.scale_x = 1.0
            box_01438.scale_y = 1.0
            if not True: box_01438.operator_context = "EXEC_DEFAULT"
            grid_999F3 = box_01438.grid_flow(columns=3, row_major=True, even_columns=False, even_rows=False, align=True)
            grid_999F3.enabled = True
            grid_999F3.active = True
            grid_999F3.use_property_split = False
            grid_999F3.use_property_decorate = False
            grid_999F3.alignment = 'Expand'.upper()
            grid_999F3.scale_x = 1.0
            grid_999F3.scale_y = 1.0
            if not True: grid_999F3.operator_context = "EXEC_DEFAULT"
            for i_12722 in range(len(supportersui['sna_data_posincats'][0])-1,-1,-1):
                op = grid_999F3.operator('sna.official_op_0e139', text=supportersui['sna_nombre'][string_to_type(supportersui['sna_data_posincats'][0][i_12722], int, 0)], icon_value=704, emboss=False, depress=False)
                op.sna_official_description = supportersui['sna_nota'][string_to_type(supportersui['sna_data_posincats'][0][i_12722], int, 0)].replace('n AWESOME', ' cute')
        row_4D6EB = col_CEDA9.row(heading='', align=True)
        row_4D6EB.alert = False
        row_4D6EB.enabled = True
        row_4D6EB.active = True
        row_4D6EB.use_property_split = False
        row_4D6EB.use_property_decorate = False
        row_4D6EB.scale_x = 1.0
        row_4D6EB.scale_y = 1.0
        row_4D6EB.alignment = 'Expand'.upper()
        row_4D6EB.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_4D6EB.operator('sna.refresh_panel_23b56', text='Refresh Panel!', icon_value=668, emboss=True, depress=False)
        op = row_4D6EB.operator('sna.report_issue_4b741', text='', icon_value=_icons['report_issue.png'].icon_id, emboss=True, depress=False)


class SNA_OT_Horny_Op_4473B(bpy.types.Operator):
    bl_idname = "sna.horny_op_4473b"
    bl_label = "HORNY OP"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_horny_description: bpy.props.StringProperty(name='horny_description', description='', default='', subtype='NONE', maxlen=0)
    sna_horny_url: bpy.props.StringProperty(name='horny_url', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        url = self.sna_horny_url
        if url.strip():
            webbrowser.open(url)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Lewd_Op_6Dbc7(bpy.types.Operator):
    bl_idname = "sna.lewd_op_6dbc7"
    bl_label = "LEWD OP"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_lewd_description: bpy.props.StringProperty(name='lewd_description', description='', default='', subtype='NONE', maxlen=0)
    sna_lewd_url: bpy.props.StringProperty(name='lewd_url', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        url = self.sna_lewd_url
        if url.strip():
            webbrowser.open(url)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Super_Op_6C998(bpy.types.Operator):
    bl_idname = "sna.super_op_6c998"
    bl_label = "SUPER OP"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_super_description: bpy.props.StringProperty(name='super_description', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Blushed_Op_6F8F5(bpy.types.Operator):
    bl_idname = "sna.blushed_op_6f8f5"
    bl_label = "BLUSHED OP"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_blushed_description: bpy.props.StringProperty(name='blushed_description', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Official_Op_0E139(bpy.types.Operator):
    bl_idname = "sna.official_op_0e139"
    bl_label = "OFFICIAL OP"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_official_description: bpy.props.StringProperty(name='official_description', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Sex_Op_792Ac(bpy.types.Operator):
    bl_idname = "sna.sex_op_792ac"
    bl_label = "SEX OP"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_sex_description: bpy.props.StringProperty(name='SEX_description', description='', default='', subtype='NONE', maxlen=0)
    sna_sex_url: bpy.props.StringProperty(name='SEX_url', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        url = self.sna_sex_url
        if url.strip():
            webbrowser.open(url)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


@persistent
def depsgraph_update_pre_handler_BC9F7(dummy):
    sna_supporterpanel_5A9E5()


@persistent
def load_post_handler_7F1C2(dummy):
    pass


def sna_supporterpanel_5A9E5():
    supportersui['sna_imagen_paths'] = []
    supportersui['sna_imagen2download'] = []
    for i_76B29 in range(len(supportersui['sna_imagen'])):
        supportersui['sna_imagen_paths'].append(load_preview_icon(pfp_cache + '\\' + supportersui['sna_nombre'][i_76B29] + '_' + str(i_76B29) + '.jpg'))
        if os.path.exists(pfp_cache + '\\' + supportersui['sna_nombre'][i_76B29] + '_' + str(i_76B29) + '.jpg'):
            pass
        else:
            supportersui['sna_imagen2download'].append(supportersui['sna_imagen'][i_76B29])
    supportersui['sna_imagen_paths'] = supportersui['sna_imagen_paths']
    supportersui['sna_imagen2download'] = supportersui['sna_imagen2download']
    lista_urls = supportersui['sna_imagen2download']
    imagen = supportersui['sna_imagen']
    nombre = supportersui['sna_nombre']
    import requests

    def descargar_lista(lista_urls, imagen, nombre):
        os.makedirs(pfp_cache, exist_ok=True)
        for url in lista_urls:
            # Nombre por defecto: el basename del enlace
            nombre_archivo = os.path.basename(url)
            # Si el enlace está en la lista imagen, usar el nombre correspondiente
            if url in imagen:
                idx = imagen.index(url)  # posición del enlace en la lista imagen
                nombre_archivo = f"{nombre[idx]}_{idx}.jpg"  # ahora índice 0-based
            ruta_destino = os.path.join(pfp_cache, nombre_archivo)
            try:
                print(f"📥 Descargando {url} ...")
                r = requests.get(url, stream=True)
                r.raise_for_status()
                with open(ruta_destino, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"✅ Guardado en {ruta_destino}")
            except Exception as e:
                print(f"❌ {url}: {e} no necesitas descargar nada!")
    # Uso: pasar las tres listas
    descargar_lista(lista_urls, imagen, nombre)


class SNA_OT_Report_Issue_4B741(bpy.types.Operator):
    bl_idname = "sna.report_issue_4b741"
    bl_label = "Report issue"
    bl_description = "DM mal if the panel doesnt show your name!"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        webbrowser.open("https://discord.com/invite/TDSdHDM4FC")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Refresh_Panel_23B56(bpy.types.Operator):
    bl_idname = "sna.refresh_panel_23b56"
    bl_label = "Refresh Panel"
    bl_description = "Reload all the member list with their icons, descriptions and links!"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_supporterpanel_5A9E5()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


@persistent
def depsgraph_update_pre_handler_68493(dummy):
    pass


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(SNA_PT_SKLX_CREATOR_69C58)
    bpy.utils.register_class(SNA_PT_PATREON_SUPPORTERS_7F269)
    if not 'report_issue.png' in _icons: _icons.load('report_issue.png', os.path.join(os.path.dirname(__file__), 'icons', 'report_issue.png'), "IMAGE")
    bpy.utils.register_class(SNA_OT_Horny_Op_4473B)
    bpy.utils.register_class(SNA_OT_Lewd_Op_6Dbc7)
    bpy.utils.register_class(SNA_OT_Super_Op_6C998)
    bpy.utils.register_class(SNA_OT_Blushed_Op_6F8F5)
    bpy.utils.register_class(SNA_OT_Official_Op_0E139)
    bpy.utils.register_class(SNA_OT_Sex_Op_792Ac)
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre_handler_BC9F7)
    bpy.app.handlers.load_post.append(load_post_handler_7F1C2)
    bpy.utils.register_class(SNA_OT_Report_Issue_4B741)
    bpy.utils.register_class(SNA_OT_Refresh_Panel_23B56)
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre_handler_68493)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(SNA_PT_SKLX_CREATOR_69C58)
    bpy.utils.unregister_class(SNA_PT_PATREON_SUPPORTERS_7F269)
    bpy.utils.unregister_class(SNA_OT_Horny_Op_4473B)
    bpy.utils.unregister_class(SNA_OT_Lewd_Op_6Dbc7)
    bpy.utils.unregister_class(SNA_OT_Super_Op_6C998)
    bpy.utils.unregister_class(SNA_OT_Blushed_Op_6F8F5)
    bpy.utils.unregister_class(SNA_OT_Official_Op_0E139)
    bpy.utils.unregister_class(SNA_OT_Sex_Op_792Ac)
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre_handler_BC9F7)
    bpy.app.handlers.load_post.remove(load_post_handler_7F1C2)
    bpy.utils.unregister_class(SNA_OT_Report_Issue_4B741)
    bpy.utils.unregister_class(SNA_OT_Refresh_Panel_23B56)
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre_handler_68493)
