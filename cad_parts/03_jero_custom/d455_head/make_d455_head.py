"""Jero D455 head, concept v2: curvy lofted shell, the D455 fully enclosed behind a perforated face plate,
and two side horns that slide down onto dovetail rails on the side walls (the antenna rods and their SG90s come out).

Built in the jero assembly frame (x forward, y left, z up, mm). The outer skin is new (a smooth loft through
rounded-rectangle sections); every interface inside it is carried over unchanged from the exact B-rep the
printed draft head was made from (cad-fit-check/Part__Feature096 head, Part__Feature103 floor): neck bearing
seat (re-cut for 6002Z), roll-servo mount bosses, floor interlock. Lines up with
04_reference_assembly/jero_rb3_d455_lipo_design_reference.FCStd.

Parts (each its own STL + STEP):
  head_shell_d455   curvy shell, open front and bottom, speaker grill, 6002Z seat, crown bolt holes
  head_floor_d455   stock floor extended to the face, clipped to the curvy walls, camera bracket holes
  head_face_d455    2 mm face plate (prints flat, face down): D455 openings + dot field + camera lip
  d455_bracket      bolts to the camera's rear M4s on the bench, then screws down to the floor
  head_horn_left_d455 / head_horn_right_d455   side horns (mirror pair), slide down onto the wall rails

The camera sits 10 mm in front of the roll servo (front face x=116.1, 6.1 mm forward of the printed draft): the roll servo front is
4 mm behind the camera, so moving the camera further back means relocating that servo.

Run with FreeCAD 1.1's bundled Python:
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" cad_parts/03_jero_custom/d455_head/make_d455_head.py
"""

import json
import math
import sys
from pathlib import Path

sys.path.append(r"C:\Program Files\FreeCAD 1.1\bin")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.append(str(HERE.parent))
sys.path.append(str(HERE.parents[1] / "05_bearing_6002z"))
import d455_optics as opt
import FreeCAD as App
import MeshPart
import Part

V = App.Vector
REF = HERE.parents[1] / "04_reference_assembly" / "jero_rb3_d455_lipo_design_reference.FCStd"

# --- camera placement (D455 envelope x 89.6..116.1, y -62..62, z 189.7..218.7) ---
SERVO_FRONT_X = 79.6      # front of the head roll servo (reference assembly)
CAM_SERVO_GAP = 10.0      # owner: 10 mm between the back of the RealSense and the roll servo, for the servo plug and cable
CAM_FRONT_X = SERVO_FRONT_X + CAM_SERVO_GAP + 26.5   # 116.1: the camera moved 6.1 mm forward of the printed draft (was 110)
LENS_Y = 0.0
LENS_Z = 189.7 + 14.5      # assumed mid-height: check on the camera
CAM_BACK_X = CAM_FRONT_X - 26.5   # posts sit for the deepest camera (25.5..26.5): front lands 0..1 mm behind CAM_FRONT_X

# --- curvy skin: the back is a smooth loft, the front (x 0..110) a straight sweep of the last section so the
#     flat roof over the roll mount stays exactly at the stock height. (x, half width, top z, top corner radius) ---
SKIN = [(-98.8, 60.0, 186.0, 6.0), (-88.0, 78.0, 212.0, 18.0), (-50.0, 92.0, 223.0, 24.0),
        (-12.0, 98.2, 233.9, 32.0), (0.0, 98.2, 233.9, 32.0)]
