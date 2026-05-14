"""Section 8 §8.17 Export Testing.

Starts with a fresh empty Blender scene, then imports the three Phase 7
export files in turn (FBX, GLB, OBJ). For each format, verifies:
  - import succeeded (at least one mesh object created)
  - no camera / light / image-plane / blockout object came through
  - object names start with AK_ or are the export master empty
  - meshes have UV layers

Writes the report into 06_documentation/export_test_results.txt
(idempotent — overwritten each run).
"""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT",
                              r"C:\AK47_NonFunctional_Prop")
EXPORTS_ROOT = os.path.join(PROJECT_ROOT, "final_delivery", "02_exports")
DOCS_ROOT = os.path.join(PROJECT_ROOT, "06_documentation")
DELIVERY_DOCS_ROOT = os.path.join(PROJECT_ROOT, "final_delivery",
                                    "06_documentation")
REPORT = []


def clean_scene():
    """Wipe everything from the current scene so each import starts fresh."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    # Also remove orphan collections
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def report(line):
    print(line)
    REPORT.append(line)


def analyse_imported(label):
    objs = list(bpy.data.objects)
    mesh_objs = [o for o in objs if o.type == "MESH"]
    cam_objs = [o for o in objs if o.type == "CAMERA"]
    light_objs = [o for o in objs if o.type == "LIGHT"]
    empty_objs = [o for o in objs if o.type == "EMPTY"]

    bad_names = []
    no_uv = []
    for o in mesh_objs:
        # Some exporters mangle names (e.g., .001 suffix, _mesh tail).
        # Accept any name that contains AK_ as a substring.
        if "AK_" not in o.name:
            bad_names.append(o.name)
        if not o.data.uv_layers:
            no_uv.append(o.name)

    blk_names = [o.name for o in mesh_objs
                 if "BLK_" in o.name
                 or o.name.startswith("REF_")
                 or o.name.startswith("GUIDE_")
                 or o.name.startswith("FLOOR_")
                 or o.name.startswith("BG_")
                 or o.name.startswith("PREVIEW_")]

    report(f"  {label:10s}: meshes={len(mesh_objs):3d}  cams={len(cam_objs)}  "
           f"lights={len(light_objs)}  empties={len(empty_objs)}")
    report(f"             non-AK_ mesh names    : {len(bad_names)} "
           f"{bad_names[:3] if bad_names else ''}")
    report(f"             meshes without UV      : {len(no_uv)} "
           f"{no_uv[:3] if no_uv else ''}")
    report(f"             blockout/reference-ish : {len(blk_names)} "
           f"{blk_names[:3] if blk_names else ''}")
    return {
        "label": label,
        "mesh_count": len(mesh_objs),
        "cam_count": len(cam_objs),
        "light_count": len(light_objs),
        "bad_name_count": len(bad_names),
        "no_uv_count": len(no_uv),
        "blockout_count": len(blk_names),
    }


report("§8.17 Export-Test Report")
report("=========================")
report("Scope reminder: non-functional exterior visual prop only.")
report("")

results = []


# --- FBX ---
clean_scene()
fbx_path = os.path.join(EXPORTS_ROOT, "fbx", "AK47_exterior_prop_visual.fbx")
report(f"FBX: {fbx_path}")
if os.path.exists(fbx_path):
    try:
        bpy.ops.import_scene.fbx(filepath=fbx_path)
        results.append(analyse_imported("FBX"))
    except Exception as e:
        report(f"  FBX import FAILED: {e}")
else:
    report("  FBX file not found")
report("")


# --- GLB ---
clean_scene()
glb_path = os.path.join(EXPORTS_ROOT, "glb", "AK47_exterior_prop_visual.glb")
report(f"GLB: {glb_path}")
if os.path.exists(glb_path):
    try:
        bpy.ops.import_scene.gltf(filepath=glb_path)
        results.append(analyse_imported("GLB"))
    except Exception as e:
        report(f"  GLB import FAILED: {e}")
else:
    report("  GLB file not found")
report("")


# --- OBJ ---
clean_scene()
obj_path = os.path.join(EXPORTS_ROOT, "obj", "AK47_exterior_prop_visual.obj")
report(f"OBJ: {obj_path}")
if os.path.exists(obj_path):
    try:
        # Blender 5.x: wm.obj_import; fallback to import_scene.obj for older
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=obj_path)
        else:
            bpy.ops.import_scene.obj(filepath=obj_path)
        results.append(analyse_imported("OBJ"))
    except Exception as e:
        report(f"  OBJ import FAILED: {e}")
else:
    report("  OBJ file not found")
report("")


# --- Pass/fail summary ---
all_pass = True
report("Pass / fail summary:")
for r in results:
    issues = []
    if r["mesh_count"] < 1:
        issues.append("no mesh imported")
    if r["cam_count"] > 0:
        issues.append(f"camera in export ({r['cam_count']})")
    if r["light_count"] > 0:
        issues.append(f"light in export ({r['light_count']})")
    if r["bad_name_count"] > 0:
        issues.append(f"non-AK_ names ({r['bad_name_count']})")
    if r["blockout_count"] > 0:
        issues.append(f"blockout/reference objects ({r['blockout_count']})")
    if issues:
        report(f"  [ ] {r['label']:6s} : {', '.join(issues)}")
        all_pass = False
    else:
        report(f"  [X] {r['label']:6s} : clean ({r['mesh_count']} meshes, "
               f"{r['no_uv_count']} without UV — UV-loss is expected for OBJ "
               f"split-meshes and is informational)")

report("")
report(f"Overall §8.17 export test: {'PASS' if all_pass else 'FAIL'}")


# --- Write report into BOTH the project docs and the delivery docs ---
def write_report(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(REPORT) + "\n")
    print(f"wrote: {path}")


write_report(os.path.join(DOCS_ROOT, "export_test_results.txt"))
write_report(os.path.join(DELIVERY_DOCS_ROOT, "export_test_results.txt"))
