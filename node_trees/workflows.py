import bpy
from bpy.types import NodeTree, NodeReroute, Context, NodeGroupInput, NodeGroupOutput, NodeCustomGroup
import traceback

INPUT_NODES = ["WFNodeSceneInput", "WFNodeObjectInput", "WFNodeCollectionInput"]

prev_nodes = set()


class WFNodeTree(NodeTree):
    bl_idname = "WFNodeTree"
    bl_label = "Workflows Graph"
    bl_icon = "NODETREE"

    # TODO HACK to stop log spam when editing group inputs
    type: bpy.props.StringProperty("WFTREE")

    def mark_invalid_links(self):
        for link in self.links:
            if type(link.from_socket) is not type(link.to_socket):
                link.is_valid = False

    def update(self):
        for link in self.links:
            if type(link.from_socket) is not type(link.to_socket):
                if isinstance(link.from_socket.node, NodeReroute):
                    try:
                        from_node = link.from_socket.node
                        from_node.outputs.clear()
                        from_node.outputs.new(link.to_socket.bl_idname, "Output")
                        self.links.new(from_node.outputs["Output"], link.to_socket)
                    except:
                        pass
                elif isinstance(link.to_socket.node, NodeReroute):
                    try:
                        to_node = link.to_socket.node
                        to_node.inputs.clear()
                        to_node.inputs.new(link.from_socket.bl_idname, "Input")
                        self.links.new(link.from_socket, to_node.inputs["Input"])
                    except:
                        pass
                else:
                    self.links.remove(link)

        global prev_nodes
        if len(self.nodes) > len(prev_nodes):
            diff = set(self.nodes) - prev_nodes
            from ..nodes.group import WFNodeGroup
            for node in list(diff):
                if isinstance(node, WFNodeGroup) and len(bpy.data.node_groups) > 0:
                    # node.node_tree = bpy.data.node_groups[-1]
                    print("Group node added")
                    print([tree.name for tree in bpy.data.node_groups])

        prev_nodes = set([node for node in self.nodes])


class RunAllWorkflowsOperator(bpy.types.Operator):
    bl_idname = "wf.run_all_workflows"
    bl_label = "Run All Workflows"
    bl_description = "Runs all the workflows in the current workflow tree"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Runs the current workflow"

    @classmethod
    def poll(cls, context: Context):
        if hasattr(bpy.context.space_data, "node_tree"):
            node_tree = bpy.context.space_data.node_tree
            for node in node_tree.nodes:
                if node.bl_idname in INPUT_NODES:
                    return True
        return False

    def execute(self, context):
        original_undo_steps = bpy.context.preferences.edit.undo_steps
        bpy.context.preferences.edit.undo_steps = 1000

        try:
            node_tree = context.space_data.node_tree
            from ..nodes.mixins import WFRunNode
            from ..nodes import execute_node
            for node in node_tree.nodes:
                if isinstance(node, WFRunNode):
                    execute_node(node, context)

                    from ..sockets.flow_socket import WFFlowSocket
                    for node in node_tree.nodes:
                        if isinstance(node, WFFlowSocket):
                            node.cleanup()

            result = {'FINISHED'}

        except Exception as err:
            traceback.print_exc()

            result = {'CANCELLED'}

        finally:
            bpy.ops.ed.undo_push(message='Workflow executed')
            bpy.ops.ed.undo()
            bpy.context.preferences.edit.undo_steps = original_undo_steps

        return result


global report
report = []


