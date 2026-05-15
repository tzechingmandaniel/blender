"""Section 5 auto-executor: cleans meshes, unwraps UVs, builds final materials,
and reassigns every AK_ object away from MAT_placeholder_* to its final
material. Saves v05_uv_materials.blend.

Auto-detects the project root from __file__ — no hardcoded path.

All exterior-only. No internal mechanism, no functional geometry.
"""
import bpy
import math
import os


# ---------- 0. paths ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v04_minor_details.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v05_uv_materials.blend")

print(f"\n=== SECTION 5 — UV + MATERIALS ===")
print(f"  source : {SRC_BLEND}")
print(f"  target : {OUT_BLEND}")
bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)


# ---------- helpers ----------
def set_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def safe_input(node, name, value):
    """Set a Principled BSDF input by name if it exists (input names vary
    across Blender versions — Specular vs Specular IOR Level etc)."""
    if name in node.inputs:
        node.inputs[name].default_value = value
        return True
    return False


# ---------- 1. mesh cleanup (§5.3) ----------
print("\n-- mesh cleanup --")

def cleanup_mesh(obj):
    set_active(obj)
    # Apply scale only
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Edit mode: select all, recalc normals, merge by distance
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.remove_doubles(threshold=1e-5)
    bpy.ops.object.mode_set(mode="OBJECT")


cleaned = 0
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if not (o.name.startswith("AK_") or o.name.startswith("BLK_")):
        continue
    # Some BLK_ are hidden in viewport — that's fine for ops, just unhide briefly
    was_hidden = o.hide_viewport
    if was_hidden:
        o.hide_viewport = False
    try:
        cleanup_mesh(o)
        cleaned += 1
    except Exception as e:
        print(f"  cleanup failed on {o.name}: {e}")
    if was_hidden:
        o.hide_viewport = True

print(f"  cleaned {cleaned} meshes (scale applied, normals recalced, doubles merged)")


# ---------- 2. UV unwrap (§5.5) ----------
print("\n-- UV unwrap (smart_project per AK_ object) --")

# Categorise AK_ objects for unwrap parameters
CYLINDRICAL = {
    "AK_barrel_outer_closed", "AK_gas_tube_outer", "AK_gas_block_visual",
    "AK_front_ring_visual", "AK_handguard_upper_front_collar_visual",
    "AK_handguard_upper_rear_collar_visual",
    "AK_ring_barrel_visual_001", "AK_ring_barrel_visual_002",
    "AK_line_cleaningrod_visual_001",
    "AK_loop_sling_rear_visual", "AK_loop_sling_front_visual",
    "AK_seam_barrel_front_001",
}

SMALL_DETAIL_PREFIXES = (
    "AK_rivet_", "AK_rib_", "AK_seam_", "AK_groove_", "AK_ridge_",
    "AK_wear_", "AK_panel_", "AK_lever_", "AK_loop_", "AK_plate_",
    "AK_wood_contour_", "AK_detail_", "AK_notch_", "AK_line_",
    "AK_ring_",
)


def smart_unwrap(obj, angle_deg, island_margin):
    set_active(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(angle_deg),
        island_margin=island_margin,
        correct_aspect=True,
        scale_to_bounds=False,
    )
    bpy.ops.object.mode_set(mode="OBJECT")


unwrapped = 0
for o in list(bpy.data.objects):
    if o.type != "MESH" or not o.name.startswith("AK_"):
        continue
    was_hidden = o.hide_viewport
    if was_hidden:
        o.hide_viewport = False
    try:
        if o.name in CYLINDRICAL:
            smart_unwrap(o, angle_deg=89.0, island_margin=0.015)
        elif any(o.name.startswith(p) for p in SMALL_DETAIL_PREFIXES):
            smart_unwrap(o, angle_deg=66.0, island_margin=0.010)
        else:
            smart_unwrap(o, angle_deg=66.0, island_margin=0.020)
        unwrapped += 1
    except Exception as e:
        print(f"  unwrap failed on {o.name}: {e}")
    if was_hidden:
        o.hide_viewport = True

print(f"  unwrapped {unwrapped} AK_ meshes")


# ---------- 3. build final material groups (§5.7, §5.16) ----------
print("\n-- create final materials --")


def _new_material(name):
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat


def _common_setup(mat):
    """Return (nodes, links, bsdf, out, tc, noise, ramp, bump). All connected
    except bsdf <-> out and ramp/bump <-> bsdf, which the caller wires."""
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    for n in list(nodes):
        nodes.remove(n)

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tc = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    noise = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")  # ColorRamp
    bump = nodes.new("ShaderNodeBump")

    out.location = (700, 0)
    bsdf.location = (450, 0)
    bump.location = (200, -200)
    ramp.location = (200, 100)
    noise.location = (0, 0)
    mapping.location = (-200, 0)
    tc.location = (-400, 0)

    links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    return nodes, links, bsdf, out, tc, mapping, noise, ramp, bump


