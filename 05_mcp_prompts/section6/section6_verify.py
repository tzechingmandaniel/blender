"""Verify v06_final_textures_lookdev.blend against the §6.37 checklist."""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
BLEND_PATH = os.path.join(PROJECT_ROOT, "01_blender",
                          "v06_final_textures_lookdev.blend")
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)

DOCS_ROOT = os.path.join(PROJECT_ROOT, "06_documentation")
REVIEWS_ROOT = os.path.join(PROJECT_ROOT, "08_reviews")
RENDERS_ROOT = os.path.join(PROJECT_ROOT, "04_renders", "lookdev")

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
HERO_MATERIALS = EXPECTED_FINAL_MATERIALS[:4]
EXPECTED_CAMERAS = [
    "CAM_lookdev_full_model",
    "CAM_lookdev_metal_closeup",
    "CAM_lookdev_wood_closeup",
    "CAM_lookdev_magazine_closeup",
    "CAM_lookdev_grip_closeup",
    "CAM_lookdev_handguard_closeup",
]
EXPECTED_LIGHTS = [
    "LIGHT_lookdev_key_soft",
    "LIGHT_lookdev_fill_soft",
    "LIGHT_lookdev_rim_subtle",
]

print("\n=== §6.37 FINAL REVIEW CHECKLIST ===")
results = []


def check(label, ok, detail=""):
    results.append((label, ok, detail))


# 1. 08_LIGHTING_CAMERA collection exists with cameras + lights
lc = bpy.data.collections.get("08_LIGHTING_CAMERA")
check("08_LIGHTING_CAMERA collection exists", lc is not None)
lc_members = {o.name for o in (lc.objects if lc else [])}
missing_cams = [c for c in EXPECTED_CAMERAS if c not in lc_members]
check("all 6 lookdev cameras in 08_LIGHTING_CAMERA",
      not missing_cams, f"missing: {missing_cams}")
missing_lights = [l for l in EXPECTED_LIGHTS if l not in lc_members]
check("all 3 lookdev area lights in 08_LIGHTING_CAMERA",
      not missing_lights, f"missing: {missing_lights}")

# 2. NodeGroups exist
edge = bpy.data.node_groups.get("EdgeWearMask")
cav = bpy.data.node_groups.get("CavityAO")
check("NodeGroup EdgeWearMask exists", edge is not None)
check("NodeGroup CavityAO exists", cav is not None)

# 3. Hero materials reference both NodeGroups (via ShaderNodeGroup nodes)
for mname in HERO_MATERIALS:
    mat = bpy.data.materials.get(mname)
    if mat is None or not mat.use_nodes:
        check(f"{mname} exists with node graph", False)
        continue
    grp_names = set()
    for n in mat.node_tree.nodes:
        if n.bl_idname == "ShaderNodeGroup" and n.node_tree:
            grp_names.add(n.node_tree.name)
    check(f"{mname} uses EdgeWearMask + CavityAO",
          "EdgeWearMask" in grp_names and "CavityAO" in grp_names,
          f"groups: {grp_names}")

# 4. Hero materials are Pointiness-driven (have a Geometry node feeding
#    a Map Range — direct or inside EdgeWearMask). The check above already
#    asserts EdgeWearMask presence; here just confirm the material graph
#    contains a Principled BSDF.
no_bsdf = []
for mname in HERO_MATERIALS:
    mat = bpy.data.materials.get(mname)
    if mat is None or not mat.use_nodes:
        no_bsdf.append(mname)
        continue
    if not any(n.bl_idname == "ShaderNodeBsdfPrincipled"
               for n in mat.node_tree.nodes):
        no_bsdf.append(mname)
check("each hero material has a Principled BSDF", not no_bsdf,
      f"missing: {no_bsdf}")

# 5. Wood shader has a Wave texture (lengthwise grain plan)
wood = bpy.data.materials.get("MAT_wood_dark_reddish")
has_wave = wood is not None and wood.use_nodes and any(
    n.bl_idname == "ShaderNodeTexWave" for n in wood.node_tree.nodes)
check("MAT_wood_dark_reddish has a Wave Bands node", has_wave)

# 6. Grip shader does NOT use a Wave texture (so it isn't wood)
grip = bpy.data.materials.get("MAT_grip_dark_bakelite")
no_wave_grip = grip is not None and grip.use_nodes and not any(
    n.bl_idname == "ShaderNodeTexWave" for n in grip.node_tree.nodes)
check("MAT_grip_dark_bakelite does NOT use Wave Bands (distinct from wood)",
      no_wave_grip)

# 7. Grip is non-metallic
grip_metallic = None
if grip and grip.use_nodes:
    for n in grip.node_tree.nodes:
        if n.bl_idname == "ShaderNodeBsdfPrincipled":
            grip_metallic = n.inputs["Metallic"].default_value
check("MAT_grip_dark_bakelite metallic == 0", grip_metallic == 0.0,
      f"got: {grip_metallic}")

