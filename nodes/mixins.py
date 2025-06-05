import bpy
from bpy.types import Node, NodeReroute, NodeGroupInput, NodeGroupOutput
from ..consts import IO_COLOR, FILTER_COLOR, ERROR_COLOR, DEBUG_COLOR, TRANSFORM_COLOR, RUNNABLE_COLOR


def set_output_socket_data(socket, data, context):
    from ..sockets.objects_socket import WFObjectsSocket
    if isinstance(socket, WFObjectsSocket):
        socket.default_value.clear()
        for ob in data:
            socket.default_value.add().value = ob
    else:
        socket.default_value = data

    socket.wf_has_cache = True


def get_all_input_socket_data(socket, context):
    result = []

    for link in socket.links:
        result.extend(get_input_socket_link_data(link, context))

    return result


def get_input_socket_data(socket, context):
    if socket and socket.is_linked:
        return get_input_socket_link_data(socket.links[0], context)
    return socket.default_value if socket else None


def get_input_socket_link_data(link, context):
    from .group import WFNodeGroup
    socket = link.to_socket
    from_socket = link.from_socket
    from_node = from_socket.node

    from ..sockets.objects_socket import WFObjectsSocket
    if isinstance(from_node, WFNode):
        if not from_socket.wf_has_cache:
            from_node.execute(context)

        if isinstance(from_node, WFNodeGroup):
            from_node.execute(context)

            output_node = next((tree_node for tree_node in from_node.node_tree.nodes
                                if isinstance(tree_node, NodeGroupOutput)),
                               None)

            if output_node:
                output_node_socket = next(
                    (output_socket for output_socket in output_node.inputs if output_socket.name == socket.name),
                    None)
                if output_node_socket:
                    return get_input_socket_data(output_node_socket, context)

        else:
            if isinstance(from_socket, WFObjectsSocket):
                return [item.value for item in from_socket.default_value]
            else:
                return from_socket.default_value

    elif isinstance(from_node, NodeReroute):
        return get_input_socket_data(from_node.inputs[0], context)

    elif isinstance(from_node, NodeGroupInput):
        if isinstance(from_socket, WFObjectsSocket):
            return [item.value for item in from_socket.default_value]
        else:
            return from_socket.default_value

    elif isinstance(from_node, NodeGroupOutput):
        input_socket = next(
            (input_socket for input_socket in from_node.inputs if from_node.name == socket.name),
            None)
        if input_socket and input_socket.is_linked:
            link = input_socket.links[0]
            return get_input_socket_data(link.from_socket, context)

    return None


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
        for socket in self.inputs:
            socket.wf_has_cache = False
        for socket in self.outputs:
            socket.wf_has_cache = False

    def refresh(self, context):
        pass


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

    all_objects: bpy.props.BoolProperty(
        name="All Objects",
        description="Export all input objects using the object name as output file",
        default=False
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR


class WFInputNode(WFOutFunctionNode):
    def init(self, context):
        super().init(context)
        self.color = IO_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "target")


class WFOutputNode(WFInFunctionNode):

    def init(self, context):
        super().init(context)
        self.color = IO_COLOR


class WFDebugNode():

    def init(self, context):
        self.color = DEBUG_COLOR


class WFRunnableNode():
    ''' Node that can be run by the workflow executor'''


def filepath_update(self, filepath):
    if self.filepath:
        self.color = RUNNABLE_COLOR
    else:
        self.color = ERROR_COLOR


class WFExportNode(WFOutputNode, WFRunnableNode):

    filepath: bpy.props.StringProperty(
        name="Output File",
        description="Choose the output file path",
        default="",
        subtype="FILE_PATH",
        update=filepath_update
    )

    all_objects: bpy.props.BoolProperty(
        name="All Objects",
        description="Export all input objects using the object name as output file",
        default=False
    )

    def init(self, context):
        super().init(context)
        self.color = ERROR_COLOR

    def draw_buttons(self, context, layout):
        layout.label(text="Default export properties will be used")
        layout.prop(self, "filepath")
        row = layout.row()
        op = row.operator("wf.run_workflow", icon='PLAY', text="Run Workflow")
        op.node_name = self.name
        row.enabled = bool(self.filepath)
        layout.prop(self, "all_objects")

    def update(self):
        if self.filepath:
            self.color = RUNNABLE_COLOR
        else:
            self.color = ERROR_COLOR
