"""Standalone re-run of the two final renders that section7_render_finals.py
failed to produce due to a Freestyle setup bug:
  render_13_wireframe_full_model.png
  render_14_material_breakdown.png

Uses a Wireframe shader node approach (no Freestyle), which is more
deterministic in headless Blender 5.x.
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

# Neutral world
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
out_n = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.20, 0.21, 0.24, 1.0)
bg.inputs["Strength"].default_value = 0.25
links.new(bg.outputs["Background"], out_n.inputs["Surface"])


# --- Wireframe material via Wireframe shader node ---
wire = bpy.data.materials.get("MAT_wireframe_breakdown")
if wire is None:
    wire = bpy.data.materials.new("MAT_wireframe_breakdown")
wire.use_nodes = True
nt = wire.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputMaterial")
out.location = (300, 0)

# Mix: clay base when not on a wire, dark line on wire
mix = nt.nodes.new("ShaderNodeMixShader")
mix.location = (100, 0)

bsdf_base = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf_base.location = (-200, 100)
bsdf_base.inputs["Base Color"].default_value = (0.62, 0.60, 0.57, 1.0)
bsdf_base.inputs["Metallic"].default_value = 0.0
bsdf_base.inputs["Roughness"].default_value = 0.70

bsdf_wire = nt.nodes.new("ShaderNodeEmission")
bsdf_wire.location = (-200, -100)
bsdf_wire.inputs["Color"].default_value = (0.03, 0.03, 0.03, 1.0)
bsdf_wire.inputs["Strength"].default_value = 1.0

wf = nt.nodes.new("ShaderNodeWireframe")
wf.location = (-450, 0)
wf.use_pixel_size = True
# Set size via input (Blender 4.x+)
if "Size" in wf.inputs:
    wf.inputs["Size"].default_value = 1.2

nt.links.new(wf.outputs["Fac"], mix.inputs["Fac"])
nt.links.new(bsdf_base.outputs["BSDF"], mix.inputs[1])
nt.links.new(bsdf_wire.outputs["Emission"], mix.inputs[2])
nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
wire.use_fake_user = True
print("  ensured MAT_wireframe_breakdown")


# --- Swap AK_ materials to wireframe, render, restore ---
ak_objects = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name.startswith("AK_")]
originals = {}
for o in ak_objects:
    if o.data.materials:
        originals[o.name] = [m.name if m else None for m in o.data.materials]
        for i in range(len(o.data.materials)):
            o.data.materials[i] = wire
    else:
        originals[o.name] = []
        o.data.materials.append(wire)


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


render_to("CAM_final_front_3quarter",
          "render_13_wireframe_full_model.png", 1920, 1080, 48)


# --- Restore materials ---
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


# --- render_14_material_breakdown: side ortho view of the final-textured model ---
render_to("CAM_final_side_profile",
          "render_14_material_breakdown.png", 1920, 1080, 96,
          ortho=True, ortho_scale=1.10)

print("done")
