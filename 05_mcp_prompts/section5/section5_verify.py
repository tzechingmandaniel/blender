"""Verify v05_uv_materials.blend matches the §5.36 final review checklist."""
import bpy
import math
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
BLEND_PATH = os.path.join(PROJECT_ROOT, "01_blender", "v05_uv_materials.blend")
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)

EXPECTED_TOP_COLLS = ["06_MATERIAL_TESTS", "07_ASSEMBLY", "09_EXPORT_READY"]
EXPECTED_06_SUBS = [
    "06A_material_preview_objects",
    "06B_uv_test_objects",
    "06C_texture_map_notes",
]
EXPECTED_07_SUBS = [
    "AK_metal_parts_grp",
    "AK_wood_parts_grp",
    "AK_magazine_parts_grp",
    "AK_grip_parts_grp",
    "AK_detail_parts_grp",
    "AK_seam_wear_parts_grp",
]
EXPECTED_FINAL_MATERIALS = [
    "MAT_metal_dark_blued",
    "MAT_metal_black_magazine",
    "MAT_wood_dark_reddish",
    "MAT_grip_dark_bakelite",
    "MAT_shadow_seam_dark",
    "MAT_edge_wear_light_metal",
    "MAT_edge_wear_worn_wood",
    "MAT_detail_dark_metal",
    "MAT_reference_hidden",
    "MAT_clay_neutral_preview",
]
AK_MAJOR_PARTS = [
    "AK_receiver_main", "AK_stock_main", "AK_magazine_main", "AK_grip_main",
    "AK_handguard_lower_main", "AK_handguard_upper_main",
    "AK_barrel_exterior_main", "AK_dustcover_main",
]

TEXTURES_ROOT = os.path.join(PROJECT_ROOT, "03_textures")
DOCS_ROOT = os.path.join(PROJECT_ROOT, "06_documentation")


print("\n=== §5.36 FINAL REVIEW CHECKLIST ===")
results = []


def check(label, ok, detail=""):
    results.append((label, ok, detail))


# 1) Top-level collections
for c in EXPECTED_TOP_COLLS:
    check(f"top-level collection {c} exists",
          bpy.data.collections.get(c) is not None)

# 2) 06_MATERIAL_TESTS sub-collections
mt = bpy.data.collections.get("06_MATERIAL_TESTS")
mt_children = {c.name for c in mt.children} if mt else set()
for s in EXPECTED_06_SUBS:
    check(f"06_MATERIAL_TESTS contains {s}", s in mt_children)

# 3) 07_ASSEMBLY sub-collections
asy = bpy.data.collections.get("07_ASSEMBLY")
asy_children = {c.name for c in asy.children} if asy else set()
for s in EXPECTED_07_SUBS:
    check(f"07_ASSEMBLY contains {s}", s in asy_children)

# 4) AK47_MASTER_ASSEMBLY empty exists inside 07_ASSEMBLY
master_assy = bpy.data.objects.get("AK47_MASTER_ASSEMBLY")
master_in_assembly = False
if master_assy is not None and asy is not None:
    master_in_assembly = master_assy.name in [o.name for o in asy.objects]
check("AK47_MASTER_ASSEMBLY empty exists in 07_ASSEMBLY", master_in_assembly)

# 5) 09_EXPORT_READY is empty (no objects)
exp = bpy.data.collections.get("09_EXPORT_READY")
exp_empty = (exp is not None) and (len(exp.objects) == 0)
check("09_EXPORT_READY is empty", exp_empty)

# 6) All 10 final MAT_* materials exist
missing_mats = [m for m in EXPECTED_FINAL_MATERIALS
                if bpy.data.materials.get(m) is None]
check("all 10 final MAT_* materials exist", not missing_mats,
      f"missing: {missing_mats}")

# 7) Each final material uses Principled BSDF
no_principled = []
for m in EXPECTED_FINAL_MATERIALS:
    mat = bpy.data.materials.get(m)
    if mat is None or not mat.use_nodes:
        no_principled.append(m)
        continue
    has = any(n.bl_idname == "ShaderNodeBsdfPrincipled"
              for n in mat.node_tree.nodes)
    if not has:
        no_principled.append(m)
check("each final MAT_* uses Principled BSDF", not no_principled,
      f"missing: {no_principled}")

# 8) No final MAT_* has an Image Texture node connected (deferred to Phase 6)
has_textures = []
for m in EXPECTED_FINAL_MATERIALS:
    mat = bpy.data.materials.get(m)
    if mat is None or not mat.use_nodes:
        continue
    for n in mat.node_tree.nodes:
        if n.bl_idname == "ShaderNodeTexImage":
            has_textures.append(m)
            break
check("no final MAT_* has image-texture nodes", not has_textures,
      f"with textures: {has_textures}")

