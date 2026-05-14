"""Verify v07_final_scene_export.blend against §7.38 final checklist."""
import bpy
import os
import math

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
BLEND_PATH = os.path.join(PROJECT_ROOT, "01_blender",
                          "v07_final_scene_export.blend")
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)

DOCS_ROOT = os.path.join(PROJECT_ROOT, "06_documentation")
REVIEWS_ROOT = os.path.join(PROJECT_ROOT, "08_reviews")
RENDERS_FINAL = os.path.join(PROJECT_ROOT, "04_renders", "final")
EXPORTS_ROOT = os.path.join(PROJECT_ROOT, "02_exports")

EXPECTED_CAMS = [
    "CAM_final_side_profile",
    "CAM_final_front_3quarter",
    "CAM_final_rear_3quarter",
    "CAM_final_top_angle",
    "CAM_final_low_angle_optional",
    "CAM_closeup_receiver",
    "CAM_closeup_wood_stock",
    "CAM_closeup_handguard",
    "CAM_closeup_magazine",
    "CAM_closeup_front_sight",
    "CAM_closeup_grip",
    "CAM_closeup_material_edgewear",
    "CAM_turntable_main",
]
EXPECTED_LIGHTS = [
    "LIGHT_final_key_soft",
    "LIGHT_final_fill_soft",
    "LIGHT_final_rim_subtle",
    "LIGHT_final_top_soft_optional",
]
HIDE_COLLS = [
    "00_REFERENCE", "01_GUIDES", "02_BLOCKOUT",
    "06_MATERIAL_TESTS", "04Z_detail_tests_archive",
    "07_ASSEMBLY", "11_ARCHIVE_BACKUP",
]
EXPECTED_STILLS = [
    "render_01_side_profile.png",
    "render_02_front_3quarter_hero.png",
    "render_03_rear_3quarter.png",
    "render_04_top_angle.png",
    "render_05_closeup_receiver_metal.png",
    "render_06_closeup_wood_stock.png",
    "render_07_closeup_handguard_wood.png",
    "render_08_closeup_magazine.png",
    "render_09_closeup_front_sight_visual.png",
    "render_10_closeup_grip.png",
    "render_11_closeup_edgewear.png",
    "render_12_clay_full_model.png",
    "render_13_wireframe_full_model.png",
    "render_14_material_breakdown.png",
]
EXPECTED_EXPORTS = [
    "AK47_exterior_prop_visual.fbx",
    "AK47_exterior_prop_visual.glb",
    "AK47_exterior_prop_visual.obj",
]

print("\n=== §7.38 FINAL REVIEW CHECKLIST ===")
results = []


def check(label, ok, detail=""):
    results.append((label, ok, detail))


# Scene cleanup — hidden collections
for nm in HIDE_COLLS:
    coll = bpy.data.collections.get(nm)
    if coll is None:
        # Not all phases create every collection; absence is acceptable.
        continue
    check(f"{nm} hide_render = True", coll.hide_render)
    check(f"{nm} hide_viewport = True", coll.hide_viewport)

# REF_ak47_side_view hidden
ref = bpy.data.objects.get("REF_ak47_side_view")
if ref is not None:
    check("REF_ak47_side_view hide_render = True", ref.hide_render)
    check("REF_ak47_side_view hide_viewport = True", ref.hide_viewport)

# Cameras
missing_cams = [c for c in EXPECTED_CAMS if bpy.data.objects.get(c) is None]
check("all 13 final cameras exist", not missing_cams,
      f"missing: {missing_cams}")
# CAM_final_side_profile is ortho
side = bpy.data.objects.get("CAM_final_side_profile")
check("CAM_final_side_profile is ORTHO",
      side is not None and side.data.type == "ORTHO")
# Cameras live in 08_LIGHTING_CAMERA
light_cam = bpy.data.collections.get("08_LIGHTING_CAMERA")
lc_members = {o.name for o in (light_cam.objects if light_cam else [])}
out_of_lc = [c for c in EXPECTED_CAMS if c not in lc_members]
check("all 13 cameras in 08_LIGHTING_CAMERA", not out_of_lc,
      f"out: {out_of_lc[:5]}")

# Final lights
missing_lights = [l for l in EXPECTED_LIGHTS
                  if bpy.data.objects.get(l) is None]
