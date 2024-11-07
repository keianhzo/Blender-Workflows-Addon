import bpy
from .mixins import WFTransformNode


class WFNodeAddPrefixToName(WFTransformNode):
    bl_label = "Add Prefix"
    bl_description = """Adds a prefix to the beginning of an object's name
    - in: One or more objects sets
    - out: All input objects"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "prefix")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)
        prefix = get_input_socket_data(self.inputs["prefix"], context)
        for ob in obs:
            ob.name = prefix + ob.name
            if hasattr(ob, "data") and ob.data:
                ob.data.name = ob.name

        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeAddSuffixToName(WFTransformNode):
    bl_label = "Add Suffix"
    bl_description = """Adds a suffix to the end of an object's name
    - in: One or more objects sets
    - out: All input objects"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "suffix")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)
        suffix = get_input_socket_data(self.inputs["suffix"], context)
        for ob in obs:
            ob.name = ob.name + suffix
            if hasattr(ob, "data") and ob.data:
                ob.data.name = ob.name

        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeTranslateToPosition(WFTransformNode):
    bl_label = "Translate To Position"
    bl_description = """Translates an object to a new position. The position can be in world or local space
    - in: One or more objects sets
    - out: All input objects"""

    relative: bpy.props.BoolProperty(default=False, name="Relative")

    position: bpy.props.FloatVectorProperty(
        name="Position", description="An offset or world position to use for translation",
        unit='LENGTH',
        subtype="XYZ",
        default=(0.0, 0.0, 0.0))

    def draw_buttons(self, context, layout):
        layout.prop(self, "relative")
        layout.label(text="Position:")
        col = layout.column()
        col.prop(self, "position", index=0, text="X")
        col.prop(self, "position", index=1, text="Y")
        col.prop(self, "position", index=2, text="Z")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        context.view_layer.objects.active = last_ob

        if self.relative:
            last_ob.location += self.position
        else:
            last_ob.matrix_world.translation = self.position

        set_output_socket_data(self.outputs["objects"], [last_ob], context)
