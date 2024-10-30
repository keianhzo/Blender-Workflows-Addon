import os
import pathlib
import types
import bpy


def get_package_dependencies(package):
    assert (hasattr(package, "__package__"))
    fn = package.__file__
    fn_dir = os.path.dirname(fn) + os.sep
    node_set = {fn}  # set of module filenames
    node_depth_dict = {fn: 0}  # tracks the greatest depth that we've seen for each node
    node_pkg_dict = {fn: package}  # mapping of module filenames to module objects
    link_set = set()  # tuple of (parent module filename, child module filename)
    del fn

    def dependency_traversal_recursive(module, depth):
        for module_child in vars(module).values():

            # skip anything that isn't a module
            if not isinstance(module_child, types.ModuleType):
                continue

            fn_child = getattr(module_child, "__file__", None)

            # skip anything without a filename or outside the package
            if (fn_child is None) or (not fn_child.startswith(fn_dir)):
                continue

            # have we seen this module before? if not, add it to the database
            if not fn_child in node_set:
                node_set.add(fn_child)
                node_depth_dict[fn_child] = depth
                node_pkg_dict[fn_child] = module_child

            # set the depth to be the deepest depth we've encountered the node
            node_depth_dict[fn_child] = max(depth, node_depth_dict[fn_child])

            # have we visited this child module from this parent module before?
            if not ((module.__file__, fn_child) in link_set):
                link_set.add((module.__file__, fn_child))
                dependency_traversal_recursive(module_child, depth+1)
            else:
                pass
                # raise ValueError("Cycle detected in dependency graph!")

    dependency_traversal_recursive(package, 1)
    return (node_pkg_dict, node_depth_dict)


def rreload(package):
    """Recursively reload modules."""
    # https://stackoverflow.com/questions/28101895/reloading-packages-and-their-submodules-recursively-in-python
    import importlib
    node_pkg_dict, node_depth_dict = get_package_dependencies(package)
    for (d, v) in sorted([(d, v) for v, d in node_depth_dict.items()], reverse=True):
        print("Reloading %s" % pathlib.Path(v).name)
        importlib.reload(node_pkg_dict[v])


def get_prefs():
    return bpy.context.preferences.addons[__package__].preferences


def export_scene_gltf(context, path):
    import os
    args = {
        # Settings from "Remember Export Settings"
        **dict(context.scene.get('glTF2ExportSettings', {})),

        'export_format': ('GLB' if path.endswith('.glb') else 'GLTF_SEPARATE'),

        'filepath': bpy.path.abspath(path),
        'use_selection': True,
        'use_visible': False,
        'use_renderable': False,
        'use_active_collection': False,
        'export_apply': False,
    }
    if bpy.app.version >= (3, 2, 0):
        args['use_active_scene'] = True

    bpy.ops.export_scene.gltf(**args)


def export_scene_fbx(context, path):
    import os
    args = {
        # TODO: Add support for FBX presets selection"

        'filepath': bpy.path.abspath(path),
        'use_selection': True,
        'use_visible': False,
        'use_active_collection': False,
        'use_mesh_modifiers': False,
        'use_mesh_modifiers_render': False,
    }

    bpy.ops.export_scene.fbx(**args)


# Function to recursively search for the LayerCollection containing the object
def find_object_layer_collection(layer_collection, obj):
    # Check if the object is in this collection
    if obj.name in layer_collection.collection.objects:
        return layer_collection
    # Recursively search in child LayerCollections
    for child in layer_collection.children:
        found = find_object_layer_collection(child, obj)
        if found:
            return found
    return None


def ensure_object_layer_active(ob, context):
    vlc = bpy.context.view_layer.layer_collection
    lc = find_object_layer_collection(vlc, ob)
    if lc:
        lc.exclude = False
    else:
        print(f"Error: object {ob.name} doesn't have an active layer collection")


def ensure_objects_layer_active(obs, context):
    for ob in obs:
        ensure_object_layer_active(ob, context)
