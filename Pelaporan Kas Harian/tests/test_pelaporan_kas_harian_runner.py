import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import PelaporanKasHarian


class PelaporanKasHarianRunnerTests(unittest.TestCase):
    def test_creates_pdf_report_even_when_behave_fails(self):
        results = [
            {
                "name": "Pelaporan",
                "elements": [
                    {
                        "type": "scenario",
                        "name": "Mengirim laporan",
                        "status": "failed",
                        "steps": [
                            {
                                "keyword": "When ",
                                "name": "mengirim laporan",
                                "result": {
                                    "status": "failed",
                                    "duration": 0.2,
                                    "error_message": "Pengujian gagal",
                                },
                            }
                        ],
                    }
                ],
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            report_directory = Path(temp_dir) / "Reports"

            def run_behave(arguments, **_kwargs):
                output_argument = next(
                    argument
                    for argument in arguments
                    if argument.startswith("--outfile=")
                )
                output_path = Path(output_argument.split("=", 1)[1])
                output_path.write_text(json.dumps(results), encoding="utf-8")
                return SimpleNamespace(returncode=1)

            with (
                patch.object(
                    PelaporanKasHarian,
                    "REPORT_DIRECTORY",
                    report_directory,
                ),
                patch.object(
                    PelaporanKasHarian.subprocess,
                    "run",
                    side_effect=run_behave,
                ) as run,
            ):
                result = PelaporanKasHarian.main([])

            self.assertEqual(result, 1)
            run_arguments = run.call_args.args[0]
            self.assertIn("--format=json", run_arguments)
            self.assertIn("--format=pretty", run_arguments)
            self.assertTrue(
                any(argument.startswith("--outfile=") for argument in run_arguments)
            )
            reports = list(report_directory.glob("pelaporan-kas-harian-*.pdf"))
            self.assertEqual(len(reports), 1)
            self.assertTrue(reports[0].read_bytes().startswith(b"%PDF"))

    def test_fails_explicitly_when_behave_does_not_write_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch.object(
                    PelaporanKasHarian,
                    "REPORT_DIRECTORY",
                    Path(temp_dir) / "Reports",
                ),
                patch.object(
                    PelaporanKasHarian.subprocess,
                    "run",
                    return_value=SimpleNamespace(returncode=1),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "tidak menghasilkan data JSON"):
                    PelaporanKasHarian.main([])


if __name__ == "__main__":
    unittest.main()
