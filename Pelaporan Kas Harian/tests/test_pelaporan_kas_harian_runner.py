import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import PelaporanKasHarian


class PelaporanKasHarianRunnerTests(unittest.TestCase):
    @patch("PelaporanKasHarian.subprocess.run")
    def test_creates_pdf_and_defaults_to_reporting_scenario(self, run):
        behave_results = [
            {
                "name": "Pelaporan dan Persetujuan Harian Kas Dan Bank PUMK",
                "elements": [],
            }
        ]

        def write_behave_results(command, **kwargs):
            output_argument = next(
                argument
                for argument in command
                if argument.startswith("--outfile=")
            )
            Path(output_argument.partition("=")[2]).write_text(
                json.dumps(behave_results),
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=0)

        run.side_effect = write_behave_results
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                PelaporanKasHarian, "REPORT_DIRECTORY", Path(temp_dir)
            ):
                result = PelaporanKasHarian.main([])

            self.assertEqual(result, 0)
            command = run.call_args.args[0]
            self.assertIn("--format=json", command)
            self.assertIn("--tags=@pelaporan_kas_harian", command)
            reports = list(Path(temp_dir).glob("pelaporan-kas-harian-*.pdf"))
            self.assertEqual(len(reports), 1)
            self.assertTrue(reports[0].read_bytes().startswith(b"%PDF-"))

    @patch("PelaporanKasHarian.subprocess.run")
    def test_creates_pdf_when_behave_reports_failure(self, run):
        failed_results = [
            {
                "name": "Pelaporan dan Persetujuan Harian Kas Dan Bank PUMK",
                "elements": [
                    {
                        "type": "scenario",
                        "name": "Approval failed",
                        "tags": ["persetujuan_kas_harian"],
                        "status": "failed",
                        "steps": [
                            {
                                "keyword": "Then ",
                                "name": "approval step",
                                "result": {
                                    "status": "failed",
                                    "duration": 1.0,
                                    "error_message": "Example failure",
                                },
                            }
                        ],
                    }
                ],
            }
        ]

        def write_failed_results(command, **kwargs):
            output_argument = next(
                argument
                for argument in command
                if argument.startswith("--outfile=")
            )
            Path(output_argument.partition("=")[2]).write_text(
                json.dumps(failed_results),
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=1)

        run.side_effect = write_failed_results
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                PelaporanKasHarian, "REPORT_DIRECTORY", Path(temp_dir)
            ):
                result = PelaporanKasHarian.main(
                    ["custom.feature", "--tags=@persetujuan_kas_harian"]
                )

            self.assertEqual(result, 1)
            reports = list(Path(temp_dir).glob("pelaporan-kas-harian-*.pdf"))
            self.assertEqual(len(reports), 1)
            self.assertTrue(reports[0].read_bytes().startswith(b"%PDF-"))

    @patch("PelaporanKasHarian.subprocess.run")
    def test_respects_explicit_feature_and_tag_arguments(self, run):
        with tempfile.TemporaryDirectory() as temp_dir:
            def write_behave_results(command, **kwargs):
                output_argument = next(
                    argument
                    for argument in command
                    if argument.startswith("--outfile=")
                )
                Path(output_argument.partition("=")[2]).write_text(
                    "[]",
                    encoding="utf-8",
                )
                return SimpleNamespace(returncode=0)

            run.side_effect = write_behave_results
            with patch.object(
                PelaporanKasHarian, "REPORT_DIRECTORY", Path(temp_dir) / "Reports"
            ):
                feature = "custom.feature"
                result = PelaporanKasHarian.main(
                    [feature, "--tags=@persetujuan_kas_harian"]
                )

            self.assertEqual(result, 0)
            command = run.call_args.args[0]
            self.assertIn(feature, command)
            self.assertIn("--tags=@persetujuan_kas_harian", command)
            self.assertNotIn("--tags=@pelaporan_kas_harian", command)


if __name__ == "__main__":
    unittest.main()
