"""Section 9 executor: builds the post_delivery/ folder + all post-delivery
documentation, templates, retrospective, and next-project notes.

Plain Python — no Blender, no rendering. Idempotent.
"""
import os
import shutil
import datetime

PROJECT_ROOT = os.environ.get(
    "AK47_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

POST = os.path.join(PROJECT_ROOT, "post_delivery")
DELIVERY = os.path.join(PROJECT_ROOT, "final_delivery")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {path}")


def copy(src, dst):
    if not os.path.exists(src):
        print(f"  MISSING: {src}")
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return True


SCOPE = ("Scope reminder: non-functional exterior visual prop only. "
         "No internal mechanism, no working trigger, no chamber/bolt/"
         "spring, no functional magazine, no bore, no rifling, no "
         "manufacturing dimensions, no real assembly instructions.")


# ---------- 1. Folder tree ----------
print("\n=== SECTION 9 STEP 1: FOLDERS ===")
LEAF_FOLDERS = [
    "01_issue_tracker",
    "02_minor_corrections",
    "03_version_updates",
    "04_portfolio_case_study",
    "05_public_safe_pack",
    "06_selected_portfolio_renders",
    "07_workflow_retrospective",
    "08_reusable_templates",
    "09_next_project_notes",
    "10_post_delivery_archive",
]
for sub in LEAF_FOLDERS:
    os.makedirs(os.path.join(POST, sub), exist_ok=True)
print(f"  created/ensured {len(LEAF_FOLDERS)} leaf folders under post_delivery/")


# ---------- 2. Issue tracker (§9.4) ----------
print("\n=== SECTION 9 STEP 2: ISSUE TRACKER ===")
today = datetime.date.today().isoformat()
issue_tracker = f"""Post-Delivery Issue Tracker
============================
{SCOPE}

Issue format (one record per ----- block):

  Issue ID            : PD_ISSUE_NNN  (or PD_INFO_NNN for info-only)
  Date found          : YYYY-MM-DD
  Category            : Render / Texture / Export / Documentation /
                        File structure / Public wording / Other
  Problem             : One-line description
  Where found         : Relative file path / render name / export file /
                        documentation file
  Severity            : Low / Medium / High
  Recommended action  : Fix / Defer / Ignore / Archive note only
  Assigned phase      : 6 / 7 / 8 / Post-delivery correction
  Status              : Open / In Progress / Fixed / Deferred / Closed
  Notes               : Additional comments

Categories:
  - Render
  - Texture
  - Export
  - Documentation
  - File structure
  - Public wording
  - Other

----------------------------------------------------------------------------

  Issue ID            : PD_INFO_001
  Date found          : {today}
  Category            : Other
  Problem             : No post-delivery issues observed at handover;
                        tracker initialised for future minor corrections.
  Where found         : --
  Severity            : Low
  Recommended action  : Archive note only
  Assigned phase      : Post-delivery correction
  Status              : Closed
  Notes               : Phase 8 verify.py reported 32/32 PASS; archive
                        round-trip OK. Phase 9 has not surfaced any
                        delivery defects.

----------------------------------------------------------------------------

Summary:
  Open issues         : 0
  Medium severity     : 0
  High severity       : 0
  Blocking next steps : NO
"""
write(os.path.join(POST, "01_issue_tracker", "post_delivery_issue_tracker.txt"),
      issue_tracker)


# ---------- 3. Minor correction workflow (§9.6) ----------
print("\n=== SECTION 9 STEP 3: MINOR CORRECTION WORKFLOW ===")
minor_correction = f"""Minor Correction Workflow
==========================
{SCOPE}

This workflow describes how to fix small post-delivery issues without
damaging the final package.

MINOR CORRECTION EXAMPLES
-------------------------
  - Missing texture path
  - One render too dark
  - Typo in readme
  - Public caption wording issue
  - Wrong file copied into final_delivery
  - Export missing material link
  - Turntable slightly off-centre
  - Small floating decorative detail visible in render

MAJOR ISSUE EXAMPLES (do NOT treat as minor)
--------------------------------------------
  - Broken model geometry
  - Major UV failure
  - Wrong object scale
  - Major material failure
  - Export unusable
  - Final .blend cannot open

Major issues require a v2.0 revision (see version_update_rules.txt).

CORRECTION RULES (in order)
---------------------------
  1. Never overwrite the original final delivery without backup.
  2. Create a correction note FIRST (see format below).
  3. Fix only the specific issue called out in the related issue tracker
     entry.
  4. Save the corrected file as a NEW version
     (AK47_exterior_prop_final_v1_1.blend, ...).
  5. Update version_history.txt in 06_documentation/.
  6. Re-test affected output (re-render the specific image; re-open the
     specific export).
  7. Replace ONLY the affected file(s) in final_delivery/. Do not
     rebuild the entire delivery folder.
  8. Archive the old file in 10_post_delivery_archive/ before overwriting.

VERSION NAMING (per §9.8)
-------------------------
  v1.0 -> AK47_exterior_prop_final.blend       (original Phase 8 delivery)
  v1.1 -> AK47_exterior_prop_final_v1_1.blend  (first minor correction)
  v1.2 -> AK47_exterior_prop_final_v1_2.blend  (second minor correction)
  ...
  v2.0 -> AK47_exterior_prop_final_v2_0.blend  (only if major revision)

NEVER use names like:
  final_final.blend, real_final.blend, fixed_final.blend,
  newnewfinal.blend, last_version_final.blend

CORRECTION NOTE FORMAT
----------------------
Write one note per correction into
02_minor_corrections/correction_NNN.txt with these 7 fields:

  Correction ID  : CORR_NNN
  Related issue  : PD_ISSUE_NNN (from post_delivery_issue_tracker.txt)
  File affected  : <relative path of the file that was replaced>
  Change made    : <one-paragraph description of the actual change>
  Reason         : <why the change was needed>
  Test result    : <which renders/files re-tested and the outcome>
  Status         : Open / Applied / Reverted / Closed
"""
write(os.path.join(POST, "02_minor_corrections", "minor_correction_workflow.txt"),
      minor_correction)


# ---------- 4. Version update rules (§9.8) ----------
print("\n=== SECTION 9 STEP 4: VERSION UPDATE RULES ===")
version_rules = f"""Version Update Rules
=====================
{SCOPE}

VERSION SYSTEM
--------------
  v1.0   Original final delivery (Phase 8 output).
  v1.1   Minor post-delivery correction.
  v1.2   Another minor correction.
  v1.3 .. v1.N   Subsequent minor corrections.
  v2.0   Major visual revision (rare; only if genuinely required).

USE v1.X FOR (minor)
--------------------
  - texture relink
  - typo fix in any documentation file
  - render replacement (single image)
  - export replacement (single FBX/GLB/OBJ)
  - small material adjustment (one MAT_* setting)
  - camera/render correction (one CAM_* tweak)

USE v2.0 FOR (major; rare)
--------------------------
  - major remodel of any AK_ part
  - major UV rebuild
  - full material redesign across all hero materials
  - full render scene redesign (new lighting + cameras)

NEVER CREATE FILE NAMES LIKE
----------------------------
  final_final.blend
  real_final.blend
  fixed_final.blend
  newnewfinal.blend
  last_version_final.blend

VERSION LOG FORMAT
------------------
Each new version gets one entry in 03_version_updates/version_log.txt
with these 6 fields:

  Version       : v1.1
  Date          : YYYY-MM-DD
  Reason        : <which issue from post_delivery_issue_tracker>
  Files changed : <relative paths of changed files>
  Testing       : <how the change was verified>
  Status        : Released / Reverted / Superseded

ARCHIVE RULE
------------
Before replacing any file in final_delivery/, copy the original file
into post_delivery/10_post_delivery_archive/<version>/ so it can be
recovered.
"""
write(os.path.join(POST, "03_version_updates", "version_update_rules.txt"),
      version_rules)


# ---------- 5. Portfolio case study outline + draft (§9.10 / §9.12) ----------
print("\n=== SECTION 9 STEP 5: CASE STUDY ===")
case_study_outline = f"""Portfolio Case Study Outline
=============================
{SCOPE}

1. Project title
2. Short summary
3. Goal
4. Tools
5. Workflow overview
6. Challenges
7. Solutions
8. Final result
9. What I learned
10. Safety/scope note

Each section is one paragraph (case_study_draft.txt has the filled-in
version).
"""
write(os.path.join(POST, "04_portfolio_case_study",
                    "portfolio_case_study_outline.txt"), case_study_outline)


case_study_draft = f"""Portfolio Case Study — Draft
=============================
{SCOPE}

TITLE
-----
Non-functional AK-style Exterior 3D Prop — phase-based Blender workflow.

SHORT SUMMARY
-------------
A non-functional exterior 3D prop created as a hard-surface modelling,
material, and render presentation exercise. The focus was on exterior
silhouette, modular asset structure, dark worn metal, reddish-brown
wood, blackened magazine material, bakelite-style grip, controlled edge
wear, and final portfolio presentation.

GOAL
----
Build a visually readable exterior prop using a structured Blender
workflow, moving from project setup to blockout, major forms, decorative
exterior details, UV/material preparation, look development, render
composition, and final delivery packaging.

TOOLS
-----
Blender 5.1 (Cycles + Eevee), Python (executor + verify + archive
scripts), imageio-ffmpeg (for headless MP4 encode).

WORKFLOW (8 phases)
-------------------
  1. Project setup and references                      (v01)
  2. Rough blockout                                    (v02)
  3. Major exterior parts                              (v03)
  4. Decorative exterior details                       (v04)
  5. UV and material preparation                       (v05)
  6. Final texture / lookdev (procedural shaders)      (v06)
  7. Final scene, renders, turntable, export setup     (v07)
  8. Final delivery packaging + archive                (AK47_exterior_prop_final.blend)

Every phase has a deterministic Python executor + verify script. Total
final-delivery output: 246 files, 234 MB zip archive.

CHALLENGES
----------
  - Keeping the blockout simple (silhouette before details)
  - Avoiding over-detailing in Phase 4 (capped at 51 detail objects)
  - Maintaining per-material UV atlas density consistency
  - Procedural shaders for wear/dirt that don't pop on flat faces
  - Lookdev lighting that doesn't blow out dark blued metal
  - Headless MP4 encoding without system ffmpeg (Blender 5.x removed
    FFMPEG from image_settings)
  - Safe public wording across all delivery documents

SOLUTIONS
---------
  - Phase-based planning with executor + verify scripts per phase
  - Preserved every checkpoint .blend file
  - Per-material UV atlas via average_islands_scale + pack_islands
  - Procedural shader graphs: Noise + Wave + Pointiness + AmbientOcclusion
  - Reusable NodeGroups: EdgeWearMask, CavityAO
  - Eevee for turntable animation (180 frames in 7 minutes vs hours)
  - imageio-ffmpeg for headless H.264 MP4 encode
  - Negation-aware forbidden-word matcher that understands "no X" / "does
    not include X" / "without X" disclaimers

FINAL RESULT
------------
The final delivery package contains:
  - AK47_exterior_prop_final.blend
  - 14 final stills (4 full-model + 7 close-up + 3 clay/wire) at
    1920x1080 or 1080x1080
  - 1.65 MB H.264 MP4 turntable (180 frames, 1280x720, 24 fps)
  - FBX + GLB + OBJ exports
  - Procedural-shader-driven materials (no PNG dependencies)
  - 16 documentation files + 5 public-pack files + handover checklist
    auto-gated to PASS

LEARNING
--------
This project deepened my workflow planning, hard-surface organisation,
material separation, lookdev control, render presentation, and final
packaging discipline. Also strengthened Python automation: writing
deterministic executor/verify scripts per phase paid off when I needed
to re-tune materials in Phase 6 — the entire pipeline re-ran without
manual intervention.

SAFETY / SCOPE NOTE
-------------------
This is a non-functional exterior visual prop only. It does not include
internal mechanisms, working firing components, manufacturing
dimensions, or real assembly instructions.
"""
write(os.path.join(POST, "04_portfolio_case_study",
                    "portfolio_case_study_draft.txt"), case_study_draft)


# ---------- 6. Selected portfolio renders (§9.13) ----------
print("\n=== SECTION 9 STEP 6: PORTFOLIO RENDERS ===")
PORTFOLIO = [
    ("04_final_renders/full_model/02_front_3quarter_hero.png", "02_front_3quarter_hero.png"),
    ("04_final_renders/full_model/01_side_profile.png", "01_side_profile.png"),
    ("04_final_renders/closeups/05_closeup_receiver_metal.png", "05_closeup_receiver_metal.png"),
    ("04_final_renders/closeups/06_closeup_wood_stock.png", "06_closeup_wood_stock.png"),
    ("04_final_renders/closeups/08_closeup_magazine.png", "08_closeup_magazine.png"),
    ("04_final_renders/closeups/10_closeup_grip.png", "10_closeup_grip.png"),
    ("05_turntable/turntable_ak_style_exterior_prop.mp4", "turntable_ak_style_exterior_prop.mp4"),
]
portfolio_dst = os.path.join(POST, "06_selected_portfolio_renders")
copied = 0
for src_rel, dst_name in PORTFOLIO:
    src = os.path.join(DELIVERY, src_rel)
    dst = os.path.join(portfolio_dst, dst_name)
    if copy(src, dst):
        copied += 1
        print(f"  copied {dst_name}")
print(f"  total portfolio files: {copied}/{len(PORTFOLIO)}")

portfolio_notes = f"""Portfolio Selection Notes
==========================
{SCOPE}

Selection rules (per §9.13):
  1. Choose fewer strong images, not every render.
  2. Use the hero render first.
  3. Include one full side profile.
  4. Include 2-4 material close-ups.
  5. Include the turntable if it is smooth.
  6. Avoid images that look too technical or blueprint-like.
  7. Avoid images focusing on functional-looking areas.

Files in this folder:

  02_front_3quarter_hero.png        HERO — shows full silhouette + all
                                    materials (metal + wood + magazine +
                                    grip) in one shot. Strongest portfolio
                                    image.
  01_side_profile.png               Full silhouette + part proportions on
                                    a neutral background.
  05_closeup_receiver_metal.png     Dark blued metal close-up with subtle
                                    Pointiness-driven edge wear.
  06_closeup_wood_stock.png         Reddish-brown wood with Wave-driven
                                    lengthwise grain.
  08_closeup_magazine.png           Blackened matte metal (visibly more
                                    matte than the receiver).
  10_closeup_grip.png               Bakelite/polymer grip — distinct from
                                    wood (fine noise, no grain).
  turntable_ak_style_exterior_prop.mp4
                                    180-frame 1280x720 turntable @ 24 fps,
                                    full 360 rotation, neutral background.

Files NOT selected and why:
  - 03_rear_3quarter.png            Redundant with the hero shot.
  - 04_top_angle.png                Useful for shape-volume QA but reads
                                    technical at first glance.
  - 07_closeup_handguard_wood.png   Material story already covered by
                                    06_closeup_wood_stock.png.
  - 09_closeup_front_sight_visual.png  Close-up of a sight-like feature
                                    — risk of reading as functional
                                    detail. Skipped per §9.13 rule 7.
  - 11_closeup_edgewear.png         Useful for breakdown, not portfolio
                                    headline.
  - 12_clay_full_model.png          Process breakdown, not final image.
  - 13_wireframe_full_model.png     Topology breakdown, not final image.
  - 14_material_breakdown.png       Same.
"""
write(os.path.join(portfolio_dst, "portfolio_selection_notes.txt"),
      portfolio_notes)


# ---------- 7. Public wording review (§9.15) ----------
print("\n=== SECTION 9 STEP 7: PUBLIC WORDING REVIEW ===")
public_wording = f"""Public Wording Review
======================
{SCOPE}

This guide ensures any public-facing copy about the project stays inside
the non-functional exterior visual prop scope.

SAFE WORDING (use freely)
-------------------------
  - non-functional exterior 3D prop
  - visual rendering
  - portfolio presentation
  - game-asset display
  - hard-surface exterior modelling
  - material/lookdev exercise
  - decorative exterior details
  - safe visual prop workflow

AVOID WORDING (do not use)
--------------------------
  - working AK
  - functional firearm
  - accurate weapon build
  - manufacturable replica
  - real assembly model
  - firing mechanism
  - internal reconstruction
  - technical firearm blueprint
  - full real weapon detail

REWRITE EXAMPLES
----------------

  Unsafe : Accurate AK-47 model with full details.
  Safer  : Non-functional AK-style exterior 3D prop focused on visual
           silhouette, materials, and portfolio presentation.

  Unsafe : Realistic weapon model ready for use.
  Safer  : Exterior visual prop asset prepared for rendering and game-art
           presentation.

  Unsafe : Complete AK build breakdown.
  Safer  : Phase-based exterior prop modelling workflow breakdown.

PORTFOLIO CAPTION GUIDANCE
--------------------------
  - Start with "non-functional exterior 3D prop" the first time the
    asset is named in a portfolio page.
  - Describe materials by visual identity (dark blued steel, reddish-brown
    wood, blackened matte metal, bakelite/polymer), not by claimed
    manufacturing accuracy.
  - For close-ups, describe surface treatment (edge wear, grain, cavity
    AO) rather than the role of the depicted part.

PUBLIC DESCRIPTION GUIDANCE
---------------------------
  - Lead with hard-surface modelling + material/lookdev framing.
  - Mention "no internal mechanism, no working components" once early.
  - Avoid claims of functional accuracy.
  - Avoid the words "ammunition", "manufacturable", "blueprint" unless
    they appear inside a "does not include" disclaimer.
"""
write(os.path.join(POST, "05_public_safe_pack", "public_wording_review.txt"),
      public_wording)


# ---------- 8. Workflow retrospective (§9.17) ----------
print("\n=== SECTION 9 STEP 8: RETROSPECTIVE ===")
retrospective = f"""Workflow Retrospective
=======================
{SCOPE}

1. WHAT WORKED WELL
-------------------
  - Phase-based workflow with three scripts per phase (executor + verify
    + render/archive). Re-runs were deterministic.
  - Separate version files (v01..v07) preserved every checkpoint — easy
    to compare or roll back without git.
  - Collection naming convention (00_REFERENCE through
    12_PRESENTATION_STAGE). Render scripts hide non-final collections by
    name; nothing leaked into final renders.
  - Material group separation (4 hero MAT_* + 6 fallback). Verify
    asserted distinctness (magazine rough > receiver rough; grip has no
    wave node).
  - Final delivery handover_checklist auto-gated by verify.py. Catches
    truncated copies and missing docs immediately.
  - Negation-aware forbidden-word matcher caught its own false
    positives during Phase 8 self-audit — the audit-the-audit pattern
    worked.
  - Idempotent doc appends (Section N marker + truncate-on-reappear)
    prevented the silent duplication seen in Phase 6 from recurring.

2. WHAT CAUSED PROBLEMS
-----------------------
  - Planning got long. Phase 5 alone wrote 12 prompts + a 500-line
    executor before any material refinement happened.
  - Early lookdev renders were too bright; took two re-tunes (key light
    150W -> 30W, base colour darker, grime factor 0.30 -> 0.12).
  - Phase 6 append_doc had a silent duplicate-Section-6 bug; only
    caught it during the self-audit "check again" request.
  - Phase 7 wireframe render: Freestyle linestyle was None at headless
    init; had to switch to the Wireframe shader node.
  - Phase 8 forbidden-word matcher flagged scope-disclaimer phrases
    ("does not include ... real assembly instructions"); fixed with a
    250-char negation look-back.
  - Blender 5.x removed FFMPEG from image_settings; the original
    section8_render_turntable_mp4.py crashed immediately. Switched to
    PNG sequence + imageio-ffmpeg encode.
  - Cycles CPU for a 180-frame turntable would have taken ~3 hours.
    Switched to Eevee — completed in 6 min 40 s.

3. WHAT TO IMPROVE NEXT TIME
----------------------------
  - Render a hero shot in Phase 3 (before details), not Phase 7. Early
    visual feedback catches silhouette problems sooner.
  - Cap each phase's prompt files at 5-8, not 12-15. Long prompt lists
    duplicate executor logic.
  - Write the verify script BEFORE the executor — it forces a tighter
    spec for what the phase actually has to produce.
  - Default to Eevee for previews; reserve Cycles for hero stills.
  - If a downstream target needs PNG textures, bake the procedural
    shaders to PNG inside Phase 6 (not deferred to Phase 9).
  - Pick the negation-aware safety matcher from day 1, not Phase 8.

4. WHAT SKILLS IMPROVED
-----------------------
  - Blender 5.x layered-action API (action.layers / strips / channels)
    — handled the keyframe-interpolation change.
  - Pointiness + AmbientOcclusion shader patterns for geometry-driven
    wear / cavity treatment.
  - Wave-driven wood grain locked to a specific UV axis (+X = +U).
  - Idempotent text generators with marker-based truncation.
  - imageio-ffmpeg as a portable headless MP4 encode path.
  - Eevee animation rendering (much faster than Cycles for previews).

5. WHAT TO REUSE (templates extracted in 08_reusable_templates/)
---------------------------------------------------------------
  - 8-phase folder structure with versioned .blend per phase
  - section{{N}}_executor.py / section{{N}}_verify.py / section{{N}}_*.py trio
  - EdgeWearMask + CavityAO shader NodeGroups
  - Negation-aware forbidden-word scanner (250-char look-back)
  - handover_checklist.txt auto-gated by verify.py
  - PNG sequence -> imageio-ffmpeg -> H.264 MP4 encode pipeline

6. WHAT NOT TO REPEAT
---------------------
  - Endless prompt expansion before any geometry exists.
  - Over-documenting steps that the executor already does.
  - Adding optional phases without a concrete deliverable.
  - Cycles CPU for animation previews — always Eevee.
  - Forbidden-word checks that flag scope disclaimers (use negation
    awareness from the start).
"""
write(os.path.join(POST, "07_workflow_retrospective",
                    "workflow_retrospective.txt"), retrospective)


# ---------- 9. Reusable templates (§9.19) ----------
print("\n=== SECTION 9 STEP 9: REUSABLE TEMPLATES ===")
templates_dir = os.path.join(POST, "08_reusable_templates")

GENERIC_SCOPE = ("Scope reminder: non-functional exterior 3D prop only. "
                 "No internal mechanism, no functional anything, no "
                 "manufacturing dimensions, no real assembly instructions.")


def template(name, body):
    write(os.path.join(templates_dir, name),
          f"{name.replace('_template.txt', '').replace('_', ' ').title()} Template\n"
          + "=" * 60 + "\n"
          + GENERIC_SCOPE + "\n\n" + body)


template("folder_structure_template.txt", """Recommended folder layout for any ProjectName_NonFunctional_Prop:

  00_references/
    proportion_notes/
    cropped_parts/
    paintover_guides/
  01_blender/
    v01_project_setup.blend
    v02_blockout.blend
    v03_major_parts.blend
    v04_minor_details.blend
    v05_uv_materials.blend
    v06_final_textures_lookdev.blend
    v07_final_scene_export.blend
    ProjectName_exterior_prop_final.blend
  02_exports/
  03_textures/
    metal/  wood/  magazine/  grip/  shared/
    (or whatever material groups apply to the project)
  04_renders/
    viewport_tests/  clay_renders/  uv_checker/  lookdev/  final/
  05_mcp_prompts/
    section1/ ... section9/
      sectionN_executor.py
      sectionN_verify.py
      sectionN_render_*.py / sectionN_archive.py / etc.
  06_documentation/
  08_reviews/
  09_archive/
  final_delivery/  (built by Phase 8)
  post_delivery/   (built by Phase 9)
""")

template("phase_workflow_template.txt", """Generic 8-phase workflow:

  1. Project setup    -> v01_project_setup.blend
  2. Blockout         -> v02_blockout.blend
  3. Major parts      -> v03_major_parts.blend
  4. Minor details    -> v04_minor_details.blend
  5. UV / materials   -> v05_uv_materials.blend
  6. Final lookdev    -> v06_final_textures_lookdev.blend
  7. Final scene      -> v07_final_scene_export.blend
  8. Delivery package -> final_delivery/ + archive zip
  (9. Post-delivery   -> post_delivery/)

Each phase has 3 Python scripts:
  sectionN_executor.py   builds the deliverable
  sectionN_verify.py     gates the §N final review checklist
  sectionN_render_*.py / archive.py / export.py  (as needed)

Idempotency rules:
  - Document appends use a marker (\\n\\nSection N —) so re-running the
    executor replaces the block instead of duplicating it.
  - Folder creation uses os.makedirs(..., exist_ok=True).
  - Material / NodeGroup creation checks bpy.data first.
""")

template("mcp_prompt_template.txt", """Template for an MCP prompt that the executor follows:

Phase N Prompt M -- <Short Title>
==================================

Open <previous-phase>.blend and save as <this-phase>.blend.

Do <specific deliverable list, one bullet per output>.

Hard scope: non-functional exterior prop only. No internal mechanism,
no working trigger, no chamber/bolt/spring, no functional magazine,
no bore, no rifling, no manufacturing dimensions, no real assembly
instructions.

After running:
  [ ] <verifiable check 1>
  [ ] <verifiable check 2>
  [ ] <verifiable check 3>
""")

template("issue_tracker_template.txt", """Issue tracker entry format:

  Issue ID            : <PREFIX>_NNN
  Date found          : YYYY-MM-DD
  Category            : Render / Texture / Export / Documentation /
                        File structure / Public wording / Other
  Problem             : <one-line description>
  Where found         : <relative file path>
  Severity            : Low / Medium / High
  Recommended action  : Fix / Defer / Ignore / Archive note only
  Assigned phase      : <which phase to handle this in>
  Status              : Open / In Progress / Fixed / Deferred / Closed
  Notes               : <additional comments>

Summary block at the end of the file:
  Open issues         : <count>
  Medium severity     : <count>
  High severity       : <count>
  Blocking next steps : YES / NO

High-severity entries always block the next phase.
""")

template("render_checklist_template.txt", """Image quality:
  [ ] Correct resolution (full-model = 1920x1080, close-up = 1080x1080)
  [ ] No major noise (Cycles samples >= 64 / Eevee taa >= 32)
  [ ] No overexposed highlights
  [ ] No crushed dark areas
  [ ] Model not clipped
  [ ] Camera framing clean
  [ ] Materials readable

Scene quality:
  [ ] No guide/reference visible
  [ ] No blockout object visible
  [ ] No test object visible
  [ ] No missing texture warnings
  [ ] No floating detail obvious

Portfolio quality:
  [ ] Hero render strong
  [ ] Side render readable
  [ ] Close-ups show material quality
  [ ] Background not distracting
  [ ] Renders feel consistent

Safety:
  [ ] No technical assembly diagram style
  [ ] No internal/cutaway view
  [ ] No dimensions
  [ ] No functional-use scene
""")

template("export_checklist_template.txt", """  [ ] Export source = <ExportReadyCollection> only
  [ ] Apply scale only if needed
  [ ] Preserve material assignments
  [ ] Preserve UVs
  [ ] Include texture references if format supports
  [ ] Export selected export-ready objects only
  [ ] Do not export references/guides/blockouts/cameras/lights
  [ ] Test import in a clean Blender scene

Safety:
  [ ] Export contains exterior visual prop only
  [ ] No internal/functional parts
  [ ] No manufacturing dimensions
  [ ] No technical assembly notes
""")

template("handover_checklist_template.txt", """A. Final files:
  [ ] Final .blend included
  [ ] Final renders included
  [ ] Turntable video / preview frames included
  [ ] Export files included if required
  [ ] Textures or texture READMEs included
  [ ] Documentation included
  [ ] Public pack included

B. Final .blend opens correctly:
  [ ] Materials load
  [ ] Textures load (or shaders are procedural)
  [ ] Cameras exist
  [ ] Lights exist
  [ ] Turntable setup exists
  [ ] Export-ready collection exists

C. Documentation completeness:
  [ ] readme.txt
  [ ] asset_notes.txt
  [ ] material_notes.txt
  [ ] texture_notes.txt
  [ ] render_notes.txt
  [ ] export_notes.txt
  [ ] scope_and_safety_note.txt
  [ ] version_history.txt

D. Safety / scope:
  [ ] Non-functional exterior scope stated
  [ ] No internal mechanisms in any object name
  [ ] No working parts in any object name
  [ ] No forbidden wording in any delivery .txt
""")

template("public_wording_template.txt", """Safe wording (use):
  - non-functional exterior 3D prop
  - visual rendering / portfolio presentation / game-asset display
  - hard-surface exterior modelling
  - material/lookdev exercise
  - decorative exterior details

Forbidden wording (use a negation-aware matcher, 250-char look-back):
  - working <subject>
  - functional <subject>
  - manufacturable / manufacturing-ready
  - real assembly instruction[s]
  - technical <subject> reconstruction
  - blueprint-level
  - live ammunition

Negation phrases to whitelist (these can precede a forbidden token):
  no, not, does not, doesn't, without, exclude, excluded, avoid,
  must not, should not, never, neither

Rewrite pattern:
  unsafe  : <claim of functional accuracy>
  safer   : Non-functional exterior 3D prop focused on <materials /
            silhouette / lookdev / portfolio presentation>.
""")

template("retrospective_template.txt", """  1. What worked well
  2. What caused problems
  3. What should be improved next time
  4. What skills improved
  5. What should be reused
  6. What should NOT be repeated

For each section, write at least 3 concrete bullets specific to this
project — no generic platitudes ("be more organised", "plan better").

Add a final line stating the next-project recommendation (see
09_next_project_notes/next_project_recommendations.txt).
""")
print("  wrote 9 generic template files")


# ---------- 10. Next project notes (§9.21) ----------
print("\n=== SECTION 9 STEP 10: NEXT PROJECT NOTES ===")
next_project = f"""Next Project Recommendations
=============================
{SCOPE}

10 candidate non-weapon subjects:
  1. Weathered toolbox
  2. Vintage camera
  3. Sci-fi radio
  4. Industrial control panel
  5. Flashlight
  6. Camping lantern
  7. Game controller
  8. Robot exterior shell
  9. Mechanical keyboard
 10. Medical scanner exterior prop

Selection criteria:
  [ ] Non-functional
  [ ] Safe for portfolio
  [ ] Clear silhouette
  [ ] Multiple materials
  [ ] Not too large in scope
  [ ] Can be finished faster than current project
  [ ] Good close-up material opportunities
  [ ] No dangerous functional mechanism

BEST RECOMMENDATION
-------------------
Weathered toolbox OR vintage camera.

Reasons:
  - Safer public portfolio subject — no chance of being misread as a
    functional / restricted item.
  - Strong hard-surface practice: corners, panel lines, screws, hinges,
    handles, leather/plastic/metal contrast.
  - Good material variety (steel + paint + leather + rubber for toolbox;
    metal + leather + bakelite + glass for camera).
  - No restricted-mechanism concerns when sharing renders publicly.
  - Easier to finish and present in a shorter cycle than this project.

WORKFLOW REUSE
--------------
The 8-phase workflow + 3-script-per-phase pattern from this project
transfers directly. Generic templates in 08_reusable_templates/ are
already de-namespaced. Just swap ProjectName_NonFunctional_Prop into the
folder layout and adjust the material groups to whatever the new subject
needs.
"""
write(os.path.join(POST, "09_next_project_notes",
                    "next_project_recommendations.txt"), next_project)


# ---------- 11. Archive contents log ----------
# Skip the archive_contents.txt file itself from the listing — otherwise
# the file's recorded self-size drifts a few bytes between successive
# runs (breaks idempotency).
print("\n=== SECTION 9 STEP 11: ARCHIVE CONTENTS LOG ===")
SELF_BASENAME = "post_delivery_archive_contents.txt"
archive_contents = [
    f"Post-Delivery Archive Contents",
    f"================================",
    f"Generated by section9_executor on {today}.",
    SCOPE,
    f"(self-listing of {SELF_BASENAME} is intentionally omitted so the "
    f"file stays byte-identical across re-runs)",
    "",
]
for dirpath, dirnames, files in os.walk(POST):
    rel = os.path.relpath(dirpath, POST)
    dirnames.sort()
    files.sort()
    if rel == ".":
        archive_contents.append("post_delivery/")
    else:
        archive_contents.append(f"  {rel}/")
    for fn in files:
        if fn == SELF_BASENAME:
            continue
        sz = os.path.getsize(os.path.join(dirpath, fn))
        archive_contents.append(f"    {fn}  ({sz} bytes)")
write(os.path.join(POST, "10_post_delivery_archive", SELF_BASENAME),
      "\n".join(archive_contents) + "\n")


print("\n=== SECTION 9 EXECUTOR DONE ===")
print(f"  post_delivery/ assembled at: {POST}")
print(f"  next: run section9_verify.py + section9_archive.py")
