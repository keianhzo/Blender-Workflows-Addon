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

    filter: bpy.props.StringProperty(
        name="Starts With",
        description="String to filter",
        default="",
        update=filter_update
    )

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "filter")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = super().execute(context)

        obs = [ob for ob in obs if ob.name.startswith(self.filter)]

        return obs


class WFNodeFilterEndsWith(WFFilterNode):
    bl_label = "Ends With"
    bl_description = """Filters the input objects set and only outputs those ending with the given string
    - in: One or more objects sets
    - out: The objects whose name ends with the given string"""
    bl_width_default = 300

    filter: bpy.props.StringProperty(
        name="Ends With",
        description="String to filter",
        default="",
        update=filter_update
    )

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "filter")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = super().execute(context)

        obs = [ob for ob in obs if ob.name.endswith(self.filter)]

        return obs


class WFNodeFilterContains(WFFilterNode):
    bl_label = "Contains"
    bl_description = """Filters the input objects set and only outputs those containing the give string
    - in: One or more objects sets
    - out: The objects whose name contains the given string"""
    bl_width_default = 200

    filter: bpy.props.StringProperty(
        name="Contains",
        description="String to filter",
        default="",
        update=filter_update
    )

    def init(self, context):
        super().init(context)
        self.outputs.new("WFObjectsSocket", "out")

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "filter")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = super().execute(context)

        obs = [ob for ob in obs if ob.name in self.filter]

        return obs


class WFNodeFilterRegex(WFFilterNode):
    bl_label = "Regex"
    bl_description = """Filters the input objects set and only outputs those matching the given regular expression
    - in: One or more objects sets
    - out: The objects whose name matches the given regular expression"""
    bl_width_default = 200

    filter: bpy.props.StringProperty(
        name="Regex",
        description="String to filter",
        default="",
        update=filter_update
    )

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "filter")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = super().execute(context)

        import re
        obs = [ob for ob in obs if re. search(self.filter, ob.name)]

        return obs


class WFNodeCombineSets(WFFilterNode):
    bl_label = "Combine Sets"
    bl_description = """Add all the input objects to the output set
    - in: One or more objects sets
    - out: The combined objects set"""

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = super().execute(context)

        return obs
    
class WFNodeRemoveFromSet(WFFilterNode):
    bl_label = "Remove From Set"
    bl_description = """Removes the given input objects from the first input set
    - in: One or more objects sets (First one is taken as main and the rest are removed)
    - out: The resulting object set"""

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = set()

        if self.cached_data:
            obs = self.cached_data
        else:
            if len(self.inputs) > 0:
                data = self.execute_input_socket(self.inputs[0], context)
                obs.update(data)

                excl = set()
                if len(self.inputs) > 1:
                    for i in range(1, len(self.inputs)):
                        data = self.execute_input_socket(self.inputs[i], context)
                        excl.update(data)

                    obs -= excl
                    self.cached_data = obs

        return list(obs)
