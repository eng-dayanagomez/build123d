"""
verification_script.py
"""

import sys
import argparse
import tempfile
import os
import numpy as np
from pathlib import Path

# Default acceptance threshhold:
DEFAULT_TOLERANCE = 0.5

# Mode A: solid boolean via manifold3d (primary):
def _validate_solid(stl_path: Path, step_path: Path, tolerance: float, verbose: bool) -> bool:

    import manifold3d as m3d
    from stl import mesh as stl_mesh
    from build123d import import_step, export_stl

    # Load the reference STL and build a manifold solid from it:
    raw_a = stl_mesh.Mesh.from_file(str(stl_path))
    verts_a = raw_a.vectors.reshape(-1, 3)
    faces_a = np.arange(len(verts_a)).reshape(-1, 3)
    verts_unique_a, inverse_a = np.unique(verts_a, axis=0, return_inverse=True)

    solid_a = m3d.Manifold(m3d.Mesh(
        vert_properties=verts_unique_a.astype(np.float32),
        tri_verts=inverse_a[faces_a].astype(np.uint32),
    ))
    if solid_a.is_empty():
        raise RuntimeError("The reference STL is not watertight.")
    
    # Tessellation parameter grid to sweep:
    linear_tolerances = [
        0.01, 0.03, 0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.5
    ]
    angular_tolerances = [
        0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7
    ]

    best_diff = float('inf')
    best_tmp_name = None
    best_solid_b = None
    best_params = (0, 0)

    if verbose:
        print("Optimizing mesh resolution to minimize volume difference...")
    
    for tol_lin in linear_tolerances:
        for tol_ang in angular_tolerances:

            # Re-import the STEP inside the loop to avoid any shape-caching artefacts:
            shape_b = import_step(str(step_path))

            tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
            tmp.close()

            export_stl(shape_b, tmp.name, tolerance=tol_lin, angular_tolerance=tol_ang)

            try:
                raw_b = stl_mesh.Mesh.from_file(tmp.name)
                verts_b = raw_b.vectors.reshape(-1, 3)
                faces_b = np.arange(len(verts_b)).reshape(-1, 3)
                verts_unique_b, inverse_b = np.unique(verts_b, axis=0, return_inverse=True)

                solid_b_temp = m3d.Manifold(m3d.Mesh(
                    vert_properties=verts_unique_b.astype(np.float32),
                    tri_verts=inverse_b[faces_b].astype(np.uint32),
                ))

                # Compute the symmetric difference volume for this tessellation:
                vol_amb = (solid_a - solid_b_temp).volume() / 1000.0
                vol_bma = (solid_b_temp - solid_a).volume() / 1000.0
                total_diff = vol_amb+vol_bma

                # Keep track of the best tessellation found so far:
                if total_diff < best_diff:
                    best_diff = total_diff
                    best_params = (tol_lin, tol_ang)
                    best_solid_b = solid_b_temp

                    # Remove the previous best temp file:
                    if best_tmp_name and os.path.exists(best_tmp_name):
                        os.remove(best_tmp_name)
                    best_tmp_name = tmp.name
                else:
                    # This tessellation is worse:
                    os.remove(tmp.name)

            except Exception:
                # Manifold creation failed:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)

    if not best_tmp_name:
        raise RuntimeError("Could not generate a valid STL with any of the tested tolerances.")
    
    if verbose:
        print(f" Best approximation found:")
        print(f"  -> tolerance: {best_params[0]}")
        print(f"  -> angular_tolerance: {best_params[1]}")
        print("=" * 50)

    # Use the best tessellation for the final report:
    solid_b = best_solid_b
    if os.path.exists(best_tmp_name):
        os.remove(best_tmp_name)

    # Individual volumes for information only:
    vol_a = solid_a.volume() / 1000.0
    vol_b = solid_b.volume() / 1000.0

    if verbose:
        print(f" Volume A (STL): {vol_a:.2f} x10^3 mm^3")
        print(f" Volume B (STEP): {vol_b:.2f} x10^3 mm^3")
        print(f" DeltaV (simple diff): {abs(vol_a - vol_b):.2f} x10^3 mm^3 (NOT SUFFICIENT ALONE)")

    # Final symmetric difference computation on the best solid pair:
    vol_amb = (solid_a - solid_b).volume() / 1000.0
    vol_bma = (solid_b - solid_a).volume() / 1000.0

    return _report(round(vol_amb, 1), round(vol_bma, 1), tolerance, verbose)

# Result printer:

def _report(vol_amb: float, vol_bma: float, tolerance: float, verbose: bool) -> bool:
    pass_amb = vol_amb <= tolerance
    pass_bma = vol_bma <= tolerance
    overall = pass_amb and pass_bma

    if verbose:
        print(f" vol(A - B) = {vol_amb:.2f} x10^3 mm^3 -> {'PASS' if pass_amb else 'FAIL'}")
        print(f" vol(B - A) = {vol_bma:.2f} x10^3 mm^3 -> {'PASS' if pass_bma else 'FAIL'}")
        print("=" * 50)
        print(f" OVERALL RESULT: {'PASS' if overall else 'FAIL'}")
        if overall:
            print("The geometries are IDENTICAL within tolerance.")
        else:
            print("The geometries DIFFER. Review the model.")
        print("=" * 50)
    
    return overall

# Public entry point:

def validate(
        reference_stl: str | Path,
        generated_step: str | Path,
        tolerance: float = DEFAULT_TOLERANCE,
        mode: str = "auto",
        verbose: bool = True,
) -> bool:
    # Compared generated STEP file against a reference STL using the symmetric difference volume method:
    reference_stl = Path(reference_stl)
    generated_step = Path(generated_step)

    if verbose:
        print("=" * 50)
        print("GEOMETRY VALIDATION - SYMMETRIC DIFFERENCE")
        print(f"Reference (A): {reference_stl.name} [STL]")
        print(f"Generated (B): {generated_step.name} [STEP]")
        print("=" * 50)
    
    if mode == "solid":
        return _validate_solid(reference_stl, generated_step, tolerance, verbose)
    
    try:
        return _validate_solid(reference_stl, generated_step, tolerance, verbose)
    except Exception:
        pass

# main():
def main():
    parser = argparse.ArgumentParser(
        description="Validate a generated STEP against a reference STL using symmetryc difference"
    )
    parser.add_argument("reference_stl", help="Reference STL file (A)")
    parser.add_argument("generated_step", help="Generated STEP file (B)")
    parser.add_argument(
        "--tolerance", type=float, default=DEFAULT_TOLERANCE,
        help="Volume tolerance in x10^3 mm^3"
    )
    parser.add_argument(
        "--mode", choices=["auto", "solid"], default="solid",
        help="Comparison mode"
    )
    args = parser.parse_args()

    result = validate(
        reference_stl=args.reference_stl,
        generated_step=args.generated_step,
        tolerance=args.tolerance,
        mode=args.mode,
    )
    sys.exit(0 if result else 1) # exit 0 = PASS, exit 1 = FAIL

if __name__ == "__main__":
    main()