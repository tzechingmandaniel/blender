Project
=======
Non-functional AK-style Exterior 3D Prop

Purpose
-------
This asset is a non-functional exterior 3D prop created for visual
rendering, portfolio presentation, and game-asset display.

Main Files
----------
- 01_blender_final/AK47_exterior_prop_final.blend
- 02_exports/{fbx,glb,obj}/AK47_exterior_prop_visual.{fbx,glb,obj}
- 03_textures/{metal,wood,magazine,grip,shared}/  (procedural shaders;
  README.txt in each folder lists planned PNG names for future bakes)
- 04_final_renders/{full_model,closeups,clay_wireframe_optional,portfolio_selected}/
- 05_turntable/turntable_frames/  (12-frame preview; full MP4 encode
  deferred — see 05_turntable/README.txt)
- 06_documentation/  (this folder)
- 07_public_pack/  (safe public description, captions, summaries)
- 08_archive_notes/  (archive contents log)

How to open
-----------
1. Open 01_blender_final/AK47_exterior_prop_final.blend with Blender 5.1+.
2. The hero materials are procedural (Noise, Wave, Pointiness,
   AmbientOcclusion, Wireframe shader nodes); no external PNG textures
   are required for the .blend to display correctly.
3. Cameras live in collection 08_LIGHTING_CAMERA. Studio lights are
   LIGHT_final_key_soft / fill_soft / rim_subtle / top_soft_optional.
4. Turntable: select EMPTY_turntable_center, frame 1..180 already
   keyframed (linear), 24 fps; render with CAM_turntable_main.
5. Export-ready geometry lives in collection 09_EXPORT_READY (already
   pre-exported to FBX/GLB/OBJ in 02_exports/).

Texture Folder Location
-----------------------
03_textures/<group>/README.txt — planned PNG map names per material
group. No painted PNGs yet (Phase 6 used procedural shaders); Phase 9
may bake the procedurals to PNG.

Render Folder Location
----------------------
04_final_renders/  (full_model + closeups + clay_wireframe_optional +
portfolio_selected)

Export Folder Location
----------------------
02_exports/{fbx,glb,obj}/

Scope
-----
This project is a non-functional exterior visual prop only. It does not
include internal firearm mechanisms, working firing components,
manufacturing dimensions, or real assembly instructions.
