import bpy
from bpy.types import Node
from ..consts import IO_COLOR, FILTER_COLOR, ERROR_COLOR


class WFNode():
    bl_label = "Workflows Graph Node"
    bl_icon = "NODE"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'WFNodeTree'

    def init(self, context):
        self.use_custom_color = True

    def draw_buttons(self, context, layout):
        pass

    def get_input_data(self) -> list[bpy.types.Object]:
        obs = []

        for i in range(0, len(self.inputs)):
            in_socket = self.inputs[i]
            if in_socket.is_linked:
                link = in_socket.links[0]
                upstream_node = link.from_socket.node
                obs.extend(upstream_node.get_input_data())

        return obs

    def execute(self) -> list[bpy.types.Object]:
        obs = []

        for i in range(0, len(self.inputs)):
            in_socket = self.inputs[i]
            if in_socket.is_linked:
                link = in_socket.links[0]
                upstream_node = link.from_socket.node
                upstream_data = upstream_node.execute()
                upstream_data = [ob for ob in upstream_data if ob not in obs]
                obs.extend(upstream_data)

        return obs


class WFActionNode(WFNode, Node):

    def init(self, context):
        super().init(context)
        self.inputs.new("WFObjectsSocket", "in")
        self.outputs.new("WFObjectsSocket", "out")

    def draw_buttons(self, context, layout):
        pass


class WFFilterNode(WFActionNode):

    def init(self, context):
        super().init(context)
        self.color = FILTER_COLOR


class WFInputNode(WFNode, Node):
    def init(self, context):
        super().init(context)
        self.color = IO_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "target")


def filepath_update(self, filepath):
    if self.filepath:
        self.color = IO_COLOR
    else:
        self.color = ERROR_COLOR


class WFOutputNode(WFNode, Node):

    def init(self, context):
        super().init(context)
        self.color = IO_COLOR


class WFExportNode(WFOutputNode):

    filepath: bpy.props.StringProperty(
        name="Output File",
        description="Choose the output file path",
        default="",
        subtype="FILE_PATH",
        update=filepath_update
    )

    def init(self, context):
        super().init(context)
        self.inputs.new("WFObjectsSocket", "in")

    def draw_buttons(self, context, layout):
        layout.label(text="Default export properties will be used")
        layout.prop(self, "filepath")
        layout.context_pointer_set('target', self)
        layout.operator("wf.run_workflow", icon='PLAY', text="")
