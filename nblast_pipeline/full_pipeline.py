#!/usr/bin/env python3
"""Run the full NBLAST upload conversion pipeline.

This script performs the same work previously done by a chain of Jenkins
`docker exec` commands. It is intended to be run inside the same environment
that has access to all required tools (ImageJ, Woolz executables, etc.).

Pipeline stages (approximate):
  1) SWC --> NRRD (existing)
  2) bounded NRRD --> TIF (ImageJ macro)
  3) TIF --> WLZ (Woolz tools)
  4) NRRD --> OBJ (maxProjVol.py)

Each stage updates a per-image status marker (`volume.status`) and reports
failures to Solr via `pipeline_status.report_error()`.
"""

from __future__ import annotations

import argparse
import glob
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

import nrrd

# Support running as a module (python -m nblast_pipeline.full_pipeline) and as a script
# (python nblast_pipeline/full_pipeline.py).
import os
import sys

# Ensure the repository root directory is on sys.path so imports work even when
# this file is executed directly from within nblast_pipeline/.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from .pipeline_status import (
        BOUNDING_FAILED,
        OBJ_GENERATION_FAILED,
        STATUS_COMPLETE,
        STATUS_NRRD_FAILED,
        STATUS_NRRD_OK,
        STATUS_OBJ_FAILED,
        STATUS_OBJ_OK,
        STATUS_TIF_FAILED,
        STATUS_TIF_OK,
        STATUS_WLZ_FAILED,
        STATUS_WLZ_OK,
        STATUS_BOUNDED_FAILED,
        STATUS_BOUNDED_OK,
        report_error,
        report_success,
        write_status,
    )
    from .process_uploaded_swc import find_swc_files, find_upload_dirs, process_file
except (ImportError, SystemError):
    from nblast_pipeline.pipeline_status import (
        BOUNDING_FAILED,
        OBJ_GENERATION_FAILED,
        STATUS_COMPLETE,
        STATUS_NRRD_FAILED,
        STATUS_NRRD_OK,
        STATUS_OBJ_FAILED,
        STATUS_OBJ_OK,
        STATUS_TIF_FAILED,
        STATUS_TIF_OK,
        STATUS_WLZ_FAILED,
        STATUS_WLZ_OK,
        STATUS_BOUNDED_FAILED,
        STATUS_BOUNDED_OK,
        report_error,
        report_success,
        write_status,
    )
    from nblast_pipeline.process_uploaded_swc import find_swc_files, find_upload_dirs, process_file


@dataclass
class ConversionPaths:
    """Paths for a single upload directory."""

    dir: Path

    @property
    def image_id(self) -> str:
        # /.../VFBu_<id>/VFB_<template>/
        return self.dir.parent.name

    @property
    def swc(self) -> Path:
        return self.dir / "volume.swc"

    @property
    def nrrd(self) -> Path:
        return self.dir / "volume.nrrd"

    @property
    def bounded_nrrd(self) -> Path:
        return self.dir / "volume_bounded.nrrd"

    @property
    def tif(self) -> Path:
        return self.dir / "volume_bounded.tif"

    @property
    def wlz(self) -> Path:
        return self.dir / "volume.wlz"

    @property
    def obj(self) -> Path:
        return self.dir / "volume.obj"

    @property
    def man_obj(self) -> Path:
        return self.dir / "volume_man.obj"


def _run(cmd: Sequence[str], cwd: Optional[str] = None, env: Optional[dict] = None) -> Tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out.strip(), err.strip()


def _ensure_executable(path: str) -> bool:
    return os.path.isfile(path) and os.access(path, os.X_OK)


def _try_chmod(path: Path, mode: int = 0o777) -> None:
    try:
        path.chmod(mode)
    except Exception:
        pass


def _read_voxel_sizes_from_nrrd(path: Path) -> Optional[Tuple[float, float, float]]:
    try:
        _, header = nrrd.read(path)
        dirs = header.get("space directions")
        if not dirs or len(dirs) != 3:
            return None
        import numpy as np

        vs = [float(np.linalg.norm(d)) for d in dirs]
        return tuple(vs)
    except Exception:
        return None


