import bpy
from .mixins import WFExportNode


class WFNodeExportGLTF(WFExportNode):
    bl_label = "Export glTF"
    bl_description = """Exports the input objects to a glTF file. The file path extension (.gltf or .glb) will be used to choose the output type.
    - in: One or more objects sets"""
    bl_width_default = 300

    def execute(self, context):
        from .mixins import get_input_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]
            context.view_layer.objects.active = last_ob

        from ..utils import export_scene_gltf
        export_scene_gltf(context, self.filepath)


class WFNodeExportFBX(WFExportNode):
    bl_label = "Export FBX"
    bl_description = """Exports the input objects to a FBX file.
    - in: One or more objects sets"""
    bl_width_default = 300

    def execute(self, context):
        from .mixins import get_input_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]
            context.view_layer.objects.active = last_ob

        from ..utils import export_scene_fbx
        export_scene_fbx(context, self.filepath)


class WFNodeExportOBJ(WFExportNode):
    bl_label = "Export OBJ"
    bl_description = """Exports the input objects to a OBJ file.
    - in: One or more objects sets"""
    bl_width_default = 300

    def execute(self, context):
        from .mixins import get_input_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]
            context.view_layer.objects.active = last_ob

        from ..utils import export_scene_obj
        export_scene_obj(context, self.filepath)
