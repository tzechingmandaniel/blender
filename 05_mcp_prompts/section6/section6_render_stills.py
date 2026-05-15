"""Render the 11 portfolio still frames from v06_final_assembly.blend into
04_renders/final/. Auto-detects repo root from __file__."""
import bpy
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "final")
os.makedirs(OUT_DIR, exist_ok=True)


# Render assignments per §7.14
STILLS = [
    ("CAM_final_side_profile",       "render_01_side_profile.png"),
    ("CAM_final_front_3quarter",     "render_02_front_3quarter_hero.png"),
    ("CAM_final_rear_3quarter",      "render_03_rear_3quarter.png"),
    ("CAM_final_top_angle",          "render_04_top_angle.png"),
    ("CAM_closeup_receiver",         "render_05_closeup_receiver_metal.png"),
    ("CAM_closeup_wood_stock",       "render_06_closeup_wood_stock.png"),
    ("CAM_closeup_handguard",        "render_07_closeup_handguard_wood.png"),
    ("CAM_closeup_magazine",         "render_08_closeup_magazine.png"),
    ("CAM_closeup_front_sight",      "render_09_closeup_front_sight_visual.png"),
    ("CAM_closeup_grip",             "render_10_closeup_grip.png"),
    ("CAM_closeup_material_edgewear", "render_11_closeup_edgewear.png"),
]

scene = bpy.context.scene
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.cycles.samples = 128

print(f"\n=== SECTION 6 — STILLS RENDER ({len(STILLS)} frames) ===")
print(f"  out: {OUT_DIR}")

failed = []
for cam_name, file_name in STILLS:
    cam = bpy.data.objects.get(cam_name)
    if cam is None:
        print(f"  SKIP {file_name}: camera {cam_name} missing")
        failed.append(file_name)
        continue
    scene.camera = cam
    out_path = os.path.join(OUT_DIR, file_name)
    scene.render.filepath = out_path
    try:
        bpy.ops.render.render(write_still=True)
        size_kb = os.path.getsize(out_path) // 1024 if os.path.exists(out_path) else 0
        print(f"  done {file_name}  ({size_kb} KB)")
    except Exception as e:
        print(f"  FAIL {file_name}: {e}")
        failed.append(file_name)

print(f"\n=== {'ALL DONE' if not failed else f'{len(failed)} FAILED'} ===")
if failed:
    for f in failed:
        print(f"  failed: {f}")
