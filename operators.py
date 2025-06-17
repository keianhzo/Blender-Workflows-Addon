import bpy
import bmesh


class OBJECT_OT_deep_merge_operator(bpy.types.Operator):
    bl_idname = "object.deep_merge_operator"
    bl_label = "Deep Merge"
    bl_description = '''
    Merges selected objects in one object by:
        1) Making every object single user
        2) Applying transforms
        3) Converting to mesh and applying all modifiers (convert to mesh)
        4) Joining all object meshes
        5) removing doubles'''
    bl_options = {'REGISTER', 'UNDO'}

    new_origin: bpy.props.EnumProperty(
        name="Options",
        items=[
            ('ORIGIN_GEOMETRY', "Geometry", "New object geometry"),
            ('ORIGIN_CURSOR', "Cursor", "Cursor location")
        ],
        default='ORIGIN_GEOMETRY'
    )

    merge: bpy.props.BoolProperty(
        name="Merge Vertices",
        default=False
    )

    merge_distance: bpy.props.FloatProperty(
        name="Merge Distance",
        default=0.0001,
        min=0.0,
        max=10.0
    )

    def execute(self, context):
        ob = bpy.context.active_object
        if ob.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for ob in bpy.context.selected_objects:
            if ob.type != 'MESH':
                ob.select_set(False)

        if len(bpy.context.selected_objects) == 0:
            return {'FINISHED'}

        last_ob = bpy.context.selected_objects[-1]
        context.view_layer.objects.active = last_ob

        bpy.ops.object.make_single_user(object=True, obdata=True, material=False,
                                        animation=False, obdata_animation=False)
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.join()

        # Remove doubles
        if self.merge:
            bpy.ops.object.editmode_toggle()
            for ob in bpy.context.selected_objects:
                mesh = bmesh.from_edit_mesh(ob.data)
                for vert in mesh.verts:
                    vert.select = True
            bpy.ops.mesh.remove_doubles(threshold=self.merge_distance, use_unselected=False,
                                        use_sharp_edge_from_normals=False)
            bpy.ops.object.editmode_toggle()

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.ops.object.origin_set(type=self.new_origin)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_origin")
        layout.prop(self, "merge")
        row = layout.row()
        row.prop(self, "merge_distance")
        row.enabled = self.merge


class VIEW3D_MT_workflows_tools_object_submenu(bpy.types.Menu):
    bl_label = "Workflows Tools"
    bl_idname = "VIEW3D_MT_workflows_tools_object_submenu"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_deep_merge_operator.bl_idname)


def menu_func(self, context):
    self.layout.menu(VIEW3D_MT_workflows_tools_object_submenu.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_deep_merge_operator)
    bpy.utils.register_class(VIEW3D_MT_workflows_tools_object_submenu)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(VIEW3D_MT_workflows_tools_object_submenu)
    bpy.utils.unregister_class(OBJECT_OT_deep_merge_operator)
