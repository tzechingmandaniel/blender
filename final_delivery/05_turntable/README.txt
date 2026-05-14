Turntable — Final Delivery
===========================
Scope reminder: non-functional exterior visual prop only.

Contents:
  turntable_ak_style_exterior_prop.mp4
    Final 180-frame turntable video. 1280x720, 24 fps, H.264 in MPEG-4
    container, full 360° rotation (frame 1 = 0°, frame 180 = 360°).
    The animation rotates EMPTY_turntable_center around Z; AK47_MASTER_ASSET
    is parented to it so the whole prop rotates as a single rigid body
    (no functional part animation).

  turntable_frames/
    12-frame low-resolution preview (960x540) — every 15° step. Useful
    for thumbnail strips and quick QA of rotation centering.

  turntable_full_seq/
    180-frame source PNG sequence (1280x720) used to encode the MP4.
    Kept alongside the MP4 so the encode can be re-run at a different
    bitrate / codec without re-rendering. Each frame name is
    frame_####.png with 4-digit zero-padded frame numbers.

Render settings:
  resolution : 1280 x 720
  samples    : Cycles 32 samples, CPU
  fps        : 24
  frames     : 1..180 (full 360° rotation)
  view xform : Filmic, Medium Contrast

Encode pipeline:
  Blender renders the PNG sequence; section8_encode_mp4.py uses the
  imageio-ffmpeg bundled binary to encode the sequence to H.264 in MP4.

To re-encode at higher quality (system ffmpeg or imageio-ffmpeg required):
  ffmpeg -framerate 24 -i turntable_full_seq/frame_%04d.png \
    -c:v libx264 -crf 15 -pix_fmt yuv420p -preset slow \
    -movflags +faststart turntable_ak_style_exterior_prop_hq.mp4

To produce a smaller preview MP4 from the existing frames:
  ffmpeg -framerate 24 -i turntable_full_seq/frame_%04d.png \
    -c:v libx264 -crf 28 -pix_fmt yuv420p -vf scale=854:480 \
    turntable_preview_480p.mp4
