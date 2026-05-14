"""Section 8 archive: zips final_delivery/ into the project root with a
date-stamped name, copies into 09_archive/, then extracts back into a
temp folder and verifies round-trip integrity.

Runs as plain Python — no Blender required.
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

DELIVERY = os.path.join(PROJECT_ROOT, "final_delivery")
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "09_archive")

if not os.path.isdir(DELIVERY):
    print(f"ABORT: final_delivery folder not found at {DELIVERY}")
    sys.exit(1)


# ---------- 1. Build the archive ----------
date_tag = datetime.date.today().strftime("%Y%m%d")
zip_name = f"AK47_NonFunctional_Prop_final_delivery_{date_tag}.zip"
zip_path = os.path.join(PROJECT_ROOT, zip_name)

print(f"\n=== SECTION 8 ARCHIVE: building {zip_name} ===")
file_count = 0
total_size = 0
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED,
                     compresslevel=6) as zf:
    for dirpath, dirnames, files in os.walk(DELIVERY):
        dirnames.sort()
        files.sort()
        for fn in files:
            src = os.path.join(dirpath, fn)
            # arcname rooted at final_delivery/
            arcname = "final_delivery/" + os.path.relpath(
                src, DELIVERY).replace("\\", "/")
            zf.write(src, arcname)
            file_count += 1
            total_size += os.path.getsize(src)

archive_size = os.path.getsize(zip_path)
print(f"  zipped {file_count} files  ({total_size:,} bytes raw -> "
      f"{archive_size:,} bytes zip)")


# ---------- 2. Copy archive into 09_archive/ ----------
os.makedirs(ARCHIVE_DIR, exist_ok=True)
backup_zip = os.path.join(ARCHIVE_DIR, zip_name)
shutil.copy2(zip_path, backup_zip)
print(f"  copied archive into {backup_zip}")


# ---------- 3. Extract-test ----------
print("\n=== SECTION 8 ARCHIVE: extract-test ===")
with tempfile.TemporaryDirectory(prefix="ak47_archive_test_") as tmp:
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                print(f"  FAIL: testzip reports bad entry: {bad}")
                sys.exit(2)
            zf.extractall(tmp)
        # Verify key files survived the round-trip
        extracted_root = os.path.join(tmp, "final_delivery")
        if not os.path.isdir(extracted_root):
            print(f"  FAIL: extracted final_delivery/ not found at {extracted_root}")
            sys.exit(3)
        # .blend
        ex_blend = os.path.join(extracted_root, "01_blender_final",
                                "AK47_exterior_prop_final.blend")
        src_blend = os.path.join(DELIVERY, "01_blender_final",
                                  "AK47_exterior_prop_final.blend")
        if not os.path.exists(ex_blend):
            print(f"  FAIL: extracted .blend missing")
            sys.exit(4)
        if os.path.getsize(ex_blend) != os.path.getsize(src_blend):
            print(f"  FAIL: extracted .blend size mismatch")
            sys.exit(5)
        # 14 stills
        full_dir = os.path.join(extracted_root, "04_final_renders",
                                "full_model")
        close_dir = os.path.join(extracted_root, "04_final_renders",
                                  "closeups")
        clay_dir = os.path.join(extracted_root, "04_final_renders",
                                 "clay_wireframe_optional")
        n_full = len([f for f in os.listdir(full_dir) if f.endswith(".png")])
        n_close = len([f for f in os.listdir(close_dir) if f.endswith(".png")])
        n_clay = len([f for f in os.listdir(clay_dir) if f.endswith(".png")])
        if n_full != 4:
            print(f"  FAIL: full_model count = {n_full}, expected 4")
            sys.exit(6)
        if n_close != 7:
            print(f"  FAIL: closeups count = {n_close}, expected 7")
            sys.exit(7)
        if n_clay != 3:
            print(f"  FAIL: clay/wireframe count = {n_clay}, expected 3")
            sys.exit(8)
        # 9 docs
        docs_dir = os.path.join(extracted_root, "06_documentation")
        REQUIRED = ["readme.txt", "asset_notes.txt", "material_notes.txt",
                    "texture_notes.txt", "render_notes.txt",
                    "export_notes.txt", "scope_and_safety_note.txt",
                    "handover_checklist.txt", "version_history.txt"]
        missing = [n for n in REQUIRED
                   if not os.path.exists(os.path.join(docs_dir, n))]
        if missing:
            print(f"  FAIL: missing docs after extract: {missing}")
            sys.exit(9)
        # readme contains scope phrase
        with open(os.path.join(docs_dir, "readme.txt"), "r",
                  encoding="utf-8") as f:
            readme = f.read().lower()
        if "non-functional" not in readme or "exterior" not in readme:
            print(f"  FAIL: readme.txt missing scope wording")
            sys.exit(10)
        print(f"  extract test PASSED")
        print(f"    .blend size match           : {os.path.getsize(ex_blend)} bytes")
        print(f"    full_model stills          : {n_full}/4")
        print(f"    closeup stills             : {n_close}/7")
        print(f"    clay/wireframe stills      : {n_clay}/3")
        print(f"    required docs              : {len(REQUIRED)}/9")
        print(f"    readme scope wording       : OK")
    except zipfile.BadZipFile as e:
        print(f"  FAIL: bad zip file: {e}")
        sys.exit(11)


print(f"\n=== SECTION 8 ARCHIVE DONE ===")
print(f"  archive : {zip_path}")
print(f"  backup  : {backup_zip}")
print(f"  size    : {archive_size:,} bytes")
print(f"  contains: {file_count} files")
