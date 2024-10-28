import bpy
from bpy.types import Node, NodeReroute
from ..consts import IO_COLOR, FILTER_COLOR, ERROR_COLOR, DEBUG_COLOR


class WFNode():
    bl_label = "Workflows Graph Node"
    bl_icon = "NODE"
    cached_data = []

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'WFNodeTree'

    def init(self, context):
        self.use_custom_color = True
        self.cached_data = []

    def draw_buttons(self, context, layout):
        pass

    def get_input_socket_data(self, in_socket, context) -> list[bpy.types.Object]:
        obs = []

        if in_socket and in_socket.is_linked:
            link = in_socket.links[0]
            upstream_node = link.from_socket.node
            if isinstance(upstream_node, WFNode):
                obs = upstream_node.get_input_data(context)
            elif isinstance(upstream_node, NodeReroute):
                for i in range(0, len(upstream_node.inputs)):
                    obs.extend(self.get_input_data(upstream_node.inputs[i], context))
            
        return obs

    def get_input_data(self, context) -> list[bpy.types.Object]:
        obs = []

        for i in range(0, len(self.inputs)):
            data = self.get_input_socket_data(self.inputs[i], context)
            obs.extend(data)

        return obs
    
    def execute_input_socket(self, in_socket, context) -> list[bpy.types.Object]:
        obs = []

        if in_socket and in_socket.is_linked:
            link = in_socket.links[0]
            upstream_node = link.from_socket.node
            if isinstance(upstream_node, WFNode):
                obs = upstream_node.execute(context)
            elif isinstance(upstream_node, NodeReroute):
                for i in range(0, len(upstream_node.inputs)):
                    obs.extend(self.execute_input_socket(upstream_node.inputs[i], context))

        return obs

    def execute(self, context) -> list[bpy.types.Object]:
        obs = []

        if self.cached_data:
            obs = self.cached_data
        else:
            for i in range(0, len(self.inputs)):
                data = self.execute_input_socket(self.inputs[i], context)
                obs.extend(data)

            self.cached_data = obs

        return list(set(obs))
    
    def cleanup(self):
        self["cached_data"] = []


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

class WFDebugNode(WFActionNode):

    def init(self, context):
        super().init(context)
        self.color = DEBUG_COLOR


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
