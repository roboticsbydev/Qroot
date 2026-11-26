# cad_parts — all Jero CAD in one place (working copy)

These are **copies**. The originals are still in `upstream/Open_Duck_Mini/print/` (git submodule)
and `cad/rb3_realsense/`, because scripts read from there. Edit the files here. Once the repo is
restructured, this folder becomes the single source.

| Folder | What | Format |
|---|---|---|
| `01_printed_parts_upstream/` | All 36 Open Duck Mini v2 printed parts | STL (mesh) |
| `02_mods_upstream/` | Community mods (Justin's head, Jaime's mods/stand) | STL / STEP |
| `03_jero_custom/` | Jero's own parts: RB3 trunk top, D455 head drafts, underbody, LiPo fit | FCStd / STEP / STL |
| `04_reference_assembly/` | Full Jero RB3 + D455 + LiPo design reference (FreeCAD) | FCStd |
| `05_bearing_6002z/` | **Print these** instead of the matching `01_` parts: re-cut for 6002Z bearings | STL + STEP |

Not copied because of size or vendor origin (still in `cad/rb3_realsense/`): the 240 MB
`onshape/*.step`, the RB3/D455 vendor models in `sources/`, and `cad-fit-check/*.brep`.

## Bearings: 6002Z (15 x 32 x 9), replacing the stock 20 x 32 x 7

3 bearings in total: 2 at hip yaw, 1 in the neck. `05_bearing_6002z/` holds the re-cut parts.
`make_6002z_parts.py` there regenerates them from the `01_`/`03_` copies, using FreeCAD 1.1's bundled Python
(the head parts take several minutes each).

| Part | Print | What changed |
|---|---|---|
| `trunk_bottom_6002z` | 1x | Both hip seats 2 mm deeper (Ø32.2 x 9 mm). Floor lip 3.5 → **1.5 mm**, still backed by `body_middle_bottom` underneath |
| `roll_motor_bottom_6002z` | 2x | Shaft Ø19.9 → **Ø14.9**, 7 → 9 mm long, 0.5 mm lead-in chamfer |
| `head_6002z` | 1x | Neck seat 2 mm deeper (Ø32.2 x 9 mm). Old lip rebuilt 2 mm further out (1.9 mm, Ø28 hole) |
| `head_yaw_to_roll_6002z` | 1x | Shaft Ø19.8 → **Ø14.8**, 2 mm longer |
| `head_face_draft_6002z` | (draft) | Jero's D455 head draft: it carries the same neck seat (shifted), re-cut the same way as `head` |

Design rules used:
- The flange-side face of each bearing did not move. The seat grew 2 mm *away* from the flange, so
  no joint axis or link moved. Joint geometry is unchanged. Mass changes slightly: the 6002Z is heavier, and the
  sim XML folds the bearings (`roll_bearing*`) into body inertias rather than listing them separately.
- Shafts keep the original undersize (−0.1 hip, −0.2 neck) for a slip fit.
- Lip holes stay Ø26.2 (hip) and Ø28 (neck). The Z shield sits inside D2 ≈ 28.2, recessed and fixed to the outer
  ring, so the lip never rubs it.
- `roll_motor_top` is **not** a bearing part. Its Ø20 cone holds a Ø7 hole for a pin.

Trade-offs to know:
- A Ø14.9 printed hip shaft has about 0.56x the area and 0.31x the bending stiffness of the Ø19.9 one.
  These shafts carry a leg each, so print them solid (100% infill or many perimeters).
- The hip floor lip is now 1.5 mm thick.

Checked: no other bearing seats exist in `02_mods_upstream/` or `03_jero_custom/` beyond the head draft. Every part is watertight (`head_6002z` keeps 6 non-manifold edges from the upstream file, on the
head top, away from the bearing). Profiles were re-measured, and no other part occupies the added material.

`Jero_print_pack.zip` still contains the **old** 20 mm versions of these four parts.

## D455 aperture test strip (`03_jero_custom/d455_test_strip/`)

A 2 mm front wall with one flared opening per optical element: both IR imagers, the projector and RGB. Its job
is to prove that a head face with the camera fully inside does not block any view before the head is redesigned.
`make_d455_test_strip.py` regenerates it. All dimensions come from the D400 datasheet 337029-017, Fig. 10-12.

- **Shape:** front face only. The openings are round: Ø16.8 outside, Ø12.2 inside. A field of 295 decorative
  Ø1.2 holes sits on a 3 mm hex grid. A 3 mm lip hooks over the camera's front edge so the openings line up
  with the lenses, with no screws. Set `RIM_DEPTH = 0` for a bare flat strip.
- **Head mounting (later):** the camera's rear points are **M4**, max insertion 4 mm, 0.4 Nm.
- **Check before printing:**
  - The pill-shaped window is the projector, 37.5 mm from the left imager. RGB is 59 mm from it.
  - The lens axis is at mid-height. The drawing does not dimension it, so set `LENS_Z` in the script if it is off.
- **Printing:** print it outside face down in matte black, with no supports and a 0.4 mm nozzle.
- **Test:**
  1. In realsense-viewer, capture the same scene without the strip and then with it, emitter on.
  2. Compare the IR streams for bright edge patches (projector light bouncing off a funnel wall).
  3. Compare depth for new holes at the edges.
  4. Compare RGB for dark corners.
  5. If any of these show up, raise `HALF_H_DEG` or `PUPIL_BEHIND` and rebuild.

## Editing further

STLs are meshes. The `.step` files in `05_` are solids converted from those meshes, so you can open them in
FreeCAD/Fusion and cut or extrude, but they have no feature history. For real parametric editing, make a copy
of the upstream Onshape document:
https://cad.onshape.com/documents/64074dfcfa379b37d8a47762/w/3650ab4221e215a4f65eb7fe/e/0505c262d882183a25049d05
