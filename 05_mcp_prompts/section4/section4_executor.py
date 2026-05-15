"""Section 4 auto-executor: adds minor exterior detail objects on top of
v03_major_parts.blend and saves v04_minor_details.blend.

Auto-detects the project root from __file__ — no hardcoded path.

Per §4.3 of the plan, detail is *surface-only*. All detail meshes are tiny
(rivets 2 mm, ribs 0.5–1 mm raised, seams 0.4 mm thick) and placed relative
to each AK_ major part's world bounding box so they follow the parent's
transform. Every detail is parented to AK47_MASTER_ASSET.

All exterior-only. No internal mechanism, no functional geometry.
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector


# ---------- 0. paths ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v03_major_parts.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v04_minor_details.blend")

print(f"\n=== SECTION 4 — MINOR EXTERIOR DETAILS ===")
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


def add_small_bevel_wn(obj, width=0.0004, segments=2, angle_deg=30):
    bev = obj.modifiers.new("Bevel", type="BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(angle_deg)
    wn = obj.modifiers.new("WeightedNormal", type="WEIGHTED_NORMAL")
    wn.weight = 50
    wn.thresh = 0.01
    wn.keep_sharp = True


def add_box_bm(bm, dims, location=(0, 0, 0)):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=dims, verts=ret["verts"])
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])


def add_cyl_bm(bm, radius, depth, segments=16, axis="Z", location=(0, 0, 0)):
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


def add_torus_bm(bm, major_radius, minor_radius, major_seg=24, minor_seg=8, axis="X"):
    bmesh.ops.create_uvsphere(bm, u_segments=4, v_segments=4, radius=0.0)
    # We'll build the torus manually since bmesh.ops doesn't have create_torus
    # Approach: place small circles around a circle
    bm.verts.ensure_lookup_table()
    # Clear any leftover verts
    bmesh.ops.delete(bm, geom=list(bm.verts), context="VERTS")
    # Build torus by hand
    verts = []
    for i in range(major_seg):
        a = (i / major_seg) * 2 * math.pi
        center = Vector((major_radius * math.cos(a), 0.0, major_radius * math.sin(a)))
        for j in range(minor_seg):
            b = (j / minor_seg) * 2 * math.pi
            offset_in_plane = Vector((math.cos(a), 0.0, math.sin(a))) * (minor_radius * math.cos(b))
            offset_normal = Vector((0.0, minor_radius * math.sin(b), 0.0))
            verts.append(bm.verts.new(center + offset_in_plane + offset_normal))
    # Build quads
    for i in range(major_seg):
        for j in range(minor_seg):
            v0 = verts[i * minor_seg + j]
            v1 = verts[i * minor_seg + (j + 1) % minor_seg]
            v2 = verts[((i + 1) % major_seg) * minor_seg + (j + 1) % minor_seg]
            v3 = verts[((i + 1) % major_seg) * minor_seg + j]
            bm.faces.new([v0, v1, v2, v3])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if axis == "X":
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                          matrix=Matrix.Rotation(math.radians(90), 4, "Y"),
                          verts=bm.verts[:])
    elif axis == "Z":
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                          matrix=Matrix.Rotation(math.radians(90), 4, "X"),
                          verts=bm.verts[:])


def make_visual_object(name, build_fn, sub_collection, location, mat_name,
                        rotation_deg=(0, 0, 0), bevel=True):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bm = bmesh.new()
    build_fn(bm)
    if bm.faces:
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

    if bevel:
        add_small_bevel_wn(obj)
    assign_material(obj, mat_name)
    return obj


def world_bbox(name):
    """Return (min Vec, max Vec, centre Vec) of named object in world space."""
    o = bpy.data.objects.get(name)
    if o is None:
        return None, None, None
    coords = [o.matrix_world @ Vector(v) for v in o.bound_box]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    mn = Vector((min(xs), min(ys), min(zs)))
    mx = Vector((max(xs), max(ys), max(zs)))
    return mn, mx, (mn + mx) * 0.5


# ---------- 1. build collection structure (§4.4.1 + 4.12.1 + 4.13.1) ----------
print("\n-- collections --")
minor = get_or_make_collection("04_MINOR_PARTS")
for sub in ("04A_receiver_details", "04B_dustcover_details", "04C_magazine_details",
            "04D_wood_details", "04E_grip_details", "04F_sling_loop",
            "04G_surface_seams", "04H_detail_backup",
            "04I_front_details", "04J_sight_details"):
    get_or_make_collection(sub, parent_name="04_MINOR_PARTS")
print(f"  04_MINOR_PARTS with 10 sub-collections")


# ---------- 2. receiver details (§4.6) ----------
print("\n-- receiver details --")
mn, mx, c = world_bbox("AK_receiver_main")
if mn is not None:
    DARK = "MAT_placeholder_dark_metal"
    rec_y_side = mx.y - 0.001  # near the +Y side face (slightly inset)
    rec_top_z = mx.z

    # 3 rivets along upper portion of side face
    for i, rx in enumerate((mn.x + 0.030, c.x, mx.x - 0.030)):
        def rivet(bm, radius=0.0035, depth=0.0010):
            add_cyl_bm(bm, radius=radius, depth=depth, segments=12, axis="Y")
        make_visual_object(f"AK_rivet_receiver_00{i+1}", rivet, "04A_receiver_details",
                            location=(rx, rec_y_side + 0.0005, c.z + 0.018),
                            mat_name=DARK)

    # 2 shallow side panel outlines (long thin slabs ~0.5 mm raised)
    panel_y = mx.y + 0.0003  # 0.3 mm proud of side surface
    for i, span in enumerate(((-0.075, +0.060, +0.014),
                              (-0.075, +0.060, -0.014))):
        x0, x1, pz = span
        def panel(bm, x0=x0, x1=x1):
            add_box_bm(bm, dims=(x1 - x0, 0.0006, 0.006), location=(0, 0, 0))
        make_visual_object(f"AK_panel_receiver_side_00{i+1}", panel,
                            "04A_receiver_details",
                            location=((x0 + x1) * 0.5, panel_y, c.z + pz),
                            mat_name=DARK)

    # Decorative selector-style lever silhouette
    def lever(bm):
        add_box_bm(bm, dims=(0.022, 0.002, 0.008), location=(0, 0, 0))
    make_visual_object("AK_lever_receiver_visual_001", lever,
                        "04A_receiver_details",
                        location=(mx.x - 0.030, mx.y + 0.001, c.z + 0.010),
                        mat_name=DARK)

    # Receiver edge wear (subtle strip across the top of the side face)
    def wear_strip(bm):
        add_box_bm(bm, dims=(0.180, 0.0005, 0.003), location=(0, 0, 0))
    make_visual_object("AK_wear_receiver_edge_001", wear_strip,
                        "04A_receiver_details",
                        location=(c.x, mx.y + 0.0002, mx.z - 0.005),
                        mat_name=DARK)


# ---------- 3. dust cover details (§4.7) ----------
print("\n-- dust cover details --")
mn, mx, c = world_bbox("AK_dustcover_main")
if mn is not None:
    DARK = "MAT_placeholder_dark_metal"

    # 2 long raised ribs along the top surface
    for i, dy in enumerate((+0.006, -0.006)):
        def rib(bm):
            add_box_bm(bm, dims=(0.180, 0.0025, 0.0010), location=(0, 0, 0))
        make_visual_object(f"AK_rib_dustcover_00{i+1}", rib,
                            "04B_dustcover_details",
                            location=(c.x, c.y + dy, mx.z + 0.0005),
                            mat_name=DARK)

    # Seam between cover and receiver — thin strip along the bottom edge
    def seam(bm):
        add_box_bm(bm, dims=(0.200, 0.040, 0.0006), location=(0, 0, 0))
    make_visual_object("AK_seam_dustcover_receiver_001", seam,
                        "04B_dustcover_details",
                        location=(c.x, c.y, mn.z - 0.0003),
                        mat_name=DARK)


# ---------- 4. magazine details (§4.8) ----------
print("\n-- magazine details --")
mn, mx, c = world_bbox("AK_magazine_main")
if mn is not None:
    BLACK = "MAT_placeholder_black_metal"

    # 3 broad shallow vertical grooves on the side face (Y side)
    for i, dx in enumerate((-0.025, 0.0, +0.025)):
        def groove(bm):
            add_box_bm(bm, dims=(0.0030, 0.0008, 0.130), location=(0, 0, 0))
        make_visual_object(f"AK_groove_magazine_00{i+1}", groove,
                            "04C_magazine_details",
                            location=(c.x + dx, mx.y + 0.0004, c.z + 0.010),
                            mat_name=BLACK)

    # Front + rear spine surface emphasis (thin ridges along curved edges)
    def front_ridge(bm):
        add_box_bm(bm, dims=(0.0030, 0.026, 0.140), location=(0, 0, 0))
    make_visual_object("AK_ridge_magazine_front_001", front_ridge,
                        "04C_magazine_details",
                        location=(mx.x - 0.001, c.y, c.z),
                        mat_name=BLACK)

    def rear_ridge(bm):
        add_box_bm(bm, dims=(0.0030, 0.026, 0.140), location=(0, 0, 0))
    make_visual_object("AK_ridge_magazine_rear_001", rear_ridge,
                        "04C_magazine_details",
                        location=(mn.x + 0.001, c.y, c.z),
                        mat_name=BLACK)

    # Decorative baseplate seam
    def base_seam(bm):
        add_box_bm(bm, dims=(0.118, 0.030, 0.0006), location=(0, 0, 0))
    make_visual_object("AK_seam_magazine_baseplate_001", base_seam,
                        "04C_magazine_details",
                        location=(c.x + 0.025, c.y, mn.z + 0.012),
                        mat_name=BLACK)

    # Subtle wear placeholder near bottom edge
    def mag_wear(bm):
        add_box_bm(bm, dims=(0.110, 0.0005, 0.003), location=(0, 0, 0))
    make_visual_object("AK_wear_magazine_edge_001", mag_wear,
                        "04C_magazine_details",
                        location=(c.x + 0.020, mx.y + 0.0002, mn.z + 0.018),
                        mat_name=BLACK)


# ---------- 5. wood details — stock + handguards (§4.9, §4.10) ----------
print("\n-- wood details --")
WOOD = "MAT_placeholder_dark_wood"

# Stock contour + wear
mn, mx, c = world_bbox("AK_stock_main")
if mn is not None:
    def contour(bm):
        add_box_bm(bm, dims=(0.180, 0.0008, 0.004), location=(0, 0, 0))
    make_visual_object("AK_wood_contour_stock_001", contour,
                        "04D_wood_details",
                        location=(c.x, mx.y + 0.0003, c.z),
                        mat_name=WOOD)

    for i, pz in enumerate((c.z + 0.020, c.z - 0.020)):
        def stock_wear(bm):
            add_box_bm(bm, dims=(0.100, 0.0005, 0.002), location=(0, 0, 0))
        make_visual_object(f"AK_wear_stock_edge_00{i+1}", stock_wear,
                            "04D_wood_details",
                            location=(c.x, mx.y + 0.0002, pz),
                            mat_name=WOOD)

# Lower handguard grooves + wear
mn_l, mx_l, c_l = world_bbox("AK_handguard_lower_main")
if mn_l is not None:
    for i, pz in enumerate((c_l.z + 0.008, c_l.z - 0.008)):
        def hg_groove(bm):
            add_box_bm(bm, dims=(0.100, 0.0006, 0.0020), location=(0, 0, 0))
        make_visual_object(f"AK_groove_handguard_lower_00{i+1}", hg_groove,
                            "04D_wood_details",
                            location=(c_l.x, mx_l.y + 0.0003, pz),
                            mat_name=WOOD)

    def hg_wear(bm):
        add_box_bm(bm, dims=(0.080, 0.0005, 0.002), location=(0, 0, 0))
    make_visual_object("AK_wear_handguard_edge_001", hg_wear,
                        "04D_wood_details",
                        location=(c_l.x, mx_l.y + 0.0002, mn_l.z + 0.006),
                        mat_name=WOOD)

    def hg_front_seam(bm):
        add_box_bm(bm, dims=(0.0008, 0.040, 0.030), location=(0, 0, 0))
    make_visual_object("AK_seam_handguard_front_001", hg_front_seam,
                        "04D_wood_details",
                        location=(mx_l.x + 0.0004, c_l.y, c_l.z),
                        mat_name=WOOD)

    def hg_rear_seam(bm):
        add_box_bm(bm, dims=(0.0008, 0.040, 0.030), location=(0, 0, 0))
    make_visual_object("AK_seam_handguard_rear_001", hg_rear_seam,
                        "04D_wood_details",
                        location=(mn_l.x - 0.0004, c_l.y, c_l.z),
                        mat_name=WOOD)

# Upper handguard contour
mn_u, mx_u, c_u = world_bbox("AK_handguard_upper_main")
if mn_u is not None:
    def hg_upper_contour(bm):
        add_box_bm(bm, dims=(0.120, 0.0008, 0.003), location=(0, 0, 0))
    make_visual_object("AK_wood_contour_handguard_upper_001", hg_upper_contour,
                        "04D_wood_details",
                        location=(c_u.x, mx_u.y + 0.0003, c_u.z + 0.005),
                        mat_name=WOOD)


# ---------- 6. grip details (§4.11) ----------
print("\n-- grip details --")
mn, mx, c = world_bbox("AK_grip_main")
if mn is not None:
    BAK = "MAT_placeholder_bakelite_grip"

    # 3 broad shallow horizontal grooves on the side face
    for i, pz in enumerate((c.z + 0.025, c.z, c.z - 0.025)):
        def grip_groove(bm):
            add_box_bm(bm, dims=(0.040, 0.0008, 0.0030), location=(0, 0, 0))
        make_visual_object(f"AK_groove_grip_00{i+1}", grip_groove,
                            "04E_grip_details",
                            location=(c.x, mx.y + 0.0004, pz),
                            mat_name=BAK)

    # Base cap seam
    def grip_seam(bm):
        add_box_bm(bm, dims=(0.050, 0.034, 0.0006), location=(0, 0, 0))
    make_visual_object("AK_seam_grip_basecap_001", grip_seam,
                        "04E_grip_details",
                        location=(c.x, c.y, mn.z + 0.005),
                        mat_name=BAK)

    # Lower edge wear
    def grip_wear(bm):
        add_box_bm(bm, dims=(0.040, 0.0005, 0.0020), location=(0, 0, 0))
    make_visual_object("AK_wear_grip_edge_001", grip_wear,
                        "04E_grip_details",
                        location=(c.x, mx.y + 0.0002, mn.z + 0.012),
                        mat_name=BAK)


# ---------- 7. sling loops (§4.14) ----------
print("\n-- sling loops --")
DARK = "MAT_placeholder_dark_metal"

# Rear loop near rear of stock
mn_s, mx_s, c_s = world_bbox("AK_stock_main")
if mn_s is not None:
    def loop_torus(bm, R=0.012, r=0.0015):
        add_torus_bm(bm, major_radius=R, minor_radius=r, major_seg=20, minor_seg=8, axis="X")
    make_visual_object("AK_loop_sling_rear_visual", loop_torus, "04F_sling_loop",
                        location=(mn_s.x + 0.030, c_s.y, mn_s.z + 0.015),
                        mat_name=DARK)

    # Bracket plate near rear loop
    def bracket_plate(bm):
        add_box_bm(bm, dims=(0.020, 0.040, 0.003), location=(0, 0, 0))
    make_visual_object("AK_plate_sling_rear_visual", bracket_plate,
                        "04F_sling_loop",
                        location=(mn_s.x + 0.030, c_s.y, mn_s.z + 0.008),
                        mat_name=DARK)

# Front loop near front of handguard
mn_h, mx_h, c_h = world_bbox("AK_handguard_lower_main")
if mn_h is not None:
    def loop_front(bm, R=0.011, r=0.0015):
        add_torus_bm(bm, major_radius=R, minor_radius=r, major_seg=20, minor_seg=8, axis="X")
    make_visual_object("AK_loop_sling_front_visual", loop_front,
                        "04F_sling_loop",
                        location=(mx_h.x - 0.010, c_h.y, mn_h.z - 0.005),
                        mat_name=DARK)


# ---------- 8. surface seams between parts (§4.16) ----------
print("\n-- surface seams --")
# Stock-to-receiver seam: thin strip near receiver-back / stock-front
mn_r, mx_r, c_r = world_bbox("AK_receiver_main")
mn_s, mx_s, c_s = world_bbox("AK_stock_main")
if mn_r is not None and mn_s is not None:
    def seam(bm):
        add_box_bm(bm, dims=(0.0008, 0.045, 0.080), location=(0, 0, 0))
    make_visual_object("AK_seam_stock_receiver_001", seam,
                        "04G_surface_seams",
                        location=((mx_s.x + mn_r.x) * 0.5, c_r.y, c_r.z),
                        mat_name=DARK)

# Grip-to-receiver seam (thin strip at top of grip)
mn_g, mx_g, c_g = world_bbox("AK_grip_main")
if mn_g is not None and mn_r is not None:
    def seam(bm):
        add_box_bm(bm, dims=(0.045, 0.034, 0.0008), location=(0, 0, 0))
    make_visual_object("AK_seam_grip_receiver_001", seam,
                        "04G_surface_seams",
                        location=(c_g.x, c_g.y, mx_g.z + 0.0004),
                        mat_name=DARK)

# Handguard-to-receiver seam
mn_h, mx_h, c_h = world_bbox("AK_handguard_lower_main")
if mn_r is not None and mn_h is not None:
    def seam(bm):
        add_box_bm(bm, dims=(0.0008, 0.045, 0.045), location=(0, 0, 0))
    make_visual_object("AK_seam_handguard_receiver_001", seam,
                        "04G_surface_seams",
                        location=((mx_r.x + mn_h.x) * 0.5, c_r.y, c_h.z),
                        mat_name=DARK)

# Barrel-to-front seam
mn_b, mx_b, c_b = world_bbox("AK_barrel_outer_closed")
mn_fb, mx_fb, c_fb = world_bbox("AK_gas_block_visual")
if mn_b is not None and mn_fb is not None:
    def seam(bm):
        add_cyl_bm(bm, radius=0.0090, depth=0.0010, segments=16, axis="X")
    make_visual_object("AK_seam_barrel_front_001", seam,
                        "04G_surface_seams",
                        location=(mn_fb.x - 0.0005, c_b.y, c_b.z),
                        mat_name=DARK)


# ---------- 9. front assembly details (§4.12) ----------
print("\n-- front details --")
mn, mx, c = world_bbox("AK_barrel_outer_closed")
if mn is not None:
    # 2 decorative bands around the barrel
    for i, dx in enumerate((mn.x + 0.080, mx.x - 0.020)):
        def ring(bm):
            add_cyl_bm(bm, radius=0.0095, depth=0.0040, segments=18, axis="X")
        make_visual_object(f"AK_ring_barrel_visual_00{i+1}", ring,
                            "04I_front_details",
                            location=(dx, c.y, c.z),
                            mat_name=DARK)

    # Cleaning rod visual line under the barrel
    def cleaning_rod(bm):
        add_cyl_bm(bm, radius=0.0020, depth=0.180, segments=10, axis="X")
    make_visual_object("AK_line_cleaningrod_visual_001", cleaning_rod,
                        "04I_front_details",
                        location=(c.x, c.y, mn.z - 0.005),
                        mat_name=DARK)

# Front block seam (where gas_block meets barrel)
mn_fb, mx_fb, c_fb = world_bbox("AK_gas_block_visual")
if mn_fb is not None:
    def front_block_seam(bm):
        add_box_bm(bm, dims=(0.0008, 0.028, 0.028), location=(0, 0, 0))
    make_visual_object("AK_seam_front_block_001", front_block_seam,
                        "04I_front_details",
                        location=(mn_fb.x - 0.0004, c_fb.y, c_fb.z),
                        mat_name=DARK)

# Front sight edge wear
mn_fs, mx_fs, c_fs = world_bbox("AK_front_sight_block_visual")
if mn_fs is not None:
    def fs_wear(bm):
        add_box_bm(bm, dims=(0.020, 0.0005, 0.0015), location=(0, 0, 0))
    make_visual_object("AK_wear_front_sight_edge_001", fs_wear,
                        "04I_front_details",
                        location=(c_fs.x, mx_fs.y + 0.0002, mx_fs.z - 0.002),
                        mat_name=DARK)


# ---------- 10. rear sight details (§4.13) ----------
print("\n-- rear sight details --")
mn, mx, c = world_bbox("AK_rear_sight_visual")
if mn is not None:
    # Small raised top shape
    def rs_top(bm):
        add_box_bm(bm, dims=(0.014, 0.012, 0.002), location=(0, 0, 0))
    make_visual_object("AK_detail_rearsight_001", rs_top,
                        "04J_sight_details",
                        location=(c.x, c.y, mx.z + 0.001),
                        mat_name=DARK)

    # Shallow visual notch (thin slot)
    def rs_notch(bm):
        add_box_bm(bm, dims=(0.0040, 0.0030, 0.0020), location=(0, 0, 0))
    make_visual_object("AK_notch_rearsight_visual_001", rs_notch,
                        "04J_sight_details",
                        location=(c.x, c.y, mx.z + 0.002),
                        mat_name=DARK)

    # Edge wear
    def rs_wear(bm):
        add_box_bm(bm, dims=(0.022, 0.0005, 0.0010), location=(0, 0, 0))
    make_visual_object("AK_wear_rearsight_edge_001", rs_wear,
                        "04J_sight_details",
                        location=(c.x, mx.y + 0.0002, mx.z - 0.002),
                        mat_name=DARK)


# ---------- 11. save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")

# Summary count of new detail objects
minor = bpy.data.collections.get("04_MINOR_PARTS")
if minor:
    total = sum(len(c.objects) for c in minor.children) + len(minor.objects)
    print(f"  total detail objects in 04_MINOR_PARTS: {total}")
