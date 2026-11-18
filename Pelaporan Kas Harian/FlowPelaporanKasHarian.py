import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
REPORT_SCRIPT = PROJECT_ROOT / "PelaporanKasHarian.py"
COMBINED_FEATURE = (
    PROJECT_ROOT
    / "features"
    / "pelaporan_kas_harian"
    / "workflow_pelaporan_kas_harian_lengkap.feature"
)


def main():
    result = subprocess.run(
        [
            sys.executable,
            str(REPORT_SCRIPT),
            str(COMBINED_FEATURE),
            "--stop",
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
