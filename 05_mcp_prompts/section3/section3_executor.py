"""Section 3 auto-executor: refines the Section 2 blockout into AK_ major parts.

Reads v02_blockout.blend, builds 8 AK_ objects in the 03_MAJOR_PARTS collection,
hides the 02_BLOCKOUT collection, parents everything to AK47_MASTER_ASSET, then
saves v03_major_parts.blend.

Strictly exterior-only: no internal mechanism, no functional barrel, chamber,
bolt, spring, firing system, detachable magazine locking, or manufacturing-
level details. All silhouette features are vertex moves or additive geometry —
no booleans, no real openings.
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v02_blockout.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v03_major_parts.blend")


# ---------- 0. start from v02 ----------
bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)


# ---------- helpers (same pattern as section2_executor) ----------
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


def add_box_bm(bm, dims=(1, 1, 1), location=(0, 0, 0), subdiv_x=0):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=dims, verts=ret["verts"])
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])
    if subdiv_x > 0:
        # Subdivide just the X-running edges of this box
        x_edges = [e for e in ret["verts"][0].link_edges if abs(e.verts[0].co.x - e.verts[1].co.x) > 1e-6]
        # Fallback: do a full subdivide on all created edges
        edges = []
        for v in ret["verts"]:
            for e in v.link_edges:
                if e not in edges:
                    edges.append(e)
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=subdiv_x, use_grid_fill=True)
    return ret["verts"]


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
    return ret["verts"]


# ---------- per-part mesh builders ----------
def build_receiver(bm):
    """§3.2 — receiver with magazine-well + ejection-port silhouette indents
    and a selector pad on the +Y face."""
    # Main body: 0.230 × 0.040 × 0.080 box (matches BLK_receiver dims)
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.230, 0.040, 0.080), verts=ret["verts"])
    # Two loop cuts along X for shaping
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)

    # Top-rear chamfer: lower the top-rear-edge verts a touch
    for v in bm.verts:
        if v.co.x < -0.10 and v.co.z > 0.035:
            v.co.z -= 0.005

    # Magazine-well silhouette: small region on -Z face pushed up (+Z)
    for v in bm.verts:
        if v.co.z < -0.035 and -0.10 < v.co.x < -0.02:
            v.co.z += 0.005

    # Ejection-port silhouette: small region on +Y face pushed inward (-Y)
    for v in bm.verts:
        if v.co.y > 0.018 and -0.05 < v.co.x < 0.00 and abs(v.co.z) < 0.015:
            v.co.y -= 0.003

    # Selector lever pad on +Y face (additive box)
    add_box_bm(
        bm,
        dims=(0.020, 0.004, 0.020),
        location=(-0.040, 0.022, 0.015),
    )

    # Trigger pocket on -Z (visual recess only)
    for v in bm.verts:
        if v.co.z < -0.035 and -0.04 < v.co.x < 0.00:
            v.co.z += 0.002


def build_stock(bm):
    """§3.3 — stock with curved buttplate, cheek slope, narrowed wrist, and
    a sling-slot silhouette on the lower-rear edge."""
    # Body: 0.320 × 0.040 × 0.090
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.320, 0.040, 0.090), verts=ret["verts"])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)

    # Curved buttplate (rear face concave along Z)
    for v in bm.verts:
        if v.co.x < -0.155:  # near rear face
            z_norm = v.co.z / 0.045
            # Pull forward in X based on |z| (more at top/bottom, less at midline)
            curve = (1.0 - z_norm * z_norm) * 0.012
            v.co.x += curve

    # Cheek slope: top edge slopes down from rear toward the receiver
    for v in bm.verts:
        if v.co.z > 0.040:
            # +X is toward the receiver -> lower Z as X increases
            tnorm = max(0.0, min(1.0, (v.co.x + 0.160) / 0.320))
            v.co.z -= tnorm * 0.024

    # Wrist narrows in Y and Z at the front (toward receiver)
    for v in bm.verts:
        if v.co.x > 0.10:
            t = (v.co.x - 0.10) / 0.060  # 0 .. 1
            t = max(0.0, min(1.0, t))
            v.co.y *= (1.0 - 0.30 * t)  # narrower Y
            v.co.z *= (1.0 - 0.35 * t)  # narrower Z

    # Buttstock bottom angle (preserved from blockout): drop the rear-bottom
    for v in bm.verts:
        if v.co.x < -0.10 and v.co.z < -0.040:
            v.co.z -= 0.005

    # Sling-slot silhouette: shallow recess on the lower-rear edge
    for v in bm.verts:
        if v.co.x < -0.05 and v.co.x > -0.10 and v.co.z < -0.030 and abs(v.co.y) < 0.014:
            v.co.z += 0.003


def build_magazine(bm):
    """§3.4 — banana magazine with raised decorative ribs and floorplate."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.110, 0.050, 0.150), verts=ret["verts"])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=4, use_grid_fill=True)

    # Banana curve: bottom (-Z) shifts forward (+X) on a quadratic curve
    for v in bm.verts:
        z_norm = max(-1.0, min(1.0, v.co.z / 0.075))
        if z_norm < 0:
            curve = ((-z_norm) ** 2) * 0.060
            v.co.x += curve

    # Decorative side ribs (raised bands) on ±Y faces. With cuts=4 the Z
    # verts land at ±0.075, ±0.045, ±0.015 — so target ±0.045 for the bands.
    for v in bm.verts:
        if abs(v.co.y) > 0.022 and (abs(v.co.z - 0.045) < 0.005 or abs(v.co.z + 0.045) < 0.005):
            v.co.y += 0.002 if v.co.y > 0 else -0.002

    # Floorplate at the bottom (slightly larger footprint)
    add_box_bm(
        bm,
        dims=(0.115, 0.060, 0.012),
        location=(0.060, 0.0, -0.080),
    )


