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
        node_tree = context.space_data.node_tree
        for node in node_tree.nodes:
            if node.bl_idname in INPUT_NODES:
                return True
        return False

    def execute(self, context):
        try:
            node_tree = context.space_data.node_tree
            from ..nodes.mixins import WFOutputNode
            for node in node_tree.nodes:
                if isinstance(node, WFOutputNode):
                    node.execute(context)

            result = {'FINISHED'}

        except Exception as err:
            traceback.print_exc()

            result = {'CANCELLED'}

        finally:
            bpy.ops.ed.undo_push(message='Workflow executed')
            bpy.ops.ed.undo()

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
    bpy.utils.register_class(RunAllWorkflowsOperator)
    bpy.utils.register_class(WF_PT_GraphPanel)


def unregister():
    bpy.utils.unregister_class(WFNodeTree)
    bpy.utils.unregister_class(RunAllWorkflowsOperator)
    bpy.utils.unregister_class(WF_PT_GraphPanel)
