import bpy
from bpy.types import NodeTree, NodeReroute, Context
import traceback

INPUT_NODES = ["WFNodeSceneInput", "WFNodeObjectInput", "WFNodeCollectionInput"]


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


class RunWorkflowOperator(bpy.types.Operator):
    bl_idname = "wf.run_workflow"
    bl_label = "Run Workflow"
    # bl_options = {'REGISTER', 'UNDO'}

    node_name: bpy.props.StringProperty(default="")

    def execute(self, context):
        original_undo_steps = bpy.context.preferences.edit.undo_steps
        bpy.context.preferences.edit.undo_steps = 1000
        prev_global_undo = bpy.context.preferences.edit.use_global_undo
        bpy.context.preferences.edit.use_global_undo = True
        bpy.ops.ed.undo_push(message='Run Workflow')

        try:
            node = None
            for tree in bpy.data.node_groups:
                node = next((tree_node for tree_node in tree.nodes if tree_node.name == self.node_name), None)
                if node:
                    break

            if not node:
                result = {'CANCELLED'}
            else:
                node.execute(context)

            # from ..nodes.mixins import WFNode
            # for node_tree in bpy.data.node_groups:
            #     for node in node_tree.nodes:
            #         if isinstance(node, WFNode):
            #             node.cleanup()

            result = {'FINISHED'}

        except Exception as err:
            self.report({'ERROR'}, f'"Run Workflow" execution for node "{self.node_name}" failed: {err}')
            traceback.print_exc()

            result = {'CANCELLED'}

        finally:
            bpy.ops.ed.undo_push(message='Run Workflow')
            bpy.ops.ed.undo()
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message=f'Run Workflow "{self.node_name}"')
            bpy.context.preferences.edit.undo_steps = original_undo_steps
            bpy.context.preferences.edit.use_global_undo = prev_global_undo

        return result


class RunAllWorkflowsOperator(bpy.types.Operator):
    bl_idname = "wf.run_all_workflows"
    bl_label = "Run All Workflows"
    bl_description = "Runs all the workflows in the current workflow tree"

    @classmethod
    def description(cls, context, properties):
        return "Runs all workflows in the active workflow tree"

    @classmethod
    def poll(cls, context: Context):
        node_tree = context.space_data.node_tree
        from ..nodes.mixins import WFRunnableNode
        for node in node_tree.nodes:
            if isinstance(node, WFRunnableNode):
                return True
        return False

    def execute(self, context):
        try:
            node_tree = context.space_data.node_tree

            node_names = []
            from ..nodes.mixins import WFRunnableNode
            for node in node_tree.nodes:
                if isinstance(node, WFRunnableNode):
                    node_names.append(node.name)

            for node_name in node_names:
                bpy.ops.wf.run_workflow(node_name=node_name)

            for node_name in node_names:
                bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message='Run All Workflows')

            self.report({'INFO'}, f'"Run All workflows" execution success')

            result = {'FINISHED'}

        except Exception as err:
            self.report({'ERROR'}, f'"Run All workflows" execution failed: {err}')
            traceback.print_exc()

            result = {'CANCELLED'}

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


CLASSES = [
    WFNodeTree,
    RunWorkflowOperator,
    RunAllWorkflowsOperator,
    WF_PT_GraphPanel
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
