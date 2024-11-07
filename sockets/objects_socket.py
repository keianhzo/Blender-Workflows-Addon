import bpy
from bpy.types import NodeSocketStandard


class AddObjectSocketOperator(bpy.types.Operator):
    bl_idname = "wf.add_object_socket"
    bl_label = "Add Object Socket"
    bl_options = {'REGISTER', 'UNDO'}

    extensible: bpy.props.BoolProperty(default=False)

    @classmethod
    def description(cls, context, properties):
        return "Adds a new object socket to the node"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        node = context.node
        socket = node.inputs.new("WFObjectsSocket", "objects")
        socket.extensible = self.extensible
        return {'FINISHED'}


class RemoveObjectSocketOperator(bpy.types.Operator):
    bl_idname = "wf.remove_object_socket"
    bl_label = "Remove Object Socket"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Removes the last added socket from the node"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        node = context.node
        if len(node.inputs) > 1:
            node.inputs.remove(node.inputs[len(node.inputs) - 1])
        return {'FINISHED'}


class ObjectsCache(bpy.types.PropertyGroup):
    value: bpy.props.PointerProperty(type=bpy.types.Object)


class WFObjectsSocket(NodeSocketStandard):
    bl_idname = "WFObjectsSocket"
    bl_label = "Workflows Objects"

    extensible: bpy.props.BoolProperty(default=False)
    default_value: bpy.props.CollectionProperty(type=ObjectsCache)

    if bpy.app.version < (4, 0, 0):
        def draw(self, context, layout):
            layout.alignment = 'RIGHT' if self.is_output else 'LEFT'
            layout.label(text=self.name)

            if self.extensible and not self.is_output:
                row = layout.row()
                row.context_pointer_set("node", self.node)
                if self == self.node.inputs[0]:
                    op = row.operator("wf.add_object_socket", icon='ADD', text="")
                    op.extensible = self.extensible
                else:
                    row.operator("wf.remove_object_socket", icon='REMOVE', text="")

        def draw_color(self, context):
            return (0.2, 1.0, 0.2, 1.0)
    else:
        def draw(self, context, layout, node, text):
            layout.alignment = 'RIGHT' if self.is_output else 'LEFT'
            layout.label(text=self.name)

            if self.extensible and not self.is_output:
                row = layout.row()
                row.context_pointer_set("node", self.node)
                if self == self.node.inputs[0]:
                    op = row.operator("wf.add_object_socket", icon='ADD', text="")
                    op.extensible = self.extensible
                else:
                    row.operator("wf.remove_object_socket", icon='REMOVE', text="")

        def draw_color(self, context, node):
            return (0.2, 1.0, 0.2, 1.0)
