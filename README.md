# AK-47 — Non-Functional Exterior 3D Prop

A Blender modelling project for a **non-functional exterior 3D visual prop** in
AK-47 / AKM style. Built with a step-by-step plan, executed via Blender Python
scripts driven by an LLM/MCP workflow.

> **Scope note.** This is an exterior visual prop only — no internal firearm
> mechanism, no working chamber/bolt/spring/firing system, no real magazine
> locking, no manufacturing dimensions. The aim is silhouette + surface
> realism for renders, game assets, and portfolio work.

## Project status

- ✅ **Section 1 — Project Setup** complete (`v01_project_setup.blend`)
- ✅ **Section 2 — Blockout** complete (`v02_blockout.blend`)
- ✅ **Section 3 — Major parts** complete (`v03_major_parts.blend`)
- ✅ **Section 4 — Minor details** complete (`v04_minor_details.blend`)
- ✅ **Section 5 — UV / Materials** complete (`v05_uv_materials.blend`)
- ✅ **Section 6 — Final texture / lookdev** complete (`v06_final_textures_lookdev.blend`)
- ✅ **Section 7 — Final scene / renders / turntable / export** complete (`v07_final_scene_export.blend`)
- ✅ **Section 8 — Final review / packaging / handover** complete (`final_delivery/` + archive zip)
- ✅ **Section 9 — Post-delivery / portfolio / retrospective** complete (`post_delivery/` + archive zip)
- ✅ **Section 10 — Advanced presentation pack** complete (`advanced_presentation_pack/` + archive zip)

## Directory layout

```
AK47_NonFunctional_Prop/
├── 00_references/          original + cropped + paintover refs, scope notes
├── 01_blender/             versioned .blend files (v01, v02, …)
├── 02_exports/             FBX / OBJ / GLB exports (later sections)
├── 03_textures/            metal / wood / grip / magazine / baked maps
├── 04_renders/             viewport tests, clay renders, finals
└── 05_mcp_prompts/         every LLM/MCP prompt + executor scripts per section
```

## Naming conventions

```
REF_   reference image
GUIDE_ guide object (non-renderable)
BLK_   blockout part
AK_    final model part
MAT_   material
CTRL_  control / helper
LOD_   level of detail
```

## How to reproduce a section

Each section is a single Blender Python script you can run headless:

```bash
# Section 1 — project setup
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python 05_mcp_prompts/section1_executor.py

# Section 2 — blockout (loads v01, saves v02)
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python 05_mcp_prompts/section2/section2_executor.py

# Section 3 — major parts (loads v02, saves v03)
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python 05_mcp_prompts/section3/section3_executor.py

# Section 4 — minor exterior details (loads v03, saves v04)
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python 05_mcp_prompts/section4/section4_executor.py

# Section 5 — UV / materials / texture-workflow prep (loads v04, saves v05)
AK47_PROJECT_ROOT="$(pwd)" \
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python 05_mcp_prompts/section5/section5_executor.py

# Section 6 — final texture / lookdev (loads v05, saves v06)
AK47_PROJECT_ROOT="$(pwd)" \
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python 05_mcp_prompts/section6/section6_executor.py

# Section 7 — final scene / renders / turntable / export (loads v06, saves v07)
AK47_PROJECT_ROOT="$(pwd)" \
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python 05_mcp_prompts/section7/section7_executor.py
# Then render finals + turntable + exports against the saved v07:
AK47_PROJECT_ROOT="$(pwd)" \
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  01_blender/v07_final_scene_export.blend \
  --python 05_mcp_prompts/section7/section7_render_finals.py
AK47_PROJECT_ROOT="$(pwd)" \
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  01_blender/v07_final_scene_export.blend \
  --python 05_mcp_prompts/section7/section7_render_turntable.py
AK47_PROJECT_ROOT="$(pwd)" \
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  01_blender/v07_final_scene_export.blend \
  --python 05_mcp_prompts/section7/section7_export.py

# Section 8 — final delivery packaging + archive (no Blender needed)
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section8/section8_executor.py
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section8/section8_archive.py
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section8/section8_verify.py

# Section 9 — post-delivery / portfolio / retrospective (no Blender needed)
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section9/section9_executor.py
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section9/section9_archive.py
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section9/section9_verify.py

# Section 10 — advanced presentation pack (no Blender needed)
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section10/section10_executor.py
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section10/section10_archive.py
AK47_PROJECT_ROOT="$(pwd)" python 05_mcp_prompts/section10/section10_verify.py
```

Each section also has a `section*_verify.py` that asserts the deliverables
are present, and a `section*_render_*.py` that produces a clay preview into
`04_renders/`.

## License

The Blender file and Python scripts in this repo are © the project author and
released under the MIT license unless noted otherwise. Reference images placed
under `00_references/` may be derivatives of third-party photographs and are
included for personal modelling reference only.
