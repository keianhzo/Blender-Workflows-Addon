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

![Screenshot](https://github.com/user-attachments/assets/79b6a6e1-6213-49b5-995a-be1862feac53)
![Screenshot](https://github.com/user-attachments/assets/041b41fb-9bcb-4276-8466-2401b855260c)
![Screenshot](https://github.com/user-attachments/assets/84432990-4988-4478-b0be-048d47068e2c)