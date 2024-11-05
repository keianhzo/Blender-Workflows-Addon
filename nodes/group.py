import bpy
from bpy.types import NodeCustomGroup
from bpy.types import Operator
from mathutils import Vector


def update_sockets(node_group_sockets, io_node_sockets):
    sockets = io_node_sockets[:-1]

    # Socket added
    if len(node_group_sockets) < len(sockets):
        print("New input socket added")
        new_idx = 0
        for idx in range(0, len(sockets)):
            if len(node_group_sockets) > idx+1 and node_group_sockets[idx].identifier != sockets[idx].identifier:
                new_idx = idx
                break

        new_socket = sockets[idx]
        node_group_sockets.new(new_socket.bl_idname, new_socket.name, identifier=new_socket.identifier)
        node_group_sockets.move(len(node_group_sockets) - 1, new_idx)

    # Socket changed position or type
    elif len(node_group_sockets) == len(sockets):
        for idx in range(0, len(sockets)):
            socket = sockets[idx]

            # Position change
            if node_group_sockets[idx].identifier != socket.identifier:
                moved_socket = next((moved_socket for moved_socket in sockets
                                    if node_group_sockets[idx].identifier == moved_socket.identifier), None)
                if moved_socket:
                    print("Socket position change")
                    new_idx = sockets.index(moved_socket)
                    node_group_sockets.move(idx, new_idx)
                    break

            # Type change
            elif node_group_sockets[idx].bl_idname != socket.bl_idname:
                print("Socket type change")
                node_group_sockets.remove(node_group_sockets[idx])
                node_group_sockets.new(socket.bl_idname, socket.name, identifier=socket.identifier)
                node_group_sockets.move(len(node_group_sockets) - 1, idx)
                break

            elif node_group_sockets[idx].name != socket.name:
                node_group_sockets[idx].name = socket.name

    # Socket removed
    else:
        print("Socket removed")
        for idx in range(0, len(sockets)):
            is_removed = next((socket for socket in sockets
                               if node_group_sockets[idx].identifier == socket.identifier), None) == None
            if is_removed:
                node_group_sockets.remove(node_group_sockets[idx])
                break


class WFNodeGroup(NodeCustomGroup):
    bl_idname = "WFNodeGroup"
    bl_label = "Node Group"

    def draw_buttons(self, context, layout):
        if (self == self.id_data.nodes.active):
            row = layout.row(align=True)
            row.prop(self, "node_tree", text="")
            row.operator("wf.toggle_edit_group", text="", icon='NODETREE')

    def free(self):
        pass
        # self.node_tree.unregister_all_objects()

    def update(self):
        if not self.node_tree:
            return

        for node in self.node_tree.nodes:
            if node.bl_idname == "NodeGroupInput":
                update_sockets(self.inputs, node.outputs)
            elif node.bl_idname == "NodeGroupOutput":
                update_sockets(self.outputs, node.inputs)


