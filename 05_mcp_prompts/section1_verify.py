"""Verify v01_project_setup.blend matches the Section 1 deliverables."""
import bpy

EXPECTED_COLLECTIONS = [
    "00_REFERENCE", "01_GUIDES", "02_BLOCKOUT", "03_MAJOR_PARTS",
    "04_MINOR_PARTS", "05_DETAIL_PARTS", "06_MATERIAL_TESTS",
    "07_ASSEMBLY", "08_LIGHTING_CAMERA", "09_EXPORT_READY",
]

EXPECTED_MATERIALS = [
    "MAT_placeholder_dark_metal", "MAT_placeholder_black_metal",
    "MAT_placeholder_dark_wood", "MAT_placeholder_bakelite_grip",
    "MAT_placeholder_rubber_dark", "MAT_placeholder_reference_blue",
    "MAT_placeholder_guide_wire", "MAT_placeholder_neutral_clay",
]

print("\n=== PRE-BLOCKOUT CHECKLIST ===")
results = []

# units
us = bpy.context.scene.unit_settings
ok = us.system == "METRIC" and abs(us.scale_length - 1.0) < 1e-6
results.append(("metric units, scale 1.0", ok))

# default cube removed
has_default_cube = "Cube" in bpy.data.objects and bpy.data.objects["Cube"].type == "MESH"
results.append(("default cube removed", not has_default_cube))

# collections
missing_c = [c for c in EXPECTED_COLLECTIONS if c not in bpy.data.collections]
results.append(("10 collections", not missing_c))
if missing_c:
    print(f"  missing collections: {missing_c}")

# materials
missing_m = [m for m in EXPECTED_MATERIALS if m not in bpy.data.materials]
results.append(("8 placeholder materials", not missing_m))
if missing_m:
    print(f"  missing materials: {missing_m}")

# reference image
ref = bpy.data.objects.get("REF_ak47_side_view")
ref_ok = ref is not None and ref.hide_select
results.append(("reference image locked", ref_ok))

# guide bounding box + centerline
guide_box = bpy.data.objects.get("GUIDE_overall_length_box")
centerline = bpy.data.objects.get("GUIDE_centerline")
results.append(("overall length box + centerline", guide_box is not None and centerline is not None))

# camera
cam = bpy.data.objects.get("CAM_preview_3quarter")
results.append(("CAM_preview_3quarter", cam is not None and cam.type == "CAMERA"))

# lights
key = bpy.data.objects.get("Area_Light_Key")
fill = bpy.data.objects.get("Area_Light_Fill")
results.append(("Area_Light_Key + Area_Light_Fill", key is not None and fill is not None))

# 4 view markers (1.11.1)
view_markers = ["VIEW_side_modeling", "VIEW_top_check", "VIEW_front_check", "VIEW_3quarter_preview"]
missing_v = [v for v in view_markers if v not in bpy.data.objects]
results.append(("4 view marker cameras", not missing_v))
if missing_v:
    print(f"  missing view markers: {missing_v}")

# print checklist
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False

print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

# Object list summary
print(f"total objects: {len(bpy.data.objects)}")
for c in EXPECTED_COLLECTIONS:
    if c in bpy.data.collections:
        n = len(bpy.data.collections[c].objects)
        print(f"  {c}: {n} objects")
