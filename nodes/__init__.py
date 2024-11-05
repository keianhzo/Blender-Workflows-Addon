
from . import export, transforms, inputs, filters, debug, run, group, mixins
import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


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


CLASSES = [
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
    mixins.register()

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    nodeitems_utils.register_node_categories("WORKFLOWS_NODES", WF_CATEGORIES)


def unregister():
    nodeitems_utils.unregister_node_categories("WORKFLOWS_NODES")

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

    group.unregister()
    mixins.unregister()
