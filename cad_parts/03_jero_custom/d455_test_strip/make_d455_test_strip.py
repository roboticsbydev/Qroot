"""D455 aperture test strip: just the front face, 2 mm thick, one round flared opening per optical element,
a perforated dot pattern for looks, and a 3 mm lip that hooks over the camera's front edge so the openings
line up with the lenses. Proves the future head face won't block any view.

Optical layout, openings and dots come from ../d455_optics.py (shared with the head face plate).
Frame: the local optics frame described there (front face y=0, lens axis z=0).

Run with FreeCAD 1.1's bundled Python:
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" cad_parts/03_jero_custom/d455_test_strip/make_d455_test_strip.py
"""

import math
import sys
from pathlib import Path

sys.path.append(r"C:\Program Files\FreeCAD 1.1\bin")
HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent))
import d455_optics as opt
import FreeCAD  # noqa: F401  (sets up the module path for MeshPart/Part)
import MeshPart
import Part

FRONT_T = 2.0      # front face wall: the head's real wall thickness
RIM_T = 1.6        # locating lip around the camera's front edge
RIM_DEPTH = 3.0    # set 0 for a bare flat strip
FLAT_T = 1.2       # plain variant: no dots, thinner face (6 layers at 0.2), quicker view test


def build(front_t=FRONT_T, dotted=True):
    W, H = opt.CAM_W + 2 * RIM_T, opt.CAM_H + 2 * RIM_T
    s = opt.stadium(W, H, -front_t, 0.0)
    if RIM_DEPTH > 0:
        s = s.fuse(opt.lip(RIM_T, RIM_DEPTH))
    for f in opt.funnels(front_t):
        s = s.cut(f)
    if not dotted:
        return s.removeSplitter()
    R, a = H / 2, (W - H) / 2

    def inside(x, z, margin):
        return math.hypot(max(abs(x) - a, 0.0), z) <= R - margin

    holes = opt.dot_holes(inside, (-W / 2, W / 2), (-H / 2, H / 2), front_t)
    print(f"decorative holes: {len(holes)}")
    return s.cut(Part.makeCompound(holes)).removeSplitter()


def report_walls(front_t=FRONT_T):
    d = 2 * opt.r_at(-front_t)
    sx, shw, shh = opt.slot_box(-front_t)
    print(f"imager openings: D{d:.1f} outside, D{2 * opt.r_at(0):.1f} inside")
    print(f"projector + RGB slot: {2 * shw:.1f} x {2 * shh:.1f} outside, corner R{opt.SLOT_CORNER * shh:.1f}")
    for n in ("left_imager", "right_imager"):
        gap = abs(opt.ELEMENTS[n] - sx) - shw - d / 2
        print(f"  wall between {n} and the slot: {gap:.1f} mm")
    print(f"  wall above and below the slot: {(opt.CAM_H + 2 * RIM_T) / 2 - shh:.1f} mm")


if __name__ == "__main__":
    for name, front_t, dotted in (("d455_test_strip", FRONT_T, True), ("d455_test_strip_flat", FLAT_T, False)):
        print(f"--- {name}: face {front_t} mm, {'dotted' if dotted else 'plain'}")
        report_walls(front_t)
        solid = build(front_t, dotted)
        assert solid.isValid() and len(solid.Solids) == 1, "invalid or multi-body result"
        solid.check(True)
        out = HERE / name
        MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.02, AngularDeflection=0.2).write(str(out.with_suffix(".stl")))
        solid.exportStep(str(out.with_suffix(".step")))
        bb = solid.BoundBox
        print(f"volume {solid.Volume:.0f} mm^3, bbox {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} -> {out.name}.stl/.step")
