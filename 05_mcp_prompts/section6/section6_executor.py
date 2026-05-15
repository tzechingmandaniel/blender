"""Section 6 auto-executor: builds the final presentation scene (cameras,
lighting, background, turntable rig, export-ready collection) on top of
v05_uv_materials.blend and saves v06_final_assembly.blend.

Auto-detects the project root from __file__ — no hardcoded path.

This script does NOT render. Rendering is split into two follow-up scripts:
  section6_render_stills.py    — 11 portfolio stills (a few minutes)
  section6_render_turntable.py — 180-frame turntable (long)

All exterior-only. No functional animation, no internal geometry.
"""
import bpy
import math
import os
from mathutils import Vector, Euler


# ---------- 0. paths ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SRC_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v05_uv_materials.blend")
OUT_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v06_final_assembly.blend")

print(f"\n=== SECTION 6 — FINAL SCENE / CAMERAS / LIGHTING / TURNTABLE ===")
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


def world_bbox(name):
    o = bpy.data.objects.get(name)
    if o is None:
        return None, None, None
    coords = [o.matrix_world @ Vector(v) for v in o.bound_box]
    xs = [c.x for c in coords]; ys = [c.y for c in coords]; zs = [c.z for c in coords]
    mn = Vector((min(xs), min(ys), min(zs)))
    mx = Vector((max(xs), max(ys), max(zs)))
    return mn, mx, (mn + mx) * 0.5


def make_camera(name, location, look_at, lens=50.0, ortho_scale=None, sub_collection="08_LIGHTING_CAMERA"):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = location

    direction = Vector(look_at) - Vector(location)
    if direction.length > 0:
        cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    if ortho_scale is not None:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.lens = lens

    link_only_to(cam_obj, sub_collection)
    return cam_obj


def make_area_light(name, location, look_at, energy, size=0.7, color=(1.0, 1.0, 1.0)):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    light_data = bpy.data.lights.new(name, type="AREA")
    light_data.energy = energy
    light_data.size = size
    light_data.color = color
    light_obj = bpy.data.objects.new(name, light_data)
    light_obj.location = location

    direction = Vector(look_at) - Vector(location)
    if direction.length > 0:
        light_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    link_only_to(light_obj, "08_LIGHTING_CAMERA")
    return light_obj


# ---------- 1. scene cleanup — hide work collections ----------
print("\n-- scene cleanup --")
HIDE_COLLECTIONS = ["00_REFERENCE", "01_GUIDES", "02_BLOCKOUT",
                     "03H_major_part_backup", "06_MATERIAL_TESTS"]
for cname in HIDE_COLLECTIONS:
    coll = bpy.data.collections.get(cname)
    if coll is None:
        continue
    # Hide every object inside from render and viewport
    for o in coll.objects:
        o.hide_viewport = True
        o.hide_render = True
    # Also try to hide the collection itself if scene tree supports it
    print(f"  hid {len(coll.objects):2d} objects in {cname}")


# Compute overall model bbox from AK_ refined parts (excluding hidden BLK_)
ak_main_parts = [
    "AK_receiver_main", "AK_dustcover_main", "AK_stock_main",
    "AK_grip_main", "AK_magazine_main",
    "AK_handguard_lower_main", "AK_handguard_upper_main",
    "AK_gas_tube_outer", "AK_barrel_outer_closed",
    "AK_front_sight_block_visual", "AK_rear_sight_visual",
]
all_pts = []
for n in ak_main_parts:
    mn, mx, _ = world_bbox(n)
    if mn is not None:
        all_pts.extend([mn, mx])
if all_pts:
    model_min = Vector((min(p.x for p in all_pts),
                        min(p.y for p in all_pts),
                        min(p.z for p in all_pts)))
    model_max = Vector((max(p.x for p in all_pts),
                        max(p.y for p in all_pts),
                        max(p.z for p in all_pts)))
else:
    model_min = Vector((-0.5, -0.05, -0.15))
    model_max = Vector((0.45, 0.05, 0.05))
model_center = (model_min + model_max) * 0.5
model_size = model_max - model_min
print(f"  model bbox center: {tuple(round(v, 3) for v in model_center)}, size: {tuple(round(v, 3) for v in model_size)}")


# ---------- 2. master assembly + turntable empty ----------
print("\n-- master assembly + turntable empty --")
get_or_make_collection("07_ASSEMBLY")
get_or_make_collection("08_LIGHTING_CAMERA")

# AK47_MASTER_ASSET already exists from Section 2 supplement. Treat it as
# the master assembly.
master = bpy.data.objects.get("AK47_MASTER_ASSET")
if master is None:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=model_center)
    master = bpy.context.active_object
    master.name = "AK47_MASTER_ASSET"
    master.empty_display_size = 0.30
