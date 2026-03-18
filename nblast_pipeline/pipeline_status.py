"""Pipeline status tracking and Solr error reporting.

This module is used by the Jenkins upload pipeline to:
- Write/inspect per-image status markers (volume.status)
- Report errors (and successes) to the VFB Solr ontology collection
- Classify errors as user-fixable vs processing issues
- Clean up directories for user-fixable errors (user must re-upload)

The Solr schema should include a `description` field (text) where we can
store user-visible processing status information.

Note: This module avoids raising exceptions on I/O/solr failures wherever
possible so that the pipeline can continue processing other images.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

import pysolr


# --- Error categories (used for Solr reporting) --------------------------------

# User-fixable errors: the uploaded file is fundamentally broken.
# The user must fix the issue and re-upload with a new VFBu_ ID.
# The entire VFBu_ directory tree should be deleted after reporting to Solr.
SWC_PARSE_ERROR = "SWC_PARSE_ERROR"
SWC_OUT_OF_BOUNDS = "SWC_OUT_OF_BOUNDS"
EMPTY_VOXELIZATION = "EMPTY_VOXELIZATION"
TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
INVALID_NRRD = "INVALID_NRRD"

# Processing errors: the file might be OK but a tool/stage failed.
# Keep the files — may resolve on retry or with a tool fix.
SHAPE_MISMATCH = "SHAPE_MISMATCH"
BOUNDING_FAILED = "BOUNDING_FAILED"
TIF_CONVERSION_FAILED = "TIF_CONVERSION_FAILED"
WLZ_CONVERSION_FAILED = "WLZ_CONVERSION_FAILED"
OBJ_GENERATION_FAILED = "OBJ_GENERATION_FAILED"

# Set of error categories where the user must fix and re-upload.
USER_FIXABLE_ERRORS = frozenset({
    SWC_PARSE_ERROR,
    SWC_OUT_OF_BOUNDS,
    EMPTY_VOXELIZATION,
    TEMPLATE_NOT_FOUND,
    INVALID_NRRD,
})


# --- Status file markers -------------------------------------------------------

STATUS_FILE_NAME = "volume.status"

STATUS_NRRD_OK = "NRRD_OK"
STATUS_NRRD_FAILED = "NRRD_FAILED"
STATUS_BOUNDED_OK = "BOUNDED_OK"
STATUS_BOUNDED_FAILED = "BOUNDED_FAILED"
STATUS_TIF_OK = "TIF_OK"
STATUS_TIF_FAILED = "TIF_FAILED"
STATUS_WLZ_OK = "WLZ_OK"
STATUS_WLZ_FAILED = "WLZ_FAILED"
STATUS_OBJ_OK = "OBJ_OK"
STATUS_OBJ_FAILED = "OBJ_FAILED"
STATUS_COMPLETE = "COMPLETE"


DEFAULT_SOLR_URL = "http://solr.virtualflybrain.org/solr/ontology/"


def _get_solr(solr_url: Optional[str] = None) -> pysolr.Solr:
    """Create a pysolr.Solr client."""
    return pysolr.Solr(solr_url or DEFAULT_SOLR_URL, timeout=10)


def report_error(
    image_id: str,
    error_category: str,
    error_detail: Optional[str] = None,
    solr_url: Optional[str] = None,
) -> bool:
    """Write a user-facing error message to the Solr description field.

    Returns True if Solr update succeeded, False otherwise.
    """
    msg = f"{error_category}: {error_detail or '(no details)'}"

    try:
        solr = _get_solr(solr_url)
        solr.add(
            [
                {
                    "id": image_id,
                    "description": {"set": msg},
                }
            ],
            commit=True,
        )
        return True
    except Exception:
        return False


def report_success(
    image_id: str,
    solr_url: Optional[str] = None,
    message: Optional[str] = None,
) -> bool:
    """Clear any previous error in the Solr description field (or set a success message)."""
    msg = message or "Processing succeeded"
    try:
        solr = _get_solr(solr_url)
        solr.add(
            [
                {
                    "id": image_id,
                    "description": {"set": msg},
                }
            ],
            commit=True,
        )
        return True
    except Exception:
        return False


def write_status(base_dir: str, status_string: str) -> None:
    """Write a status marker file (volume.status) in the given directory."""
    try:
        status_path = os.path.join(base_dir, STATUS_FILE_NAME)
        with open(status_path, "w", encoding="utf-8") as f:
            f.write(status_string.strip() + "\n")
    except Exception:
        # Best effort only
        pass


def read_status(base_dir: str) -> Optional[str]:
    """Read the status marker file (volume.status) if it exists."""
    try:
        status_path = os.path.join(base_dir, STATUS_FILE_NAME)
        if not os.path.exists(status_path):
            return None
        with open(status_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def is_user_fixable(error_category: str) -> bool:
    """Return True if this error requires the user to fix and re-upload."""
    return error_category in USER_FIXABLE_ERRORS


def clean_upload_directory(
    image_dir: str | Path,
    image_id: str,
    error_category: str,
    error_detail: str,
    solr_url: Optional[str] = None,
) -> bool:
    """Report error to Solr and delete the entire VFBu_ directory tree.

    Called when a user-fixable error is detected. The user must fix the source
    file and re-upload, which creates a new VFBu_ ID, so all files under the
    old VFBu_ directory can be safely removed.

    Args:
        image_dir: The VFBu_*/VFB_*/ directory (or parent VFBu_*/ directory).
        image_id: The VFBu_ identifier for Solr reporting.
        error_category: One of the USER_FIXABLE_ERRORS categories.
        error_detail: Human-readable description of the problem.
        solr_url: Optional Solr URL override.

    Returns:
        True if cleanup succeeded, False on error.
    """
    image_dir = Path(image_dir)

    # Report to Solr first (before deleting files)
    report_error(image_id, error_category, error_detail, solr_url)

    # Find the VFBu_ parent directory to delete the whole tree
    # Directory structure: /IMAGE_PRIVATE/VFBu_<id>/VFB_<template>/
    vfbu_dir = image_dir
    while vfbu_dir.name and not vfbu_dir.name.startswith("VFBu_"):
        vfbu_dir = vfbu_dir.parent

    if not vfbu_dir.name.startswith("VFBu_"):
        print(f"  WARNING: Could not find VFBu_ parent for {image_dir}")
        return False

    try:
        print(f"  Cleaning up {vfbu_dir} (user-fixable error: {error_category})")
        shutil.rmtree(str(vfbu_dir))
        return True
    except Exception as e:
        print(f"  WARNING: Failed to remove {vfbu_dir}: {e}")
        return False
