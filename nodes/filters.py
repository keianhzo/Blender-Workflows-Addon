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

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        obs = [ob for ob in obs if ob.name.startswith(self.filter)]

        return obs


class WFNodeFilterEndsWith(WFFilterNode):
    bl_label = "Ends With"
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

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        obs = [ob for ob in obs if ob.name.endswith(self.filter)]

        return obs


class WFNodeFilterContains(WFFilterNode):
    bl_label = "Contains"
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

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        obs = [ob for ob in obs if ob.name in self.filter]

        return obs


class WFNodeFilterRegex(WFFilterNode):
    bl_label = "Regex"
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

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        import re
        obs = [ob for ob in obs if re. search(self.filter, ob.name)]

        return obs


class WFNodeMerge(WFFilterNode):
    bl_label = "Merge"

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def execute(self) -> list[bpy.types.Object]:
        obs = super().execute()

        return obs