link_only_to(master, "07_ASSEMBLY")
print(f"  master assembly: {master.name}")

# Turntable center empty — placed at the model's visual centre
if "EMPTY_turntable_center" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["EMPTY_turntable_center"], do_unlink=True)
bpy.ops.object.empty_add(type="ARROWS", location=model_center)
turntable_empty = bpy.context.active_object
turntable_empty.name = "EMPTY_turntable_center"
turntable_empty.empty_display_size = 0.18
link_only_to(turntable_empty, "08_LIGHTING_CAMERA")

# Parent AK47_MASTER_ASSET to EMPTY_turntable_center while keeping world transform
master.parent = turntable_empty
master.matrix_parent_inverse = turntable_empty.matrix_world.inverted()
print(f"  AK47_MASTER_ASSET parented to EMPTY_turntable_center at {tuple(round(v, 3) for v in model_center)}")


# ---------- 3. final cameras ----------
print("\n-- final cameras --")

cx, cy, cz = model_center.x, model_center.y, model_center.z
# Camera offsets — distance scales with model length
L = max(model_size.x, 0.8)  # use model length as reference distance
D = L * 1.3   # standard portrait distance

# Full-model cameras
# ortho_scale bumped to 2.7x model length so the full silhouette fits with
# generous margin — values below 2.0 cropped the receiver/grip area.
make_camera("CAM_final_side_profile",
            location=(cx, cy + D, cz),
            look_at=(cx, cy, cz),
            ortho_scale=L * 2.7)

make_camera("CAM_final_front_3quarter",
            location=(cx + D * 0.55, cy + D * 0.85, cz + L * 0.25),
            look_at=(cx, cy, cz), lens=55.0)

make_camera("CAM_final_rear_3quarter",
            location=(cx - D * 0.55, cy + D * 0.85, cz + L * 0.20),
            look_at=(cx, cy, cz), lens=55.0)

make_camera("CAM_final_top_angle",
            location=(cx + D * 0.15, cy + D * 0.40, cz + L * 0.70),
            look_at=(cx, cy, cz), lens=55.0)

make_camera("CAM_final_low_angle_optional",
            location=(cx + D * 0.40, cy + D * 0.80, cz - L * 0.12),
            look_at=(cx, cy, cz + L * 0.05), lens=60.0)


# Close-up camera helper — frames an AK_ part with the camera in front (+Y)
def make_closeup(name, target_obj_name, dist_mult=4.0, elev_mult=0.6, lens=85.0):
    mn, mx, c = world_bbox(target_obj_name)
    if mn is None:
        print(f"  skip {name}: missing target {target_obj_name}")
        return None
    target_center = c
    target_size = mx - mn
    target_max_dim = max(target_size.x, target_size.y, target_size.z)
    cam_dist = max(target_max_dim * dist_mult, 0.08)
    location = (target_center.x, target_center.y + cam_dist, target_center.z + target_max_dim * elev_mult)
    return make_camera(name, location=location, look_at=tuple(target_center), lens=lens)


# Close-ups (frame the named part)
make_closeup("CAM_closeup_receiver",          "AK_receiver_main")
make_closeup("CAM_closeup_wood_stock",        "AK_stock_main")
make_closeup("CAM_closeup_handguard",         "AK_handguard_lower_main")
make_closeup("CAM_closeup_magazine",          "AK_magazine_main")
make_closeup("CAM_closeup_front_sight",       "AK_front_sight_block_visual", dist_mult=8.0)
make_closeup("CAM_closeup_grip",              "AK_grip_main")
make_closeup("CAM_closeup_material_edgewear", "AK_receiver_main", dist_mult=3.0, elev_mult=0.4, lens=100.0)


# Turntable camera — same framing as front 3/4 but parented to nothing
# so it stays static while EMPTY_turntable_center rotates.
make_camera("CAM_turntable_main",
            location=(cx + D * 0.55, cy + D * 0.95, cz + L * 0.20),
            look_at=(cx, cy, cz), lens=55.0)


print(f"  created 13 cameras in 08_LIGHTING_CAMERA")


# ---------- 4. final studio lighting ----------
print("\n-- final lighting --")

# Key — large soft area, upper front, slightly camera-left
# Energies tuned after first render pass: original 120/40/80/60 W blew out
# wood/metal under Filmic. Current values render the dark worn-prop look the
# materials were designed for.
make_area_light("LIGHT_final_key_soft",
                location=(cx + L * 0.3, cy + D * 0.9, cz + L * 1.0),
                look_at=(cx, cy, cz), energy=50.0, size=0.7)

# Fill — opposite side, weaker
make_area_light("LIGHT_final_fill_soft",
                location=(cx - L * 0.5, cy + D * 0.6, cz + L * 0.4),
                look_at=(cx, cy, cz), energy=20.0, size=0.9)

