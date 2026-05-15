"""Render the 360° turntable animation from v06_final_assembly.blend as a
PNG sequence into 04_renders/turntable/frames/. A separate post-process step
(or external tool like ffmpeg) is needed to assemble the PNGs into an .mp4.

WARNING: This is a long render. 180 frames at 64 Cycles samples on CPU is
typically ~25–40 minutes depending on hardware.

Why PNG sequence instead of MP4: Blender 5.x removed FFMPEG from
`image_settings.file_format` (only image formats are listed). The portable
fix is to render PNG frames and assemble them with an external ffmpeg.

Run with:
  blender --background 01_blender/v06_final_assembly.blend \
          --python 05_mcp_prompts/section6/section6_render_turntable.py
"""
import bpy
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUT_DIR = os.path.join(PROJECT_ROOT, "04_renders", "turntable", "frames")
os.makedirs(OUT_DIR, exist_ok=True)


import math

scene = bpy.context.scene
scene.camera = bpy.data.objects.get("CAM_turntable_main")
if scene.camera is None:
    raise RuntimeError("CAM_turntable_main missing from scene; run section6_executor.py first")

# Compress the turntable: 120 frames @ 30 fps = 4-second loop, full 360°.
# Override the rotation keyframe at frame 180 to land on frame 120 instead.
TARGET_END_FRAME = 120
scene.frame_start = 1
scene.frame_end = TARGET_END_FRAME

empty = bpy.data.objects.get("EMPTY_turntable_center")
if empty is None:
    raise RuntimeError("EMPTY_turntable_center missing")

# Clear any existing rotation keyframes, then re-key 0->2π over 1..TARGET_END_FRAME
empty.animation_data_clear()
empty.rotation_euler = (0.0, 0.0, 0.0)
empty.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
empty.rotation_euler = (0.0, 0.0, 2.0 * math.pi)
empty.keyframe_insert(data_path="rotation_euler", index=2, frame=TARGET_END_FRAME)

# PNG sequence at portfolio-preview resolution
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 15
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.cycles.samples = 24  # aggressive but viable for a turntable preview

# Blender appends the frame number (####) and the extension automatically.
scene.render.filepath = os.path.join(OUT_DIR, "turntable_")

print(f"\n=== SECTION 6 — TURNTABLE RENDER (PNG sequence) ===")
print(f"  out: {OUT_DIR}/turntable_####.png")
print(f"  frames {scene.frame_start}..{scene.frame_end} @ {scene.render.fps} fps, samples={scene.cycles.samples}")

bpy.ops.render.render(animation=True)
print("=== TURNTABLE RENDER DONE ===")
print("  to assemble into mp4 (when ffmpeg is available):")
print(f"  ffmpeg -framerate 30 -i {OUT_DIR}/turntable_%04d.png \\")
print(f"         -c:v libx264 -pix_fmt yuv420p -crf 18 \\")
print(f"         {os.path.dirname(OUT_DIR)}/turntable_ak_style_exterior_prop.mp4")
