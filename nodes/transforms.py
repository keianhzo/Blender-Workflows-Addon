import bpy
from .mixins import WFActionNode
from ..consts import TRANSFORM_COLOR, ERROR_COLOR


def get_modifiers_types(self, context):
    mods = set()

    obs = self.get_input_data(context)
    for ob in obs:
        if hasattr(ob, "modifiers") and ob.modifiers:
            for mod in ob.modifiers:
                maxid = -1
                id = -1
                found = False
                for idrec in self.mods_types_store:
                    id = idrec[0]
                    if id > maxid:
                        maxid = id
                    if idrec[1] == mod.type:
                        found = True
                        break

                if not found:
                    self.mods_types_store.append((maxid+1, mod.type))

                mods.add((mod.type, mod.type, mod.type, id))

    return mods


class WFNodeApplyModifierType(WFActionNode):
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

    mods_types_store = []

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR
        self.mods_types_store = []

    def draw_buttons(self, context, layout):
        layout.prop(self, "modifier")

    def get_input_data(self, context) -> list[bpy.types.Object]:
        return super().get_input_data(context)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = super().execute(context)

        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type in self.modifier:
                        ob.select_set(True)
                        context.view_layer.objects.active = ob
                        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


def get_modifiers_names(self, context):
    mods = set()

    obs = self.get_input_data(context)
    for ob in obs:
        if hasattr(ob, "modifiers") and ob.modifiers:
            for mod in ob.modifiers:
                maxid = -1
                id = -1
                found = False
                for idrec in self.mods_names_store:
                    id = idrec[0]
                    if id > maxid:
                        maxid = id
                    if idrec[1] == mod.name:
                        found = True
                        break

                if not found:
                    self.mods_names_store.append((maxid+1, mod.name))

                mods.add((mod.name, mod.name, mod.name, id))

    return mods


class WFNodeApplyModifierName(WFActionNode):
    bl_label = "Apply Modifier By Name"
    bl_description = """Applies the selected modifier to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier
This node won't work correctly with upstream nodes that change the object set like filter nodes"""

    modifier: bpy.props.EnumProperty(
        name="",
        description="Modifier",
        items=get_modifiers_names,
        default=0
    )

    mods_names_store = []

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR
        self.mods_names_store = []

    def draw_buttons(self, context, layout):
        layout.prop(self, "modifier")

    def get_input_data(self, context) -> list[bpy.types.Object]:
        return super().get_input_data(context)

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

        for ob in obs:
            if hasattr(ob, "modifiers") and ob.modifiers:
                for mod in ob.modifiers:
                    if mod.name in self.modifier:
                        ob.select_set(True)
                        context.view_layer.objects.active = ob
                        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        return obs


class WFNodeApplyAllModifiers(WFActionNode):
    bl_label = "Apply All Modifiers"
    bl_description = """Applies all modifiers to an object
    - in: One or more objects sets
    - out: All input objects
Note: "Make single user" is applied on the object data before applying the modifier"""

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

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


class WFNodeAddPrefixToName(WFActionNode):
    bl_label = "Add Prefix To Objects Names"
    bl_description = """Adds a prefix to the beginning of an object's name
    - in: One or more objects sets
    - out: All input objects"""
    bl_width_default = 200

    prefix: bpy.props.StringProperty(
        name="Prefix",
        description="String to prepend",
        default="",
        update=string_update
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "prefix")

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

        for ob in obs:
            ob.name = self.prefix + ob.name
            if hasattr(ob, "data") and ob.data:
                ob.data.name = ob.name

        return obs


class WFNodeAddSuffixToName(WFActionNode):
    bl_label = "Add Suffix To Objects Names"
    bl_description = """Adds a suffix to the end of an object's name
    - in: One or more objects sets
    - out: All input objects"""
    bl_width_default = 200

    suffix: bpy.props.StringProperty(
        name="Suffix",
        description="String to append",
        default="",
        update=string_update
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "suffix")

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

        for ob in obs:
            ob.name = ob.name + self.suffix
            if hasattr(ob, "data") and ob.data:
                ob.data.name = ob.name

        return obs


class WFNodeJoinObjects(WFActionNode):
    bl_label = "⚠️ Join Objects Geometry"
    bl_description = """Joins several meshes geometry and optionally renames the output object
    - name: The name to use for the joined object
    - in: One or more objects sets
    - out: The resulting object set
Note: Only meshes are joined all other objects are ignore."""
    bl_width_default = 160

    name: bpy.props.StringProperty(
        name="Name",
        description="New Object Name",
        default="",
        update=string_update
    )

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

        layout.prop(self, "name")

    def execute(self, context) -> set[bpy.types.Object]:
        obs = set(super().execute(context))

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
            meshes = [ob for ob in obs if ob.type == 'MESH']
            if meshes:
                last_ob = meshes[-1]

        context.view_layer.objects.active = last_ob
        bpy.ops.object.join()
        last_ob.name = self.name
        if hasattr(ob, "data") and ob.data:
            last_ob.data.name = self.name

        obs -= set(meshes)
        obs.add(last_ob)

        return list(obs)


class WFNodeTranslateToPosition(WFActionNode):
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
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        layout.prop(self, "relative")
        layout.label(text="Position:")
        col = layout.column()
        col.prop(self, "position", index=0, text="X")
        col.prop(self, "position", index=1, text="Y")
        col.prop(self, "position", index=2, text="Z")

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

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


class WFNodeTranslateToObjectPosition(WFActionNode):
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
        self.color = TRANSFORM_COLOR

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "target")

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

        bpy.ops.object.select_all(action='DESELECT')

        for ob in obs:
            ob.select_set(True)

        if obs:
            last_ob = obs[-1]

        context.view_layer.objects.active = last_ob

        last_ob.matrix_world.translation = self.target.matrix_world.translation

        return [last_ob]
    
def get_uv_maps(self, context):
    uvs = set()

    obs = self.get_input_data(context)
    for ob in obs:
        if hasattr(ob, "data") and ob.data:
            for uv in ob.data.uv_layers:
                maxid = -1
                id = -1
                found = False
                for idrec in self.uv_maps_store:
                    id = idrec[0]
                    if id > maxid:
                        maxid = id
                    if idrec[1] == uv.name:
                        found = True
                        break

                if not found:
                    self.uv_maps_store.append((maxid+1, uv.name))

                uvs.add((uv.name, uv.name, uv.name, id))

    return uvs

class WFNodeSetActiveUVMap(WFActionNode):
    bl_label = "Sets Active UV Map"
    bl_description = """Changes the active uv map to the one selected for all input objects
    - uvmap: The UVMap to set as active
    - in: One or more objects sets
    - out: All input objects
Note: If the UV map doesn't exist in the object, the uv map is not changed"""
    bl_width_default = 160

    uv_map: bpy.props.EnumProperty(
        name="UVMap",
        description="UVMap to set active",
        items=get_uv_maps,
        default=0
    )

    uv_maps_store = []

    def init(self, context):
        super().init(context)
        self.color = TRANSFORM_COLOR
        self.uv_maps_store = []

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.prop(self, "uv_map")

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

        for ob in obs:
            if hasattr(ob, "data") and ob.data:
                for uv in ob.data.uv_layers:
                    if uv.name in self.uv_map:
                        uv.active = True

        return obs