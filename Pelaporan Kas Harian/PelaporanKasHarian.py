import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_FEATURE = (
    "features/pelaporan_kas_harian/workflow_pelaporan_kas_harian_lengkap.feature"
)


def _has_feature_path(arguments):
    return any(
        argument.endswith(".feature")
        or argument.startswith("features/")
        or argument.startswith("@features")
        for argument in arguments
    )


def main(arguments):
    behave_arguments = [sys.executable, "-m", "behave"]
    if not _has_feature_path(arguments):
        behave_arguments.append(DEFAULT_FEATURE)
    behave_arguments.extend(arguments)
    result = subprocess.run(behave_arguments, cwd=PROJECT_ROOT, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
