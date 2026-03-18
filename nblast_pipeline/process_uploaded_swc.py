#!/usr/bin/env python3
"""Orchestrate processing of user-uploaded SWC and NRRD files.

This script is meant to replace the inline Jenkins Step 2 Python code.
It scans for uploaded SWC files and converts them to NRRD, validates
uploaded NRRD files, writes status markers and reports errors to Solr.

Usage:
  process_uploaded_swc.py --base-path /IMAGE_PRIVATE
"""

from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path

from nblast_pipeline.pipeline_status import (
    STATUS_NRRD_FAILED,
    STATUS_NRRD_OK,
    write_status,
    report_error,
)
from swc_to_nrrd import (
    convert_swc_to_nrrd_with_status,
    is_valid_nrrd,
    strip_leading_whitespace,
    clean_derived_files,
)


def get_template_path(template_id: str) -> str:
    """Construct template path from VFB template ID."""
    part1 = template_id[4:8]
    part2 = template_id[8:12]
    return f"/IMAGE_DATA/VFB/i/{part1}/{part2}/{template_id}/template.nrrd"


def find_swc_files(base_path: str) -> list[str]:
    pattern = os.path.join(base_path, "VFBu_*/VFB_*/volume.swc")
    return sorted(glob.glob(pattern))


def find_upload_dirs(base_path: str) -> list[str]:
    """Find all VFBu_*/VFB_*/ upload directories (both SWC and NRRD uploads)."""
    pattern = os.path.join(base_path, "VFBu_*", "VFB_*", "")
    return sorted(glob.glob(pattern))


def process_file(
    swc_path: str,
    solr_url: str | None = None,
    redo: bool = False,
    dry_run: bool = False,
) -> dict:
    """Process a single SWC file and return the status dict."""
    swc_path = Path(swc_path)
    base_dir = str(swc_path.parent)
    image_id = swc_path.parents[1].name
    template_id = swc_path.parent.name
    nrrd_path = str(swc_path.with_suffix(".nrrd"))

    template_path = get_template_path(template_id)

    if not os.path.exists(template_path):
        if dry_run:
            print(f"[DRY RUN] {swc_path}: template missing ({template_path})")
            return {"success": False, "dry_run": True, "error_category": "TEMPLATE_NOT_FOUND"}
        error_category = "TEMPLATE_NOT_FOUND"
        error_detail = f"Template not found: {template_path}"
        write_status(base_dir, f"{STATUS_NRRD_FAILED}:{error_category}")
        report_error(image_id, error_category, error_detail, solr_url)
        return {"success": False, "error_category": error_category, "error_detail": error_detail}

    # Validate existing NRRD if present
    if not redo and os.path.exists(nrrd_path):
        import nrrd

        template_data, _ = nrrd.read(template_path)
        valid, reason = is_valid_nrrd(nrrd_path, template_data.shape)
        if valid:
            return {"skipped": True, "reason": "already valid"}
        else:
            print(f"  NRRD invalid ({reason}), will regenerate")

    if dry_run:
        print(f"[DRY RUN] Would convert {swc_path} -> {nrrd_path}")
        return {"success": True, "dry_run": True}

    # Preprocess SWC
    strip_leading_whitespace(str(swc_path))

    # Clean derived files before regenerating
    clean_derived_files(swc_path)

    result = convert_swc_to_nrrd_with_status(str(swc_path), template_path, nrrd_path)

    if result.get("success"):
        write_status(base_dir, STATUS_NRRD_OK)
        return {"success": True, **result}

    error_category = result.get("error_category") or "UNKNOWN"
    error_detail = result.get("error_detail")
    write_status(base_dir, f"{STATUS_NRRD_FAILED}:{error_category}")
    report_error(image_id, error_category, error_detail, solr_url)
    return {"success": False, **result}


