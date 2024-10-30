import bpy
from .mixins import WFDebugNode, WFInFlowNode
from ..consts import IO_COLOR


class WFNodePrintObjectNames(WFDebugNode):
    bl_label = "Print Object Names"
    bl_description = """Prints all the input object names in the console
    - in: One or more objects sets
    - out: All input objects"""

    def init(self, context):
        super().init(context)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = self.get_input_data(context)

        for ob in obs:
            print(ob.name)

        return obs


class WFNodeDryRun(WFInFlowNode):
    bl_label = "Dry Run"
    bl_description = """Executes the workflow without doing anything"""
    bl_width_default = 300

    def init(self, context):
        super().init(context)
        self.color = IO_COLOR
        self.inputs.new("WFObjectsSocket", "in")
