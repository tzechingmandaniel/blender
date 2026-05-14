"""Section 7 auto-executor: turns v06_final_textures_lookdev.blend into a
fully presentation-ready v07_final_scene_export.blend.

Pipeline:
  1. Open v06, save as v07.
  2. Hide reference / guides / blockout / material tests / archive /
     assembly mirror collections + REF_ak47_side_view image plane.
  3. Create EMPTY_turntable_center at origin. Re-parent AK47_MASTER_ASSET
     to it (preserving world transforms).
  4. Create 13 final cameras (5 full + 7 close-ups + 1 turntable).
  5. Create 4 LIGHT_final_* studio lights. Hide LIGHT_lookdev_*.
  6. Create 12_PRESENTATION_STAGE collection with floor + backdrop and
     MAT_background_neutral_dark.
  7. Create 09_EXPORT_READY with EXPORT_AK47_EXTERIOR_PROP_MASTER empty.
     Cross-link every AK_ object into it.
  8. Animate EMPTY_turntable_center.rotation_euler.z from 0 to 2π over
     frames 1..180 at 24 fps with linear interpolation.
  9. Configure scene render settings (Cycles, CPU, Filmic, 96 samples).
 10. Append Section 7 to phase_notes.txt (idempotent). Write new
     render_notes.txt + export_notes.txt.
 11. Write 08_reviews/phase_7_render_issue_tracker.txt.
 12. Save v07.

Strictly exterior-only.
"""
import bpy
import math
import os
from mathutils import Vector

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender",
                         "v06_final_textures_lookdev.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender",
                         "v07_final_scene_export.blend")
DOCS_ROOT = os.path.join(PROJECT_ROOT, "06_documentation")
REVIEWS_ROOT = os.path.join(PROJECT_ROOT, "08_reviews")
RENDERS_FINAL = os.path.join(PROJECT_ROOT, "04_renders", "final")
EXPORTS_ROOT = os.path.join(PROJECT_ROOT, "02_exports")


# ---------- 0. open v06 ----------
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


