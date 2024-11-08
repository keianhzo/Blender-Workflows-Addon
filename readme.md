# Blender Workflows Add-On
A Node Graph-Based Solution for Streamlined Blender Tasks

This add-on introduces a node-based system to simplify complex or repetitive tasks in Blender, especially those that require fine control. Designed to automate time-consuming processes I often handle manually or through scripts—primarily scene exporting—this add-on helps users define workflows that sequentially execute specified actions on any set of objects, producing efficient outputs.

A key application is optimizing workflows for exporting high- and low-poly versions of objects to other software. For example, I often need a low-poly export with certain modifiers removed and a specific naming convention, alongside a high-poly version with other modifiers and a different suffix. While achievable through collection exporter configurations, manual renaming, and scripts, a node-based workflow is far more manageable and user-friendly.

Currently, the nodes focus on export tasks, but future updates may expand functionality to support pre-rendering, post-import processing, and more. This add-on is still in development (WIP) and not yet ready for production use, so use with caution. I’m iterating based on my workflow needs and welcome suggestions for new features—please open an issue if you have ideas for broadly useful enhancements.

⚠️ **Note:** This add-on updates your scene during workflow execution and then reverts the changes. However, some modifications may not fully revert. Always save your scene before running workflows and verify the reversion before saving again.

![Captura de pantalla 2024-11-07 160159](https://github.com/user-attachments/assets/e7ff6128-00b2-45ba-93f1-345a218a13fe)

## Examples
[Here](https://github.com/keianhzo/Blender-Workflows-Addon/wiki/Examples)

## Supported tasks
- Export glTF, OBJ and FBX
- Translate objects to work or other object position
- Make instances real
- Join objects
- Apply all modifiers or selectively by type/name
- Change the active UV map
- Filter object sets by string or regex
- Add prefix/suffix to object/data names
- Add/remove objects to/from sets

## Installation
Download this repo as a zip file and install the add-on.

## Usage
1. Open the Workflows editor type using the dropdown menu:
   
![Captura de pantalla 2024-10-28 163659](https://github.com/user-attachments/assets/e056e283-ac95-4ac0-b85e-8bac998adb81)

2. Create a new Workflows graph using the "New" button:

![Captura de pantalla 2024-10-28 164001](https://github.com/user-attachments/assets/43e9b50c-cfcf-4248-a963-21b57479ae4e)

3. Add an input node suing "Shift + A" or the "Add" menu. Use the "Scene Input" node for this example:

![Captura de pantalla 2024-10-28 164208](https://github.com/user-attachments/assets/582b29ee-0212-4bdb-b3ae-8adb021a5f2c)

4. Select the current scene as the input scene.
5. Add an output node, select and output file and link the input and output nodes. You can use either the "glTF Export" or the "FBX Export" nodes:

![Captura de pantalla 2024-10-28 164424](https://github.com/user-attachments/assets/a93338c6-c5e5-423a-b749-81eb0cfffeee)

6. Run the Workflow clicking on the "Play" button on the output node. If you have multiple output nodes in one workflow you can batch them using the "Run All Workflows" button:

![Captura de pantalla 2024-10-28 164530](https://github.com/user-attachments/assets/a74f21f4-2b5f-49d0-b964-25a6b3f0e5c8)