def validate_uploaded_nrrd(
    nrrd_dir: str,
    solr_url: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Validate a directly uploaded NRRD file (no SWC source).

    Returns status dict similar to process_file.
    """
    nrrd_dir = Path(nrrd_dir)
    nrrd_path = nrrd_dir / "volume.nrrd"
    image_id = nrrd_dir.parent.name
    template_id = nrrd_dir.name

    if not nrrd_path.exists():
        return {"skipped": True, "reason": "no NRRD file"}

    template_path = get_template_path(template_id)

    if not os.path.exists(template_path):
        if dry_run:
            print(f"[DRY RUN] {nrrd_path}: template missing, cannot validate shape")
            return {"success": True, "dry_run": True}
        # No template to validate against — accept the NRRD as-is
        valid, reason = is_valid_nrrd(str(nrrd_path))
    else:
        import nrrd as nrrd_mod

        template_data, _ = nrrd_mod.read(template_path)
        valid, reason = is_valid_nrrd(str(nrrd_path), template_data.shape)

    if valid:
        write_status(str(nrrd_dir), STATUS_NRRD_OK)
        return {"success": True, "reason": reason}

    if dry_run:
        print(f"[DRY RUN] {nrrd_path}: invalid ({reason})")
        return {"success": False, "dry_run": True}

    error_detail = f"Uploaded NRRD invalid: {reason}"
    write_status(str(nrrd_dir), f"{STATUS_NRRD_FAILED}:INVALID_NRRD")
    report_error(image_id, "INVALID_NRRD", error_detail, solr_url)
    return {"success": False, "error_category": "INVALID_NRRD", "error_detail": error_detail}


def main():
    parser = argparse.ArgumentParser(description="Process user-uploaded SWC and NRRD files")
    parser.add_argument(
        "--base-path",
        default="/IMAGE_PRIVATE",
        help="Base path where VFBu_* directories live (default: /IMAGE_PRIVATE)",
    )
    parser.add_argument(
        "--solr-url",
        default=None,
        help="Optional Solr URL to use for publishing error/success messages",
    )
    parser.add_argument(
        "--redo",
        action="store_true",
        help="Re-run conversion even if volume.nrrd already exists and is valid",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Just list files and validation status, don't process",
    )
    args = parser.parse_args()

    # Collect all upload directories
    all_dirs = find_upload_dirs(args.base_path)
    if not all_dirs:
        print(f"No upload directories found under {args.base_path}")
        return 0

    # Separate SWC uploads from NRRD-only uploads
    swc_dirs = set()
    results = {"success": [], "failed": [], "skipped": []}

    # Stage 1: Process SWC files
    swc_files = find_swc_files(args.base_path)
    for swc_path in swc_files:
        swc_dirs.add(str(Path(swc_path).parent))
        print(f"Processing SWC: {swc_path}")
        result = process_file(swc_path, solr_url=args.solr_url, redo=args.redo, dry_run=args.dry_run)
        if result.get("skipped"):
            print(f"  Skipped ({result.get('reason', 'already valid')})")
            results["skipped"].append(swc_path)
        elif result.get("success"):
            print(f"  Success: voxels={result.get('voxel_count')}")
            results["success"].append(swc_path)
        else:
            print(f"  Failed: {result.get('error_category')}: {result.get('error_detail')}")
            results["failed"].append(swc_path)

    # Stage 2: Validate NRRD-only uploads (directories without SWC)
    for d in all_dirs:
        if d.rstrip("/") in swc_dirs:
            continue
        nrrd_path = os.path.join(d, "volume.nrrd")
        if not os.path.exists(nrrd_path):
            continue
        print(f"Validating uploaded NRRD: {nrrd_path}")
        result = validate_uploaded_nrrd(d, solr_url=args.solr_url, dry_run=args.dry_run)
        if result.get("skipped"):
            results["skipped"].append(nrrd_path)
        elif result.get("success"):
            print(f"  Valid")
            results["success"].append(nrrd_path)
        else:
            print(f"  Invalid: {result.get('error_detail')}")
            results["failed"].append(nrrd_path)

    # Summary
    total = len(results["success"]) + len(results["failed"]) + len(results["skipped"])
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total files: {total}")
    print(f"Skipped (already valid): {len(results['skipped'])}")
    print(f"Successfully processed: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")

    if results["failed"]:
        print("\nFailed files:")
        for path in results["failed"]:
            print(f"  {path}")

    return 0  # failures shouldn't stop the pipeline


if __name__ == "__main__":
    raise SystemExit(main())
