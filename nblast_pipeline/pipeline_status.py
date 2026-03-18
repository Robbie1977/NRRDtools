"""Pipeline status tracking and Solr error reporting.

This module is used by the Jenkins upload pipeline to:
- Write/inspect per-image status markers (volume.status)
- Report errors (and successes) to the VFB Solr ontology collection

The Solr schema should include a `description` field (text) where we can
store user-visible processing status information.

Note: This module avoids raising exceptions on I/O/solr failures wherever
possible so that the pipeline can continue processing other images.
"""

from __future__ import annotations

import os
from typing import Optional

import pysolr


# --- Error categories (used for Solr reporting) --------------------------------

SWC_PARSE_ERROR = "SWC_PARSE_ERROR"
SWC_OUT_OF_BOUNDS = "SWC_OUT_OF_BOUNDS"
EMPTY_VOXELIZATION = "EMPTY_VOXELIZATION"
SHAPE_MISMATCH = "SHAPE_MISMATCH"
BOUNDING_FAILED = "BOUNDING_FAILED"
TIF_CONVERSION_FAILED = "TIF_CONVERSION_FAILED"
WLZ_CONVERSION_FAILED = "WLZ_CONVERSION_FAILED"
OBJ_GENERATION_FAILED = "OBJ_GENERATION_FAILED"


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
