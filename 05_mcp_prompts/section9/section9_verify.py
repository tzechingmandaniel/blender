"""Verify the post_delivery/ package against the §9.24 final checklist.

Plain Python — no Blender required.
"""
import os
import glob
import zipfile

PROJECT_ROOT = os.environ.get(
    "AK47_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

POST = os.path.join(PROJECT_ROOT, "post_delivery")

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

REQUIRED_FILES = [
    "01_issue_tracker/post_delivery_issue_tracker.txt",
    "02_minor_corrections/minor_correction_workflow.txt",
    "03_version_updates/version_update_rules.txt",
    "04_portfolio_case_study/portfolio_case_study_outline.txt",
    "04_portfolio_case_study/portfolio_case_study_draft.txt",
    "05_public_safe_pack/public_wording_review.txt",
    "06_selected_portfolio_renders/portfolio_selection_notes.txt",
    "07_workflow_retrospective/workflow_retrospective.txt",
    "09_next_project_notes/next_project_recommendations.txt",
    "10_post_delivery_archive/post_delivery_archive_contents.txt",
]

REQUIRED_TEMPLATES = [
    "folder_structure_template.txt",
    "phase_workflow_template.txt",
    "mcp_prompt_template.txt",
    "issue_tracker_template.txt",
    "render_checklist_template.txt",
    "export_checklist_template.txt",
    "handover_checklist_template.txt",
    "public_wording_template.txt",
    "retrospective_template.txt",
]

PORTFOLIO_RENDERS = [
    "02_front_3quarter_hero.png",
    "01_side_profile.png",
    "05_closeup_receiver_metal.png",
    "06_closeup_wood_stock.png",
    "08_closeup_magazine.png",
    "10_closeup_grip.png",
    "turntable_ak_style_exterior_prop.mp4",
]

print("\n=== §9.24 FINAL POST-DELIVERY CHECKLIST ===")
results = []


def check(label, ok, detail=""):
    results.append((label, ok, detail))


def file_size(rel):
    p = os.path.join(POST, rel)
    if not os.path.exists(p):
        return -1
    return os.path.getsize(p)


# Folder structure
check("post_delivery/ exists", os.path.isdir(POST))
missing_folders = [f for f in LEAF_FOLDERS
                   if not os.path.isdir(os.path.join(POST, f))]
check("all 10 leaf folders exist", not missing_folders,
      f"missing: {missing_folders}")

# Required text files
for rel in REQUIRED_FILES:
    check(f"{rel} exists + non-empty", file_size(rel) > 0)

# Templates
for tpl in REQUIRED_TEMPLATES:
    rel = f"08_reusable_templates/{tpl}"
    check(f"template {tpl} exists + non-empty", file_size(rel) > 0)

# Portfolio renders + MP4 copied across
for fn in PORTFOLIO_RENDERS:
    rel = f"06_selected_portfolio_renders/{fn}"
    sz = file_size(rel)
    if fn.endswith(".mp4"):
        check(f"portfolio MP4 {fn} present (> 100 KB)", sz > 100_000)
    else:
        check(f"portfolio still {fn} present (> 100 KB)", sz > 100_000)

# Templates are de-namespaced (no AK47_NonFunctional_Prop)
de_namespace_hits = []
for tpl in REQUIRED_TEMPLATES:
    rel = f"08_reusable_templates/{tpl}"
    p = os.path.join(POST, rel)
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    if "AK47_NonFunctional_Prop" in text:
        de_namespace_hits.append(tpl)
check("templates are generic (no AK47_NonFunctional_Prop)",
      not de_namespace_hits, f"hits: {de_namespace_hits}")
# Templates SHOULD contain placeholder
no_placeholder = []
for tpl in REQUIRED_TEMPLATES:
    rel = f"08_reusable_templates/{tpl}"
    p = os.path.join(POST, rel)
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    # folder_structure_template uses ProjectName_NonFunctional_Prop;
    # other templates can use any safe generic phrasing
    if tpl == "folder_structure_template.txt" \
            and "ProjectName_NonFunctional_Prop" not in text:
        no_placeholder.append(tpl)
check("folder_structure_template uses ProjectName_NonFunctional_Prop placeholder",
      not no_placeholder)

# Scope reminder in every text file
no_scope = []
for dirpath, _, files in os.walk(POST):
    for fn in files:
        if not fn.endswith(".txt"):
            continue
        p = os.path.join(dirpath, fn)
        with open(p, "r", encoding="utf-8") as f:
            text = f.read().lower()
        if "non-functional" not in text and "scope reminder" not in text:
            rel = os.path.relpath(p, POST)
            no_scope.append(rel)
check("every post_delivery .txt mentions non-functional scope reminder",
      not no_scope, f"missing: {no_scope[:5]}")

# Negation-aware forbidden-word check (reused from Phase 8)
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

SCAN_SKIP_BASENAMES = {"handover_checklist.txt",
                       "post_delivery_issue_tracker.txt",
                       "public_wording_review.txt",
                       "public_wording_template.txt"}


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


forbidden_hits = []
for dirpath, _, files in os.walk(POST):
    for fn in files:
        if not fn.endswith(".txt"):
            continue
        if fn in SCAN_SKIP_BASENAMES:
            continue
        p = os.path.join(dirpath, fn)
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
        for tok in FORBIDDEN:
            if find_unsafe_hits(text, tok):
                rel = os.path.relpath(p, POST)
                forbidden_hits.append(f"{rel}:{tok}")
check("no forbidden wording (negation-aware) in post_delivery .txt",
      not forbidden_hits, f"hits: {forbidden_hits[:5]}")

# Issue tracker has the §9.4 fields and one initial entry
tracker_path = os.path.join(POST, "01_issue_tracker",
                             "post_delivery_issue_tracker.txt")
if os.path.exists(tracker_path):
    with open(tracker_path, "r", encoding="utf-8") as f:
        t = f.read()
    check("issue tracker has Issue ID + Category fields",
          "Issue ID" in t and "Category" in t)
    check("issue tracker has at least one entry (PD_INFO_001)",
          "PD_INFO_001" in t)
    check("issue tracker reports Blocking next steps : NO",
          "Blocking next steps : NO" in t)

# Retrospective has 6 sections
retro_path = os.path.join(POST, "07_workflow_retrospective",
                          "workflow_retrospective.txt")
if os.path.exists(retro_path):
    with open(retro_path, "r", encoding="utf-8") as f:
        r = f.read()
    sections_ok = all(s in r for s in (
        "WHAT WORKED WELL", "WHAT CAUSED PROBLEMS",
        "WHAT TO IMPROVE NEXT TIME", "WHAT SKILLS IMPROVED",
        "WHAT TO REUSE", "WHAT NOT TO REPEAT"))
    check("retrospective has all 6 §9.17 sections", sections_ok)

# Next project notes have 10 candidates
np_path = os.path.join(POST, "09_next_project_notes",
                       "next_project_recommendations.txt")
if os.path.exists(np_path):
    with open(np_path, "r", encoding="utf-8") as f:
        n = f.read()
    candidates_present = sum(1 for kw in (
        "toolbox", "camera", "radio", "control panel", "flashlight",
        "lantern", "controller", "robot", "keyboard", "scanner")
        if kw in n.lower())
    check(f"next_project_recommendations has all 10 §9.21 candidates "
          f"(found {candidates_present})", candidates_present == 10)

# Optional: archive zip in project root (only checked if exists)
zips = sorted(glob.glob(os.path.join(
    PROJECT_ROOT, "AK47_NonFunctional_Prop_post_delivery_*.zip")))
if zips:
    z = zips[-1]
    try:
        with zipfile.ZipFile(z, "r") as zf:
            bad = zf.testzip()
            names = zf.namelist()
        check(f"post-delivery archive integrity OK ({os.path.basename(z)})",
              bad is None)
        check("post-delivery archive contains post_delivery/ root",
              any(n.startswith("post_delivery/") for n in names))
    except Exception as e:
        check("post-delivery archive readable", False, str(e))
else:
    print("  (no post-delivery archive zip found yet — run section9_archive.py)")


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
print(f"post_delivery/ summary:")
print(f"  leaf folders               : {len(LEAF_FOLDERS) - len(missing_folders)}/{len(LEAF_FOLDERS)}")
print(f"  required text files        : {sum(1 for r in REQUIRED_FILES if file_size(r) > 0)}/{len(REQUIRED_FILES)}")
print(f"  reusable templates         : {sum(1 for t in REQUIRED_TEMPLATES if file_size('08_reusable_templates/' + t) > 0)}/{len(REQUIRED_TEMPLATES)}")
print(f"  portfolio renders + MP4    : {sum(1 for f in PORTFOLIO_RENDERS if file_size('06_selected_portfolio_renders/' + f) > 100_000)}/{len(PORTFOLIO_RENDERS)}")
