"""Verify v06_final_assembly.blend matches the Phase 7 §7.38 checklist."""
import bpy


EXPECTED_CAMERAS = [
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
    "LIGHT_final_top_soft",
]


print("\n=== §7.38 PHASE 7 FINAL REVIEW ===")
results = []


# --- 13 cameras ---
missing_cams = [n for n in EXPECTED_CAMERAS if n not in bpy.data.objects]
results.append(("13 final cameras present", not missing_cams))
if missing_cams:
    print(f"  missing cameras: {missing_cams}")


# --- 4 lights ---
missing_lights = [n for n in EXPECTED_LIGHTS if n not in bpy.data.objects]
results.append(("4 LIGHT_final_* lights present", not missing_lights))
if missing_lights:
    print(f"  missing lights: {missing_lights}")


# --- BG + floor ---
bg = bpy.data.objects.get("BG_final_neutral_backdrop")
floor = bpy.data.objects.get("FLOOR_final_studio_plane")
results.append(("BG_final_neutral_backdrop exists", bg is not None))
results.append(("FLOOR_final_studio_plane exists", floor is not None))


# --- Turntable rig ---
empty = bpy.data.objects.get("EMPTY_turntable_center")
results.append(("EMPTY_turntable_center exists", empty is not None))

master = bpy.data.objects.get("AK47_MASTER_ASSET")
results.append(("AK47_MASTER_ASSET exists", master is not None))

if master is not None and empty is not None:
    results.append(("AK47_MASTER_ASSET parented to EMPTY_turntable_center",
                     master.parent is empty))
else:
    results.append(("AK47_MASTER_ASSET parented to EMPTY_turntable_center", False))


# --- Turntable animation: 2 keyframes on rotation_z ---
# Blender 5.x moved fcurves into slot channelbags; handle both APIs.
def _collect_fcurves(action):
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    out = []
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                for slot in getattr(action, "slots", []):
                    try:
                        cb = strip.channelbag(slot)
                    except Exception:
                        cb = None
                    if cb is not None and hasattr(cb, "fcurves"):
                        out.extend(cb.fcurves)
    return out


has_anim = False
key_count = 0
if empty is not None and empty.animation_data and empty.animation_data.action:
    for fc in _collect_fcurves(empty.animation_data.action):
        if fc.data_path == "rotation_euler" and fc.array_index == 2:
            has_anim = True
            key_count = len(fc.keyframe_points)
            break
results.append(("turntable rotation_z has 2 keyframes",
                 has_anim and key_count >= 2))


# --- Render settings ---
scene = bpy.context.scene
results.append(("render engine = CYCLES", scene.render.engine == "CYCLES"))
results.append(("resolution 1920x1080",
                 scene.render.resolution_x == 1920 and scene.render.resolution_y == 1080))
results.append(("samples >= 64", scene.cycles.samples >= 64))


# --- Frame range 1..180 ---
results.append(("frame range 1..180",
                 scene.frame_start == 1 and scene.frame_end == 180))


# --- 09_EXPORT_READY contains AK_ meshes ---
exp = bpy.data.collections.get("09_EXPORT_READY")
results.append(("09_EXPORT_READY exists", exp is not None))
if exp is not None:
    ak_count = sum(1 for o in exp.objects if o.name.startswith("AK_"))
    blk_count = sum(1 for o in exp.objects if o.name.startswith("BLK_"))
    results.append(("09_EXPORT_READY has AK_ meshes (>=20)", ak_count >= 20))
    results.append(("09_EXPORT_READY contains no BLK_", blk_count == 0))


# --- Hidden collections (sanity) ---
hide_targets = ["00_REFERENCE", "01_GUIDES", "02_BLOCKOUT", "03H_major_part_backup"]
visible_when_should_be_hidden = []
for cname in hide_targets:
    coll = bpy.data.collections.get(cname)
    if coll is None:
        continue
    for o in coll.objects:
        if not (o.hide_viewport and o.hide_render):
            visible_when_should_be_hidden.append(f"{o.name}@{cname}")
results.append(("reference/guide/blockout/backup hidden",
                 not visible_when_should_be_hidden))
if visible_when_should_be_hidden:
    print(f"  still visible: {visible_when_should_be_hidden[:5]}{'…' if len(visible_when_should_be_hidden) > 5 else ''}")


# --- Final ---
all_pass = True
for label, ok in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok:
        all_pass = False
print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

print(f"Cameras in scene: {sum(1 for o in bpy.data.objects if o.type == 'CAMERA')}")
print(f"Lights in scene:  {sum(1 for o in bpy.data.objects if o.type == 'LIGHT')}")
print(f"Frame range:      {scene.frame_start} .. {scene.frame_end} @ {scene.render.fps} fps")
print(f"Cycles samples:   {scene.cycles.samples}")
