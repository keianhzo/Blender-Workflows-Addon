# Blender Workflows Add-On
A Node Graph-Based Solution for Streamlined Blender Tasks

This add-on introduces a node graph system to simplify certain Blender tasks requiring granular control. I've designed it to streamline processes I frequently handle manually or through scripts, particularly when exporting scenes.

Some of the tasks this add-on automates for scene export include:
- Merging multiple high-poly meshes into a single mesh before export
- Adding prefixes or suffixes to objects and meshes
- Moving objects to specific positions before export
- Exporting different collections or objects into separate files
- Defining sets of objects and collections to export together
- Selectively applying modifiers during export

While this add-on helps automate repetitive tasks, it is currently a work-in-progress (WIP) and not feature-complete or production-ready, so use it at your own risk. I plan to expand its features based on my own needs, so comprehensive functionality may take time. If you have feature suggestions, feel free to open an issue—I’m open to adding useful, broadly applicable features.

⚠️ **Note:** This add-on updates the scene with each execution step and reverts changes afterward. However, in some cases, it may fail to fully revert modifications, potentially leaving your scene altered. Always save your scene before running workflows and verify that the scene reverts correctly before saving again.

![Captura de pantalla 2024-11-07 160159](https://github.com/user-attachments/assets/e7ff6128-00b2-45ba-93f1-345a218a13fe)


# Installation
Download this repo as a zip file and install the add-on.

# Usage
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
