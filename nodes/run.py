from .mixins import WFRunNode


class WFExecuteGraph(WFRunNode):
    bl_label = "Start Execution"
    bl_description = """Starts the execution of the node graph"""
    bl_width_default = 300

    def init(self, context):
        super().init(context)