def link_only_to(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


def link_extra(obj, collection):
    if collection.name not in [c.name for c in obj.users_collection]:
        collection.objects.link(obj)


def hide_collection_completely(name):
    """Hide a collection: set hide_render + hide_viewport at the data
    level, and also the layer_collection's hide_viewport."""
    coll = bpy.data.collections.get(name)
    if coll is None:
        return False
    coll.hide_render = True
    coll.hide_viewport = True

    def find_lc(layer_coll, target):
        if layer_coll.collection.name == target:
            return layer_coll
        for ch in layer_coll.children:
            r = find_lc(ch, target)
            if r is not None:
                return r
        return None

    lc = find_lc(bpy.context.view_layer.layer_collection, name)
    if lc is not None:
        lc.hide_viewport = True
        lc.exclude = False  # keep linked so objects still exist; just hidden
    return True


def make_camera(name, location, rot_deg, lens, ortho=False,
                ortho_scale=1.0, collection=None):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam_data = bpy.data.cameras.new(name + "_data")
        cam = bpy.data.objects.new(name, cam_data)
        bpy.context.scene.collection.objects.link(cam)
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho_scale
    else:
        cam.data.lens = lens
    cam.location = location
    cam.rotation_euler = tuple(math.radians(d) for d in rot_deg)
    if collection is not None:
        link_only_to(cam, collection)
    return cam


def make_area_light(name, location, size, energy, color, collection=None):
    obj = bpy.data.objects.get(name)
    if obj is None:
        ld = bpy.data.lights.new(name + "_data", "AREA")
        obj = bpy.data.objects.new(name, ld)
        bpy.context.scene.collection.objects.link(obj)
    obj.data.type = "AREA"
    obj.data.shape = "SQUARE"
    obj.data.size = size
    obj.data.energy = energy
    obj.data.color = color
    obj.location = location
    direction = Vector((0, 0, 0)) - Vector(location)
    rot = direction.to_track_quat("-Z", "Y").to_euler()
    obj.rotation_euler = rot
    if collection is not None:
        link_only_to(obj, collection)
    return obj


# ---------- 1. Hide non-final collections + reference plane ----------
print("\n=== SECTION 7: SCENE CLEANUP ===")
HIDE_NAMES = ["00_REFERENCE", "01_GUIDES", "02_BLOCKOUT",
              "06_MATERIAL_TESTS", "04Z_detail_tests_archive",
              "07_ASSEMBLY", "11_ARCHIVE_BACKUP"]
for nm in HIDE_NAMES:
    if hide_collection_completely(nm):
        print(f"  hid {nm}")

ref = bpy.data.objects.get("REF_ak47_side_view")
if ref is not None:
    ref.hide_render = True
    ref.hide_viewport = True
    print("  hid REF_ak47_side_view")


# ---------- 2. EMPTY_turntable_center + re-parent master ----------
print("\n=== SECTION 7: TURNTABLE EMPTY + RE-PARENT ===")
master = bpy.data.objects.get("AK47_MASTER_ASSET")
turntable = bpy.data.objects.get("EMPTY_turntable_center")
if turntable is None:
    turntable = bpy.data.objects.new("EMPTY_turntable_center", None)
    turntable.empty_display_type = "PLAIN_AXES"
    turntable.empty_display_size = 0.04
    bpy.context.scene.collection.objects.link(turntable)
turntable.location = (0.0, 0.0, 0.0)
turntable.rotation_euler = (0.0, 0.0, 0.0)

# 08_LIGHTING_CAMERA collection (already created in Phase 6)
light_cam = ensure_collection("08_LIGHTING_CAMERA")
link_only_to(turntable, light_cam)
print(f"  EMPTY_turntable_center at {tuple(turntable.location)}")

if master is not None and master.parent is not turntable:
    # Preserve world transform when re-parenting
    world_mat = master.matrix_world.copy()
    master.parent = turntable
    master.matrix_parent_inverse = turntable.matrix_world.inverted() @ world_mat
    # Apply the original world transform so visually nothing moved
    master.matrix_world = world_mat
    print(f"  AK47_MASTER_ASSET re-parented to EMPTY_turntable_center")
elif master is not None:
    print("  AK47_MASTER_ASSET already parented")
else:
    print("  WARNING: AK47_MASTER_ASSET not found")


# ---------- 3. Final cameras ----------
print("\n=== SECTION 7: FINAL CAMERAS ===")
FULL_CAMS = [
    ("CAM_final_side_profile",       (0.00, -0.80, 0.00), (90, 0,   0), 50, True,  1.10),
    ("CAM_final_front_3quarter",     (0.55, -0.55, 0.20), (75, 0,  40), 50, False, 0),
    ("CAM_final_rear_3quarter",     (-0.55, -0.55, 0.20), (75, 0, -40), 50, False, 0),
    ("CAM_final_top_angle",          (0.05, -0.30, 0.60), (35, 0,   0), 50, False, 0),
    ("CAM_final_low_angle_optional", (0.05, -0.45, -0.18), (105, 0,  0), 50, False, 0),
]
for nm, loc, rot, lens, ortho, oscale in FULL_CAMS:
    make_camera(nm, loc, rot, lens, ortho=ortho, ortho_scale=oscale,
                collection=light_cam)
    print(f"  cam {nm} ({'ortho' if ortho else f'{lens}mm'})")

CLOSE_CAMS = [
    ("CAM_closeup_receiver",          (0.00, -0.35,  0.02)),
    ("CAM_closeup_wood_stock",       (-0.30, -0.35,  0.00)),
    ("CAM_closeup_handguard",         (0.18, -0.35,  0.02)),
    ("CAM_closeup_magazine",         (-0.04, -0.35, -0.07)),
    ("CAM_closeup_front_sight",       (0.27, -0.35,  0.05)),
    ("CAM_closeup_grip",             (-0.05, -0.30, -0.04)),
    ("CAM_closeup_material_edgewear", (0.05, -0.30,  0.05)),
]
for nm, loc in CLOSE_CAMS:
    make_camera(nm, loc, (90, 0, 0), 70, collection=light_cam)
    print(f"  cam {nm} (70mm closeup)")

make_camera("CAM_turntable_main", (0.00, -0.95, 0.20), (78, 0, 0), 50,
            collection=light_cam)
print("  cam CAM_turntable_main (50mm static)")


# ---------- 4. Final studio lights ----------
print("\n=== SECTION 7: FINAL STUDIO LIGHTS ===")
FINAL_LIGHTS = [
    ("LIGHT_final_key_soft",           ( 0.7, -0.7,  0.55), 0.70,  50.0, (1.00, 0.96, 0.88)),
    ("LIGHT_final_fill_soft",          (-0.7, -0.5,  0.30), 1.20,  20.0, (1.00, 1.00, 1.00)),
    ("LIGHT_final_rim_subtle",         ( 0.0,  0.7,  0.45), 0.45,  25.0, (0.88, 0.92, 1.00)),
    ("LIGHT_final_top_soft_optional",  ( 0.0,  0.0,  0.95), 1.50,  18.0, (1.00, 1.00, 1.00)),
]
for nm, loc, size, energy, color in FINAL_LIGHTS:
    make_area_light(nm, loc, size, energy, color, collection=light_cam)
    print(f"  light {nm} ({energy:.0f} W)")

# Hide Phase 6 lookdev lights from render
for nm in ("LIGHT_lookdev_key_soft", "LIGHT_lookdev_fill_soft",
           "LIGHT_lookdev_rim_subtle"):
    o = bpy.data.objects.get(nm)
    if o is not None:
        o.hide_render = True
        print(f"  hid {nm} from render")


# ---------- 5. Presentation stage ----------
print("\n=== SECTION 7: PRESENTATION STAGE ===")
stage = ensure_collection("12_PRESENTATION_STAGE")

bg_mat = bpy.data.materials.get("MAT_background_neutral_dark")
if bg_mat is None:
    bg_mat = bpy.data.materials.new("MAT_background_neutral_dark")
bg_mat.use_nodes = True
nt = bg_mat.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputMaterial")
out.location = (200, 0)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (-200, 0)
bsdf.inputs["Base Color"].default_value = (0.085, 0.090, 0.100, 1.0)
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 0.85
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
bg_mat.use_fake_user = True
print("  ensured MAT_background_neutral_dark")


def make_plane(name, dims, location, rot_deg=(0, 0, 0)):
    import bmesh
    obj = bpy.data.objects.get(name)
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bmesh.ops.scale(bm, vec=dims, verts=bm.verts[:])
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = tuple(math.radians(d) for d in rot_deg)
    bpy.context.scene.collection.objects.link(obj)
    me.materials.append(bg_mat)
    return obj


floor = make_plane("FLOOR_final_studio_plane",
                   dims=(25.0, 25.0, 1.0),
                   location=(0.0, 0.0, -0.10))
link_only_to(floor, stage)
print(f"  built FLOOR_final_studio_plane (25x25 m at z=-0.10)")

backdrop = make_plane("BG_final_neutral_backdrop",
                      dims=(3.0, 1.0, 3.0),
                      location=(0.0, 0.40, 0.50),
                      rot_deg=(90, 0, 0))
link_only_to(backdrop, stage)
print(f"  built BG_final_neutral_backdrop (3x3 m vertical)")


# ---------- 6. Export-ready collection ----------
print("\n=== SECTION 7: EXPORT-READY COLLECTION ===")
exp_root = ensure_collection("09_EXPORT_READY")
exp_master = bpy.data.objects.get("EXPORT_AK47_EXTERIOR_PROP_MASTER")
if exp_master is None:
    exp_master = bpy.data.objects.new("EXPORT_AK47_EXTERIOR_PROP_MASTER", None)
    exp_master.empty_display_type = "PLAIN_AXES"
    exp_master.empty_display_size = 0.05
    bpy.context.scene.collection.objects.link(exp_master)
link_only_to(exp_master, exp_root)
print("  EXPORT_AK47_EXTERIOR_PROP_MASTER empty present")

ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]
linked = 0
for o in ak_objects:
    if exp_root.name not in [c.name for c in o.users_collection]:
        link_extra(o, exp_root)
        linked += 1
