"""Entry point for the NBLAST upload pipeline (SWC→NRRD step).

This file is a small wrapper that delegates to `nblast_pipeline.process_uploaded_swc`.
It exists to preserve backwards compatibility for callers that expect a top-level script.
"""

from nblast_pipeline.process_uploaded_swc import main


if __name__ == "__main__":
    raise SystemExit(main())