FRONT_RIM_R = 0.0          # a rim round thins the 2 mm wall at the face opening; keep it sharp
SHELL_FRONT_X = CAM_FRONT_X + 0.3 + 2.0   # shell rim, flush with the face plate's outer surface
FACE_GAP = 0.25                    # the face plate is part of the BASE now: this is its running gap to the head rim
FACE_ROOT = 0.6                    # plate runs this far down into the base slab so the two fuse
FACE_RIBS_Y = (-85.0, -62.0, -10.0, 20.0, 50.0, 80.0)   # ribs behind the plate foot (clear of the USB hole at y -47..-27)
FACE_RIB = 10.0                    # rib leg; the camera's underside is 12.2 mm above the base, so 10 stays under it
CAM_CLEAR = 0.3                    # face plate stands this far off the camera front so the camera can slide up past it
FACE_X = CAM_FRONT_X + CAM_CLEAR
Z_BOT, R_BOT = 174.5, 3.0
WALL = 2.0                  # stock roof is 2.0 thick (roll mount top sits at z 231.9)
FACE_T = 2.0
RIM_T, RIM_DEPTH = 1.6, 3.0
FLOOR_TOP = 177.5

# --- speaker grill on the -y wall (speaker x 1.5..39, z 183.7..224) ---
GRILL_X, GRILL_Z = (4.0, 36.0), (186.0, 214.0)

# --- bracket ---
POST_T = 3.0               # M4x6 -> 3 mm into the camera (max 4)
POST_Y = (37.0, 62.0)      # |y| span of each post: fully outside head_roll_mount (ears to 32.4, screw bosses to 34.6)
POST_TOP = 214.0           # head_roll_mount starts at z 216.8
FOOT_X = (72.0, CAM_BACK_X)
FOOT_T = 4.0
FOOT_HOLES = [(76.0, s * y) for s in (1, -1) for y in (28.0, 56.0)]

# --- USB-C pass-through: the port is on the camera's bottom face, 37.01 mm from the tripod centreline
#     (datasheet Fig. 10-12). Only 12 mm between camera and floor, so a straight plug drops through a slot.
USB_Y = 37.0
USB_SIDE = -1                      # owner: port on the robot's own right (facing the same way as the robot) = robot -y
BASE_EDGE_R = 2.5
USB_HOLE_X, USB_HOLE_D = CAM_FRONT_X - 13.0, 20.0  # round; covers both possible port depths (10.2 / 15.8 behind the front)

# --- side horns: one per side wall, each slides DOWN onto a vertical dovetail rail on the flat part of the wall
#     (the wall is flat from the base up to z 201.9, where the 32 mm top corner starts) ---
WALL_Y = 98.2                         # outer face of the side walls (x >= -12)
RAIL_X = 62.0                         # rail centre along the head; the speaker grill ends at x 36
RAIL_Z = (180.0, 200.0)               # rail bottom, rail top (the channel's closed top end rests on the rail top)
RAIL_NECK_W, RAIL_TOP_W, RAIL_H = 8.0, 12.0, 4.0   # dovetail: wider away from the wall
RAIL_ROOT = 1.5                       # rail extends this far into the 2 mm wall
SLIDE_CLEAR = 0.25                    # per side in the channel
WALL_GAP = 0.3                        # horn stands this far off the head skin
SHOE_W, SHOE_TOP = 20.0, 2.5          # block around the channel, material outboard of the rail
SHOE_Z = (179.0, 203.0)
DETENT_R, DETENT_UP = 1.2, 0.4        # bump on the rail near its bottom end, clicks into a recess when home
HORN_T = 5.0
HORN_OUT_DEG = 10.0                   # upper blade leans outward
HORN_KINK = 20.0                      # height above SHOE_Z[0] where the lean starts
HORN_LOW = [(11, 0), (11, 23), (-13, 23), (-13, 0)]                 # (along x from RAIL_X, up from SHOE_Z[0]) mm
HORN_UP = [(11, 17), (6, 46), (-9, 78), (-13, 56), (-13, 17)]       # swept back, tip 23 mm above the roof


def load_brep(name):
    s = Part.Shape()
    s.read(str(ROOT / "cad-fit-check" / f"{name}.brep"))
    return s


def largest_solid(s):
    return max(s.Solids, key=lambda x: x.Volume)


