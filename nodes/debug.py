import bpy
from .mixins import WFDebugNode, WFOutputNode


class WFNodePrintObjectNames(WFDebugNode):
    bl_label = "Print Object Names"
    bl_description = """Prints all the input object names in the console
    - in: One or more objects sets
    - out: All input objects"""

    def init(self, context):
        super().init(context)

    def execute(self, context) -> list[bpy.types.Object]:
        obs = super().execute(context)

        for ob in obs:
            print(ob.name)

        return obs
    
class WFNodeDryRun(WFOutputNode):
    bl_label = "Dry Run"
    bl_description = """Executes the workflow without doing anything"""
    bl_width_default = 300

    def init(self, context):
        super().init(context)
        self.inputs.new("WFObjectsSocket", "in")

    def draw_buttons(self, context, layout):
        layout.context_pointer_set('target', self)
        layout.operator("wf.run_workflow", icon='PLAY', text="")

    def execute(self, context) -> set[bpy.types.Object]:
        obs = super().execute(context)

        return obs