check("all 4 LIGHT_final_* exist", not missing_lights,
      f"missing: {missing_lights}")
lookdev_hidden = []
for nm in ("LIGHT_lookdev_key_soft", "LIGHT_lookdev_fill_soft",
           "LIGHT_lookdev_rim_subtle"):
    o = bpy.data.objects.get(nm)
    if o is not None and not o.hide_render:
        lookdev_hidden.append(nm)
check("all LIGHT_lookdev_* hide_render = True",
      not lookdev_hidden, f"still visible: {lookdev_hidden}")

# Presentation stage
stage = bpy.data.collections.get("12_PRESENTATION_STAGE")
check("12_PRESENTATION_STAGE collection exists", stage is not None)
floor = bpy.data.objects.get("FLOOR_final_studio_plane")
bg = bpy.data.objects.get("BG_final_neutral_backdrop")
check("FLOOR_final_studio_plane exists", floor is not None)
check("BG_final_neutral_backdrop exists", bg is not None)
mat_bg = bpy.data.materials.get("MAT_background_neutral_dark")
check("MAT_background_neutral_dark exists", mat_bg is not None)

# Turntable empty + reparent
turntable = bpy.data.objects.get("EMPTY_turntable_center")
check("EMPTY_turntable_center exists", turntable is not None)
master = bpy.data.objects.get("AK47_MASTER_ASSET")
check("AK47_MASTER_ASSET.parent == EMPTY_turntable_center",
      master is not None and master.parent is turntable)

# Turntable keyframes — handle both Blender 3.x flat fcurves and
# 5.x layered actions (layers -> strips -> channels/channelbags).
def iter_fcurves(action):
    if hasattr(action, "fcurves") and len(action.fcurves) > 0:
        for fc in action.fcurves:
            yield fc
        return
    try:
        for layer in action.layers:
            for strip in layer.strips:
                if hasattr(strip, "channels"):
                    for fc in strip.channels:
                        yield fc
                    continue
                for slot in action.slots:
                    cb = strip.channelbag(slot)
                    if cb is None:
                        continue
                    for fc in cb.fcurves:
                        yield fc
    except Exception:
        return


def has_z_rotation_keyframes(obj, expected_frames):
    if obj is None or obj.animation_data is None or obj.animation_data.action is None:
        return False, []
    found = []
    for fc in iter_fcurves(obj.animation_data.action):
        if fc.data_path == "rotation_euler" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                found.append(int(round(kp.co.x)))
    return all(f in found for f in expected_frames), found


ok_kf, found_kf = has_z_rotation_keyframes(turntable, [1, 180])
check("EMPTY_turntable_center keyframed at frames 1 and 180", ok_kf,
      f"found: {found_kf}")
# Linear interpolation
linear_ok = False
if (turntable is not None and turntable.animation_data is not None
        and turntable.animation_data.action is not None):
    interps = []
    for fc in iter_fcurves(turntable.animation_data.action):
        if fc.data_path == "rotation_euler" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                interps.append(kp.interpolation)
    linear_ok = len(interps) >= 2 and all(i == "LINEAR" for i in interps)
check("turntable keyframes use LINEAR interpolation", linear_ok)

# Camera CAM_turntable_main has NO animation
turn_cam = bpy.data.objects.get("CAM_turntable_main")
turn_cam_static = (turn_cam is None
                   or turn_cam.animation_data is None
                   or turn_cam.animation_data.action is None)
check("CAM_turntable_main is static (no animation data)", turn_cam_static)

# Frame range + fps
scene = bpy.context.scene
check("scene.frame_start == 1", scene.frame_start == 1)
check("scene.frame_end == 180", scene.frame_end == 180)
check("scene.render.fps == 24", scene.render.fps == 24)

# Render engine + view transform
check("scene.render.engine == CYCLES",
      scene.render.engine == "CYCLES")
check("Filmic view transform",
      scene.view_settings.view_transform == "Filmic")

# Export-ready collection
exp_root = bpy.data.collections.get("09_EXPORT_READY")
check("09_EXPORT_READY collection exists", exp_root is not None)
exp_master = bpy.data.objects.get("EXPORT_AK47_EXTERIOR_PROP_MASTER")
check("EXPORT_AK47_EXTERIOR_PROP_MASTER empty exists",
      exp_master is not None)
ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]
not_in_export = []
for o in ak_objects:
    if exp_root is None:
        continue
    if exp_root.name not in [c.name for c in o.users_collection]:
        not_in_export.append(o.name)
