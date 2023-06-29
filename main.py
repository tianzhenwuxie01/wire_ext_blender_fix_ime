import sys
import traceback
from typing import cast, Literal
from types import SimpleNamespace
import ctypes

import bpy
import bpy.types
import blf

from .mark import *
from .debug import *

from .native import native

# ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰

def use_debug_update(self: dict, context: bpy.types.Context):
    use_debug = bool(self.get('use_debug'))

    global DEBUG
    DEBUG = use_debug

    native.use_debug(DEBUG)
    native.use_hook_debug(DEBUG)
    native.use_fix_ime_debug(DEBUG)

    if DEBUG:
        if not WIRE_PT_text_editor_info._registered:
            bpy.utils.register_class(WIRE_PT_text_editor_info)
            WIRE_PT_text_editor_info._registered = True
    else:
        if WIRE_PT_text_editor_info._registered:
            bpy.utils.unregister_class(WIRE_PT_text_editor_info)
            WIRE_PT_text_editor_info._registered = False

def use_fix_ime_update(self: dict, context: bpy.types.Context):
    use_fix_ime_state = bool(self.get('use_fix_ime_state'))
    use_fix_ime_input = bool(self.get('use_fix_ime_input'))

    if native.dll_loaded:
        if use_fix_ime_state:
            native.use_fix_ime_state(True)
            native.use_fix_ime_input(use_fix_ime_input)
            if use_fix_ime_input:
                register_fix_ime_input()
            else:
                unregister_fix_ime_input()
        else:
            native.use_fix_ime_state(False)
            native.use_fix_ime_input(False)  # 必须关闭
            unregister_fix_ime_input()

def use_header_extned(self: dict, context: bpy.types.Context):
    global TEXT_HT_header_extend_appended
    global CONSOLE_HT_header_extend_appended

    use_header_extend_text_editor = bool(self.get('use_header_extend_text_editor'))
    use_header_extend_console = bool(self.get('use_header_extend_console'))

    if use_header_extend_text_editor:
        if not TEXT_HT_header_extend_appended:
            bpy.types.TEXT_HT_header.append(TEXT_HT_header_extend)
            TEXT_HT_header_extend_appended = True
    else:
        if TEXT_HT_header_extend_appended:
            bpy.types.TEXT_HT_header.remove(TEXT_HT_header_extend)
            TEXT_HT_header_extend_appended = False

    if use_header_extend_console:
        if not CONSOLE_HT_header_extend_appended:
            bpy.types.CONSOLE_HT_header.append(CONSOLE_HT_header_extend)
            CONSOLE_HT_header_extend_appended = True
    else:
        if CONSOLE_HT_header_extend_appended:
            bpy.types.CONSOLE_HT_header.remove(CONSOLE_HT_header_extend)
            CONSOLE_HT_header_extend_appended = False


def get_prefs(context: bpy.types.Context) -> 'WIRE_FIX_Preferences':
    return context.preferences.addons[__package__].preferences

