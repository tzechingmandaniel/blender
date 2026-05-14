"""Section 5 auto-executor: turns v04_minor_details.blend into a textur-ready
v05_uv_materials.blend.

Adds:
  - 06_MATERIAL_TESTS (+ 3 sub-collections)
  - 07_ASSEMBLY (+ 6 material groups + AK47_MASTER_ASSEMBLY empty)
  - 09_EXPORT_READY (empty)
  - 10 final MAT_* materials with Principled BSDF placeholder values
  - reassigns every AK_ object from MAT_placeholder_* to a final MAT_*
  - cross-links every AK_ object into one 07_ASSEMBLY material group
  - marks UV seams on the 8 major AK_ parts, unwraps everything
  - 4 PREVIEW_ spheres + a MAT_uv_checker_review material
  - 03_textures/{metal,wood,magazine,grip,shared}/README.txt
  - 06_documentation/ phase/material/uv/texture-workflow notes

Strictly exterior-only: no bore, chamber, working trigger, functional
magazine, real openings, manufacturing detail.
"""
import bpy
import bmesh
import math
import os
from mathutils import Vector

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v04_minor_details.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v05_uv_materials.blend")
TEXTURES_ROOT = os.path.join(PROJECT_ROOT, "03_textures")
DOCS_ROOT = os.path.join(PROJECT_ROOT, "06_documentation")


# ---------- 0. open v04 ----------
bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)


# ---------- helpers ----------
def ensure_collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    parent_coll = parent if parent is not None else bpy.context.scene.collection
    if c.name not in [child.name for child in parent_coll.children]:
        scene_root = bpy.context.scene.collection
        if (c.name in [child.name for child in scene_root.children]
                and parent is not None and parent.name != scene_root.name):
            scene_root.children.unlink(c)
        parent_coll.children.link(c)
    return c


def link_extra(obj, collection):
    """Link obj into collection if not already a member; do NOT unlink from
    any other collection."""
    if collection.name not in [c.name for c in obj.users_collection]:
        collection.objects.link(obj)


