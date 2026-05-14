"""Section 4 auto-executor: adds ~50 minor exterior detail objects on top of
the Section 3 major parts.

Reads v03_major_parts.blend, creates the 9 sub-collections under
04_MINOR_PARTS, creates the 2 new placeholder materials, builds all detail
objects per §4.4..§4.22, parents them to AK47_MASTER_ASSET, hides
04Z_detail_tests_archive, and saves v04_minor_details.blend.

Strictly exterior-only: no bore, no chamber, no working trigger, no functional
magazine, no real openings, no real screw holes. All details are surface
placeholders.
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v03_major_parts.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v04_minor_details.blend")


# ---------- 0. start from v03 ----------
bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)


# ---------- helpers ----------
def ensure_collection(name, parent=None):
    """Ensure a collection with `name` exists; if `parent` is given, ensure
    it is linked under that parent collection."""
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    parent_coll = parent if parent is not None else bpy.context.scene.collection
    if c.name not in [child.name for child in parent_coll.children]:
        # Unlink from scene root if it's there spuriously
        scene_root = bpy.context.scene.collection
        if c.name in [child.name for child in scene_root.children] and parent is not None and parent.name != scene_root.name:
            scene_root.children.unlink(c)
        parent_coll.children.link(c)
    return c


def link_only_to(obj, collection):
    """Move obj so it lives in exactly one collection."""
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


def ensure_material(name, base_color, roughness=0.6, metallic=0.4):
    """Create a Principled BSDF placeholder material if it doesn't already exist."""
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