class WFGroupNodesOperator(Operator):
    """Create a node group from the selected nodes"""
    bl_idname = "wf.group_nodes"
    bl_label = "Group Workflow Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space_data = context.space_data
        if hasattr(space_data, "node_tree"):
            if (space_data.node_tree):
                return space_data.tree_type == "WFNodeTree"
        return False

    def execute(self, context):
        space_data = context.space_data
        path = space_data.path
        base_node_tree = path[-1].node_tree
        node_group = bpy.data.node_groups.new("WFNodeGroup", "WFNodeTree")

        # Get the selected nodes (excluding any group inputs/outputs)
        selected_nodes = []
        nodes_count = 0
        for node in base_node_tree.nodes:
            if node.bl_idname in ['NodeGroupInput', 'NodeGroupOutput']:
                node.select = False
            if node.select:
                selected_nodes.append(node)
                nodes_count += 1

        # Get any links that link outside the selection
        external_links = {
            "inputs": [],
            "outputs": []
        }
        for node in selected_nodes:
            for node_input in node.inputs:
                if node_input.is_linked:
                    link = node_input.links[0]
                    if not link.from_node in selected_nodes:
                        if not link in external_links["inputs"]:
                            external_links["inputs"].append(link)
            for node_output in node.outputs:
                if node_output.is_linked:
                    for link in node_output.links:
                        if not link.to_node in selected_nodes:
                            if not link in external_links["outputs"]:
                                external_links["outputs"].append(link)

        # Find the center of the node group and how much space it needs.
        group_min_x = 0
        group_max_x = 0
        group_center = Vector((0, 0))
        offset = selected_nodes[0].location.copy() if len(selected_nodes) > 0 else Vector((0, 0))
        for node in selected_nodes:
            node.location -= offset
            group_center += node.location / nodes_count
            if node.location.x < group_min_x:
                group_min_x = node.location.x
            if node.location.x > group_max_x:
                group_max_x = node.location.x + node.width
        group_center += offset

        # Add group input and output nodes for the new node group
        group_input_node = node_group.nodes.new("NodeGroupInput")
        group_output_node = node_group.nodes.new("NodeGroupOutput")
        group_input_node.location = Vector((group_min_x - 200, 0))
        group_output_node.location = Vector((group_max_x + 100, 0))

        # Copy the selected nodes for later pasting into the group.
        if nodes_count > 0:
            bpy.ops.node.clipboard_copy()

        # Create the new group node.
        group_node = base_node_tree.nodes.new("WFNodeGroup")
        group_node.location = group_center
        group_node.node_tree = node_group

        # Switch the editor to view the group node.
        path.append(node_group, node=group_node)

        # Paste the copied nodes into the group.
        if nodes_count > 0:
            bpy.ops.node.clipboard_paste()

        # Create the group node tree input/output sockets and attache links
        # node_group.interface.new_socket will create the group_node sockets on update.
        # # See WFNodeGroup.update
        for link in external_links["inputs"]:
            link_node = node_group.nodes[link.to_node.name]
            node_input = link_node.inputs[link.to_socket.name]

            node_group.interface.new_socket(
                name=link.to_socket.name, in_out="INPUT",
                socket_type=link.to_socket.bl_idname)
            node_group.links.new(group_input_node.outputs[link.to_socket.name], node_input)

            base_node_tree.links.new(
                link.from_node.outputs[link.from_socket.name],
                group_node.inputs[link.to_socket.name]
            )

        for link in external_links["outputs"]:
            link_node = node_group.nodes[link.from_node.name]
            node_output = link_node.outputs[link.from_socket.name]

            node_group.interface.new_socket(
                name=link.from_socket.name, in_out="OUTPUT",
                socket_type=link.from_socket.bl_idname)
            node_group.links.new(node_output, group_output_node.inputs[link.from_socket.name])

            base_node_tree.links.new(
                group_node.outputs[link.from_socket.name],
                link.to_node.inputs[link.to_socket.name]
            )

        # Remove the original nodes from the base node tree since they've been copied into the group.
        for node in selected_nodes:
            base_node_tree.nodes.remove(node)

        return {'FINISHED'}


class WFToggleEditGroupOperator(Operator):
    """Create a node group from the selected nodes"""
    bl_idname = "wf.toggle_edit_group"
    bl_label = "Toggle Workflow Group"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space_data = context.space_data
        if hasattr(space_data, "node_tree"):
            if (space_data.node_tree):
                return space_data.tree_type == "WFNodeTree"
        return False

    def execute(self, context):
        path = context.space_data.path
        active_node = path[-1].node_tree.nodes.active

        if hasattr(active_node, "node_tree") and active_node.select:
            path.append(active_node.node_tree, node=active_node)
            return {'FINISHED'}
        elif len(path) > 1:
            path.pop()

        return {'CANCELLED'}


def node_menu_addition(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("wf.group_nodes")
    layout.operator("wf.toggle_edit_group")


classes = [
    WFNodeGroup,
    WFGroupNodesOperator,
    WFToggleEditGroupOperator
]

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="Node Generic", space_type='NODE_EDITOR')

    kmi = km.keymap_items.new("wf.group_nodes", 'G', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wf.toggle_edit_group", 'TAB', 'PRESS')
    addon_keymaps.append((km, kmi))

    bpy.types.NODE_MT_node.append(node_menu_addition)
    bpy.types.NODE_MT_context_menu.append(node_menu_addition)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.NODE_MT_node.remove(node_menu_addition)
    bpy.types.NODE_MT_context_menu.remove(node_menu_addition)