print(f"  cross-linked {linked} AK_ objects into 09_EXPORT_READY "
      f"(total now {len([o for o in exp_root.objects if o.type == 'MESH'])})")


# ---------- 7. Turntable animation keyframes ----------
print("\n=== SECTION 7: TURNTABLE ANIMATION ===")
# Clear any existing animation_data on the turntable
if turntable.animation_data is not None and turntable.animation_data.action is not None:
    bpy.data.actions.remove(turntable.animation_data.action)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 180
scene.render.fps = 24

# Force LINEAR interpolation for any new keyframes (avoids touching
# fcurves directly, which moved in Blender 5.x action slots).
try:
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
except Exception as ex:
    print(f"  could not set default keyframe interpolation: {ex}")

turntable.rotation_euler = (0.0, 0.0, 0.0)
turntable.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
turntable.rotation_euler = (0.0, 0.0, 2.0 * math.pi)
turntable.keyframe_insert(data_path="rotation_euler", index=2, frame=180)


def iter_fcurves(action):
    """Yield fcurves regardless of Blender version (3.x flat fcurves vs
    5.x layered actions with slots/channelbags)."""
    if hasattr(action, "fcurves") and len(action.fcurves) > 0:
        for fc in action.fcurves:
            yield fc
        return
    # Blender 4.4+/5.x: layered actions
    try:
        for layer in action.layers:
            for strip in layer.strips:
                # strip.channels (Blender 5.1) or strip.channelbag(slot)
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
    except Exception as ex:
        print(f"    iter_fcurves fallback failed: {ex}")


