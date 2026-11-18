import unittest
from types import SimpleNamespace
from unittest.mock import patch

import PersetujuanKasHarian


class PersetujuanKasHarianRunnerTests(unittest.TestCase):
    @patch("PersetujuanKasHarian.subprocess.run")
    def test_runs_approval_scenario_through_reporting_runner(self, run):
        run.return_value = SimpleNamespace(returncode=0)

        result = PersetujuanKasHarian.main(["--dry-run"])

        self.assertEqual(result, 0)
        run.assert_called_once_with(
            [
                PersetujuanKasHarian.sys.executable,
                str(PersetujuanKasHarian.REPORT_SCRIPT),
                str(PersetujuanKasHarian.COMBINED_FEATURE),
                "--tags=@persetujuan_kas_harian",
                "--dry-run",
            ],
            cwd=PersetujuanKasHarian.PROJECT_ROOT,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