class WIRE_FIX_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__  # 必须和插件模块名称相同

    use_debug: bpy.props.BoolProperty(
        name="启用调试",
        description="启用调试模式，运行信息将会输出到控制台",
        default=True if DEBUG_BUILD else False,
        update=use_debug_update,
    )

    use_fix_ime_state: bpy.props.BoolProperty(
        name="自动管理输入法状态",
        description="启用后，当用户激活输入框时，插件会自动启用输入法，退出输入框时，插件会自动停用输入法",
        default=True,
        update=use_fix_ime_update,
    )

    use_fix_ime_input: bpy.props.BoolProperty(
        name="使用输入法输入文字",
        description="启用后，可以在某些情况下直接使用输入法输入文字",
        default=True,
        update=use_fix_ime_update,
    )

    use_fix_ime_input_font_edit: bpy.props.BoolProperty(
        name="文本物体编辑模式",
        description="启用后，可以在【3D视图】的【文本物体】的【编辑模式】中直接使用输入法输入文字",
        default=True,
    )

    use_fix_ime_input_text_editor: bpy.props.BoolProperty(
        name="文本编辑器",
        description="启用后，可以在【文本编辑器】中直接使用输入法输入文字",
        default=True,
    )

    use_fix_ime_input_console: bpy.props.BoolProperty(
        name="控制台",
        description="启用后，可以在【控制台】中直接使用输入法输入文字",
        default=True,
    )

    candidate_window_percent: bpy.props.FloatProperty(
        name="候选窗口水平位置",
        description="候选窗口的左侧在屏幕工作区底部的水平位置，最终位置会受系统调整",
        default=0.4,
        min=0,
        max=1,
        subtype='FACTOR',
    )

    use_header_extend_text_editor: bpy.props.BoolProperty(
        name="文本编辑器状态提示",
        description="启用后，在【文本编辑器】的标题栏中显示“使用输入法输入文字”功能相关的状态提示",
        default=True,
        update=use_header_extned,
    )

    use_header_extend_console: bpy.props.BoolProperty(
        name="控制台状态提示",
        description="启用后，在【控制台】的标题栏中显示“使用输入法输入文字”功能相关的状态提示",
        default=True,
        update=use_header_extned,
    )

    def draw(self, context: bpy.types.Context):
        layout: bpy.types.UILayout = self.layout.column()
        split_factor = 0.3

        column = layout.column(align=True)

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.prop(self, 'use_fix_ime_state')

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.active = self.use_fix_ime_state
        rowr.separator(factor=1.5)
        rowr.prop(self, 'use_fix_ime_input')

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.active = self.use_fix_ime_state and self.use_fix_ime_input
        rowr.separator(factor=1.5)
        rowr.separator(factor=1.5)
        rowr.prop(self, 'use_fix_ime_input_font_edit')

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowl.alignment = 'RIGHT'
        rowl.label(text="候选窗口水平位置")
        rowr = split.row()
        rowr.active = self.use_fix_ime_state and self.use_fix_ime_input and self.use_fix_ime_input_font_edit
        rowr.separator(factor=1.5)
        rowr.separator(factor=1.5)
        rowr.separator(factor=1.5)
        rowr.prop(self, 'candidate_window_percent', text="")

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.active = self.use_fix_ime_state and self.use_fix_ime_input
        rowr.separator(factor=1.5)
        rowr.separator(factor=1.5)
        rowr.prop(self, 'use_fix_ime_input_text_editor')

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.active = self.use_fix_ime_state and self.use_fix_ime_input
        rowr.separator(factor=1.5)
        rowr.separator(factor=1.5)
        rowr.prop(self, 'use_fix_ime_input_console')

        # 界面

        layout.separator()

        column = layout.column(align=True)

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowl.alignment = 'RIGHT'
        rowl.label(text="显示状态提示")
        rowr = split.row()
        rowr.active = self.use_fix_ime_state and self.use_fix_ime_input
        rowr.separator(factor=1.5)
        rowr.separator(factor=1.5)
        rowr.prop(self, 'use_header_extend_text_editor', text="文本编辑器")

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.active = self.use_fix_ime_state and self.use_fix_ime_input
        rowr.separator(factor=1.5)
        rowr.separator(factor=1.5)
        rowr.prop(self, 'use_header_extend_console', text="控制台")

        # 调试

        layout.separator()

        column = layout.column(align=True)

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.prop(self, 'use_debug')

        split = column.split(factor=split_factor)
        rowl = split.row()
        rowr = split.row()
        rowr.alert = True
        rowr.separator(factor=1.5)
        rowr.label(text="平时不要开启调试，会影响性能")


# ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰


_registered = False

# Font, EMPTY, WINDOW
_object_font_edit_key_map: bpy.types.KeyMap = None
_object_font_edit_key_map_item: bpy.types.KeyMapItem = None

# Text, TEXT_EDITOR, WINDOW
_space_text_editor_key_map: bpy.types.KeyMap = None
_space_text_editor_key_map_item: bpy.types.KeyMapItem = None

# Console, CONSOLE, WINDOW
_space_console_key_map: bpy.types.KeyMap = None
_space_console_key_map_item: bpy.types.KeyMapItem = None


