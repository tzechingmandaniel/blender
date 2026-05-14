"""Verify the final_delivery/ package and the archive zip against the
§8.34 Final Quality Gate.

Runs as plain Python — no Blender required.
"""
import os
import zipfile
import sys

PROJECT_ROOT = os.environ.get(
    "AK47_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DELIVERY = os.path.join(PROJECT_ROOT, "final_delivery")
DOCS = os.path.join(DELIVERY, "06_documentation")

print("\n=== §8.34 FINAL QUALITY GATE ===")
results = []


def check(label, ok, detail=""):
    results.append((label, ok, detail))


# A. Visual quality (files exist + non-zero)
def file_size(rel):
    p = os.path.join(DELIVERY, rel)
    if not os.path.exists(p):
        return -1
    return os.path.getsize(p)


def list_pngs(rel):
    d = os.path.join(DELIVERY, rel)
    if not os.path.isdir(d):
        return []
    return [f for f in sorted(os.listdir(d)) if f.endswith(".png")]


EXPECTED_FULL_MODEL = [
    "01_side_profile.png", "02_front_3quarter_hero.png",
    "03_rear_3quarter.png", "04_top_angle.png",
]
EXPECTED_CLOSEUPS = [
    "05_closeup_receiver_metal.png", "06_closeup_wood_stock.png",
    "07_closeup_handguard_wood.png", "08_closeup_magazine.png",
    "09_closeup_front_sight_visual.png", "10_closeup_grip.png",
    "11_closeup_edgewear.png",
]
EXPECTED_CLAY_WIRE = [
    "12_clay_full_model.png", "13_wireframe_full_model.png",
    "14_material_breakdown.png",
]
EXPECTED_PORTFOLIO = [
    "01_side_profile.png", "02_front_3quarter_hero.png",
    "05_closeup_receiver_metal.png", "06_closeup_wood_stock.png",
    "08_closeup_magazine.png",
]


def check_set(label, rel_dir, expected_files):
    actual = set(list_pngs(rel_dir))
    missing = [e for e in expected_files if e not in actual]
    check(label, not missing, f"missing: {missing}")


check_set("04_final_renders/full_model has 4 named stills",
          "04_final_renders/full_model", EXPECTED_FULL_MODEL)
check_set("04_final_renders/closeups has 7 named close-ups",
          "04_final_renders/closeups", EXPECTED_CLOSEUPS)
check_set("04_final_renders/clay_wireframe_optional has 3 named files",
          "04_final_renders/clay_wireframe_optional", EXPECTED_CLAY_WIRE)
check_set("04_final_renders/portfolio_selected has 5 named files",
          "04_final_renders/portfolio_selected", EXPECTED_PORTFOLIO)

# Each render > 100 KB (catches truncated copies)
for rel_dir, names in (
    ("04_final_renders/full_model", EXPECTED_FULL_MODEL),
    ("04_final_renders/closeups", EXPECTED_CLOSEUPS),
    ("04_final_renders/clay_wireframe_optional", EXPECTED_CLAY_WIRE),
    ("04_final_renders/portfolio_selected", EXPECTED_PORTFOLIO),
):
    bad = []
    for fn in names:
        sz = file_size(f"{rel_dir}/{fn}")
        if sz < 100_000:
            bad.append(f"{fn}={sz}")
    check(f"{rel_dir} stills > 100 KB each", not bad, f"bad: {bad}")


# Turntable preview frames
ttf = list_pngs("05_turntable/turntable_frames")
check(f"turntable preview has >= 12 frames (got {len(ttf)})",
      len(ttf) >= 12)
turntable_readme = file_size("05_turntable/README.txt")
check("05_turntable/README.txt exists + non-empty",
      turntable_readme > 0)
# Turntable MP4 (full 180-frame video per §8.12)
mp4_size = file_size("05_turntable/turntable_ak_style_exterior_prop.mp4")
check(f"turntable MP4 video exists (got {mp4_size:,} bytes)",
      mp4_size > 100_000)


# B. File quality — final .blend
blend_sz = file_size("01_blender_final/AK47_exterior_prop_final.blend")
check(f"AK47_exterior_prop_final.blend present (size={blend_sz})",
      blend_sz > 100_000)

# Working-copy of final blend in 01_blender/
work_blend = os.path.join(PROJECT_ROOT, "01_blender",
                          "AK47_exterior_prop_final.blend")
check("01_blender/AK47_exterior_prop_final.blend (working copy) exists",
      os.path.exists(work_blend) and os.path.getsize(work_blend) > 100_000)

# Earlier phase files preserved
PRESERVED = [
    "v01_project_setup.blend", "v02_blockout.blend",
    "v03_major_parts.blend", "v04_minor_details.blend",
    "v05_uv_materials.blend", "v06_final_textures_lookdev.blend",
    "v07_final_scene_export.blend",
]
missing_preserved = [n for n in PRESERVED
                     if not os.path.exists(
                         os.path.join(PROJECT_ROOT, "01_blender", n))]
check("all earlier-phase .blend files preserved (v01..v07)",
      not missing_preserved, f"missing: {missing_preserved}")


# Exports
EXPORT_PATHS = [
    "02_exports/fbx/AK47_exterior_prop_visual.fbx",
    "02_exports/glb/AK47_exterior_prop_visual.glb",
    "02_exports/obj/AK47_exterior_prop_visual.obj",
    "02_exports/obj/AK47_exterior_prop_visual.mtl",
]
missing_exp = [p for p in EXPORT_PATHS if file_size(p) < 1024]
check("FBX/GLB/OBJ/MTL exports present + > 1 KB", not missing_exp,
      f"bad: {missing_exp}")


# Textures
for group in ("metal", "wood", "magazine", "grip", "shared"):
    check(f"03_textures/{group}/README.txt present",
          file_size(f"03_textures/{group}/README.txt") > 0)


# C. Documentation
REQUIRED_DOCS = [
    "readme.txt", "asset_notes.txt", "material_notes.txt",
    "texture_notes.txt", "render_notes.txt", "export_notes.txt",
    "scope_and_safety_note.txt", "handover_checklist.txt",
    "version_history.txt",
]
missing_docs = [n for n in REQUIRED_DOCS
                if file_size(f"06_documentation/{n}") <= 0]
check("all 9 required docs present in 06_documentation/",
      not missing_docs, f"missing: {missing_docs}")


# Public pack
REQUIRED_PUBLIC = [
    "public_description.txt", "portfolio_captions.txt",
    "selected_render_list.txt", "project_summary_short.txt",
    "project_summary_long.txt",
]
missing_pub = [n for n in REQUIRED_PUBLIC
               if file_size(f"07_public_pack/{n}") <= 0]
check("all 5 public_pack files present", not missing_pub,
      f"missing: {missing_pub}")


# D. Safety / scope — negation-aware forbidden-word check
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


# handover_checklist.txt contains a META report that lists the forbidden
# token strings verbatim — skip it to avoid self-flagging.
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
check("no forbidden wording (negation-aware) in any delivery .txt",
      not forbidden_hits, f"hits: {forbidden_hits[:5]}")


# Scope statement in scope_and_safety_note.txt — collapse whitespace so
# wrapped phrases like "visual\nrendering" still match.
import re as _re
ssn = os.path.join(DOCS, "scope_and_safety_note.txt")
ssn_ok = False
if os.path.exists(ssn):
    with open(ssn, "r", encoding="utf-8") as f:
        text = _re.sub(r"\s+", " ", f.read().lower())
    ssn_ok = ("non-functional" in text and "exterior" in text
              and "visual rendering" in text)
check("scope_and_safety_note.txt mentions non-functional + exterior + visual rendering",
      ssn_ok)


# Handover checklist gate
hc = os.path.join(DOCS, "handover_checklist.txt")
hc_ok = False
if os.path.exists(hc):
    with open(hc, "r", encoding="utf-8") as f:
        text = f.read()
    hc_ok = "Phase 8 quality gate: PASS" in text
check("handover_checklist.txt reports 'Phase 8 quality gate: PASS'",
      hc_ok)


# Archive notes
check("08_archive_notes/archive_contents.txt present",
      file_size("08_archive_notes/archive_contents.txt") > 0)
check("08_archive_notes/excluded_from_archive.txt present",
      file_size("08_archive_notes/excluded_from_archive.txt") > 0)


# E. Archive zip — optional in verify (created by section8_archive.py)
import glob
zips = sorted(glob.glob(os.path.join(
    PROJECT_ROOT, "AK47_NonFunctional_Prop_final_delivery_*.zip")))
check("project-root delivery archive zip exists (created by archive script)",
      len(zips) >= 1, f"found: {[os.path.basename(z) for z in zips]}")
if zips:
    z = zips[-1]
    # Test the zip integrity + contents
    try:
        with zipfile.ZipFile(z, "r") as zf:
            bad = zf.testzip()
            names = zf.namelist()
        check(f"archive integrity OK ({os.path.basename(z)})", bad is None,
              f"bad: {bad}")
        check("archive contains 01_blender_final/AK47_exterior_prop_final.blend",
              any(n.endswith(
                  "01_blender_final/AK47_exterior_prop_final.blend")
                  for n in names))
        # Count the renders inside
        full_count = sum(1 for n in names
                         if "/04_final_renders/full_model/" in n
                         and n.endswith(".png"))
        close_count = sum(1 for n in names
                          if "/04_final_renders/closeups/" in n
                          and n.endswith(".png"))
        check(f"archive contains 4 full_model stills (got {full_count})",
              full_count == 4)
        check(f"archive contains 7 close-up stills (got {close_count})",
              close_count == 7)
    except Exception as e:
        check("archive readable", False, str(e))


# Print
all_pass = True
for label, ok, detail in results:
    mark = "[X]" if ok else "[ ]"
    print(f"  {mark} {label}")
    if not ok and detail:
        print(f"        -> {detail}")
    if not ok:
        all_pass = False

print(f"\n=== {'PASS' if all_pass else 'FAIL'} ===\n")

# Summary
def count(rel):
    return len(list_pngs(rel))

print(f"Delivery folder summary:")
print(f"  full_model        : {count('04_final_renders/full_model')}/4 PNGs")
print(f"  closeups          : {count('04_final_renders/closeups')}/7 PNGs")
print(f"  clay/wireframe    : {count('04_final_renders/clay_wireframe_optional')}/3 PNGs")
print(f"  portfolio_selected: {count('04_final_renders/portfolio_selected')}/5 PNGs")
print(f"  turntable frames  : {count('05_turntable/turntable_frames')} PNGs")
exp_n = sum(1 for p in EXPORT_PATHS if file_size(p) > 0)
print(f"  exports           : {exp_n}/{len(EXPORT_PATHS)} files")
print(f"  docs              : {sum(1 for n in REQUIRED_DOCS if file_size(f'06_documentation/{n}') > 0)}/{len(REQUIRED_DOCS)} files")
print(f"  public_pack       : {sum(1 for n in REQUIRED_PUBLIC if file_size(f'07_public_pack/{n}') > 0)}/{len(REQUIRED_PUBLIC)} files")
