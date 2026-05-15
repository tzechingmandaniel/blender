"""Section 3 auto-executor: refines the v02_blockout BLK_ objects into AK_
major exterior parts for the non-functional AK-style 3D prop, saves
v03_major_parts.blend.

Auto-detects the project root from __file__ — no hardcoded path. The script
lives at <repo>/05_mcp_prompts/section3/section3_executor.py.

Operations per the Section 3 plan:
  - Duplicates each BLK_ to AK_ (object + mesh data).
  - Moves AK_ to the right sub-collection under 03_MAJOR_PARTS.
  - Replaces modifier stack with per-part bevel style from §3.18.2.
  - Re-assigns placeholder material (single slot).
  - Adds 7 optional decorative AK_ parts.
  - Hides BLK_ originals in 03H_major_part_backup as backup.

All exterior-only. No internal mechanism, no functional geometry.
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector


# ---------- 0. paths ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# .../05_mcp_prompts/section3 -> .../05_mcp_prompts -> repo root
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v02_blockout.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v03_major_parts.blend")

print(f"\n=== SECTION 3 — MAJOR PARTS ===")
print(f"  source : {SRC_BLEND}")
print(f"  target : {OUT_BLEND}")

bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)


# ---------- helpers ----------
def get_or_make_collection(name, parent_name=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        parent = bpy.data.collections.get(parent_name) if parent_name else None
        target = parent if parent is not None else bpy.context.scene.collection
        target.children.link(c)
    return c


def link_only_to(obj, collection_name):
    target = get_or_make_collection(collection_name)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)


def assign_material(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        print(f"  WARNING: material missing: {mat_name}")
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def clear_modifiers(obj, types=("BEVEL", "WEIGHTED_NORMAL")):
    for mod in list(obj.modifiers):
        if mod.type in types:
            obj.modifiers.remove(mod)


def add_bevel_and_weighted_normals(obj, width, segments, angle_deg=30):
    """§3.18.2 — per-part bevel style + weighted normals."""
    clear_modifiers(obj)
    bev = obj.modifiers.new("Bevel", type="BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(angle_deg)
    wn = obj.modifiers.new("WeightedNormal", type="WEIGHTED_NORMAL")
    wn.weight = 50
    wn.thresh = 0.01
    wn.keep_sharp = True


def duplicate_blk_to_ak(blk_name, ak_name, sub_collection, mat_name, bevel_w, bevel_s, bevel_a=30):
    """Duplicate BLK_ -> AK_, place in sub-collection, refresh modifiers + material.
    Returns the new AK_ object (or None if BLK_ missing)."""
    src = bpy.data.objects.get(blk_name)
    if src is None:
        print(f"  WARNING: missing source: {blk_name}")
        return None

    # Remove any prior AK_ with the same name (idempotent re-run)
    if ak_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[ak_name], do_unlink=True)

    # Duplicate object + mesh data so AK_ is fully independent of BLK_
    new_data = src.data.copy()
    new_data.name = ak_name + "_mesh"
    new_obj = bpy.data.objects.new(ak_name, new_data)
    new_obj.matrix_world = src.matrix_world.copy()

    # Link into target sub-collection only
    target = get_or_make_collection(sub_collection)
    target.objects.link(new_obj)

    # Parent to master empty (keep world transform)
    master = bpy.data.objects.get("AK47_MASTER_ASSET")
    if master is not None:
        new_obj.parent = master
        new_obj.matrix_parent_inverse = master.matrix_world.inverted()

    # Refresh modifier stack + material
    add_bevel_and_weighted_normals(new_obj, bevel_w, bevel_s, bevel_a)
    assign_material(new_obj, mat_name)

    # Backup the original BLK_: move into backup collection, hide it
    link_only_to(src, "03H_major_part_backup")
    src.hide_viewport = True
    src.hide_render = True

    print(f"  refined {blk_name} -> {ak_name}  ({sub_collection}, mat={mat_name}, bevel={bevel_w}/{bevel_s})")
    return new_obj


def make_visual_object_from_bmesh(name, build_fn, sub_collection, location, mat_name,
                                   bevel_w=0.0010, bevel_s=2, bevel_a=30, rotation_deg=(0, 0, 0)):
    """Build a fresh decorative AK_ visual part (buttplate, basecap, spine, collar, …)."""
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bm = bmesh.new()
    build_fn(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = tuple(math.radians(d) for d in rotation_deg)

    target = get_or_make_collection(sub_collection)
    target.objects.link(obj)

    master = bpy.data.objects.get("AK47_MASTER_ASSET")
    if master is not None:
        obj.parent = master
        obj.matrix_parent_inverse = master.matrix_world.inverted()

    add_bevel_and_weighted_normals(obj, bevel_w, bevel_s, bevel_a)
    assign_material(obj, mat_name)
    print(f"  built   {name}  ({sub_collection}, mat={mat_name})")
    return obj


def add_box_bm(bm, dims, location=(0, 0, 0)):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=dims, verts=ret["verts"])
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])


def add_cyl_bm(bm, radius, depth, segments=24, axis="Z", location=(0, 0, 0)):
    ret = bmesh.ops.create_cone(
        bm, segments=segments, radius1=radius, radius2=radius,
        depth=depth, cap_ends=True, cap_tris=False,
    )
    if axis == "X":
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                          matrix=Matrix.Rotation(math.radians(90), 4, "Y"),
                          verts=ret["verts"])
    elif axis == "Y":
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                          matrix=Matrix.Rotation(math.radians(90), 4, "X"),
                          verts=ret["verts"])
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])


# ---------- 1. build collection structure (§3.4) ----------
print("\n-- collections --")
major = get_or_make_collection("03_MAJOR_PARTS")
for sub in ("03A_receiver", "03B_stock", "03C_grip", "03D_magazine",
            "03E_handguard", "03F_barrel_front", "03G_sights",
            "03H_major_part_backup"):
    get_or_make_collection(sub, parent_name="03_MAJOR_PARTS")
print(f"  03_MAJOR_PARTS with 8 sub-collections")


# ---------- 2. duplicate BLK_ -> AK_ (§3.3.1, §3.18.2) ----------
# (BLK_name, AK_name, sub_collection, material, bevel_width, bevel_segments)
REFINEMENTS = [
    ("BLK_receiver_main",             "AK_receiver_main",             "03A_receiver",     "MAT_placeholder_dark_metal",    0.0018, 2),
    ("BLK_dustcover_main",            "AK_dustcover_main",            "03A_receiver",     "MAT_placeholder_dark_metal",    0.0015, 2),
    ("BLK_stock_main",                "AK_stock_main",                "03B_stock",        "MAT_placeholder_dark_wood",     0.0035, 3, 35),
    ("BLK_grip_main",                 "AK_grip_main",                 "03C_grip",         "MAT_placeholder_bakelite_grip", 0.0030, 3, 35),
    ("BLK_trigger_guard_visual",      "AK_trigger_guard_visual",      "03C_grip",         "MAT_placeholder_dark_metal",    0.0015, 2),
    ("BLK_magazine_main",             "AK_magazine_main",             "03D_magazine",     "MAT_placeholder_black_metal",   0.0020, 2),
    ("BLK_handguard_lower",           "AK_handguard_lower_main",      "03E_handguard",    "MAT_placeholder_dark_wood",     0.0030, 3, 35),
    ("BLK_handguard_upper",           "AK_handguard_upper_main",      "03E_handguard",    "MAT_placeholder_dark_wood",     0.0030, 3, 35),
    ("BLK_gas_tube_outer",            "AK_gas_tube_outer",            "03E_handguard",    "MAT_placeholder_dark_metal",    0.0010, 2),
    ("BLK_barrel_outer_closed",       "AK_barrel_outer_closed",       "03F_barrel_front", "MAT_placeholder_dark_metal",    0.0010, 2),
    ("BLK_front_sight_block_visual",  "AK_front_sight_block_visual",  "03F_barrel_front", "MAT_placeholder_dark_metal",    0.0008, 2),
    ("BLK_front_ring_visual",         "AK_front_ring_visual",         "03F_barrel_front", "MAT_placeholder_dark_metal",    0.0008, 2),
    ("BLK_gas_block_visual",          "AK_gas_block_visual",          "03F_barrel_front", "MAT_placeholder_dark_metal",    0.0008, 2),
    ("BLK_rear_sight_visual",         "AK_rear_sight_visual",         "03G_sights",       "MAT_placeholder_dark_metal",    0.0010, 2),
]

print("\n-- BLK_ -> AK_ refinements --")
ak_objects = {}
for spec in REFINEMENTS:
    blk_name, ak_name, sub, mat, bw, bs = spec[:6]
    ba = spec[6] if len(spec) > 6 else 30
    obj = duplicate_blk_to_ak(blk_name, ak_name, sub, mat, bw, bs, ba)
    if obj is not None:
        ak_objects[ak_name] = obj


# ---------- 3. add optional decorative visual parts (§3.8.4, §3.9.4, §3.10.4, §3.12.4) ----------
print("\n-- optional decorative parts --")

# Helper: source object position so the decorative part can be placed relative
def src_world_loc(name):
    o = bpy.data.objects.get(name)
    return o.matrix_world.translation.copy() if o else Vector((0, 0, 0))


# 3a. Stock buttplate — thin cap on rear face of stock
def build_stock_buttplate(bm):
    add_box_bm(bm, dims=(0.012, 0.040, 0.090), location=(0, 0, 0))

stock_loc = src_world_loc("AK_stock_main")
# Rear face of the stock is ~ X = stock_loc.x - 0.160 (stock length 0.320)
make_visual_object_from_bmesh(
    "AK_stock_buttplate_visual", build_stock_buttplate, "03B_stock",
    location=(stock_loc.x - 0.165, stock_loc.y, stock_loc.z - 0.005),
    mat_name="MAT_placeholder_black_metal", bevel_w=0.0008, bevel_s=2,
)


# 3b. Grip basecap — thin flange at the bottom of grip
def build_grip_basecap(bm):
    add_box_bm(bm, dims=(0.050, 0.034, 0.005), location=(0, 0, 0))

grip = bpy.data.objects.get("AK_grip_main")
if grip is not None:
    # Compute world-space lowest point of the grip
    grip_min_z = min((grip.matrix_world @ Vector(v)).z for v in grip.bound_box)
    make_visual_object_from_bmesh(
        "AK_grip_basecap_visual", build_grip_basecap, "03C_grip",
        location=(grip.matrix_world.translation.x,
                   grip.matrix_world.translation.y,
                   grip_min_z + 0.002),
        mat_name="MAT_placeholder_black_metal", bevel_w=0.0008, bevel_s=2,
    )


# 3c. Magazine baseplate + spines
mag = bpy.data.objects.get("AK_magazine_main")
if mag is not None:
    mag_loc = mag.matrix_world.translation
    mag_min_z = min((mag.matrix_world @ Vector(v)).z for v in mag.bound_box)
    mag_min_x = min((mag.matrix_world @ Vector(v)).x for v in mag.bound_box)
    mag_max_x = max((mag.matrix_world @ Vector(v)).x for v in mag.bound_box)

    def build_mag_baseplate(bm):
        # Slight forward offset because the magazine bottom curves forward
        add_box_bm(bm, dims=(0.118, 0.032, 0.012), location=(0, 0, 0))

    make_visual_object_from_bmesh(
        "AK_magazine_baseplate_visual", build_mag_baseplate, "03D_magazine",
        location=(mag_loc.x + 0.025, mag_loc.y, mag_min_z + 0.004),
        mat_name="MAT_placeholder_black_metal", bevel_w=0.0008, bevel_s=2,
    )

    def build_mag_front_spine(bm):
        # Tall thin slab oriented along the front face of the magazine
        add_box_bm(bm, dims=(0.008, 0.026, 0.140), location=(0, 0, 0))

    make_visual_object_from_bmesh(
        "AK_magazine_front_spine_visual", build_mag_front_spine, "03D_magazine",
        location=(mag_max_x - 0.004, mag_loc.y, mag_loc.z),
        mat_name="MAT_placeholder_black_metal", bevel_w=0.0006, bevel_s=2,
    )

    def build_mag_rear_spine(bm):
        add_box_bm(bm, dims=(0.008, 0.026, 0.140), location=(0, 0, 0))

    make_visual_object_from_bmesh(
        "AK_magazine_rear_spine_visual", build_mag_rear_spine, "03D_magazine",
        location=(mag_min_x + 0.004, mag_loc.y, mag_loc.z),
        mat_name="MAT_placeholder_black_metal", bevel_w=0.0006, bevel_s=2,
    )


# 3d. Upper handguard collars (front + rear)
hg_upper = bpy.data.objects.get("AK_handguard_upper_main")
if hg_upper is not None:
    hg_min_x = min((hg_upper.matrix_world @ Vector(v)).x for v in hg_upper.bound_box)
    hg_max_x = max((hg_upper.matrix_world @ Vector(v)).x for v in hg_upper.bound_box)
    hg_z = hg_upper.matrix_world.translation.z

    def build_collar(bm):
        add_cyl_bm(bm, radius=0.013, depth=0.012, segments=24, axis="X")

    make_visual_object_from_bmesh(
        "AK_handguard_upper_front_collar_visual", build_collar, "03E_handguard",
        location=(hg_max_x + 0.006, hg_upper.matrix_world.translation.y, hg_z),
        mat_name="MAT_placeholder_dark_metal", bevel_w=0.0006, bevel_s=2,
    )
    make_visual_object_from_bmesh(
        "AK_handguard_upper_rear_collar_visual", build_collar, "03E_handguard",
        location=(hg_min_x - 0.006, hg_upper.matrix_world.translation.y, hg_z),
        mat_name="MAT_placeholder_dark_metal", bevel_w=0.0006, bevel_s=2,
    )


# ---------- 4. save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")
