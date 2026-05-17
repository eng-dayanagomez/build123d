# Open-Smartwatch Light — 3D CAD Reconstruction

**Source project:** [open-smartwatch-light](https://github.com/Open-Smartwatch/open-smartwatch-light)  
**CAD library:** [build123d](https://github.com/gumyr/build123d) (Python)  

---

## Overview

Fully parametric reconstruction of the Open-Smartwatch Light enclosure in Python using `build123d`. All four structural components (base, mid, top, strap) are scripted from scratch, sharing geometry through a common module. The project includes STEP and STL exports for each part, a complete multi-body assembly, and an automated geometry validation pipeline.

---

## File Structure

```
smarwatch_light/
├── common.py               # Shared parameters and geometry primitives
├── base.py                 # Watch base (battery cavity, screw mounts, strap latches)
├── mid.py                  # Mid section (electronics bay, button cutouts, snap pins)
├── top.py                  # Top cover / face (glass seat, display hole, mount tabs)
├── strap.py                # Watch strap (multi-piece latch system)
├── assembly.py             # Full assembly and print layout scripts
├── verification_script.py  # Geometry validation: STL vs STEP symmetric difference
├── *.step / *.stl          # Exported geometry (per-part and full assembly)
├── 1.6mm_*.stl / watch.stl # Original reference STLs for validation
└── screenshot_validation_*.png  # Validation output screenshots
```

---

## Architecture

### `common.py` — Shared Module

All global dimensions and reusable geometry live here, keeping every part script DRY and easy to reparametrize.

**Parameters defined (selection):**

| Parameter | Value | Description |
|---|---|---|
| `body_dia` | 43.7 mm | Main watch body diameter |
| `pcb_h` | 1.6 mm | PCB thickness |
| `mount_dist_w/h` | 18.0 / 41.0 mm | Screw mount spacing |
| `screw_dia` / `nut_dia` | 2.3 / 1.9 mm | Fastener geometry |
| `button_angle_*` | ±32.5° offsets | Button angular positions on body |
| `strap_latch_ws/wl` | 3.3 / 8.4 mm | Strap latch widths |

**Primitive wrappers** (OpenSCAD-style API built on top of build123d):

`Cube`, `Cyl`, `Sph`, `Tor`, `Translate`, `Rotate`, `Scale`, `Union`, `Difference`

These wrap build123d's builder API into a concise functional style that mirrors how primitives work in OpenSCAD, making the construction logic easy to read and audit.

**Compound geometry helpers:**

- `roundedcylinder(d, h, r)` — cylinder with torus-based edge rounding
- `roundedcube(x, y, z, r, round_bot, round_top)` — box with sphere-corner rounding, 3 variants
- `body(h, rounded)` — full watch body profile (circular + strap lug extensions)
- `StrapHull / FStrapHull` — convex hull profiles for strap attachment geometry
- `base_screws` — 4-corner screw pattern placed from mount distance parameters
- `prism`, `screw_part`, `usb_flatten` — cross-part construction utilities

---

### `base.py` — Watch Base

The bottom shell. Combines a rounded body profile with battery cavity, strap latch attachments, screw holes, and USB cutout.

**Key geometry:**

- `base_bat(h)` — D-shaped battery cavity: cylinder minus a rectangular slice, plus a rectangular protrusion for the flat side
- `base_strap()` — convex-hull strap latch arm with screw hole and clearance cuts
- `fstrap_piece(w, s_hole)` — flush-mount strap variant using `FStrapHull` with a through-hole pin
- `fstrap()` — mirrored pair of `fstrap_piece` for both strap sides
- `base()` — main assembly: rounded bottom + cylindrical wall + strap attachments − battery cutout − screw holes − USB flat

**Exports:** `base.step`, `base.stl`

---

### `top.py` — Watch Face / Top Cover

The front cover with display opening, glass seat, and four triangular mount tabs.

**Key geometry:**

- `ConeWrap(d1, d2, h)` — frustum (truncated cone) wrapper; used to build the stepped face profile that transitions from body diameter to bezel diameter
- `face_base()` — two-stage frustum stack forming the face profile
- `face_mount(for_top, base_h)` — single triangular mount tab with rounded fillet; uses `make_hull()` to blend a rectangle and a circle arc into the mounting geometry
- `face_mounts()` — 4× placement of `face_mount` at screw hole locations with X/Y mirror
- `face()` — full top: face base + mounts − display hole − glass seat − USB cutout − optional engraved button labels (R, 1, 2, 3)

**Notable detail:** optional `draw_text` flag engraves button labels using `Text()` + `extrude`, positioned radially at each button angle.

**Exports:** `top.step`, `top.stl`

---

### `mid.py` — Mid Section

The structural ring that sits between base and top. Houses the electronics bay, four button cutouts, snap-fit pins, and USB port opening.

**Key geometry:**

- `mid_cutout(h)` — L-shaped slot (rectangle + offset rectangle) for PCB/connector alignment
- `mid_button_cut_original()` — three-body cutout per button: outer slot, inner holder slot, top gap
- `mid_button_original()` — physical button geometry: rounded cuboid body + two wing tabs, built from `roundedcube` with `round_bot=True`
- `mid_body()` — main ring: `body()` shell minus angled prism cuts at strap interfaces (top and bottom), with a flush cylinder cap at the top edge
- `mid()` — full mid: body minus electronics cylinder, PCB ledges, USB opening, button cutouts, screw through-holes, plus 4 snap-fit pins added via `Union`

Snap pins are placed at 4× 45°-offset angles using `Rotate([0,0,angle])` — these index into the base shell for alignment.

**Exports:** `mid.step`, `mid.stl`

---

### `strap.py` — Watch Strap

A multi-piece interlocking strap system. Each strap "piece" has a central body, two short latches on one side, and one long latch on the other, allowing them to chain together.

**Key geometry:**

- `fixed_roundedcube(x, y, z, r)` — local variant using `fillet` on top edges; used instead of `common.roundedcube` to avoid edge-case failures on thin bodies
- `strap_latch(long, latch_id)` — single latch arm: rounded cuboid nose + cylindrical hinge + screw/nut hole; `long=True` produces the receiver latch
- `strap_piece(latch_dist)` — full strap link: two short latches + central body + one long receiver latch
- `strap(assembled, rows, angle)` — array of `strap_piece` in either assembled (interlocked) or print-flat layout; supports angular flex via `Rotate([0, angle, 0])`

**Exports:** `strap.step`, `strap.stl` (multi-body `Compound`)

---

### `assembly.py` — Full Assembly

Places all parts at correct Z-offsets and exports the complete watch.

- `assembly()` — stacks Base → Mid → Face at computed Z heights; positions two strap sub-assemblies (top/bottom) rotated 90° and offset from the body edge by `assembly_strap_off`
- `print_layout()` — flat print layout: parts spread on XY plane for slicing previews
- Exports `smartwatch_assembly.step` and `smartwatch_assembly.stl` as a `Compound` with 90° global rotation applied

Color coding in `ocp_vscode`: green = face, blue = mid, orange = base, red = buttons, cyan = straps.

---

### `verification_script.py` — Geometry Validation

Automated validation pipeline comparing the reconstructed STEP against the original reference STL using the **symmetric difference volume method**.

**Algorithm:**

1. Load reference STL into a `manifold3d` solid
2. Grid-search over 11 × 11 = 121 tessellation parameter combinations (`linear_tolerance` × `angular_tolerance`) to find the STEP-to-STL export that minimizes volume discrepancy
3. Compute symmetric difference: `vol(A − B)` and `vol(B − A)` on the optimal pair
4. Report PASS if both values are within tolerance (default: **0.5 × 10³ mm³**)

**Why symmetric difference instead of simple volume delta:**  
A simple `|vol_A − vol_B|` can cancel out if material is missing in one region and added in another. The symmetric difference catches both independently, making it a stricter and more geometrically meaningful metric.

**Usage:**

```bash
python verification_script.py 1.6mm_base.stl base.step
python verification_script.py 1.6mm_base.stl base.step --tolerance 0.3
```

---

## Technical Stack

| Tool | Role |
|---|---|
| `build123d` | Core CAD modeling (Python) |
| `ocp_vscode` | Interactive 3D viewer during development |
| `manifold3d` | Watertight solid operations for validation |
| `numpy-stl` | STL mesh loading |
| `numpy` | Vertex deduplication and array ops |
| STEP / STL | Export formats |

---

## Geometric Techniques Demonstrated

- Frustum stacking (`Cone` / `ConeWrap`) for tapered body profiles
- Convex hull profiles (`make_hull`) for organic blended geometry
- Torus-based edge rounding on cylinders
- Sphere-corner 3D rounding on boxes
- Multi-body boolean difference at assembly scale
- Polar and mirror placement of repeated features
- Compound multi-body export for strap arrays
- Parametric angular button placement via trigonometric offsets
- Automated tessellation optimization for geometry validation
