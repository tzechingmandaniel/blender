"""Render side + 3/4 previews of v05_uv_materials with the new final materials.
This is the §5.18 test render. Auto-detects repo root from __file__."""
import bpy
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "clay_renders")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 64  # bumped a bit for the material preview
scene.render.resolution_x = 1400
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"


HIDE_NAMES = ["REF_ak47_side_view"]
guides_coll = bpy.data.collections.get("01_GUIDES")
if guides_coll:
    HIDE_NAMES += [o.name for o in guides_coll.objects]
backup_coll = bpy.data.collections.get("03H_major_part_backup")
if backup_coll:
    HIDE_NAMES += [o.name for o in backup_coll.objects]

prev = {}
for name in HIDE_NAMES:
    obj = bpy.data.objects.get(name)
    if obj is not None:
        prev[name] = obj.hide_render
        obj.hide_render = True


# Studio world
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.22, 0.23, 0.26, 1.0)
bg.inputs["Strength"].default_value = 0.65
links.new(bg.outputs["Background"], out.inputs["Surface"])


# Stronger key for the material preview
for nm, e in (("Area_Light_Key", 90), ("Area_Light_Fill", 35)):
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


render_from("CAM_preview_3quarter", "v05_uv_materials_3quarter.png")

side = bpy.data.objects.get("VIEW_side_modeling")
if side:
    side.data.type = "ORTHO"
    side.data.ortho_scale = 1.10
    render_from("VIEW_side_modeling", "v05_uv_materials_side.png")


for name, p in prev.items():
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.hide_render = p

print("done")
