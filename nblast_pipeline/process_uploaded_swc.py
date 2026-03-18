#!/usr/bin/env python3
"""Orchestrate processing of user-uploaded SWC files.

This script is meant to replace the inline Jenkins Step 2 Python code.
It scans for uploaded SWC files and converts them to NRRD, writing status
markers and reporting errors to Solr for visibility.

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
from swc_to_nrrd import convert_swc_to_nrrd_with_status


def get_template_path(template_id: str) -> str:
    """Construct template path from VFB template ID."""
    # template_id format: VFB_00101567
    # Path format: /IMAGE_DATA/VFB/i/0010/1567/VFB_00101567/template.nrrd
    part1 = template_id[4:8]  # e.g., "0010"
    part2 = template_id[8:12]  # e.g., "1567"
    return f"/IMAGE_DATA/VFB/i/{part1}/{part2}/{template_id}/template.nrrd"


def find_swc_files(base_path: str) -> list[str]:
    pattern = os.path.join(base_path, "VFBu_*/VFB_*/volume.swc")
    return sorted(glob.glob(pattern))


def process_file(
    swc_path: str,
    solr_url: str | None = None,
    redo: bool = False,
    dry_run: bool = False,
) -> dict:
    """Process a single SWC file and return the status dict.

    Args:
        dry_run: If True, do not actually run conversions, just report what would run.
    """
    swc_path = Path(swc_path)
    base_dir = str(swc_path.parent)
    image_id = swc_path.parents[1].name
    template_id = swc_path.parent.name
    nrrd_path = str(swc_path.with_suffix(".nrrd"))

    if not redo and os.path.exists(nrrd_path):
        return {"skipped": True, "reason": "exists"}

    if dry_run:
        print(f"[DRY RUN] Would convert {swc_path} -> {nrrd_path}")
        return {"success": True, "dry_run": True}

    template_path = get_template_path(template_id)

    if not os.path.exists(template_path):
        error_category = "TEMPLATE_NOT_FOUND"
        error_detail = f"Template not found: {template_path}"
        write_status(base_dir, f"{STATUS_NRRD_FAILED}:{error_category}")
        report_error(image_id, error_category, error_detail, solr_url)
        return {"success": False, "error_category": error_category, "error_detail": error_detail}

    result = convert_swc_to_nrrd_with_status(str(swc_path), template_path, nrrd_path)

    if result.get("success"):
        write_status(base_dir, STATUS_NRRD_OK)
        return {"success": True, **result}

    error_category = result.get("error_category") or "UNKNOWN"
    error_detail = result.get("error_detail")
    write_status(base_dir, f"{STATUS_NRRD_FAILED}:{error_category}")
    report_error(image_id, error_category, error_detail, solr_url)
    return {"success": False, **result}


def main():
    parser = argparse.ArgumentParser(description="Process user-uploaded SWC files into NRRD volumes")
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
        help="Re-run conversion even if volume.nrrd already exists",
    )
    args = parser.parse_args()

    swc_files = find_swc_files(args.base_path)
    if not swc_files:
        print(f"No SWC files found under {args.base_path}")
        return 0

    for swc_path in swc_files:
        print(f"Processing: {swc_path}")
        result = process_file(swc_path, solr_url=args.solr_url, redo=args.redo)
        if result.get("skipped"):
            print(f"  Skipped (already has NRRD)")
        elif result.get("success"):
            print(f"  Success: voxels={result.get('voxel_count')}")
        else:
            print(f"  Failed: {result.get('error_category')}: {result.get('error_detail')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
