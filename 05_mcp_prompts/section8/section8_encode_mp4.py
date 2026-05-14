"""Encode the rendered turntable PNG sequence into an MP4 using ffmpeg.

Reads from:
  final_delivery/05_turntable/turntable_full_seq/frame_####.png

Writes:
  final_delivery/05_turntable/turntable_ak_style_exterior_prop.mp4

Uses imageio-ffmpeg (pip-installed) to provide ffmpeg without depending
on a system PATH binary.
"""
import os
import subprocess
import sys

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT",
                              os.path.dirname(os.path.dirname(
                                  os.path.dirname(os.path.abspath(__file__)))))
SEQ_DIR = os.path.join(PROJECT_ROOT, "final_delivery", "05_turntable",
                       "turntable_full_seq")
OUT_MP4 = os.path.join(PROJECT_ROOT, "final_delivery", "05_turntable",
                       "turntable_ak_style_exterior_prop.mp4")

if not os.path.isdir(SEQ_DIR):
    print(f"ABORT: PNG sequence dir not found: {SEQ_DIR}")
    sys.exit(1)

pngs = sorted([f for f in os.listdir(SEQ_DIR) if f.endswith(".png")])
if len(pngs) < 60:
    print(f"ABORT: only {len(pngs)} PNG frames found, need at least 60")
    sys.exit(2)

print(f"Encoding {len(pngs)} frames -> {OUT_MP4}")

try:
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using ffmpeg at: {ffmpeg}")
except Exception as e:
    print(f"ABORT: imageio-ffmpeg not available: {e}")
    sys.exit(3)

input_pattern = os.path.join(SEQ_DIR, "frame_%04d.png")

cmd = [
    ffmpeg,
    "-y",                       # overwrite output
    "-framerate", "24",
    "-i", input_pattern,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "18",               # high quality
    "-preset", "medium",
    "-movflags", "+faststart",
    OUT_MP4,
]
print("ffmpeg command:")
print("  " + " ".join(cmd))
print()

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("FFMPEG STDERR (tail):")
    print(result.stderr[-2000:])
    print(f"ABORT: ffmpeg returned {result.returncode}")
    sys.exit(result.returncode)

if not os.path.exists(OUT_MP4):
    print("ABORT: expected output not produced")
    sys.exit(4)

sz = os.path.getsize(OUT_MP4)
print(f"\nDONE: {OUT_MP4} ({sz:,} bytes)")
