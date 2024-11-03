
from . import export, transforms, inputs, filters, debug, run, group
import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
import traceback


class WFCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "WFNodeTree"


WF_CATEGORIES = [
    WFCategory("WORKFLOWS_Events", "Events", items=[
        NodeItem("WFExecuteGraph"),
    ]),
    WFCategory("WORKFLOWS_Input", "Input", items=[
        NodeItem("WFNodeSceneInput"),
        NodeItem("WFNodeObjectInput"),
        NodeItem("WFNodeCollectionInput"),
    ]),
    WFCategory("WORKFLOWS_Export", "Export", items=[
        NodeItem("WFNodeExportGLTF"),
        NodeItem("WFNodeExportFBX"),
    ]),
    WFCategory("WORKFLOWS_Transforms", "Transforms", items=[
        NodeItem("WFNodeApplyModifierType"),
        NodeItem("WFNodeApplyModifierName"),
        NodeItem("WFNodeApplyAllModifiers"),
        NodeItem("WFNodeAddPrefixToName"),
        NodeItem("WFNodeAddSuffixToName"),
        NodeItem("WFNodeJoinObjects"),
        NodeItem("WFNodeTranslateToPosition"),
        NodeItem("WFNodeTranslateToObjectPosition"),
        NodeItem("WFNodeSetActiveUVMap"),
    ]),
    WFCategory("WORKFLOWS_Filters", "Filters", items=[
        NodeItem("WFNodeFilterStartsWith"),
        NodeItem("WFNodeFilterEndsWith"),
        NodeItem("WFNodeFilterContains"),
        NodeItem("WFNodeFilterRegex"),
        NodeItem("WFNodeCombineSets"),
        NodeItem("WFNodeRemoveFromSet"),
    ]),
    WFCategory("WORKFLOWS_Debug", "Debug", items=[
        NodeItem("WFNodePrintObjectNames"),
        NodeItem("WFNodeDryRun"),
    ])
]

global report
report = []


class RunWorkflowStepOperator(bpy.types.Operator):
    bl_idname = "wf.run_workflow_step"
    bl_label = "Run Workflow Step"

    node_name: bpy.props.StringProperty(default="")
    initial: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        global report
        try:
            fork = False

            node = context.space_data.node_tree.nodes[self.node_name]

            if self.initial:
                self.report({'INFO'}, f"Start of {node.name} execution")
                original_undo_steps = bpy.context.preferences.edit.undo_steps
                bpy.context.preferences.edit.undo_steps = 1000
                prev_global_undo = bpy.context.preferences.edit.use_global_undo
                bpy.context.preferences.edit.use_global_undo = True

            from .mixins import WFFlowNode
            if isinstance(node, WFFlowNode):
                if not node["cached_data"]:
                    obs = node.execute(context)
                    node["cached_data"] = obs
                    exec_result_str = ", ".join([ob.name for ob in obs])
                    if exec_result_str:
                        report.append(f"{node.name} execution output: {exec_result_str}")
                    from ..utils import ensure_objects_layer_active
                    ensure_objects_layer_active(obs, context)

            from ..sockets.flow_socket import WFFlowSocket
            flow_socket = None
            if len(node.outputs) > 0:
                flow_socket = node.outputs[0]

            if flow_socket and isinstance(flow_socket, WFFlowSocket) and flow_socket.is_linked:
                fork = len(flow_socket.links) > 1
                if fork:
                    bpy.ops.ed.undo_push(message=f"{node.name}")

                # Mega Hack: I cache the names because it seems that running undo on a loop breaks the context
                names = []
                for link in flow_socket.links:
                    names.append(link.to_socket.node.name)
                for name in names:
                    bpy.ops.wf.run_workflow_step(node_name=name, initial=False)
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
            bpy.ops.ed.undo_push(message=f"Run Workflow")

            bpy.context.preferences.edit.undo_steps = original_undo_steps
            bpy.context.preferences.edit.use_global_undo = prev_global_undo

            from .mixins import WFFlowNode
            node_tree = context.space_data.node_tree
            for node in node_tree.nodes:
                if isinstance(node, WFFlowNode):
                    node.cleanup()

            for item in report:
                self.report({'INFO'}, item)
            self.report({'INFO'}, f"End of {node.name} execution")
            bpy.ops.screen.info_log_show()

        return result


CLASSES = [
    RunWorkflowStepOperator,
    run.WFExecuteGraph,
    inputs.WFNodeSceneInput,
    inputs.WFNodeObjectInput,
    inputs.WFNodeCollectionInput,
    export.WFNodeExportGLTF,
    export.WFNodeExportFBX,
    transforms.WFNodeApplyModifierType,
    transforms.WFNodeApplyModifierName,
    transforms.WFNodeApplyAllModifiers,
    transforms.WFNodeAddPrefixToName,
    transforms.WFNodeAddSuffixToName,
    transforms.WFNodeJoinObjects,
    transforms.WFNodeTranslateToPosition,
    transforms.WFNodeTranslateToObjectPosition,
    transforms.WFNodeSetActiveUVMap,
    filters.WFNodeFilterStartsWith,
    filters.WFNodeFilterEndsWith,
    filters.WFNodeFilterContains,
    filters.WFNodeFilterRegex,
    filters.WFNodeCombineSets,
    filters.WFNodeRemoveFromSet,
    debug.WFNodePrintObjectNames,
    debug.WFNodeDryRun,
]


def register():
    group.register()

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    nodeitems_utils.register_node_categories("WORKFLOWS_NODES", WF_CATEGORIES)


def unregister():
    nodeitems_utils.unregister_node_categories("WORKFLOWS_NODES")

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

    group.unregister()