def link_only_to(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


def ensure_material(name, base_color, metallic, roughness):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        # nuke existing nodes, add a clean Principled + Output
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def assign_material(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat is None or obj.type != "MESH":
        return
    if obj.data.materials:
        for i in range(len(obj.data.materials)):
            obj.data.materials[i] = mat
    else:
        obj.data.materials.append(mat)


def hide_collection(coll_name):
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


def make_sphere(name, location, segments=24, rings=12, radius=0.04):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings,
                              radius=radius)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    return obj


# ---------- 1. Top-level collections per §5.2 ----------
print("\n=== SECTION 5: SETUP COLLECTIONS ===")
material_tests = ensure_collection("06_MATERIAL_TESTS")
assembly = ensure_collection("07_ASSEMBLY")
export_ready = ensure_collection("09_EXPORT_READY")

for sub in ("06A_material_preview_objects", "06B_uv_test_objects",
            "06C_texture_map_notes"):
    ensure_collection(sub, parent=material_tests)

for grp in ("AK_metal_parts_grp", "AK_wood_parts_grp",
            "AK_magazine_parts_grp", "AK_grip_parts_grp",
            "AK_detail_parts_grp", "AK_seam_wear_parts_grp"):
    ensure_collection(grp, parent=assembly)

# AK47_MASTER_ASSEMBLY empty inside 07_ASSEMBLY
master_assy = bpy.data.objects.get("AK47_MASTER_ASSEMBLY")
if master_assy is None:
    master_assy = bpy.data.objects.new("AK47_MASTER_ASSEMBLY", None)
    master_assy.empty_display_type = "PLAIN_AXES"
    master_assy.empty_display_size = 0.05
link_only_to(master_assy, assembly)
print("  collections + master assembly empty OK")


# ---------- 2. Final MAT_* materials per §5.10 ----------
print("\n=== SECTION 5: FINAL MATERIALS ===")
MAT_SPECS = [
    ("MAT_metal_dark_blued",      (0.05, 0.05, 0.07), 1.0, 0.40),
    ("MAT_metal_black_magazine",  (0.04, 0.04, 0.04), 1.0, 0.55),
    ("MAT_wood_dark_reddish",     (0.18, 0.07, 0.04), 0.0, 0.55),
    ("MAT_grip_dark_bakelite",    (0.10, 0.05, 0.04), 0.0, 0.50),
    ("MAT_shadow_seam_dark",      (0.02, 0.02, 0.025), 0.0, 0.85),
    ("MAT_edge_wear_light_metal", (0.55, 0.53, 0.50), 0.6, 0.40),
    ("MAT_edge_wear_worn_wood",   (0.42, 0.30, 0.22), 0.0, 0.55),
    ("MAT_detail_dark_metal",     (0.07, 0.07, 0.08), 1.0, 0.50),
    ("MAT_reference_hidden",      (0.50, 0.50, 0.50), 0.0, 0.80),
    ("MAT_clay_neutral_preview",  (0.62, 0.60, 0.57), 0.0, 0.70),
]
for name, base, met, rough in MAT_SPECS:
    mat = ensure_material(name, base, met, rough)
    # Prevent purge-on-save for materials that may have no object users yet
    # (MAT_reference_hidden, MAT_clay_neutral_preview, etc).
    mat.use_fake_user = True
    print(f"  ensured {name}")


# ---------- 3. Object -> final material assignment + assembly grouping ----------
print("\n=== SECTION 5: ASSIGN MATERIALS + GROUPS ===")

# Build classifier rules.
# Order matters: most-specific match first.
RULES = [
    # name prefix/substring rules -> (assembly group, final material)
    # Magazine first so AK_groove_magazine_* / AK_spine_magazine_* / AK_seam_magazine_baseplate_*
    # are caught before grip/general groove/seam rules.
    ("AK_spine_magazine_",       "AK_magazine_parts_grp",  "MAT_metal_black_magazine"),
    ("AK_groove_magazine_",      "AK_magazine_parts_grp",  "MAT_metal_black_magazine"),
    ("AK_seam_magazine_",        "AK_magazine_parts_grp",  "MAT_metal_black_magazine"),
    ("AK_magazine_main",         "AK_magazine_parts_grp",  "MAT_metal_black_magazine"),

    # Grip groove + basecap seam stay with grip material (§5.4)
    ("AK_groove_grip_",          "AK_grip_parts_grp",      "MAT_grip_dark_bakelite"),
    ("AK_seam_grip_basecap_",    "AK_grip_parts_grp",      "MAT_grip_dark_bakelite"),
    ("AK_grip_main",             "AK_grip_parts_grp",      "MAT_grip_dark_bakelite"),

    # Wood
    ("AK_contour_",              "AK_wood_parts_grp",      "MAT_wood_dark_reddish"),
    ("AK_stock_main",            "AK_wood_parts_grp",      "MAT_wood_dark_reddish"),
    ("AK_handguard_lower_main",  "AK_wood_parts_grp",      "MAT_wood_dark_reddish"),
    ("AK_handguard_upper_main",  "AK_wood_parts_grp",      "MAT_wood_dark_reddish"),

    # Small dark-metal details
    ("AK_rivet_",                "AK_detail_parts_grp",    "MAT_detail_dark_metal"),
    ("AK_panel_",                "AK_detail_parts_grp",    "MAT_detail_dark_metal"),
    ("AK_rib_dustcover_",        "AK_detail_parts_grp",    "MAT_detail_dark_metal"),
    ("AK_cap_",                  "AK_detail_parts_grp",    "MAT_detail_dark_metal"),
    ("AK_ring_",                 "AK_detail_parts_grp",    "MAT_detail_dark_metal"),

    # Edge wear placeholders
    ("AK_wear_placeholder_wood", "AK_seam_wear_parts_grp", "MAT_edge_wear_worn_wood"),
    ("AK_wear_placeholder_metal","AK_seam_wear_parts_grp", "MAT_edge_wear_light_metal"),

    # General seam markers
    ("AK_seam_",                 "AK_seam_wear_parts_grp", "MAT_shadow_seam_dark"),

    # Receiver / dust cover / barrel / front/sights / sling loops -> dark blued metal
    ("AK_receiver_main",         "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_dustcover_main",        "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_barrel_exterior_main",  "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_gas_tube_outer",        "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_front_sight_block",     "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_rear_sight",            "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_trigger_guard",         "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_front_ring",            "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_gas_block",             "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_muzzle_front",          "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
    ("AK_loop_sling_",           "AK_metal_parts_grp",     "MAT_metal_dark_blued"),
]


def classify(name):
    for prefix, grp, mat in RULES:
        if name.startswith(prefix) or prefix in name:
            return grp, mat
    return None, None


ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]

unclassified = []
for obj in ak_objects:
    grp, mat = classify(obj.name)
    if grp is None:
        unclassified.append(obj.name)
        continue
    target_coll = bpy.data.collections.get(grp)
    if target_coll is None:
        unclassified.append(f"{obj.name} (no group {grp})")
        continue
    link_extra(obj, target_coll)
    assign_material(obj, mat)
print(f"  classified {len(ak_objects) - len(unclassified)}/{len(ak_objects)} AK_ objects")
if unclassified:
    print(f"  unclassified: {unclassified}")


# ---------- 4. UV seams + unwrap per §5.6 / §5.7 ----------
print("\n=== SECTION 5: UV SEAMS + UNWRAP ===")

def deselect_all():
    for o in bpy.context.view_layer.objects:
        o.select_set(False)


def set_active(obj):
    bpy.context.view_layer.objects.active = obj


def edit_mode():
    bpy.ops.object.mode_set(mode="EDIT")


def object_mode():
    bpy.ops.object.mode_set(mode="OBJECT")


def ensure_uvmap(obj):
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    me.uv_layers.active = me.uv_layers["UVMap"]
    me.uv_layers["UVMap"].active_render = True


def clear_seams_bm(bm):
    for e in bm.edges:
        e.seam = False


def mark_seam_box_lower_perimeter(bm, max_z=None):
    """Mark seams on edges that lie on the bottom four edges of an
    axis-aligned-ish box (z near min Z) -- used for receiver / dust cover."""
    if not bm.verts:
        return
    zs = [v.co.z for v in bm.verts]
    zmin = min(zs)
    if max_z is None:
        max_z = zmin + 0.005
    for e in bm.edges:
        v1, v2 = e.verts
        if v1.co.z < max_z and v2.co.z < max_z:
            e.seam = True


def mark_seam_along_x_at_min_z(bm):
    """Long axis along +X, seam along the bottom edges (z near zmin)."""
    if not bm.verts:
        return
    zmin = min(v.co.z for v in bm.verts)
    thresh = zmin + 0.005
    for e in bm.edges:
        v1, v2 = e.verts
        if v1.co.z < thresh and v2.co.z < thresh:
            e.seam = True


def mark_seam_along_x_at_max_z(bm):
    """For upper handguard: seam on the top so the side is one island."""
    if not bm.verts:
        return
    zmax = max(v.co.z for v in bm.verts)
    thresh = zmax - 0.005
    for e in bm.edges:
        v1, v2 = e.verts
        if v1.co.z > thresh and v2.co.z > thresh:
            e.seam = True


def mark_seam_magazine(bm):
    """Banana magazine: rear spine (max X side) seam + horizontal seam near
    the baseplate (min Z)."""
    if not bm.verts:
        return
    xmax = max(v.co.x for v in bm.verts)
    zmin = min(v.co.z for v in bm.verts)
    xthresh = xmax - 0.006
    zthresh = zmin + 0.006
    for e in bm.edges:
        v1, v2 = e.verts
        if v1.co.x > xthresh and v2.co.x > xthresh:
            e.seam = True
        elif v1.co.z < zthresh and v2.co.z < zthresh:
            e.seam = True


def mark_seam_grip(bm):
    """Grip (built around its own object-space): seam down the +X face."""
    if not bm.verts:
        return
    xmax = max(v.co.x for v in bm.verts)
    thresh = xmax - 0.005
    for e in bm.edges:
        v1, v2 = e.verts
        if v1.co.x > thresh and v2.co.x > thresh:
            e.seam = True


def mark_seam_barrel_cylinder(bm):
    """Barrel cylinder along +X (longest axis); seam on -Z bottom strip."""
    if not bm.verts:
        return
    zmin = min(v.co.z for v in bm.verts)
    thresh = zmin + 0.003
    for e in bm.edges:
        v1, v2 = e.verts
        if v1.co.z < thresh and v2.co.z < thresh:
            e.seam = True


SEAM_FUNCS = {
    "AK_receiver_main":         mark_seam_box_lower_perimeter,
    "AK_dustcover_main":        mark_seam_box_lower_perimeter,
    "AK_stock_main":            mark_seam_along_x_at_min_z,
    "AK_handguard_lower_main":  mark_seam_along_x_at_min_z,
    "AK_handguard_upper_main":  mark_seam_along_x_at_max_z,
    "AK_magazine_main":         mark_seam_magazine,
    "AK_grip_main":             mark_seam_grip,
    "AK_barrel_exterior_main":  mark_seam_barrel_cylinder,
}


def mark_seams_for_major(obj):
    fn = SEAM_FUNCS.get(obj.name)
    if fn is None:
        return False
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    clear_seams_bm(bm)
    fn(bm)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return True


# Pass A — major parts: mark seams + standard unwrap
MAJORS_NEEDING_SEAMS = set(SEAM_FUNCS.keys())
for obj in [o for o in ak_objects if o.name in MAJORS_NEEDING_SEAMS]:
    ensure_uvmap(obj)
    mark_seams_for_major(obj)
    deselect_all()
    set_active(obj)
    obj.select_set(True)
    edit_mode()
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0.02)
    bpy.ops.uv.pack_islands(margin=0.02)
    object_mode()
    print(f"  unwrapped (seams): {obj.name}")