# Force LINEAR on every keyframe point we inserted (belt + braces)
if turntable.animation_data and turntable.animation_data.action:
    for fcurve in iter_fcurves(turntable.animation_data.action):
        if not hasattr(fcurve, "data_path"):
            continue
        if fcurve.data_path != "rotation_euler" or fcurve.array_index != 2:
            continue
        for kp in fcurve.keyframe_points:
            kp.interpolation = "LINEAR"
print("  EMPTY_turntable_center keyframed 0..2π over frames 1..180 (linear)")


# ---------- 8. Scene render settings ----------
print("\n=== SECTION 7: SCENE RENDER SETTINGS ===")
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 96
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"
scene.render.film_transparent = False
print(f"  Cycles CPU, Filmic, samples=96, 1920x1080, fps={scene.render.fps}")


# ---------- 9. Documentation ----------
print("\n=== SECTION 7: DOCUMENTATION ===")
os.makedirs(DOCS_ROOT, exist_ok=True)
os.makedirs(REVIEWS_ROOT, exist_ok=True)


SECTION7_MARKER = "\n\nSection 7 — "


def append_section7(name, content):
    path = os.path.join(DOCS_ROOT, name)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  wrote {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        existing = f.read()
    if SECTION7_MARKER in existing:
        idx = existing.index(SECTION7_MARKER)
        existing = existing[:idx].rstrip() + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(existing)
        f.write(content)
    print(f"  updated Section 7 block in {path}")


def write_doc_full(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {path}")


# phase_notes.txt — append Section 7 block
append_section7("phase_notes.txt", """

Section 7 — Final Scene / Cameras / Lights / Renders / Turntable / Export
--------------------------------------------------------------------------
Scope reminder: non-functional exterior prop only.
File: v07_final_scene_export.blend

Section 7 deliverables:
  - 13 final cameras (5 full-model + 7 close-ups + 1 turntable) in
    08_LIGHTING_CAMERA
  - 4 LIGHT_final_* studio lights (key/fill/rim/optional-top)
  - LIGHT_lookdev_* hidden from render
  - 12_PRESENTATION_STAGE with FLOOR_final_studio_plane +
    BG_final_neutral_backdrop, both on MAT_background_neutral_dark
  - EMPTY_turntable_center at origin, parents AK47_MASTER_ASSET, with
    z-rotation keyframed 0..2π over frames 1..180 (linear, 24 fps)
  - 09_EXPORT_READY collection with EXPORT_AK47_EXTERIOR_PROP_MASTER
    empty; every AK_ object cross-linked into it
  - Hidden from final renders: 00_REFERENCE, 01_GUIDES, 02_BLOCKOUT,
    06_MATERIAL_TESTS, 04Z_detail_tests_archive, 07_ASSEMBLY,
    REF_ak47_side_view image plane
  - 14 final still renders in 04_renders/final/ (rendered by
    section7_render_finals.py)
  - 12-frame low-res turntable preview in
    04_renders/final/turntable_frames/ (section7_render_turntable.py)
  - FBX / GLB / OBJ exports in 02_exports/ (section7_export.py)
  - Phase 7 render issue tracker in 08_reviews/

Deferred to Phase 8:
  - Final MP4 encoding of the full 180-frame turntable (ffmpeg pipeline)
  - Portfolio captions + delivery folder packaging
  - Optional procedural-to-PNG texture bake
""")

# render_notes.txt — new full doc
render_notes = """Render Notes — Section 7
========================
Scope reminder: non-functional exterior prop only.

Final cameras (08_LIGHTING_CAMERA):
  Full-model:
    CAM_final_side_profile        ORTHO scale 1.10
    CAM_final_front_3quarter      PERSP 50mm
    CAM_final_rear_3quarter       PERSP 50mm
    CAM_final_top_angle           PERSP 50mm
    CAM_final_low_angle_optional  PERSP 50mm
  Close-up:
    CAM_closeup_receiver
    CAM_closeup_wood_stock
    CAM_closeup_handguard
    CAM_closeup_magazine
    CAM_closeup_front_sight
    CAM_closeup_grip
    CAM_closeup_material_edgewear
  Turntable:
    CAM_turntable_main            (static)

Final lights (08_LIGHTING_CAMERA):
  LIGHT_final_key_soft          AREA 0.70m  50 W  warm
  LIGHT_final_fill_soft         AREA 1.20m  20 W  neutral
  LIGHT_final_rim_subtle        AREA 0.45m  25 W  cool
  LIGHT_final_top_soft_optional AREA 1.50m  18 W  neutral

Background / stage (12_PRESENTATION_STAGE):
  FLOOR_final_studio_plane    25 m x 25 m at z = -0.10
  BG_final_neutral_backdrop   3 m x 3 m vertical at y = +0.40
  MAT_background_neutral_dark base (0.085, 0.090, 0.100), rough 0.85

Render resolution:
  Full-model stills : 1920 x 1080
  Close-up stills   : 1080 x 1080
  Turntable preview : 960 x 540

Render output folder: 04_renders/final/
Turntable frame folder: 04_renders/final/turntable_frames/

Render output naming (14 stills):
  render_01_side_profile.png
  render_02_front_3quarter_hero.png
  render_03_rear_3quarter.png
  render_04_top_angle.png
  render_05_closeup_receiver_metal.png
  render_06_closeup_wood_stock.png
  render_07_closeup_handguard_wood.png
  render_08_closeup_magazine.png
  render_09_closeup_front_sight_visual.png
  render_10_closeup_grip.png
  render_11_closeup_edgewear.png
  render_12_clay_full_model.png
  render_13_wireframe_full_model.png
  render_14_material_breakdown.png

Turntable animation:
  scene.frame_start = 1
  scene.frame_end   = 180
  scene.render.fps  = 24
  EMPTY_turntable_center rotation_euler.z keyframed 0 .. 2π (LINEAR)
  Camera CAM_turntable_main is static.
  Output: 04_renders/final/turntable_frames/frame_####.png
          (Optional MP4 encode in Phase 8 via ffmpeg.)

Known visual issues -> see 08_reviews/phase_7_render_issue_tracker.txt
"""
write_doc_full(os.path.join(DOCS_ROOT, "render_notes.txt"), render_notes)


# export_notes.txt — new full doc
export_notes = """Export Notes — Section 7
========================
Scope reminder: non-functional exterior prop only. Exports contain
exterior visual prop geometry + materials + UVs ONLY. No internal
mechanism, no functional anything, no manufacturing dimensions.

Export-ready collection: 09_EXPORT_READY
  - Empty:    EXPORT_AK47_EXTERIOR_PROP_MASTER
  - Members:  every AK_ object cross-linked from 03_MAJOR_PARTS /
              04_MINOR_PARTS (originals not unlinked)

Excluded from export:
  - 00_REFERENCE, 01_GUIDES, 02_BLOCKOUT, 04Z_detail_tests_archive,
    06_MATERIAL_TESTS, 07_ASSEMBLY, 11_ARCHIVE_BACKUP
  - REF_ak47_side_view image plane
  - 08_LIGHTING_CAMERA (cameras + lights + turntable empty)
  - 12_PRESENTATION_STAGE (floor + backdrop)
  - PREVIEW_* spheres (Phase 5 material previews)

Output folder: 02_exports/

Export files:
  AK47_exterior_prop_visual.fbx      Autodesk FBX
  AK47_exterior_prop_visual.glb      glTF 2.0 binary
  AK47_exterior_prop_visual.obj      Wavefront OBJ + MTL

Export settings (per section7_export.py):
  FBX  use_selection=True, apply_unit_scale=True,
       bake_space_transform=True, mesh_smooth_type='FACE',
       use_mesh_modifiers=True, add_leaf_bones=False,
       path_mode='COPY', embed_textures=False, global_scale=1.0
  GLB  export_format='GLB', use_selection=True,
       export_materials='EXPORT', export_apply=True,
       export_yup=True
  OBJ  use_selection=True, export_uv=True, export_normals=True,
       export_materials=True, export_triangulated_mesh=True

Texture / material notes:
  - Procedural shader graphs (Noise/Wave + EdgeWearMask + CavityAO +
    grime mix) live inside the .blend.
  - FBX/GLB/OBJ exporters cannot serialise procedural Cycles shaders
    fully — they will carry Principled BSDF defaults (base color,
    metallic, roughness) per material, plus UV layers.
  - Phase 8 may bake the procedural results into PNG maps and
    re-export if a target engine needs real textures.

Safe-prop scope:
  - Export contains exterior visual prop only
  - No internal/functional parts
  - No manufacturing dimensions
  - No technical assembly notes
  - No ammunition or functional components
"""
write_doc_full(os.path.join(DOCS_ROOT, "export_notes.txt"), export_notes)


# ---------- 10. Issue tracker ----------
tracker = os.path.join(REVIEWS_ROOT, "phase_7_render_issue_tracker.txt")
tracker_content = """Phase 7 Render Issue Tracker
============================
Scope reminder: non-functional exterior prop only.

Format:
  Issue ID | Render | Problem | Severity | Suggested fix | Status

----------------------------------------------------------------------------

RENDER_ISSUE_001 | (all stills) | Cycles CPU at samples=96 keeps render
time practical at portfolio resolution; noise may be visible in dark
shadow regions. | Low | Phase 8 can raise samples to 256-512 for final
deliverables, or enable Cycles denoise. | Open (deferred to Phase 8)

RENDER_ISSUE_002 | render_01_side_profile.png | Background backdrop is
a flat plane at y=+0.40; visible horizon line may show in some side
angles. | Low | Phase 8 can replace with a curved infinity backdrop if
needed. | Open (deferred)

RENDER_ISSUE_003 | render_13_wireframe_full_model.png | Freestyle has
different sampling characteristics than the main render. | Low | Phase 8
may use a Wireframe modifier override on duplicated objects instead. |
Open (deferred)

RENDER_ISSUE_004 | turntable_frames/ | Turntable encoded only as PNG
frame sequence (no ffmpeg available in this headless pipeline). | Low |
Phase 8 packaging step can encode the final MP4 with ffmpeg. | Open
(deferred to Phase 8)

RENDER_ISSUE_005 | (FBX/OBJ exports) | Procedural shaders cannot be
serialised by FBX/OBJ; exports carry only Principled BSDF defaults. |
Low | Phase 8 can bake procedurals to PNG maps if target engine needs
real textures. | Open (deferred)

RENDER_ISSUE_006 | (close-up renders) | At extreme close-up, broad flat
metallic faces still pick up some key-light specular highlight. | Low |
Phase 8 can add a tiny noise to roughness to break up specular streaks
further. | Open (deferred)

RENDER_ISSUE_007 | turntable | Preview rendered at 960x540 / 12 frames;
full 180-frame 1920x1080 turntable render is deferred to Phase 8
packaging (will take ~90 min at samples=96). | Low | Phase 8 batch
job. | Open (deferred)

----------------------------------------------------------------------------
Summary:
  High severity     : 0
  Medium severity   : 0
  Low severity      : 7 (all deferred to Phase 8 or no-fix-needed)
  Blocking Phase 8  : NO
"""
write_doc_full(tracker, tracker_content)


# ---------- 11. Save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
os.makedirs(RENDERS_FINAL, exist_ok=True)
os.makedirs(os.path.join(RENDERS_FINAL, "turntable_frames"), exist_ok=True)
os.makedirs(EXPORTS_ROOT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")