def rrect(x, hw, z0, z1, rt, rb):
    """Closed rounded rectangle in the plane x = const (y-z): 4 lines + 4 tangent arcs, same edge count for
    every section so the loft stays smooth. Top corners rt, bottom corners rb."""
    def pt(y, z):
        return V(x, y, z)

    def arc(cy, cz, r, a0, a1):
        am = math.radians((a0 + a1) / 2)
        a0, a1 = math.radians(a0), math.radians(a1)
        return Part.Arc(pt(cy + r * math.cos(a0), cz + r * math.sin(a0)), pt(cy + r * math.cos(am), cz + r * math.sin(am)),
                        pt(cy + r * math.cos(a1), cz + r * math.sin(a1))).toShape()

    edges = [
        Part.makeLine(pt(-hw + rb, z0), pt(hw - rb, z0)), arc(hw - rb, z0 + rb, rb, -90, 0),
        Part.makeLine(pt(hw, z0 + rb), pt(hw, z1 - rt)), arc(hw - rt, z1 - rt, rt, 0, 90),
        Part.makeLine(pt(hw - rt, z1), pt(-hw + rt, z1)), arc(-hw + rt, z1 - rt, rt, 90, 180),
        Part.makeLine(pt(-hw, z1 - rt), pt(-hw, z0 + rb)), arc(-hw + rb, z0 + rb, rb, 180, 270),
    ]
    return Part.Wire(edges)


def skin(grow=0.0, z_bot=Z_BOT, x_front=CAM_FRONT_X, rim=True):
    """Curvy outer solid grown outward by `grow` (negative = inner surface): smooth loft over the back,
    straight sweep from x=0 to x_front, soft round on the front rim (outer skin only)."""
    secs = []
    for i, (x, hw, zt, rt) in enumerate(SKIN):
        if i == 0:
            x -= grow
        secs.append(rrect(x, hw + grow, z_bot, zt + grow, max(rt + grow, 1.0), max(R_BOT + grow, 0.5)))
    back = Part.makeLoft(secs, True, False)
    back.fix(1e-4, 1e-4, 1e-4)        # the raw loft is flagged invalid on tolerance; fix() repairs it
    front = Part.Face(secs[-1]).extrude(V(x_front - SKIN[-1][0], 0, 0))
    s = largest_solid(back.fuse(front).removeSplitter())
    if rim and FRONT_RIM_R > 0:
        fr = max((f for f in s.Faces if abs(f.CenterOfMass.x - x_front) < 0.01), key=lambda f: f.Area)
        try:
            s = s.makeFillet(FRONT_RIM_R, fr.Edges)
        except Exception as e:  # noqa: BLE001 - keep a sharp rim rather than fail the build
            print("front rim fillet skipped:", e)
    return s


# --- interior features, built natively at the positions measured off the stock head B-rep
#     (cad-fit-check/Part__Feature096). That B-rep fails OCC's geometry check (InvalidCurveOnSurface) and cannot
#     be healed, and booleans against it failed silently, so nothing of it is fused into the head any more. ---
BRG_Y, BRG_Z = 0.1, 193.9             # neck bearing axis (along x)
BRG_LIP_X, BRG_SEAT_X, BRG_END_X = -51.0, -49.1, -40.0   # lip outer face / bearing face / housing end (flange side)
BRG_POCKET_R, BRG_LIP_R, BRG_HOUSING_R = 16.1, 14.0, 19.0   # 6002Z: D32.2 pocket x 9, D28 lip hole
PILLARS = [(-14.9, -62.0), (-87.4, -44.4), (61.0, -83.9), (86.0, -68.9),
           (-87.4, 44.6), (-14.9, 62.2), (86.0, 69.1), (61.0, 84.1)]      # base screw pillars
PILLAR_R, INSERT_R, INSERT_DEPTH = 4.5, 2.0, 8.0                          # D4 pocket for an M3 heat-set insert
ROLL_BOSSES = [(46.0, -27.3), (46.0, 27.5), (76.0, -27.3), (76.0, 27.5)]  # head_roll_mount screw bosses
BOSS_Z0, BOSS_R0, BOSS_TAPER = 223.85, 4.985, 0.286                       # cone: bottom z, bottom radius, dr/dz
BOSS_HOLE_TOP = 230.0


