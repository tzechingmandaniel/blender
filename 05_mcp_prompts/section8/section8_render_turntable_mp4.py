"""Render the full 180-frame turntable as a PNG sequence (Blender 5.x's
file_format enum no longer includes FFMPEG for image_settings). The
sequence is rendered into a temp folder; section8_encode_mp4.py picks it
up and encodes the MP4 via imageio-ffmpeg.

Settings:
  resolution : 1280 x 720
  samples    : 32
  fps        : 24 (used by the encode step)
  frames     : 1..180  (matches keyframes set in Phase 7)
"""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT",
                              r"C:\AK47_NonFunctional_Prop")
OUT_DIR = os.path.join(PROJECT_ROOT, "final_delivery", "05_turntable",
                       "turntable_full_seq")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene

turntable = bpy.data.objects.get("EMPTY_turntable_center")
if turntable is None:
    print("ERROR: EMPTY_turntable_center not found")
    raise SystemExit(1)
cam = bpy.data.objects.get("CAM_turntable_main")
if cam is None:
    print("ERROR: CAM_turntable_main not found")
    raise SystemExit(1)
scene.camera = cam

# Eevee is dramatically faster than Cycles for animations; it's the
# standard pick for turntable previews. Quality is more than sufficient
# at portfolio resolution for a 180-frame loop.
# Blender 5.x has EEVEE_NEXT as the new engine ID; fall back to BLENDER_EEVEE
# for older builds.
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE"
# Eevee samples are render samples (not Cycles light samples)
if hasattr(scene, "eevee"):
    if hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 32
    if hasattr(scene.eevee, "use_gtao"):
        scene.eevee.use_gtao = True   # ambient occlusion driven by geometry
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 180
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"

# Hide guides/reference/blockout
HIDE_OBJECTS = ["REF_ak47_side_view"]
for coll_name in ("01_GUIDES", "02_BLOCKOUT",
                  "04Z_detail_tests_archive", "06_MATERIAL_TESTS"):
    coll = bpy.data.collections.get(coll_name)
    if coll:
        HIDE_OBJECTS += [o.name for o in coll.objects]
for name in HIDE_OBJECTS:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = True

for nm in ("LIGHT_lookdev_key_soft", "LIGHT_lookdev_fill_soft",
           "LIGHT_lookdev_rim_subtle"):
    o = bpy.data.objects.get(nm)
    if o is not None:
        o.hide_render = True

# Neutral grey world
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out_node = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.18, 0.19, 0.22, 1.0)
bg.inputs["Strength"].default_value = 0.20
links.new(bg.outputs["Background"], out_node.inputs["Surface"])


# PNG sequence output
scene.render.image_settings.file_format = "PNG"
# Blender expands #### into zero-padded frame numbers
scene.render.filepath = os.path.join(OUT_DIR, "frame_####")

print(f"\n=== TURNTABLE PNG SEQUENCE RENDER ===")
print(f"  output    : {OUT_DIR}/frame_####.png")
print(f"  resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"  samples   : {scene.cycles.samples}")
print(f"  frames    : {scene.frame_start}..{scene.frame_end} @ {scene.render.fps} fps")
print()

bpy.ops.render.render(animation=True)

# Count what we got
pngs = [f for f in os.listdir(OUT_DIR) if f.endswith(".png")]
print(f"\nDONE: rendered {len(pngs)} PNG frames into {OUT_DIR}")
