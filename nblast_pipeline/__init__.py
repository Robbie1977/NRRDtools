"""NBLAST pipeline utilities.

This package contains code used by the Jenkins NBLAST pipeline (SWC→NRRD→TIF→WLZ+OBJ).

The intent is to keep pipeline-specific helpers isolated from the rest of the NRRDtools codebase.

Public API:
- pipeline_status: Solr + status-marker helpers
- process_uploaded_swc: entry point used by Jenkins Step 2 (SWC→NRRD)
"""

from . import pipeline_status  # noqa: F401
from . import process_uploaded_swc  # noqa: F401
from . import full_pipeline  # noqa: F401

__all__ = ["pipeline_status", "process_uploaded_swc", "full_pipeline"]
