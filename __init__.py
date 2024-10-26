if "bpy" in locals():
    import importlib
    package = importlib.import_module("blender_io_workflows")
    from .utils import rreload
    rreload(package)

import bpy
from bpy.app.handlers import persistent


bl_info = {
    "name": "Blender IO Workflows",
    "blender": (4, 2, 0),
    "category": "IO",
    "author": "keianhzo",
    "version": (0, 0, 1),
    "location": "Node Editor > Sidebar > Workflows",
    "description": "Create workflows to streamline Export operation using node graphs"
}


class WFGlobalProps(bpy.types.PropertyGroup):
    version: bpy.props.IntVectorProperty(name="version",
                                         description="The WFs add-on version last used by this file",
                                         default=(0, 0, 0),
                                         size=3)


@persistent
def load_post(dummy):
    from .migrations import migrate
    migrate()


@persistent
def save_post(dummy):
    for scene in bpy.data.scenes:
        scene.wf_global_props.version = bl_info["version"]
    for object in bpy.data.objects:
        object.wf_global_props.version = bl_info["version"]
    for node_tree in bpy.data.node_groups:
        node_tree.wf_global_props.version = bl_info["version"]


def register():
    from . import sockets
    sockets.register()
    from . import nodes
    nodes.register()
    from . import node_trees
    node_trees.register()

    bpy.utils.register_class(WFGlobalProps)
    bpy.types.Scene.wf_global_props = bpy.props.PointerProperty(type=WFGlobalProps)
    bpy.types.Object.wf_global_props = bpy.props.PointerProperty(type=WFGlobalProps)
    bpy.types.NodeTree.wf_global_props = bpy.props.PointerProperty(type=WFGlobalProps)

    if load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post)

    if load_post not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(save_post)


def unregister():
    from . import node_trees
    node_trees.unregister()
    from . import sockets
    sockets.unregister()
    from . import nodes
    nodes.unregister()

    bpy.utils.unregister_class(WFGlobalProps)
    del bpy.types.Scene.wf_global_props
    del bpy.types.Object.wf_global_props
    del bpy.types.NodeTree.wf_global_props

    if load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post)

    if load_post in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(save_post)


if __name__ == "__main__":
    register()