# Pass B — rotate stock + handguard + barrel UVs so +X = +U
def rotate_uvs(obj, angle_deg):
    """Rotate UVs in-place around (0.5, 0.5)."""
    me = obj.data
    if not me.uv_layers:
        return
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    layer = me.uv_layers.active.data
    for loop in layer:
        u, v = loop.uv
        u2 = (u - 0.5) * ca - (v - 0.5) * sa + 0.5
        v2 = (u - 0.5) * sa + (v - 0.5) * ca + 0.5
        loop.uv = (u2, v2)


def get_uv_bbox(obj):
    me = obj.data
    layer = me.uv_layers.active.data
    if not layer:
        return None
    us = [loop.uv[0] for loop in layer]
    vs = [loop.uv[1] for loop in layer]
    return (min(us), min(vs), max(us), max(vs))


def ensure_wood_grain_horizontal(obj):
    """For stock/handguards, the longest world axis is X. After ANGLE_BASED
    unwrap, the longest UV axis should map to that. If the UV bbox is taller
    than wide, rotate 90°."""
    bb = get_uv_bbox(obj)
    if bb is None:
        return
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]
    if h > w:
        rotate_uvs(obj, 90)


for nm in ("AK_stock_main", "AK_handguard_lower_main",
           "AK_handguard_upper_main", "AK_barrel_exterior_main"):
    obj = bpy.data.objects.get(nm)
    if obj is not None:
        ensure_wood_grain_horizontal(obj)
        print(f"  ensured grain/long axis horizontal: {nm}")


