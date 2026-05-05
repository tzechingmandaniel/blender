"""Section 2 supplement — fills the gaps from re-reading the .tex:
  §2.8.9 — adds BLK_gas_block_visual and BLK_front_ring_visual
  §2.5.1 step 14 — creates AK47_master empty + parents all BLK_ to it
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix

PROJECT_ROOT = r"C:\AK47_NonFunctional_Prop"
BLEND = os.path.join(PROJECT_ROOT, "01_blender", "v02_blockout.blend")

bpy.ops.wm.open_mainfile(filepath=BLEND)


def get_collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def link_only_to(obj, collection_name):
    target = get_collection(collection_name)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)


def assign_material(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def add_bevel_and_weighted_normals(obj, width=0.002, segments=2, angle_deg=30):
    bev = obj.modifiers.new("Bevel", type="BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(angle_deg)
    wn = obj.modifiers.new("WeightedNormal", type="WEIGHTED_NORMAL")
    wn.weight = 50
    wn.thresh = 0.01
    wn.keep_sharp = True


def add_box_bm(bm, dims, location=(0, 0, 0)):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=dims, verts=ret["verts"])
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])


def add_cyl_bm(bm, radius, depth, segments=24, axis="Z", location=(0, 0, 0)):
    ret = bmesh.ops.create_cone(
        bm, segments=segments, radius1=radius, radius2=radius,
        depth=depth, cap_ends=True, cap_tris=False,
    )
    if axis == "X":
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                          matrix=Matrix.Rotation(math.radians(90), 4, "Y"),
                          verts=ret["verts"])
    bmesh.ops.translate(bm, vec=location, verts=ret["verts"])


def make_object(name, build, location=(0, 0, 0)):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bm = bmesh.new()
    build(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    return obj


# ---------- §2.8.9 missing front assembly parts ----------
def build_gas_block(bm):
    """Visual gas block — small box clamped around barrel between handguard and front sight."""
    add_box_bm(bm, dims=(0.025, 0.030, 0.030), location=(0, 0, 0))
    # Cleaning rod boss underneath
    add_cyl_bm(bm, radius=0.004, depth=0.026, segments=10, axis="X", location=(0, 0, -0.014))


def build_front_ring(bm):
    """Visual band ring around the barrel — exterior decorative collar at the muzzle end."""
    add_cyl_bm(bm, radius=0.014, depth=0.012, segments=24, axis="X", location=(0, 0, 0))


print("\n=== SECTION 2 SUPPLEMENT ===")

# Gas block sits between upper handguard end (X=0.215) and front sight (X=0.405)
gas_block = make_object("BLK_gas_block_visual", build_gas_block, location=(0.290, 0.0, 0.045))
add_bevel_and_weighted_normals(gas_block)
assign_material(gas_block, "MAT_placeholder_dark_metal")
link_only_to(gas_block, "02_BLOCKOUT")
print(f"  built BLK_gas_block_visual: {len(gas_block.data.vertices)}v")

# Front ring sits at the muzzle end, just before the front sight
front_ring = make_object("BLK_front_ring_visual", build_front_ring, location=(0.380, 0.0, 0.020))
add_bevel_and_weighted_normals(front_ring, width=0.0015, segments=2)
assign_material(front_ring, "MAT_placeholder_dark_metal")
link_only_to(front_ring, "02_BLOCKOUT")
print(f"  built BLK_front_ring_visual: {len(front_ring.data.vertices)}v")


# ---------- §2.5.1 step 14: final assembly preparation ----------
# Create a master empty and parent every BLK_ object to it. This makes the prop
# transformable as a single unit while individual parts stay editable.
master_name = "AK47_MASTER_ASSET"
master = bpy.data.objects.get(master_name)
if master is None:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    master = bpy.context.active_object
    master.name = master_name
    master.empty_display_size = 0.30

# Move master to 07_ASSEMBLY collection (per Section 1's collection scheme)
link_only_to(master, "07_ASSEMBLY")

parented = 0
for o in bpy.data.objects:
    if o.name.startswith("BLK_") and o.parent is None:
        o.parent = master
        # Keep current world transform after parenting (set inverse)
        o.matrix_parent_inverse = master.matrix_world.inverted()
        parented += 1
print(f"  AK47_MASTER_ASSET created; parented {parented} BLK_ objects")


bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print(f"saved: {BLEND}")
