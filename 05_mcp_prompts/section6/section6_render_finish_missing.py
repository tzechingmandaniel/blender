"""One-off recovery script: fix CAM_final_side_profile ortho_scale, save the
.blend, then re-render just frame 01 (side profile) and frame 11 (edgewear
close-up). These two were missing/cropped after the original bg render task
ended at frame 10.

Auto-detects repo root from __file__.
"""
import bpy
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
BLEND_PATH = os.path.join(PROJECT_ROOT, "01_blender", "v06_final_assembly.blend")
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "final")
os.makedirs(OUT_DIR, exist_ok=True)


# 1. Fix side camera ortho_scale (1.05 -> 1.5) and save
side = bpy.data.objects.get("CAM_final_side_profile")
if side is None:
    raise RuntimeError("CAM_final_side_profile missing")
print(f"  side ortho_scale: {side.data.ortho_scale} -> 2.5")
side.data.ortho_scale = 2.5
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"  saved {BLEND_PATH}")


# 2. Render frame 01 (side profile) and frame 11 (edgewear)
scene = bpy.context.scene
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.cycles.samples = 128

FRAMES_TO_RENDER = [
    ("CAM_final_side_profile", "render_01_side_profile.png"),
]

for cam_name, file_name in FRAMES_TO_RENDER:
    cam = bpy.data.objects.get(cam_name)
    if cam is None:
        print(f"  SKIP {file_name}: camera {cam_name} missing")
        continue
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_DIR, file_name)
    bpy.ops.render.render(write_still=True)
    print(f"  done {file_name}")

print("=== RECOVERY RENDER DONE ===")