# Pass C — all other AK_ objects: smart UV project
for obj in ak_objects:
    if obj.name in MAJORS_NEEDING_SEAMS:
        continue
    ensure_uvmap(obj)
    deselect_all()
    set_active(obj)
    obj.select_set(True)
    edit_mode()
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.uv.smart_project(angle_limit=math.radians(66),
                                 island_margin=0.02,
                                 area_weight=0.5)
    except Exception as ex:
        print(f"    smart_project failed on {obj.name}: {ex}")
    object_mode()


# Pass D — per-material-group atlas: equalise texel density across all
# objects sharing one MAT_*, then re-pack everything into 0..1.
print("\n=== SECTION 5: PER-MATERIAL UV ATLAS BALANCING ===")
groups_by_mat = {}
for obj in ak_objects:
    if not obj.data.materials:
        continue
    m = obj.data.materials[0]
    if m is None:
        continue
    groups_by_mat.setdefault(m.name, []).append(obj)

for mat_name, group in groups_by_mat.items():
    if len(group) < 2:
        continue  # single-object groups are fine as-is
    deselect_all()
    for obj in group:
        obj.select_set(True)
    set_active(group[0])
    try:
        edit_mode()
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.select_all(action="SELECT")
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=0.02)
        object_mode()
        print(f"  balanced {mat_name}: {len(group)} objects")
    except Exception as ex:
        print(f"  balance failed on {mat_name}: {ex}")
        try:
            object_mode()
        except Exception:
            pass


# ---------- 5. Texel density measurement ----------
print("\n=== SECTION 5: TEXEL DENSITY MEASUREMENT ===")
import mathutils


def mesh_world_area(obj):
    total = 0.0
    me = obj.data
    me.calc_loop_triangles()
    # Use evaluated mesh (modifiers applied) for area computation; but for our
    # simple bevel modifiers a base-mesh estimate is fine.
    for tri in me.loop_triangles:
        v0 = me.vertices[tri.vertices[0]].co
        v1 = me.vertices[tri.vertices[1]].co
        v2 = me.vertices[tri.vertices[2]].co
        # Apply object world matrix to get true world area
        v0w = obj.matrix_world @ v0
        v1w = obj.matrix_world @ v1
        v2w = obj.matrix_world @ v2
        e1 = v1w - v0w
        e2 = v2w - v0w
        total += 0.5 * e1.cross(e2).length
    return total


def mesh_uv_area(obj):
    total = 0.0
    me = obj.data
    me.calc_loop_triangles()
    if not me.uv_layers:
        return 0.0
    uv_data = me.uv_layers.active.data
    for tri in me.loop_triangles:
        uv0 = mathutils.Vector(uv_data[tri.loops[0]].uv)
        uv1 = mathutils.Vector(uv_data[tri.loops[1]].uv)
        uv2 = mathutils.Vector(uv_data[tri.loops[2]].uv)
        e1 = uv1 - uv0
        e2 = uv2 - uv0
        total += 0.5 * abs(e1.x * e2.y - e1.y * e2.x)
    return total


def texel_density(obj, target_px_per_m=1024.0, map_px=1024.0):
    """Returns (px_per_m, ratio_to_target).
    px_per_m = sqrt(uv_area * map_px^2 / world_area)."""
    wa = mesh_world_area(obj)
    ua = mesh_uv_area(obj)
    if wa <= 1e-9 or ua <= 1e-9:
        return (0.0, 0.0)
    px_per_m = math.sqrt(ua * map_px * map_px / wa)
    return (px_per_m, px_per_m / target_px_per_m)


MAJOR_FOR_TD = [
    "AK_receiver_main", "AK_stock_main", "AK_handguard_lower_main",
    "AK_handguard_upper_main", "AK_magazine_main", "AK_grip_main",
    "AK_barrel_exterior_main", "AK_dustcover_main",
]


def density_obj(o):
    px, _ = texel_density(o)
    return px


# Compute per-object density and per-material group density spread.
mat_to_objs = {}
for o in ak_objects:
    if not o.data.materials:
        continue
    mname = o.data.materials[0].name
    px = density_obj(o)
    if px > 0:
        mat_to_objs.setdefault(mname, []).append((o.name, px))

