"""Verify v03_major_parts.blend matches the §3.20 + §3.21 checklists."""
import bpy
from mathutils import Vector

# Refined AK_ major parts (BLK_ → AK_ map from §3.3.1, extended for v02 supplement)
EXPECTED_AK_OBJECTS = [
    "AK_receiver_main",
    "AK_dustcover_main",
    "AK_stock_main",
    "AK_grip_main",
    "AK_trigger_guard_visual",
    "AK_magazine_main",
    "AK_handguard_lower_main",
    "AK_handguard_upper_main",
    "AK_gas_tube_outer",
    "AK_barrel_outer_closed",
    "AK_front_sight_block_visual",
    "AK_front_ring_visual",
    "AK_gas_block_visual",
    "AK_rear_sight_visual",
]

# Optional decorative AK_ visuals (§3.8.4, §3.9.4, §3.10.4, §3.12.4)
EXPECTED_DECORATIVE_AK = [
    "AK_stock_buttplate_visual",
    "AK_grip_basecap_visual",
    "AK_magazine_baseplate_visual",
    "AK_magazine_front_spine_visual",
    "AK_magazine_rear_spine_visual",
    "AK_handguard_upper_front_collar_visual",
    "AK_handguard_upper_rear_collar_visual",
]

EXPECTED_MATERIALS = {
    "AK_receiver_main": "MAT_placeholder_dark_metal",
    "AK_dustcover_main": "MAT_placeholder_dark_metal",
    "AK_stock_main": "MAT_placeholder_dark_wood",
    "AK_grip_main": "MAT_placeholder_bakelite_grip",
    "AK_trigger_guard_visual": "MAT_placeholder_dark_metal",
    "AK_magazine_main": "MAT_placeholder_black_metal",
    "AK_handguard_lower_main": "MAT_placeholder_dark_wood",
    "AK_handguard_upper_main": "MAT_placeholder_dark_wood",
    "AK_gas_tube_outer": "MAT_placeholder_dark_metal",
    "AK_barrel_outer_closed": "MAT_placeholder_dark_metal",
    "AK_front_sight_block_visual": "MAT_placeholder_dark_metal",
    "AK_front_ring_visual": "MAT_placeholder_dark_metal",
    "AK_gas_block_visual": "MAT_placeholder_dark_metal",
    "AK_rear_sight_visual": "MAT_placeholder_dark_metal",
}

EXPECTED_SUB_COLLECTIONS = [
    "03A_receiver", "03B_stock", "03C_grip", "03D_magazine",
    "03E_handguard", "03F_barrel_front", "03G_sights",
    "03H_major_part_backup",
]

EXPECTED_BLK_BACKUP = [
    "BLK_receiver_main", "BLK_dustcover_main", "BLK_stock_main",
    "BLK_grip_main", "BLK_trigger_guard_visual", "BLK_magazine_main",
    "BLK_handguard_lower", "BLK_handguard_upper", "BLK_gas_tube_outer",
    "BLK_barrel_outer_closed", "BLK_front_sight_block_visual",
    "BLK_front_ring_visual", "BLK_gas_block_visual", "BLK_rear_sight_visual",
]


print("\n=== §3.20 + §3.21 MAJOR PARTS REVIEW ===")
results = []


# --- structure ---
major = bpy.data.collections.get("03_MAJOR_PARTS")
results.append(("03_MAJOR_PARTS collection exists", major is not None))
if major is not None:
    child_names = {c.name for c in major.children}
    missing_subs = [n for n in EXPECTED_SUB_COLLECTIONS if n not in child_names]
    results.append(("all 8 sub-collections present", not missing_subs))
    if missing_subs:
        print(f"  missing sub-collections: {missing_subs}")


# --- 14 AK_ refined parts exist ---
missing_ak = [n for n in EXPECTED_AK_OBJECTS if n not in bpy.data.objects]
results.append(("14 AK_ refined parts present", not missing_ak))
if missing_ak:
    print(f"  missing AK_ parts: {missing_ak}")


# --- 7 AK_ decorative parts exist ---
missing_dec = [n for n in EXPECTED_DECORATIVE_AK if n not in bpy.data.objects]
results.append(("7 AK_ decorative visuals present", not missing_dec))
if missing_dec:
    print(f"  missing decorative AK_: {missing_dec}")


# --- BLK_ backups exist + hidden ---
missing_blk = [n for n in EXPECTED_BLK_BACKUP if n not in bpy.data.objects]
results.append(("all BLK_ backups preserved", not missing_blk))
if missing_blk:
    print(f"  missing BLK_ backups: {missing_blk}")

backup = bpy.data.collections.get("03H_major_part_backup")
if backup is not None:
    in_backup = {o.name for o in backup.objects}
    not_in_backup = [n for n in EXPECTED_BLK_BACKUP if n in bpy.data.objects and n not in in_backup]
    results.append(("BLK_ backups live in 03H_major_part_backup", not not_in_backup))
    if not_in_backup:
        print(f"  BLK_ not in backup collection: {not_in_backup}")