def convert_bounded_nrrd_to_tif(
    paths: ConversionPaths,
    imagej_binary: str,
    macro_path: str,
    solr_url: Optional[str],
    dry_run: bool = False,
) -> bool:
    """Run ImageJ macro to create a TIF from a bounded NRRD."""

    if not paths.bounded_nrrd.exists():
        write_status(paths.dir, STATUS_BOUNDED_FAILED)
        report_error(paths.image_id, BOUNDING_FAILED, "Missing bounded NRRD", solr_url)
        return False

    if paths.wlz.exists() or paths.tif.exists():
        # Already produced.
        write_status(paths.dir, STATUS_TIF_OK)
        return True

    if dry_run:
        print(f"[DRY RUN] Would run ImageJ to convert {paths.bounded_nrrd} -> {paths.tif}")
        write_status(paths.dir, STATUS_TIF_OK)
        return True

    if not _ensure_executable(imagej_binary):
        report_error(
            paths.image_id,
            "IMAGEJ_MISSING",
            f"ImageJ binary not found: {imagej_binary}",
            solr_url,
        )
        write_status(paths.dir, STATUS_TIF_FAILED)
        return False

    cmd = [imagej_binary, "--headless", "--default-gc", "-macro", macro_path, str(paths.bounded_nrrd)]

    code, out, err = _run(cmd)
    if code != 0 or not paths.tif.exists():
        report_error(
            paths.image_id,
            "TIF_CONVERSION_FAILED",
            f"ImageJ failed (code={code}) stdout={out!r} stderr={err!r}",
            solr_url,
        )
        write_status(paths.dir, STATUS_TIF_FAILED)
        return False

    _try_chmod(paths.tif)
    write_status(paths.dir, STATUS_TIF_OK)
    return True


