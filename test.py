
import typing
import bpy
import bpy.types
import time
import traceback
import sys

from .mark import mark
from .printx import *


# ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰

'''
WIRE_OT_test_delete_speed_1：基本用时 476215700
WIRE_OT_test_delete_speed_2：基本用时 121231100
'''

class WIRE_PT_text_editor_info(bpy.types.Panel):
    bl_idname = 'WIRE_PT_text_editor_info'
    bl_label = "信息（仅用于测试）"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Text'
    '''
    用于显示文本编辑器的光标的位置，仅测试用
    '''

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        space = cast(bpy.types.SpaceTextEditor, context.space_data)
        area = context.area
        region: bpy.types.Region = None
        for _r in area.regions:
            if _r.type == 'WINDOW':
                region = _r
                break
        window = context.window
        text = space.text

        # offset 的原点在区块左下角
        offset_x, offset_y = space.region_location_from_cursor(
            text.current_line_index, text.current_character)

        client_x = region.x + offset_x
        client_y = window.height - (region.y + offset_y)

        layout.label(text="光标位置（相对区块左下角）：")
        layout.label(text="%d, %d" % (offset_x, offset_y))
        layout.label(text="光标位置（相对窗口左上角）：")
        layout.label(text="%d, %d" % (client_x, client_y))

        layout.separator()

        layout.label(text="region x, y：")
        layout.label(text="%d, %d" % (region.x, region.y))
        layout.label(text="region w, h：")
        layout.label(text="%d, %d" % (region.width, region.height))

        layout.separator()

        layout.label(text="area x, y：")
        layout.label(text="%d, %d" % (area.x, area.y))
        layout.label(text="area w, h：")
        layout.label(text="%d, %d" % (area.width, area.height))

        layout.separator()

        layout.label(text="window x, y：")
        layout.label(text="%d, %d" % (window.x, window.y))
        layout.label(text="window w, h：")
        layout.label(text="%d, %d" % (window.width, window.height))

        pass

class WIRE_OT_test_delete_speed_1(bpy.types.Operator):
    bl_idname = 'wire.test_delete_speed_1'
    bl_label = "删除速度测试1"
    bl_description = "删除速度测试1"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        _text = "删除速度测试删除速度测试删除速度测试删除速度测试"
        _len = len(_text)
        _statr = time.perf_counter_ns()

        for _ in range(100):  # 测试100次
            bpy.ops.font.text_insert(text=_text)
            for _ in range(_len):  # 删除之前的输入
                bpy.ops.font.delete('EXEC_REGION_WIN', type='PREVIOUS_CHARACTER')

        _end = time.perf_counter_ns()
        _span = _end - _statr

        printx(CCBY, "删除速度测试1 用时：", _span)

        return {'FINISHED'}

class WIRE_OT_test_delete_speed_2(bpy.types.Operator):
    bl_idname = 'wire.test_delete_speed_2'
    bl_label = "删除速度测试2"
    bl_description = "删除速度测试2"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        _text = "删除速度测试删除速度测试删除速度测试删除速度测试"
        _len = len(_text)
        _statr = time.perf_counter_ns()

        for _ in range(100):  # 测试100次
            bpy.ops.font.text_insert(text=_text)
            for _ in range(_len):  # 删除之前的输入
                bpy.ops.font.move_select('EXEC_REGION_WIN', type='PREVIOUS_CHARACTER')
            bpy.ops.font.delete('EXEC_REGION_WIN', type='SELECTION')

        _end = time.perf_counter_ns()
        _span = _end - _statr

        printx(CCBY, "删除速度测试2 用时：", _span)

        return {'FINISHED'}

def VIEW3D_MT_edit_font_draw_func(self: bpy.types.Menu, context: bpy.types.Context):
    layout = self.layout
    layout.operator(WIRE_OT_test_delete_speed_1.bl_idname)
    layout.operator(WIRE_OT_test_delete_speed_2.bl_idname)

# ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰

def register():
    if mark.DEBUG_BUILD:
        printx(CCBY, "已加载测试相关功能")
        bpy.utils.register_class(WIRE_PT_text_editor_info)
        bpy.utils.register_class(WIRE_OT_test_delete_speed_1)
        bpy.utils.register_class(WIRE_OT_test_delete_speed_2)
        bpy.types.VIEW3D_MT_edit_font.prepend(VIEW3D_MT_edit_font_draw_func)

        if WIRE_OT_test_fix_ime_toggle.__name__ not in dir(bpy.types):
            # 注册后不卸载
            bpy.utils.register_class(WIRE_OT_test_fix_ime_toggle)
            bpy.utils.register_class(WIRE_OT_test_fix_ime_reload)
            bpy.types.STATUSBAR_HT_header.prepend(STATUSBAR_HT_header_draw_func)

def unregister():
    if mark.DEBUG_BUILD:
        bpy.types.VIEW3D_MT_edit_font.remove(VIEW3D_MT_edit_font_draw_func)
        bpy.utils.unregister_class(WIRE_OT_test_delete_speed_1)
        bpy.utils.unregister_class(WIRE_OT_test_delete_speed_2)
        bpy.utils.unregister_class(WIRE_PT_text_editor_info)

# ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰


class WIRE_OT_test_fix_ime_toggle(bpy.types.Operator):
    bl_idname = 'wire.test_fix_ime_toggle'
    bl_label = "启停插件"
    bl_description = "启停插件"

    def execute(self, context: bpy.types.Context):
        if __package__ in bpy.context.preferences.addons:
            try:
                bpy.ops.preferences.addon_disable(module=__package__)
            except:
                traceback.print_exc()
                print("ERROR: addon_disable %s false" % __package__)
                return {'CANCELLED'}

            for name in list(sys.modules.keys()):
                if name == __package__:
                    del sys.modules[name]
        else:
            try:
                bpy.ops.preferences.addon_enable(module=__package__)
            except:
                traceback.print_exc()
                print("ERROR: addon_enable %s false" % __package__)
                return {'CANCELLED'}

            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

        return {'FINISHED'}

class WIRE_OT_test_fix_ime_reload(bpy.types.Operator):
    bl_idname = 'wire.test_fix_ime_reload'
    bl_label = "重启插件"
    bl_description = "重启插件"

    def execute(self, context: bpy.types.Context):
        try:
            bpy.ops.preferences.addon_disable(module=__package__)
        except:
            traceback.print_exc()
            print("插件停用失败：%s" % __package__)
            return {'CANCELLED'}

        for name in list(sys.modules.keys()):
            if name == __package__:
                del sys.modules[name]

        try:
            bpy.ops.preferences.addon_enable(module=__package__)
        except:
            traceback.print_exc()
            print("插件启用失败：%s" % __package__)
            return {'CANCELLED'}

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

        return {'FINISHED'}

def STATUSBAR_HT_header_draw_func(self: 'bpy.types.TOPBAR_MT_blender', context: bpy.types.Context):
    layout: bpy.types.UILayout = self.layout
    row = layout.row(align=True)
    row.operator(WIRE_OT_test_fix_ime_reload.bl_idname, text="", icon='FILE_SCRIPT')
    row.operator(WIRE_OT_test_fix_ime_toggle.bl_idname, text="",
        icon='RADIOBUT_ON' if __package__ in context.preferences.addons else 'RADIOBUT_OFF')
