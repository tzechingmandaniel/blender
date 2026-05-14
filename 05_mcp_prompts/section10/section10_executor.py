"""Section 10 executor: builds the advanced_presentation_pack/ folder
with all 17 documentation files for public portfolio presentation.

Plain Python — no Blender, no rendering. Idempotent.
"""
import os
import datetime

PROJECT_ROOT = os.environ.get(
    "AK47_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

PACK = os.path.join(PROJECT_ROOT, "advanced_presentation_pack")
DELIVERY_REL = "final_delivery"
POST_REL = "post_delivery"

SCOPE = ("Scope reminder: non-functional exterior visual prop only. "
         "No internal mechanism, no working trigger, no chamber/bolt/"
         "spring, no functional magazine, no bore, no rifling, no "
         "manufacturing dimensions, no real assembly instructions.")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {os.path.relpath(path, PROJECT_ROOT)}")


# ---------- 1. Folder tree ----------
print("\n=== SECTION 10 STEP 1: FOLDERS ===")
LEAF_FOLDERS = [
    "01_portfolio_page",
    "02_website_case_study",
    "03_artstation_style_layout",
    "04_public_social_pack",
    "05_image_sequence",
    "06_thumbnail_and_cover",
    "07_process_breakdown",
    "08_submission_pack",
    "09_reusable_presentation_template",
    "10_publication_checklist",
    "11_archive",
]
for sub in LEAF_FOLDERS:
    os.makedirs(os.path.join(PACK, sub), exist_ok=True)
print(f"  created/ensured {len(LEAF_FOLDERS)} leaf folders under "
      f"advanced_presentation_pack/")


# ---------- 2. Portfolio page (§10.4) ----------
print("\n=== SECTION 10 STEP 2: PORTFOLIO PAGE ===")
portfolio_page = f"""Portfolio Page Plan
====================
{SCOPE}

1. TITLE
--------
Non-functional AK-style Exterior 3D Prop

2. HERO IMAGE
-------------
final_delivery/04_final_renders/full_model/02_front_3quarter_hero.png

3. ONE-SENTENCE SUMMARY
-----------------------
A non-functional exterior 3D prop created for hard-surface modelling,
material lookdev, and portfolio presentation.

4. PROJECT FOCUS
----------------
  - exterior silhouette
  - modular asset organisation
  - material separation
  - worn metal and wood lookdev
  - final render and turntable presentation

5. FINAL RENDERS (recommended order)
------------------------------------
  - hero render        (02_front_3quarter_hero.png)
  - side profile       (01_side_profile.png)
  - rear 3/4           (03_rear_3quarter.png)
  - top angle          (04_top_angle.png)
  - receiver close-up  (05_closeup_receiver_metal.png)
  - wood close-up      (06_closeup_wood_stock.png)
  - magazine close-up  (08_closeup_magazine.png)
  - grip close-up      (10_closeup_grip.png)

6. PROCESS SUMMARY (4 steps)
----------------------------
  1. Blockout
  2. Major exterior forms
  3. Decorative surface details
  4. Materials and final renders

7. TOOLS
--------
  - Blender 5.x
  - Blender MCP (structured prompt-based workflow)
  - Image references (exterior silhouette only)
  - Procedural shader / material workflow

8. SCOPE NOTE
-------------
This is a non-functional exterior visual prop only. It does not include
internal firearm mechanisms, working firing components, manufacturing
dimensions, or real assembly instructions.
"""
write(os.path.join(PACK, "01_portfolio_page", "portfolio_page_plan.txt"),
      portfolio_page)


# ---------- 3. Website case study (§10.6) + long summary (§10.15) ----------
print("\n=== SECTION 10 STEP 3: WEBSITE CASE STUDY ===")
case_study = f"""Website Case Study Plan
========================
{SCOPE}

1. HERO SECTION
---------------
Title       : Non-functional AK-style Exterior 3D Prop
Hero image  : final_delivery/04_final_renders/full_model/02_front_3quarter_hero.png
One-line    : A non-functional exterior 3D prop created for hard-surface
              modelling, material lookdev, and portfolio presentation.

2. PROJECT OVERVIEW
-------------------
This project is a non-functional exterior 3D prop built as a Blender
hard-surface modelling and material lookdev exercise. The focus was on
silhouette, modular asset organisation, dark worn metal, reddish-brown
wood, blackened magazine material, bakelite-style grip, controlled edge
wear, and clean studio presentation.

3. GOALS
--------
  - Create a readable exterior silhouette.
  - Use modular object organisation (collection per material group).
  - Practise hard-surface modelling planning.
  - Develop dark metal / wood / grip materials.
  - Produce final studio renders and a turntable animation.

4. REFERENCE AND PLANNING
-------------------------
  - Reference collection of exterior images only.
  - Side / top / front view planning grid.
  - Material reference planning (steel + wood + bakelite).
  - Safe exterior-only scope from project setup onward.

5. WORKFLOW
-----------
  A. Project setup
  B. Blockout
  C. Major exterior forms
  D. Decorative exterior details
  E. UV and material setup
  F. Final texture / lookdev
  G. Render and turntable
  H. Packaging

6. CHALLENGES
-------------
  - Controlling proportion across the 8-phase workflow.
  - Avoiding over-detailing in Phase 4 (capped at 51 detail objects).
  - Organising files across 7 versioned .blend checkpoints.
  - Balancing materials so the 4 hero materials read distinct.
  - Keeping public wording safe in every documentation file.

7. SOLUTIONS
------------
  - Phase-based workflow with executor + verify scripts per phase.
  - Versioned .blend files preserved every checkpoint.
  - Named collections (00_REFERENCE..12_PRESENTATION_STAGE).
  - Material groups (4 hero MAT_* + 6 fallback).
  - Render and delivery checklists auto-gated by verify.py.
  - Negation-aware safety-word scanner for all .txt outputs.

8. FINAL RESULT
---------------
The final delivery package includes:
  - AK47_exterior_prop_final.blend (procedural shaders, portable)
  - 14 final still renders (4 full-model + 7 close-up + 3 breakdown)
  - 1.65 MB H.264 MP4 turntable (180 frames, 1280x720, 24 fps)
  - FBX + GLB + OBJ exports
  - 16 documentation files + 5 public-pack files
  - Handover checklist auto-gated to PASS
  - 234 MB archive zip with 246 files

9. REFLECTION
-------------
This project deepened workflow planning, hard-surface organisation,
material separation, lookdev control, render presentation, and final
packaging discipline. The reusable executor/verify/archive script trio
per phase transfers directly to any future non-functional exterior prop.

10. SCOPE NOTE
--------------
This is a non-functional exterior visual prop only. It does not include
internal mechanisms, working firing components, manufacturing dimensions,
or real assembly instructions.
"""
write(os.path.join(PACK, "02_website_case_study",
                    "website_case_study_plan.txt"), case_study)

long_summary = f"""Long Project Summary
=====================
{SCOPE}

This project is a non-functional AK-style exterior 3D prop created as a
Blender hard-surface modelling, material lookdev, and portfolio
presentation exercise. The project was structured across a phase-based
workflow, starting with project setup and reference planning, then
moving into rough blockout, major exterior part modelling, decorative
exterior surface details, UV and material preparation, final texture
and lookdev, render composition, turntable animation, and final delivery
packaging. Every phase produced a deterministic Python executor and a
verify script, so the entire pipeline can re-run end-to-end without
manual intervention.

The main focus was not to create a functional or technical model, but
to practise visual prop production: silhouette control, clean object
organisation, material separation, worn dark metal, reddish-brown wood,
blackened magazine finish, bakelite-style grip, controlled edge wear,
and clean studio presentation. The shader graphs for the four hero
materials are fully procedural (Noise + Wave + Pointiness +
AmbientOcclusion via reusable EdgeWearMask and CavityAO node groups),
which keeps the final .blend portable on any machine without external
texture files.

The final package includes the Blender scene, 14 final still renders,
close-up material renders, a 180-frame H.264 MP4 turntable animation,
FBX/GLB/OBJ exports, texture-folder READMEs, full project documentation,
issue trackers, a public-safe presentation pack, and a date-stamped
archive zip. This asset is intended only for visual rendering, portfolio
presentation, and game-asset display. It does not include internal
mechanisms, working firing components, manufacturing dimensions, or
real assembly instructions.
"""
write(os.path.join(PACK, "02_website_case_study",
                    "long_project_summary.txt"), long_summary)


# ---------- 4. ArtStation-style layout (§10.8) ----------
print("\n=== SECTION 10 STEP 4: ARTSTATION LAYOUT ===")
artstation_layout = f"""ArtStation-Style Layout
========================
{SCOPE}

1. COVER IMAGE
--------------
final_delivery/04_final_renders/full_model/02_front_3quarter_hero.png

2. SHORT TITLE + TAGLINE
------------------------
Title   : Non-functional AK-style Exterior 3D Prop
Tagline : Hard-surface exterior modelling and material lookdev study.

3. FULL MODEL IMAGE STRIP (left to right)
-----------------------------------------
  side profile        01_side_profile.png
  front 3/4 (hero)    02_front_3quarter_hero.png
  rear 3/4            03_rear_3quarter.png
  top angle           04_top_angle.png

4. MATERIAL CLOSE-UP STRIP
--------------------------
  receiver metal      05_closeup_receiver_metal.png
  wood stock          06_closeup_wood_stock.png
  handguard wood      07_closeup_handguard_wood.png
  magazine            08_closeup_magazine.png
  grip                10_closeup_grip.png

5. PROCESS BREAKDOWN STRIP
--------------------------
  blockout            (Phase 2 clay render)
  major forms         (Phase 3 clay render)
  decorative details  (Phase 4 close-ups)
  final material/look (Phase 6 lookdev close-ups)

6. TURNTABLE EMBED
------------------
final_delivery/05_turntable/turntable_ak_style_exterior_prop.mp4

7. TOOL AND WORKFLOW NOTES (bullets only)
-----------------------------------------
  - Blender 5.x (Cycles + Eevee)
  - 8-phase pipeline, executor + verify scripts per phase
  - Procedural shader graphs (no PNG textures required)
  - Reusable shader NodeGroups: EdgeWearMask, CavityAO
  - imageio-ffmpeg for headless MP4 encoding

8. SCOPE NOTE
-------------
Non-functional exterior visual prop only. No internal mechanism,
no working components, no manufacturing dimensions, no real assembly
instructions.

LAYOUT RULES
------------
  - Lead with the strongest image (cover).
  - Avoid too many text blocks.
  - Use image captions, not long paragraphs.
  - No dimensions, no technical internal diagrams, no blueprint
    overlays.
  - Safe public wording throughout.
"""
write(os.path.join(PACK, "03_artstation_style_layout",
                    "artstation_style_layout.txt"), artstation_layout)


# ---------- 5. Final image sequence (§10.10) ----------
print("\n=== SECTION 10 STEP 5: IMAGE SEQUENCE ===")
image_sequence = f"""Final Image Sequence
=====================
{SCOPE}

Ordered presentation sequence (13 shots):

  01_cover_hero          02_front_3quarter_hero.png
                         (hero front 3/4 view)

  02_side_silhouette     01_side_profile.png
                         (full silhouette + part proportions)

  03_rear_volume         03_rear_3quarter.png
                         (stock + grip + rear proportions)

  04_top_volume          04_top_angle.png
                         (model thickness + 3D volume)

  05_receiver_material   05_closeup_receiver_metal.png
                         (dark blued metal close-up)

  06_wood_material       06_closeup_wood_stock.png
                         (reddish-brown wood + lengthwise grain)

  07_handguard_material  07_closeup_handguard_wood.png
                         (handguard wood close-up)

  08_magazine_material   08_closeup_magazine.png
                         (blackened matte metal)

  09_grip_material       10_closeup_grip.png
                         (bakelite/polymer surface noise)

  10_edgewear_detail     11_closeup_edgewear.png
                         (controlled exposed-edge wear)

  11_optional_clay       12_clay_full_model.png
                         (neutral clay — modelling forms only)

  12_optional_wireframe  13_wireframe_full_model.png
                         (topology / wireframe breakdown)

  13_turntable           turntable_ak_style_exterior_prop.mp4
                         (180-frame 1280x720 turntable, 24 fps)

Files live under:
  final_delivery/04_final_renders/full_model/
  final_delivery/04_final_renders/closeups/
  final_delivery/04_final_renders/clay_wireframe_optional/
  final_delivery/05_turntable/

ORDER RULES
-----------
  1. Start with strongest hero image.
  2. Show full model before close-ups.
  3. Show close-ups by material group (metal -> wood -> magazine -> grip).
  4. Place optional clay/wireframe breakdown near the end.
  5. End with the turntable.
  6. Do not include weak renders.
  7. Do not include unsafe technical views.
"""
write(os.path.join(PACK, "05_image_sequence", "final_image_sequence.txt"),
      image_sequence)


# ---------- 6. Thumbnail and cover (§10.12) ----------
print("\n=== SECTION 10 STEP 6: THUMBNAIL + COVER ===")
thumbnail_cover = f"""Thumbnail and Cover Plan
=========================
{SCOPE}

THUMBNAIL PURPOSE
-----------------
Make people click while still representing the project accurately and
safely.

RECOMMENDED COVER
-----------------
final_delivery/04_final_renders/full_model/02_front_3quarter_hero.png

ALTERNATIVE COVER
-----------------
final_delivery/04_final_renders/full_model/01_side_profile.png
(if the hero feels too busy at thumbnail size)

THUMBNAIL CROP NOTES
--------------------
  - Focus on the full prop silhouette.
  - Show metal + wood contrast (both materials visible).
  - Avoid cutting off too much of the model on any side.
  - No overlay text if the image is strong on its own.
  - Optional small text: "Exterior 3D Prop" (bottom-left, small,
    neutral colour).

THUMBNAIL RULES
---------------
  1. Use neutral background (grey, no scene clutter).
  2. Avoid aggressive scene context.
  3. Avoid technical-diagram styling.
  4. Avoid framing that makes the prop look usable.
  5. Keep it clean and professional.
  6. Do not include dimensions or blueprint overlays.

CHECKLIST
---------
  [X] Hero render selected
  [X] Crop planned (full silhouette + material contrast)
  [X] Text-vs-no-text decision made (no overlay)
  [X] Safe context confirmed (neutral grey background)
  [X] Thumbnail readable at small size (full silhouette visible)
  [X] No technical blueprint styling
"""
write(os.path.join(PACK, "06_thumbnail_and_cover", "thumbnail_cover_plan.txt"),
      thumbnail_cover)


# ---------- 7. Short summary (§10.14) ----------
print("\n=== SECTION 10 STEP 7: SHORT SUMMARY ===")
short_summary = f"""Short Project Summary
======================
{SCOPE}

OPTION A (recommended)
----------------------
Non-functional AK-style exterior 3D prop created as a Blender
hard-surface modelling and material lookdev study. Focus areas included
exterior silhouette, modular object organisation, dark metal,
reddish-brown wood, blackened magazine material, bakelite-style grip,
controlled edge wear, studio renders, and turntable presentation.

OPTION B
--------
A non-functional exterior visual prop made for portfolio and game-asset
presentation. This project focused on hard-surface modelling workflow,
material separation, worn metal/wood lookdev, close-up render
presentation, and final delivery packaging.

OPTION C
--------
Blender exterior prop study focused on silhouette, hard-surface forms,
material lookdev, edge wear, studio rendering, and clean asset delivery.
Non-functional visual prop only.
"""
write(os.path.join(PACK, "04_public_social_pack", "short_project_summary.txt"),
      short_summary)


# ---------- 8. Social post pack (§10.17) ----------
print("\n=== SECTION 10 STEP 8: SOCIAL POST PACK ===")
social_pack = f"""Public Social Post Pack
========================
{SCOPE}

MEDIUM-LENGTH POST (~3 sentences)
---------------------------------
Finished a non-functional exterior 3D prop study in Blender, focused on
hard-surface modelling, material separation, dark worn metal, reddish-
brown wood, blackened metal finish, bakelite-style grip, edge wear,
studio renders, and turntable presentation.

This was mainly a workflow and lookdev exercise: blockout -> major forms
-> decorative exterior details -> UV/material setup -> final renders
and delivery package.

Non-functional visual prop only.

SHORT POST (~2 sentences, single line for social media)
-------------------------------------------------------
Blender hard-surface exterior prop study — focused on silhouette,
modular modelling, worn metal, wood material, edge wear, studio renders,
and turntable presentation. Non-functional visual prop only.

ONE-LINE TURNTABLE CAPTION
--------------------------
360 degree turntable of a non-functional exterior 3D prop —
hard-surface modelling, material lookdev, and studio rendering.

SAFE HASHTAG SUGGESTIONS
------------------------
  #Blender3D
  #HardSurfaceModeling
  #GameArt
  #3DProp
  #Lookdev
  #Portfolio

FORBIDDEN HASHTAGS (do NOT include)
-----------------------------------
  #firearms
  #weaponbuild
  #gunsmithing
  #blueprint
  #realweapon
  #tactical

CHECKLIST
---------
  [X] Social post written
  [X] Short version written
  [X] One-line turntable caption written
  [X] Safe hashtags selected
  [X] Forbidden hashtags listed for awareness
  [X] Non-functional wording included
"""
write(os.path.join(PACK, "04_public_social_pack", "social_post_pack.txt"),
      social_pack)


# ---------- 9. Process breakdown (§10.19) ----------
print("\n=== SECTION 10 STEP 9: PROCESS BREAKDOWN ===")
process_breakdown = f"""Process Breakdown Plan
=======================
{SCOPE}

1. REFERENCE AND SETUP
----------------------
Suggested image : project folder structure / collection outline screenshot
Caption         : Project setup focused on clean folder structure,
                  references, named collections, and non-functional
                  exterior prop scope. Eight-phase Blender workflow with
                  a Python executor + verify script per phase.

2. BLOCKOUT
-----------
Suggested image : 04_renders/clay_renders/v02_blockout_side.png
Caption         : Rough blockout used to establish exterior silhouette,
                  part separation, and 3D volume before any detail work.
                  14 BLK_ objects across the receiver, stock, handguards,
                  magazine, grip, and barrel/front-assembly groups.

3. MAJOR EXTERIOR FORMS
-----------------------
Suggested image : 04_renders/clay_renders/v03_major_parts_3quarter.png
Caption         : Major exterior parts were refined from the blockout
                  while keeping objects modular and editable. Bevel +
                  WeightedNormal modifiers applied per part.

4. DECORATIVE EXTERIOR DETAILS
------------------------------
Suggested image : 04_renders/clay_renders/v04_minor_details_3quarter.png
Caption         : 51 decorative surface details added across nine sub-
                  collections (rivets, ribs, grooves, contour bands,
                  sling loops, seam markers, edge-wear placeholders).
                  All surface-only, no functional geometry.

5. MATERIALS AND LOOKDEV
------------------------
Suggested image : 04_renders/lookdev/lookdev_closeup_metal_receiver.png
Caption         : Final lookdev focused on worn dark metal, reddish-brown
                  wood with lengthwise grain, blackened magazine material,
                  bakelite-style grip, controlled edge wear via
                  Pointiness, cavity darkening via AmbientOcclusion, and
                  subtle roughness variation via noise.

6. FINAL PRESENTATION
---------------------
Suggested image : final_delivery/04_final_renders/full_model/02_front_3quarter_hero.png
Caption         : Final presentation includes 14 studio renders, six
                  material close-ups, a 180-frame H.264 MP4 turntable
                  animation, FBX/GLB/OBJ exports, and a clean delivery
                  package with handover checklist.

PROCESS RULES
-------------
  - Keep the process short.
  - Avoid technical weapon detail.
  - Do not show internal diagrams or cutaways.
  - Do not include dimensions.
  - Focus on art workflow.
"""
write(os.path.join(PACK, "07_process_breakdown", "process_breakdown_plan.txt"),
      process_breakdown)


# ---------- 10. Submission pack (§10.21 / §10.23 / §10.24) ----------
print("\n=== SECTION 10 STEP 10: SUBMISSION PACK ===")
submission_pack = f"""Submission Pack Plan
=====================
{SCOPE}

PURPOSE
-------
Use this if you need to submit the project to a teacher, client,
reviewer, or portfolio platform.

SUBMISSION PACK CONTENTS (10 items)
-----------------------------------
  1. cover_image.png
     -> final_delivery/04_final_renders/full_model/02_front_3quarter_hero.png

  2. project_summary_short.txt
     -> advanced_presentation_pack/04_public_social_pack/short_project_summary.txt

  3. project_summary_long.txt
     -> advanced_presentation_pack/02_website_case_study/long_project_summary.txt

  4. selected_render_list.txt
     -> post_delivery/06_selected_portfolio_renders/portfolio_selection_notes.txt

  5. portfolio_captions.txt
     -> final_delivery/07_public_pack/portfolio_captions.txt

  6. final_turntable_link_or_file.txt
     -> final_delivery/05_turntable/turntable_ak_style_exterior_prop.mp4

  7. workflow_summary.txt
     -> see process_breakdown_plan.txt in this folder
        plus advanced_presentation_pack/02_website_case_study/website_case_study_plan.txt
        section 5 (Workflow)

  8. tools_used.txt
     -> advanced_presentation_pack/08_submission_pack/tools_used.txt

  9. scope_and_safety_note.txt
     -> final_delivery/06_documentation/scope_and_safety_note.txt

 10. file_inventory.txt
     -> advanced_presentation_pack/08_submission_pack/file_inventory.txt

SUBMISSION PACK RULES
---------------------
  1. Include only final selected content.
  2. Do not include all working files unless requested.
  3. Keep public-safe wording.
  4. Avoid technical-weapon language.
  5. Include a clear scope note.

CHECKLIST
---------
  [X] Cover image referenced
  [X] Short summary referenced
  [X] Long summary referenced
  [X] Selected render list referenced
  [X] Captions referenced
  [X] Turntable file referenced
  [X] Workflow summary referenced
  [X] Tools used included
  [X] Scope note referenced
  [X] File inventory included
"""
write(os.path.join(PACK, "08_submission_pack", "submission_pack_plan.txt"),
      submission_pack)


tools_used = f"""Tools Used
===========
{SCOPE}

TOOLS
-----
  - Blender 5.x       Modelling, material setup, lighting, rendering,
                      and turntable animation. Both Cycles (still
                      renders) and Eevee (turntable animation) used.

  - Blender MCP       Structured prompt-based scene organisation and
                      workflow support. Each phase has a deterministic
                      Python executor + verify script run via Blender's
                      headless --background --python interface or via
                      plain Python for documentation phases.

  - imageio-ffmpeg    Headless MP4 encoding for the turntable video
                      (Blender 5.x removed FFMPEG output from
                      image_settings, so PNG sequence + ffmpeg is the
                      working path).

  - Reference images  Exterior silhouette and material reference only.

  - Texture/material  Dark blued metal, blackened magazine metal, dark
    workflow          reddish wood (with lengthwise Wave grain), bakelite
                      grip, seam shadow material, edge-wear materials,
                      cavity AO via AmbientOcclusion node, roughness
                      variation via fine Noise. Two reusable shader
                      NodeGroups: EdgeWearMask, CavityAO.

  - Documentation     Phase plans, issue trackers (Phase 6 + Phase 7),
    workflow          render notes, export notes, lookdev notes,
                      texture-workflow notes, handover checklist,
                      version history, public pack.

SCOPE
-----
The tools were used to create a non-functional exterior visual prop
only. No internal mechanisms, manufacturing dimensions, or real
assembly instructions are included.
"""
write(os.path.join(PACK, "08_submission_pack", "tools_used.txt"), tools_used)


file_inventory = f"""File Inventory
===============
{SCOPE}

FINAL BLENDER FILE
------------------
  final_delivery/01_blender_final/AK47_exterior_prop_final.blend
  01_blender/AK47_exterior_prop_final.blend   (working copy)

FINAL RENDERS
-------------
  final_delivery/04_final_renders/full_model/                4 stills
  final_delivery/04_final_renders/closeups/                  7 stills
  final_delivery/04_final_renders/clay_wireframe_optional/   3 stills
  final_delivery/04_final_renders/portfolio_selected/        5 stills

TURNTABLE
---------
  final_delivery/05_turntable/turntable_ak_style_exterior_prop.mp4
  final_delivery/05_turntable/turntable_frames/   (12-frame preview)
  final_delivery/05_turntable/turntable_full_seq/ (180 PNG source frames;
                                                    excluded from git)

EXPORTS
-------
  final_delivery/02_exports/fbx/AK47_exterior_prop_visual.fbx
  final_delivery/02_exports/glb/AK47_exterior_prop_visual.glb
  final_delivery/02_exports/obj/AK47_exterior_prop_visual.obj
  final_delivery/02_exports/obj/AK47_exterior_prop_visual.mtl

TEXTURES (procedural shaders; READMEs only)
-------------------------------------------
  final_delivery/03_textures/metal/README.txt
  final_delivery/03_textures/wood/README.txt
  final_delivery/03_textures/magazine/README.txt
  final_delivery/03_textures/grip/README.txt
  final_delivery/03_textures/shared/README.txt

DOCUMENTATION
-------------
  final_delivery/06_documentation/    (9 required + 7 history files)

PUBLIC PACK
-----------
  final_delivery/07_public_pack/      (5 files)

POST-DELIVERY
-------------
  post_delivery/01_issue_tracker/post_delivery_issue_tracker.txt
  post_delivery/02_minor_corrections/minor_correction_workflow.txt
  post_delivery/03_version_updates/version_update_rules.txt
  post_delivery/04_portfolio_case_study/  (outline + draft)
  post_delivery/05_public_safe_pack/public_wording_review.txt
  post_delivery/06_selected_portfolio_renders/  (6 PNGs + MP4 + notes)
  post_delivery/07_workflow_retrospective/workflow_retrospective.txt
  post_delivery/08_reusable_templates/  (9 generic templates)
  post_delivery/09_next_project_notes/next_project_recommendations.txt

ADVANCED PRESENTATION PACK (this folder)
----------------------------------------
  advanced_presentation_pack/01_portfolio_page/
  advanced_presentation_pack/02_website_case_study/
  advanced_presentation_pack/03_artstation_style_layout/
  advanced_presentation_pack/04_public_social_pack/
  advanced_presentation_pack/05_image_sequence/
  advanced_presentation_pack/06_thumbnail_and_cover/
  advanced_presentation_pack/07_process_breakdown/
  advanced_presentation_pack/08_submission_pack/
  advanced_presentation_pack/09_reusable_presentation_template/
  advanced_presentation_pack/10_publication_checklist/
  advanced_presentation_pack/11_archive/

ARCHIVES (regeneratable, excluded from git)
-------------------------------------------
  AK47_NonFunctional_Prop_final_delivery_YYYYMMDD.zip       (~234 MB)
  AK47_NonFunctional_Prop_post_delivery_YYYYMMDD.zip        (~11 MB)
  AK47_NonFunctional_Prop_advanced_presentation_pack_YYYYMMDD.zip (~50 KB)
"""
write(os.path.join(PACK, "08_submission_pack", "file_inventory.txt"),
      file_inventory)


# ---------- 11. Reusable presentation template (§10.25) ----------
print("\n=== SECTION 10 STEP 11: REUSABLE TEMPLATE ===")
template = f"""Reusable Presentation Template
===============================
{SCOPE}

This is a generic presentation template for any future non-functional
exterior 3D prop project. Replace [ProjectName] with the actual project
name and [hero_image.png] with the real hero render.

PROJECT TITLE
-------------
[ProjectName] — Non-functional Exterior 3D Prop

ONE-LINE SUMMARY
----------------
A non-functional exterior 3D prop created for hard-surface modelling,
material lookdev, and portfolio/game-asset presentation.

HERO IMAGE
----------
[hero_image.png]

PROJECT FOCUS
-------------
  - exterior silhouette
  - modular modelling
  - material separation
  - decorative exterior details
  - UV/material workflow
  - final renders
  - turntable

WORKFLOW (8 phases)
-------------------
  1. Project setup
  2. Blockout
  3. Major exterior forms
  4. Decorative exterior details
  5. UV / material preparation
  6. Texture / lookdev
  7. Render / turntable / export
  8. Final delivery

FINAL OUTPUTS
-------------
  - Blender file (procedural shaders if possible — keeps the file
    portable with no external textures)
  - Final still renders (full-model + close-ups)
  - Turntable video (MP4)
  - Exports (FBX / GLB / OBJ)
  - Texture folders (or README placeholders if procedural)
  - Documentation (readme, asset notes, render notes, export notes,
    scope/safety note, version history)
  - Public pack (description, captions, summaries)

IMAGE SEQUENCE
--------------
Recommended order (per §10.10):
  1. Hero (front 3/4)
  2. Side profile
  3. Rear 3/4
  4. Top angle
  5. Material close-ups (one per material group)
  6. Edge-wear / surface-detail close-up
  7. Optional clay + wireframe breakdown
  8. Turntable

PUBLIC CAPTIONS
---------------
  - Hero       : "[ProjectName] — non-functional exterior 3D prop, final
                 studio render."
  - Side       : "Full silhouette and part proportions on a neutral
                 background."
  - Close-up   : "<material> close-up showing <surface treatment>."
  - Turntable  : "360 degree turntable of a non-functional exterior 3D
                 prop."

SAFE SCOPE NOTE
---------------
This project is a non-functional exterior visual prop only. It does not
include internal mechanisms, working components, manufacturing
dimensions, or real assembly instructions.

TEMPLATE RULES
--------------
  1. Replace [ProjectName] with the actual project name.
  2. Replace [hero_image.png] with the chosen hero render.
  3. Keep the safe-scope note verbatim.
  4. Remove subject-specific wording outside scope disclaimers.
  5. Keep all public wording concise.
  6. Pair this template with the negation-aware forbidden-word scanner
     before publishing.
"""
write(os.path.join(PACK, "09_reusable_presentation_template",
                    "presentation_template.txt"), template)


# ---------- 12. Publication checklist (§10.27) ----------
print("\n=== SECTION 10 STEP 12: PUBLICATION CHECKLIST ===")
publication_checklist = f"""Publication Checklist
======================
{SCOPE}

Before publishing, check:

IMAGES
------
  [X] Hero image selected (02_front_3quarter_hero.png)
  [X] Side profile selected (01_side_profile.png)
  [X] Material close-ups selected (receiver / wood / magazine / grip)
  [X] Weak renders removed
  [X] No guide / reference / blockout objects visible
  [X] No internal / cutaway images
  [X] No dimensions or blueprint overlays

TEXT
----
  [X] Short summary safe
  [X] Long summary safe
  [X] Captions safe (per public_wording_review.txt)
  [X] Social post safe
  [X] Case study wording safe
  [X] No functional claims
  [X] No manufacturing wording
  [X] No real-assembly wording

VIDEO
-----
  [X] Turntable plays smoothly
  [X] No functional part animation
  [X] No hidden objects visible
  [X] Neutral presentation

FILES
-----
  [X] Public pack separated from full delivery package
  [X] Only selected images included
  [X] No private notes included
  [X] No messy prompt dumps included
  [X] No unnecessary working files included

FINAL DECISION
--------------
  [X] Ready to publish
  [ ] Needs minor text fix
  [ ] Needs image replacement
  [ ] Not ready
"""
write(os.path.join(PACK, "10_publication_checklist",
                    "publication_checklist.txt"),
      publication_checklist)


# Quality gate filled by verify.py; executor writes initial draft.
quality_gate = f"""Final Presentation Quality Gate
================================
{SCOPE}

This draft is replaced with auto-checked results when section10_verify.py
runs against the actual artifacts on disk.

QUALITY GATE RESULT
-------------------
PASS / FAIL / PASS WITH MINOR FIXES

A. VISUAL QUALITY
-----------------
  [ ] Hero image strong
  [ ] Image sequence logical
  [ ] Close-ups show material quality
  [ ] Thumbnail readable
  [ ] Turntable works
  [ ] No weak images included

B. TEXT QUALITY
---------------
  [ ] Summary clear
  [ ] Case study readable
  [ ] Captions concise
  [ ] Process breakdown useful
  [ ] Tools listed clearly
  [ ] No unnecessary long text

C. PUBLIC SAFETY
----------------
  [ ] Non-functional wording included
  [ ] Exterior visual prop wording included
  [ ] No functional firearm claims
  [ ] No manufacturing wording
  [ ] No internal mechanisms
  [ ] No real assembly instructions
  [ ] No dimensions or blueprint framing

D. PACKAGE QUALITY
------------------
  [ ] Public pack separated
  [ ] Submission pack complete
  [ ] File inventory clear
  [ ] Reusable template created
  [ ] Archive ready

DECISION
--------
  [ ] Publish now
  [ ] Fix captions first
  [ ] Replace image first
  [ ] Review safety wording first
  [ ] Do not publish yet
"""
write(os.path.join(PACK, "10_publication_checklist",
                    "final_presentation_quality_gate.txt"), quality_gate)


# ---------- 13. Archive contents log ----------
print("\n=== SECTION 10 STEP 13: ARCHIVE CONTENTS ===")
today = datetime.date.today().isoformat()
SELF_BASENAME = "archive_contents.txt"
archive_contents = [
    f"Advanced Presentation Pack — Archive Contents",
    f"==============================================",
    f"Generated by section10_executor on {today}.",
    SCOPE,
    f"(self-listing of {SELF_BASENAME} omitted so the file stays "
    f"byte-identical across re-runs)",
    "",
]
for dirpath, dirnames, files in os.walk(PACK):
    rel = os.path.relpath(dirpath, PACK)
    dirnames.sort()
    files.sort()
    if rel == ".":
        archive_contents.append("advanced_presentation_pack/")
    else:
        archive_contents.append(f"  {rel}/")
    for fn in files:
        if fn == SELF_BASENAME:
            continue
        sz = os.path.getsize(os.path.join(dirpath, fn))
        archive_contents.append(f"    {fn}  ({sz} bytes)")
write(os.path.join(PACK, "11_archive", SELF_BASENAME),
      "\n".join(archive_contents) + "\n")


print("\n=== SECTION 10 EXECUTOR DONE ===")
print(f"  advanced_presentation_pack/ assembled at: {PACK}")
print(f"  next: run section10_verify.py + section10_archive.py")
