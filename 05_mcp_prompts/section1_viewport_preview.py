"""Viewport-style preview that shows the guides + reference (overrides hide_render
just for the preview — the source .blend is left untouched)."""
import bpy
import os

OUT = r"C:\AK47_NonFunctional_Prop\04_renders\viewport_tests\v01_setup_preview.png"

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"  # OpenGL-style render: shows wireframes
scene.render.resolution_x = 1200
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

# Workbench shading: solid + cavity
ws = scene.display.shading
ws.light = "STUDIO"
ws.color_type = "MATERIAL"
ws.show_cavity = True
ws.show_object_outline = True

# Force everything visible during this render
hidden_during_render = []
for obj in bpy.data.objects:
    if obj.hide_render:
        obj.hide_render = False
        hidden_during_render.append(obj.name)

# Camera
cam = bpy.data.objects.get("CAM_preview_3quarter")
if cam:
    scene.camera = cam

os.makedirs(os.path.dirname(OUT), exist_ok=True)
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)

# Restore hide_render flags so the .blend isn't dirtied
for name in hidden_during_render:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = True

print(f"rendered: {OUT}")
print(f"objects shown (hide_render flipped): {len(hidden_during_render)}")
