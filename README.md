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
- ⬜ Section 3 — Major parts (planned)
- ⬜ Section 4 — Detail pass (planned)
- ⬜ Section 5 — Materials (planned)
- ⬜ Section 6 — Final assembly (planned)

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
```

Each section also has a `section*_verify.py` that asserts the deliverables
are present, and a `section*_render_*.py` that produces a clay preview into
`04_renders/`.

## License

The Blender file and Python scripts in this repo are © the project author and
released under the MIT license unless noted otherwise. Reference images placed
under `00_references/` may be derivatives of third-party photographs and are
included for personal modelling reference only.