def bearing_housing(reach):
    ax = V(1, 0, 0)
    L = BRG_END_X - BRG_LIP_X
    body = Part.makeCylinder(BRG_HOUSING_R, L, V(BRG_LIP_X, BRG_Y, BRG_Z), ax)
    body = body.fuse(Part.makeBox(L, 2 * BRG_HOUSING_R, 60, V(BRG_LIP_X, BRG_Y - BRG_HOUSING_R, BRG_Z)))   # hangs from the roof
    body = body.common(reach)
    body = body.cut(Part.makeCylinder(BRG_POCKET_R, BRG_END_X - BRG_SEAT_X + 1, V(BRG_SEAT_X, BRG_Y, BRG_Z), ax))
    body = body.cut(Part.makeCylinder(BRG_LIP_R, BRG_SEAT_X - BRG_LIP_X + 2, V(BRG_LIP_X - 1, BRG_Y, BRG_Z), ax))
    return body


def pillars(reach):
    out = []
    for x, y in PILLARS:
        c = Part.makeCylinder(PILLAR_R, 80, V(x, y, FLOOR_TOP)).common(reach)
        out.append(c.cut(Part.makeCylinder(INSERT_R, INSERT_DEPTH + 1, V(x, y, FLOOR_TOP - 1))))
    return out


def roll_bosses(reach):
    out = []
    for x, y in ROLL_BOSSES:
        h = 12.0
        c = Part.makeCone(BOSS_R0, BOSS_R0 + BOSS_TAPER * h, h, V(x, y, BOSS_Z0)).common(reach)
        out.append(c.cut(Part.makeCylinder(INSERT_R, BOSS_HOLE_TOP - BOSS_Z0 + 1, V(x, y, BOSS_Z0 - 1))))
    return out


def shell(outer, inner):
    wall = outer.cut(inner)
    reach = skin(-WALL + 0.6, z_bot=Z_BOT, rim=False)              # 0.6 mm into the new wall so features bond
    ins = bearing_housing(reach)
    cols = pillars(reach) + roll_bosses(reach)
    s = wall.fuse([ins] + cols)
    holes = []
    row, z = 0, GRILL_Z[0]
    while z <= GRILL_Z[1]:
        x = GRILL_X[0] + (1.5 if row % 2 else 0)
        while x <= GRILL_X[1]:
            holes.append(Part.makeCylinder(0.6, 10, V(x, -103, z), V(0, 1, 0)))
            x += 3.0
        z += 3.0 * math.sqrt(3) / 2
        row += 1
    s = s.cut(Part.makeCompound(holes))
    s = s.cut(Part.makeBox(400, 400, 20, V(-200, -200, FLOOR_TOP - 20)))   # walls stand on the base cover
    return largest_solid(s.removeSplitter())


def floor(outer):
    """Curvy base cover: outline flush with the shell's outer skin, rounded bottom edge, screwed up into the
    shell's carried-over floor bosses. Every hole/cut-out of the stock floor (screws, neck opening) is kept."""
    sec = max(outer.slice(V(0, 0, 1), FLOOR_TOP - 0.01), key=lambda w: w.BoundBox.DiagonalLength)
    sec.translate(V(0, 0, Z_BOT - sec.BoundBox.ZMin))
    slab = Part.Face(sec).extrude(V(0, 0, FLOOR_TOP - Z_BOT))
    try:
        bottom = min(slab.Faces, key=lambda f: f.CenterOfMass.z)
        slab = slab.makeFillet(BASE_EDGE_R, bottom.OuterWire.Edges)
    except Exception as e:  # noqa: BLE001 - keep a square edge rather than fail the build
        print("base edge round skipped:", e)
    stock = load_brep("Part__Feature103")
    rim = max(stock.slice(V(0, 0, 1), (Z_BOT + FLOOR_TOP) / 2), key=lambda w: w.BoundBox.DiagonalLength)
    rim.translate(V(0, 0, Z_BOT - 1 - rim.BoundBox.ZMin))
    filled = Part.Face(rim).extrude(V(0, 0, FLOOR_TOP - Z_BOT + 2))
    f = slab.cut(filled.cut(stock))               # stock cut-outs, only inside the stock outline
    f = f.cut(Part.makeCylinder(USB_HOLE_D / 2, 20, V(USB_HOLE_X, USB_SIDE * USB_Y, 165)))
    return largest_solid(f.removeSplitter())


