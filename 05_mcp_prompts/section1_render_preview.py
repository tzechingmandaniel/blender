"""Render a preview from the v01_project_setup.blend so we can confirm the
camera, lighting, guides, and reference image are placed correctly."""
import bpy
import os

OUT = r"C:\AK47_NonFunctional_Prop\04_renders\viewport_tests\v01_setup_preview.png"

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.render.resolution_x = 1000
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"

# Use the placeholder camera
cam = bpy.data.objects.get("CAM_preview_3quarter")
if cam:
    scene.camera = cam

# A neutral world so we can see the wireframes against grey
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.18, 0.18, 0.20, 1.0)
bg.inputs["Strength"].default_value = 0.5
links.new(bg.outputs["Background"], out.inputs["Surface"])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print(f"rendered: {OUT}")