def convert_tif_to_wlz(
    paths: ConversionPaths,
    wlz_ext: str,
    wlz_threshold: str,
    wlz_set_voxel: str,
    solr_url: Optional[str],
    cleanup_tif: bool = True,
    dry_run: bool = False,
) -> bool:
    """Convert a TIF to WLZ using Woolz tools."""

    if paths.wlz.exists():
        write_status(paths.dir, STATUS_WLZ_OK)
        return True

    if dry_run:
        print(f"[DRY RUN] Would run Woolz conversion for {paths.tif} -> {paths.wlz}")
        write_status(paths.dir, STATUS_WLZ_OK)
        return True

    if not paths.tif.exists():
        report_error(
            paths.image_id,
            "TIF_MISSING",
            "Missing TIF file for WLZ conversion",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    if not _ensure_executable(wlz_ext):
        report_error(
            paths.image_id,
            "WLZ_CONVERTER_MISSING",
            f"WlzExtFFConvert missing: {wlz_ext}",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    if not _ensure_executable(wlz_threshold) or not _ensure_executable(wlz_set_voxel):
        report_error(
            paths.image_id,
            "WLZ_TOOL_MISSING",
            f"Woolz tool missing ({wlz_threshold} or {wlz_set_voxel})",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    # Step 1: convert TIF -> WLZ
    wlz_tmp = paths.dir / "_tmp.wlz"
    code, out, err = _run([wlz_ext, "-f", "tif", "-F", "wlz", "-o", str(wlz_tmp), str(paths.tif)])
    if code != 0 or not wlz_tmp.exists():
        report_error(
            paths.image_id,
            "WLZ_CONVERSION_FAILED",
            f"WlzExtFFConvert failed (code={code}) stdout={out!r} stderr={err!r}",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    # Step 2: threshold (output is written to stdout)
    wlz_th = paths.dir / "_th.wlz"
    code, out, err = _run([wlz_threshold, "-v2", "-H", str(wlz_tmp)])
    if code != 0:
        report_error(
            paths.image_id,
            "WLZ_THRESHOLD_FAILED",
            f"WlzThreshold failed (code={code}) stdout={out!r} stderr={err!r}",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    try:
        with open(wlz_th, "wb") as f:
            f.write(out.encode())
    except Exception as e:
        report_error(
            paths.image_id,
            "WLZ_THRESHOLD_FAILED",
            f"Failed to write threshold output: {e}",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    if not wlz_th.exists():
        report_error(
            paths.image_id,
            "WLZ_THRESHOLD_FAILED",
            "Threshold output missing",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    # Step 3: set voxel size
    voxel_sizes = _read_voxel_sizes_from_nrrd(paths.bounded_nrrd)
    if voxel_sizes is None:
        report_error(
            paths.image_id,
            "WLZ_VOXEL_SIZE_FAILED",
            "Unable to read voxel size from NRRD header",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    x, y, z = voxel_sizes
    x_arg = f"-x{float(x):.9f}"
    y_arg = f"-y{float(y):.9f}"
    z_arg = f"-z{float(z):.9f}"

    code, out, err = _run([wlz_set_voxel, x_arg, y_arg, z_arg, str(wlz_th)])
    if code != 0:
        report_error(
            paths.image_id,
            "WLZ_SETVOXEL_FAILED",
            f"WlzSetVoxelSize failed (code={code}) stdout={out!r} stderr={err!r}",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    # Step 4: set voxel size and write final WLZ to stdout
    final_wlz = paths.wlz
    code, out, err = _run([wlz_set_voxel, x_arg, y_arg, z_arg, str(wlz_th)])
    if code != 0:
        report_error(
            paths.image_id,
            "WLZ_SETVOXEL_FAILED",
            f"WlzSetVoxelSize failed (code={code}) stdout={out!r} stderr={err!r}",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    try:
        with open(final_wlz, "wb") as f:
            f.write(out.encode())
    except Exception as e:
        report_error(
            paths.image_id,
            "WLZ_FINALIZE_FAILED",
            f"Failed to write WLZ output: {e}",
            solr_url,
        )
        write_status(paths.dir, STATUS_WLZ_FAILED)
        return False

    _try_chmod(final_wlz)
    if cleanup_tif:
        try:
            paths.tif.unlink()
        except Exception:
            pass

    write_status(paths.dir, STATUS_WLZ_OK)
    return True


def generate_obj(
    paths: ConversionPaths,
    python_bin: str,
    maxproj_path: str,
    solr_url: Optional[str],
    dry_run: bool = False,
) -> bool:
    """Generate an OBJ from a NRRD using maxProjVol.py."""

    if paths.obj.exists() or paths.man_obj.exists():
        return True

    if dry_run:
        print(f"[DRY RUN] Would run maxProjVol to generate OBJ from {paths.nrrd}")
        write_status(paths.dir, STATUS_OBJ_OK)
        return True

    if not paths.nrrd.exists():
        report_error(
            paths.image_id,
            OBJ_GENERATION_FAILED,
            "Missing source NRRD for OBJ generation",
            solr_url,
        )
        write_status(paths.dir, STATUS_OBJ_FAILED)
        return False

    cmd = [python_bin, maxproj_path, str(paths.nrrd)]
    code, out, err = _run(cmd)
    if code != 0:
        report_error(
            paths.image_id,
            OBJ_GENERATION_FAILED,
            f"maxProjVol.py failed (code={code}) stdout={out!r} stderr={err!r}",
            solr_url,
        )
        write_status(paths.dir, STATUS_OBJ_FAILED)
        return False

    if not paths.obj.exists() and not paths.man_obj.exists():
        report_error(
            paths.image_id,
            OBJ_GENERATION_FAILED,
            "maxProjVol.py did not produce an OBJ file",
            solr_url,
        )
        write_status(paths.dir, STATUS_OBJ_FAILED)
        return False

    _try_chmod(paths.obj)
    write_status(paths.dir, STATUS_OBJ_OK)
    return True


def _check_tools(args: argparse.Namespace) -> bool:
    """Validate required external tools are available."""
    missing = []

    def require(path: str, desc: str):
        if not _ensure_executable(path):
            missing.append(f"{desc} not found or not executable: {path}")

    require(args.python, "Python")

    if not args.host_only:
        require(args.imagej, "ImageJ")
        require(args.wlz_ext, "Woolz converter")
        require(args.wlz_threshold, "Woolz threshold")
        require(args.wlz_setvoxel, "Woolz set voxel size")

    if missing:
        print("Tool check failed:")
        for m in missing:
            print("  ", m)
        return False

    return True


def run_full_pipeline(args: argparse.Namespace) -> int:
    if args.check_tools:
        return 0 if _check_tools(args) else 1

    # Stage 1: SWC --> NRRD (only for directories with SWC files)
    process_file_results = []
    swc_files = find_swc_files(args.base_path)
    for swc in swc_files:
        print(f"Processing SWC: {swc}")
        result = process_file(
            swc, solr_url=args.solr_url, redo=args.redo, dry_run=args.dry_run
        )
        process_file_results.append(result)

    if args.host_only:
        return 0

    # Stage 2..4: run conversions for all upload directories (SWC and NRRD uploads)
    all_dirs = find_upload_dirs(args.base_path)

    for d in all_dirs:
        paths = ConversionPaths(Path(d))
        id_tag = paths.image_id

        if args.skip_tif:
            print(f"Skipping TIF/WLZ for {id_tag}")
        else:
            if not convert_bounded_nrrd_to_tif(
                paths,
                args.imagej,
                args.imagej_macro,
                args.solr_url,
                dry_run=args.dry_run,
            ):
                continue
            if not convert_tif_to_wlz(
                paths,
                args.wlz_ext,
                args.wlz_threshold,
                args.wlz_setvoxel,
                args.solr_url,
                cleanup_tif=args.cleanup_tif,
                dry_run=args.dry_run,
            ):
                continue

        if not generate_obj(
            paths,
            args.python,
            args.maxproj,
            args.solr_url,
            dry_run=args.dry_run,
        ):
            continue

        # If we got here, we made it through all stages.
        write_status(d, STATUS_COMPLETE)
        report_success(id_tag, args.solr_url)

    return 0


def main():
    parser = argparse.ArgumentParser(description="Run the full NBLAST upload conversion pipeline")
    parser.add_argument("--base-path", default="/IMAGE_PRIVATE", help="Base path where VFBu_*/ directories live.")
    parser.add_argument("--solr-url", default=None, help="Solr URL for reporting status updates")
    parser.add_argument("--redo", action="store_true", help="Re-run SWC->NRRD conversion even if output exists")
    parser.add_argument("--skip-tif", action="store_true", help="Skip the bounded NRRD -> TIF/WLZ steps")
    parser.add_argument("--host-only", action="store_true", help="Only run host-side stages (SWC->NRRD); skip docker-dependent stages (TIF/WLZ/OBJ)")
    parser.add_argument("--imagej", default="ImageJ-linux64", help="ImageJ executable path")
    parser.add_argument("--imagej-macro", default="nrrd2tif.ijm", help="ImageJ macro file to run")
    parser.add_argument("--wlz-ext", default="/opt/MouseAtlas/bin/WlzExtFFConvert", help="Woolz converter executable")
    parser.add_argument("--wlz-threshold", default="/opt/MouseAtlas/bin/WlzThreshold", help="Woolz threshold executable")
    parser.add_argument("--wlz-setvoxel", default="/opt/MouseAtlas/bin/WlzSetVoxelSize", help="Woolz set voxel size executable")
    parser.add_argument("--maxproj", default="maxProjVol.py", help="maxProjVol.py script path")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable to run maxProjVol.py (defaults to current interpreter)",
    )
    parser.add_argument("--cleanup-tif", action="store_true", help="Remove intermediate TIF files after WLZ generation")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing conversions")
    parser.add_argument("--check-tools", action="store_true", help="Check that required external tools exist and are executable")
    args = parser.parse_args()
    return run_full_pipeline(args)


if __name__ == "__main__":
    raise SystemExit(main())
