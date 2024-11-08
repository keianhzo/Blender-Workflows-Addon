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
