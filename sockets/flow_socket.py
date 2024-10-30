
from bpy.types import NodeSocketStandard


class WFFlowSocket(NodeSocketStandard):
    bl_idname = "WFFlowSocket"
    bl_label = "Workflows Flow"

    def draw(self, context, layout, node, text):
        if text == "flow":
            layout.label(text="▶")
        elif self.is_output:
            layout.label(text=text + " ▶")
        else:
            layout.label(text="▶ " + text)

    def draw_color(self, context, node):
        return (1.0, 1.0, 1.0, 1.0)

    @classmethod
    def create(cls, target, name="flow"):
        socket = target.new(cls.bl_rna.name, name)
        socket.display_shape = "DIAMOND"
        socket.link_limit = 0
        # if socket.is_output:
        #     socket.link_limit = 0
        # else:
        #     socket.link_limit = 1
