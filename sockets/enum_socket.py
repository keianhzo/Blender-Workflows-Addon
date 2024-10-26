import bpy
from bpy.types import NodeSocketStandard


def get_choices(self, context):
    return [(choice.value, choice.text, "") for choice in self.choices]


class WFEnumSocketChoice(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty()
    value: bpy.props.StringProperty()


class WFEnumSocket(NodeSocketStandard):
    bl_label = "String Choice"

    default_value: bpy.props.EnumProperty(
        name="",
        items=get_choices
    )

    choices: bpy.props.CollectionProperty(type=WFEnumSocketChoice)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        return (0.4, 0.7, 1.0, 1.0)