def assign_material(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def add_small_bevel(obj, width=0.0005, segments=1, angle_deg=30):
    """Tiny bevel for detail objects — keeps shading clean without adding cost."""
    bev = obj.modifiers.new("Bevel", type="BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(angle_deg)


def make_box_obj(name, dims, location, rotation_deg=(0, 0, 0)):
    bm = bmesh.new()
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=dims, verts=ret["verts"])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = tuple(math.radians(d) for d in rotation_deg)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_cyl_obj(name, radius, depth, location, rotation_deg=(0, 0, 0), segments=12):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, segments=segments, radius1=radius, radius2=radius,
        depth=depth, cap_ends=True, cap_tris=False,
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = tuple(math.radians(d) for d in rotation_deg)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_torus_obj(name, major_r, minor_r, location, rotation_deg=(0, 0, 0),
                   major_segments=24, minor_segments=10):
    """Build a torus via two concentric circles bridged. Lies in the XY plane
    before rotation."""
    bm = bmesh.new()
    ring_verts = []
    for i in range(major_segments):
        ang = (i / major_segments) * 2.0 * math.pi
        cx = math.cos(ang) * major_r
        cy = math.sin(ang) * major_r
        for j in range(minor_segments):
            mang = (j / minor_segments) * 2.0 * math.pi
            dx = math.cos(mang) * minor_r
            dz = math.sin(mang) * minor_r
            v = bm.verts.new((cx + dx * math.cos(ang),
                              cy + dx * math.sin(ang),
                              dz))
            ring_verts.append(v)
    bm.verts.ensure_lookup_table()
    for i in range(major_segments):
        for j in range(minor_segments):
            a = i * minor_segments + j
            b = i * minor_segments + (j + 1) % minor_segments
            c = ((i + 1) % major_segments) * minor_segments + (j + 1) % minor_segments
            d = ((i + 1) % major_segments) * minor_segments + j
            bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = tuple(math.radians(d) for d in rotation_deg)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def hide_collection_in_view_layer(coll_name):
    """Hide a collection in the active view layer and at the data level."""
    coll = bpy.data.collections.get(coll_name)
    if coll is None:
        return False
    coll.hide_viewport = True
    coll.hide_render = True

    def find_layer(layer_coll, target):
        if layer_coll.collection.name == target:
            return layer_coll
        for child in layer_coll.children:
            r = find_layer(child, target)
            if r is not None:
                return r
        return None

    lc = find_layer(bpy.context.view_layer.layer_collection, coll_name)
    if lc is not None:
        lc.hide_viewport = True
    return True


# ---------- 1. ensure new materials ----------
print("\n=== SECTION 4 SETUP ===")
shadow_mat = ensure_material(
    "MAT_placeholder_shadow_seam",
    base_color=(0.025, 0.025, 0.028),
    roughness=0.85,
    metallic=0.0,
)
edge_mat = ensure_material(
    "MAT_placeholder_edge_wear",
    base_color=(0.45, 0.43, 0.40),
    roughness=0.45,
    metallic=0.55,
)
print(f"  ensured material: {shadow_mat.name}")
print(f"  ensured material: {edge_mat.name}")


# ---------- 2. ensure 04_MINOR_PARTS + sub-collections ----------
minor_parts_root = ensure_collection("04_MINOR_PARTS")
SUBCOLLS = [
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
sub_lookup = {}
for sc_name in SUBCOLLS:
    sc = ensure_collection(sc_name, parent=minor_parts_root)
    sub_lookup[sc_name] = sc
    print(f"  ensured sub-collection: {sc_name}")


# ---------- 3. detail spec table ----------
# Each entry: (name, primitive, params, location, rotation_deg, material, subcoll)
# primitive == "box":  params = (dx, dy, dz)
# primitive == "cyl":  params = (radius, depth, axis, segments)
# primitive == "tor":  params = (major_r, minor_r, major_segs, minor_segs)
DETAIL_SPECS = []

# --- 04A receiver details (11 objects) ---
RIVET_R = 0.0015
RIVET_D = 0.003
# Rivets — two rows on +Y face of receiver at z = ±0.018, three X positions
for i, x in enumerate([-0.155, -0.075, +0.005]):
    DETAIL_SPECS.append((
        f"AK_rivet_receiver_{i+1:03d}", "cyl",
        (RIVET_R, RIVET_D, "Y", 14),
        (x, 0.021, 0.018), (0, 0, 0),
        "MAT_placeholder_dark_metal", "04A_receiver_details",
    ))
for i, x in enumerate([-0.155, -0.075, +0.005]):
    DETAIL_SPECS.append((
        f"AK_rivet_receiver_{i+4:03d}", "cyl",
        (RIVET_R, RIVET_D, "Y", 14),
        (x, 0.021, -0.018), (0, 0, 0),
        "MAT_placeholder_dark_metal", "04A_receiver_details",
    ))
# Side panel lines
DETAIL_SPECS += [
    ("AK_panel_receiver_side_001", "box", (0.040, 0.0010, 0.012),
     (-0.030, 0.021, 0.000), (0, 0, 0),
     "MAT_placeholder_dark_metal", "04A_receiver_details"),
    ("AK_panel_receiver_side_002", "box", (0.040, 0.0010, 0.012),
     (-0.110, 0.021, 0.000), (0, 0, 0),
     "MAT_placeholder_dark_metal", "04A_receiver_details"),
    # Top seam where dust cover meets receiver
    ("AK_seam_receiver_top_001", "box", (0.220, 0.034, 0.0008),
     (-0.065, 0.0, 0.039), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04A_receiver_details"),
    # Vertical boundary seams
    ("AK_seam_receiver_stock_001", "box", (0.0008, 0.040, 0.080),
     (-0.180, 0.0, 0.0), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04A_receiver_details"),
    ("AK_seam_receiver_handguard_001", "box", (0.0008, 0.040, 0.080),
     (0.050, 0.0, 0.0), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04A_receiver_details"),
]

# --- 04B dust cover details (5 objects) ---
for i, x in enumerate([-0.120, -0.065, -0.010]):
    DETAIL_SPECS.append((
        f"AK_rib_dustcover_{i+1:03d}", "box",
        (0.0030, 0.030, 0.0020),
        (x, 0.0, 0.055), (0, 0, 0),
        "MAT_placeholder_dark_metal", "04B_dustcover_details",
    ))
DETAIL_SPECS += [
    ("AK_seam_dustcover_side_001", "box", (0.218, 0.0008, 0.005),
     (-0.065, 0.019, 0.046), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04B_dustcover_details"),
    ("AK_seam_dustcover_side_002", "box", (0.218, 0.0008, 0.005),
     (-0.065, -0.019, 0.046), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04B_dustcover_details"),
]

# --- 04C magazine details (7 objects) ---
# The magazine front face curls forward as Z drops (banana curve):
# world X(front) = -0.050 + 0.055 + max(0, -((world_z+0.105)/0.075))**2 * 0.060
# Place each groove at the actual front-face X + 0.0005 so it sits as a
# raised band on the surface (not embedded, not floating).
def _mag_front_x(world_z):
    local_z = world_z - (-0.105)
    z_norm = max(-1.0, min(1.0, local_z / 0.075))
    curl = (max(0.0, -z_norm) ** 2) * 0.060
    return -0.050 + 0.055 + curl + 0.0005

MAG_GROOVE_Z = [-0.045, -0.085, -0.125, -0.165]
for i, mz in enumerate(MAG_GROOVE_Z):
    DETAIL_SPECS.append((
        f"AK_groove_magazine_{i+1:03d}", "box",
        (0.0015, 0.030, 0.005),
        (_mag_front_x(mz), 0.0, mz), (0, 0, 0),
        "MAT_placeholder_black_metal", "04C_magazine_details",
    ))
DETAIL_SPECS += [
    # Front spine: centred where the curl is small, slightly outside the front face
    ("AK_spine_magazine_front_001", "box", (0.003, 0.012, 0.060),
     (_mag_front_x(-0.085) + 0.0005, 0.0, -0.085), (0, 0, 0),
     "MAT_placeholder_black_metal", "04C_magazine_details"),
    # Rear spine: rear face is at world X=-0.105, place at -0.106 (just outside)
    ("AK_spine_magazine_rear_001", "box", (0.003, 0.012, 0.060),
     (-0.106, 0.0, -0.085), (0, 0, 0),
     "MAT_placeholder_black_metal", "04C_magazine_details"),
    # Baseplate seam: baseplate top is at world Z=-0.179, sit the seam right there
    ("AK_seam_magazine_baseplate_001", "box", (0.118, 0.062, 0.0008),
     (0.010, 0.0, -0.179), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04C_magazine_details"),
]

# --- 04D wood details (9 objects) ---
# All wood contours are side-mounted strips that hug the ±Y face of their
# host (so they read from the standard 3/4 view). Each contour center sits
# 0.0005 m outside the host surface so half the strip is embedded and half
# protrudes — i.e., a clean raised band on the face.
DETAIL_SPECS += [
    ("AK_contour_stock_001", "box", (0.280, 0.001, 0.002),
     (-0.340, 0.0205, 0.030), (0, 0, 0),
     "MAT_placeholder_dark_wood", "04D_wood_details"),
    ("AK_contour_stock_002", "box", (0.280, 0.001, 0.002),
     (-0.340, 0.0205, -0.040), (0, 0, 0),
     "MAT_placeholder_dark_wood", "04D_wood_details"),
    ("AK_contour_handguard_lower_001", "box", (0.120, 0.0008, 0.002),
     (0.135, 0.0205, 0.005), (0, 0, 0),
     "MAT_placeholder_dark_wood", "04D_wood_details"),
    ("AK_contour_handguard_lower_002", "box", (0.120, 0.0008, 0.002),
     (0.135, -0.0205, 0.005), (0, 0, 0),
     "MAT_placeholder_dark_wood", "04D_wood_details"),
    ("AK_contour_handguard_upper_001", "box", (0.140, 0.0008, 0.002),
     (0.140, 0.0155, 0.050), (0, 0, 0),
     "MAT_placeholder_dark_wood", "04D_wood_details"),
    ("AK_contour_handguard_upper_002", "box", (0.140, 0.0008, 0.002),
     (0.140, -0.0155, 0.050), (0, 0, 0),
     "MAT_placeholder_dark_wood", "04D_wood_details"),
    ("AK_wear_placeholder_wood_edge_001", "box", (0.005, 0.040, 0.0006),
     (-0.500, 0.0, 0.0), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04D_wood_details"),
    ("AK_wear_placeholder_wood_edge_002", "box", (0.005, 0.040, 0.0006),
     (0.200, 0.0, 0.005), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04D_wood_details"),
    ("AK_wear_placeholder_wood_edge_003", "box", (0.005, 0.030, 0.0006),
     (0.065, 0.0, 0.050), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04D_wood_details"),
]

# --- 04E grip details (4 objects, rotated -18° to match grip tilt) ---
GRIP_TILT_DEG = (0, -18, 0)
DETAIL_SPECS += [
    ("AK_groove_grip_001", "box", (0.0015, 0.020, 0.004),
     (-0.110, 0.0, -0.060), GRIP_TILT_DEG,
     "MAT_placeholder_bakelite_grip", "04E_grip_details"),
    ("AK_groove_grip_002", "box", (0.0015, 0.020, 0.004),
     (-0.110, 0.0, -0.090), GRIP_TILT_DEG,
     "MAT_placeholder_bakelite_grip", "04E_grip_details"),
    ("AK_groove_grip_003", "box", (0.0015, 0.020, 0.004),
     (-0.110, 0.0, -0.120), GRIP_TILT_DEG,
     "MAT_placeholder_bakelite_grip", "04E_grip_details"),
    ("AK_seam_grip_basecap_001", "box", (0.052, 0.036, 0.0008),
     (-0.090, 0.0, -0.150), GRIP_TILT_DEG,
     "MAT_placeholder_shadow_seam", "04E_grip_details"),
]

# --- 04F sight + front details (3 objects) ---
DETAIL_SPECS += [
    ("AK_cap_front_sight_001", "box", (0.008, 0.004, 0.003),
     (0.405, 0.0, 0.075), (0, 0, 0),
     "MAT_placeholder_dark_metal", "04F_sight_front_details"),
    ("AK_seam_gas_block_001", "box", (0.026, 0.034, 0.0008),
     (0.275, 0.0, 0.040), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04F_sight_front_details"),
    ("AK_ring_front_001", "tor", (0.013, 0.0015, 24, 10),
     (0.395, 0.0, 0.020), (0, 90, 0),
     "MAT_placeholder_dark_metal", "04F_sight_front_details"),
]

# --- 04G sling loops (2 objects) ---
# Each loop is a torus oriented with its ring in the X-Z plane (hole faces
# ±Y). Centred at y = +0.022 so the tube straddles the host's +Y surface
# (≈ y = +0.020 for stock and lower handguard) — half embedded, half
# protruding outward as a decorative attachment.
DETAIL_SPECS += [
    ("AK_loop_sling_rear_visual", "tor", (0.008, 0.0015, 24, 10),
     (-0.490, 0.022, -0.020), (90, 0, 0),
     "MAT_placeholder_dark_metal", "04G_sling_loop_visuals"),
    ("AK_loop_sling_front_visual", "tor", (0.008, 0.0015, 24, 10),
     (0.195, 0.022, -0.010), (90, 0, 0),
     "MAT_placeholder_dark_metal", "04G_sling_loop_visuals"),
]

# --- 04H general seams + edge-wear (10 objects) ---
DETAIL_SPECS += [
    # General seam markers (5)
    ("AK_seam_visual_001", "box", (0.001, 0.044, 0.010),
     (-0.180, 0.0, -0.040), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04H_seams_and_edge_wear_placeholders"),
    ("AK_seam_visual_002", "box", (0.030, 0.034, 0.001),
     (-0.080, 0.0, -0.040), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04H_seams_and_edge_wear_placeholders"),
    ("AK_seam_visual_003", "box", (0.110, 0.042, 0.001),
     (-0.050, 0.0, -0.040), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04H_seams_and_edge_wear_placeholders"),
    ("AK_seam_visual_004", "box", (0.001, 0.030, 0.044),
     (0.075, 0.0, 0.030), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04H_seams_and_edge_wear_placeholders"),
    ("AK_seam_visual_005", "box", (0.001, 0.018, 0.018),
     (0.392, 0.0, 0.020), (0, 0, 0),
     "MAT_placeholder_shadow_seam", "04H_seams_and_edge_wear_placeholders"),
    # Metal edge wear (3)
    ("AK_wear_placeholder_metal_edge_001", "box", (0.220, 0.0006, 0.0020),
     (-0.065, 0.021, 0.038), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04H_seams_and_edge_wear_placeholders"),
    ("AK_wear_placeholder_metal_edge_002", "box", (0.220, 0.0006, 0.0020),
     (-0.065, -0.021, 0.038), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04H_seams_and_edge_wear_placeholders"),
    ("AK_wear_placeholder_metal_edge_003", "box", (0.001, 0.034, 0.002),
     (0.044, 0.0, 0.050), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04H_seams_and_edge_wear_placeholders"),
    # Wood edge wear (2)
    ("AK_wear_placeholder_wood_edge_004", "box", (0.260, 0.001, 0.002),
     (-0.350, 0.0, 0.040), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04H_seams_and_edge_wear_placeholders"),
    ("AK_wear_placeholder_wood_edge_005", "box", (0.020, 0.040, 0.001),
     (0.200, 0.0, -0.013), (0, 0, 0),
     "MAT_placeholder_edge_wear", "04H_seams_and_edge_wear_placeholders"),
]


# ---------- 4. ensure AK47_MASTER_ASSET ----------
master = bpy.data.objects.get("AK47_MASTER_ASSET")
if master is None:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    master = bpy.context.active_object
    master.name = "AK47_MASTER_ASSET"
    master.empty_display_size = 0.30
    link_only_to(master, ensure_collection("07_ASSEMBLY"))


# ---------- 5. build all details ----------
print(f"\n=== SECTION 4 DETAILS ({len(DETAIL_SPECS)} objects) ===")
built = []
for spec in DETAIL_SPECS:
    name, prim, params, loc, rot, mat_name, sub_name = spec
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    if prim == "box":
        obj = make_box_obj(name, params, loc, rot)
    elif prim == "cyl":
        radius, depth, axis, segments = params
        # Rotation per axis: built along Z by default; rotate to align
        extra_rot = (0, 0, 0)
        if axis == "X":
            extra_rot = (0, 90, 0)
        elif axis == "Y":
            extra_rot = (90, 0, 0)
        # combine the user-supplied rot with axis-orient rot
        combined = (rot[0] + extra_rot[0], rot[1] + extra_rot[1], rot[2] + extra_rot[2])
        obj = make_cyl_obj(name, radius, depth, loc, combined, segments)
    elif prim == "tor":
        major_r, minor_r, major_segs, minor_segs = params
        obj = make_torus_obj(name, major_r, minor_r, loc, rot, major_segs, minor_segs)
    else:
        raise ValueError(f"unknown primitive {prim} for {name}")
    add_small_bevel(obj)
    assign_material(obj, mat_name)
    link_only_to(obj, sub_lookup[sub_name])
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    built.append(obj)


# ---------- 6. hide 04Z archive ----------
hide_collection_in_view_layer("04Z_detail_tests_archive")
print("  hid 04Z_detail_tests_archive in viewport + render")


# ---------- 7. summary ----------
counts = {}
for o in built:
    sc = o.users_collection[0].name if o.users_collection else "<none>"
    counts[sc] = counts.get(sc, 0) + 1
print("\nSub-collection object counts:")
for sc_name in SUBCOLLS:
    print(f"  {sc_name}: {counts.get(sc_name, 0)}")
print(f"  TOTAL details added: {len(built)}")


# ---------- 8. save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")