def face(inner):
    """Face plate, part of the base: the shell's front opening (inner section) less FACE_GAP all round, standing on
    the base slab at x FACE_X..FACE_X+FACE_T. Outer face flush with the shell rim, inner face CAM_CLEAR off the camera.
    Camera posts and lens openings are in the same print, so they cannot drift apart."""
    sec = max(inner.slice(V(1, 0, 0), CAM_FRONT_X + 1.0), key=lambda w: w.BoundBox.DiagonalLength)
    f = Part.Face(sec).makeOffset2D(-FACE_GAP)
    f = f.common(Part.makeBox(10, 300, 100, V(CAM_FRONT_X - 4, -150, FLOOR_TOP - FACE_ROOT)))   # foot sunk into the base slab
    f = max(f.Faces, key=lambda x: x.Area)
    f.translate(V(FACE_X - f.BoundBox.XMin, 0, 0))
    w = f.OuterWire
    plate = Part.Face(w).extrude(V(FACE_T, 0, 0))
    for y in FACE_RIBS_Y:
        tri = Part.makePolygon([V(FACE_X, y - 1.5, FLOOR_TOP - FACE_ROOT), V(FACE_X - FACE_RIB, y - 1.5, FLOOR_TOP - FACE_ROOT),
                                V(FACE_X - FACE_RIB, y - 1.5, FLOOR_TOP), V(FACE_X, y - 1.5, FLOOR_TOP + FACE_RIB),
                                V(FACE_X, y - 1.5, FLOOR_TOP - FACE_ROOT)])
        plate = plate.fuse(Part.Face(tri).extrude(V(0, 3.0, 0)))
    for f in opt.funnels(FACE_T):
        plate = plate.cut(opt.place(f, FACE_X, LENS_Y, LENS_Z))
    face2d = Part.Face(w)

    def inside(x, z, margin):          # local optics (x, z) -> robot (y, z) on the plate
        p = V(FACE_X, LENS_Y + x, LENS_Z + z)
        on_rib = LENS_Z + z < FLOOR_TOP + FACE_RIB + 1.5 and any(abs(LENS_Y + x - ry) < 3.3 for ry in FACE_RIBS_Y)
        return (face2d.isInside(p, 1e-6, True) and w.distToShape(Part.Vertex(p))[0] >= margin
                and LENS_Z + z > FLOOR_TOP + 1.5 and not on_rib)

    bb = w.BoundBox
    holes = opt.dot_holes(inside, (bb.YMin - LENS_Y, bb.YMax - LENS_Y), (bb.ZMin - LENS_Z, bb.ZMax - LENS_Z), FACE_T)
    print(f"face plate dots: {len(holes)}")
    holes = [opt.place(hh, FACE_X, LENS_Y, LENS_Z) for hh in holes]
    return plate.cut(Part.makeCompound(holes)).removeSplitter()


# Rests under the camera: its weight (and the shock of a fall) goes into the base, the two M4s only hold it back.
# The camera's underside is flat for |y| < 47.5 (R14.5 ends). The right rest sits inside the USB hole (y -47..-27).
REST_Y = ((38.0, 46.0), (-24.0, -16.0))
REST_GAP = 0.2            # under a camera at its tallest (29.5); a 29.0 camera clears by 0.45


