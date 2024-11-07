import bpy
from .mixins import WFFilterNode
from ..consts import FILTER_COLOR, ERROR_COLOR


def filter_update(self, filepath):
    if self.filter:
        self.color = FILTER_COLOR
    else:
        self.color = ERROR_COLOR


class WFNodeFilterStartsWith(WFFilterNode):
    bl_label = "Starts With"
    bl_description = """Filters the input objects set and only outputs those starting with the given string
    - in: One or more objects sets
    - out: The objects whose name starts with the given string"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "filter")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)
        filter = get_input_socket_data(self.inputs["filter"], context)
        obs = [ob for ob in obs if ob.name.startswith(filter)]
        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeFilterEndsWith(WFFilterNode):
    bl_label = "Ends With"
    bl_description = """Filters the input objects set and only outputs those ending with the given string
    - in: One or more objects sets
    - out: The objects whose name ends with the given string"""
    bl_width_default = 300

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "filter")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)
        filter = get_input_socket_data(self.inputs["filter"], context)
        obs = [ob for ob in obs if ob.name.endswith(filter)]
        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeFilterContains(WFFilterNode):
    bl_label = "Contains"
    bl_description = """Filters the input objects set and only outputs those containing the give string
    - in: One or more objects sets
    - out: The objects whose name contains the given string"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "filter")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)
        filter = get_input_socket_data(self.inputs["filter"], context)
        obs = [ob for ob in obs if ob.name in filter]
        set_output_socket_data(self.outputs["objects"], obs, context)


class WFNodeFilterRegex(WFFilterNode):
    bl_label = "Regex"
    bl_description = """Filters the input objects set and only outputs those matching the given regular expression
    - in: One or more objects sets
    - out: The objects whose name matches the given regular expression"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "filter")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)
        filter = get_input_socket_data(self.inputs["filter"], context)
        import re
        obs = [ob for ob in obs if re. search(filter, ob.name)]
        set_output_socket_data(self.outputs["objects"], obs, context)


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
        obs = get_all_input_socket_data(self.inputs["objects"], context)

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
        obs = set(get_all_input_socket_data(self.inputs["objects"], context))
        excl = set(get_all_input_socket_data(self.inputs["exclude"], context))
        obs -= excl

        set_output_socket_data(self.outputs["objects"], list(obs), context)
