import bpy
from .mixins import WFFilterNode


class WFNodeCombineSets(WFFilterNode):
    bl_label = "Combine Sets"
    bl_description = """Add all the input objects to the output set
    - in: One or more objects sets
    - out: The combined objects set"""

    def init(self, context):
        super().init(context)
        self.inputs["objects"].link_limit = 0

    def execute(self, context):
        from .mixins import get_all_input_socket_data, set_output_socket_data
        obs = list(set(get_all_input_socket_data(self.inputs["objects"], context)))

        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeRemoveFromSet(WFFilterNode):
    bl_label = "Remove From Set"
    bl_description = """Removes the given input objects from the first input set
    - in: One or more objects sets (First one is taken as main and the rest are removed)
    - out: The resulting object set"""

    def init(self, context):
        super().init(context)
        self.inputs["objects"].link_limit = 0
        self.inputs.new("WFObjectsSocket", "exclude")
        self.inputs["exclude"].link_limit = 0

    def execute(self, context):
        from .mixins import get_all_input_socket_data, set_output_socket_data
        obs = list(set(get_all_input_socket_data(self.inputs["objects"], context)))
        excl = get_all_input_socket_data(self.inputs["exclude"], context)
        for ex_ob in excl:
            obs.remove(ex_ob)

        set_output_socket_data(self.outputs["objects"], list(obs), context)
