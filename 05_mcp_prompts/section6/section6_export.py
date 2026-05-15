"""Export the 09_EXPORT_READY collection from v06_final_assembly.blend to
FBX / GLB / OBJ for game-prop or portfolio use.

Auto-detects repo root from __file__. All exports are exterior-visual-only;
no functional or internal geometry is included.
"""
import bpy
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
FBX_OUT = os.path.join(PROJECT_ROOT, "02_exports", "fbx", "AK47_exterior_prop_visual.fbx")
GLB_OUT = os.path.join(PROJECT_ROOT, "02_exports", "glb", "AK47_exterior_prop_visual.glb")
OBJ_OUT = os.path.join(PROJECT_ROOT, "02_exports", "obj", "AK47_exterior_prop_visual.obj")
for p in (FBX_OUT, GLB_OUT, OBJ_OUT):
    os.makedirs(os.path.dirname(p), exist_ok=True)

export_coll = bpy.data.collections.get("09_EXPORT_READY")
if export_coll is None:
    raise RuntimeError("09_EXPORT_READY missing; run section6_executor.py first")

# Select only AK_ meshes from the export collection
bpy.ops.object.select_all(action="DESELECT")
selected_count = 0
for o in export_coll.objects:
    if o.type == "MESH" and o.name.startswith("AK_"):
        # Unhide briefly so export selection works
        o.hide_set(False)
        o.select_set(True)
        selected_count += 1
if selected_count == 0:
    raise RuntimeError("09_EXPORT_READY contains no AK_ meshes")

print(f"\n=== SECTION 6 — EXPORTS ({selected_count} objects) ===")

# FBX
try:
    bpy.ops.export_scene.fbx(
        filepath=FBX_OUT,
        use_selection=True,
        apply_scale_options="FBX_SCALE_ALL",
        bake_space_transform=True,
        object_types={"MESH"},
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        path_mode="COPY",
        embed_textures=False,
    )
    print(f"  fbx -> {FBX_OUT}  ({os.path.getsize(FBX_OUT) // 1024} KB)")
except Exception as e:
    print(f"  FBX failed: {e}")

# GLB
try:
    bpy.ops.export_scene.gltf(
        filepath=GLB_OUT,
        use_selection=True,
        export_format="GLB",
        export_apply=True,
    )
    print(f"  glb -> {GLB_OUT}  ({os.path.getsize(GLB_OUT) // 1024} KB)")
except Exception as e:
    print(f"  GLB failed: {e}")

# OBJ — Blender 5.x uses bpy.ops.wm.obj_export (the new operator)
try:
    if hasattr(bpy.ops.wm, "obj_export"):
        bpy.ops.wm.obj_export(
            filepath=OBJ_OUT,
            export_selected_objects=True,
            apply_modifiers=True,
        )
    else:
        # Fallback for older Blender that still has export_scene.obj
        bpy.ops.export_scene.obj(
            filepath=OBJ_OUT,
            use_selection=True,
            use_mesh_modifiers=True,
        )
    print(f"  obj -> {OBJ_OUT}  ({os.path.getsize(OBJ_OUT) // 1024} KB)")
except Exception as e:
    print(f"  OBJ failed: {e}")

print("=== EXPORTS DONE ===")
