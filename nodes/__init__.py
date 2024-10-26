
from . import transforms, inputs, outputs, filters
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
    WFCategory("WORKFLOWS_Output", "Output", items=[
        NodeItem("WFNodeExportGLTF"),
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
    ]),
    WFCategory("WORKFLOWS_Filters", "Filters", items=[
        NodeItem("WFNodeFilterStartsWith"),
        NodeItem("WFNodeFilterEndsWith"),
        NodeItem("WFNodeFilterContains"),
        NodeItem("WFNodeFilterRegex"),
        NodeItem("WFNodeMerge"),
    ])
]


class RunWorkflowOperator(bpy.types.Operator):
    bl_idname = "wf.run_workflow"
    bl_label = "Run Workflow"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        node = context.target
        if node.filepath:
            return "Runs this workflow"
        return "The file path must be set to run this workflow"

    @classmethod
    def poll(cls, context: Context):
        node = context.target
        if node.filepath:
            return True
        return False

    def execute(self, context):
        try:
            node = context.target
            node.execute()

            return {'FINISHED'}

        except Exception as err:
            traceback.print_exc()

            return {'CANCELLED'}

        finally:
            bpy.ops.ed.undo_push(message='Workflow executed')
            bpy.ops.ed.undo()


CLASSES = [
    RunWorkflowOperator,
    inputs.WFNodeSceneInput,
    inputs.WFNodeObjectInput,
    inputs.WFNodeCollectionInput,
    outputs.WFNodeExportGLTF,
    transforms.WFNodeApplyModifierType,
    transforms.WFNodeApplyModifierName,
    transforms.WFNodeApplyAllModifiers,
    transforms.WFNodeAddPrefixToName,
    transforms.WFNodeAddSuffixToName,
    transforms.AddObjectSocketOperator,
    transforms.RemoveObjectSocketOperator,
    transforms.WFNodeJoinObjects,
    transforms.WFNodeTranslateToPosition,
    transforms.WFNodeTranslateToObjectPosition,
    filters.WFNodeFilterStartsWith,
    filters.WFNodeFilterEndsWith,
    filters.WFNodeFilterContains,
    filters.WFNodeFilterRegex,
    filters.WFNodeMerge,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    nodeitems_utils.register_node_categories("WORKFLOWS_NODES", WF_CATEGORIES)


def unregister():
    nodeitems_utils.unregister_node_categories("WORKFLOWS_NODES")

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
