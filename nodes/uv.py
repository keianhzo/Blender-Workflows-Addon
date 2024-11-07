import bpy
from .mixins import WFTransformNode


class WFNodeSetActiveUVMap(WFTransformNode):
    bl_label = "Sets Active UV Map"
    bl_description = """Changes the active uv map to the one selected for all input objects
    - uvmap: The UVMap to set as active
    - in: One or more objects sets
    - out: All input objects
Note: If the UV map doesn't exist in the object, the uv map is not changed"""
    bl_width_default = 160

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "name")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        for ob in obs:
            if hasattr(ob, "data") and ob.data:
                name = get_input_socket_data(self.inputs["name"], context)
                for uv in ob.data.uv_layers:
                    if uv.name in name:
                        uv.active = True

        set_output_socket_data(self.outputs["objects"], obs, context)
