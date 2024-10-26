import bpy
from bpy.types import NodeSocketStandard


class WFObjectsSocket(NodeSocketStandard):
    bl_idname = "WFObjectsSocket"
    bl_label = "Workflows Objects"

    if bpy.app.version < (4, 0, 0):
        def draw(self, context, layout):
            layout.alignment = 'RIGHT' if self.is_output else 'LEFT'
            layout.label(text=self.name)

            if not self.is_output and self == self.node.inputs[len(self.node.inputs) - 1]:
                row = layout.row()
                row.context_pointer_set("node", self.node)
                row.operator("wf.add_object_socket", icon='ADD', text="")
                if len(self.node.inputs) > 1:
                    row.operator("wf.remove_object_socket", icon='REMOVE', text="")

        def draw_color(self, context):
            return (0.2, 1.0, 0.2, 1.0)
    else:
        def draw(self, context, layout, node, text):
            layout.alignment = 'RIGHT' if self.is_output else 'LEFT'
            layout.label(text=self.name)

            if not self.is_output and self == self.node.inputs[len(self.node.inputs) - 1]:
                row = layout.row()
                row.context_pointer_set("node", self.node)
                row.operator("wf.add_object_socket", icon='ADD', text="")
                if len(self.node.inputs) > 1:
                    row.operator("wf.remove_object_socket", icon='REMOVE', text="")

        def draw_color(self, context, node):
            return (0.2, 1.0, 0.2, 1.0)