def rests():
    top = LENS_Z - (opt.CAM_H - 0.3) / 2 - REST_GAP
    x0 = CAM_BACK_X + 2.0
    out = []
    for y0, y1 in REST_Y:
        r = Part.makeBox(FACE_X - x0 + 0.5, y1 - y0, top - (FLOOR_TOP - FACE_ROOT), V(x0, y0, FLOOR_TOP - FACE_ROOT))   # runs into the face plate
        out.append(r.makeFillet(1.5, [e for e in r.Edges if abs(e.BoundBox.XLength - (FACE_X - x0 + 0.5)) < 0.01 and e.BoundBox.ZMin > top - 0.01]))
    return out


def bracket():
    parts = []
    for s in (1, -1):
        y0, y1 = sorted((s * POST_Y[0], s * POST_Y[1]))
        post = Part.makeBox(POST_T, y1 - y0, POST_TOP - FLOOR_TOP, V(CAM_BACK_X - POST_T, y0, FLOOR_TOP))
        foot = Part.makeBox(FOOT_X[1] - FOOT_X[0], y1 - y0, FOOT_T, V(FOOT_X[0], y0, FLOOR_TOP))
        b = post.fuse(foot)
        for gy in (s * 38.5, s * 60.0):             # gussets, clear of the M4 head at y=47.5
            tri = Part.makePolygon([V(FOOT_X[0], gy - 1.5, FLOOR_TOP + FOOT_T), V(CAM_BACK_X - POST_T, gy - 1.5, FLOOR_TOP + FOOT_T),
                                    V(CAM_BACK_X - POST_T, gy - 1.5, 200.0), V(FOOT_X[0], gy - 1.5, FLOOR_TOP + FOOT_T)])
            b = b.fuse(Part.Face(tri).extrude(V(0, 3.0, 0)))
        parts.append(b)
    # No tie bar across the middle: the roll servo's plug and cable sit under its camera-side end (6.2 mm to the
    # base). The two posts are tied together by the base slab and, since the face plate moved here, by the face.
    b = parts[0].fuse(parts[1])
    for my in opt.M4_X:          # local optics x -> robot y
        b = b.cut(Part.makeCylinder(2.2, POST_T + 2, V(CAM_BACK_X - POST_T - 1, LENS_Y + my, LENS_Z), V(1, 0, 0)))
    return b.removeSplitter()


def dovetail(length, neck, top, h, root, z0=0.0):
    """Dovetail on the +y side wall, running up z from z0: neck at the wall (y = WALL_Y), wider at y = WALL_Y + h."""
    y = WALL_Y
    pts = [V(RAIL_X - neck / 2, y - root, z0), V(RAIL_X + neck / 2, y - root, z0), V(RAIL_X + neck / 2, y, z0),
           V(RAIL_X + top / 2, y + h, z0), V(RAIL_X - top / 2, y + h, z0), V(RAIL_X - neck / 2, y, z0)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, length))


def detent(grow=0.0):
    return Part.makeSphere(DETENT_R + grow, V(RAIL_X, WALL_Y + RAIL_H + DETENT_UP - DETENT_R, RAIL_Z[0] + 4.0))


def mirrored(s, side):
    return s if side > 0 else s.mirror(V(0, 0, 0), V(0, 1, 0))


def side_rail(side):
    s = dovetail(RAIL_Z[1] - RAIL_Z[0], RAIL_NECK_W, RAIL_TOP_W, RAIL_H, RAIL_ROOT, RAIL_Z[0]).fuse(detent())
    return mirrored(s, side)


