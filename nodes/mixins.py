import bpy
from bpy.types import Node, NodeReroute
from ..consts import IO_COLOR, FILTER_COLOR, ERROR_COLOR, DEBUG_COLOR, FUNCTION_COLOR, FLOW_COLOR, TRANSFORM_COLOR


def get_input_socket_data(socket, context) -> list:
    obs = []

    if socket and socket.is_linked:
        link = socket.links[0]
        upstream_node = link.from_socket.node
        if isinstance(upstream_node, WFNode):
            # For function nodes pulling its output data triggers execution
            if isinstance(upstream_node, WFFunctionNode):
                obs = upstream_node.execute(context)
            # For Flow nodes the execution must be explicit through a flow socket
            else:
                obs = upstream_node["cached_data"]
        elif isinstance(upstream_node, NodeReroute):
            for i in range(0, len(upstream_node.inputs)):
                obs.extend(get_input_socket_data(upstream_node.inputs[i], context))

    return obs


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

    def get_input_socket_data(self, socket, context) -> list[bpy.types.Object]:
        return get_input_socket_data(socket, context)

    def get_input_data(self, context) -> list[bpy.types.Object]:
        return []

    def execute(self, context) -> list[bpy.types.Object]:
        return []


class WFFlowNode(WFNode, Node):

    def init(self, context):
        super().init(context)
        self.color = FLOW_COLOR
        self["cached_data"] = []

    def get_input_data(self, context) -> list[bpy.types.Object]:
        obs = []

        for i in range(1, len(self.inputs)):
            obs.extend(get_input_socket_data(self.inputs[i], context))

        return obs

    def cleanup(self):
        self["cached_data"] = []


class WFInFlowNode(WFFlowNode):
    """Flow node that doesn't have output flow socket.
When triggered through a flow input socket it will evaluate and end the graph execution"""

    def init(self, context):
        super().init(context)
        from ..sockets.flow_socket import WFFlowSocket
        WFFlowSocket.create(self.inputs)


class WFOutFlowNode(WFFlowNode):
    """Flow node that doesn't have input flow socket.
When it's run, it will evaluate and then synchronously trigger one of its flow outputs, continuing execution of the graph"""

    def init(self, context):
        super().init(context)
        from ..sockets.flow_socket import WFFlowSocket
        WFFlowSocket.create(self.outputs)


class WFInOutFlowNode(WFFlowNode):
    """Flow node that has both input and output flow sockets.
When its flow input is triggered, it will evaluate and then synchronously trigger one of its flow outputs,
continuing execution of the graph"""

    def init(self, context):
        super().init(context)
        from ..sockets.flow_socket import WFFlowSocket
        WFFlowSocket.create(self.inputs)
        WFFlowSocket.create(self.outputs)


class WFRunNode(WFOutFlowNode):

    def init(self, context):
        super().init(context)
        self.color = IO_COLOR

    def draw_buttons(self, context, layout):
        op = layout.operator("wf.run_workflow_step", icon='PLAY', text="")
        op.node_name = self.name


class WFFunctionNode(WFNode, Node):
    """These nodes are evaluated on demand when an output of theirs is required.
These are most often used for mathematical operators, or for queries of context or state."""

    def init(self, context):
        super().init(context)
        self.color = FUNCTION_COLOR

    def get_input_data(self, context) -> list[bpy.types.Object]:
        obs = []

        for i in range(0, len(self.inputs)):
            obs.extend(get_input_socket_data(self.inputs[i], context))

        return obs

    def execute(self, context) -> list[bpy.types.Object]:
        return self.get_input_data(context)


class WFInFunctionNode(WFFunctionNode):
    def init(self, context):
        super().init(context)
        self.inputs.new("WFObjectsSocket", "in")


class WFOutFunctionNode(WFFunctionNode):
    def init(self, context):
        super().init(context)
        self.outputs.new("WFObjectsSocket", "out")


class WFInOutFunctionNode(WFFunctionNode):
    def init(self, context):
        super().init(context)
        self.inputs.new("WFObjectsSocket", "in")
        self.outputs.new("WFObjectsSocket", "out")


class WFInputNode(WFOutFunctionNode):
    """These nodes are evaluated on demand when an output of theirs is required.
They don't have any input, they are data providers only"""

    def init(self, context):
        super().init(context)
        self.color = FUNCTION_COLOR


class WFFilterNode(WFInOutFunctionNode):

    def init(self, context):
        super().init(context)
        self.color = FILTER_COLOR


class WFDebugNode(WFInOutFlowNode):

    def init(self, context):
        super().init(context)
        self.color = DEBUG_COLOR
        self.inputs.new("WFObjectsSocket", "in")
        self.outputs.new("WFObjectsSocket", "out")


def filepath_update(self, filepath):
    if self.filepath:
        self.color = IO_COLOR
    else:
        self.color = ERROR_COLOR


class WFExportNode(WFInFlowNode):

    filepath: bpy.props.StringProperty(
        name="Output File",
        description="Choose the output file path",
        default="",
        subtype="FILE_PATH",
        update=filepath_update
    )

    def init(self, context):
        super().init(context)
        self.color = IO_COLOR
        self.inputs.new("WFObjectsSocket", "in")

    def draw_buttons(self, context, layout):
        layout.label(text="Default export properties will be used")
        layout.prop(self, "filepath")


class WFTransformNode(WFInOutFlowNode):

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR
        self.inputs.new("WFObjectsSocket", "in")
        self.outputs.new("WFObjectsSocket", "out")
