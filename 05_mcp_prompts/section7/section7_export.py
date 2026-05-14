"""Export AK_ prop to FBX / GLB / OBJ in 02_exports/.

Selects only objects in 09_EXPORT_READY (AK_ meshes + the
EXPORT_AK47_EXTERIOR_PROP_MASTER empty), then runs each exporter with
selection-only.
"""
import bpy
import os

PROJECT_ROOT = os.environ.get("AK47_PROJECT_ROOT", r"C:\AK47_NonFunctional_Prop")
EXPORTS_ROOT = os.path.join(PROJECT_ROOT, "02_exports")
os.makedirs(EXPORTS_ROOT, exist_ok=True)


def select_export_ready():
    bpy.ops.object.select_all(action='DESELECT')
    exp = bpy.data.collections.get("09_EXPORT_READY")
    if exp is None:
        print("ERROR: 09_EXPORT_READY not found")
        return False
    sel = 0
    for o in exp.objects:
        # Skip the master empty for OBJ (some exporters reject empties);
        # include for FBX/GLB which handle empties fine.
        o.select_set(True)
        sel += 1
    # Activate the first object so operators have a context
    if sel > 0:
        first = next(iter(exp.objects))
        bpy.context.view_layer.objects.active = first
    print(f"  selected {sel} objects from 09_EXPORT_READY")
    return sel > 0


# --- FBX ---
print("\n=== EXPORT: FBX ===")
if select_export_ready():
    fbx_path = os.path.join(EXPORTS_ROOT, "AK47_exterior_prop_visual.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        bake_space_transform=True,
        mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode='COPY',
        embed_textures=False,
        global_scale=1.0,
    )
    print(f"  wrote {fbx_path}")


# --- GLB ---
print("\n=== EXPORT: GLB ===")
if select_export_ready():
    glb_path = os.path.join(EXPORTS_ROOT, "AK47_exterior_prop_visual.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_apply=True,
        export_yup=True,
    )
    print(f"  wrote {glb_path}")


# --- OBJ ---
# OBJ exporter doesn't accept an empty object as a mesh — re-select only
# meshes from 09_EXPORT_READY.
print("\n=== EXPORT: OBJ ===")
bpy.ops.object.select_all(action='DESELECT')
exp = bpy.data.collections.get("09_EXPORT_READY")
sel = 0
if exp is not None:
    for o in exp.objects:
        if o.type == "MESH":
            o.select_set(True)
            sel += 1
    if sel > 0:
        bpy.context.view_layer.objects.active = next(
            o for o in exp.objects if o.type == "MESH")
print(f"  selected {sel} mesh objects for OBJ")
if sel > 0:
    obj_path = os.path.join(EXPORTS_ROOT, "AK47_exterior_prop_visual.obj")
    # Blender 4.x: wm.obj_export; Blender 5.1 also exposes this.
    bpy.ops.wm.obj_export(
        filepath=obj_path,
        export_selected_objects=True,
        export_uv=True,
        export_normals=True,
        export_materials=True,
        export_triangulated_mesh=True,
    )
    print(f"  wrote {obj_path}")

print("\ndone")
