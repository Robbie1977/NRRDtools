# NBLAST Pipeline Helpers

This directory contains code used by the **NBLAST upload pipeline** (Jenkins) to:

- Convert user-uploaded SWC neuron files into NRRD (SWC→NRRD)
- Track per-image processing status via `volume.status`
- Report errors back into Solr so users can see why upload processing failed

## Files

- `pipeline_status.py` — Solr reporting + disk-based status markers (`volume.status`).
- `process_uploaded_swc.py` — Jenkins Step 2 replacement: finds uploaded `volume.swc` files and converts them to `volume.nrrd`.

## Usage

### Run SWC→NRRD conversion for all uploads (Jenkins Step 2)

```bash
python nblast_pipeline/process_uploaded_swc.py --base-path /IMAGE_PRIVATE
```

### Run the full NBLAST conversion pipeline (SWC → NRRD → TIF → WLZ → OBJ)

```bash
python nblast_pipeline/full_pipeline.py --base-path /IMAGE_PRIVATE
```

This will:
1. Convert `volume.swc` → `volume.nrrd`
2. Convert `volume_bounded.nrrd` → `volume_bounded.tif` (via ImageJ macro)
3. Convert `volume_bounded.tif` → `volume.wlz` (via Woolz tools)
4. Generate `volume.obj` from `volume.nrrd` (via `maxProjVol.py`)

Status markers are written to `volume.status` and errors are reported to Solr.

### Solr error reporting

`pipeline_status.report_error(image_id, category, detail, solr_url)` writes a user-visible message into the Solr `description` field for `image_id`.

### Status markers

Each uploaded image directory includes `volume.status`, which will contain values like:

- `NRRD_OK`
- `NRRD_FAILED:<CATEGORY>`

This allows downstream pipeline steps to skip or abort processing based on previous failures.

## Notes

- The package is intentionally self-contained under `nblast_pipeline` so that pipeline-specific logic is isolated from the rest of `NRRDtools`.
- The submodule supports both being executed as a script and as a module (`python -m nblast_pipeline.process_uploaded_swc`).