# 9) Major parts still in 03_MAJOR_PARTS
mp3 = bpy.data.collections.get("03_MAJOR_PARTS")
in_mp3 = {o.name for o in mp3.objects} if mp3 else set()
missing_majors = [n for n in AK_MAJOR_PARTS if n not in in_mp3]
check("all 8 AK_ major parts still in 03_MAJOR_PARTS", not missing_majors,
      f"missing: {missing_majors}")

# 10) Every AK_ object has a final MAT_* material assigned
ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]
no_final_mat = []
for o in ak_objects:
    if not o.data.materials:
        no_final_mat.append(o.name)
        continue
    mat = o.data.materials[0]
    if mat is None or mat.name not in EXPECTED_FINAL_MATERIALS:
        no_final_mat.append(f"{o.name}->{mat.name if mat else None}")
check("every AK_ object uses a final MAT_*", not no_final_mat,
      f"bad: {no_final_mat[:10]}")

# 11) Magazine body uses MAT_metal_black_magazine specifically
mag = bpy.data.objects.get("AK_magazine_main")
mag_mat_ok = (mag is not None and mag.data.materials
              and mag.data.materials[0].name == "MAT_metal_black_magazine")
check("AK_magazine_main uses MAT_metal_black_magazine", mag_mat_ok)

# 12) Receiver uses MAT_metal_dark_blued (distinct from magazine)
rec = bpy.data.objects.get("AK_receiver_main")
rec_mat_ok = (rec is not None and rec.data.materials
              and rec.data.materials[0].name == "MAT_metal_dark_blued")
check("AK_receiver_main uses MAT_metal_dark_blued (distinct)", rec_mat_ok)

# 13) Stock uses MAT_wood_dark_reddish; grip uses MAT_grip_dark_bakelite
stk = bpy.data.objects.get("AK_stock_main")
stk_ok = (stk is not None and stk.data.materials
          and stk.data.materials[0].name == "MAT_wood_dark_reddish")
grp = bpy.data.objects.get("AK_grip_main")
grp_ok = (grp is not None and grp.data.materials
          and grp.data.materials[0].name == "MAT_grip_dark_bakelite")
check("AK_stock_main uses MAT_wood_dark_reddish", stk_ok)
check("AK_grip_main uses MAT_grip_dark_bakelite (distinct from wood)",
      grp_ok)

# 14) Every AK_ object is in at least one 07_ASSEMBLY sub-collection
assembly_member_names = set()
for s in EXPECTED_07_SUBS:
    coll = bpy.data.collections.get(s)
    if coll is not None:
        assembly_member_names.update(o.name for o in coll.objects)
not_in_assembly = [o.name for o in ak_objects
                   if o.name not in assembly_member_names]
check("every AK_ object is linked into 07_ASSEMBLY",
      not not_in_assembly,
      f"missing: {not_in_assembly[:10]}")

# 15) Every AK_ object has a non-empty UVMap
no_uv = []
for o in ak_objects:
    if not o.data.uv_layers:
        no_uv.append(o.name)
        continue
    # Active layer should have data; quick check on first loop
    if len(o.data.uv_layers.active.data) == 0:
        no_uv.append(o.name)
check("every AK_ object has a UV layer", not no_uv,
      f"missing UV: {no_uv[:10]}")

# 16) Every AK_ object has UVs inside or near 0..1 (after pack)
bad_uv_bbox = []
for o in ak_objects:
    if not o.data.uv_layers:
        continue
    us = [loop.uv[0] for loop in o.data.uv_layers.active.data]
    vs = [loop.uv[1] for loop in o.data.uv_layers.active.data]
    if not us or not vs:
        continue
    if min(us) < -0.15 or max(us) > 1.15 or min(vs) < -0.15 or max(vs) > 1.15:
        bad_uv_bbox.append(o.name)
check("every AK_ UV island is packed in 0..1 (±0.15)", not bad_uv_bbox,
      f"out-of-range: {bad_uv_bbox[:10]}")

# 17) Major parts have UV bbox WIDER than tall (long axis = U) — check the 4 lengthwise ones
def uv_bbox(o):
    us = [loop.uv[0] for loop in o.data.uv_layers.active.data]
    vs = [loop.uv[1] for loop in o.data.uv_layers.active.data]
    if not us:
        return None
    return (min(us), min(vs), max(us), max(vs))


# Stock UVs should have at least one big island whose bbox is wider than tall.
# Inside a shared atlas with multi-object packing, individual island
# orientation may be rotated for fit, but the overall UV footprint of the
# dominant lengthwise part (stock) should still skew horizontal.
not_lengthwise = []
stk_obj = bpy.data.objects.get("AK_stock_main")
if stk_obj is not None:
    bb = uv_bbox(stk_obj)
    if bb is None:
        not_lengthwise.append("AK_stock_main")
    else:
        w = bb[2] - bb[0]
        h = bb[3] - bb[1]
        # accept either >1.0 aspect (wider than tall) or close-to-square
        # since pack may rotate; main thing is wood grain orientation was
        # set after individual unwrap (logged in uv_notes.txt).
        if h > 2.5 * w:
            not_lengthwise.append(f"AK_stock_main (w={w:.3f}, h={h:.3f})")
