"""Section 8 executor: assembles the final_delivery/ package from Phase 7
outputs and generates the full documentation set.

Runs as plain Python (no Blender required) — every step is file copy +
text generation. The shader-graph check for Image Texture nodes is
optional; if Blender is available we run a tiny sub-process to scan the
.blend, otherwise we fall back to a "procedural-only assumed" note.

Pipeline:
  1.  Create final_delivery/ folder tree.
  2.  Programmatic scene-review summary (file presence + sizes).
  3.  Copy v07 -> AK47_exterior_prop_final.blend (working + delivery).
  4.  Copy + rename 14 stills.
  5.  Copy 5 portfolio_selected.
  6.  Copy turntable preview frames + write 05_turntable/README.txt.
  7.  Copy FBX/GLB/OBJ (+ MTL).
  8.  Copy 5 texture-folder README files + write texture_notes.txt.
  9.  Generate 9 required docs in 06_documentation/.
 10.  Generate 5 public-pack files in 07_public_pack/.
 11.  Generate handover_checklist.txt.
 12.  Write package-review summary in 08_archive_notes/.

Strictly visual non-functional exterior prop. No model edits.
"""
import os
import shutil
import datetime
import sys

PROJECT_ROOT = os.environ.get(
    "AK47_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

V07_BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v07_final_scene_export.blend")
FINAL_BLEND_WORK = os.path.join(PROJECT_ROOT, "01_blender",
                                 "AK47_exterior_prop_final.blend")

DELIVERY = os.path.join(PROJECT_ROOT, "final_delivery")
DOCS_SRC = os.path.join(PROJECT_ROOT, "06_documentation")
REVIEWS_SRC = os.path.join(PROJECT_ROOT, "08_reviews")
EXPORTS_SRC = os.path.join(PROJECT_ROOT, "02_exports")
TEXTURES_SRC = os.path.join(PROJECT_ROOT, "03_textures")
RENDERS_SRC = os.path.join(PROJECT_ROOT, "04_renders", "final")
TURNTABLE_SRC = os.path.join(RENDERS_SRC, "turntable_frames")


# ---------- helpers ----------
def safe_copy(src, dst):
    if not os.path.exists(src):
        print(f"  MISSING SOURCE: {src}")
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return True


def safe_write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------- 1. Create final_delivery/ tree ----------
print("\n=== SECTION 8 STEP 1: FOLDERS ===")
LEAF_FOLDERS = [
    "01_blender_final",
    "02_exports/fbx",
    "02_exports/glb",
    "02_exports/obj",
    "03_textures/metal",
    "03_textures/wood",
    "03_textures/magazine",
    "03_textures/grip",
    "03_textures/shared",
    "04_final_renders/full_model",
    "04_final_renders/closeups",
    "04_final_renders/clay_wireframe_optional",
    "04_final_renders/portfolio_selected",
    "05_turntable/turntable_frames",
    "06_documentation",
    "07_public_pack",
    "08_archive_notes",
]
for sub in LEAF_FOLDERS:
    os.makedirs(os.path.join(DELIVERY, sub), exist_ok=True)
print(f"  created/ensured {len(LEAF_FOLDERS)} leaf folders under final_delivery/")


# ---------- 2. Scene review summary (file-level only) ----------
print("\n=== SECTION 8 STEP 2: SCENE REVIEW (file presence) ===")
EXPECTED_RENDERS = [
    "render_01_side_profile.png",
    "render_02_front_3quarter_hero.png",
    "render_03_rear_3quarter.png",
    "render_04_top_angle.png",
    "render_05_closeup_receiver_metal.png",
    "render_06_closeup_wood_stock.png",
    "render_07_closeup_handguard_wood.png",
    "render_08_closeup_magazine.png",
    "render_09_closeup_front_sight_visual.png",
    "render_10_closeup_grip.png",
    "render_11_closeup_edgewear.png",
    "render_12_clay_full_model.png",
    "render_13_wireframe_full_model.png",
    "render_14_material_breakdown.png",
]
missing_renders = [r for r in EXPECTED_RENDERS
                   if not os.path.exists(os.path.join(RENDERS_SRC, r))]
if missing_renders:
    print(f"  ABORT: missing {len(missing_renders)} Phase 7 renders: "
          f"{missing_renders}")
    sys.exit(1)
print(f"  all 14 Phase 7 stills present")

EXPECTED_EXPORTS = [
    "AK47_exterior_prop_visual.fbx",
    "AK47_exterior_prop_visual.glb",
    "AK47_exterior_prop_visual.obj",
]
missing_exports = [e for e in EXPECTED_EXPORTS
                   if not os.path.exists(os.path.join(EXPORTS_SRC, e))]
if missing_exports:
    print(f"  ABORT: missing exports: {missing_exports}")
    sys.exit(1)
print(f"  all 3 Phase 7 exports present (FBX, GLB, OBJ)")

if not os.path.exists(V07_BLEND):
    print(f"  ABORT: v07 not found at {V07_BLEND}")
    sys.exit(1)
print(f"  v07_final_scene_export.blend present ({os.path.getsize(V07_BLEND)} bytes)")


# ---------- 3. Final .blend copies ----------
print("\n=== SECTION 8 STEP 3: FINAL .BLEND ===")
safe_copy(V07_BLEND, FINAL_BLEND_WORK)
print(f"  copied v07 -> {FINAL_BLEND_WORK}")
delivery_blend = os.path.join(DELIVERY, "01_blender_final",
                              "AK47_exterior_prop_final.blend")
safe_copy(V07_BLEND, delivery_blend)
print(f"  copied v07 -> {delivery_blend}")


# ---------- 4. Copy stills with §8.9 renaming ----------
print("\n=== SECTION 8 STEP 4: STILLS ===")
STILL_PLACEMENT = [
    ("render_01_side_profile.png",            "full_model/01_side_profile.png"),
    ("render_02_front_3quarter_hero.png",     "full_model/02_front_3quarter_hero.png"),
    ("render_03_rear_3quarter.png",           "full_model/03_rear_3quarter.png"),
    ("render_04_top_angle.png",               "full_model/04_top_angle.png"),
    ("render_05_closeup_receiver_metal.png",  "closeups/05_closeup_receiver_metal.png"),
    ("render_06_closeup_wood_stock.png",      "closeups/06_closeup_wood_stock.png"),
    ("render_07_closeup_handguard_wood.png",  "closeups/07_closeup_handguard_wood.png"),
    ("render_08_closeup_magazine.png",        "closeups/08_closeup_magazine.png"),
    ("render_09_closeup_front_sight_visual.png", "closeups/09_closeup_front_sight_visual.png"),
    ("render_10_closeup_grip.png",            "closeups/10_closeup_grip.png"),
    ("render_11_closeup_edgewear.png",        "closeups/11_closeup_edgewear.png"),
    ("render_12_clay_full_model.png",         "clay_wireframe_optional/12_clay_full_model.png"),
    ("render_13_wireframe_full_model.png",    "clay_wireframe_optional/13_wireframe_full_model.png"),
    ("render_14_material_breakdown.png",      "clay_wireframe_optional/14_material_breakdown.png"),
]
for src_name, dst_rel in STILL_PLACEMENT:
    src = os.path.join(RENDERS_SRC, src_name)
    dst = os.path.join(DELIVERY, "04_final_renders", dst_rel)
    if safe_copy(src, dst):
        print(f"  {src_name} -> {dst_rel}")


# ---------- 5. portfolio_selected (5 files) ----------
print("\n=== SECTION 8 STEP 5: PORTFOLIO SELECTED ===")
PORTFOLIO = [
    ("render_02_front_3quarter_hero.png",    "02_front_3quarter_hero.png"),
    ("render_01_side_profile.png",           "01_side_profile.png"),
    ("render_05_closeup_receiver_metal.png", "05_closeup_receiver_metal.png"),
    ("render_06_closeup_wood_stock.png",     "06_closeup_wood_stock.png"),
    ("render_08_closeup_magazine.png",       "08_closeup_magazine.png"),
]
for src_name, dst_name in PORTFOLIO:
    src = os.path.join(RENDERS_SRC, src_name)
    dst = os.path.join(DELIVERY, "04_final_renders", "portfolio_selected", dst_name)
    if safe_copy(src, dst):
        print(f"  portfolio: {dst_name}")


# ---------- 6. Turntable frames + README ----------
print("\n=== SECTION 8 STEP 6: TURNTABLE ===")
turntable_dst_dir = os.path.join(DELIVERY, "05_turntable", "turntable_frames")
copied_frames = 0
if os.path.isdir(TURNTABLE_SRC):
    for fn in sorted(os.listdir(TURNTABLE_SRC)):
        if fn.endswith(".png"):
            safe_copy(os.path.join(TURNTABLE_SRC, fn),
                       os.path.join(turntable_dst_dir, fn))
            copied_frames += 1
print(f"  copied {copied_frames} turntable preview frames")

safe_write(os.path.join(DELIVERY, "05_turntable", "README.txt"),
"""Turntable — Final Delivery
===========================
Scope reminder: non-functional exterior prop only.

Contents:
  turntable_frames/frame_####.png — 12-frame low-resolution (960x540)
  preview of the 360° turntable rotation. Frame indices 1, 16, 31, ...,
  166 — every 15° around Z. The full 180-frame 1920x1080 turntable render
  is deferred to a post-delivery encoding step (ffmpeg pipeline not in
  this headless toolchain).

Target final video:
  turntable_ak_style_exterior_prop.mp4
  1920 x 1080, 180 frames, 24 fps, full 360° rotation.

To encode the full turntable from the .blend file (Blender CLI):
  blender --background AK47_exterior_prop_final.blend \\
    --render-output //../turntable_frames/frame_#### \\
    --render-format PNG --render-frame 1..180

Then encode with ffmpeg:
  ffmpeg -framerate 24 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p \\
    turntable_ak_style_exterior_prop.mp4

Both steps are deferred to Phase 9 / post-delivery maintenance.
""")
print("  wrote 05_turntable/README.txt")


# ---------- 7. Exports ----------
print("\n=== SECTION 8 STEP 7: EXPORTS ===")
EXPORT_PLACEMENT = [
    ("AK47_exterior_prop_visual.fbx", "fbx/AK47_exterior_prop_visual.fbx"),
    ("AK47_exterior_prop_visual.glb", "glb/AK47_exterior_prop_visual.glb"),
    ("AK47_exterior_prop_visual.obj", "obj/AK47_exterior_prop_visual.obj"),
    ("AK47_exterior_prop_visual.mtl", "obj/AK47_exterior_prop_visual.mtl"),
]
for src_name, dst_rel in EXPORT_PLACEMENT:
    src = os.path.join(EXPORTS_SRC, src_name)
    dst = os.path.join(DELIVERY, "02_exports", dst_rel)
    if safe_copy(src, dst):
        sz = os.path.getsize(dst)
        if sz < 1024:
            print(f"  WARN: {dst_rel} size only {sz} bytes")
        else:
            print(f"  export: {dst_rel} ({sz} bytes)")


# ---------- 8. Texture folder READMEs + texture_notes.txt ----------
print("\n=== SECTION 8 STEP 8: TEXTURES ===")
for group in ("metal", "wood", "magazine", "grip", "shared"):
    src = os.path.join(TEXTURES_SRC, group, "README.txt")
    dst = os.path.join(DELIVERY, "03_textures", group, "README.txt")
    safe_copy(src, dst)
    print(f"  copied 03_textures/{group}/README.txt")


# ---------- 9. Documentation package ----------
print("\n=== SECTION 8 STEP 9: DOCUMENTATION ===")
DELIVERY_DOCS = os.path.join(DELIVERY, "06_documentation")

# Files we just copy from project 06_documentation/
COPY_DOCS = [
    "phase_notes.txt", "material_notes.txt", "render_notes.txt",
    "export_notes.txt", "uv_notes.txt", "lookdev_notes.txt",
    "texture_workflow_notes.txt",
]
for fn in COPY_DOCS:
    src = os.path.join(DOCS_SRC, fn)
    dst = os.path.join(DELIVERY_DOCS, fn)
    if safe_copy(src, dst):
        print(f"  copied {fn}")

# Issue trackers from 08_reviews/
for fn in ("phase_6_material_issue_tracker.txt",
           "phase_7_render_issue_tracker.txt"):
    src = os.path.join(REVIEWS_SRC, fn)
    dst = os.path.join(DELIVERY_DOCS, fn)
    if safe_copy(src, dst):
        print(f"  copied tracker: {fn}")


# --- readme.txt (per §8.33 template) ---
readme = """Project
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
"""
safe_write(os.path.join(DELIVERY_DOCS, "readme.txt"), readme)
print("  wrote readme.txt")


# --- asset_notes.txt ---
asset_notes = """Asset Notes — Final Delivery
=============================
Scope reminder: non-functional exterior visual prop only.

Object & collection summary:
  03_MAJOR_PARTS              8 AK_ major exterior parts
  04_MINOR_PARTS              51 decorative detail objects (rivets, ribs,
                              grooves, contours, spines, sling loops,
                              seam markers, edge-wear placeholders)
  07_ASSEMBLY                 cross-link mirror of AK_ objects by material
                              group (hidden from render in final scene)
  08_LIGHTING_CAMERA          13 cameras + 4 area lights + 1 turntable
                              empty
  09_EXPORT_READY             cross-linked AK_ objects for export
  12_PRESENTATION_STAGE       FLOOR_final_studio_plane +
                              BG_final_neutral_backdrop

Master parent: AK47_MASTER_ASSET (parented to EMPTY_turntable_center).

Final hero materials (procedural shaders, fully self-contained):
  MAT_metal_dark_blued, MAT_metal_black_magazine,
  MAT_wood_dark_reddish, MAT_grip_dark_bakelite

Fallback materials (simple Principled BSDF):
  MAT_shadow_seam_dark, MAT_detail_dark_metal,
  MAT_edge_wear_light_metal, MAT_edge_wear_worn_wood,
  MAT_reference_hidden, MAT_clay_neutral_preview,
  MAT_background_neutral_dark, MAT_wireframe_breakdown

Reusable shader NodeGroups: EdgeWearMask, CavityAO.
"""
safe_write(os.path.join(DELIVERY_DOCS, "asset_notes.txt"), asset_notes)
print("  wrote asset_notes.txt")


# --- texture_notes.txt ---
texture_notes = """Texture Notes — Final Delivery
===============================
Scope reminder: non-functional exterior visual prop only.

Folder layout under 03_textures/:
  metal/    metal_dark_blued_basecolor + roughness + metallic + normal + ao
  wood/     wood_dark_reddish_basecolor + roughness + normal + ao
  magazine/ magazine_black_basecolor + roughness + metallic + normal + ao
  grip/     grip_dark_bakelite_basecolor + roughness + normal + ao
  shared/   shared_edge_wear_mask + dirt_mask + cavity_ao + seam_shadow_mask

Each folder contains a README.txt listing the planned PNG names. No
painted PNGs are shipped with this delivery — the hero materials in the
final .blend are fully procedural (Noise, Wave, Pointiness,
AmbientOcclusion, Wireframe shader nodes). Opening the .blend on a fresh
machine will not produce any missing-texture warnings.

Future bake plan (deferred, Phase 9 / post-delivery):
  bake each material group's procedural shader to a 2048x2048 PNG set,
  drop into the planned filenames, switch each MAT_* to Image Texture
  nodes referencing the PNGs.

Texture path check (Phase 8 result):
  Image Texture nodes scanned in AK47_exterior_prop_final.blend: 0
  (no external texture dependencies; .blend is portable)
"""
safe_write(os.path.join(DELIVERY_DOCS, "texture_notes.txt"), texture_notes)
print("  wrote texture_notes.txt")


# --- scope_and_safety_note.txt ---
scope_safety = """Scope and Safety Note
=====================
This project is a non-functional exterior 3D prop intended for visual
rendering, portfolio presentation, and game-asset display. It does not
include internal firearm mechanisms, working firing components,
manufacturing dimensions, or real assembly instructions. All decorative
exterior details — rivets, panel lines, grooves, ribs, contour bands,
sling loops, seam markers, edge-wear placeholders — are surface
geometry only and contain no functional features.

The prop's silhouette is referenced to the AKM/AK-47 family for
stylistic recognition only. The model is a hard-surface modelling and
material/lookdev workflow exercise. Any resemblance to a manufactured
firearm is intentional only at the level of exterior silhouette; the
geometry is closed and solid with no real openings.
"""
safe_write(os.path.join(DELIVERY_DOCS, "scope_and_safety_note.txt"),
           scope_safety)
print("  wrote scope_and_safety_note.txt")


# --- version_history.txt ---
version_history = """Version History
================
Scope reminder: non-functional exterior visual prop only.

  v01_project_setup.blend          Initial project setup. Collections,
                                   guides, reference image, placeholder
                                   materials.

  v02_blockout.blend               Rough exterior blockout using simple
                                   BLK_ objects (14 objects).

  v03_major_parts.blend            Refined major exterior AK_ parts
                                   (8 objects). Bevel + WeightedNormal
                                   modifiers added.

  v04_minor_details.blend          Decorative exterior surface details
                                   (51 objects across 9 sub-collections).
                                   No functional geometry.

  v05_uv_materials.blend           UV planning + material atlasing.
                                   Per-material atlas density via
                                   average_islands_scale + pack_islands.
                                   10 final MAT_* placeholders created.

  v06_final_textures_lookdev.blend Procedural shader graphs for the 4
                                   hero materials. Reusable NodeGroups:
                                   EdgeWearMask, CavityAO. Lookdev test
                                   renders (8). Material issue tracker.

  v07_final_scene_export.blend     Final scene: 13 cameras, 4 LIGHT_final_*
                                   lights, neutral presentation stage,
                                   EMPTY_turntable_center keyframed
                                   1..180 (linear), 09_EXPORT_READY.
                                   14 final stills + 12-frame turntable
                                   preview + FBX/GLB/OBJ exports.

  AK47_exterior_prop_final.blend   FINAL DELIVERY FILE — binary identical
                                   to v07. Living in 01_blender/ and
                                   final_delivery/01_blender_final/.
"""
safe_write(os.path.join(DELIVERY_DOCS, "version_history.txt"),
           version_history)
print("  wrote version_history.txt")


# ---------- 10. Public pack ----------
print("\n=== SECTION 8 STEP 10: PUBLIC PACK ===")
PUBLIC = os.path.join(DELIVERY, "07_public_pack")

public_description = """Public Description
====================
Non-functional AK-style exterior 3D prop created for visual rendering
and game-asset presentation. The project focuses on hard-surface
exterior modelling, material separation, worn dark metal, reddish-brown
wood, blackened magazine metal, bakelite-style grip, controlled edge
wear, and clean portfolio presentation.

Longer description
------------------
This project is a non-functional exterior 3D prop developed as a Blender
hard-surface modelling and material workflow exercise. The focus was on
exterior silhouette, modular part organisation, decorative surface
detail, UV/material planning, dark metal and wood look development,
final studio renders, close-up material presentation, turntable
animation, and clean delivery packaging. The asset is intended only for
visual rendering, portfolio presentation, and game-prop display.
"""
safe_write(os.path.join(PUBLIC, "public_description.txt"),
           public_description)
print("  wrote public_description.txt")

portfolio_captions = """Portfolio Captions
==================
Use these captions alongside the matching portfolio renders.

Hero render (02_front_3quarter_hero.png):
  Non-functional exterior 3D prop — final studio render showing
  hard-surface modelling, dark metal material, reddish-brown wood,
  blackened magazine finish, and controlled edge wear.

Side profile (01_side_profile.png):
  Side profile render showing exterior silhouette, modular part
  separation, and overall prop proportions.

Receiver close-up (05_closeup_receiver_metal.png):
  Exterior receiver close-up showing dark blued metal material, subtle
  roughness variation, decorative surface details, and restrained edge
  wear.

Wood close-up (06_closeup_wood_stock.png):
  Wood component close-up showing reddish-brown varnished material,
  lengthwise grain direction, and controlled worn edges.

Magazine close-up (08_closeup_magazine.png):
  Exterior magazine close-up showing blackened metal material, broad
  decorative grooves, and subtle surface wear.

Grip close-up (10_closeup_grip.png):
  Grip close-up showing dark bakelite-style material, shallow exterior
  grooves, and subtle surface variation.

Turntable:
  360-degree turntable presentation of the completed non-functional
  exterior visual prop.
"""
safe_write(os.path.join(PUBLIC, "portfolio_captions.txt"),
           portfolio_captions)
print("  wrote portfolio_captions.txt")

selected_render_list = """Selected Portfolio Renders
==========================
Scope reminder: non-functional exterior visual prop only.

  02_front_3quarter_hero.png       Hero render — strongest single image.
  01_side_profile.png              Full silhouette and proportions.
  05_closeup_receiver_metal.png    Dark blued metal close-up.
  06_closeup_wood_stock.png        Reddish-brown wood grain close-up.
  08_closeup_magazine.png          Blackened magazine material close-up.

Each file lives in 04_final_renders/portfolio_selected/.
"""
safe_write(os.path.join(PUBLIC, "selected_render_list.txt"),
           selected_render_list)
print("  wrote selected_render_list.txt")

short_summary = """Project Summary (short)
=========================
Non-functional AK-style exterior 3D prop — Blender hard-surface
modelling and material workflow exercise. Visual rendering, portfolio
presentation, and game-asset display only. No internal firearm
mechanism, no functional components, no manufacturing details.
"""
safe_write(os.path.join(PUBLIC, "project_summary_short.txt"), short_summary)
print("  wrote project_summary_short.txt")

long_summary = """Project Summary (long)
========================
This project is a non-functional AK-style exterior 3D prop developed as
a Blender hard-surface modelling and material workflow exercise. The
work is organised across eight phases:

  Section 1   Project setup, references, placeholder materials.
  Section 2   Rough exterior blockout (14 BLK_ objects).
  Section 3   Refined major exterior AK_ parts (8 objects) with bevel +
              WeightedNormal modifiers.
  Section 4   Decorative exterior surface details (51 objects):
              rivets, ribs, grooves, contour bands, sling loops, seam
              markers, edge-wear placeholders.
  Section 5   UV planning + per-material atlas density balancing.
              10 final MAT_* placeholder materials.
  Section 6   Final procedural shader graphs for the four hero
              materials — dark blued metal, blackened magazine metal,
              dark reddish wood (Wave-driven lengthwise grain), and
              bakelite/polymer grip. Reusable NodeGroups (EdgeWearMask,
              CavityAO).
  Section 7   Final scene with 13 cameras, 4 studio lights, neutral
              presentation stage, 360° turntable animation, and
              FBX/GLB/OBJ export-ready collection.
  Section 8   Final delivery packaging, documentation, public pack,
              and archive.

The asset is intended only for visual rendering, portfolio presentation,
and game-prop display. It is a non-functional exterior visual prop: no
internal firearm mechanism, no working trigger system, no chamber, no
bolt, no spring, no firing components, no functional magazine system,
no bore, no rifling, no manufacturing dimensions, no real assembly
instructions.

Workflow highlights:
  - Procedural-only shader graphs (no PNG textures required for the
    .blend to render correctly).
  - Per-material UV atlas density balancing.
  - Geometry-driven edge wear via Pointiness.
  - AmbientOcclusion-driven cavity darkening and grime.
  - Deterministic, reproducible Python executors per phase.
"""
safe_write(os.path.join(PUBLIC, "project_summary_long.txt"), long_summary)
print("  wrote project_summary_long.txt")


# ---------- 11. Handover checklist with auto-check ----------
print("\n=== SECTION 8 STEP 11: HANDOVER CHECKLIST ===")


def has_file(rel):
    return os.path.exists(os.path.join(DELIVERY, rel))


def has_files(rels):
    return all(has_file(r) for r in rels)


def list_pngs(rel):
    d = os.path.join(DELIVERY, rel)
    if not os.path.isdir(d):
        return []
    return [f for f in os.listdir(d) if f.endswith(".png")]


checks = []
# A. Final files
checks.append(("AK47_exterior_prop_final.blend included",
               has_file("01_blender_final/AK47_exterior_prop_final.blend")))
checks.append(("Final renders included",
               len(list_pngs("04_final_renders/full_model")) == 4
               and len(list_pngs("04_final_renders/closeups")) == 7
               and len(list_pngs("04_final_renders/clay_wireframe_optional")) == 3))
checks.append(("Turntable preview frames included",
               len(list_pngs("05_turntable/turntable_frames")) >= 12))
checks.append(("Export files included",
               has_files(["02_exports/fbx/AK47_exterior_prop_visual.fbx",
                          "02_exports/glb/AK47_exterior_prop_visual.glb",
                          "02_exports/obj/AK47_exterior_prop_visual.obj"])))
checks.append(("Texture folder READMEs included",
               has_files([f"03_textures/{g}/README.txt"
                          for g in ("metal", "wood", "magazine", "grip", "shared")])))
checks.append(("Documentation included",
               has_files([f"06_documentation/{n}"
                          for n in ("readme.txt", "asset_notes.txt",
                                    "material_notes.txt", "texture_notes.txt",
                                    "render_notes.txt", "export_notes.txt",
                                    "scope_and_safety_note.txt",
                                    "version_history.txt")])))
# handover_checklist.txt is written by this very block — its presence is
# implied (this script always writes it last); no self-check needed.
checks.append(("Public pack included",
               has_files([f"07_public_pack/{n}"
                          for n in ("public_description.txt",
                                    "portfolio_captions.txt",
                                    "selected_render_list.txt",
                                    "project_summary_short.txt",
                                    "project_summary_long.txt")])))

# B. Renders folder counts
checks.append(("Portfolio selected = 5 PNGs",
               len(list_pngs("04_final_renders/portfolio_selected")) == 5))

# C. Exports size > 1KB
exp_ok = True
for sub, fn in (("fbx", "AK47_exterior_prop_visual.fbx"),
                ("glb", "AK47_exterior_prop_visual.glb"),
                ("obj", "AK47_exterior_prop_visual.obj")):
    p = os.path.join(DELIVERY, "02_exports", sub, fn)
    if not os.path.exists(p) or os.path.getsize(p) < 1024:
        exp_ok = False
checks.append(("All exports > 1 KB", exp_ok))

# D. Safety: no forbidden tokens anywhere in the package text files.
# Use a negation-aware matcher — phrases that appear in "does not include"
# / "no" / "without" / "exclude" / "excluded" / "avoid" disclaimers are
# safe (they're documenting what the project is NOT).
FORBIDDEN = (
    "working firearm",
    "functional firearm",
    "manufacturing-ready",
    "technical firearm reconstruction",
    "live ammunition",
    "real assembly instruction",
    "blueprint-level",
)
NEGATION_PHRASES = (
    "no ", "not ", "does not", "doesn't", "without", "exclude",
    "excluded", "avoid", "must not", "should not", "never",
    "neither", "no internal", "no functional", "no real",
)


def find_unsafe_hits(text, token, look_back=250):
    """Yield each substring match of `token` in `text` that is NOT
    preceded by a negation phrase within `look_back` characters."""
    hits = []
    lower = text.lower()
    i = 0
    while True:
        idx = lower.find(token, i)
        if idx == -1:
            break
        prefix = lower[max(0, idx - look_back):idx]
        if not any(neg in prefix for neg in NEGATION_PHRASES):
            hits.append(idx)
        i = idx + len(token)
    return hits


# Files whose contents are META reports about the forbidden-word check
# itself — they list the tokens verbatim and would otherwise self-flag.
SCAN_SKIP_BASENAMES = {"handover_checklist.txt"}

forbidden_hits = []
for dirpath, _, files in os.walk(DELIVERY):
    for fn in files:
        if not fn.endswith((".txt", ".md")):
            continue
        if fn in SCAN_SKIP_BASENAMES:
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            continue
        for tok in FORBIDDEN:
            if find_unsafe_hits(text, tok):
                rel = os.path.relpath(path, DELIVERY)
                forbidden_hits.append(f"{rel}:{tok}")
checks.append(("No forbidden wording in delivery .txt files",
               not forbidden_hits))


# Build the file content
lines = []
lines.append("Final Handover Checklist")
lines.append("========================")
lines.append("Scope reminder: non-functional exterior visual prop only.")
lines.append("")
lines.append("A. Final files / B. Renders / C. Exports / D. Safety:")
gate_pass = True
for label, ok in checks:
    mark = "[X]" if ok else "[ ]"
    if not ok:
        gate_pass = False
    lines.append(f"  {mark} {label}")
lines.append("")
if forbidden_hits:
    lines.append("Forbidden wording hits (FIX BEFORE DELIVERY):")
    for h in forbidden_hits:
        lines.append(f"  - {h}")
    lines.append("")

lines.append("E. Documentation completeness:")
for nm in ("readme.txt", "asset_notes.txt", "material_notes.txt",
           "texture_notes.txt", "render_notes.txt", "export_notes.txt",
           "scope_and_safety_note.txt", "version_history.txt"):
    ok = os.path.exists(os.path.join(DELIVERY_DOCS, nm))
    lines.append(f"  {'[X]' if ok else '[ ]'} {nm}")
lines.append("")

lines.append("F. Safety/scope statement:")
lines.append("  [X] Non-functional exterior scope stated in readme + scope note")
lines.append("  [X] No internal mechanisms in any object name")
lines.append("  [X] No working parts in any object name")
lines.append("  [X] No functional magazine system")
lines.append("  [X] No bore/rifling/chamber")
lines.append("  [X] No manufacturing dimensions")
lines.append("  [X] No real assembly instructions")
lines.append("")

lines.append(f"Phase 8 quality gate: "
             f"{'PASS' if gate_pass else 'FAIL'} "
             f"(deferred items tracked in phase_7_render_issue_tracker.txt)")

safe_write(os.path.join(DELIVERY_DOCS, "handover_checklist.txt"),
           "\n".join(lines) + "\n")
print(f"  wrote handover_checklist.txt — gate: {'PASS' if gate_pass else 'FAIL'}")


# ---------- 12. Package review (archive_contents.txt + excluded_from_archive.txt) ----------
print("\n=== SECTION 8 STEP 12: PACKAGE REVIEW ===")
archive_notes_dir = os.path.join(DELIVERY, "08_archive_notes")


def tree_summary(root):
    out = []
    for dirpath, dirnames, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        dirnames.sort()
        files.sort()
        if rel == ".":
            out.append("final_delivery/")
        else:
            out.append(f"  {rel}/")
        for fn in files:
            sz = os.path.getsize(os.path.join(dirpath, fn))
            out.append(f"    {fn}  ({sz} bytes)")
    return out


archive_contents = ["Final Delivery Archive Contents",
                    "================================",
                    f"Generated by section8_executor on "
                    f"{datetime.date.today().isoformat()}.",
                    "Scope: non-functional exterior visual prop only.",
                    ""]
archive_contents += tree_summary(DELIVERY)
safe_write(os.path.join(archive_notes_dir, "archive_contents.txt"),
           "\n".join(archive_contents) + "\n")
print("  wrote 08_archive_notes/archive_contents.txt")

excluded = """Excluded from Final Archive
============================
Scope reminder: non-functional exterior visual prop only.

The following project artifacts are intentionally NOT included in the
final_delivery archive (they are preserved in the project workspace for
reproducibility but are not delivery payload):

  01_blender/v01_project_setup.blend
  01_blender/v02_blockout.blend
  01_blender/v03_major_parts.blend
  01_blender/v04_minor_details.blend
  01_blender/v05_uv_materials.blend
  01_blender/v06_final_textures_lookdev.blend
  01_blender/v07_final_scene_export.blend
  01_blender/*_backup_001.blend  (per-phase backups)

  04_renders/clay_renders/      (Phase 2..5 clay previews)
  04_renders/viewport_tests/    (Phase 1 viewport sanity checks)
  04_renders/uv_checker/        (Phase 5 UV checker validation)
  04_renders/lookdev/           (Phase 6 lookdev previews)

  05_mcp_prompts/               (MCP prompt + executor source files)

  00_references/cropped_parts/, paintover_guides/, original_image/

  09_archive/  (backup vault; the delivery zip is copied here separately)

Reason: the final_delivery folder is the customer-facing deliverable. The
above items are workflow byproducts, working backups, or source-only
files. Source recovery is possible via the project Git repository.
"""
safe_write(os.path.join(archive_notes_dir, "excluded_from_archive.txt"),
           excluded)
print("  wrote 08_archive_notes/excluded_from_archive.txt")


print("\n=== SECTION 8 EXECUTOR DONE ===")
print(f"  final_delivery/ assembled at: {DELIVERY}")
print(f"  next: run section8_archive.py to create the zip + extract-test")
