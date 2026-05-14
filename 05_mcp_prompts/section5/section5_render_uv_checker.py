"""Render side + 3/4 UV-checker previews of v05_uv_materials.blend into
04_renders/uv_checker. Temporarily swaps every AK_ object onto
MAT_uv_checker_review (procedural checker tied to UVMap), then restores
the original material after rendering."""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "uv_checker")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.render.resolution_x = 1400
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"

# Hide reference image, guides, BLK_ blockout, 04Z archive, and 06_ tests
HIDE_OBJECTS = ["REF_ak47_side_view"]
for coll_name in ("01_GUIDES", "02_BLOCKOUT", "04Z_detail_tests_archive",
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
bg.inputs["Color"].default_value = (0.20, 0.21, 0.24, 1.0)
bg.inputs["Strength"].default_value = 0.55
links.new(bg.outputs["Background"], out_node.inputs["Surface"])

# Lights
for nm, e in (("Area_Light_Key", 75), ("Area_Light_Fill", 30)):
    lt = bpy.data.objects.get(nm)
    if lt:
        lt.data.energy = e

# Swap to checker material, remember originals
checker = bpy.data.materials.get("MAT_uv_checker_review")
if checker is None:
    print("ERROR: MAT_uv_checker_review not found — run section5_executor first")
    raise SystemExit(1)

original_materials = {}
ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]
for o in ak_objects:
    if o.data.materials:
        original_materials[o.name] = [m.name if m else None
                                      for m in o.data.materials]
        for i in range(len(o.data.materials)):
            o.data.materials[i] = checker
    else:
        original_materials[o.name] = []
        o.data.materials.append(checker)


def render_from(camera_name, filename):
    cam = bpy.data.objects.get(camera_name)
    if not cam:
        print(f"  cam not found: {camera_name}")
        return
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_DIR, filename)
    bpy.ops.render.render(write_still=True)
    print(f"  rendered {camera_name} -> {filename}")


render_from("CAM_preview_3quarter", "v05_uv_checker_3quarter.png")

side = bpy.data.objects.get("VIEW_side_modeling")
if side:
    side.data.type = "ORTHO"
    side.data.ortho_scale = 1.10
    render_from("VIEW_side_modeling", "v05_uv_checker_side.png")

# Restore materials
for nm, slots in original_materials.items():
    obj = bpy.data.objects.get(nm)
    if obj is None:
        continue
    if not slots:
        # Strip checker
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

for name, prev in prev_states.items():
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = prev

print("done")
