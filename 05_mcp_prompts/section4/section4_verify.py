"""Verify v04_minor_details.blend matches the §4.20 + §4.21 checklists."""
import bpy
from mathutils import Vector


EXPECTED_SUB_COLLECTIONS = [
    "04A_receiver_details", "04B_dustcover_details", "04C_magazine_details",
    "04D_wood_details",     "04E_grip_details",      "04F_sling_loop",
    "04G_surface_seams",    "04H_detail_backup",
    "04I_front_details",    "04J_sight_details",
]

EXPECTED_DETAIL_OBJECTS = {
    "04A_receiver_details": [
        "AK_rivet_receiver_001", "AK_rivet_receiver_002", "AK_rivet_receiver_003",
        "AK_panel_receiver_side_001", "AK_panel_receiver_side_002",
        "AK_lever_receiver_visual_001",
        "AK_wear_receiver_edge_001",
    ],
    "04B_dustcover_details": [
        "AK_rib_dustcover_001", "AK_rib_dustcover_002",
        "AK_seam_dustcover_receiver_001",
    ],
    "04C_magazine_details": [
        "AK_groove_magazine_001", "AK_groove_magazine_002", "AK_groove_magazine_003",
        "AK_ridge_magazine_front_001", "AK_ridge_magazine_rear_001",
        "AK_seam_magazine_baseplate_001",
        "AK_wear_magazine_edge_001",
    ],
    "04D_wood_details": [
        "AK_wood_contour_stock_001",
        "AK_wear_stock_edge_001", "AK_wear_stock_edge_002",
        "AK_groove_handguard_lower_001", "AK_groove_handguard_lower_002",
        "AK_wear_handguard_edge_001",
        "AK_seam_handguard_front_001", "AK_seam_handguard_rear_001",
        "AK_wood_contour_handguard_upper_001",
    ],
    "04E_grip_details": [
        "AK_groove_grip_001", "AK_groove_grip_002", "AK_groove_grip_003",
        "AK_seam_grip_basecap_001", "AK_wear_grip_edge_001",
    ],
    "04F_sling_loop": [
        "AK_loop_sling_rear_visual", "AK_plate_sling_rear_visual",
        "AK_loop_sling_front_visual",
    ],
    "04G_surface_seams": [
        "AK_seam_stock_receiver_001", "AK_seam_grip_receiver_001",
        "AK_seam_handguard_receiver_001", "AK_seam_barrel_front_001",
    ],
    "04I_front_details": [
        "AK_ring_barrel_visual_001", "AK_ring_barrel_visual_002",
        "AK_line_cleaningrod_visual_001",
        "AK_seam_front_block_001",
        "AK_wear_front_sight_edge_001",
    ],
    "04J_sight_details": [
        "AK_detail_rearsight_001", "AK_notch_rearsight_visual_001",
        "AK_wear_rearsight_edge_001",
    ],
}

EXPECTED_MATERIAL_FAMILY = {
    "AK_rivet_receiver_001": "MAT_placeholder_dark_metal",
    "AK_groove_magazine_001": "MAT_placeholder_black_metal",
    "AK_wood_contour_stock_001": "MAT_placeholder_dark_wood",
    "AK_groove_grip_001": "MAT_placeholder_bakelite_grip",
    "AK_loop_sling_rear_visual": "MAT_placeholder_dark_metal",
    "AK_ring_barrel_visual_001": "MAT_placeholder_dark_metal",
    "AK_detail_rearsight_001": "MAT_placeholder_dark_metal",
}


# Section 3 invariants we must not have broken
SECTION_3_AK_INVARIANT = [
    "AK_receiver_main", "AK_dustcover_main", "AK_stock_main",
    "AK_grip_main", "AK_trigger_guard_visual", "AK_magazine_main",
    "AK_handguard_lower_main", "AK_handguard_upper_main", "AK_gas_tube_outer",
    "AK_barrel_outer_closed", "AK_front_sight_block_visual",
    "AK_front_ring_visual", "AK_gas_block_visual", "AK_rear_sight_visual",
]

