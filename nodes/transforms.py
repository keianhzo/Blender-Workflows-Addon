import bpy
from .mixins import WFTransformNode
from ..consts import TRANSFORM_COLOR, ERROR_COLOR


def get_modifiers_types(self, context):
    return [(item.identifier, item.name, item.name) for item in bpy.types.Modifier.bl_rna.properties['type'].enum_items]


class WFNodeApplyModifierType(WFTransformNode):
    bl_label = "Apply Modifier By Type"
    bl_description = """Applies the selected modifier to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier
      This node won't work correctly with upstream nodes that change the object set like filter nodes"""
    bl_width_default = 200

    modifier: bpy.props.EnumProperty(
        name="",
        description="Modifier",
        items=get_modifiers_types,
        default=0
    )

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "modifier")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type in self.modifier:
                        ob.select_set(True)
                        context.view_layer.objects.active = ob
                        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


class WFNodeApplyModifierName(WFTransformNode):
    bl_label = "Apply Modifier By Name"
    bl_description = """Applies the selected modifier to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier
This node won't work correctly with upstream nodes that change the object set like filter nodes"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "name")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        from .mixins import get_input_socket_data
        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    name = get_input_socket_data(self.inputs["name"], context)
                    if mod.name == name:
                        ob.select_set(True)
                        context.view_layer.objects.active = ob
                        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


class WFNodeApplyAllModifiers(WFTransformNode):
    bl_label = "Apply All Modifiers"
    bl_description = """Applies all modifiers to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier"""

    def init(self, context):
        super().init(context)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    ob.select_set(True)
                    context.view_layer.objects.active = ob
                    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                    bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


def string_update(self, string):
    if string:
        self.color = TRANSFORM_COLOR
    else:
        self.color = ERROR_COLOR


class WFNodeAddPrefixToName(WFTransformNode):
    bl_label = "Add Prefix To Objects Names"
    bl_description = """Adds a prefix to the beginning of an object's name
    - in: One or more objects sets
    - out: All input objects"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "prefix")

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        from .mixins import get_input_socket_data
        prefix = get_input_socket_data(self.inputs["prefix"], context)
        for ob in obs:
            ob.name = prefix + ob.name
            if hasattr(ob, "data") and ob.data:
                ob.data.name = ob.name

        return obs


class WFNodeAddSuffixToName(WFTransformNode):
    bl_label = "Add Suffix To Objects Names"
    bl_description = """Adds a suffix to the end of an object's name
    - in: One or more objects sets
    - out: All input objects"""
    bl_width_default = 200

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "suffix")

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        from .mixins import get_input_socket_data
        suffix = get_input_socket_data(self.inputs["suffix"], context)
        for ob in obs:
            ob.name = ob.name + suffix
            if hasattr(ob, "data") and ob.data:
                ob.data.name = ob.name

        return obs


class WFNodeJoinObjects(WFTransformNode):
    bl_label = "Join Objects Geometry"
    bl_description = """Joins several meshes geometry and optionally renames the output object
    - name: The name to use for the joined object
    - in: One or more objects sets
    - out: The resulting object set
Note: Only meshes are joined all other objects are ignored"""
    bl_width_default = 160

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "name")

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = set(self.get_object_input_data(context))

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

        last_ob = None
        if obs:
            meshes = [ob for ob in obs if ob.type == 'MESH']
            if meshes:
                last_ob = meshes[-1]

        if last_ob:
            context.view_layer.objects.active = last_ob
            bpy.ops.object.join()
            from .mixins import get_input_socket_data
            name = get_input_socket_data(self.inputs["name"], context)
            if name:
                last_ob.name = name
                if hasattr(ob, "data") and ob.data:
                    last_ob.data.name = name

            obs -= set(meshes)
            obs.add(last_ob)

        return list(obs)


class WFNodeTranslateToPosition(WFTransformNode):
    bl_label = "Translate To Position"
    bl_description = """Translates an object to a new position. The position can be in world or local space
    - in: One or more objects sets
    - out: All input objects"""

    relative: bpy.props.BoolProperty(default=False, name="Relative")

    position: bpy.props.FloatVectorProperty(
        name="Position", description="An offset or world position to use for translation",
        unit='LENGTH',
        subtype="XYZ",
        default=(0.0, 0.0, 0.0))

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "relative")
        layout.label(text="Position:")
        col = layout.column()
        col.prop(self, "position", index=0, text="X")
        col.prop(self, "position", index=1, text="Y")
        col.prop(self, "position", index=2, text="Z")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        context.view_layer.objects.active = last_ob

        if self.relative:
            last_ob.location += self.position
        else:
            last_ob.matrix_world.translation = self.position

        return [last_ob]


class WFNodeTranslateToObjectPosition(WFTransformNode):
    bl_label = "Translate To Object Position"
    bl_description = """Translates an object to another object's position
    - in: One or more objects sets
    - out: All input objects"""

    target: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object
    )

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "target")

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        context.view_layer.objects.active = last_ob

        last_ob.matrix_world.translation = self.target.matrix_world.translation

        return [last_ob]


class WFNodeSetActiveUVMap(WFTransformNode):
    bl_label = "Sets Active UV Map"
    bl_description = """Changes the active uv map to the one selected for all input objects
    - name: The UVMap to set as active
    - in: One or more objects sets
    - out: All input objects
Note: If the UV map doesn't exist in the object, the uv map is not changed"""
    bl_width_default = 160

    def init(self, context):
        super().init(context)
        self.inputs.new("NodeSocketString", "name")

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_object_input_data(context)

        from .mixins import get_input_socket_data
        for ob in obs:
            if hasattr(ob, "data") and ob.data:
                for uv in ob.data.uv_layers:
                    uv_map = get_input_socket_data(self.inputs["name"], context)
                    if uv.name in uv_map:
                        uv.active = True

        return obs
