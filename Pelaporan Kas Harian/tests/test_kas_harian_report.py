import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.reports.kas_harian_report import create_pdf_report


class KasHarianReportTests(unittest.TestCase):
    def test_creates_pdf_report_with_scenario_results(self):
        results = [
            {
                "name": "Pelaporan dan Persetujuan Harian Kas Dan Bank PUMK",
                "elements": [
                    {
                        "type": "scenario",
                        "name": "Mengirim laporan kas dan bank PUMK",
                        "tags": ["pelaporan_kas_harian"],
                        "status": "passed",
                        "steps": [
                            {
                                "keyword": "Then ",
                                "name": "laporan diproses",
                                "result": {
                                    "status": "passed",
                                    "duration": 1.25,
                                },
                            }
                        ],
                    }
                ],
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "Reports" / "kas-harian.pdf"
            create_pdf_report(
                results=results,
                run_id="20261119-test",
                started_at=datetime(2026, 11, 19, 1, 0, 0),
                duration_seconds=2.5,
                output_path=output_path,
            )

            self.assertTrue(output_path.is_file())
            self.assertTrue(output_path.read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
