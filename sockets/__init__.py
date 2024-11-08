from . import objects_socket
import bpy

CLASSES = [
    objects_socket.ObjectsCache,
    objects_socket.AddObjectSocketOperator,
    objects_socket.RemoveObjectSocketOperator,
    objects_socket.WFObjectsSocket,
]


def register():
    bpy.types.NodeSocket.wf_has_cache = bpy.props.BoolProperty(default=False)

    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    del bpy.types.NodeSocket.wf_has_cache

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
