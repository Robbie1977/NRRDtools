"""Backwards-compatible shim for NBLAST pipeline status helpers.

The real implementation lives under `nblast_pipeline.pipeline_status`. This shim
exists so that any existing imports (`import pipeline_status`) continue to work
without changing dependent code.
"""

from nblast_pipeline.pipeline_status import *  # noqa: F401,F403