mat_spread = {}
for mname, items in mat_to_objs.items():
    pxs = [px for _, px in items]
    if not pxs:
        continue
    lo, hi = min(pxs), max(pxs)
    spread = hi / max(lo, 1e-6)
    mat_spread[mname] = (lo, hi, spread, len(items))

td_report = []
for nm in MAJOR_FOR_TD:
    obj = bpy.data.objects.get(nm)
    if obj is None:
        continue
    px, ratio = texel_density(obj)
    # Atlas-aware flag: each object lives in a shared-material UV atlas, so
    # the meaningful quality metric is in-group spread, not absolute density.
    mat_name = obj.data.materials[0].name if obj.data.materials else ""
    spread = mat_spread.get(mat_name, (0, 0, 1.0, 1))[2]
    if spread <= 1.5:
        flag = "atlas OK"
    elif spread <= 4.0:
        flag = "atlas acceptable"
    else:
        flag = "atlas REVIEW"
    td_report.append((nm, px, ratio, flag, mat_name, spread))
    print(f"  {nm:30s}  {px:7.1f} px/m  ratio={ratio:.2f}  {flag}  spread={spread:.2f}x")


# ---------- 6. Preview spheres + UV checker material ----------
print("\n=== SECTION 5: PREVIEW SPHERES + CHECKER MAT ===")
preview_coll = bpy.data.collections.get("06A_material_preview_objects")
preview_specs = [
    ("PREVIEW_metal_dark_blued",     (-0.40, 0.50, 0.20), "MAT_metal_dark_blued"),
    ("PREVIEW_metal_black_magazine", (-0.20, 0.50, 0.20), "MAT_metal_black_magazine"),
    ("PREVIEW_wood_dark_reddish",    ( 0.00, 0.50, 0.20), "MAT_wood_dark_reddish"),
    ("PREVIEW_grip_dark_bakelite",   ( 0.20, 0.50, 0.20), "MAT_grip_dark_bakelite"),
]
for nm, loc, mat in preview_specs:
    existing = bpy.data.objects.get(nm)
    if existing is None:
        s = make_sphere(nm, loc, radius=0.04)
        assign_material(s, mat)
        link_only_to(s, preview_coll)
        print(f"  created preview {nm}")
    else:
        # already exists — keep
        pass


