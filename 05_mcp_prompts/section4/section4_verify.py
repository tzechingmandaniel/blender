"""Verify v04_minor_details.blend matches the §4.29 final review checklist."""
import bpy

EXPECTED_SUBCOLLS = [
    "04A_receiver_details",
    "04B_dustcover_details",
    "04C_magazine_details",
    "04D_wood_details",
    "04E_grip_details",
    "04F_sight_front_details",
    "04G_sling_loop_visuals",
    "04H_seams_and_edge_wear_placeholders",
    "04Z_detail_tests_archive",
]

DENSITY_CAPS = {
    "04A_receiver_details": 11,
    "04B_dustcover_details": 5,
    "04C_magazine_details": 7,
    "04D_wood_details": 9,
    "04E_grip_details": 4,
    "04F_sight_front_details": 3,
    "04G_sling_loop_visuals": 2,
    "04H_seams_and_edge_wear_placeholders": 10,
    "04Z_detail_tests_archive": 0,
}

# Major parts from Section 3 must still be present
AK_MAJOR_PARTS = [
    "AK_receiver_main",
    "AK_stock_main",
    "AK_magazine_main",
    "AK_grip_main",
    "AK_handguard_lower_main",
    "AK_handguard_upper_main",
    "AK_barrel_exterior_main",
    "AK_dustcover_main",
]

# Blockout parts from Section 2 must still be preserved
BLK_PARTS = [
    "BLK_receiver_main",
    "BLK_stock_main",
    "BLK_grip_main",
    "BLK_magazine_main",
    "BLK_handguard_lower",
    "BLK_handguard_upper",
    "BLK_gas_tube_outer",
    "BLK_barrel_outer_closed",
    "BLK_dustcover_main",
    "BLK_front_sight_block_visual",
    "BLK_gas_block_visual",
    "BLK_front_ring_visual",
    "BLK_rear_sight_visual",
    "BLK_trigger_guard_visual",
]

DETAIL_KEYWORDS = ("rivet", "panel", "rib", "seam", "groove", "spine",
                   "contour", "loop", "wear", "cap", "ring")

print("\n=== §4.29 FINAL REVIEW CHECKLIST ===")
results = []

# 04_MINOR_PARTS + sub-collections exist
mp = bpy.data.collections.get("04_MINOR_PARTS")
results.append(("04_MINOR_PARTS collection exists", mp is not None))
missing_subs = []
mp_child_names = {c.name for c in (mp.children if mp else [])}
for s in EXPECTED_SUBCOLLS:
    if s not in mp_child_names:
        missing_subs.append(s)
results.append(("9 sub-collections under 04_MINOR_PARTS exist", not missing_subs))
if missing_subs:
    print(f"  missing sub-collections: {missing_subs}")

# New materials exist
shadow = bpy.data.materials.get("MAT_placeholder_shadow_seam")
edge = bpy.data.materials.get("MAT_placeholder_edge_wear")
results.append(("MAT_placeholder_shadow_seam exists", shadow is not None))
results.append(("MAT_placeholder_edge_wear exists", edge is not None))

# Major parts still in 03_MAJOR_PARTS
mp3 = bpy.data.collections.get("03_MAJOR_PARTS")
results.append(("03_MAJOR_PARTS collection still exists", mp3 is not None))
missing_majors = []
if mp3:
    mp3_names = {o.name for o in mp3.objects}
    for n in AK_MAJOR_PARTS:
        if n not in mp3_names:
            missing_majors.append(n)
results.append(("all 8 AK_ major parts still in 03_MAJOR_PARTS", not missing_majors))
if missing_majors:
    print(f"  missing major parts: {missing_majors}")

# BLK_ blockout objects still preserved
missing_blk = [n for n in BLK_PARTS if n not in bpy.data.objects]
results.append(("all BLK_ blockout objects preserved", not missing_blk))
if missing_blk:
    print(f"  missing BLK_: {missing_blk}")

# Per-collection density caps
detail_objects = []
density_ok = True
for sc_name in EXPECTED_SUBCOLLS:
    coll = bpy.data.collections.get(sc_name)
    if coll is None:
        continue
    n = len(coll.objects)
    cap = DENSITY_CAPS[sc_name]
    if n > cap:
        density_ok = False
        print(f"  {sc_name}: {n} objects, cap {cap}")
    detail_objects.extend(coll.objects)
results.append(("each sub-collection within density cap", density_ok))

# Total detail count <= 51 (sum of per-collection caps in §4.4)
total = len(detail_objects)
results.append((f"total detail objects <= 51 (got {total})", total <= 51))

# Naming: AK_ prefix + has a detail keyword
bad_naming = []
for o in detail_objects:
    if not o.name.startswith("AK_"):
        bad_naming.append(o.name)
        continue
    low = o.name.lower()
    if not any(k in low for k in DETAIL_KEYWORDS):
        bad_naming.append(o.name)
results.append(("all details use AK_ + detail keyword", not bad_naming))
if bad_naming:
    print(f"  bad names: {bad_naming}")

# Every detail has Bevel modifier
no_bevel = [o.name for o in detail_objects if not any(m.type == "BEVEL" for m in o.modifiers)]
results.append(("Bevel modifier on every detail", not no_bevel))
if no_bevel:
    print(f"  missing bevel on: {no_bevel}")

# Every detail has at least one material
no_mat = [o.name for o in detail_objects if not o.data.materials]
results.append(("every detail has a material", not no_mat))
if no_mat:
    print(f"  no material on: {no_mat}")

# Every detail parented to AK47_MASTER_ASSET
master = bpy.data.objects.get("AK47_MASTER_ASSET")
results.append(("AK47_MASTER_ASSET still exists", master is not None))
unparented = []
if master:
    for o in detail_objects:
        if o.parent is not master:
            unparented.append(o.name)
results.append(("every detail parented to AK47_MASTER_ASSET", not unparented))
if unparented:
    print(f"  unparented details: {unparented}")

# 04Z_detail_tests_archive hidden
arch = bpy.data.collections.get("04Z_detail_tests_archive")
if arch is not None:
    results.append(("04Z_detail_tests_archive hide_render = True", arch.hide_render))
    results.append(("04Z_detail_tests_archive hide_viewport = True", arch.hide_viewport))

# Print checklist
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False

print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

# Summary
print(f"04_MINOR_PARTS total objects: {len(detail_objects)}")
for sc_name in EXPECTED_SUBCOLLS:
    coll = bpy.data.collections.get(sc_name)
    if coll is None:
        continue
    print(f"  {sc_name}: {len(coll.objects)}")
    for o in coll.objects:
        mat = o.data.materials[0].name if o.data.materials else "<none>"
        print(f"    - {o.name} ({len(o.data.vertices)}v, mat={mat})")
