"""Re-cut the bearing parts for a 6002Z (15 x 32 x 9) instead of the stock 20 x 32 x 7.

Rule: the flange-side face of every bearing stays where it was, so no joint moves
(MuJoCo model / trained policy stay valid). Each seat grows 2 mm away from the flange,
and each shaft drops 20 -> 15 mm nominal, keeping its original undersize.

Run with FreeCAD 1.1's bundled Python (the venv Python is a different build and cannot import FreeCAD):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" cad_parts/05_bearing_6002z/make_6002z_parts.py
All coordinates are the shared assembly frame the upstream STLs are exported in, in mm.
"""

import sys
from pathlib import Path

sys.path.append(r"C:\Program Files\FreeCAD 1.1\bin")
import FreeCAD as App
import Mesh
import MeshPart
import Part

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "01_printed_parts_upstream"
V = App.Vector

X, Z = V(1, 0, 0), V(0, 0, 1)


def load_solid(name, src=SRC):
    mesh = Mesh.Mesh(str(src / f"{name}.stl"))
    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh.Topology, 0.01)
    solid = Part.Solid(Part.Shell(shape.Faces))
    if solid.Volume < 0:
        solid.reverse()
    return solid


def cyl(r, a0, a1, axis, c1, c2):
    """Cylinder radius r spanning axial coords a0..a1 along X or Z, centred at (c1, c2)."""
    base = V(a0, c1, c2) if axis == X else V(c1, c2, a0)
    return Part.makeCylinder(r, a1 - a0, base, axis)


def tube(r_in, r_out, a0, a1, axis, c1, c2):
    return cyl(r_out, a0, a1, axis, c1, c2).cut(cyl(r_in, a0, a1, axis, c1, c2))


def cone(r0, r1, a0, a1, axis, c1, c2):
    base = V(a0, c1, c2) if axis == X else V(c1, c2, a0)
    return Part.makeCone(r0, r1, a1 - a0, base, axis)


def save(name, solid):
    solid = solid.removeSplitter()
    assert solid.isValid(), f"{name}: invalid solid"
    out = HERE / f"{name}_6002z"
    mesh = MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.02, AngularDeflection=0.2)
    mesh.write(str(out.with_suffix(".stl")))
    solid.exportStep(str(out.with_suffix(".step")))
    print(f"{name}: volume {solid.Volume:.0f} mm^3 -> {out.name}.stl/.step")


def roll_motor_bottom():
    # Hip-yaw shaft, axis Z at (0, 35). Old: solid D19.9 z -85.18..-78.18, flange from -78.18.
    s = load_solid("roll_motor_bottom")
    s = s.cut(tube(7.45, 10.8, -86.0, -78.18, Z, 0, 35))           # drop the old D19.9 shaft
    s = s.fuse(cyl(7.45, -86.68, -78.0, Z, 0, 35))                  # D14.9 shaft, 9 mm bearing span
    s = s.fuse(cone(6.95, 7.45, -87.18, -86.68, Z, 0, 35))          # 0.5 mm lead-in chamfer, tip -87.18
    return s


def trunk_bottom():
    # Two hip seats, axis Z at (0, +/-35). Old: lip -88.78..-85.28 (D26.2 hole), pocket D32.2 up to -79.78.
    # body_middle_bottom sits flush under -88.78, so the seat grows down into the lip: lip -> 1.5 mm.
    s = load_solid("trunk_bottom")
    for y in (35, -35):
        # ends exactly on the old floor plane: overlapping the faceted pocket wall leaves sliver faces
        s = s.cut(cyl(16.1, -87.28, -85.28, Z, 0, y))
    return s


def recut_neck_seat(s, dx=0.0, cy=0.0, cz=129.1, past_lip=0.0):
    # Neck seat, axis X at (y 0, z 129.1). Old: lip x -30..-28.1 (D28 hole), pocket D32.2 to -21.
    # Space outside the lip is clear, so the old lip is cut away and rebuilt 2 mm further out.
    # remove old lip (ends on its top plane). r16.15 not 16.1: a true r16.1 cylinder grazes the faceted
    # r16.1 wall within 0.01 mm and leaves non-manifold slivers; 0.05 mm extra is a clean step instead.
    # past_lip: on head_face_draft, stopping exactly on the old lip-top plane leaves a zero-thickness
    # edge ring at the old D28 hole, so that mesh cuts 0.1 mm past it.
    s = s.cut(cyl(16.15, dx - 30.1, dx - 28.1 + past_lip, X, cy, cz))
    s = s.fuse(tube(14.0, 19.0, dx - 32.0, dx - 30.1, X, cy, cz))   # new 1.9 mm lip, D28 hole
    s = s.fuse(tube(16.1, 19.0, dx - 30.2, dx - 29.5, X, cy, cz))   # sleeve bonding new lip to old wall
    return s


def head():
    return recut_neck_seat(load_solid("head"))


def head_face_draft():
    # Jero's D455 head draft (cad/rb3_realsense/build_head_draft.py) carries the same neck seat,
    # shifted to lip x -49..-47.1, axis (y 0.1, z 193.9). head_floor/d455_cradle drafts are clear of the new lip.
    return recut_neck_seat(load_solid("head_face_draft", HERE.parent / "03_jero_custom"), dx=-19.0, cy=0.1, cz=193.9, past_lip=0.1)


def head_yaw_to_roll():
    # Neck shaft, axis X at (y 0, z 129.1). Old: D19.8 x -27..-20 (chamfered tip), flange from -20.
    s = load_solid("head_yaw_to_roll")
    s = s.cut(tube(7.4, 10.8, -27.5, -20.0, X, 0, 129.1))
    s = s.fuse(cyl(7.4, -28.5, -19.8, X, 0, 129.1))                 # D14.8 shaft
    s = s.fuse(cone(6.9, 7.4, -29.0, -28.5, X, 0, 129.1))           # chamfer, tip -29 (1.1 short of lip, as before)
    return s


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for fn in (roll_motor_bottom, head_yaw_to_roll, trunk_bottom, head, head_face_draft):
        if not only or fn.__name__ in only:
            save(fn.__name__, fn())
