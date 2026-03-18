#!/usr/bin/env python3
"""Post-docker verification of the upload conversion pipeline.

Run this script after the Docker-based conversion stages (bounding, ImageJ,
Woolz, OBJ generation) to check which images completed successfully and
update Solr status accordingly.

Usage:
  python nblast_pipeline/verify_pipeline.py --base-path /IMAGE_PRIVATE
  python nblast_pipeline/verify_pipeline.py --base-path /IMAGE_PRIVATE --dry-run
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from .full_pipeline import ConversionPaths
    from .pipeline_status import (
        BOUNDING_FAILED,
        OBJ_GENERATION_FAILED,
        TIF_CONVERSION_FAILED,
        WLZ_CONVERSION_FAILED,
        STATUS_BOUNDED_FAILED,
        STATUS_COMPLETE,
        STATUS_NRRD_FAILED,
        STATUS_OBJ_FAILED,
        STATUS_TIF_FAILED,
        STATUS_WLZ_FAILED,
        report_error,
        report_success,
        write_status,
    )
except (ImportError, SystemError):
    from nblast_pipeline.full_pipeline import ConversionPaths
    from nblast_pipeline.pipeline_status import (
        BOUNDING_FAILED,
        OBJ_GENERATION_FAILED,
        TIF_CONVERSION_FAILED,
        WLZ_CONVERSION_FAILED,
        STATUS_BOUNDED_FAILED,
        STATUS_COMPLETE,
        STATUS_NRRD_FAILED,
        STATUS_OBJ_FAILED,
        STATUS_TIF_FAILED,
        STATUS_WLZ_FAILED,
        report_error,
        report_success,
        write_status,
    )


# Stage result constants
STAGE_COMPLETE = "COMPLETE"
STAGE_NRRD_FAILED = "NRRD_FAILED"
STAGE_BOUNDING_FAILED = "BOUNDING_FAILED"
STAGE_TIF_FAILED = "TIF_FAILED"
STAGE_WLZ_FAILED = "WLZ_FAILED"
STAGE_OBJ_FAILED = "OBJ_FAILED"


@dataclass
class VerificationResult:
    image_id: str
    directory: Path
    stage: str
    is_complete: bool
    detail: str


def _file_ok(path: Path) -> bool:
    """Return True if path exists and is non-empty."""
    try:
        return path.exists() and path.stat().st_size > 0
    except OSError:
        return False


def verify_directory(paths: ConversionPaths) -> VerificationResult:
    """Check which pipeline outputs exist and determine the completion stage."""
    image_id = paths.image_id
    d = paths.dir

    has_nrrd = _file_ok(paths.nrrd)
    has_wlz = _file_ok(paths.wlz)
    has_obj = _file_ok(paths.obj) or _file_ok(paths.man_obj)
    has_tif = _file_ok(paths.tif)
    has_bounded = _file_ok(paths.bounded_nrrd)

    if has_wlz and has_obj:
        return VerificationResult(image_id, d, STAGE_COMPLETE, True, "All outputs present")

    if has_wlz and not has_obj:
        return VerificationResult(image_id, d, STAGE_OBJ_FAILED, False,
                                  "WLZ exists but no OBJ found")

    if has_tif:
        return VerificationResult(image_id, d, STAGE_WLZ_FAILED, False,
                                  "TIF exists but no WLZ produced")

    if has_bounded:
        return VerificationResult(image_id, d, STAGE_TIF_FAILED, False,
                                  "Bounded NRRD exists but no TIF or WLZ produced")

    if has_nrrd:
        return VerificationResult(image_id, d, STAGE_BOUNDING_FAILED, False,
                                  "NRRD exists but no downstream outputs found")

    return VerificationResult(image_id, d, STAGE_NRRD_FAILED, False,
                              "No volume.nrrd found")


# Maps stage result to (status marker, error category for Solr)
_STATUS_MAP = {
    STAGE_COMPLETE: (STATUS_COMPLETE, None),
    STAGE_OBJ_FAILED: (STATUS_OBJ_FAILED, OBJ_GENERATION_FAILED),
    STAGE_WLZ_FAILED: (STATUS_WLZ_FAILED, WLZ_CONVERSION_FAILED),
    STAGE_TIF_FAILED: (STATUS_TIF_FAILED, TIF_CONVERSION_FAILED),
    STAGE_BOUNDING_FAILED: (STATUS_BOUNDED_FAILED, BOUNDING_FAILED),
    STAGE_NRRD_FAILED: (STATUS_NRRD_FAILED, "NRRD_GENERATION_FAILED"),
}


def apply_status(result: VerificationResult, solr_url: Optional[str]) -> None:
    """Write volume.status and report to Solr based on the verification result."""
    status_str, error_cat = _STATUS_MAP[result.stage]
    write_status(str(result.directory), status_str)

    if result.is_complete:
        report_success(result.image_id, solr_url, "Pipeline verification: all outputs present")
    elif error_cat:
        report_error(result.image_id, error_cat, result.detail, solr_url)


def verify_all(
    base_path: str,
    solr_url: Optional[str],
    dry_run: bool = False,
) -> list[VerificationResult]:
    """Verify all upload directories and optionally update status/Solr."""
    pattern = os.path.join(base_path, "VFBu_*", "VFB_*", "")
    directories = sorted(glob.glob(pattern))

    if not directories:
        print(f"No VFBu_*/VFB_*/ directories found under {base_path}")
        return []

    results = []
    for d in directories:
        paths = ConversionPaths(Path(d))
        result = verify_directory(paths)
        results.append(result)

        status_icon = "OK" if result.is_complete else "FAIL"
        print(f"  [{status_icon}] {result.image_id}: {result.detail}")

        if not dry_run:
            apply_status(result, solr_url)

    return results


def print_summary(results: list[VerificationResult]) -> None:
    """Print a summary of verification results."""
    if not results:
        return

    counts = Counter(r.stage for r in results)
    total = len(results)
    complete = counts.get(STAGE_COMPLETE, 0)
    failed = total - complete

    print()
    print("=== Pipeline Verification Summary ===")
    print(f"Total directories checked: {total}")
    print(f"  Complete:  {complete}")
    print(f"  Failed:    {failed}")
    if failed:
        for stage in [STAGE_NRRD_FAILED, STAGE_BOUNDING_FAILED,
                      STAGE_TIF_FAILED, STAGE_WLZ_FAILED, STAGE_OBJ_FAILED]:
            c = counts.get(stage, 0)
            if c:
                print(f"    {stage}: {c}")


def main():
    parser = argparse.ArgumentParser(
        description="Verify pipeline outputs and update Solr status"
    )
    parser.add_argument("--base-path", default="/IMAGE_PRIVATE",
                        help="Base path where VFBu_*/ directories live.")
    parser.add_argument("--solr-url", default=None,
                        help="Solr URL for reporting status updates")
    parser.add_argument("--dry-run", action="store_true",
                        help="Check outputs without writing status or updating Solr")
    args = parser.parse_args()

    results = verify_all(args.base_path, args.solr_url, dry_run=args.dry_run)
    print_summary(results)

    if any(not r.is_complete for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
