from . import enum_socket, flow_socket, objects_socket
import bpy

CLASSES = [
    objects_socket.ObjectsCache,
    objects_socket.AddObjectSocketOperator,
    objects_socket.RemoveObjectSocketOperator,
    objects_socket.WFObjectsSocket,
    enum_socket.WFEnumSocketChoice,
    enum_socket.WFEnumSocket,
    flow_socket.WFFlowSocket
]


def register():
    bpy.types.NodeSocket.wf_has_cache = bpy.props.BoolProperty(default=False)

    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    del bpy.types.NodeSocket.wf_has_cache

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
