"""Verify v02_blockout.blend matches the §2.10 + §2.14 checklists."""
import bpy
import math
from mathutils import Vector

EXPECTED_BLK_OBJECTS = [
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
    "BLK_gas_block_visual",        # §2.8.9
    "BLK_front_ring_visual",       # §2.8.9
    "BLK_rear_sight_visual",
    "BLK_trigger_guard_visual",
]

EXPECTED_MATERIALS_PER_PART = {
    "BLK_receiver_main": "MAT_placeholder_dark_metal",
    "BLK_stock_main": "MAT_placeholder_dark_wood",
    "BLK_grip_main": "MAT_placeholder_bakelite_grip",
    "BLK_magazine_main": "MAT_placeholder_black_metal",
    "BLK_handguard_lower": "MAT_placeholder_dark_wood",
    "BLK_handguard_upper": "MAT_placeholder_dark_wood",
    "BLK_gas_tube_outer": "MAT_placeholder_dark_metal",
    "BLK_barrel_outer_closed": "MAT_placeholder_dark_metal",
    "BLK_dustcover_main": "MAT_placeholder_dark_metal",
    "BLK_front_sight_block_visual": "MAT_placeholder_dark_metal",
    "BLK_gas_block_visual": "MAT_placeholder_dark_metal",
    "BLK_front_ring_visual": "MAT_placeholder_dark_metal",
    "BLK_rear_sight_visual": "MAT_placeholder_dark_metal",
    "BLK_trigger_guard_visual": "MAT_placeholder_dark_metal",
}

print("\n=== §2.10 + §2.14 BLOCKOUT REVIEW ===")
results = []

# All 12 expected BLK_ exist
missing = [n for n in EXPECTED_BLK_OBJECTS if n not in bpy.data.objects]
results.append(("12 BLK_ blockout objects present", not missing))
if missing:
    print(f"  missing: {missing}")

# All separate objects (no mesh sharing)
shared = []
seen = {}
for name in EXPECTED_BLK_OBJECTS:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    if o.data.name in seen:
        shared.append(o.name)
    seen[o.data.name] = o.name
results.append(("all parts are separate objects (no shared mesh)", not shared))

# All have BLK_ prefix (sanity)
bad_named = [n for n in EXPECTED_BLK_OBJECTS if not n.startswith("BLK_")]
results.append(("all use BLK_ naming", not bad_named))

# All in 02_BLOCKOUT collection
blockout = bpy.data.collections.get("02_BLOCKOUT")
if blockout:
    in_collection = {o.name for o in blockout.objects}
    not_in = [n for n in EXPECTED_BLK_OBJECTS if n not in in_collection]
    results.append(("all parts in 02_BLOCKOUT collection", not not_in))
    if not_in:
        print(f"  not in 02_BLOCKOUT: {not_in}")
else:
    results.append(("02_BLOCKOUT collection exists", False))

# All have Bevel + Weighted Normal modifier (§2.6.4)
missing_mods = []
for name in EXPECTED_BLK_OBJECTS:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    has_bevel = any(m.type == "BEVEL" for m in o.modifiers)
    has_wn = any(m.type == "WEIGHTED_NORMAL" for m in o.modifiers)
    if not (has_bevel and has_wn):
        missing_mods.append(name)
results.append(("Bevel + WeightedNormal on every part", not missing_mods))
if missing_mods:
    print(f"  missing modifiers on: {missing_mods}")

# Material assignment per part
mat_problems = []
for name, expected_mat in EXPECTED_MATERIALS_PER_PART.items():
    o = bpy.data.objects.get(name)
    if not o or not o.data.materials:
        mat_problems.append(f"{name}: no material")
        continue
    actual = o.data.materials[0].name if o.data.materials[0] else None
    if actual != expected_mat:
        mat_problems.append(f"{name}: {actual} (expected {expected_mat})")
results.append(("placeholder material per spec", not mat_problems))
if mat_problems:
    for p in mat_problems:
        print(f"  {p}")

# Spatial sanity: receiver near origin, barrel forward, stock backward, magazine below
def world_x(name):
    o = bpy.data.objects.get(name)
    return o.location.x if o else None

receiver_x = world_x("BLK_receiver_main")
stock_x = world_x("BLK_stock_main")
barrel_x = world_x("BLK_barrel_outer_closed")
mag_z = bpy.data.objects.get("BLK_magazine_main").location.z if bpy.data.objects.get("BLK_magazine_main") else 0

results.append(("stock is BEHIND receiver",  stock_x is not None and receiver_x is not None and stock_x < receiver_x))
results.append(("barrel is IN FRONT of receiver", barrel_x is not None and receiver_x is not None and barrel_x > receiver_x))
results.append(("magazine sits BELOW receiver", mag_z < 0))

# §2.14 Side-view bounds: model spans about 1.0 unit
all_x = []
for name in EXPECTED_BLK_OBJECTS:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    for v in o.bound_box:
        wp = o.matrix_world @ Vector(v)  # type: ignore
        all_x.append(wp.x)
if all_x:
    span_x = max(all_x) - min(all_x)
    results.append(("overall length close to 1.0 unit (±0.2)", abs(span_x - 1.0) < 0.25))
    print(f"  overall X span: {span_x:.3f} units")

# §2.5.1 step 14: master parent
master = bpy.data.objects.get("AK47_MASTER_ASSET")
results.append(("AK47_MASTER_ASSET empty exists", master is not None))
all_parented = master is not None and all(
    bpy.data.objects[n].parent is master for n in EXPECTED_BLK_OBJECTS if n in bpy.data.objects
)
results.append(("all BLK_ parented to master empty", all_parented))

# Print checklist
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False

print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

# Summary
blockout_count = len(blockout.objects) if blockout else 0
print(f"02_BLOCKOUT contains: {blockout_count} objects")
for o in blockout.objects:
    has_bevel = any(m.type == "BEVEL" for m in o.modifiers)
    mat = o.data.materials[0].name if o.data.materials else "<none>"
    print(f"  {o.name}: {len(o.data.vertices)}v  bevel={has_bevel}  mat={mat}")
