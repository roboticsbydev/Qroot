"""D455 optical layout and the aperture / perforation geometry shared by the test strip and the head face plate.

Source: RealSense D400 datasheet 337029-017, Fig. 10-12 (D455 drawing), Table 3-53, Tables 3-14/3-17/3-19.
  Body 124 W x 29 H x 26 D (D tolerance 25.5..26.5), stadium outline (R14.5 ends).
  Front view, from the LEFT imager (viewer's right): projector 37.5, RGB 59, right imager 95.
  2x M4 on the back at the imager positions, mid-height, max insertion 4 mm, 0.4 Nm.
  FOV: imagers 90x64 (+/-1), RGB 90x65, projector 90x63 (+/-3).

Local frame (mm): x = viewer's right looking at the camera front, y = into the camera (front face y=0),
z = up, lens axis z=0. The lens height is NOT dimensioned on the drawing (assumed mid-height): check
with calipers. Callers place this frame with `place()`.

Import from a script run with FreeCAD 1.1's bundled Python (FreeCAD must already be on sys.path).
"""

import math

import FreeCAD as App
import Part

V = App.Vector

CAM_W, CAM_H, CAM_D = 124.5 + 0.3, 29.5 + 0.3, 26.5 + 0.3   # max tolerance + fit clearance
ELEMENTS = {            # name: x of centre in the local frame
    "left_imager": 47.5,
    "projector": 47.5 - 37.5,
    "rgb": 47.5 - 59.0,
    "right_imager": 47.5 - 95.0,
}
M4_X = (47.5, -47.5)    # rear M4 points, on the lens axis height
HALF_DEG = 53.0         # imager openings (round): the frame corners sit at 48-49 deg off axis; 49 left no margin
SLOT_HALF_DEG = 56.0    # projector + RGB share one rounded-rectangle opening; the projector has to light what both
                        # imagers see from their offset positions, so it gets the widest cone
SLOT = ("projector", "rgb")
SLOT_CORNER = 0.5       # slot corner radius as a fraction of its half height
PUPIL_BEHIND = 4.0      # virtual pupil behind the wall's inner face: glass + lens recess + up to 1.3 mm fit gap
PUPIL_HALF = 1.5        # pupil ~1 mm + 1 mm position error


def r_at(y, half=None):
    """Opening radius at depth y (camera front face = 0, outside of a wall of thickness t = -t)."""
    return PUPIL_HALF + (PUPIL_BEHIND - y) * math.tan(math.radians(HALF_DEG if half is None else half))


def slot_box(y):
    """(centre x, half width, half height) of the shared projector + RGB opening at depth y."""
    xs = [ELEMENTS[n] for n in SLOT]
    r = r_at(y, SLOT_HALF_DEG)
    return (min(xs) + max(xs)) / 2, (max(xs) - min(xs)) / 2 + r, r


def slot_wire(y):
    """Rounded rectangle (4 lines + 4 arcs) in the plane at depth y."""
    cx, hw, hh = slot_box(y)
    rc = SLOT_CORNER * hh

    def pt(x, z):
        return V(x, y, z)

    def arc(ax, az, a0, a1):
        am = math.radians((a0 + a1) / 2)
        a0, a1 = math.radians(a0), math.radians(a1)
        return Part.Arc(pt(ax + rc * math.cos(a0), az + rc * math.sin(a0)), pt(ax + rc * math.cos(am), az + rc * math.sin(am)),
                        pt(ax + rc * math.cos(a1), az + rc * math.sin(a1))).toShape()

    x0, x1 = cx - hw, cx + hw
    return Part.Wire([
        Part.makeLine(pt(x0 + rc, -hh), pt(x1 - rc, -hh)), arc(x1 - rc, -hh + rc, -90, 0),
        Part.makeLine(pt(x1, -hh + rc), pt(x1, hh - rc)), arc(x1 - rc, hh - rc, 0, 90),
        Part.makeLine(pt(x1 - rc, hh), pt(x0 + rc, hh)), arc(x0 + rc, hh - rc, 90, 180),
        Part.makeLine(pt(x0, hh - rc), pt(x0, -hh + rc)), arc(x0 + rc, -hh + rc, 180, 270)])


def stadium(w, h, y0, y1, cx=0.0, cz=0.0):
    """Stadium prism in local XZ (rounded ends), extruded along y from y0 to y1."""
    r, L = h / 2, y1 - y0
    box = Part.makeBox(w - h, L, h, V(cx - (w - h) / 2, y0, cz - r))
    c1 = Part.makeCylinder(r, L, V(cx - (w - h) / 2, y0, cz), V(0, 1, 0))
    c2 = Part.makeCylinder(r, L, V(cx + (w - h) / 2, y0, cz), V(0, 1, 0))
    return box.fuse([c1, c2]).removeSplitter()


def funnels(front_t):
    """Cutters from the virtual pupil out past the wall's outer face: a round cone for each imager, and one flared
    rounded-rectangle for the projector and RGB together."""
    y_pupil, y_out = PUPIL_BEHIND, -front_t - 1.0
    out = [Part.makeCone(PUPIL_HALF, r_at(y_out), y_pupil - y_out, V(cx, y_pupil, 0), V(0, -1, 0))
           for n, cx in ELEMENTS.items() if n not in SLOT]
    slot = Part.makeLoft([slot_wire(y_pupil), slot_wire(y_out)], True, True)
    assert slot.isValid() and slot.Volume > 0, "slot loft failed"
    return out + [slot]


def lip(rim_t, depth):
    """Locating lip that hooks over the camera's front edge (local y 0..depth)."""
    return stadium(CAM_W + 2 * rim_t, CAM_H + 2 * rim_t, -0.01, depth).cut(stadium(CAM_W, CAM_H, -0.02, depth + 1))


def dot_holes(inside, x_range, z_range, front_t, d=1.2, pitch=3.0, keep=1.2):
    """Hex grid of through-holes. inside(x, z, margin) says whether a point is that far inside the outline.
    Holes stay `keep` clear of every optical opening and of the outline edge."""
    r_open = r_at(-front_t) + keep + d / 2
    edge = keep + d / 2
    holes, row, z = [], 0, z_range[0]
    while z <= z_range[1]:
        x = x_range[0] + (pitch / 2 if row % 2 else 0)
        while x <= x_range[1]:
            clear = all(math.hypot(x - cx, z) >= r_open for n, cx in ELEMENTS.items() if n not in SLOT)
            sx, shw, shh = slot_box(-front_t)
            clear = clear and math.hypot(max(abs(x - sx) - shw, 0.0), max(abs(z) - shh, 0.0)) >= keep + d / 2
            if clear and inside(x, z, edge):
                holes.append(Part.makeCylinder(d / 2, front_t + 2, V(x, 1.0, z), V(0, -1, 0)))
            x += pitch
        z += pitch * math.sqrt(3) / 2
        row += 1
    return holes


def place(shape, front_x, lens_y, lens_z):
    """Local optics frame -> robot frame (x forward, y left, z up) with the camera facing +x.
    Local x (viewer's right) -> robot +y, local y (into the camera) -> robot -x."""
    s = shape.copy()
    s.Placement = App.Placement(V(front_x, lens_y, lens_z), App.Rotation(V(0, 0, 1), 90)).multiply(s.Placement)
    return s
