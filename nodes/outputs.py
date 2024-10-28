import bpy
from .mixins import WFExportNode
from ..consts import IO_COLOR, ERROR_COLOR


class WFNodeExportGLTF(WFExportNode):
    bl_label = "Export glTF"
    bl_description = """Exports the input objects to a glTF file. The file path extension (.gltf or .glb) will be used to choose the output type.
    - in: One or more objects sets"""
    bl_width_default = 300

    def init(self, context):
        super().init(context)

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')

        # Iterate through the list and select each object by name
        for ob in obs:
            ob.select_set(True)

        # Optionally, make one of the objects active (usually the last one)
        if obs:
            last_ob = obs[-1]
            context.view_layer.objects.active = last_ob

        from ..utils import export_scene_gltf
        export_scene_gltf(context, self.filepath)

        return obs

    def update(self):
        if self.filepath:
            self.color = IO_COLOR
        else:
            self.color = ERROR_COLOR