#!/usr/bin/env python
"""Add boundary markers to an NRRD volume.

This script adds a thin border of non-zero voxels around the bounding box
of existing content in a 3D NRRD volume. This ensures that downstream tools
(ImageJ, Woolz) can correctly detect the volume extent.

The boundary is added by setting voxels at the edges of the content bounding
box (expanded by ``pad`` voxels) to a marker value. All spatial metadata
(space directions, space origin, etc.) from the source NRRD is preserved
in the output.

Usage:
    python Bound.py <pad> <input.nrrd> <output_bounded.nrrd>

Arguments:
    pad     Number of voxels to expand the bounding box by on each side.
    input   Path to the source volume.nrrd file.
    output  Path to write the bounded volume_bounded.nrrd file.

Example:
    python Bound.py 3 /IMAGE_PRIVATE/VFBu_xxx/VFB_yyy/volume.nrrd \
                      /IMAGE_PRIVATE/VFBu_xxx/VFB_yyy/volume_bounded.nrrd
"""

import os
import sys

import numpy as np
import nrrd


BOUNDARY_VALUE = 1


def add_boundary(data, pad=3):
    """Add boundary markers around non-zero content in the volume.

    Finds the bounding box of all non-zero voxels, expands it by ``pad``
    voxels in each direction (clamped to the volume extent), and sets the
    six faces of the expanded box to ``BOUNDARY_VALUE``.

    Args:
        data: 3D numpy array (the volume).
        pad: Number of voxels to expand the bounding box by.

    Returns:
        A copy of the input array with boundary markers added.
    """
    result = data.copy()

    # Find bounding box of non-zero content
    nonzero = np.argwhere(data > 0)
    if len(nonzero) == 0:
        # Nothing to bound -- return as-is
        return result

    mins = nonzero.min(axis=0)
    maxs = nonzero.max(axis=0)

    # Expand by pad, clamp to volume dimensions
    lo = np.maximum(mins - pad, 0)
    hi = np.minimum(maxs + pad, np.array(data.shape) - 1)

    # Set the six faces of the bounding box
    # X faces
    result[lo[0], lo[1]:hi[1]+1, lo[2]:hi[2]+1] = BOUNDARY_VALUE
    result[hi[0], lo[1]:hi[1]+1, lo[2]:hi[2]+1] = BOUNDARY_VALUE
    # Y faces
    result[lo[0]:hi[0]+1, lo[1], lo[2]:hi[2]+1] = BOUNDARY_VALUE
    result[lo[0]:hi[0]+1, hi[1], lo[2]:hi[2]+1] = BOUNDARY_VALUE
    # Z faces
    result[lo[0]:hi[0]+1, lo[1]:hi[1]+1, lo[2]] = BOUNDARY_VALUE
    result[lo[0]:hi[0]+1, lo[1]:hi[1]+1, hi[2]] = BOUNDARY_VALUE

    return result


def bound_nrrd(input_path, output_path, pad=3):
    """Read an NRRD, add boundary markers, and write the result.

    All spatial metadata (space, space directions, space origin, kinds, etc.)
    is preserved from the source file into the output.

    Args:
        input_path: Path to the source NRRD file.
        output_path: Path for the bounded output NRRD file.
        pad: Number of voxels to expand the bounding box by.

    Returns:
        True on success, False on failure.
    """
    print("Adding boundary markers to %s..." % input_path)

    try:
        data, header = nrrd.read(input_path)
    except Exception as e:
        print("Error reading %s: %s" % (input_path, e))
        return False

    if data.ndim != 3:
        print("Error: Expected 3D volume, got %dD" % data.ndim)
        return False

    bounded = add_boundary(data, pad=pad)

    # Debug: show what keys pynrrd found in the source header
    print("  Source header keys: %s" % sorted(header.keys()))
    for k in ["space", "space directions", "space origin", "kinds"]:
        if k in header:
            print("  %s: %s" % (k, header[k]))

    # Build output header preserving ALL spatial metadata from the source.
    # We copy the ENTIRE source header so nothing is lost, then let pynrrd
    # override type/dimension/sizes from the data array automatically.
    output_header = dict(header)

    # ImageJ requires "space directions" -- if missing, synthesize from
    # "spacings" or fall back to identity so ImageJ can still open the file.
    if "space directions" not in output_header:
        if "spacings" in header:
            sp = header["spacings"]
            output_header["space directions"] = np.diag(sp).tolist()
            print("Warning: synthesized space directions from spacings: %s" % sp)
        else:
            output_header["space directions"] = np.identity(3).tolist()
            print("Warning: no space directions in source, using identity matrix")
        if "space" not in output_header:
            output_header["space"] = "left-posterior-superior"

    # NRRD v5 requires "space" when "space directions" is present.
    # ImageJ will ignore space directions entirely without it.
    if "space directions" in output_header and "space" not in output_header:
        output_header["space"] = "left-posterior-superior"
        print("  Added missing 'space' field (required by ImageJ)")

    print("  Output header space directions: %s" % repr(output_header.get("space directions")))
    print("  Output header space: %s" % repr(output_header.get("space")))
    print("Saving result to %s..." % output_path)
    try:
        nrrd.write(output_path, bounded, header=output_header)
    except Exception as e:
        print("Error writing %s: %s" % (output_path, e))
        return False

    # Verify the written file actually has space directions
    try:
        _, verify_header = nrrd.read(output_path)
        if "space directions" in verify_header:
            print("  Verified: output has space directions")
        else:
            print("  WARNING: output is MISSING space directions! Keys: %s" % sorted(verify_header.keys()))
    except Exception as e:
        print("  WARNING: could not verify output: %s" % e)

    # Set permissions (best effort)
    try:
        os.chmod(output_path, 0o777)
    except Exception:
        pass

    print("Done.")
    return True


def main():
    if len(sys.argv) != 4:
        print("Usage: %s <pad> <input.nrrd> <output.nrrd>" % sys.argv[0])
        sys.exit(1)

    try:
        pad = int(sys.argv[1])
    except ValueError:
        print("Error: pad must be an integer, got '%s'" % sys.argv[1])
        sys.exit(1)

    input_path = sys.argv[2]
    output_path = sys.argv[3]

    if not os.path.exists(input_path):
        print("Error: Input file not found: %s" % input_path)
        sys.exit(1)

    success = bound_nrrd(input_path, output_path, pad=pad)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