class RunWorkflowOperator(bpy.types.Operator):
    bl_idname = "wf.run_workflow"
    bl_label = "Run Workflow"

    node_name: bpy.props.StringProperty(default="")
    initial: bpy.props.BoolProperty(default=True)
    group_node_name: bpy.props.StringProperty(default="")

    def execute(self, context):
        global report
        try:
            fork = False

            node = None
            for tree in bpy.data.node_groups:
                node = next((tree_node for tree_node in tree.nodes if tree_node.name == self.node_name), None)
                if node:
                    break

            if self.initial:
                self.report({'INFO'}, f"Start of \"{node.name}\" execution")
                original_undo_steps = bpy.context.preferences.edit.undo_steps
                bpy.context.preferences.edit.undo_steps = 1000
                prev_global_undo = bpy.context.preferences.edit.use_global_undo
                bpy.context.preferences.edit.use_global_undo = True

            flow_socket = None
            from ..nodes.group import WFNodeGroup
            from ..nodes.mixins import WFFlowNode
            from ..sockets.flow_socket import WFFlowSocket
            if isinstance(node, WFFlowNode):
                if not len(node.cache):
                    obs = node.execute(context)
                    for ob in obs:
                        node.cache.add().ob = ob
                    exec_result_str = ", ".join([ob.name for ob in obs])
                    if exec_result_str:
                        report.append(f"\"{node.name}\" execution output: {exec_result_str}")
                    from ..utils import ensure_objects_layer_active
                    ensure_objects_layer_active(obs, context)

                flow_socket = next((socket for socket in node.outputs
                                    if isinstance(socket, WFFlowSocket)), None)

            elif isinstance(node, WFNodeGroup):
                for tree_node in node.node_tree.nodes:
                    if isinstance(tree_node, NodeGroupInput):
                        flow_socket = next((socket for socket in tree_node.outputs
                                            if isinstance(socket, WFFlowSocket)), None)
                        self.group_node_name = node.name
                        break

            elif isinstance(node, NodeGroupOutput):
                for tree in bpy.data.node_groups:
                    group_node = next(
                        (tree_node for tree_node in tree.nodes if tree_node.name == self.group_node_name),
                        None)

                    if group_node:
                        flow_socket = next((socket for socket in group_node.outputs
                                            if isinstance(socket, WFFlowSocket)), None)
                        self.group_node_name = ""
                        break

            else:
                flow_socket = next((socket for socket in node.outputs
                                    if isinstance(socket, WFFlowSocket)), None)

            if flow_socket and flow_socket.is_linked:
                fork = len(flow_socket.links) > 1
                if fork:
                    bpy.ops.ed.undo_push(message=f"{node.name}")

                # Mega Hack: I cache the names because it seems that running undo on a loop breaks the context
                names = []
                for link in flow_socket.links:
                    names.append(link.to_socket.node.name)
                for name in names:
                    bpy.ops.wf.run_workflow(node_name=name, initial=False, group_node_name=self.group_node_name)
                    if fork:
                        bpy.ops.ed.undo_push(message=f"{name}")
                        bpy.ops.ed.undo()

                if fork:
                    bpy.ops.ed.undo()

            result = {'FINISHED'}

        except Exception as err:
            traceback.print_exc()

            result = {'CANCELLED'}

        if self.initial:
            self.report({'INFO'}, f"End of \"{node.name}\" execution")

            bpy.ops.ed.undo_push(message=f"Run Workflow")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message=f"Run Workflow")

            bpy.context.preferences.edit.undo_steps = original_undo_steps
            bpy.context.preferences.edit.use_global_undo = prev_global_undo

            from ..nodes.mixins import WFFlowNode
            node_tree = node.id_data
            for node_item in node_tree.nodes:
                if isinstance(node_item, WFFlowNode):
                    node_item.cleanup()

            # bpy.ops.screen.info_log_show()

        return result


class WF_PT_GraphPanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Workflows"
    bl_category = "Workflows"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column(align=True)
        col.operator(RunAllWorkflowsOperator.bl_idname)


def register():
    bpy.utils.register_class(WFNodeTree)
    bpy.utils.register_class(RunWorkflowOperator)
    bpy.utils.register_class(RunAllWorkflowsOperator)
    bpy.utils.register_class(WF_PT_GraphPanel)


def unregister():
    bpy.utils.unregister_class(WFNodeTree)
    bpy.utils.unregister_class(RunAllWorkflowsOperator)
    bpy.utils.unregister_class(RunWorkflowOperator)
    bpy.utils.unregister_class(WF_PT_GraphPanel)
