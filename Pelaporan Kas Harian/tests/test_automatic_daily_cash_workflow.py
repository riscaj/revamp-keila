import unittest
from types import SimpleNamespace
from unittest.mock import patch

import FlowPelaporanKasHarian


class CombinedDailyCashWorkflowTests(unittest.TestCase):
    @patch("FlowPelaporanKasHarian.subprocess.run")
    def test_runs_combined_feature_once_and_stops_after_failure(self, run):
        run.return_value = SimpleNamespace(returncode=1)

        result = FlowPelaporanKasHarian.main()

        self.assertEqual(result, 1)
        run.assert_called_once_with(
            [
                FlowPelaporanKasHarian.sys.executable,
                str(FlowPelaporanKasHarian.REPORT_SCRIPT),
                str(FlowPelaporanKasHarian.COMBINED_FEATURE),
                "--stop",
            ],
            cwd=FlowPelaporanKasHarian.PROJECT_ROOT,
            check=False,
        )

    @patch("FlowPelaporanKasHarian.subprocess.run")
    def test_returns_behave_success_code(self, run):
        run.return_value = SimpleNamespace(returncode=0)

        self.assertEqual(FlowPelaporanKasHarian.main(), 0)


if __name__ == "__main__":
    unittest.main()
