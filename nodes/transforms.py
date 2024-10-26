import bpy
from .mixins import WFActionNode
from ..consts import TRANSFORM_COLOR, ERROR_COLOR


def get_modifiers_types(self, context):
    mods = []

    obs = self.get_input_data()
    for ob in obs:
        for mod in ob.modifiers:
            maxid = -1
            id = -1
            found = False
            for idrec in self.mods_types_store:
                id = idrec[0]
                if id > maxid:
                    maxid = id
                if idrec[1] == mod.type:
                    found = True
                    break

            if not found:
                self.mods_types_store.append((maxid+1, mod.type))

            # AMENDED CODE - include the ID
            mods.append((mod.type, mod.type, mod.type, id))

    return mods


class WFNodeApplyModifierType(WFActionNode):
    bl_label = "Apply Modifier By Type"
    bl_width_default = 200

    mods_types_store = []

    modifier: bpy.props.EnumProperty(
        name="",
        description="Modifier",
        items=get_modifiers_types,
        default=0
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "modifier")

    def get_input_data(self) -> list[bpy.types.Object]:
        return super().get_input_data()

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        for ob in obs:
            for mod in ob.modifiers:
                bpy.context.view_layer.objects.active = ob
                if mod.type in self.modifier:
                    bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


def get_modifiers_names(self, context):
    mods = []

    obs = self.get_input_data()
    for ob in obs:
        for mod in ob.modifiers:
            maxid = -1
            id = -1
            found = False
            for idrec in self.mods_names_store:
                id = idrec[0]
                if id > maxid:
                    maxid = id
                if idrec[1] == mod.name:
                    found = True
                    break

            if not found:
                self.mods_names_store.append((maxid+1, mod.name))

            # AMENDED CODE - include the ID
            mods.append((mod.name, mod.name, mod.name, id))

    return mods


class WFNodeApplyModifierName(WFActionNode):
    bl_label = "Apply Modifier By Name"

    mods_names_store = []

    modifier: bpy.props.EnumProperty(
        name="",
        description="Modifier",
        items=get_modifiers_names,
        default=0
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "modifier")

    def get_input_data(self) -> list[bpy.types.Object]:
        return super().get_input_data()

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        for ob in obs:
            for mod in ob.modifiers:
                bpy.context.view_layer.objects.active = ob
                if mod.name in self.modifier:
                    bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


class WFNodeApplyAllModifiers(WFActionNode):
    bl_label = "Apply All Modifiers"

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        for ob in obs:
            for mod in ob.modifiers:
                bpy.context.view_layer.objects.active = ob
                bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


def string_update(self, appendix):
    if self.filter:
        self.color = TRANSFORM_COLOR
    else:
        self.color = ERROR_COLOR


class WFNodeAddPrefixToName(WFActionNode):
    bl_label = "Add Prefix To Objects Names"
    bl_width_default = 200

    prefix: bpy.props.StringProperty(
        name="Prefix",
        description="String to prepend",
        default="",
        update=string_update
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "prefix")

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        for ob in obs:
            ob.name = self.prefix + ob.name

        return obs


class WFNodeAddSuffixToName(WFActionNode):
    bl_label = "Add Suffix To Objects Names"
    bl_width_default = 200

    suffix: bpy.props.StringProperty(
        name="Suffix",
        description="String to append",
        default="",
        update=string_update
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "suffix")

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        for ob in obs:
            ob.name = ob.name + self.suffix

        return obs


class AddObjectSocketOperator(bpy.types.Operator):
    bl_idname = "wf.add_object_socket"
    bl_label = "Add Object Socket"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Adds a new object socket to the node"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        node = context.node
        node.inputs.new("WFObjectsSocket", "in")
        return {'FINISHED'}


class RemoveObjectSocketOperator(bpy.types.Operator):
    bl_idname = "wf.remove_object_socket"
    bl_label = "Remove Object Socket"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Removes the last added socket from the node"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        node = context.node
        if len(node.inputs) > 1:
            node.inputs.remove(node.inputs[len(node.inputs) - 1])
        return {'FINISHED'}


class WFNodeJoinObjects(WFActionNode):
    bl_label = "Join Objects Geometry"
    bl_width_default = 160

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        bpy.context.view_layer.objects.active = last_ob
        bpy.ops.object.join()

        return [last_ob]


class WFNodeTranslateToPosition(WFActionNode):
    bl_label = "Translate To Position"

    relative: bpy.props.BoolProperty(default=False, name="Relative")

    position: bpy.props.FloatVectorProperty(
        name="Position", description="An offset or world position to use for translation",
        unit='LENGTH',
        subtype="XYZ",
        default=(0.0, 0.0, 0.0))

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "relative")
        layout.label(text="Position:")
        col = layout.column()
        col.prop(self, "position", index=0, text="X")
        col.prop(self, "position", index=1, text="Y")
        col.prop(self, "position", index=2, text="Z")

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        bpy.context.view_layer.objects.active = last_ob

        if self.relative:
            last_ob.location += self.position
        else:
            last_ob.location = self.position

        return [last_ob]


class WFNodeTranslateToObjectPosition(WFActionNode):
    bl_label = "Translate To Object Position"

    target: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "target")

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        bpy.context.view_layer.objects.active = last_ob

        last_ob.location = self.target.location

        return [last_ob]
