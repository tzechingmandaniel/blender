"""Standalone PIL script: crop side reference into 10 part images and create a
colour-coded paintover. Uses system Python 3.11's Pillow (Blender's bundled
Python doesn't ship with PIL)."""
import os
from PIL import Image, ImageDraw

PROJECT_ROOT = r"C:\AK47_NonFunctional_Prop"
REF = os.path.join(PROJECT_ROOT, "00_references", "original_image", "ak47_side_reference.png")
CROPS_DIR = os.path.join(PROJECT_ROOT, "00_references", "cropped_parts")
PAINTOVER_DIR = os.path.join(PROJECT_ROOT, "00_references", "paintover_guides")

os.makedirs(CROPS_DIR, exist_ok=True)
os.makedirs(PAINTOVER_DIR, exist_ok=True)

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

src = Image.open(REF).convert("RGBA")
W, H = src.size
print(f"reference: {W}x{H}")

for filename, (l, t, r, b) in ROIS.items():
    box = (int(l * W), int(t * H), int(r * W), int(b * H))
    src.crop(box).save(os.path.join(CROPS_DIR, filename))
print(f"wrote {len(ROIS)} cropped references")

overlay = src.copy()
draw = ImageDraw.Draw(overlay, "RGBA")
PAINTOVER = {
    "receiver":  ((0.28, 0.10, 0.55, 0.55), (255, 30, 30, 110)),
    "stock":     ((0.00, 0.20, 0.30, 0.75), (60, 90, 255, 110)),
    "magazine":  ((0.32, 0.55, 0.55, 1.00), (60, 200, 60, 110)),
    "handguard": ((0.50, 0.30, 0.78, 0.55), (255, 220, 30, 110)),
    "grip":      ((0.30, 0.60, 0.42, 1.00), (190, 60, 230, 130)),
    "barrel":    ((0.65, 0.30, 0.95, 0.55), (255, 130, 0, 110)),
    "sight":     ((0.85, 0.10, 1.00, 0.45), (0, 220, 230, 110)),
}
for name, (rect, colour) in PAINTOVER.items():
    l, t, r, b = rect
    box = (int(l * W), int(t * H), int(r * W), int(b * H))
    draw.rectangle(box, fill=colour, outline=(255, 255, 255, 220), width=3)
    draw.text((box[0] + 8, box[1] + 4), name, fill=(255, 255, 255, 255))
overlay.save(os.path.join(PAINTOVER_DIR, "paintover_color_coded.png"))
print("wrote paintover_color_coded.png")
