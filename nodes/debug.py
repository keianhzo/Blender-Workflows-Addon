import bpy
from .mixins import WFDebugNode, WFOutputNode, WFInOutFunctionNode, WFRunnableNode


class WFNodePrintObjectNames(WFInOutFunctionNode, WFDebugNode):
    bl_label = "Print Object Names"
    bl_description = """Prints all the input object names in the console
    - in: One or more objects sets
    - out: All input objects"""

    def init(self, context):
        super().init(context)

    def execute(self, context):
        from .mixins import get_input_socket_data, set_output_socket_data
        obs = get_input_socket_data(self.inputs["objects"], context)

        set_output_socket_data(self.outputs["objects"], obs, context)

        for ob in obs:
            print(ob.name)


class WFNodeDryRun(WFOutputNode, WFDebugNode, WFRunnableNode):
    bl_label = "Dry Run"
    bl_description = """Executes the workflow without doing anything"""
    bl_width_default = 300

    def init(self, context):
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.context_pointer_set('target', self)
        op = layout.operator("wf.run_workflow", icon='PLAY', text="")
        op.node_name = self.name
