import bpy
from .mixins import WFExportNode


class WFNodeExportGLTF(WFExportNode):
    bl_label = "Export glTF"
    bl_description = """Exports the input objects to a glTF file. The file path extension (.gltf or .glb) will be used to choose the output type.
    - in: One or more objects sets"""
    bl_width_default = 300

    preset: bpy.props.StringProperty(default="")

    def execute(self, context):
        from .mixins import get_input_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        import os
        from ..utils import export_scene_gltf
        if self.all_objects:
            for ob in obs:
                ob.select_set(True)
                context.view_layer.objects.active = ob
                dir = os.path.dirname(self.filepath)
                export_scene_gltf(context, os.path.join(dir, ob.name + ".gltf"), self.preset)
                ob.select_set(False)
        else:
            for ob in obs:
                ob.select_set(True)

            if obs:
                last_ob = obs[-1]
                context.view_layer.objects.active = last_ob

            export_scene_gltf(context, self.filepath, self.preset)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

        layout.prop(self, "preset")


class WFNodeExportFBX(WFExportNode):
    bl_label = "Export FBX"
    bl_description = """Exports the input objects to a FBX file.
    - in: One or more objects sets"""
    bl_width_default = 300

    preset: bpy.props.StringProperty(default="")

    def execute(self, context):
        from .mixins import get_input_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        import os
        from ..utils import export_scene_fbx
        if self.all_objects:
            for ob in obs:
                ob.select_set(True)
                context.view_layer.objects.active = ob
                dir = os.path.dirname(self.filepath)
                export_scene_fbx(context, os.path.join(dir, ob.name + ".fbx"), self.preset)
                ob.select_set(False)
        else:
            for ob in obs:
                ob.select_set(True)

            if obs:
                last_ob = obs[-1]
                context.view_layer.objects.active = last_ob

            export_scene_fbx(context, self.filepath, self.preset)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

        layout.prop(self, "preset")


class WFNodeExportOBJ(WFExportNode):
    bl_label = "Export OBJ"
    bl_description = """Exports the input objects to a OBJ file.
    - in: One or more objects sets"""
    bl_width_default = 300

    preset: bpy.props.StringProperty(default="")

    def execute(self, context):
        from .mixins import get_input_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        import os
        from ..utils import export_scene_obj
        if self.all_objects:
            for ob in obs:
                ob.select_set(True)
                context.view_layer.objects.active = ob
                dir = os.path.dirname(self.filepath)
                export_scene_obj(context, os.path.join(dir, ob.name + ".obj"), self.preset)
                ob.select_set(False)
        else:
            for ob in obs:
                ob.select_set(True)

            if obs:
                last_ob = obs[-1]
                context.view_layer.objects.active = last_ob

            export_scene_obj(context, self.filepath, self.preset)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

        layout.prop(self, "preset")