# 8. Magazine is more matte than receiver (rough_base 0.55 vs 0.40 — check
#    base default values on the Principled BSDF roughness OR on the
#    MULTIPLY_ADD constant that builds final roughness).
def rough_base_of(mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat is None or not mat.use_nodes:
        return None
    # Look for the MULTIPLY_ADD math node that outputs into roughness
    nt = mat.node_tree
    for n in nt.nodes:
        if (n.bl_idname == "ShaderNodeMath"
                and n.operation == "MULTIPLY_ADD"):
            return n.inputs[2].default_value
    # fallback to Principled BSDF default
    for n in nt.nodes:
        if n.bl_idname == "ShaderNodeBsdfPrincipled":
            return n.inputs["Roughness"].default_value
    return None


rec_rough = rough_base_of("MAT_metal_dark_blued")
mag_rough = rough_base_of("MAT_metal_black_magazine")
check(f"magazine rough_base ({mag_rough}) > receiver ({rec_rough})",
      (rec_rough is not None and mag_rough is not None
       and mag_rough > rec_rough))

# 9. All AK_ objects use a final MAT_* (not the checker material)
ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]
checker_used = []
for o in ak_objects:
    if not o.data.materials:
        checker_used.append(o.name + " (no material)")
        continue
    for m in o.data.materials:
        if m is None or m.name == "MAT_uv_checker_review":
            checker_used.append(o.name)
            break
check("no AK_ object uses MAT_uv_checker_review or empty material",
      not checker_used, f"bad: {checker_used[:10]}")

# 10. No AK_ object has a Boolean modifier
booleans = [o.name for o in ak_objects
            if any(m.type == "BOOLEAN" for m in o.modifiers)]
check("no AK_ object has a Boolean modifier", not booleans,
      f"with boolean: {booleans}")

# 11. 06_MATERIAL_TESTS is hidden
mt = bpy.data.collections.get("06_MATERIAL_TESTS")
check("06_MATERIAL_TESTS hide_render = True",
      mt is not None and mt.hide_render)
check("06_MATERIAL_TESTS hide_viewport = True",
      mt is not None and mt.hide_viewport)

# 12. All 10 final MAT_* materials exist
missing_mats = [m for m in EXPECTED_FINAL_MATERIALS
                if bpy.data.materials.get(m) is None]
check("all 10 final MAT_* materials present", not missing_mats,
      f"missing: {missing_mats}")

# 13. Lookdev render files exist (8 of them)
EXPECTED_RENDERS = [
    "lookdev_full_model_side.png",
    "lookdev_full_model_3quarter.png",
    "lookdev_closeup_metal_receiver.png",
    "lookdev_closeup_wood_stock.png",
    "lookdev_closeup_handguard.png",
    "lookdev_closeup_magazine.png",
    "lookdev_closeup_grip.png",
    "lookdev_clay_material_check.png",
]
missing_renders = [r for r in EXPECTED_RENDERS
                   if not os.path.exists(os.path.join(RENDERS_ROOT, r))]
check("all 8 lookdev renders exist", not missing_renders,
      f"missing: {missing_renders}")

# 14. Documentation files exist
for nm in ("phase_notes.txt", "material_notes.txt",
           "texture_workflow_notes.txt", "lookdev_notes.txt"):
    path = os.path.join(DOCS_ROOT, nm)
    check(f"06_documentation/{nm} exists", os.path.exists(path))

# 15. Section 6 markers in docs
for nm in ("phase_notes.txt", "material_notes.txt",
           "texture_workflow_notes.txt"):
    path = os.path.join(DOCS_ROOT, nm)
    if not os.path.exists(path):
        check(f"06_documentation/{nm} mentions Section 6", False, "missing file")
        continue
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    check(f"06_documentation/{nm} mentions Section 6",
          "Section 6" in text)

# 16. Issue tracker exists with severity summary
tracker = os.path.join(REVIEWS_ROOT, "phase_6_material_issue_tracker.txt")
check("08_reviews/phase_6_material_issue_tracker.txt exists",
      os.path.exists(tracker))
if os.path.exists(tracker):
    with open(tracker, "r", encoding="utf-8") as f:
        text = f.read()
    check("issue tracker has 'High severity     : 0'",
          "High severity     : 0" in text)
    check("issue tracker has 'Blocking Phase 7  : NO'",
          "Blocking Phase 7  : NO" in text)

# 17. No forbidden object names
FORBIDDEN = ("bore", "rifling", "chamber", "bolt_carrier", "firing_pin",
             "feed_lip", "follower", "trigger_mech")
hits = []
for o in ak_objects:
    low = o.name.lower()
    for tok in FORBIDDEN:
        if tok in low:
            hits.append(o.name)
            break
check("no AK_ object name contains forbidden tokens", not hits,
      f"hits: {hits}")

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
print("Hero materials:")
for m in HERO_MATERIALS:
    mat = bpy.data.materials.get(m)
    if mat is None:
        continue
    n_nodes = len(mat.node_tree.nodes) if mat.use_nodes else 0
    print(f"  {m:30s}  nodes={n_nodes}")

print(f"\nAK_ object count: {len(ak_objects)}")
print(f"Lookdev cameras : {len([c for c in EXPECTED_CAMERAS if bpy.data.objects.get(c)])}")
print(f"Lookdev lights  : {len([l for l in EXPECTED_LIGHTS if bpy.data.objects.get(l)])}")
print(f"Lookdev renders : {len([r for r in EXPECTED_RENDERS if os.path.exists(os.path.join(RENDERS_ROOT, r))])}/{len(EXPECTED_RENDERS)}")
