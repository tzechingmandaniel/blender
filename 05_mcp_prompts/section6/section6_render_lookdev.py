"""Render the 8 Phase 6 lookdev views into 04_renders/lookdev/.

  lookdev_full_model_side.png         VIEW_side_modeling (ortho)
  lookdev_full_model_3quarter.png     CAM_lookdev_full_model
  lookdev_closeup_metal_receiver.png  CAM_lookdev_metal_closeup
  lookdev_closeup_wood_stock.png      CAM_lookdev_wood_closeup
  lookdev_closeup_handguard.png       CAM_lookdev_handguard_closeup
  lookdev_closeup_magazine.png        CAM_lookdev_magazine_closeup
  lookdev_closeup_grip.png            CAM_lookdev_grip_closeup
  lookdev_clay_material_check.png     full model under MAT_clay_neutral_preview

Hides REF_, GUIDE_, BLK_, archive, and 06_MATERIAL_TESTS / 07_ASSEMBLY
collections during rendering. Restores after each render.
"""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "lookdev")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"

# Neutral grey world
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out_node = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.18, 0.19, 0.22, 1.0)
bg.inputs["Strength"].default_value = 0.20
links.new(bg.outputs["Background"], out_node.inputs["Surface"])


# --- Hide guide/blockout/archive/tests ---
HIDE_OBJECTS = ["REF_ak47_side_view"]
for coll_name in ("01_GUIDES", "02_BLOCKOUT",
                  "04Z_detail_tests_archive",
                  "06_MATERIAL_TESTS"):
    coll = bpy.data.collections.get(coll_name)
    if coll:
        HIDE_OBJECTS += [o.name for o in coll.objects]

prev_states = {}
for name in HIDE_OBJECTS:
    obj = bpy.data.objects.get(name)
    if obj:
        prev_states[name] = obj.hide_render
        obj.hide_render = True

# Boost old Section 5 area lights only if Phase 6 lights are missing
LOOKDEV_LIGHTS = ["LIGHT_lookdev_key_soft", "LIGHT_lookdev_fill_soft",
                  "LIGHT_lookdev_rim_subtle"]
for nm in LOOKDEV_LIGHTS:
    o = bpy.data.objects.get(nm)
    if o is not None:
        # ensure they're visible
        o.hide_render = False
        o.hide_viewport = False


def render_to(cam_name, filename, width=1400, height=700, samples=64,
              ortho=False, ortho_scale=1.10):
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"  cam not found: {cam_name}")
        return False
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho_scale
    scene.camera = cam
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.cycles.samples = samples
    scene.render.filepath = os.path.join(OUT_DIR, filename)
    bpy.ops.render.render(write_still=True)
    print(f"  rendered {cam_name} -> {filename}")
    return True


# Full views
render_to("VIEW_side_modeling",      "lookdev_full_model_side.png",
          width=1400, height=700, samples=64, ortho=True, ortho_scale=1.10)
render_to("CAM_lookdev_full_model",  "lookdev_full_model_3quarter.png",
          width=1400, height=700, samples=64)

# Close-ups (square format)
render_to("CAM_lookdev_metal_closeup",     "lookdev_closeup_metal_receiver.png",
          width=1000, height=1000, samples=96)
render_to("CAM_lookdev_wood_closeup",      "lookdev_closeup_wood_stock.png",
          width=1000, height=1000, samples=96)
render_to("CAM_lookdev_handguard_closeup", "lookdev_closeup_handguard.png",
          width=1000, height=1000, samples=96)
render_to("CAM_lookdev_magazine_closeup",  "lookdev_closeup_magazine.png",
          width=1000, height=1000, samples=96)
render_to("CAM_lookdev_grip_closeup",      "lookdev_closeup_grip.png",
          width=1000, height=1000, samples=96)

# Clay render: temporarily swap every AK_ object to MAT_clay_neutral_preview
clay = bpy.data.materials.get("MAT_clay_neutral_preview")
if clay is None:
    print("  warning: MAT_clay_neutral_preview not found, skipping clay render")
else:
    originals = {}
    ak_objects = [o for o in bpy.data.objects
                  if o.type == "MESH" and o.name.startswith("AK_")]
    for o in ak_objects:
        if o.data.materials:
            originals[o.name] = [m.name if m else None for m in o.data.materials]
            for i in range(len(o.data.materials)):
                o.data.materials[i] = clay
        else:
            originals[o.name] = []
            o.data.materials.append(clay)
    render_to("CAM_lookdev_full_model", "lookdev_clay_material_check.png",
              width=1400, height=700, samples=48)
    # Restore
    for nm, slots in originals.items():
        obj = bpy.data.objects.get(nm)
        if obj is None:
            continue
        if not slots:
            while obj.data.materials:
                obj.data.materials.pop(index=-1)
            continue
        for i, mname in enumerate(slots):
            if mname is None:
                continue
            mat = bpy.data.materials.get(mname)
            if mat is None:
                continue
            if i < len(obj.data.materials):
                obj.data.materials[i] = mat
            else:
                obj.data.materials.append(mat)

# Restore hidden objects
for name, prev in prev_states.items():
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = prev

print("done")
