import bpy
from bpy.types import Node, NodeReroute, NodeGroupInput, NodeGroupOutput
from ..consts import IO_COLOR, FILTER_COLOR, ERROR_COLOR, DEBUG_COLOR, TRANSFORM_COLOR


def set_output_socket_data(socket, data, context):
    from ..sockets.objects_socket import WFObjectsSocket
    if isinstance(socket, WFObjectsSocket):
        socket.default_value.clear()
        for ob in data:
            socket.default_value.add().value = ob
    else:
        socket.default_value = data

    socket.wf_has_cache = True


def get_input_socket_data(socket, context) -> list:
    from .group import WFNodeGroup
    if socket and socket.is_linked:
        link = socket.links[0]
        from_socket = link.from_socket
        from_node = from_socket.node

        if isinstance(from_node, WFNode) or isinstance(from_node, NodeGroupInput):
            if isinstance(from_node, WFNode) and not from_socket.wf_has_cache:
                from_node.execute(context)

            from ..sockets.objects_socket import WFObjectsSocket
            if isinstance(from_socket, WFObjectsSocket):
                return [item.value for item in from_socket.default_value]
            else:
                return from_socket.default_value

        elif isinstance(from_node, NodeReroute):
            for i in range(0, len(from_node.inputs)):
                return get_input_socket_data(from_node.inputs[i], context)

        elif isinstance(from_node, NodeGroupOutput):
            input_socket = next(
                (input_socket for input_socket in from_node.inputs if from_node.name == socket.name),
                None)
            if input_socket and input_socket.is_linked:
                link = input_socket.links[0]
                return get_input_socket_data(link.from_socket, context)

        elif isinstance(from_node, WFNodeGroup):
            for node in from_node.node_tree.nodes:
                for output in node.outputs:
                    output.wf_has_cache = False

            input_node = next((tree_node for tree_node in from_node.node_tree.nodes
                               if isinstance(tree_node, NodeGroupInput)),
                              None)

            for input_socket in from_node.inputs:
                data = get_input_socket_data(input_socket, context)
                input_node_socket = next(
                    (output_socket for output_socket in input_node.outputs
                     if output_socket.identifier == input_socket.identifier),
                    None)
                if input_node_socket:
                    set_output_socket_data(input_node_socket, data, context)

            output_node = next((tree_node for tree_node in from_node.node_tree.nodes
                                if isinstance(tree_node, NodeGroupOutput)),
                               None)

            if output_node:
                output_node_socket = next(
                    (output_socket for output_socket in output_node.inputs if output_socket.name == socket.name),
                    None)
                if output_node_socket:
                    return get_input_socket_data(output_node_socket, context)

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

    def execute(self, context):
        for socket in self.inputs:
            get_input_socket_data(socket, context)

    def cleanup(self):
        from ..sockets.objects_socket import WFObjectsSocket
        for socket in self.inputs:
            socket.wf_has_cache = False


class WFFunctionNode(Node, WFNode):

    def init(self, context):
        super().init(context)


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


class WFFilterNode(WFInOutFunctionNode):

    def init(self, context):
        super().init(context)
        self.color = FILTER_COLOR


class WFTransformNode(WFInOutFunctionNode):

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR


class WFInputNode(WFOutFunctionNode):
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


class WFOutputNode(WFInFunctionNode):

    def init(self, context):
        super().init(context)
        self.color = IO_COLOR


class WFDebugNode():

    def init(self, context):
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

    def draw_buttons(self, context, layout):
        layout.label(text="Default export properties will be used")
        layout.prop(self, "filepath")
        layout.context_pointer_set('target', self)
        layout.operator("wf.run_workflow", icon='PLAY', text="")


CLASSES = [
    WFFunctionNode
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
