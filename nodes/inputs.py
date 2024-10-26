import bpy
from .mixins import WFInputNode


def on_scene_update(self, context):
    pass


class WFNodeSceneInput(WFInputNode):
    bl_label = "Scene Input"

    target: bpy.props.PointerProperty(
        name="Scene",
        type=bpy.types.Scene,
        update=on_scene_update,
    )

    def init(self, context):
        super().init(context)
        self.outputs.new("WFObjectsSocket", "out")
        self.target = bpy.context.scene

    def get_input_data(self) -> list[bpy.types.Object]:
        return self.target.objects.values()

    def execute(self) -> list[bpy.types.Object]:
        return self.get_input_data()


def on_collection_update(self, context):
    pass


class WFNodeCollectionInput(WFInputNode):
    bl_label = "Collection Input"

    target: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        update=on_collection_update
    )

    def init(self, context):
        super().init(context)
        self.outputs.new("WFObjectsSocket", "out")
        self.target = bpy.data.collections[0]

    def get_input_data(self) -> list[bpy.types.Object]:
        return self.target.objects.values()

    def execute(self) -> list[bpy.types.Object]:
        return self.get_input_data()


def on_object_update(self, context):
    pass


def object_filter(self, ob):
    return True


class WFNodeObjectInput(WFInputNode):
    bl_label = "Object Input"

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

    def get_input_data(self) -> list[bpy.types.Object]:
        obs = [self.target]

        if self.children:
            for child in self.target.children:
                obs.append(child)

        return obs

    def execute(self) -> list[bpy.types.Object]:
        return self.get_input_data()
