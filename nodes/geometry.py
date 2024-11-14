import bpy
from .mixins import WFTransformNode


class WFNodeJoinObjects(WFTransformNode):
    bl_label = "Join Objects Geometry"
    bl_description = """Joins several meshes geometry and optionally renames the output object
    - name: The name to use for the joined object
    - in: One or more objects sets
    - out: The resulting object set
Note: Only meshes are joined all other objects are ignore."""
    bl_width_default = 160

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "name")

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        bpy.ops.object.select_all(action='DESELECT')

        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        for ob in obs:
            lc = find_object_layer_collection(vlc, ob)
            if lc:
                lc.exclude = False
            else:
                print(f"Error: object {ob.name} doesn't have an active layer collection")
            ob.select_set(True)

        if obs:
            for ob in obs:
                if ob.type != 'MESH':
                    context.view_layer.objects.active = ob
                    bpy.ops.object.convert(target='MESH')

            meshes = [ob for ob in obs if ob.type == 'MESH']
            if meshes:
                last_ob = meshes[0]

        context.view_layer.objects.active = last_ob
        bpy.ops.object.join()

        name = get_input_socket_data(self.inputs["name"], context)
        if name:
            last_ob.name = name
            if hasattr(ob, "data") and ob.data:
                last_ob.data.name = name

        for mesh in meshes:
            obs.remove(mesh)
        obs.append(last_ob)

        set_output_socket_data(self.outputs["objects"], list(obs), context)
