"""Section 1 auto-executor.

Builds a fresh v01_project_setup.blend exactly to spec from the plan:
- Metric units, default cube removed
- Ten organized collections
- Eight placeholder materials with the recommended colour palette
- Guide objects (overall length box, centerline, region markers)
- Locked, non-selectable side-view reference image
- Preview camera + key/fill area lights
- Saved to AK47_NonFunctional_Prop/01_blender/v01_project_setup.blend
"""
import bpy
import os
import math
from mathutils import Vector

PROJECT_ROOT = r"C:\AK47_NonFunctional_Prop"
BLEND_OUT = os.path.join(PROJECT_ROOT, "01_blender", "v01_project_setup.blend")
REF_IMAGE = os.path.join(PROJECT_ROOT, "00_references", "original_image", "ak47_side_reference.png")


# -------- 0. fresh scene --------
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.name = "Scene"


# -------- 1.4 unit settings --------
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = "METERS"


# -------- 1.7 create collections --------
COLLECTIONS = [
    "00_REFERENCE", "01_GUIDES", "02_BLOCKOUT", "03_MAJOR_PARTS",
    "04_MINOR_PARTS", "05_DETAIL_PARTS", "06_MATERIAL_TESTS",
    "07_ASSEMBLY", "08_LIGHTING_CAMERA", "09_EXPORT_READY",
]
collections = {}
for name in COLLECTIONS:
    if name in bpy.data.collections:
        c = bpy.data.collections[name]
    else:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    collections[name] = c


def link_to(obj, collection_name):
    """Move obj so it lives only in the named collection."""
    target = collections[collection_name]
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)


# -------- 1.9 placeholder materials --------
def make_material(name, base_color, metallic=0.0, roughness=0.5, display="SOLID"):
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_fake_user = True  # keep around even without object users
    mat.diffuse_color = base_color
    p = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = base_color
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    return mat


# Recommended colours from the plan
make_material("MAT_placeholder_dark_metal",   (0.04, 0.04, 0.045, 1.0), metallic=0.85, roughness=0.55)
make_material("MAT_placeholder_black_metal",  (0.015, 0.015, 0.018, 1.0), metallic=0.85, roughness=0.70)
make_material("MAT_placeholder_dark_wood",    (0.06, 0.020, 0.010, 1.0), metallic=0.0,  roughness=0.55)
make_material("MAT_placeholder_bakelite_grip",(0.10, 0.04, 0.025, 1.0),  metallic=0.0,  roughness=0.50)
make_material("MAT_placeholder_rubber_dark",  (0.02, 0.02, 0.02, 1.0),   metallic=0.0,  roughness=0.85)
make_material("MAT_placeholder_reference_blue",(0.10, 0.30, 0.85, 1.0),  metallic=0.0,  roughness=1.0)
make_material("MAT_placeholder_guide_wire",   (0.10, 0.85, 0.30, 1.0),   metallic=0.0,  roughness=1.0)
make_material("MAT_placeholder_neutral_clay", (0.45, 0.45, 0.45, 1.0),   metallic=0.0,  roughness=0.85)
print(f"materials created: {len(bpy.data.materials)}")


# -------- 1.5 + 1.6 guide objects --------
def add_wire_cube(name, dims, location=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = dims
    obj.display_type = "WIRE"
    obj.show_in_front = True
    obj.hide_render = True
    obj.data.materials.append(bpy.data.materials["MAT_placeholder_guide_wire"])
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)
    return obj


def add_marker_plane(name, location, size=0.04):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = (math.radians(90), 0, 0)  # face the side view
    obj.display_type = "WIRE"
    obj.show_in_front = True
    obj.hide_render = True
    obj.data.materials.append(bpy.data.materials["MAT_placeholder_guide_wire"])
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)
    return obj


# Overall bounding box: 1.0 unit (X length) × 0.08 (Y thickness) × 0.30 (Z height)
overall_box = add_wire_cube("GUIDE_overall_length_box", (1.00, 0.08, 0.30), (0.0, 0.0, 0.0))
link_to(overall_box, "01_GUIDES")

