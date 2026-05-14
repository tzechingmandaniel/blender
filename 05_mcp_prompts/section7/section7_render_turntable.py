"""Render a low-resolution 12-frame turntable preview into
04_renders/final/turntable_frames/.

The full 180-frame 1920x1080 turntable render is deferred to Phase 8
packaging (would take ~90 min at samples=96). This preview confirms the
animation set-up works.

EMPTY_turntable_center is keyframed in section7_executor.py (rotation_z
0 -> 2π linear over frames 1..180). We render frames 1, 16, 31, 46, 61,
76, 91, 106, 121, 136, 151, 166 — every 15° step.
"""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "final",
                       "turntable_frames")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32  # preview-only
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"

# Neutral world
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out_n = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.15, 0.16, 0.18, 1.0)
bg.inputs["Strength"].default_value = 0.20
links.new(bg.outputs["Background"], out_n.inputs["Surface"])

cam = bpy.data.objects.get("CAM_turntable_main")
if cam is None:
    print("ERROR: CAM_turntable_main not found")
    raise SystemExit(1)
scene.camera = cam

# 12-frame preview (every 15 frames in the 1..180 range)
FRAMES = [1, 16, 31, 46, 61, 76, 91, 106, 121, 136, 151, 166]
for f in FRAMES:
    scene.frame_set(f)
    scene.render.filepath = os.path.join(OUT_DIR, f"frame_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"  rendered frame {f:04d}")

print("done")
