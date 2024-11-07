import bpy
from .mixins import WFTransformNode


class WFNodeInstancesMakeReal(WFTransformNode):
    bl_label = "Instances Make Real"
    bl_description = """Make instances real
    - in: One or more objects sets
    - out: All input objects and the created instances
Note: "Make single user" is applied on the object data before applying the modifier
      This node won't work correctly with upstream nodes that change the object set like filter nodes"""
    bl_width_default = 200

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        for ob in obs:
            ob.select_set(True)
            context.view_layer.objects.active = ob
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)

        bpy.ops.object.duplicates_make_real()

        obs.extend(context.selected_objects)
        set_output_socket_data(self.outputs["objects"], obs, context)