# Centerline: long thin wireframe along X axis
centerline = add_wire_cube("GUIDE_centerline", (1.10, 0.002, 0.002), (0.0, 0.0, 0.0))
link_to(centerline, "01_GUIDES")

# Region markers — visual proportion guides for each major part
REGION_MARKERS = [
    ("GUIDE_stock_end",            (-0.50, 0.0,  0.0)),
    ("GUIDE_receiver_start",       (-0.18, 0.0,  0.0)),
    ("GUIDE_receiver_end",         ( 0.05, 0.0,  0.0)),
    ("GUIDE_magazine_center",      (-0.05, 0.0, -0.10)),
    ("GUIDE_handguard_start",      ( 0.07, 0.0,  0.04)),
    ("GUIDE_barrel_end",           ( 0.42, 0.0,  0.04)),
    ("GUIDE_front_sight_position", ( 0.40, 0.0,  0.07)),
    ("GUIDE_stock_region",         (-0.35, 0.0,  0.0)),
    ("GUIDE_grip_region",          (-0.10, 0.0, -0.05)),
    ("GUIDE_rear_sight_region",    (-0.05, 0.0,  0.06)),
]
for name, loc in REGION_MARKERS:
    m = add_marker_plane(name, loc)
    link_to(m, "01_GUIDES")
print(f"guide objects: {len(collections['01_GUIDES'].objects)}")


# -------- 1.6 import reference image --------
if os.path.isfile(REF_IMAGE):
    bpy.ops.object.empty_add(type="IMAGE", location=(0.0, 0.05, 0.0))
    ref = bpy.context.active_object
    ref.name = "REF_ak47_side_view"
    ref.data = bpy.data.images.load(REF_IMAGE)
    ref.empty_display_size = 1.0
    ref.empty_image_offset = (-0.5, -0.3)
    ref.empty_image_depth = "BACK"
    # Side-view modelling: rotate so the image faces the +Y direction (we look from -Y)
    ref.rotation_euler = (math.radians(90), 0, 0)
    ref.color = (1, 1, 1, 0.40)  # 40% opacity per the plan
    ref.show_empty_image_orthographic = True
    ref.show_empty_image_perspective = True
    ref.hide_render = True
    ref.lock_location = (True, True, True)
    ref.lock_rotation = (True, True, True)
    ref.lock_scale = (True, True, True)
    ref.hide_select = True  # non-selectable per plan
    link_to(ref, "00_REFERENCE")
    print(f"reference image loaded: {ref.name}")
else:
    print(f"WARN: reference not found at {REF_IMAGE}")


# -------- 1.11 camera + lighting --------
bpy.ops.object.camera_add(location=(0.65, -0.85, 0.30))
cam = bpy.context.active_object
cam.name = "CAM_preview_3quarter"
cam.rotation_euler = (math.radians(78), 0, math.radians(38))
cam.data.lens = 70  # 70mm per the plan
link_to(cam, "08_LIGHTING_CAMERA")
scene.camera = cam

bpy.ops.object.light_add(type="AREA", location=(0.6, -0.6, 0.9))
key = bpy.context.active_object
key.name = "Area_Light_Key"
key.data.size = 0.6
key.data.energy = 80
key.rotation_euler = (math.radians(-25), math.radians(20), 0)
link_to(key, "08_LIGHTING_CAMERA")

bpy.ops.object.light_add(type="AREA", location=(-0.7, 0.5, 0.6))
fill = bpy.context.active_object
fill.name = "Area_Light_Fill"
fill.data.size = 0.8
fill.data.energy = 35
fill.rotation_euler = (math.radians(-30), math.radians(-20), 0)
link_to(fill, "08_LIGHTING_CAMERA")
print("camera + 2 area lights placed")


# -------- 1.12 save --------
os.makedirs(os.path.dirname(BLEND_OUT), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print(f"saved: {BLEND_OUT}")
