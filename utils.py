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


def get_preset_args(preset_filename, preset_path):
    preset_filepath = bpy.utils.preset_find(preset_filename, preset_path)
    if preset_filepath:
        class Container(object):
            __slots__ = ('__dict__',)

        op = Container()
        file = open(preset_filepath, 'r')

        # storing the values from the preset on the class
        for line in file.readlines()[3::]:
            exec(line, globals(), locals())

        # pass class dictionary to the operator
        return op.__dict__

    else:
        raise FileNotFoundError(f'Preset not found: "{preset_filename}"')


def export_scene_gltf(context, path, preset):
    kwargs = {}

    if preset:
        preset_filename = "_".join(s for s in preset.split())
        preset_path = os.path.join("operator", "export_scene.gltf")
        kwargs = get_preset_args(preset_filename, preset_path)

    else:
        kwargs = {**dict(context.window_manager.operator_properties_last("export_scene.gltf"))}

    kwargs['filepath'] = bpy.path.abspath(path)

    if bpy.app.version >= (3, 2, 0):
        kwargs['use_active_scene'] = True

    bpy.ops.export_scene.gltf(**kwargs)


def export_scene_fbx(context, path, preset):
    kwargs = {}

    if preset:
        preset_filename = "_".join(s for s in preset.split())
        preset_path = os.path.join("operator", "export_scene.fbx")
        kwargs = get_preset_args(preset_filename, preset_path)

    else:
        kwargs = {**dict(context.window_manager.operator_properties_last("export_scene.fbx"))}

    kwargs['filepath'] = bpy.path.abspath(path)

    bpy.ops.export_scene.fbx(**kwargs)


def export_scene_obj(context, path, preset):
    kwargs = {}

    if preset:
        preset_filename = "_".join(s for s in preset.split())
        preset_path = os.path.join("operator", "wm.obj_export")
        kwargs = get_preset_args(preset_filename, preset_path)

    else:
        kwargs = {**dict(context.window_manager.operator_properties_last("wm.obj_export"))}

    kwargs['filepath'] = bpy.path.abspath(path)

    bpy.ops.wm.obj_export(**kwargs)


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
