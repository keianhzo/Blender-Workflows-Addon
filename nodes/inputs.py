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
        self.outputs.new("WFObjectsSocket", "out")
        self.target = context.scene

    def get_input_data(self, context) -> list[bpy.types.Object]:
        if self.target:
            return self.target.objects.values()
        return []

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_input_data(context)

        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        for ob in obs:
            lc = find_object_layer_collection(vlc, ob)
            lc.exclude = False

        return obs


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
        self.outputs.new("WFObjectsSocket", "out")
        self.target = bpy.data.collections[0]

    def get_input_data(self, context) -> list[bpy.types.Object]:
        obs = []

        def get_collection_objects(col):
            obs = []
            obs.extend(col.objects.values())
            for child in col.children:
                obs.extend(get_collection_objects(child))

            return obs
            
        if self.target:
            obs = get_collection_objects(self.target)
        
        return list(set(obs))

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_input_data(context)

        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        for ob in obs:
            lc = find_object_layer_collection(vlc, ob)
            lc.exclude = False

        return obs


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
        self.outputs.new("WFObjectsSocket", "out")

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "children")
        if self.target and self.target.users == 0:
            from ..consts import ERROR_COLOR
            self.color = ERROR_COLOR

    def get_input_data(self, context) -> list[bpy.types.Object]:
        obs = [self.target]

        if self.children:
            for child in self.target.children:
                obs.append(child)

        return obs

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_input_data(context)

        vlc = bpy.context.view_layer.layer_collection
        from ..utils import find_object_layer_collection
        for ob in obs:
            lc = find_object_layer_collection(vlc, ob)
            if lc:
                lc.exclude = False
            else:
                print(f"Error: object {ob.name} doesn't have an active layer collection")

        return obs
