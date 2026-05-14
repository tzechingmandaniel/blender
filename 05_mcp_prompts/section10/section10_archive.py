"""Section 10 archive: zips advanced_presentation_pack/ into the project
root with a date-stamped name, copies into 09_archive/, then extracts
back into a temp folder and verifies round-trip integrity.

Plain Python — no Blender required.
"""
import os
import shutil
import zipfile
import datetime
import tempfile
import sys

PROJECT_ROOT = os.environ.get(
    "AK47_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

PACK = os.path.join(PROJECT_ROOT, "advanced_presentation_pack")
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "09_archive")

if not os.path.isdir(PACK):
    print(f"ABORT: advanced_presentation_pack/ not found at {PACK}")
    sys.exit(1)

date_tag = datetime.date.today().strftime("%Y%m%d")
zip_name = f"AK47_NonFunctional_Prop_advanced_presentation_pack_{date_tag}.zip"
zip_path = os.path.join(PROJECT_ROOT, zip_name)

print(f"\n=== SECTION 10 ARCHIVE: building {zip_name} ===")
file_count = 0
total_raw = 0
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED,
                     compresslevel=6) as zf:
    for dirpath, dirnames, files in os.walk(PACK):
        dirnames.sort()
        files.sort()
        for fn in files:
            src = os.path.join(dirpath, fn)
            arcname = "advanced_presentation_pack/" + os.path.relpath(
                src, PACK).replace("\\", "/")
            zf.write(src, arcname)
            file_count += 1
            total_raw += os.path.getsize(src)

archive_size = os.path.getsize(zip_path)
print(f"  zipped {file_count} files  "
      f"({total_raw:,} bytes raw -> {archive_size:,} bytes zip)")

os.makedirs(ARCHIVE_DIR, exist_ok=True)
backup_zip = os.path.join(ARCHIVE_DIR, zip_name)
shutil.copy2(zip_path, backup_zip)
print(f"  copied archive into {backup_zip}")


# --- Extract test ---
print("\n=== SECTION 10 ARCHIVE: extract-test ===")
with tempfile.TemporaryDirectory(prefix="ak47_pres_test_") as tmp:
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            print(f"  FAIL: testzip reports bad entry: {bad}")
            sys.exit(2)
        zf.extractall(tmp)
    ex_root = os.path.join(tmp, "advanced_presentation_pack")
    if not os.path.isdir(ex_root):
        print("  FAIL: extracted advanced_presentation_pack/ not found")
        sys.exit(3)
    KEY_FILES = [
        "01_portfolio_page/portfolio_page_plan.txt",
        "02_website_case_study/website_case_study_plan.txt",
        "05_image_sequence/final_image_sequence.txt",
        "08_submission_pack/file_inventory.txt",
        "09_reusable_presentation_template/presentation_template.txt",
        "10_publication_checklist/final_presentation_quality_gate.txt",
    ]
    missing = [k for k in KEY_FILES
               if not os.path.exists(os.path.join(ex_root, k))]
    if missing:
        print(f"  FAIL: missing after extract: {missing}")
        sys.exit(4)
    print(f"  extract test PASSED — all {len(KEY_FILES)} key files survive")


print(f"\n=== SECTION 10 ARCHIVE DONE ===")
print(f"  archive : {zip_path}")
print(f"  backup  : {backup_zip}")
print(f"  size    : {archive_size:,} bytes")
print(f"  contains: {file_count} files")
