
from . import export, transforms, inputs, filters, debug, group, modifiers, geometry, uv, grouping, misc
import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


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
        NodeItem("WFNodeExportOBJ"),
    ]),
    WFCategory("WORKFLOWS_Transforms", "Transforms", items=[
        NodeItem("WFNodeTranslateToPosition"),
        NodeItem("WFNodeTranslateToObjectPosition"),
    ]),
    WFCategory("WORKFLOWS_Geometry", "Geometry", items=[
        NodeItem("WFNodeJoinObjects"),
    ]),
    WFCategory("WORKFLOWS_Modifiers", "Modifiers", items=[
        NodeItem("WFNodeApplyModifierType"),
        NodeItem("WFNodeApplyModifierName"),
        NodeItem("WFNodeApplyAllModifiers"),
    ]),
    WFCategory("WORKFLOWS_UV", "UV", items=[
        NodeItem("WFNodeSetActiveUVMap"),
    ]),
    WFCategory("WORKFLOWS_Filters", "Filters", items=[
        NodeItem("WFNodeFilterStartsWith"),
        NodeItem("WFNodeFilterEndsWith"),
        NodeItem("WFNodeFilterContains"),
        NodeItem("WFNodeFilterRegex"),
    ]),
    WFCategory("WORKFLOWS_Grouping", "Grouping", items=[
        NodeItem("WFNodeCombineSets"),
        NodeItem("WFNodeRemoveFromSet"),
    ]),
    WFCategory("WORKFLOWS_Debug", "Debug", items=[
        NodeItem("WFNodePrintObjectNames"),
        NodeItem("WFNodeDryRun"),
    ]),
    WFCategory("WORKFLOWS_Misc", "Misc", items=[
        NodeItem("WFNodeAddPrefixToName"),
        NodeItem("WFNodeAddSuffixToName"),
    ]),
]

CLASSES = [
    inputs.WFNodeSceneInput,
    inputs.WFNodeObjectInput,
    inputs.WFNodeCollectionInput,
    export.WFNodeExportGLTF,
    export.WFNodeExportFBX,
    export.WFNodeExportOBJ,
    modifiers.WFNodeApplyModifierType,
    modifiers.WFNodeApplyModifierName,
    modifiers.WFNodeApplyAllModifiers,
    misc.WFNodeAddPrefixToName,
    misc.WFNodeAddSuffixToName,
    geometry.WFNodeJoinObjects,
    transforms.WFNodeTranslateToPosition,
    transforms.WFNodeTranslateToObjectPosition,
    uv.WFNodeSetActiveUVMap,
    filters.WFNodeFilterStartsWith,
    filters.WFNodeFilterEndsWith,
    filters.WFNodeFilterContains,
    filters.WFNodeFilterRegex,
    grouping.WFNodeCombineSets,
    grouping.WFNodeRemoveFromSet,
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

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    group.unregister()