# Rim — behind, mid-height, to separate silhouette from background
make_area_light("LIGHT_final_rim_subtle",
                location=(cx - L * 0.4, cy - D * 0.6, cz + L * 0.3),
                look_at=(cx, cy, cz), energy=30.0, size=0.4)

# Optional top soft
make_area_light("LIGHT_final_top_soft",
                location=(cx, cy + L * 0.2, cz + L * 1.4),
                look_at=(cx, cy, cz), energy=25.0, size=1.2)

print(f"  created 4 LIGHT_final_* lights")


# ---------- 5. background and stage ----------
print("\n-- background / floor / world ----")

# Neutral mid-grey material for background and floor
bg_mat = bpy.data.materials.get("MAT_background_neutral_dark")
if bg_mat is None:
    bg_mat = bpy.data.materials.new("MAT_background_neutral_dark")
    bg_mat.use_nodes = True
    nt = bg_mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.15, 0.16, 0.18, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.85
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
bg_mat.use_fake_user = True


def make_plane(name, location, size, rotation_deg=(0, 0, 0)):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = tuple(math.radians(d) for d in rotation_deg)
    obj.data.materials.clear()
    obj.data.materials.append(bg_mat)
    link_only_to(obj, "08_LIGHTING_CAMERA")
    return obj


make_plane("FLOOR_final_studio_plane",
           location=(cx, cy, model_min.z - 0.02),
           size=12.0)

make_plane("BG_final_neutral_backdrop",
           location=(cx, cy - 3.0, cz + 1.0),
           size=12.0,
           rotation_deg=(90, 0, 0))


# Studio world background
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.13, 0.14, 0.16, 1.0)
bg.inputs["Strength"].default_value = 0.4
links.new(bg.outputs["Background"], out.inputs["Surface"])

print("  background + floor planes + world set")


# ---------- 6. render settings ----------
print("\n-- render settings --")
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"
print("  Cycles, 1920x1080, 128 samples, Filmic")


# ---------- 7. turntable animation ----------
print("\n-- turntable animation --")
scene.frame_start = 1
scene.frame_end = 180
scene.render.fps = 30

# Two keyframes on EMPTY_turntable_center: frame 1 = 0 rad, frame 180 = 2π
turntable_empty.rotation_euler = Euler((0.0, 0.0, 0.0), "XYZ")
turntable_empty.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
turntable_empty.rotation_euler = Euler((0.0, 0.0, 2.0 * math.pi), "XYZ")
turntable_empty.keyframe_insert(data_path="rotation_euler", index=2, frame=180)

# Linear interpolation on the rotation Z curve so the spin is constant.
# Blender 5.x moved fcurves into slot channelbags; fall back to 4.x .fcurves.
def _set_rotation_z_linear(obj):
    if not (obj.animation_data and obj.animation_data.action):
        return False
    action = obj.animation_data.action
    fcurves = []
    if hasattr(action, "fcurves"):  # 4.x and earlier
        fcurves = list(action.fcurves)
    elif hasattr(action, "layers"):  # 5.x slotted actions
        for layer in action.layers:
            for strip in layer.strips:
                for slot in getattr(action, "slots", []):
                    try:
                        cb = strip.channelbag(slot)
                    except Exception:
                        cb = None
                    if cb is not None and hasattr(cb, "fcurves"):
                        fcurves.extend(cb.fcurves)
    changed = False
    for fc in fcurves:
        if fc.data_path == "rotation_euler" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
                changed = True
    return changed


if not _set_rotation_z_linear(turntable_empty):
    print("  WARN: could not set LINEAR interpolation (fcurve API mismatch); bezier easing in effect")

print("  EMPTY_turntable_center: rotation_euler.z 0→2π over frames 1..180, linear")


# ---------- 8. export-ready collection (links, not copies) ----------
print("\n-- export-ready collection --")
export_coll = get_or_make_collection("09_EXPORT_READY")
# Clear any prior links first
for o in list(export_coll.objects):
    export_coll.objects.unlink(o)

linked = 0
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if not o.name.startswith("AK_"):
        continue
    if o.name in export_coll.objects:
        continue
    # Link (don't move) — the object stays in its original collection AND
    # is also referenced by 09_EXPORT_READY
    try:
        export_coll.objects.link(o)
        linked += 1
    except RuntimeError:
        pass
print(f"  09_EXPORT_READY now references {linked} AK_ mesh objects")


# ---------- 9. save ----------
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"\nsaved: {OUT_BLEND}")

# Summary
cams = [o for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith("CAM_final_") or o.name.startswith("CAM_closeup_") or o.name.startswith("CAM_turntable_")]
lights = [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith("LIGHT_final_")]
print(f"  cameras: {len(cams)};  final lights: {len(lights)};  export-ready: {linked}")
