"""Backward-compatible wrapper to run the full NBLAST conversion pipeline.

This script exists so the pipeline can run with a simple:

    python full_pipeline.py

while the implementation lives inside the `nblast_pipeline` package.
"""

from nblast_pipeline.full_pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