def build_grip(bm):
    """§3.5 — pistol grip with finger relief, palm swell, taper, and base cap."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.045, 0.030, 0.115), verts=ret["verts"])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)

    # Top half taper (top narrower in X than bottom)
    for v in bm.verts:
        if v.co.z > 0:
            t = v.co.z / 0.0575
            v.co.x *= (1.0 - 0.45 * t)

    # Concave front (-X): central-front verts pushed inward (+X)
    for v in bm.verts:
        if v.co.x < -0.020 and abs(v.co.z) < 0.030:
            v.co.x += 0.003

    # Convex rear (+X): central-rear verts pushed outward (+X)
    for v in bm.verts:
        if v.co.x > 0.020 and abs(v.co.z) < 0.030:
            v.co.x += 0.003

    # Base cap flange at the bottom (joined into same mesh)
    add_box_bm(
        bm,
        dims=(0.050, 0.034, 0.008),
        location=(0.0, 0.0, -0.062),
    )


def build_handguard_lower(bm):
    """§3.6.1 — lower handguard with finger grooves and front collar."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.130, 0.040, 0.030), verts=ret["verts"])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)

    # Front taller than rear
    for v in bm.verts:
        if v.co.z > 0.013 and v.co.x > 0.040:
            v.co.z += 0.005

    # Lower-face finger grooves: two shallow recesses on -Z face. With
    # cuts=2 the X verts land at ±0.065 and ±0.0217 — target the inner
    # band (~±0.0217) for the grooves.
    for v in bm.verts:
        if v.co.z < -0.013 and (abs(v.co.x) < 0.030 and abs(v.co.x) > 0.012):
            v.co.z += 0.0025

    # Front collar band (additive box)
    add_box_bm(
        bm,
        dims=(0.014, 0.038, 0.028),
        location=(0.072, 0.0, 0.0),
    )


def build_handguard_upper(bm):
    """§3.6.2 — upper handguard with rounded top and rear thumb-shelf."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.150, 0.030, 0.022), verts=ret["verts"])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)

    # Rounded top: cosine falloff lift along X
    for v in bm.verts:
        if v.co.z > 0.005:
            t = v.co.x / 0.075  # -1..1
            lift = 0.003 * math.cos(t * math.pi / 2.0)
            v.co.z += max(0.0, lift)

    # Rear thumb-shelf raise
    add_box_bm(
        bm,
        dims=(0.018, 0.024, 0.006),
        location=(-0.066, 0.0, 0.013),
    )


def build_barrel(bm):
    """§3.7 — barrel cylinder tapered toward muzzle + decorative collar ring,
    closed muzzle disc (no bore)."""
    # Main barrel
    barrel_verts = add_cyl_bm(bm, radius=0.0090, depth=0.320, segments=32, axis="X")
    # Per-vertex taper toward +X muzzle (~89% of base radius at +X end)
    for v in barrel_verts:
        if v.co.x > 0:
            t = v.co.x / 0.160  # 0..1
            s = 1.0 - 0.11 * t
            v.co.y *= s
            v.co.z *= s

    # Decorative collar near the muzzle end
    add_cyl_bm(bm, radius=0.0125, depth=0.010, segments=32, axis="X", location=(0.150, 0, 0))


def build_dustcover(bm):
    """§3.8 — dust cover with convex top, rear dip, front lip."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.220, 0.036, 0.014), verts=ret["verts"])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)

    # Convex top profile: cosine falloff lift on +Z
    for v in bm.verts:
        if v.co.z > 0:
            t = v.co.x / 0.110  # -1..1
            lift = 0.004 * math.cos(t * math.pi / 2.0)
            v.co.z += max(0.0, lift)

    # Rear edge dip (X ~= -0.110, lower-rear edge)
    for v in bm.verts:
        if v.co.x < -0.090 and v.co.z < -0.005:
            v.co.z -= 0.003

    # Front lip (X ~= +0.105 area)
    for v in bm.verts:
        if v.co.x > 0.085 and v.co.z > 0.005:
            v.co.z += 0.002


