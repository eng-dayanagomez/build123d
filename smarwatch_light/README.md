# Open-Smartwatch Light — 3D CAD Reconstruction

**Task ID:** TID1318107  
**Repository File:** smarwatch_light.zip  
**Source Repository:** https://github.com/Open-Smartwatch/open-smartwatch-light/tree/main

---

## Project Description

Parametric 3D CAD reconstruction of the Open-Smartwatch Light enclosure using Python and the `build123d` CAD library. The project reproduces all four structural components of the watch body (base, mid, top, and strap) as fully parametric scripts, sharing common geometry through a dedicated `common.py` module, with STEP and STL exports for each part and a full assembly.

---

## Delivered Files

### Parametric Scripts

| File | Description |
|------|-------------|
| `base.py` | Parametric script for the watch base |
| `mid.py` | Parametric script for the mid section |
| `top.py` | Parametric script for the top cover |
| `strap.py` | Parametric script for the watch strap |
| `common.py` | Shared geometry and parameter definitions |
| `assembly.py` | Full assembly script |

### Generated STEP & STL Exports

| File | Description |
|------|-------------|
| `base.step` | STEP export of the base |
| `base.stl` | STL export of the base |
| `mid.step` | STEP export of the mid section |
| `mid.stl` | STL export of the mid section |
| `top.step` | STEP export of the top cover |
| `top.stl` | STL export of the top cover |
| `strap.step` | STEP export of the strap |
| `strap.stl` | STL export of the strap |
| `smartwatch_assembly.step` | STEP export of the full assembly |
| `smartwatch_assembly.stl` | STL export of the full assembly |

### Original Reference STLs

| File | Description |
|------|-------------|
| `1.6mm_base.stl` | Original reference STL (base) |
| `1.6mm_mid.stl` | Original reference STL (mid section) |
| `1.6mm_top.stl` | Original reference STL (top cover) |
| `1.6mm_strap.stl` | Original reference STL (strap) |
| `watch.stl` | Original reference STL (full watch body) |

### Validation

| File | Description |
|------|-------------|
| `verification_script.py` | Geometry validation script |
| `screenshot_validation_1.png` | Geometric comparison screenshot 1 |
| `screenshot_validation_2.png` | Geometric comparison screenshot 2 |

---

## Tools & Workflow

- **CAD Library:** `build123d` (Python)
- **Export Formats:** STEP, STL
- **Validation:** Symmetric difference methodology (reconstructed vs. original STL)
