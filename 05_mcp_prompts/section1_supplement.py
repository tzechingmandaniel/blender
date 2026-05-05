"""Section 1 supplement — fills the gaps after the first executor run.

  - Crops the side-view reference into 10 part references (PIL).
  - Generates a colour-coded paintover.png on the same reference.
  - Adds 4 view-marker cameras to 08_LIGHTING_CAMERA.
  - Re-saves v01_project_setup.blend.
"""
import bpy
import os
import math
from mathutils import Vector

PROJECT_ROOT = r"C:\AK47_NonFunctional_Prop"
BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v01_project_setup.blend")
REF = os.path.join(PROJECT_ROOT, "00_references", "original_image", "ak47_side_reference.png")
CROPS_DIR = os.path.join(PROJECT_ROOT, "00_references", "cropped_parts")
PAINTOVER_DIR = os.path.join(PROJECT_ROOT, "00_references", "paintover_guides")

os.makedirs(CROPS_DIR, exist_ok=True)
os.makedirs(PAINTOVER_DIR, exist_ok=True)


# ---- 1) crop the side reference into 10 named part regions ----
# Approximate per-part ROIs as fractions of the source image (left, top, right, bottom).
# These are PROPORTION GUIDES only — real cropping by hand will be more accurate.
ROIS = {
    "stock_reference.png":           (0.00, 0.20, 0.30, 0.85),
    "receiver_reference.png":        (0.28, 0.10, 0.55, 0.75),
    "dust_cover_reference.png":      (0.32, 0.05, 0.55, 0.40),
    "grip_reference.png":            (0.30, 0.55, 0.45, 1.00),
    "magazine_reference.png":        (0.32, 0.55, 0.55, 1.00),
    "lower_handguard_reference.png": (0.50, 0.30, 0.78, 0.70),
    "upper_handguard_reference.png": (0.52, 0.10, 0.78, 0.40),
    "barrel_front_reference.png":    (0.65, 0.25, 1.00, 0.65),
    "front_sight_reference.png":     (0.85, 0.10, 1.00, 0.50),
    "rear_sight_reference.png":      (0.30, 0.05, 0.42, 0.30),
}

try:
    from PIL import Image, ImageDraw

    src = Image.open(REF).convert("RGBA")
    W, H = src.size
    print(f"reference image: {W}x{H}")

    for filename, (l, t, r, b) in ROIS.items():
        box = (int(l * W), int(t * H), int(r * W), int(b * H))
        crop = src.crop(box)
        crop.save(os.path.join(CROPS_DIR, filename))
    print(f"wrote {len(ROIS)} cropped references")

    # Paintover overlay
    overlay = src.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    PAINTOVER = {
        "receiver":   ((0.28, 0.10, 0.55, 0.55), (255, 30, 30, 110)),
        "stock":      ((0.00, 0.20, 0.30, 0.75), (60, 90, 255, 110)),
        "magazine":   ((0.32, 0.55, 0.55, 1.00), (60, 200, 60, 110)),
        "handguard":  ((0.50, 0.30, 0.78, 0.55), (255, 220, 30, 110)),
        "grip":       ((0.30, 0.60, 0.42, 1.00), (190, 60, 230, 130)),
        "barrel":     ((0.65, 0.30, 0.95, 0.55), (255, 130, 0, 110)),
        "sight":      ((0.85, 0.10, 1.00, 0.45), (0, 220, 230, 110)),
    }
    for name, (rect, colour) in PAINTOVER.items():
        l, t, r, b = rect
        box = (int(l * W), int(t * H), int(r * W), int(b * H))
        draw.rectangle(box, fill=colour, outline=(255, 255, 255, 220), width=3)
        draw.text((box[0] + 8, box[1] + 4), name, fill=(255, 255, 255, 255))
    overlay.save(os.path.join(PAINTOVER_DIR, "paintover_color_coded.png"))
    print("wrote paintover_color_coded.png")
except ImportError:
    print("PIL not available; skipping image cropping/paintover")
except Exception as e:
    print(f"PIL error: {e}")


# ---- 2) load the existing v01 .blend and add the 4 view markers ----
bpy.ops.wm.open_mainfile(filepath=BLEND)


def add_view_camera(name, location, rotation_euler_deg, lens=50, ortho=False):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.name = name
    cam.rotation_euler = tuple(math.radians(d) for d in rotation_euler_deg)
    cam.data.lens = lens
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = 1.4
    # Move to 08_LIGHTING_CAMERA
    target = bpy.data.collections.get("08_LIGHTING_CAMERA")
    if target:
        for c in list(cam.users_collection):
            c.objects.unlink(cam)
        target.objects.link(cam)
    return cam


# Per Section 1.11.1 — modelling view bookmarks (cameras you can switch to via Numpad 0)
add_view_camera("VIEW_side_modeling",   ( 0.0, -1.20, 0.0),  (90, 0, 0),    lens=50, ortho=True)
add_view_camera("VIEW_top_check",       ( 0.0,  0.0,  1.20), ( 0, 0, 0),    lens=50, ortho=True)
add_view_camera("VIEW_front_check",     (-1.20, 0.0,  0.0),  (90, 0, -90),  lens=50, ortho=True)
add_view_camera("VIEW_3quarter_preview",( 0.65, -0.85, 0.30),(78, 0,  38),  lens=70, ortho=False)
print("4 view markers added")

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print(f"saved: {BLEND}")