# ---------- spec: 8 AK_ parts ----------
PARTS = [
    # (name, builder, location, rotation_deg, material, bevel_width)
    ("AK_receiver_main",        build_receiver,        (-0.065, 0.0,  0.000),  (0, 0, 0),    "MAT_placeholder_dark_metal",   0.0020),
    ("AK_stock_main",           build_stock,           (-0.340, 0.0, -0.005),  (0, 0, 0),    "MAT_placeholder_dark_wood",    0.0025),
    ("AK_magazine_main",        build_magazine,        (-0.050, 0.0, -0.105),  (0, 0, 0),    "MAT_placeholder_black_metal",  0.0015),
    ("AK_grip_main",            build_grip,            (-0.090, 0.0, -0.090),  (0, -18, 0),  "MAT_placeholder_bakelite_grip",0.0020),
    ("AK_handguard_lower_main", build_handguard_lower, ( 0.135, 0.0,  0.005),  (0, 0, 0),    "MAT_placeholder_dark_wood",    0.0020),
    ("AK_handguard_upper_main", build_handguard_upper, ( 0.140, 0.0,  0.050),  (0, 0, 0),    "MAT_placeholder_dark_wood",    0.0018),
    ("AK_barrel_exterior_main", build_barrel,          ( 0.250, 0.0,  0.020),  (0, 0, 0),    "MAT_placeholder_dark_metal",   0.0015),
    ("AK_dustcover_main",       build_dustcover,       (-0.065, 0.0,  0.046),  (0, 0, 0),    "MAT_placeholder_dark_metal",   0.0018),
]


# ---------- ensure 03_MAJOR_PARTS collection exists ----------
major_parts = get_collection("03_MAJOR_PARTS")


# ---------- ensure AK47_MASTER_ASSET empty exists ----------
master = bpy.data.objects.get("AK47_MASTER_ASSET")
if master is None:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    master = bpy.context.active_object
    master.name = "AK47_MASTER_ASSET"
    master.empty_display_size = 0.30
    link_only_to(master, "07_ASSEMBLY")


# ---------- build the 8 AK_ parts ----------
print("\n=== SECTION 3 MAJOR PARTS ===")
for name, builder, loc, rot, mat_name, bw in PARTS:
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bm = bmesh.new()
    builder(bm)
    # Recompute normals + remove doubles for clean meshes (additive boxes
    # may overlap with the main body, which is fine for visuals; merge any
    # duplicate verts within a tight tolerance)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    obj = make_object_from_bmesh(name, bm, location=loc, rotation_deg=rot)
    add_bevel_and_weighted_normals(obj, width=bw)
    assign_material(obj, mat_name)
    link_only_to(obj, "03_MAJOR_PARTS")
    # Parent to master, preserving world transform
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    print(f"  built {name}: {len(obj.data.vertices)}v  loc={loc}  mat={mat_name}")


# ---------- hide 02_BLOCKOUT in viewport + render ----------
blockout = bpy.data.collections.get("02_BLOCKOUT")
if blockout is not None:
    # Find the layer-collection entry and hide it in the viewport
    def find_layer_collection(layer_coll, target_name):
        if layer_coll.collection.name == target_name:
            return layer_coll
        for child in layer_coll.children:
            r = find_layer_collection(child, target_name)
            if r is not None:
                return r
        return None

    view_layer = bpy.context.view_layer
    lc = find_layer_collection(view_layer.layer_collection, "02_BLOCKOUT")
    if lc is not None:
        lc.hide_viewport = True
    blockout.hide_render = True
    blockout.hide_viewport = True
    print("  hid 02_BLOCKOUT in viewport + render")


# ---------- save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")
