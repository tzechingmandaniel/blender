"""Verify v03_major_parts.blend matches the §3.10 checklist."""
import bpy
from mathutils import Vector

EXPECTED_AK_OBJECTS = [
    "AK_receiver_main",
    "AK_stock_main",
    "AK_magazine_main",
    "AK_grip_main",
    "AK_handguard_lower_main",
    "AK_handguard_upper_main",
    "AK_barrel_exterior_main",
    "AK_dustcover_main",
]

EXPECTED_MATERIALS_PER_PART = {
    "AK_receiver_main":        "MAT_placeholder_dark_metal",
    "AK_stock_main":           "MAT_placeholder_dark_wood",
    "AK_magazine_main":        "MAT_placeholder_black_metal",
    "AK_grip_main":            "MAT_placeholder_bakelite_grip",
    "AK_handguard_lower_main": "MAT_placeholder_dark_wood",
    "AK_handguard_upper_main": "MAT_placeholder_dark_wood",
    "AK_barrel_exterior_main": "MAT_placeholder_dark_metal",
    "AK_dustcover_main":       "MAT_placeholder_dark_metal",
}

print("\n=== §3.10 MAJOR-PARTS REVIEW ===")
results = []

# All 8 expected AK_ exist
missing = [n for n in EXPECTED_AK_OBJECTS if n not in bpy.data.objects]
results.append(("8 AK_ major-part objects present", not missing))
if missing:
    print(f"  missing: {missing}")

# All separate objects (no shared mesh)
shared = []
seen = {}
for name in EXPECTED_AK_OBJECTS:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    if o.data.name in seen:
        shared.append(o.name)
    seen[o.data.name] = o.name
results.append(("all parts are separate objects (no shared mesh)", not shared))

# All have AK_ prefix
bad_named = [n for n in EXPECTED_AK_OBJECTS if not n.startswith("AK_")]
results.append(("all use AK_ naming", not bad_named))

# All in 03_MAJOR_PARTS collection
major_parts = bpy.data.collections.get("03_MAJOR_PARTS")
if major_parts:
    in_collection = {o.name for o in major_parts.objects}
    not_in = [n for n in EXPECTED_AK_OBJECTS if n not in in_collection]
    results.append(("all parts in 03_MAJOR_PARTS collection", not not_in))
    if not_in:
        print(f"  not in 03_MAJOR_PARTS: {not_in}")
else:
    results.append(("03_MAJOR_PARTS collection exists", False))

# All have Bevel + Weighted Normal modifier (§3.4)
missing_mods = []
for name in EXPECTED_AK_OBJECTS:
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


def world_z(name):
    o = bpy.data.objects.get(name)
    return o.location.z if o else None


receiver_x = world_x("AK_receiver_main")
stock_x = world_x("AK_stock_main")
barrel_x = world_x("AK_barrel_exterior_main")
mag_z = world_z("AK_magazine_main")
grip_z = world_z("AK_grip_main")
dustcover_z = world_z("AK_dustcover_main")

results.append(("stock is BEHIND receiver",
                stock_x is not None and receiver_x is not None and stock_x < receiver_x))
results.append(("barrel is IN FRONT of receiver",
                barrel_x is not None and receiver_x is not None and barrel_x > receiver_x))
results.append(("magazine sits BELOW receiver", mag_z is not None and mag_z < 0))
results.append(("grip sits BELOW receiver", grip_z is not None and grip_z < 0))
results.append(("dust cover sits ABOVE receiver", dustcover_z is not None and dustcover_z > 0))

# Side-view bounds: overall length still close to 1.0 unit
all_x = []
for name in EXPECTED_AK_OBJECTS:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    for v in o.bound_box:
        wp = o.matrix_world @ Vector(v)  # type: ignore
        all_x.append(wp.x)
if all_x:
    span_x = max(all_x) - min(all_x)
    results.append(("overall length still close to 1.0 unit (±0.25)",
                    abs(span_x - 1.0) < 0.25))
    print(f"  overall X span: {span_x:.3f} units")

# Master parent: every AK_ part is parented to AK47_MASTER_ASSET
master = bpy.data.objects.get("AK47_MASTER_ASSET")
results.append(("AK47_MASTER_ASSET empty exists", master is not None))
parented = master is not None and all(
    bpy.data.objects[n].parent is master
    for n in EXPECTED_AK_OBJECTS
    if n in bpy.data.objects
)
results.append(("all AK_ parts parented to master empty", parented))

# 02_BLOCKOUT hidden in viewport + render
blockout = bpy.data.collections.get("02_BLOCKOUT")
results.append(("02_BLOCKOUT still exists (for reference)", blockout is not None))
if blockout is not None:
    # collection-level hide_render flag should be on
    results.append(("02_BLOCKOUT hide_render = True", blockout.hide_render))

# Topology: each AK_ part should have more verts than its BLK_ counterpart
BLK_AK_PAIRS = [
    ("BLK_receiver_main",        "AK_receiver_main"),
    ("BLK_stock_main",           "AK_stock_main"),
    ("BLK_magazine_main",        "AK_magazine_main"),
    ("BLK_grip_main",            "AK_grip_main"),
    ("BLK_handguard_lower",      "AK_handguard_lower_main"),
    ("BLK_handguard_upper",      "AK_handguard_upper_main"),
    ("BLK_barrel_outer_closed",  "AK_barrel_exterior_main"),
    ("BLK_dustcover_main",       "AK_dustcover_main"),
]
topology_ok = True
for blk_name, ak_name in BLK_AK_PAIRS:
    blk = bpy.data.objects.get(blk_name)
    ak = bpy.data.objects.get(ak_name)
    if blk is None or ak is None:
        continue
    if len(ak.data.vertices) <= len(blk.data.vertices):
        topology_ok = False
        print(f"  {ak_name} ({len(ak.data.vertices)}v) not denser than {blk_name} ({len(blk.data.vertices)}v)")
results.append(("each AK_ part has more verts than its BLK_ source", topology_ok))

# Print checklist
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False

print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

# Summary
if major_parts:
    print(f"03_MAJOR_PARTS contains: {len(major_parts.objects)} objects")
    for o in major_parts.objects:
        has_bevel = any(m.type == "BEVEL" for m in o.modifiers)
        mat = o.data.materials[0].name if o.data.materials else "<none>"
        print(f"  {o.name}: {len(o.data.vertices)}v  bevel={has_bevel}  mat={mat}")
