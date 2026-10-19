import json
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

from src.reports.monitoring_report import create_pdf_report


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_FEATURE = "features/monitoring/workflow_monitoring.feature"
REPORT_DIRECTORY = PROJECT_ROOT / "Reports"


def _has_feature_path(arguments):
    return any(
        argument.endswith(".feature")
        or argument.startswith("features/")
        or argument.startswith("@features")
        for argument in arguments
    )


def main(arguments):
    run_started = datetime.now().astimezone()
    started_at = time.monotonic()
    run_id = f"{run_started:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"
    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIRECTORY / f"monitoring-{run_id}.pdf"

    with tempfile.TemporaryDirectory(prefix="monitoring-report-") as temp_dir:
        json_path = Path(temp_dir) / "behave-results.json"
        behave_arguments = [
            sys.executable,
            "-m",
            "behave",
            "--format=json",
            f"--outfile={json_path}",
        ]
        if not _has_feature_path(arguments):
            behave_arguments.append(DEFAULT_FEATURE)
        behave_arguments.extend(arguments)

        result = subprocess.run(
            behave_arguments,
            cwd=PROJECT_ROOT,
            check=False,
        )
        duration = time.monotonic() - started_at
        if not json_path.is_file():
            raise RuntimeError(
                "Behave tidak menghasilkan data JSON; laporan PDF tidak dapat dibuat."
            )

        with json_path.open(encoding="utf-8") as results_file:
            results = json.load(results_file)

        create_pdf_report(
            results=results,
            run_id=run_id,
            started_at=run_started,
            duration_seconds=duration,
            output_path=report_path,
        )

    print(f"\nLaporan PDF: {report_path}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
