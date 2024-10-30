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

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "target")
        if self.target and self.target.users == 0:
            from ..consts import ERROR_COLOR
            self.color = ERROR_COLOR

    def get_input_data(self, context) -> list[bpy.types.Object]:
        if self.target:
            return self.target.objects.values()

        return []

    def execute(self, context) -> list[bpy.types.Object]:
        return self.get_input_data(context)


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

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "target")
        if self.target and self.target.users == 0:
            from ..consts import ERROR_COLOR
            self.color = ERROR_COLOR

    def get_input_data(self, context) -> list[bpy.types.Object]:
        def get_collection_objects(col):
            obs = []
            obs.extend(col.objects.values())
            for child in col.children:
                obs.extend(get_collection_objects(child))

            return obs

        if self.target:
            return list(set(get_collection_objects(self.target)))

    def execute(self, context) -> list[bpy.types.Object]:
        return self.get_input_data(context)


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
        self.target = bpy.context.active_object

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "target")
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
        return self.get_input_data(context)
