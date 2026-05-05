"""Section 2 auto-executor: builds the full blockout for the non-functional
AK-style exterior prop on top of v01_project_setup.blend, then saves
v02_blockout.blend.

Builds 12 BLK_ objects in the order from §2.5.1, each with a Bevel +
Weighted-Normal modifier and the placeholder material assigned per §2.6.3.
All exterior-only — no internal mechanism, no functional geometry.
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector

PROJECT_ROOT = r"C:\AK47_NonFunctional_Prop"
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v01_project_setup.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v02_blockout.blend")


# ---------- 0. start from v01 ----------
bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)


# ---------- helpers ----------
def get_collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def link_only_to(obj, collection_name):
    target = get_collection(collection_name)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)


def assign_material(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def add_bevel_and_weighted_normals(obj, width=0.002, segments=2, angle_deg=30):
    """§2.6.4 — bevel for softened hard-surface edges + weighted normals for clean shading."""
    bev = obj.modifiers.new("Bevel", type="BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(angle_deg)
    wn = obj.modifiers.new("WeightedNormal", type="WEIGHTED_NORMAL")
    wn.weight = 50
    wn.thresh = 0.01
    wn.keep_sharp = True


def make_object_from_bmesh(name, bm, location=(0, 0, 0), rotation_deg=(0, 0, 0)):
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = tuple(math.radians(d) for d in rotation_deg)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def add_box_bm(bm, dims=(1, 1, 1), location=(0, 0, 0)):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=dims, verts=ret["verts"])
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])


def add_cyl_bm(bm, radius=0.01, depth=0.1, segments=24, axis="Z", location=(0, 0, 0)):
    ret = bmesh.ops.create_cone(
        bm, segments=segments, radius1=radius, radius2=radius,
        depth=depth, cap_ends=True, cap_tris=False,
    )
    if axis == "X":
        bmesh.ops.rotate(
            bm, cent=(0, 0, 0),
            matrix=Matrix.Rotation(math.radians(90), 4, "Y"),
            verts=ret["verts"],
        )
    elif axis == "Y":
        bmesh.ops.rotate(
            bm, cent=(0, 0, 0),
            matrix=Matrix.Rotation(math.radians(90), 4, "X"),
            verts=ret["verts"],
        )
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])


# ---------- per-part mesh builders ----------
def build_receiver(bm):
    """§2.8.1 — rectangular hard-surface box, central reference part."""
    # Receiver spans X=-0.18 to +0.05  (length 0.23), Y ±0.020, Z ±0.040
    add_box_bm(bm, dims=(0.230, 0.040, 0.080), location=(0.0, 0.0, 0.0))


def build_stock(bm):
    """§2.8.2 — tapered box behind receiver, taller at rear, narrower toward receiver."""
    # Stock body: X=-0.18 to -0.50 (length 0.32), centred at -0.34
    add_box_bm(bm, dims=(0.320, 0.040, 0.090), location=(0.0, 0.0, 0.0))
    # Taper: pull the front (toward receiver, +X side) verts inward
    for v in bm.verts:
        if v.co.x > 0.0:
            v.co.z *= 0.55
            v.co.y *= 0.85
    # Buttstock back-bottom angle (slope from rear-bottom up to mid-bottom)
    for v in bm.verts:
        if v.co.x < -0.10 and v.co.z < 0:
            v.co.z -= 0.005


def build_magazine(bm):
    """§2.8.3 — curved rectangular form. Add subtle banana curve plus a baseplate visual."""
    # Main mag body: subdivided box bent in X-Z plane
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.110, 0.025, 0.150), verts=ret["verts"])
    # Subdivide horizontally so we can curve the bottom forward
    bmesh.ops.subdivide_edges(
        bm, edges=bm.edges[:], cuts=2, use_grid_fill=True,
    )
    # Bend: bottom (z<0) shifts forward (+x); top stays
    for v in bm.verts:
        # Normalised z from top (1) to bottom (-1)
        z_norm = max(-1.0, min(1.0, v.co.z / 0.075))
        if z_norm < 0:
            curve = (1.0 - (1.0 + z_norm)) ** 2  # 0 at top, 1 at bottom
            v.co.x += curve * 0.060
    # Floorplate visual at the bottom
    add_box_bm(bm, dims=(0.115, 0.030, 0.012), location=(0.060, 0.0, -0.080))


def build_grip(bm):
    """§2.8.4 — angled tapered box. Top narrower than bottom, tilted backward."""
    add_box_bm(bm, dims=(0.045, 0.030, 0.115), location=(0.0, 0.0, 0.0))
    # Taper: top narrower than bottom
    for v in bm.verts:
        if v.co.z > 0:
            v.co.x *= 0.55
    # Base cap (small flange at bottom)
    add_box_bm(bm, dims=(0.050, 0.034, 0.008), location=(0.0, 0.0, -0.062))


def build_handguard_lower(bm):
    """§2.8.5 — rounded rectangular wood block under the upper handguard."""
    add_box_bm(bm, dims=(0.130, 0.040, 0.030), location=(0.0, 0.0, 0.0))
    # Slight lower contour: pull bottom-front edge down a touch
    for v in bm.verts:
        if v.co.z < 0 and abs(v.co.x) < 0.05:
            v.co.z -= 0.004


def build_handguard_upper(bm):
    """§2.8.6 — top wooden cover above barrel."""
    add_box_bm(bm, dims=(0.150, 0.030, 0.022), location=(0.0, 0.0, 0.0))


def build_gas_tube(bm):
    """§2.8.6 — dark metal tube, exterior visual only."""
    add_cyl_bm(bm, radius=0.0085, depth=0.080, segments=18, axis="X")


def build_barrel(bm):
    """§2.8.7 — straight cylinder along the barrel axis."""
    add_cyl_bm(bm, radius=0.0085, depth=0.320, segments=24, axis="X")


def build_dust_cover(bm):
    """§2.8.8 — rounded rectangular cover sitting on top of the receiver."""
    add_box_bm(bm, dims=(0.220, 0.036, 0.014), location=(0.0, 0.0, 0.0))
    # Curved top: lift centre slightly
    for v in bm.verts:
        if v.co.z > 0:
            v.co.z += 0.003 * (1.0 - (abs(v.co.x) / 0.110))


def build_front_sight(bm):
    """§2.8.9 — upright front sight block silhouette."""
    add_box_bm(bm, dims=(0.025, 0.024, 0.040), location=(0.0, 0.0, 0.0))
    # Small post on top (still very basic per §2.8.9)
    add_box_bm(bm, dims=(0.006, 0.006, 0.014), location=(0.0, 0.0, 0.025))


def build_rear_sight(bm):
    """§2.8.10 — small block + thin raised shape on top of receiver/front receiver area."""
    add_box_bm(bm, dims=(0.030, 0.030, 0.012), location=(0.0, 0.0, 0.0))
    # Notch riser — kept as a single thin block at this stage (no real notch yet)
    add_box_bm(bm, dims=(0.020, 0.012, 0.005), location=(0.0, 0.0, 0.008))


def build_trigger_guard(bm):
    """Visual trigger guard: simple curved rectangle around the trigger area."""
    # Outer ring
    add_box_bm(bm, dims=(0.060, 0.022, 0.030), location=(0.0, 0.0, 0.0))
    # Inner cutout would require boolean — deferred to detail pass


# ---------- spec table: what to build, where, and which material ----------
PARTS = [
    # (object_name, builder, location, rotation_deg, material)
    ("BLK_receiver_main",            build_receiver,        (-0.065, 0.0,  0.000),  (0, 0, 0),    "MAT_placeholder_dark_metal"),
    ("BLK_stock_main",               build_stock,           (-0.340, 0.0, -0.005),  (0, 0, 0),    "MAT_placeholder_dark_wood"),
    ("BLK_magazine_main",            build_magazine,        (-0.050, 0.0, -0.105),  (0, 0, 0),    "MAT_placeholder_black_metal"),
    ("BLK_grip_main",                build_grip,            (-0.090, 0.0, -0.090),  (0, -18, 0),  "MAT_placeholder_bakelite_grip"),
    ("BLK_handguard_lower",          build_handguard_lower, ( 0.135, 0.0,  0.005),  (0, 0, 0),    "MAT_placeholder_dark_wood"),
    ("BLK_handguard_upper",          build_handguard_upper, ( 0.140, 0.0,  0.050),  (0, 0, 0),    "MAT_placeholder_dark_wood"),
    ("BLK_gas_tube_outer",           build_gas_tube,        ( 0.235, 0.0,  0.050),  (0, 0, 0),    "MAT_placeholder_dark_metal"),
    ("BLK_barrel_outer_closed",      build_barrel,          ( 0.250, 0.0,  0.020),  (0, 0, 0),    "MAT_placeholder_dark_metal"),
    ("BLK_dustcover_main",           build_dust_cover,      (-0.065, 0.0,  0.046),  (0, 0, 0),    "MAT_placeholder_dark_metal"),
    ("BLK_front_sight_block_visual", build_front_sight,     ( 0.405, 0.0,  0.045),  (0, 0, 0),    "MAT_placeholder_dark_metal"),
    ("BLK_rear_sight_visual",        build_rear_sight,      ( 0.045, 0.0,  0.052),  (0, 0, 0),    "MAT_placeholder_dark_metal"),
    ("BLK_trigger_guard_visual",     build_trigger_guard,   (-0.050, 0.0, -0.040),  (0, 0, 0),    "MAT_placeholder_dark_metal"),
]

print("\n=== SECTION 2 BLOCKOUT ===")
for name, builder, loc, rot, mat_name in PARTS:
    # Skip if already exists from a previous run (shouldn't, since we open v01)
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bm = bmesh.new()
    builder(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = make_object_from_bmesh(name, bm, location=loc, rotation_deg=rot)
    add_bevel_and_weighted_normals(obj)
    assign_material(obj, mat_name)
    link_only_to(obj, "02_BLOCKOUT")
    print(f"  built {name}: {len(obj.data.vertices)}v  loc={loc}  mat={mat_name}")


# ---------- save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")
