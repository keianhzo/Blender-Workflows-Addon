import bpy
from bpy.types import Node, NodeReroute, NodeGroupInput, NodeGroupOutput
from ..consts import IO_COLOR, FILTER_COLOR, ERROR_COLOR, DEBUG_COLOR, FUNCTION_COLOR, FLOW_COLOR, TRANSFORM_COLOR


def get_input_socket_data(socket, context, group_nodes=[]) -> list:
    from .group import WFNodeGroup
    if socket and socket.is_linked:
        link = socket.links[0]
        # TODO handle from_socket_node being a NodeGroupInput/Output
        upstream_node = link.from_socket.node
        from ..sockets.objects_socket import WFObjectsSocket
        if isinstance(upstream_node, WFNode) and isinstance(socket, WFObjectsSocket):
            # For function nodes pulling its output data triggers execution
            if isinstance(upstream_node, WFFunctionNode):
                return upstream_node.execute(context)
            # For Flow nodes the execution must be explicit through a flow socket
            # so we just get whatever was cached from the last execution if any
            else:
                return [item.ob for item in upstream_node.cache]

        elif isinstance(upstream_node, NodeReroute):
            for i in range(0, len(upstream_node.inputs)):
                return get_input_socket_data(upstream_node.inputs[i], context), group_nodes

        elif isinstance(upstream_node, NodeGroupInput):
            if len(group_nodes) > 0:
                group_node = group_nodes.pop()
                object_socket = next(
                    (group_socket for group_socket in group_node.inputs if group_socket.name == socket.name),
                    None)
                return get_input_socket_data(object_socket, context, group_nodes)

        elif isinstance(upstream_node, NodeGroupOutput):
            input_socket = next(
                (input_socket for input_socket in upstream_node.inputs if upstream_node.name == socket.name),
                None)
            if input_socket and input_socket.is_linked:
                link = input_socket.links[0]
                return get_input_socket_data(link.from_socket, context, group_nodes)

        elif isinstance(upstream_node, WFNodeGroup):
            output_node = next((tree_node for tree_node in upstream_node.node_tree.nodes
                                if isinstance(tree_node, NodeGroupOutput)),
                               None)

            if output_node:
                object_socket = next(
                    (output_socket for output_socket in output_node.inputs if output_socket.name == socket.name),
                    None)
                if object_socket:
                    group_nodes.append(upstream_node)
                    return get_input_socket_data(object_socket, context, group_nodes)

        else:
            return None

    else:
        return socket.default_value if socket else None


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

    def get_object_input_data(self, context) -> list[bpy.types.Object]:
        return []

    def execute(self, context) -> list[bpy.types.Object]:
        return []


class ObjectsCache(bpy.types.PropertyGroup):
    ob: bpy.props.PointerProperty(type=bpy.types.Object)


class WFFlowNode(WFNode, Node):

    cache: bpy.props.CollectionProperty(type=ObjectsCache)

    def init(self, context):
        super().init(context)
        self.color = FLOW_COLOR

    def get_object_input_data(self, context) -> list[bpy.types.Object]:
        from ..sockets.objects_socket import WFObjectsSocket
        objects_socket = next((socket for socket in self.inputs
                               if isinstance(socket, WFObjectsSocket)), None)

        return get_input_socket_data(objects_socket, context) or []

    def cleanup(self):
        self.cache.clear()


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
        op = layout.operator("wf.run_workflow", icon='PLAY', text="")
        op.node_name = self.name


class WFFunctionNode(WFNode, Node):
    """These nodes are evaluated on demand when an output of theirs is required.
These are most often used for mathematical operators, or for queries of context or state."""

    def init(self, context):
        super().init(context)
        self.color = FUNCTION_COLOR

    def get_object_input_data(self, context) -> list[bpy.types.Object]:
        from ..sockets.objects_socket import WFObjectsSocket
        objects_socket = next((socket for socket in self.inputs
                               if isinstance(socket, WFObjectsSocket)), None)

        if objects_socket:
            return get_input_socket_data(objects_socket, context)

        return []

    def execute(self, context) -> list[bpy.types.Object]:
        return self.get_object_input_data(context)


class WFInFunctionNode(WFFunctionNode):
    def init(self, context):
        super().init(context)
        self.inputs.new("WFObjectsSocket", "objects")


class WFOutFunctionNode(WFFunctionNode):
    def init(self, context):
        super().init(context)
        self.outputs.new("WFObjectsSocket", "objects")


class WFInOutFunctionNode(WFFunctionNode):
    def init(self, context):
        super().init(context)
        self.inputs.new("WFObjectsSocket", "objects")
        self.outputs.new("WFObjectsSocket", "objects")


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
        self.inputs.new("WFObjectsSocket", "objects")
        self.outputs.new("WFObjectsSocket", "objects")


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
        self.inputs.new("WFObjectsSocket", "objects")

    def draw_buttons(self, context, layout):
        layout.label(text="Default export properties will be used")
        layout.prop(self, "filepath")


class WFTransformNode(WFInOutFlowNode):

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR
        self.inputs.new("WFObjectsSocket", "objects")
        self.outputs.new("WFObjectsSocket", "objects")


CLASSES = [
    ObjectsCache,
    WFFlowNode,
    WFFunctionNode
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