check("every AK_ object linked into 09_EXPORT_READY",
      not not_in_export, f"missing: {not_in_export[:5]}")

# 09_EXPORT_READY should NOT contain cameras/lights/stage planes
if exp_root is not None:
    bad_in_export = [o.name for o in exp_root.objects
                     if o.type in ("CAMERA", "LIGHT")
                     or o.name.startswith("FLOOR_")
                     or o.name.startswith("BG_")]
    check("09_EXPORT_READY has no cameras/lights/stage planes",
          not bad_in_export, f"bad: {bad_in_export}")

# No AK_ object has a Boolean modifier
booleans = [o.name for o in ak_objects
            if any(m.type == "BOOLEAN" for m in o.modifiers)]
check("no AK_ object has a Boolean modifier", not booleans,
      f"with boolean: {booleans}")

# Final material integrity preserved
EXPECTED_FINALS = [
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
missing_mats = [m for m in EXPECTED_FINALS
                if bpy.data.materials.get(m) is None]
check("all 10 final MAT_* materials still present", not missing_mats,
      f"missing: {missing_mats}")

# Final renders on disk
missing_renders = [r for r in EXPECTED_STILLS
                   if not os.path.exists(os.path.join(RENDERS_FINAL, r))]
check("all 14 final still renders exist in 04_renders/final/",
      not missing_renders, f"missing: {missing_renders}")

# Turntable frames
ttf = os.path.join(RENDERS_FINAL, "turntable_frames")
ttf_count = 0
if os.path.isdir(ttf):
    ttf_count = len([f for f in os.listdir(ttf) if f.endswith(".png")])
check(f"turntable preview frames rendered ({ttf_count} PNGs found)",
      ttf_count >= 12)

# Export files
missing_exports = [e for e in EXPECTED_EXPORTS
                   if not os.path.exists(os.path.join(EXPORTS_ROOT, e))]
check("FBX + GLB + OBJ exports exist in 02_exports/",
      not missing_exports, f"missing: {missing_exports}")

# Documentation
for nm in ("phase_notes.txt", "material_notes.txt", "uv_notes.txt",
           "texture_workflow_notes.txt", "lookdev_notes.txt",
           "render_notes.txt", "export_notes.txt"):
    path = os.path.join(DOCS_ROOT, nm)
    check(f"06_documentation/{nm} exists", os.path.exists(path))
# Section 7 mentioned in render/export/phase
for nm in ("phase_notes.txt", "render_notes.txt", "export_notes.txt"):
    path = os.path.join(DOCS_ROOT, nm)
    if not os.path.exists(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    check(f"06_documentation/{nm} mentions Section 7",
          "Section 7" in text)

# Issue tracker
tracker = os.path.join(REVIEWS_ROOT, "phase_7_render_issue_tracker.txt")
check("08_reviews/phase_7_render_issue_tracker.txt exists",
      os.path.exists(tracker))
if os.path.exists(tracker):
    with open(tracker, "r", encoding="utf-8") as f:
        text = f.read()
    check("issue tracker reports 0 High severity",
          "High severity     : 0" in text)
    check("issue tracker reports 'Blocking Phase 8  : NO'",
          "Blocking Phase 8  : NO" in text)

# Forbidden tokens
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
print(f"AK_ object count        : {len(ak_objects)}")
print(f"Final cameras           : {len([c for c in EXPECTED_CAMS if bpy.data.objects.get(c)])}")
print(f"Final lights            : {len([l for l in EXPECTED_LIGHTS if bpy.data.objects.get(l)])}")
print(f"Final stills rendered   : {len([r for r in EXPECTED_STILLS if os.path.exists(os.path.join(RENDERS_FINAL, r))])}/{len(EXPECTED_STILLS)}")
print(f"Turntable preview frames: {ttf_count}")
print(f"Export files            : {len([e for e in EXPECTED_EXPORTS if os.path.exists(os.path.join(EXPORTS_ROOT, e))])}/{len(EXPECTED_EXPORTS)}")
