"""Render all 14 Phase 7 final stills into 04_renders/final/.

Reads v07_final_scene_export.blend. Assumes the scene already has:
  - 13 final cameras in 08_LIGHTING_CAMERA
  - 4 LIGHT_final_* studio lights
  - 12_PRESENTATION_STAGE collection
  - Non-final collections hidden from render
"""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "final")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium Contrast"

# Neutral world background (subtle ambient)
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out_n = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.15, 0.16, 0.18, 1.0)
bg.inputs["Strength"].default_value = 0.20
links.new(bg.outputs["Background"], out_n.inputs["Surface"])


def render_to(cam_name, filename, width, height, samples, ortho=False,
              ortho_scale=None):
    cam = bpy.data.objects.get(cam_name)
    if cam is None:
        print(f"  cam not found: {cam_name}")
        return False
    if ortho:
        cam.data.type = "ORTHO"
        if ortho_scale is not None:
            cam.data.ortho_scale = ortho_scale
    scene.camera = cam
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.cycles.samples = samples
    scene.render.filepath = os.path.join(OUT_DIR, filename)
    bpy.ops.render.render(write_still=True)
    print(f"  rendered {cam_name} -> {filename}")
    return True


# --- Standard final renders ---
RENDER_LIST = [
    ("CAM_final_side_profile",        "render_01_side_profile.png",            1920, 1080,  96, True,  1.10),
    ("CAM_final_front_3quarter",      "render_02_front_3quarter_hero.png",     1920, 1080,  96, False, None),
    ("CAM_final_rear_3quarter",       "render_03_rear_3quarter.png",           1920, 1080,  96, False, None),
    ("CAM_final_top_angle",           "render_04_top_angle.png",               1920, 1080,  96, False, None),
    ("CAM_closeup_receiver",          "render_05_closeup_receiver_metal.png",  1080, 1080, 128, False, None),
    ("CAM_closeup_wood_stock",        "render_06_closeup_wood_stock.png",      1080, 1080, 128, False, None),
    ("CAM_closeup_handguard",         "render_07_closeup_handguard_wood.png",  1080, 1080, 128, False, None),
    ("CAM_closeup_magazine",          "render_08_closeup_magazine.png",        1080, 1080, 128, False, None),
    ("CAM_closeup_front_sight",       "render_09_closeup_front_sight_visual.png", 1080, 1080, 128, False, None),
    ("CAM_closeup_grip",              "render_10_closeup_grip.png",            1080, 1080, 128, False, None),
    ("CAM_closeup_material_edgewear", "render_11_closeup_edgewear.png",        1080, 1080, 128, False, None),
]
for cam, fn, w, h, s, ortho, oscale in RENDER_LIST:
    render_to(cam, fn, w, h, s, ortho=ortho, ortho_scale=oscale)


# --- Clay render (render_12) ---
print("\n  building clay material swap...")
clay = bpy.data.materials.get("MAT_clay_neutral_preview")
ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]
originals = {}
if clay is not None:
    for o in ak_objects:
        if o.data.materials:
            originals[o.name] = [m.name if m else None for m in o.data.materials]
            for i in range(len(o.data.materials)):
                o.data.materials[i] = clay
        else:
            originals[o.name] = []
            o.data.materials.append(clay)
    render_to("CAM_final_front_3quarter",
              "render_12_clay_full_model.png", 1920, 1080, 64)
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


# --- Wireframe render (render_13) — via Wireframe shader node ---
print("\n  building wireframe render...")
wire = bpy.data.materials.get("MAT_wireframe_breakdown")
if wire is None:
    wire = bpy.data.materials.new("MAT_wireframe_breakdown")
wire.use_nodes = True
wnt = wire.node_tree
for n in list(wnt.nodes):
    wnt.nodes.remove(n)
w_out = wnt.nodes.new("ShaderNodeOutputMaterial")
w_out.location = (300, 0)
w_mix = wnt.nodes.new("ShaderNodeMixShader")
w_mix.location = (100, 0)
w_clay = wnt.nodes.new("ShaderNodeBsdfPrincipled")
w_clay.location = (-200, 100)
w_clay.inputs["Base Color"].default_value = (0.62, 0.60, 0.57, 1.0)
w_clay.inputs["Metallic"].default_value = 0.0
w_clay.inputs["Roughness"].default_value = 0.70
w_emit = wnt.nodes.new("ShaderNodeEmission")
w_emit.location = (-200, -100)
w_emit.inputs["Color"].default_value = (0.03, 0.03, 0.03, 1.0)
w_emit.inputs["Strength"].default_value = 1.0
w_wf = wnt.nodes.new("ShaderNodeWireframe")
w_wf.location = (-450, 0)
w_wf.use_pixel_size = True
if "Size" in w_wf.inputs:
    w_wf.inputs["Size"].default_value = 1.2
wnt.links.new(w_wf.outputs["Fac"], w_mix.inputs["Fac"])
wnt.links.new(w_clay.outputs["BSDF"], w_mix.inputs[1])
wnt.links.new(w_emit.outputs["Emission"], w_mix.inputs[2])
wnt.links.new(w_mix.outputs["Shader"], w_out.inputs["Surface"])
wire.use_fake_user = True

# Swap to wireframe, render, restore
for o in ak_objects:
    if o.data.materials:
        originals[o.name] = [m.name if m else None for m in o.data.materials]
        for i in range(len(o.data.materials)):
            o.data.materials[i] = wire
    else:
        originals[o.name] = []
        o.data.materials.append(wire)
render_to("CAM_final_front_3quarter",
          "render_13_wireframe_full_model.png", 1920, 1080, 48)
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


# --- Material breakdown (render_14): side view at 1920x1080 ---
render_to("CAM_final_side_profile",
          "render_14_material_breakdown.png", 1920, 1080, 96,
          ortho=True, ortho_scale=1.10)

print("\ndone")