def side_horn(side):
    c = SLIDE_CLEAR
    y_out = WALL_Y + RAIL_H + c + SHOE_TOP                    # outer face of the shoe and of the lower blade
    shoe = Part.makeBox(SHOE_W, y_out - WALL_Y, SHOE_Z[1] - SHOE_Z[0], V(RAIL_X - SHOE_W / 2, WALL_Y, SHOE_Z[0]))

    def blade(profile):
        pts = [V(RAIL_X + u, y_out - HORN_T, SHOE_Z[0] + v) for u, v in profile]
        return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, HORN_T, 0))

    up = blade(HORN_UP)
    up.rotate(V(0, y_out - HORN_T, SHOE_Z[0] + HORN_KINK), V(1, 0, 0), -HORN_OUT_DEG)   # tip goes outward (+y)
    horn = shoe.fuse([blade(HORN_LOW), up])
    horn = horn.cut(skin(WALL_GAP, x_front=SHELL_FRONT_X, rim=False))      # running clearance to the head skin
    # channel: open at the bottom, closed just above the rail top (the stop)
    ch = dovetail(RAIL_Z[1] + c - SHOE_Z[0] + 5.0, RAIL_NECK_W + 2 * c, RAIL_TOP_W + 2 * c, RAIL_H + c, 3.0, SHOE_Z[0] - 5.0)
    horn = horn.cut(ch.fuse(detent(c)))
    return mirrored(largest_solid(horn.removeSplitter()), side)


def save(name, s, ang=0.2):
    assert s.isValid() and len(s.Solids) == 1, f"{name}: invalid or multi-body"
    s.check(True)                     # raises on self-intersections etc.: booleans on such a solid fail silently
    out = HERE / name
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.03, AngularDeflection=ang).write(str(out.with_suffix(".stl")))
    s.exportStep(str(out.with_suffix(".step")))
    print(f"{name}: {s.Volume / 1000:.1f} cm^3")


def check(parts):
    d = App.openDocument(str(REF))
    names = {"head_yaw_to_roll", "head_roll_mount", "head_pitch_to_yaw", "speaker_stand", "speaker_interface",
             "speaker_top", "speaker_bottom"}
    refs = {o.Label: o.Shape for o in d.Objects
            if o.Label in names or (o.Label.endswith("007") and ("WJ-WK00" in o.Label or "palonier" in o.Label))}
    refs["d455_envelope"] = opt.place(opt.stadium(opt.CAM_W - 0.3, opt.CAM_H - 0.3, 0.0, 26.0), CAM_FRONT_X, LENS_Y, LENS_Z)
    refs["bearing_6002z"] = Part.makeCylinder(16, 9, V(-49.1, 0.1, 193.9), V(1, 0, 0)).cut(
        Part.makeCylinder(7.5, 9, V(-49.1, 0.1, 193.9), V(1, 0, 0)))
    hits = []
    for pn, ps in parts.items():
        for rn, rs in refs.items():
            v = ps.common(rs).Volume
            if v > 0.5:
                hits.append({"part": pn, "ref": rn, "overlap_mm3": round(v, 1)})
    App.closeDocument(d.Name)
    return hits


