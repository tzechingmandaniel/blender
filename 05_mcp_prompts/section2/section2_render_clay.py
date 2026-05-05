"""Render side + 3/4 clay previews of the blockout into 04_renders/clay_renders.
Uses Cycles with the placeholder materials so we get a colour-coded clay shot."""
import bpy
import os
import math

PROJECT_ROOT = r"C:\AK47_NonFunctional_Prop"
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "clay_renders")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.render.resolution_x = 1400
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"

# Hide reference image and guides for the clay render
HIDE = ["REF_ak47_side_view"] + [
    o.name for o in bpy.data.collections.get("01_GUIDES").objects
    if bpy.data.collections.get("01_GUIDES")
]
prev_states = {}
for name in HIDE:
    obj = bpy.data.objects.get(name)
    if obj:
        prev_states[name] = obj.hide_render
        obj.hide_render = True

# World
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.20, 0.21, 0.24, 1.0)
bg.inputs["Strength"].default_value = 0.55
links.new(bg.outputs["Background"], out.inputs["Surface"])

# Push existing lights up a touch
for nm, e in (("Area_Light_Key", 60), ("Area_Light_Fill", 25)):
    lt = bpy.data.objects.get(nm)
    if lt:
        lt.data.energy = e


def render_from(camera_name, filename):
    cam = bpy.data.objects.get(camera_name)
    if not cam:
        print(f"  cam not found: {camera_name}")
        return
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_DIR, filename)
    bpy.ops.render.render(write_still=True)
    print(f"  rendered {camera_name} -> {filename}")


# Two angles: 3/4 preview + side modeling
render_from("CAM_preview_3quarter", "v02_blockout_3quarter.png")

# Override side view camera lens for a tighter framing
side = bpy.data.objects.get("VIEW_side_modeling")
if side:
    side.data.type = "ORTHO"
    side.data.ortho_scale = 1.10
    render_from("VIEW_side_modeling", "v02_blockout_side.png")

# Restore
for name, prev in prev_states.items():
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = prev
print("done")