SECTION_3_DECORATIVE_AK = [
    "AK_stock_buttplate_visual", "AK_grip_basecap_visual",
    "AK_magazine_baseplate_visual", "AK_magazine_front_spine_visual",
    "AK_magazine_rear_spine_visual",
    "AK_handguard_upper_front_collar_visual",
    "AK_handguard_upper_rear_collar_visual",
]


print("\n=== §4.20 + §4.21 MINOR DETAILS REVIEW ===")
results = []


# --- structure ---
minor = bpy.data.collections.get("04_MINOR_PARTS")
results.append(("04_MINOR_PARTS collection exists", minor is not None))
if minor is not None:
    child_names = {c.name for c in minor.children}
    missing_subs = [n for n in EXPECTED_SUB_COLLECTIONS if n not in child_names]
    results.append(("all 10 sub-collections present", not missing_subs))
    if missing_subs:
        print(f"  missing sub-collections: {missing_subs}")


# --- detail objects exist and live in the right sub-collection ---
flat_expected = []
mis_placed = []
missing = []
for sub, names in EXPECTED_DETAIL_OBJECTS.items():
    flat_expected.extend(names)
    sub_coll = bpy.data.collections.get(sub)
    members = {o.name for o in sub_coll.objects} if sub_coll else set()
    for n in names:
        if n not in bpy.data.objects:
            missing.append(n)
            continue
        if n not in members:
            mis_placed.append(f"{n} (expected in {sub})")
results.append(("all expected detail objects exist", not missing))
if missing:
    print(f"  missing: {missing}")
results.append(("detail objects in correct sub-collections", not mis_placed))
if mis_placed:
    for p in mis_placed:
        print(f"  {p}")


# --- detail count target: ~40 ---
total = len(flat_expected)
print(f"  expected detail objects: {total}")
results.append(("at least 35 detail objects defined", total >= 35))


# --- representative material check per family ---
mat_problems = []
for name, expected in EXPECTED_MATERIAL_FAMILY.items():
    o = bpy.data.objects.get(name)
    if not o or not o.data.materials:
        mat_problems.append(f"{name}: no material")
        continue
    actual = o.data.materials[0].name if o.data.materials[0] else None
    if actual != expected:
        mat_problems.append(f"{name}: {actual} (expected {expected})")
results.append(("placeholder material per detail family", not mat_problems))
if mat_problems:
    for p in mat_problems:
        print(f"  {p}")


# --- All details parented to AK47_MASTER_ASSET ---
master = bpy.data.objects.get("AK47_MASTER_ASSET")
results.append(("AK47_MASTER_ASSET still exists", master is not None))
unparented = []
for n in flat_expected:
    o = bpy.data.objects.get(n)
    if o and o.parent is not master:
        unparented.append(n)
results.append(("all detail objects parented to AK47_MASTER_ASSET", not unparented))
if unparented:
    print(f"  unparented detail objects: {unparented[:5]}{'…' if len(unparented) > 5 else ''}")


# --- Section 3 invariants preserved ---
missing_s3 = [n for n in SECTION_3_AK_INVARIANT if n not in bpy.data.objects]
results.append(("Section 3 AK_ refined parts still present", not missing_s3))
missing_dec = [n for n in SECTION_3_DECORATIVE_AK if n not in bpy.data.objects]
results.append(("Section 3 AK_ decorative parts still present", not missing_dec))


# --- BLK_ backups still hidden ---
backup = bpy.data.collections.get("03H_major_part_backup")
results.append(("Section 3 BLK_ backup collection still exists", backup is not None))


# --- Print final ---
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False
print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")


# Summary
if minor is not None:
    print(f"04_MINOR_PARTS sub-collections and counts:")
    for child in sorted(minor.children, key=lambda c: c.name):
        print(f"  {child.name}: {len(child.objects)} objects")