def register_fix_ime_input():
    global _registered
    global _object_font_edit_key_map
    global _object_font_edit_key_map_item
    global _space_text_editor_key_map
    global _space_text_editor_key_map_item
    global _space_console_key_map
    global _space_console_key_map_item

    if _registered:
        return

    if DEBUG:
        print("注册快捷键")

    context = bpy.context
    wm = context.window_manager
    kc = wm.keyconfigs.addon

    # 映射项中的 Shift 必须为 -1，否则无法在用户输入 Shift + 1 的情况下处理输入
    # 因为此时发送的 Ctrl + F16 会附加一个 Shift 按键。

    km = kc.keymaps.new(name="Font", space_type='EMPTY', region_type='WINDOW')
    kmi = km.keymap_items.new(
        idname=WIRE_OT_fix_ime_input_font_edit.bl_idname,
        type='F16', value='PRESS',
        ctrl=True, shift=-1, alt=False, repeat=False,
    )
    _object_font_edit_key_map = km
    _object_font_edit_key_map_item = kmi

    km = kc.keymaps.new(name="Text", space_type='TEXT_EDITOR', region_type='WINDOW')
    kmi = km.keymap_items.new(
        idname=WIRE_OT_fix_ime_input_text_editor.bl_idname,
        type='F16', value='PRESS',
        ctrl=True, shift=-1, alt=False, repeat=False,
    )
    _space_text_editor_key_map = km
    _space_text_editor_key_map_item = kmi

    km = kc.keymaps.new(name="Console", space_type='CONSOLE', region_type='WINDOW')

    kmi = km.keymap_items.new(
        idname=WIRE_OT_fix_ime_input_console.bl_idname,
        type='F16', value='PRESS',
        ctrl=True, shift=-1, alt=False, repeat=False,
    )
    _space_console_key_map = km
    _space_console_key_map_item = kmi

    _registered = True

def unregister_fix_ime_input():
    global _registered
    global _object_font_edit_key_map
    global _object_font_edit_key_map_item
    global _space_text_editor_key_map
    global _space_text_editor_key_map_item
    global _space_console_key_map
    global _space_console_key_map_item

    if not _registered:
        return

    if DEBUG:
        print("卸载快捷键")

    if _object_font_edit_key_map and _object_font_edit_key_map_item:
        _object_font_edit_key_map.keymap_items.remove(_object_font_edit_key_map_item)
    _object_font_edit_key_map = None
    _object_font_edit_key_map_item = None

    if _space_text_editor_key_map and _space_text_editor_key_map_item:
        _space_text_editor_key_map.keymap_items.remove(_space_text_editor_key_map_item)
    _space_text_editor_key_map = None
    _space_text_editor_key_map_item = None

    if _space_console_key_map and _space_console_key_map_item:
        _space_console_key_map.keymap_items.remove(_space_console_key_map_item)
    _space_console_key_map = None
    _space_console_key_map_item = None

    _registered = False

# ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰

def update_candidate_window_pos_font_edit(context: bpy.types.Context):
    # 注意 ：修改代码时留意 update_candidate_window_pos 中的 _ctx 的属性

    if DEBUG:
        print(CFHIT1, "更新光标位置", "VIEW_3D")

    window = context.window

    # 由 Native 完成设置
    pref = get_prefs(context)
    native.candidate_window_position_update_font_edit(
        window.as_pointer(), pref.candidate_window_percent)

def update_candidate_window_pos_text_editor(context: bpy.types.Context):
    # 注意 ：修改代码时留意 update_candidate_window_pos 中的 _ctx 的属性

    if DEBUG:
        print(CFHIT1, "更新光标位置", "TEXT_EDITOR")

    window = context.window
    space = cast(bpy.types.SpaceTextEditor, context.space_data)
    region = context.region
    text = space.text

    # 偏移（offset）的原点在区块左下角
    offset_x, offset_y = space.region_location_from_cursor(
        text.current_line_index, text.current_character)
    # 区块（region）的原点在窗口左下角
    client_x = region.x + offset_x
    client_y = window.height - (region.y + offset_y)

    # if DEBUG:
    #     print("offset: ", offset_x, offset_y)
    #     print("region: ", region.x, region.y)
    #     print("client: ", client_x, client_y)

    native.candidate_window_position_update_text_editor(
        window.as_pointer(), client_x, client_y)

