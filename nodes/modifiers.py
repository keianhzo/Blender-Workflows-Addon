import bpy
from .mixins import WFTransformNode
from ..consts import TRANSFORM_COLOR, ERROR_COLOR


def get_modifiers_types(self, context):
    return [(item.identifier, item.name, item.name) for item in bpy.types.Modifier.bl_rna.properties['type'].enum_items]


class WFNodeApplyModifierType(WFTransformNode):
    bl_label = "Apply Modifier By Type"
    bl_description = """Applies the selected modifier to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier
      This node won't work correctly with upstream nodes that change the object set like filter nodes"""
    bl_width_default = 200

    modifier: bpy.props.EnumProperty(
        name="",
        description="Modifier",
        items=get_modifiers_types,
        default=0
    )

    def draw_buttons(self, context, layout):
        layout.prop(self, "modifier")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type in self.modifier:
                        ob.select_set(True)
                        context.view_layer.objects.active = ob
                        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeApplyModifierName(WFTransformNode):
    bl_label = "Apply Modifier By Name"
    bl_description = """Applies the selected modifier to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier
This node won't work correctly with upstream nodes that change the object set like filter nodes"""

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "name")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    name = get_input_socket_data(self.inputs["name"], context)
                    if mod.name == name:
                        ob.select_set(True)
                        context.view_layer.objects.active = ob
                        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeApplyAllModifiers(WFTransformNode):
    bl_label = "Apply All Modifiers"
    bl_description = """Applies all modifiers to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier"""

    def init(self, context):
        super().init(context)

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    ob.select_set(True)
                    context.view_layer.objects.active = ob
                    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                    bpy.ops.object.modifier_apply(modifier=mod.name)

        set_output_socket_data(self.outputs["objects"], obs, context)


def string_update(self, string):
    if string:
        self.color = TRANSFORM_COLOR
    else:
        self.color = ERROR_COLOR
