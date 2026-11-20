import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
REPORT_SCRIPT = PROJECT_ROOT / "PelaporanKasHarian.py"
WORKFLOW_FEATURE = (
    PROJECT_ROOT
    / "features"
    / "pelaporan_kas_harian"
    / "workflow_pelaporan_kas_harian_lengkap.feature"
)


def main():
    report_result = subprocess.run(
        [
            sys.executable,
            str(REPORT_SCRIPT),
            str(WORKFLOW_FEATURE),
            "--stop",
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return report_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
