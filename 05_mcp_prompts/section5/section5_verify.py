"""Verify v05_uv_materials.blend matches the §5.20 + §5.21 checklists."""
import bpy


EXPECTED_FINAL_MATERIALS = [
    "MAT_metal_dark_blued",
    "MAT_metal_black_magazine",
    "MAT_wood_dark_reddish",
    "MAT_grip_dark_bakelite",
    "MAT_edge_wear_light_metal",
    "MAT_shadow_seam_dark",
    "MAT_rubber_dark_optional",
]

# Expected (object → final material) for the main visible AK_ parts
EXPECTED_MATERIAL_FOR = {
    "AK_receiver_main":             "MAT_metal_dark_blued",
    "AK_dustcover_main":            "MAT_metal_dark_blued",
    "AK_barrel_outer_closed":       "MAT_metal_dark_blued",
    "AK_gas_tube_outer":            "MAT_metal_dark_blued",
    "AK_gas_block_visual":          "MAT_metal_dark_blued",
    "AK_front_sight_block_visual":  "MAT_metal_dark_blued",
    "AK_front_ring_visual":         "MAT_metal_dark_blued",
    "AK_rear_sight_visual":         "MAT_metal_dark_blued",
    "AK_trigger_guard_visual":      "MAT_metal_dark_blued",
    "AK_magazine_main":             "MAT_metal_black_magazine",
    "AK_stock_main":                "MAT_wood_dark_reddish",
    "AK_handguard_lower_main":      "MAT_wood_dark_reddish",
    "AK_handguard_upper_main":      "MAT_wood_dark_reddish",
    "AK_grip_main":                 "MAT_grip_dark_bakelite",
}

# Seam objects should all be MAT_shadow_seam_dark
EXPECTED_SEAM_MATERIAL = "MAT_shadow_seam_dark"

# Section 3 invariants we must not have broken
SECTION_3_AK_INVARIANT = list(EXPECTED_MATERIAL_FOR.keys())

# Section 4 invariants
SECTION_4_SAMPLE_DETAILS = [
    "AK_rivet_receiver_001", "AK_rib_dustcover_001",
    "AK_groove_magazine_001", "AK_wood_contour_stock_001",
    "AK_groove_grip_001", "AK_loop_sling_rear_visual",
    "AK_ring_barrel_visual_001", "AK_detail_rearsight_001",
]


print("\n=== §5.20 + §5.21 UV + MATERIALS REVIEW ===")
results = []


# --- 7 final materials exist ---
missing_mats = [m for m in EXPECTED_FINAL_MATERIALS if m not in bpy.data.materials]
results.append(("7 final MAT_ materials exist", not missing_mats))
if missing_mats:
    print(f"  missing materials: {missing_mats}")


# --- Material assignment correct on main visible parts ---
wrong = []
for name, expected in EXPECTED_MATERIAL_FOR.items():
    o = bpy.data.objects.get(name)
    if not o or not o.data.materials or o.data.materials[0] is None:
        wrong.append(f"{name}: no material")
        continue
    actual = o.data.materials[0].name
    if actual != expected:
        wrong.append(f"{name}: {actual} (expected {expected})")
results.append(("main AK_ parts have correct final material", not wrong))
if wrong:
    for w in wrong:
        print(f"  {w}")


# --- All AK_seam_* objects use MAT_shadow_seam_dark ---
seam_wrong = []
for o in bpy.data.objects:
    if not o.name.startswith("AK_seam_"):
        continue
    if not o.data.materials or o.data.materials[0] is None:
        seam_wrong.append(f"{o.name}: no material")
        continue
    actual = o.data.materials[0].name
    if actual != EXPECTED_SEAM_MATERIAL:
        seam_wrong.append(f"{o.name}: {actual} (expected {EXPECTED_SEAM_MATERIAL})")
results.append(("AK_seam_* use MAT_shadow_seam_dark", not seam_wrong))
if seam_wrong:
    for w in seam_wrong:
        print(f"  {w}")


# --- No AK_ object still references a MAT_placeholder_* material ---
still_placeholder = []
for o in bpy.data.objects:
    if not (o.type == "MESH" and o.name.startswith("AK_")):
        continue
    for slot in o.data.materials:
        if slot is None:
            continue
        if slot.name.startswith("MAT_placeholder_"):
            still_placeholder.append(f"{o.name} -> {slot.name}")
            break
results.append(("no AK_ object still uses MAT_placeholder_", not still_placeholder))
if still_placeholder:
    for s in still_placeholder:
        print(f"  {s}")


# --- Every AK_ mesh has a uv_layer ---
no_uvs = []
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.startswith("AK_"):
        if not o.data.uv_layers:
            no_uvs.append(o.name)
results.append(("every AK_ mesh has a uv_layer", not no_uvs))
if no_uvs:
    print(f"  no UV layer: {no_uvs[:5]}{'…' if len(no_uvs) > 5 else ''}")


# --- Section 3 invariants (parts still exist) ---
missing_s3 = [n for n in SECTION_3_AK_INVARIANT if n not in bpy.data.objects]
results.append(("Section 3 AK_ refined parts still present", not missing_s3))


# --- Section 4 invariants (sample of details still exist) ---
missing_s4 = [n for n in SECTION_4_SAMPLE_DETAILS if n not in bpy.data.objects]
results.append(("Section 4 detail objects still present (sample)", not missing_s4))


# --- BLK_ backups still in 03H_major_part_backup ---
backup = bpy.data.collections.get("03H_major_part_backup")
results.append(("Section 3 BLK_ backup collection still exists", backup is not None))


# --- AK47_MASTER_ASSET still parents all AK_ ---
master = bpy.data.objects.get("AK47_MASTER_ASSET")
results.append(("AK47_MASTER_ASSET still exists", master is not None))


# --- Final ---
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False
print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")


# Summary
ak_total = sum(1 for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_"))
uvs_ok = sum(1 for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_") and o.data.uv_layers)
print(f"AK_ meshes: {ak_total};  with uv_layer: {uvs_ok}")

# Material usage summary
mat_usage = {}
for o in bpy.data.objects:
    if o.type != "MESH" or not o.name.startswith("AK_"):
        continue
    if not o.data.materials or o.data.materials[0] is None:
        continue
    nm = o.data.materials[0].name
    mat_usage[nm] = mat_usage.get(nm, 0) + 1
print("Material usage on AK_ objects:")
for nm, count in sorted(mat_usage.items()):
    print(f"  {nm}: {count}")
