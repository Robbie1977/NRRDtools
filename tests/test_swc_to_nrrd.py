import os
import tempfile
import unittest

import numpy as np
import nrrd

from swc_to_nrrd import convert_swc_to_nrrd_with_status
from nblast_pipeline import pipeline_status


def _write_template_nrrd(path, shape=(20, 20, 20)):
    data = np.zeros(shape, dtype=np.uint8)
    # Create a simple header with isotropic 1 micron voxels
    header = {
        "type": "uint8",
        "dimension": 3,
        "sizes": list(shape),
        "space": "left-posterior-superior",
        "space directions": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "space origin": [0.0, 0.0, 0.0],
        "encoding": "raw",
    }
    nrrd.write(path, data, header=header)


class TestSwcToNrrd(unittest.TestCase):
    def test_bad_swc_parsing_returns_parse_error(self):
        with tempfile.TemporaryDirectory() as d:
            template = os.path.join(d, "template.nrrd")
            _write_template_nrrd(template)

            swc_path = os.path.join(d, "bad.swc")
            with open(swc_path, "w", encoding="utf-8") as f:
                f.write("this is not a valid swc\n")

            result = convert_swc_to_nrrd_with_status(swc_path, template, os.path.join(d, "out.nrrd"))
            self.assertFalse(result["success"])
            self.assertEqual(result["error_category"], pipeline_status.SWC_PARSE_ERROR)

    def test_out_of_bounds_swc_returns_out_of_bounds_error(self):
        with tempfile.TemporaryDirectory() as d:
            template = os.path.join(d, "template.nrrd")
            _write_template_nrrd(template)

            swc_path = os.path.join(d, "oob.swc")
            # This SWC node is far outside the 20x20x20 volume.
            with open(swc_path, "w", encoding="utf-8") as f:
                f.write("1 1 1000 1000 1000 1 -1\n")

            result = convert_swc_to_nrrd_with_status(swc_path, template, os.path.join(d, "out.nrrd"))
            self.assertFalse(result["success"])
            self.assertEqual(result["error_category"], pipeline_status.SWC_OUT_OF_BOUNDS)

    def test_valid_swc_produces_nonzero_voxelization(self):
        with tempfile.TemporaryDirectory() as d:
            template = os.path.join(d, "template.nrrd")
            _write_template_nrrd(template)

            swc_path = os.path.join(d, "good.swc")
            # Simple two-node tree inside the volume
            with open(swc_path, "w", encoding="utf-8") as f:
                f.write("1 1 5 5 5 1 -1\n")
                f.write("2 1 6 5 5 1 1\n")

            out_nrrd = os.path.join(d, "out.nrrd")
            result = convert_swc_to_nrrd_with_status(swc_path, template, out_nrrd)
            self.assertTrue(result["success"])
            self.assertGreater(result["voxel_count"], 0)
            self.assertTrue(os.path.exists(out_nrrd))


if __name__ == "__main__":
    unittest.main()