def update_candidate_window_pos_console(context: bpy.types.Context):
    # 注意 ：修改代码时留意 update_candidate_window_pos 中的 _ctx 的属性

    if DEBUG:
        print(CFHIT1, "更新光标位置", "CONSOLE")

    window = context.window
    space = cast(bpy.types.SpaceConsole, context.space_data)
    region = context.region
    preferences = context.preferences

    client_x = region.x
    client_y = window.height - region.y
    rect_l = region.x
    # 20 是 Blender 界面元素的基准高度，2 是 两行，
    # context.preferences.system.ui_scale 是 系统 和 程序 界面缩放系数之积，
    # (space.font_size / 12) 是当前编辑器的缩放系数
    rect_t = window.height - region.y - int(
        20 * 2 * preferences.system.ui_scale * (space.font_size / 12))
    rect_r = region.x + region.width
    rect_b = window.height - region.y

    # if DEBUG:
    #     print("client: ", client_x, client_y)
    #     print("rect: ", rect_l, rect_t, rect_r, rect_b)

    native.candidate_window_position_update_console(
        window.as_pointer(),
        client_x, client_y,
        rect_l, rect_t, rect_r, rect_b)

# ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰


_state = {
    'inputing': False,  # 是否正在输入文字
    'font': {
        'insert': bpy.ops.font.text_insert,
        'delete': bpy.ops.font.delete,
        'move': bpy.ops.font.move,
        'instance': None,  # 似乎多余
    },
    'text': {
        'insert': bpy.ops.text.insert,
        'delete': bpy.ops.text.delete,
        'move': bpy.ops.text.move,
        'instance': None,
    },
    'console': {
        'insert': bpy.ops.console.insert,
        'delete': bpy.ops.console.delete,
        'move': bpy.ops.console.move,
        'instance': None,
    },
}