if __name__ == "__main__":
    outer = skin(x_front=SHELL_FRONT_X)
    inner = skin(-WALL, z_bot=168.0, x_front=SHELL_FRONT_X + 5, rim=False)
    assert outer.isValid() and inner.isValid(), "skin loft failed"
    sh = shell(outer, inner)
    plate, base, brk = face(inner), floor(outer), bracket()
    horns = {side: side_horn(side) for side in (1, -1)}
    fused = sh.fuse([side_rail(side) for side in (1, -1)]).removeSplitter()
    assert len(fused.Solids) == 1, f"head fused into {len(fused.Solids)} bodies"
    head = fused.Solids[0]
    fused = base.fuse([brk, plate] + rests()).removeSplitter()
    assert len(fused.Solids) == 1, f"base fused into {len(fused.Solids)} bodies"
    base = fused.Solids[0]
    parts = {"head_d455": head, "head_base_d455": base,
             "head_horn_left_d455": horns[1], "head_horn_right_d455": horns[-1]}

    # horn fit: seated, and at every 2 mm of the lift-off stroke, overlap with head + base (detent click excepted)
    fit = {}
    for side, nm in ((1, "left"), (-1, "right")):
        worst = 0.0
        for lift in range(0, 31, 2):
            h = horns[side].copy()
            h.translate(V(0, 0, lift))
            worst = max(worst, h.common(head).Volume + h.common(base).Volume)
        seated = horns[side].common(head).Volume + horns[side].common(base).Volume
        fit[nm] = {"seated_overlap_mm3": round(seated, 3), "worst_overlap_during_slide_mm3": round(worst, 3)}
        assert seated < 0.01, f"{nm} horn overlaps the head when seated: {seated}"
        assert worst < 0.5, f"{nm} horn binds while sliding: {worst}"
        gap = horns[side].distToShape(sh)[0]
        fit[nm]["min_gap_to_shell_mm"] = round(gap, 3)
    print("horn fit:", fit)

    # the face plate rides inside the head rim: nothing may overlap, and the gap must be the running clearance
    ov = head.common(base).Volume
    gap = plate.distToShape(sh)[0]
    print(f"head vs base overlap {ov:.3f} mm3, face plate to head rim {gap:.3f} mm")
    assert ov < 0.01, f"head and base overlap: {ov}"
    assert 0.15 < gap < 0.35, f"face plate gap to the head is {gap}"

    # the head is lowered onto the base (camera already bolted on): it must clear the face plate, posts and camera all the way
    cam_env = opt.place(opt.stadium(opt.CAM_W - 0.3, opt.CAM_H - 0.3, 0.0, 26.5), CAM_FRONT_X, LENS_Y, LENS_Z)
    worst = 0.0
    for lift in range(0, 61, 4):
        hh = head.copy()
        hh.translate(V(0, 0, lift))
        worst = max(worst, hh.common(base).Volume + hh.common(cam_env).Volume)
    rest_top = max(r.BoundBox.ZMax for r in rests())
    print(f"camera rests: top z {rest_top:.2f}; under a 29.0 mm camera {189.7 - rest_top:.2f} mm, under a 29.5 mm camera {189.45 - rest_top:.2f} mm")
    print(f"head lowered over base + camera, worst overlap {worst:.3f} mm3; camera vs base {base.common(cam_env).Volume:.3f} mm3")
    assert worst < 0.01, "head cannot be lowered over the base"

    # guard: the 6002Z seat housing and every floor screw pillar must survive into the head
    ring = Part.makeCylinder(19, 11, V(-51.5, 0.1, 193.9), V(1, 0, 0)).cut(Part.makeCylinder(16.2, 11, V(-51.5, 0.1, 193.9), V(1, 0, 0)))
    assert head.common(ring).Volume > 1500, "6002Z bearing housing missing from the head"
    for x, y in PILLARS:
        assert head.common(Part.makeCylinder(4.0, 10, V(x, y, FLOOR_TOP + 9))).Volume > 400, f"screw pillar missing at {x},{y}"
    for n, p_ in parts.items():
        save(n, p_, 0.4)
    for stale in ("head_horns_d455", "horn_left", "horn_right", "head_shell_d455", "head_face_d455", "horn_crown", "head_floor_d455", "d455_bracket"):
        for ext in (".stl", ".step"):
            (HERE / (stale + ext)).unlink(missing_ok=True)

    rho = 1.24e-3   # PLA g/mm^3, solid

    def mass_com(shapes):
        shapes = [so for s in shapes for so in s.Solids]
        m = sum(s.Volume for s in shapes) * rho
        c = V()
        for s in shapes:
            c = c + s.CenterOfMass * (s.Volume * rho)
        return m, c * (1.0 / m)

    m_new, c_new = mass_com(list(parts.values()))
    m_old, c_old = mass_com([load_brep("Part__Feature096"), load_brep("Part__Feature103")])
    report = {
        "printed_mass_g_solid_new": round(m_new, 1), "com_new": [round(c_new.x, 1), round(c_new.y, 1), round(c_new.z, 1)],
        "printed_mass_g_solid_stock_head_floor": round(m_old, 1), "com_stock": [round(c_old.x, 1), round(c_old.y, 1), round(c_old.z, 1)],
        "note": "solid PLA 1.24 g/cm3; real prints are lighter with infill. Camera (116 g) is unchanged in position.",
        "horn_fit": fit,
        "clearance": check(parts),
    }
    (HERE / "head_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