def make_metal_dark_blued():
    mat = _new_material("MAT_metal_dark_blued")
    _, _, bsdf, _, _, _, noise, ramp, bump = _common_setup(mat)
    bsdf.inputs["Base Color"].default_value = (0.06, 0.06, 0.07, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.9
    noise.inputs["Scale"].default_value = 60.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Distortion"].default_value = 0.3
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1.0)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (0.65, 0.65, 0.65, 1.0)
    bump.inputs["Strength"].default_value = 0.05
    return mat


def make_metal_black_magazine():
    mat = _new_material("MAT_metal_black_magazine")
    _, _, bsdf, _, _, _, noise, ramp, bump = _common_setup(mat)
    bsdf.inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.85
    noise.inputs["Scale"].default_value = 50.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Distortion"].default_value = 0.4
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (0.5, 0.5, 0.5, 1.0)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.8, 0.8, 0.8, 1.0)
    bump.inputs["Strength"].default_value = 0.04
    return mat


def make_wood_dark_reddish():
    mat = _new_material("MAT_wood_dark_reddish")
    _, _, bsdf, _, _, mapping, noise, ramp, bump = _common_setup(mat)
    # Wood grain runs along X. Stretch noise along X for grain feel.
    mapping.inputs["Scale"].default_value = (1.0, 12.0, 12.0)
    bsdf.inputs["Base Color"].default_value = (0.18, 0.08, 0.05, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    noise.inputs["Scale"].default_value = 8.0
    noise.inputs["Detail"].default_value = 12.0
    noise.inputs["Distortion"].default_value = 0.5
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.45, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.70, 0.70, 0.70, 1.0)
    bump.inputs["Strength"].default_value = 0.10
    return mat


def make_grip_dark_bakelite():
    mat = _new_material("MAT_grip_dark_bakelite")
    _, _, bsdf, _, _, _, noise, ramp, bump = _common_setup(mat)
    bsdf.inputs["Base Color"].default_value = (0.10, 0.04, 0.03, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    noise.inputs["Scale"].default_value = 80.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Distortion"].default_value = 0.2
    ramp.color_ramp.elements[0].position = 0.45
    ramp.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1.0)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.75, 0.75, 0.75, 1.0)
    bump.inputs["Strength"].default_value = 0.05
    return mat


def make_edge_wear_light_metal():
    mat = _new_material("MAT_edge_wear_light_metal")
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.45, 0.45, 0.45, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.95
    bsdf.inputs["Roughness"].default_value = 0.3
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_shadow_seam_dark():
    mat = _new_material("MAT_shadow_seam_dark")
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.85
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_rubber_dark_optional():
    mat = _new_material("MAT_rubber_dark_optional")
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.04, 0.04, 0.04, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.8
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


mats = {
    "MAT_metal_dark_blued":      make_metal_dark_blued(),
    "MAT_metal_black_magazine":  make_metal_black_magazine(),
    "MAT_wood_dark_reddish":     make_wood_dark_reddish(),
    "MAT_grip_dark_bakelite":    make_grip_dark_bakelite(),
    "MAT_edge_wear_light_metal": make_edge_wear_light_metal(),
    "MAT_shadow_seam_dark":      make_shadow_seam_dark(),
    "MAT_rubber_dark_optional":  make_rubber_dark_optional(),
}
# Force fake-user so unassigned materials survive Blender's orphan cleanup on save.
# MAT_edge_wear_light_metal and MAT_rubber_dark_optional aren't assigned to any
# object in this section but are part of the §5.7 material palette.
for name, mat in mats.items():
    mat.use_fake_user = True
    print(f"  created {name}")


# ---------- 4. material reassignment (§5.7.2) ----------
print("\n-- reassign materials (placeholder -> final) --")

PLACEHOLDER_TO_FINAL = {
    "MAT_placeholder_dark_metal":    "MAT_metal_dark_blued",
    "MAT_placeholder_black_metal":   "MAT_metal_black_magazine",
    "MAT_placeholder_dark_wood":     "MAT_wood_dark_reddish",
    "MAT_placeholder_bakelite_grip": "MAT_grip_dark_bakelite",
}

reassigned = 0
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if not o.name.startswith("AK_"):
        continue
    # Seam objects use the dedicated seam material
    if o.name.startswith("AK_seam_"):
        final_name = "MAT_shadow_seam_dark"
    else:
        # Look at current material slot
        if not o.data.materials or o.data.materials[0] is None:
            continue
        current = o.data.materials[0].name
        final_name = PLACEHOLDER_TO_FINAL.get(current)
        if final_name is None:
            # Already a final material (e.g. re-runs) — leave it
            continue
    final = bpy.data.materials.get(final_name)
    if final is None:
        continue
    o.data.materials.clear()
    o.data.materials.append(final)
    reassigned += 1

print(f"  reassigned {reassigned} AK_ objects to final materials")


# ---------- 5. save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")

# Summary
ak_total = sum(1 for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_"))
uvs_ok = sum(1 for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("AK_") and o.data.uv_layers)
print(f"  AK_ meshes: {ak_total};  with uv_layer: {uvs_ok}")
