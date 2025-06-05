import bpy
from .mixins import WFInputNode


def on_scene_update(self, context):
    if self.target:
        self.cached_objects = self.target.objects.values()
    else:
        self.cached_objects = []


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
        on_scene_update(self, context)

    def execute(self, context):
        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        on_scene_update(self, context)
        for ob in self.cached_objects:
            lc = find_object_layer_collection(vlc, ob)
            lc.exclude = False

        from .mixins import set_output_socket_data
        set_output_socket_data(self.outputs["objects"], self.cached_objects, context)

    def refresh(self, context):
        on_scene_update(self, context)


def get_collection_objects(col):
    obs = []
    obs.extend(col.objects.values())
    for child in col.children:
        obs.extend(get_collection_objects(child))

    return obs


def on_collection_update(self, context):
    if self.target:
        self.cached_objects = get_collection_objects(self.target)
    else:
        self.cached_objects = []


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
        self.cached_objects = []
        on_collection_update(self, context)

    def execute(self, context):
        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        on_collection_update(self, context)
        for ob in self.cached_objects:
            lc = find_object_layer_collection(vlc, ob)
            lc.exclude = False

        from .mixins import set_output_socket_data
        set_output_socket_data(self.outputs["objects"], self.cached_objects, context)

    def refresh(self, context):
        on_collection_update(self, context)


def on_object_update(self, context):
    if self.target:
        self.cached_objects = [self.target]
        if self.children:
            for child in self.target.children:
                self.cached_objects.append(child)
    else:
        self.cached_objects = []


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
        on_object_update(self, context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "children")
        if self.target and self.target.users == 0:
            from ..consts import ERROR_COLOR
            self.color = ERROR_COLOR

    def execute(self, context):
        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        on_object_update(self, context)
        for ob in self.cached_objects:
            lc = find_object_layer_collection(vlc, ob)
            if lc:
                lc.exclude = False
            else:
                print(f"Error: object {ob.name} doesn't have an active layer collection")

        from .mixins import set_output_socket_data
        set_output_socket_data(self.outputs["objects"], self.cached_objects, context)

    def refresh(self, context):
        on_object_update(self, context)
