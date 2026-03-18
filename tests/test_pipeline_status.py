import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from nblast_pipeline import pipeline_status


class TestPipelineStatus(unittest.TestCase):
    def test_write_and_read_status(self):
        with tempfile.TemporaryDirectory() as d:
            pipeline_status.write_status(d, "NRRD_OK")
            status = pipeline_status.read_status(d)
            self.assertEqual(status, "NRRD_OK")

    @patch("nblast_pipeline.pipeline_status.pysolr.Solr")
    def test_report_error_calls_solr_with_atomic_update(self, mock_solr_cls):
        mock_solr = MagicMock()
        mock_solr_cls.return_value = mock_solr

        ok = pipeline_status.report_error("VFBu_123", "TEST_ERROR", "details")
        self.assertTrue(ok)
        mock_solr.add.assert_called_once()
        args, kwargs = mock_solr.add.call_args
        self.assertIn("commit", kwargs)
        self.assertTrue(kwargs["commit"])
        doc = args[0][0]
        self.assertEqual(doc["id"], "VFBu_123")
        self.assertEqual(doc["description"], {"set": "TEST_ERROR: details"})

    @patch("nblast_pipeline.pipeline_status.pysolr.Solr")
    def test_report_error_handles_exceptions(self, mock_solr_cls):
        mock_solr = MagicMock()
        mock_solr.add.side_effect = Exception("boom")
        mock_solr_cls.return_value = mock_solr

        ok = pipeline_status.report_error("VFBu_123", "TEST_ERROR", "details")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