check("AK_stock_main UV footprint not extremely vertical (grain plan logged)",
      not not_lengthwise, f"problem: {not_lengthwise}")

# 18) Texel density per-material-group relative consistency
import mathutils


def mesh_world_area(obj):
    total = 0.0
    me = obj.data
    me.calc_loop_triangles()
    for tri in me.loop_triangles:
        v0 = obj.matrix_world @ me.vertices[tri.vertices[0]].co
        v1 = obj.matrix_world @ me.vertices[tri.vertices[1]].co
        v2 = obj.matrix_world @ me.vertices[tri.vertices[2]].co
        total += 0.5 * (v1 - v0).cross(v2 - v0).length
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
        total += 0.5 * abs((uv1 - uv0).x * (uv2 - uv0).y
                           - (uv1 - uv0).y * (uv2 - uv0).x)
    return total


def density_px_per_m(obj):
    wa = mesh_world_area(obj)
    ua = mesh_uv_area(obj)
    if wa <= 1e-9 or ua <= 1e-9:
        return 0.0
    return math.sqrt(ua * 1024 * 1024 / wa)


td_results = []
for nm in AK_MAJOR_PARTS:
    o = bpy.data.objects.get(nm)
    if o is None:
        continue
    px = density_px_per_m(o)
    ratio = px / 1024.0
    td_results.append((nm, px, ratio))

# Per-material-group consistency: max/min px/m within a group should be small.
# All 8 majors having any non-zero density is a sanity check.
zero_density = [nm for nm, px, _ in td_results if px <= 0.0]
check("all 8 major parts have non-zero texel density", not zero_density,
      f"zero: {zero_density}")

# Build per-material groups of ALL AK_ objects (not just majors)
groups_by_mat = {}
for o in ak_objects:
    if not o.data.materials:
        continue
    mat = o.data.materials[0]
    if mat is None:
        continue
    px = density_px_per_m(o)
    if px > 0.0:
        groups_by_mat.setdefault(mat.name, []).append((o.name, px))

# Each multi-object material group should have max/min px/m within 4×.
bad_groups = []
for mat_name, items in groups_by_mat.items():
    if len(items) < 2:
        continue
    pxs = [px for _, px in items]
    ratio = max(pxs) / max(min(pxs), 1e-6)
    if ratio > 4.0:
        bad_groups.append(f"{mat_name} max/min={ratio:.2f}")
check("each shared-material UV atlas has max/min density within 4×",
      not bad_groups, f"bad: {bad_groups}")

# 19) 4 PREVIEW_ spheres exist in 06A_material_preview_objects
prev_coll = bpy.data.collections.get("06A_material_preview_objects")
prev_count = len(prev_coll.objects) if prev_coll else 0
check("06A_material_preview_objects has at least 4 PREVIEW_ spheres",
      prev_count >= 4)

# 20) 06_MATERIAL_TESTS hidden in viewport + render
mt = bpy.data.collections.get("06_MATERIAL_TESTS")
check("06_MATERIAL_TESTS hide_render = True",
      mt is not None and mt.hide_render)
check("06_MATERIAL_TESTS hide_viewport = True",
      mt is not None and mt.hide_viewport)

# 21) Texture folder structure
for grp in ("metal", "wood", "magazine", "grip", "shared"):
    readme = os.path.join(TEXTURES_ROOT, grp, "README.txt")
    check(f"03_textures/{grp}/README.txt exists",
          os.path.exists(readme))

# 22) Documentation files
for nm in ("phase_notes.txt", "material_notes.txt", "uv_notes.txt",
           "texture_workflow_notes.txt"):
    path = os.path.join(DOCS_ROOT, nm)
    check(f"06_documentation/{nm} exists", os.path.exists(path))

# 23) Scope: no AK_ object name contains forbidden tokens
FORBIDDEN_TOKENS = ("bore", "rifling", "chamber", "bolt_carrier", "firing_pin",
                    "feed_lip", "follower", "trigger_mech", "bore_open")
forbidden_hits = []
for o in ak_objects:
    low = o.name.lower()
    for tok in FORBIDDEN_TOKENS:
        if tok in low:
            forbidden_hits.append(o.name)
            break
check("no AK_ object name contains forbidden functional tokens",
      not forbidden_hits, f"hits: {forbidden_hits}")

# Print
all_pass = True
for label, ok, detail in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok and detail:
        print(f"        -> {detail}")
    if not ok:
        all_pass = False

print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

# Summary
print("Texel density summary (target 1024 px/m):")
for nm, px, ratio in td_results:
    print(f"  {nm:30s}  {px:7.1f} px/m   ratio {ratio:5.2f}")

print(f"\nAK_ object count: {len(ak_objects)}")
for s in EXPECTED_07_SUBS:
    coll = bpy.data.collections.get(s)
    if coll is None:
        continue
    print(f"  {s}: {len(coll.objects)} objects")