still_visible = [n for n in EXPECTED_BLK_BACKUP
                  if n in bpy.data.objects and not bpy.data.objects[n].hide_viewport]
results.append(("BLK_ backups hidden in viewport", not still_visible))


# --- Materials ---
mat_problems = []
for name, expected in EXPECTED_MATERIALS.items():
    o = bpy.data.objects.get(name)
    if not o or not o.data.materials:
        mat_problems.append(f"{name}: no material")
        continue
    actual = o.data.materials[0].name if o.data.materials[0] else None
    if actual != expected:
        mat_problems.append(f"{name}: {actual} (expected {expected})")
results.append(("placeholder material per AK_ part", not mat_problems))
if mat_problems:
    for p in mat_problems:
        print(f"  {p}")


# --- Bevel + WeightedNormal modifiers on AK_ parts ---
all_ak = EXPECTED_AK_OBJECTS + EXPECTED_DECORATIVE_AK
missing_mods = []
for name in all_ak:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    has_b = any(m.type == "BEVEL" for m in o.modifiers)
    has_w = any(m.type == "WEIGHTED_NORMAL" for m in o.modifiers)
    if not (has_b and has_w):
        missing_mods.append(name)
results.append(("Bevel + WeightedNormal on every AK_ part", not missing_mods))
if missing_mods:
    print(f"  missing modifiers on: {missing_mods}")


# --- AK_ objects in correct sub-collection (membership check) ---
EXPECTED_LOCATION = {
    "AK_receiver_main": "03A_receiver",
    "AK_dustcover_main": "03A_receiver",
    "AK_stock_main": "03B_stock",
    "AK_stock_buttplate_visual": "03B_stock",
    "AK_grip_main": "03C_grip",
    "AK_grip_basecap_visual": "03C_grip",
    "AK_trigger_guard_visual": "03C_grip",
    "AK_magazine_main": "03D_magazine",
    "AK_magazine_baseplate_visual": "03D_magazine",
    "AK_magazine_front_spine_visual": "03D_magazine",
    "AK_magazine_rear_spine_visual": "03D_magazine",
    "AK_handguard_lower_main": "03E_handguard",
    "AK_handguard_upper_main": "03E_handguard",
    "AK_gas_tube_outer": "03E_handguard",
    "AK_handguard_upper_front_collar_visual": "03E_handguard",
    "AK_handguard_upper_rear_collar_visual": "03E_handguard",
    "AK_barrel_outer_closed": "03F_barrel_front",
    "AK_front_sight_block_visual": "03F_barrel_front",
    "AK_front_ring_visual": "03F_barrel_front",
    "AK_gas_block_visual": "03F_barrel_front",
    "AK_rear_sight_visual": "03G_sights",
}
mis_placed = []
for name, expected in EXPECTED_LOCATION.items():
    o = bpy.data.objects.get(name)
    if not o:
        continue
    coll_names = {c.name for c in o.users_collection}
    if expected not in coll_names:
        mis_placed.append(f"{name}: in {coll_names} (expected {expected})")
results.append(("AK_ parts in correct sub-collection", not mis_placed))
if mis_placed:
    for p in mis_placed:
        print(f"  {p}")


# --- Parent: every AK_ should parent to AK47_MASTER_ASSET ---
master = bpy.data.objects.get("AK47_MASTER_ASSET")
results.append(("AK47_MASTER_ASSET still exists", master is not None))
unparented = []
for n in all_ak:
    o = bpy.data.objects.get(n)
    if o and o.parent is not master:
        unparented.append(n)
results.append(("all AK_ parented to AK47_MASTER_ASSET", not unparented))
if unparented:
    print(f"  unparented AK_: {unparented}")


# --- Spatial sanity (same as Section 2 but on AK_) ---
def world_x(name):
    o = bpy.data.objects.get(name)
    return o.matrix_world.translation.x if o else None

rec_x = world_x("AK_receiver_main")
stock_x = world_x("AK_stock_main")
bar_x = world_x("AK_barrel_outer_closed")
mag = bpy.data.objects.get("AK_magazine_main")
mag_z = mag.matrix_world.translation.z if mag else 0
results.append(("stock BEHIND receiver",  stock_x is not None and rec_x is not None and stock_x < rec_x))
results.append(("barrel FORWARD of receiver", bar_x is not None and rec_x is not None and bar_x > rec_x))
results.append(("magazine BELOW receiver", mag_z < 0))


# --- Print final ---
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False
print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

# Summary
if major is not None:
    total = sum(len(c.objects) for c in [major] + list(major.children))
    print(f"03_MAJOR_PARTS total objects (incl. backup): {total}")
    for child in major.children:
        print(f"  {child.name}: {len(child.objects)} objects")
        for o in child.objects:
            mat = o.data.materials[0].name if o.data.materials else "<none>"
            hidden = " (hidden)" if o.hide_viewport else ""
            print(f"    {o.name}: {len(o.data.vertices)}v  mat={mat}{hidden}")