class WIRE_OT_fix_ime_input_BASE():
    '''
    必须独立设置一个操作，不能合并到 WIRE_OT_fix_ime_input，
    否则用户无法通过撤销（Undo）来撤销文字的输入。
    '''

    def __init__(self, target: Literal['font', 'text', 'console']):
        self.target = target
        self.insert = _state[self.target]['insert']
        self.delete = _state[self.target]['delete']
        self.move = _state[self.target]['move']
        self.length = 0
        self.caret_pos = 0

    def execute(self, context: bpy.types.Context):
        self.report({'ERROR'}, "必须以 INVOKE 的方式调用")
        return {'CANCELLED'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        if _state[self.target]['instance']:  # 防止多个实例运行
            return {'CANCELLED'}
        _state[self.target]['instance'] = self

        _state['inputing'] = True

        if DEBUG:
            print(CFHIT1, "开始合成文本")

        text = native.ime_text_get()
        self.length = len(text) + 2
        self.caret_pos = native.ime_text_caret_pos_get()
        self.move_times = self.length - self.caret_pos - 1  # -1 = -2 + 1，-2 是减去之前多加的 2，+1 是右侧的中括号
        self.insert(text='[' + text + ']')
        for _ in range(self.move_times):
            self.move(type='PREVIOUS_CHARACTER')

        if DEBUG:
            print("当前文本 (长度：%d，光标：%d):" % (self.length - 2, self.caret_pos), CCBY + text + CCZ0)

        if self.target == 'font':
            update_candidate_window_pos_font_edit(context)
        elif self.target == 'text':
            update_candidate_window_pos_text_editor(context)
        elif self.target == 'console':
            update_candidate_window_pos_console(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        key = event.type
        value = event.value

        # 合成文字 UPDATE
        if key == 'F17' and value == 'PRESS':
            if DEBUG:
                print(CFHIT1, "更新合成文本")

            if self.move_times != 0:  # 移动到最后的位置
                for _ in range(self.move_times):
                    self.move(type='NEXT_CHARACTER')

            for _ in range(self.length):  # 删除之前的输入
                self.delete('EXEC_REGION_WIN', type='PREVIOUS_CHARACTER')

            text = native.ime_text_get()
            self.length = len(text) + 2  # 加上中括号两个字符
            self.caret_pos = native.ime_text_caret_pos_get()
            self.move_times = self.length - self.caret_pos - 1  # -1 = -2 + 1，-2 是减去之前多加的 2，+1 是右侧的中括号
            self.insert(text='[' + text + ']')
            for _ in range(self.move_times):
                self.move(type='PREVIOUS_CHARACTER')

            if DEBUG:
                print("当前文本 (长度：%d，光标：%d):" % (self.length - 2, self.caret_pos), CCBY + text + CCZ0)

            if self.target == 'font':
                update_candidate_window_pos_font_edit(context)
            elif self.target == 'text':
                update_candidate_window_pos_text_editor(context)
            elif self.target == 'console':
                update_candidate_window_pos_console(context)

        # 输出文字 FINISH
        elif key == 'F18' and value == 'PRESS':
            if DEBUG:
                print(CFHIT1, "确认合成文本")

            if self.move_times != 0:  # 移动到最后的位置
                for _ in range(self.move_times):
                    self.move(type='NEXT_CHARACTER')

            for _ in range(self.length):
                self.delete('EXEC_REGION_WIN', type='PREVIOUS_CHARACTER')

            text = native.ime_text_get()
            self.insert(text=text)

            if DEBUG:
                print("当前文本 (长度：%d):" % (self.length - 2), CCBY + text + CCZ0)

            if self.target == 'font':
                update_candidate_window_pos_font_edit(context)
            elif self.target == 'text':
                update_candidate_window_pos_text_editor(context)
            elif self.target == 'console':
                update_candidate_window_pos_console(context)

            _state[self.target]['instance'] = None
            _state['inputing'] = False
            return {'FINISHED'}

        # 取消合成 CNACEL
        elif ((key == 'F19' and value == 'PRESS') or
              (key == 'MOUSEMOVE' and not native.is_in_composition())):
            if DEBUG:
                print(CFHIT1, "取消合成文本")

            if self.move_times != 0:  # 移动到最后的位置
                for _ in range(self.move_times):
                    self.move(type='NEXT_CHARACTER')

            for _ in range(self.length):
                self.delete('EXEC_REGION_WIN', type='PREVIOUS_CHARACTER')

            if self.target == 'font':
                update_candidate_window_pos_font_edit(context)
            elif self.target == 'text':
                update_candidate_window_pos_text_editor(context)
            elif self.target == 'console':
                update_candidate_window_pos_console(context)

            _state[self.target]['instance'] = None
            _state['inputing'] = False
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

class WIRE_OT_fix_ime_input_font_edit(WIRE_OT_fix_ime_input_BASE, bpy.types.Operator):
    bl_idname = 'wire.fix_ime_input_font_edit'
    bl_label = "[输入文字]"
    bl_description = ""
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(clss, context: bpy.types.Context):
        prefs = get_prefs(context)
        return context.space_data.type == 'VIEW_3D' and context.mode == 'EDIT_TEXT' and (
            prefs.use_fix_ime_input and
            prefs.use_fix_ime_input_font_edit and
            native.dll_loaded)

    def __init__(self) -> None:
        super().__init__('font')

class WIRE_OT_fix_ime_input_text_editor(WIRE_OT_fix_ime_input_BASE, bpy.types.Operator):
    bl_idname = 'wire.fix_ime_input_text_editor'
    bl_label = "[输入文字]"
    bl_description = ""
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(clss, context: bpy.types.Context):
        prefs = get_prefs(context)
        return context.space_data.type == 'TEXT_EDITOR' and (
            prefs.use_fix_ime_input and
            prefs.use_fix_ime_input_text_editor and
            native.dll_loaded)

    def __init__(self) -> None:
        super().__init__('text')

class WIRE_OT_fix_ime_input_console(WIRE_OT_fix_ime_input_BASE, bpy.types.Operator):
    bl_idname = 'wire.fix_ime_input_console'
    bl_label = "[输入文字]"
    bl_description = ""
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(clss, context: bpy.types.Context):
        prefs = get_prefs(context)
        return context.space_data.type == 'CONSOLE' and (
            prefs.use_fix_ime_input and
            prefs.use_fix_ime_input_console and
            native.dll_loaded)

    def __init__(self) -> None:
        super().__init__('console')


watchers: dict[bpy.types.Window, 'WIRE_OT_fix_ime_input_watcher'] = {}

class WIRE_OT_fix_ime_input_watcher(bpy.types.Operator):
    bl_idname = 'wire.fix_ime_input_watcher'
    bl_label = "鼠标位置监视器"
    bl_description = "根据鼠标当前位置，在区块中启用或停用输入法"
    bl_options = set()

    _windows: list[bpy.types.Window] = []

    @classmethod
    def poll(clss, context: bpy.types.Context) -> bool:
        if not native.dll:
            return False

        prefs = get_prefs(context)
        if not (prefs.use_fix_ime_state and
                prefs.use_fix_ime_input and (
            prefs.use_fix_ime_input_font_edit or
            prefs.use_fix_ime_input_text_editor or
            prefs.use_fix_ime_input_console)):
            return False

        # 每个窗口只需运行一个监视器。
        # 似乎 Blender 在销毁临时窗口时不会真正销毁临时窗口，而是隐藏临时窗口，连模态操作也不会销毁，
        # 不过切换工作区时似乎会真正销毁被隐藏的临时窗口。
        if (window := context.window) not in clss._windows:
            clss._windows.append(window)
            return True
        return False

    def __init__(self) -> None:
        super().__init__()
        # 当前输入法是否已经启动
        self._enabled = False
        self._space = None
        self._region = None

    def execute(self, context: bpy.types.Context):
        self.report({'ERROR'}, "必须以 INVOKE 的方式调用")
        return {'CANCELLED'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        if DEBUG:
            _index = self._windows.index(context.window)
            print(CFHIT1, "鼠标位置监视器启动 (%d, %d)：%X" % (
                _index, len(self._windows), context.window.as_pointer()))

        watchers[context.window] = self

        # 将窗口指针和窗口句柄绑定
        native.window_associate_pointer(context.window.as_pointer())

        self.update_ime_state(context, event)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL', 'PASS_THROUGH', 'INTERFACE'}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        # 如果用户激活了输入控件，则所有输入消息都会返送到输入控件，此时不会收到任何消息，
        # 因此不用担心和输入控件中输入法状态的冲突。

        window = context.window

        prefs = get_prefs(context)
        if not (prefs.use_fix_ime_state and
                prefs.use_fix_ime_input and (
            prefs.use_fix_ime_input_font_edit or
            prefs.use_fix_ime_input_text_editor or
            prefs.use_fix_ime_input_console)):
            if (_index := self._windows.index(window)) >= 0:
                self._windows.remove(window)
            if DEBUG:
                print(CFWARN, "鼠标位置监视器停用 (%d, %d)：%X" % (
                    _index, len(self._windows), window.as_pointer()))
            return {'CANCELLED', 'PASS_THROUGH', 'INTERFACE'}

        if not _state['inputing'] and native.window_is_active(window.as_pointer()):
            self.update_ime_state(context, event)

        return {'RUNNING_MODAL', 'PASS_THROUGH', 'INTERFACE'}

    def cancel(self, context: bpy.types.Context):
        # 窗口关闭的时候 Blender 也会触发 cancel 函数
        window = context.window
        if (_index := self._windows.index(window)) >= 0:
            self._windows.remove(window)
        if window in watchers:
            watchers.pop(window)
        if DEBUG:
            print(CFWARN, "鼠标位置监视器停用 (%d, %d)：%X" % (
                _index, len(self._windows), context.window.as_pointer()))
        pass

    def update_ime_state(self, context: bpy.types.Context, event: bpy.types.Event):
        # 鼠标进入符合条件的区块则启用输入法，否则停用输入法

        prefs = get_prefs(context)
        key = event.type
        value = event.value
        mouse_x = event.mouse_x
        mouse_y = event.mouse_y

        if key == 'WINDOW_DEACTIVATE':
            native.ime_input_disable(context.window.as_pointer())
            self._enabled = False
            self._space = None
            self._region = None

        # 仅在鼠标发生了移动时才检查，否则可能会误判
        # 虽然只是监听 MOUSEMOVE，但实际在鼠标不移动的时候也会触发，譬如按 TAB 切换编辑模式时。
        elif key == 'MOUSEMOVE':

            editor_type: Literal['font', 'text', 'console'] = None
            _space: bpy.types.Space = False
            _region: bpy.types.Region = None

            areas_view3d: list[bpy.types.Area] = []
            areas_text_editor: list[bpy.types.Area] = []
            areas_console: list[bpy.types.Area] = []
            for area in context.screen.areas.values():
                if area.type == 'VIEW_3D':
                    areas_view3d.append(area)
                elif area.type == 'TEXT_EDITOR':
                    areas_text_editor.append(area)
                elif area.type == 'CONSOLE':
                    areas_console.append(area)

            if not editor_type and prefs.use_fix_ime_input_font_edit:
                obj = context.active_object
                if obj and obj.type == 'FONT' and obj.mode == 'EDIT':
                    for area in areas_view3d:
                        region = [r for r in area.regions.values() if r.type == 'WINDOW'][0]
                        if (region.x <= mouse_x <= region.x + region.width and
                            region.y <= mouse_y <= region.y + region.height):
                            editor_type = 'font'
                            _space = area.spaces[0]
                            _region = region
                            break

            if not editor_type and prefs.use_fix_ime_input_text_editor:
                for area in areas_text_editor:
                    tx_editor = cast(bpy.types.SpaceTextEditor, area.spaces[0])
                    if tx_editor.text:
                        region = [r for r in area.regions.values() if r.type == 'WINDOW'][0]
                        if (region.x <= mouse_x <= region.x + region.width and
                            region.y <= mouse_y <= region.y + region.height):
                            editor_type = 'text'
                            _space = area.spaces[0]
                            _region = region
                            break

            if not editor_type and prefs.use_fix_ime_input_console:
                for area in areas_console:
                    region = [r for r in area.regions.values() if r.type == 'WINDOW'][0]
                    if (region.x <= mouse_x <= region.x + region.width and
                        region.y <= mouse_y <= region.y + region.height):
                        editor_type = 'console'
                        _space = area.spaces[0]
                        _region = region
                        break

            if editor_type:
                # 检测到符合条件的区块，如果当前没有启用输入法或当前鼠标所在空间和之前不同，则启用输入法
                if not self._enabled or _space != self._space:
                    if DEBUG:
                        print(CCFG, "在区块中启用输入法：%s" % _space.type)
                    native.ime_input_enable(context.window.as_pointer())
                    self._enabled = True
                    self._space = _space
                    self._region = _region
                    self.update_candidate_window_pos(context)
            else:
                if self._enabled:
                    if DEBUG:
                        print(CCFP, "在区块中停用输入法")
                    native.ime_input_disable(context.window.as_pointer())  # 此处会间接使得【输入法冲突】被“二次”修复
                    self._enabled = False
                    self._space = None
                    self._region = None

        # 在大部分按键事件中均会重新获取光标位置，以便下次输入的时候，候选框能够在准确的位置显示，不会闪一下
        elif self._enabled and key not in [
            '',  # 未知按键类型
            'LEFT_CTRL', 'LEFT_SHIFT', 'LEFT_ALT', 'RIGHT_ALT', 'RIGHT_CTRL', 'RIGHT_SHIFT',
            'F16', 'F17', 'F18', 'F19',  # 原则上需要加入更多不需要的按键，目前先这样
        ] and value == 'RELEASE':
            if DEBUG:
                print("触发光标位置更新：" + "'" + key + "'")
            self.update_candidate_window_pos(context)

    def update_candidate_window_pos(self, context: bpy.types.Context):
        _ctx = SimpleNamespace()
        _ctx.window = context.window
        _ctx.space_data = self._space
        _ctx.region = self._region
        _ctx.preferences = context.preferences
        if self._space.type == 'VIEW_3D':
            update_candidate_window_pos_font_edit(_ctx)
        elif self._space.type == 'TEXT_EDITOR':
            update_candidate_window_pos_text_editor(_ctx)
        elif self._space.type == 'CONSOLE':
            update_candidate_window_pos_console(_ctx)

    @staticmethod
    def add_key_map_item():
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
            'Screen Editing', space_type='EMPTY', region_type='WINDOW')
        km.keymap_items.new(
            WIRE_OT_fix_ime_input_watcher.bl_idname,
            type='MOUSEMOVE',
            value='ANY')

    @staticmethod
    def remove_key_map_item():
        WIRE_OT_fix_ime_input_watcher._windows.clear()
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
            'Screen Editing', space_type='EMPTY', region_type='WINDOW')
        for _kmi in reversed(km.keymap_items):
            if _kmi.idname == WIRE_OT_fix_ime_input_watcher.bl_idname:
                km.keymap_items.remove(_kmi)

class WIRE_PT_text_editor_info(bpy.types.Panel):
    bl_idname = 'WIRE_PT_text_editor_info'
    bl_label = "信息（仅用于测试）"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Text'
    '''
    用于显示文本编辑器的光标的位置，仅测试用
    '''
    _registered = False

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        space = cast(bpy.types.SpaceTextEditor, context.space_data)
        region = context.region
        window = context.window
        text = space.text

        # offset 的原点在区块左下角
        offset_x, offset_y = space.region_location_from_cursor(text.current_line_index, text.current_character)

        client_x = region.x + offset_x
        client_y = window.height - (region.y + offset_y)

        layout.label(text='光标位置（相对区块左下角）：%d, %d' % (offset_x, offset_y))
        layout.label(text='光标位置（相对窗口左上角）：%d, %d' % (client_x, client_y))

        pass


TEXT_HT_header_extend_appended = False
CONSOLE_HT_header_extend_appended = False

def TEXT_HT_header_extend(self: bpy.types.Header, context: bpy.types.Context):
    layout = self.layout

    prefs = get_prefs(context)

    watcher: WIRE_OT_fix_ime_input_watcher = None
    if context.window in watchers:
        watcher = watchers[context.window]

    active = (prefs.use_fix_ime_state and prefs.use_fix_ime_input)

    row = layout.row()
    row.active = active

    _icon = 'PROP_OFF'
    if active and prefs.use_fix_ime_input_text_editor:
        if watcher and watcher._space == context.space_data:
            _icon = 'PROP_ON'
        else:
            _icon = 'PROP_CON'

    row.prop(prefs, 'use_fix_ime_input_text_editor', text="", icon=_icon, emboss=False,
        invert_checkbox=True if prefs.use_fix_ime_input_text_editor else False)

def CONSOLE_HT_header_extend(self: bpy.types.Header, context: bpy.types.Context):
    layout = self.layout

    prefs = get_prefs(context)

    watcher: WIRE_OT_fix_ime_input_watcher = None
    if context.window in watchers:
        watcher = watchers[context.window]

    active = (prefs.use_fix_ime_state and prefs.use_fix_ime_input)

    layout.separator_spacer()

    row = layout.row()
    row.active = active

    _icon = 'PROP_OFF'
    if active and prefs.use_fix_ime_input_console:
        if watcher and watcher._space == context.space_data:
            _icon = 'PROP_ON'
        else:
            _icon = 'PROP_CON'

    row.prop(prefs, 'use_fix_ime_input_console', text="", icon=_icon, emboss=False,
        invert_checkbox=True if prefs.use_fix_ime_input_console else False)

def register():
    global TEXT_HT_header_extend_appended
    global CONSOLE_HT_header_extend_appended

    bpy.utils.register_class(WIRE_FIX_Preferences)

    bpy.utils.register_class(WIRE_OT_fix_ime_input_font_edit)
    bpy.utils.register_class(WIRE_OT_fix_ime_input_text_editor)
    bpy.utils.register_class(WIRE_OT_fix_ime_input_console)
    bpy.utils.register_class(WIRE_OT_fix_ime_input_watcher)

    WIRE_OT_fix_ime_input_watcher.add_key_map_item()

    native.dll_load()

    prefs = get_prefs(bpy.context)

    use_debug_update({
        'use_debug': int(prefs.use_debug),
    }, bpy.context)

    native.init()

    native.use_hook(True)

    use_fix_ime_update({
        'use_fix_ime_state': int(prefs.use_fix_ime_state),
        'use_fix_ime_input': int(prefs.use_fix_ime_input),
    }, bpy.context)

    use_header_extned({
        'use_header_extend_text_editor': int(prefs.use_header_extend_text_editor),
        'use_header_extend_console': int(prefs.use_header_extend_console),
    }, bpy.context)

    pass

def unregister():
    global TEXT_HT_header_extend_appended
    global CONSOLE_HT_header_extend_appended

    native.use_fix_ime_input(False)
    native.use_fix_ime_state(False)

    native.use_hook(False)

    native.dll_unload()

    if CONSOLE_HT_header_extend_appended:
        bpy.types.TEXT_HT_header.remove(CONSOLE_HT_header_extend)
        CONSOLE_HT_header_extend_appended = False
    if TEXT_HT_header_extend_appended:
        bpy.types.TEXT_HT_header.remove(TEXT_HT_header_extend)
        TEXT_HT_header_extend_appended = False

    WIRE_OT_fix_ime_input_watcher.remove_key_map_item()

    if WIRE_PT_text_editor_info._registered:
        bpy.utils.unregister_class(WIRE_PT_text_editor_info)
        WIRE_PT_text_editor_info._registered = False

    bpy.utils.unregister_class(WIRE_OT_fix_ime_input_watcher)
    bpy.utils.unregister_class(WIRE_OT_fix_ime_input_console)
    bpy.utils.unregister_class(WIRE_OT_fix_ime_input_text_editor)
    bpy.utils.unregister_class(WIRE_OT_fix_ime_input_font_edit)

    bpy.utils.unregister_class(WIRE_FIX_Preferences)

    pass
