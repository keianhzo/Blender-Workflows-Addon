import bpy
from .mixins import WFInputNode


def on_scene_update(self, context):
    pass


class WFNodeSceneInput(WFInputNode):
    bl_label = "Scene Input"
    bl_description = """Outputs all the objects in the selected scene
    - out: All the objects in the selected scene"""

    target: bpy.props.PointerProperty(
        name="Scene",
        type=bpy.types.Scene,
        update=on_scene_update,
    )

    def init(self, context):
        super().init(context)
        self.target = bpy.context.scene

    def execute(self, context):
        obs = []
        if self.target:
            obs = self.target.objects.values()

        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        for ob in obs:
            lc = find_object_layer_collection(vlc, ob)
            lc.exclude = False

        from .mixins import set_output_socket_data
        set_output_socket_data(self.outputs["objects"], obs, context)


def on_collection_update(self, context):
    pass


class WFNodeCollectionInput(WFInputNode):
    bl_label = "Collection Input"
    bl_description = """Outputs all the objects in the selected collection
    - out: All the objects in the selected collection"""

    target: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        update=on_collection_update
    )

    def init(self, context):
        super().init(context)
        self.target = bpy.data.collections[0]

    def execute(self, context):
        obs = []
        if self.target:
            def get_collection_objects(col):
                obs = []
                obs.extend(col.objects.values())
                for child in col.children:
                    obs.extend(get_collection_objects(child))

                return obs

            obs = get_collection_objects(self.target)

        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        for ob in obs:
            lc = find_object_layer_collection(vlc, ob)
            lc.exclude = False

        from .mixins import set_output_socket_data
        set_output_socket_data(self.outputs["objects"], obs, context)


def on_object_update(self, context):
    pass


def object_filter(self, ob):
    return True


class WFNodeObjectInput(WFInputNode):
    bl_label = "Object Input"
    bl_description = """Outputs the selected object. If the "children" option is enabled it will also output the object's children
    - out: The selected object and optionally also its children"""

    children: bpy.props.BoolProperty(default=False, name="Children")

    target: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        poll=object_filter,
        update=on_object_update
    )

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "children")
        if self.target and self.target.users == 0:
            from ..consts import ERROR_COLOR
            self.color = ERROR_COLOR

    def execute(self, context):
        obs = [self.target]
        if self.children:
            for child in self.target.children:
                obs.append(child)

        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        for ob in obs:
            lc = find_object_layer_collection(vlc, ob)
            if lc:
                lc.exclude = False
            else:
                print(f"Error: object {ob.name} doesn't have an active layer collection")

        from .mixins import set_output_socket_data
        set_output_socket_data(self.outputs["objects"], obs, context)
