import bpy
from bpy.types import NodeSocketStandard


class AddObjectSocketOperator(bpy.types.Operator):
    bl_idname = "wf.add_object_socket"
    bl_label = "Add Object Socket"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Adds a new object socket to the node"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        node = context.node
        node.inputs.new("WFObjectsSocket", "in")
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


def has_prev_transforms(node):
    has_prev_transform = False
    from ..sockets.flow_socket import WFFlowSocket
    if len(node.inputs) > 0 and isinstance(node.inputs[0], WFFlowSocket):
        from ..nodes.mixins import WFTransformNode
        for link in node.inputs[0].links:
            if isinstance(link.from_socket.node, WFTransformNode):
                has_prev_transform = True

    return has_prev_transform


class WFObjectsSocket(NodeSocketStandard):
    bl_idname = "WFObjectsSocket"
    bl_label = "Workflows Objects"

    if bpy.app.version < (4, 0, 0):
        def draw(self, context, layout):
            layout.alignment = 'RIGHT' if self.is_output else 'LEFT'
            layout.label(text=self.name)

            if not self.is_output and self.node.bl_idname not in ["NodeGroupInput", "NodeGroupOutput", "WFNodeGroup"]:
                row = layout.row()
                row.context_pointer_set("node", self.node)
                from ..nodes.mixins import WFFunctionNode
                start_index = 0 if isinstance(self.node, WFFunctionNode) else 1
                if len(self.node.inputs) > start_index and self == self.node.inputs[start_index]:
                    row.operator("wf.add_object_socket", icon='ADD', text="")
                else:
                    row.operator("wf.remove_object_socket", icon='REMOVE', text="")

        def draw_color(self, context):
            return (0.2, 1.0, 0.2, 1.0)
    else:
        def draw(self, context, layout, node, text):
            layout.alignment = 'RIGHT' if self.is_output else 'LEFT'
            layout.label(text=self.name)

            if not self.is_output and self.node.bl_idname not in ["NodeGroupInput", "NodeGroupOutput", "WFNodeGroup"]:
                row = layout.row()
                row.context_pointer_set("node", self.node)
                from ..nodes.mixins import WFFunctionNode
                start_index = 0 if isinstance(self.node, WFFunctionNode) else 1
                if len(self.node.inputs) > start_index and self == self.node.inputs[start_index]:
                    row.operator("wf.add_object_socket", icon='ADD', text="")
                else:
                    row.operator("wf.remove_object_socket", icon='REMOVE', text="")

        def draw_color(self, context, node):
            output_color = (0.2, 1.0, 0.2, 1.0)

            from ..nodes.mixins import WFInputNode
            if has_prev_transforms(
                    self.node) and self.is_linked and isinstance(
                    self.links[0].from_socket.node, WFInputNode):
                output_color = (1.0, 0.0, 0.0, 1.0)

            return output_color