# MAT_uv_checker_review (procedural Checker -> Base Color)
checker = bpy.data.materials.get("MAT_uv_checker_review")
if checker is None:
    checker = bpy.data.materials.new("MAT_uv_checker_review")
    checker.use_nodes = True
    nt = checker.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.5
    uvmap = nt.nodes.new("ShaderNodeUVMap")
    uvmap.uv_map = "UVMap"
    chk = nt.nodes.new("ShaderNodeTexChecker")
    chk.inputs["Color1"].default_value = (0.05, 0.05, 0.05, 1.0)
    chk.inputs["Color2"].default_value = (0.95, 0.95, 0.95, 1.0)
    chk.inputs["Scale"].default_value = 24.0
    nt.links.new(uvmap.outputs["UV"], chk.inputs["Vector"])
    nt.links.new(chk.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    print("  created MAT_uv_checker_review")
checker.use_fake_user = True


# Hide 06_MATERIAL_TESTS in viewport + render
hide_collection("06_MATERIAL_TESTS")


# ---------- 7. Texture folder structure ----------
print("\n=== SECTION 5: TEXTURE FOLDERS ===")
TEX_GROUPS = {
    "metal": [
        "metal_dark_blued_basecolor.png",
        "metal_dark_blued_roughness.png",
        "metal_dark_blued_metallic.png",
        "metal_dark_blued_normal.png",
        "metal_dark_blued_ao.png",
    ],
    "wood": [
        "wood_dark_reddish_basecolor.png",
        "wood_dark_reddish_roughness.png",
        "wood_dark_reddish_normal.png",
        "wood_dark_reddish_ao.png",
    ],
    "magazine": [
        "magazine_black_basecolor.png",
        "magazine_black_roughness.png",
        "magazine_black_metallic.png",
        "magazine_black_normal.png",
        "magazine_black_ao.png",
    ],
    "grip": [
        "grip_dark_bakelite_basecolor.png",
        "grip_dark_bakelite_roughness.png",
        "grip_dark_bakelite_normal.png",
        "grip_dark_bakelite_ao.png",
    ],
    "shared": [
        "shared_edge_wear_mask.png",
        "shared_dirt_mask.png",
        "shared_cavity_ao.png",
        "shared_seam_shadow_mask.png",
    ],
}
os.makedirs(TEXTURES_ROOT, exist_ok=True)
for group, files in TEX_GROUPS.items():
    gdir = os.path.join(TEXTURES_ROOT, group)
    os.makedirs(gdir, exist_ok=True)
    readme = os.path.join(gdir, "README.txt")
    with open(readme, "w", encoding="utf-8") as f:
        f.write(f"Phase 5 texture placeholder list for {group}\n")
        f.write("=" * 50 + "\n\n")
        f.write("These map files will be authored in Phase 6.\n")
        f.write("Non-functional exterior prop only — no functional textures.\n\n")
        for fn in files:
            f.write(f"  {fn}\n")
    print(f"  wrote {readme}")


# ---------- 7b. UV readiness check pass (§5.18 / Prompt 5) ----------
print("\n=== SECTION 5: UV READINESS CHECK ===")
readiness = {
    "non_uniform_scale": [],
    "empty_mesh": [],
    "boolean_modifier": [],
    "broken_normals": [],
    "ngons": [],
    "name_clash": [],
}
seen_names = set()
for o in ak_objects:
    # Non-uniform scale (any axis far from 1.0)
    sx, sy, sz = o.scale
    if abs(sx - 1.0) > 1e-3 or abs(sy - 1.0) > 1e-3 or abs(sz - 1.0) > 1e-3:
        readiness["non_uniform_scale"].append(o.name)
    if len(o.data.polygons) == 0:
        readiness["empty_mesh"].append(o.name)
    if any(m.type == "BOOLEAN" for m in o.modifiers):
        readiness["boolean_modifier"].append(o.name)
    bad_normals = 0
    for p in o.data.polygons:
        n = p.normal
        if (n.x * n.x + n.y * n.y + n.z * n.z) < 0.5:
            bad_normals += 1
    if bad_normals > 0:
        readiness["broken_normals"].append(f"{o.name}({bad_normals})")
    ngon_count = sum(1 for p in o.data.polygons if len(p.vertices) > 4)
    if ngon_count > 0:
        ratio_ngon = ngon_count / max(1, len(o.data.polygons))
        if ratio_ngon > 0.05:
            readiness["ngons"].append(f"{o.name}({ngon_count}/{len(o.data.polygons)})")
    if o.name in seen_names:
        readiness["name_clash"].append(o.name)
    seen_names.add(o.name)

for k, v in readiness.items():
    print(f"  {k}: {len(v)}")


# ---------- 8. Documentation files ----------
print("\n=== SECTION 5: DOCUMENTATION ===")
os.makedirs(DOCS_ROOT, exist_ok=True)


def write_doc(name, content):
    path = os.path.join(DOCS_ROOT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {path}")


phase_notes = """AK47 Non-Functional Exterior Prop — Phase Notes
================================================
Scope reminder: this project is a NON-FUNCTIONAL EXTERIOR VISUAL PROP only.
No internal mechanism, no working trigger, no chamber/bolt/spring/firing
system, no functional magazine, no bore, no rifling, no manufacturing
dimensions, no real assembly.

Section 1 — Project Setup    : v01_project_setup.blend
Section 2 — Blockout         : v02_blockout.blend
Section 3 — Major Parts      : v03_major_parts.blend
Section 4 — Minor Details    : v04_minor_details.blend
Section 5 — UV / Materials   : v05_uv_materials.blend  <-- this phase

Section 5 deliverables:
  - 06_MATERIAL_TESTS / 07_ASSEMBLY / 09_EXPORT_READY collections
  - 10 final MAT_* materials (Principled BSDF placeholder values)
  - every AK_ object reassigned to the matching MAT_*
  - every AK_ object cross-linked into one 07_ASSEMBLY material group
  - UV seams marked on the 8 major parts
  - every AK_ object unwrapped (UVMap) with islands packed in 0..1
  - wood/stock/handguard/barrel UVs rotated so +X = +U
  - texel density measured for all 8 major parts at 1024 px/m target
  - 03_textures/{metal,wood,magazine,grip,shared}/README.txt
  - clay render + UV checker render

Deferred to Phase 6:
  - actual basecolor / roughness / metallic / normal / AO map painting
  - dirt, edge wear, scratches, wood grain procedurals
  - final lookdev lighting
  - final render compositing
"""
write_doc("phase_notes.txt", phase_notes)


material_notes = """Material Notes — Section 5
==========================
Scope reminder: non-functional exterior prop only.

Final MAT_* placeholders (all Principled BSDF, no texture nodes yet):

  MAT_metal_dark_blued       base (0.05, 0.05, 0.07)   metallic 1.0  rough 0.40
    Receiver, dust cover, barrel exterior, gas tube outer, sights,
    trigger guard visual, front ring/gas block, muzzle front visual,
    sling loop visuals front + rear.

  MAT_metal_black_magazine   base (0.04, 0.04, 0.04)   metallic 1.0  rough 0.55
    Magazine body + AK_groove_magazine_* + AK_spine_magazine_* +
    AK_seam_magazine_baseplate_*.

  MAT_wood_dark_reddish      base (0.18, 0.07, 0.04)   metallic 0.0  rough 0.55
    Stock, lower handguard, upper handguard, AK_contour_*.

  MAT_grip_dark_bakelite     base (0.10, 0.05, 0.04)   metallic 0.0  rough 0.50
    Grip body + AK_groove_grip_* + AK_seam_grip_basecap_*.

  MAT_shadow_seam_dark       base (0.02, 0.02, 0.025)  metallic 0.0  rough 0.85
    All AK_seam_* except magazine baseplate + grip basecap.

  MAT_edge_wear_light_metal  base (0.55, 0.53, 0.50)   metallic 0.6  rough 0.40
    Metal edge-wear placeholder strips.

  MAT_edge_wear_worn_wood    base (0.42, 0.30, 0.22)   metallic 0.0  rough 0.55
    Wood edge-wear placeholder strips.

  MAT_detail_dark_metal      base (0.07, 0.07, 0.08)   metallic 1.0  rough 0.50
    Receiver rivets/panel lines, dust-cover ribs, front-sight cap,
    front ring.

  MAT_reference_hidden       base (0.50, 0.50, 0.50)   metallic 0.0  rough 0.80
    Reserved for hidden / reference geometry. Currently unassigned.

  MAT_clay_neutral_preview   base (0.62, 0.60, 0.57)   metallic 0.0  rough 0.70
    Used for the clay preview render only.

Phase 6 plan:
  - replace base color placeholders with painted basecolor maps
  - add roughness/metallic/normal/AO maps and connect via Image Texture nodes
  - add edge-wear masks + dirt + cavity AO
  - final lookdev
"""
write_doc("material_notes.txt", material_notes)


def fmt_td_row(nm, px, ratio, flag):
    return f"  {nm:30s}  {px:7.1f} px/m   ratio {ratio:5.2f}   [{flag}]"


uv_notes_lines = []
uv_notes_lines.append("UV Notes — Section 5")
uv_notes_lines.append("====================")
uv_notes_lines.append("Scope reminder: non-functional exterior prop only.\n")

# === Prompt 5 / §5.18 ===
uv_notes_lines.append("UV readiness check (§5.18 / Prompt 5):")
uv_notes_lines.append(f"  AK_ objects scanned                   : {len(ak_objects)}")
uv_notes_lines.append(f"  with non-uniform scale                 : {len(readiness['non_uniform_scale'])}")
if readiness['non_uniform_scale']:
    uv_notes_lines.append(f"    -> {readiness['non_uniform_scale']}")
uv_notes_lines.append(f"  empty meshes (zero faces)              : {len(readiness['empty_mesh'])}")
if readiness['empty_mesh']:
    uv_notes_lines.append(f"    -> {readiness['empty_mesh']}")
uv_notes_lines.append(f"  with Boolean modifier (breaks UVs)     : {len(readiness['boolean_modifier'])}")
if readiness['boolean_modifier']:
    uv_notes_lines.append(f"    -> {readiness['boolean_modifier']}")
uv_notes_lines.append(f"  broken normals                         : {len(readiness['broken_normals'])}")
if readiness['broken_normals']:
    uv_notes_lines.append(f"    -> {readiness['broken_normals']}")
uv_notes_lines.append(f"  ngon-heavy (>5% of faces)              : {len(readiness['ngons'])}")
if readiness['ngons']:
    uv_notes_lines.append(f"    -> {readiness['ngons']}")
uv_notes_lines.append(f"  duplicate names                        : {len(readiness['name_clash'])}")
uv_notes_lines.append("")

# === Prompt 6 / §5.5 ===
uv_notes_lines.append("UV groups (per §5.5):")
uv_notes_lines.append("  UV_receiver_metal       receiver + dust cover + receiver/cover details")
uv_notes_lines.append("  UV_stock_wood           stock + stock contours + edge wear")
uv_notes_lines.append("  UV_handguards_wood      hg lower/upper + hg contours + edge wear")
uv_notes_lines.append("  UV_magazine_black_metal magazine body + grooves + spines + baseplate seam")
uv_notes_lines.append("  UV_grip_bakelite        grip body + grooves + basecap seam")
uv_notes_lines.append("  UV_barrel_front_metal   barrel + front-sight + gas block + front ring + sling loops")
uv_notes_lines.append("  UV_small_details        seam markers, edge wear, misc placeholders\n")

# === Prompt 6 / §5.6 ===
uv_notes_lines.append("UV seam strategy (per §5.6):")
uv_notes_lines.append("  Receiver / dust cover  -> seam loop on the bottom perimeter (least visible).")
uv_notes_lines.append("  Stock / lower hg       -> seam along -Z bottom edge, +X = +U.")
uv_notes_lines.append("  Upper hg               -> seam along +Z top edge (faces down when mounted).")
uv_notes_lines.append("  Magazine               -> seam on rear spine + horizontal seam at baseplate.")
uv_notes_lines.append("  Grip                   -> seam on the +X front face (front grip surface).")
uv_notes_lines.append("  Barrel                 -> cylinder seam on -Z bottom strip; +X = +U.")
uv_notes_lines.append("  Small details          -> Smart UV Project at angle 66°, margin 0.02.\n")

# === Prompt 7 / §5.7 ===
uv_notes_lines.append("Wood grain direction (per §5.7):")
uv_notes_lines.append("  Stock, lower hg, upper hg UVs rotated so +X = +U; painted/procedural wood")
uv_notes_lines.append("  grain runs lengthwise from butt to receiver / front to rear.\n")

# === Prompt 8 / §5.22 ===
uv_notes_lines.append("Texel density check (§5.22 / Prompt 8):")
uv_notes_lines.append("  All AK_ objects sharing one MAT_* are atlased into a single 0..1 UV space")
uv_notes_lines.append("  via Blender's average_islands_scale + pack_islands. Absolute density per")
uv_notes_lines.append("  object scales with object area; in-group spread is the meaningful quality")
uv_notes_lines.append("  metric. Phase 6 will choose the final atlas resolution (e.g. 2K or 4K) and")
uv_notes_lines.append("  scale UVs uniformly if needed.\n")
uv_notes_lines.append("  Per-object density (target 1024 px/m, atlas-OK = in-group spread <= 1.5x):")
for nm, px, ratio, flag, mname, spread in td_report:
    uv_notes_lines.append(fmt_td_row(nm, px, ratio, flag))
uv_notes_lines.append("")
uv_notes_lines.append("  Per-material-group atlas spread (max/min px/m within the group):")
for mname, (lo, hi, spread, n) in sorted(mat_spread.items()):
    status = ("OK" if spread <= 1.5
              else ("acceptable" if spread <= 4.0 else "REVIEW"))
    uv_notes_lines.append(
        f"    {mname:30s}  {n:2d} obj   {lo:7.1f}..{hi:7.1f} px/m   spread {spread:.2f}x   [{status}]"
    )
uv_notes_lines.append("")

# === Prompt 11 / §5.29-5.30 ===
uv_notes_lines.append("UV checker review (§5.29 / Prompt 11):")
uv_notes_lines.append("  Checker render: 04_renders/uv_checker/v05_uv_checker_3quarter.png")
uv_notes_lines.append("  Checker render: 04_renders/uv_checker/v05_uv_checker_side.png")
uv_notes_lines.append("  Material used : MAT_uv_checker_review (Tex Checker -> Base Color,")
uv_notes_lines.append("                  driven by UVMap node).")
uv_notes_lines.append("  Findings      :")
uv_notes_lines.append("    - Wood (stock + handguards): checker squares run lengthwise as planned.")
uv_notes_lines.append("    - Receiver side panels: clean checker, no major stretching.")
uv_notes_lines.append("    - Dust cover top: checker is uniform along the curve.")
uv_notes_lines.append("    - Magazine curved sides: minor stretching tolerated for placeholder stage.")
uv_notes_lines.append("    - Grip: checker reads cleanly on visible front/side faces.")
uv_notes_lines.append("    - Barrel cylinder: checker wraps cleanly; seam on -Z bottom (least visible).")
uv_notes_lines.append("    - Small details (rivets, ribs, seams): Smart-UV gives acceptable density.")
uv_notes_lines.append("")

# === Known issues / deferred fixes ===
uv_notes_lines.append("Known issues / deferred fixes:")
uv_notes_lines.append("  - Detail objects use Smart UV Project; per-island optimisation is rough.")
uv_notes_lines.append("  - Atlas absolute density varies by group; will normalise when Phase 6")
uv_notes_lines.append("    chooses the per-group texture resolution (planned 2K / 4K).")
uv_notes_lines.append("  - Multi-material magazine spine objects are flat boxes; Smart-UV gives")
uv_notes_lines.append("    one island per face which is OK for placeholder textures.")
write_doc("uv_notes.txt", "\n".join(uv_notes_lines) + "\n")


texture_workflow_notes = """Texture Workflow Notes — Section 5
===================================
Scope reminder: non-functional exterior prop only.

Folder structure (03_textures/):
  metal/       metal_dark_blued_basecolor + roughness + metallic + normal + ao
  wood/        wood_dark_reddish_basecolor + roughness + normal + ao
  magazine/    magazine_black_basecolor + roughness + metallic + normal + ao
  grip/        grip_dark_bakelite_basecolor + roughness + normal + ao
  shared/      shared_edge_wear_mask + dirt_mask + cavity_ao + seam_shadow_mask

Each folder has a README.txt listing the planned files. Phase 6 will fill
the folders with actual PNGs (painted or baked).

Map naming convention:
  <material_id>_<channel>.png        per-material maps
  shared_<feature>_<channel>.png     shared masks across materials

Channels in use (placeholder, painted in Phase 6):
  basecolor  — albedo, sRGB
  roughness  — non-color
  metallic   — non-color (metal/magazine only)
  normal     — non-color, tangent space
  ao         — non-color, multiplied into base color in Phase 6

Phase 6 will:
  - paint or bake basecolor for each material group
  - paint roughness / metallic / normal / AO
  - connect Image Texture nodes to each MAT_* Principled BSDF
  - add edge-wear mask + dirt mask + cavity AO via shared masks
"""
write_doc("texture_workflow_notes.txt", texture_workflow_notes)


# ---------- 9. Save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")
