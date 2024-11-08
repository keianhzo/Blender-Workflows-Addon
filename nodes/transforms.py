import bpy
from .mixins import WFTransformNode


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

        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeTranslateToObjectPosition(WFTransformNode):
    bl_label = "Translate To Object Position"
    bl_description = """Translates an object to another object's position
    - in: One or more objects sets
    - out: All input objects"""

    target: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object
    )

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "target")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        context.view_layer.objects.active = last_ob

        last_ob.matrix_world.translation = self.target.matrix_world.translation

        set_output_socket_data(self.outputs["objects"], obs, context)
