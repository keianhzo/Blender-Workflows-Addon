
from . import transforms, inputs, outputs, filters, debug, mixins, group
import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from bpy.types import Context
import traceback


class WFCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "WFNodeTree"


WF_CATEGORIES = [
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


class RunWorkflowOperator(bpy.types.Operator):
    bl_idname = "wf.run_workflow"
    bl_label = "Run Workflow"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        node = context.target
        if hasattr(node, "filepath") and node.filepath:
            return "Runs this workflow"
        return "The file path must be set to run this workflow"

    @classmethod
    def poll(cls, context: Context):
        if not context:
            return False

        node = bpy.context.target
        if hasattr(node, "filepath"):
            if node.filepath:
                return True
            return False

        return True

    def execute(self, context):
        original_undo_steps = bpy.context.preferences.edit.undo_steps
        bpy.context.preferences.edit.undo_steps = 1000

        try:
            node = context.target
            node.execute(context)

            node_tree = context.space_data.node_tree
            from .mixins import WFNode
            for node in node_tree.nodes:
                if isinstance(node, WFNode):
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


CLASSES = [
    RunWorkflowOperator,
    inputs.WFNodeSceneInput,
    inputs.WFNodeObjectInput,
    inputs.WFNodeCollectionInput,
    outputs.WFNodeExportGLTF,
    outputs.WFNodeExportFBX,
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
    mixins.register()
    group.register()

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    nodeitems_utils.register_node_categories("WORKFLOWS_NODES", WF_CATEGORIES)


def unregister():
    nodeitems_utils.unregister_node_categories("WORKFLOWS_NODES")

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

    group.unregister()
    mixins.unregister()
