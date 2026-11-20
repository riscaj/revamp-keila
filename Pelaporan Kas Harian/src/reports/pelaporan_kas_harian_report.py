from datetime import datetime
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.pages.transactions.pelaporan_kas_harian.pelaporan_kas_harian_locators import (
    LOGIN_URL,
)


GREEN = colors.HexColor("#00594C")
LIGHT_GREEN = colors.HexColor("#F0F7F4")
GRID = colors.HexColor("#D8E5E0")
TEXT = colors.HexColor("#25443D")
PASSED = colors.HexColor("#16804A")
FAILED = colors.HexColor("#B42318")
MUTED = colors.HexColor("#667A74")


def _paragraph(text, style):
    safe_text = re.sub(
        r"\b\d{10,}\b",
        lambda match: f"{'*' * (len(match.group()) - 4)}{match.group()[-4:]}",
        str(text),
    )
    return Paragraph(escape(safe_text).replace("\n", "<br/>"), style)


def _scenarios(results):
    scenarios = []
    for feature in results:
        for element in feature.get("elements", []):
            if element.get("type") == "scenario":
                scenarios.append(
                    {
                        "feature": feature.get("name", ""),
                        "name": element.get("name", ""),
                        "status": element.get("status", "untested"),
                        "steps": element.get("steps", []),
                    }
                )
    return scenarios


def _status_color(status):
    if status == "passed":
        return PASSED
    if status in {"failed", "error"}:
        return FAILED
    return MUTED


def create_pdf_report(
    results,
    run_id,
    started_at,
    duration_seconds,
    output_path,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scenarios = _scenarios(results)
    passed = sum(scenario["status"] == "passed" for scenario in scenarios)
    failed = sum(
        scenario["status"] in {"failed", "error"} for scenario in scenarios
    )
    skipped = len(scenarios) - passed - failed

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=GREEN,
            alignment=0,
            spaceAfter=2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            textColor=MUTED,
            spaceAfter=5 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=GREEN,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportCell",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportCellBold",
            parent=styles["ReportCell"],
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportCellRight",
            parent=styles["ReportCell"],
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportError",
            parent=styles["ReportCell"],
            textColor=FAILED,
        )
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Pelaporan Harian Kas Dan Bank PUMK - {run_id}",
        author="Automation Keila",
    )
    story = [
        _paragraph(
            "Pelaporan Harian Kas Dan Bank PUMK",
            styles["ReportTitle"],
        ),
        _paragraph(
            "TEST EXECUTION REPORT - Selenium + Python + Behave",
            styles["ReportSubtitle"],
        ),
    ]

    metadata = [
        [
            _paragraph("Run ID", styles["ReportCell"]),
            _paragraph(run_id, styles["ReportCellBold"]),
            _paragraph("Started", styles["ReportCell"]),
            _paragraph(
                started_at.strftime("%d %B %Y %H:%M:%S %Z"),
                styles["ReportCellBold"],
            ),
        ],
        [
            _paragraph("Duration", styles["ReportCell"]),
            _paragraph(
                f"{duration_seconds:.3f} seconds",
                styles["ReportCellBold"],
            ),
            _paragraph("Target", styles["ReportCell"]),
            _paragraph(LOGIN_URL, styles["ReportCell"]),
        ],
    ]
    metadata_table = Table(
        metadata,
        colWidths=[19 * mm, 65 * mm, 19 * mm, 69 * mm],
    )
    metadata_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREEN),
                ("BACKGROUND", (2, 0), (2, -1), LIGHT_GREEN),
                ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([metadata_table, Spacer(1, 5 * mm)])

    summary = Table(
        [[
            _paragraph(f"SCENARIOS: {len(scenarios)}", styles["ReportCellBold"]),
            _paragraph(f"PASSED: {passed}", styles["ReportCellBold"]),
            _paragraph(f"FAILED: {failed}", styles["ReportCellBold"]),
            _paragraph(f"SKIPPED / UNTESTED: {skipped}", styles["ReportCellBold"]),
        ]],
        colWidths=[40 * mm, 35 * mm, 35 * mm, 62 * mm],
    )
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
                ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            summary,
            _paragraph("Scenario details", styles["SectionTitle"]),
        ]
    )

    for scenario in scenarios:
        status_style = ParagraphStyle(
            name=f"ScenarioStatus{len(story)}",
            parent=styles["ReportCellBold"],
            textColor=_status_color(scenario["status"]),
            alignment=TA_RIGHT,
        )
        scenario_title = Table(
            [[
                _paragraph(
                    f"{scenario['feature']} - {scenario['name']}",
                    styles["ReportCellBold"],
                ),
                Paragraph(scenario["status"].upper(), status_style),
            ]],
            colWidths=[145 * mm, 27 * mm],
        )
        scenario_title.setStyle(
            TableStyle(
                [
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, GRID),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(scenario_title)
        step_rows = [
            [
                _paragraph("Step", styles["ReportCellBold"]),
                _paragraph("Status", styles["ReportCellBold"]),
                _paragraph("Duration", styles["ReportCellBold"]),
            ]
        ]
        for step in scenario["steps"]:
            result = step.get("result", {})
            step_status = result.get("status", "untested")
            step_style = ParagraphStyle(
                name=f"StepStatus{len(step_rows)}",
                parent=styles["ReportCellBold"],
                textColor=_status_color(step_status),
            )
            step_rows.append(
                [
                    _paragraph(
                        f"{step.get('keyword', '')} {step.get('name', '')}",
                        styles["ReportCell"],
                    ),
                    Paragraph(step_status.upper(), step_style),
                    _paragraph(
                        f"{result.get('duration', 0):.3f} s",
                        styles["ReportCellRight"],
                    ),
                ]
            )
        step_table = Table(
            step_rows,
            colWidths=[128 * mm, 30 * mm, 14 * mm],
            repeatRows=1,
        )
        step_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GREEN),
                    ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.extend([step_table, Spacer(1, 3 * mm)])

        error_messages = [
            step.get("result", {}).get("error_message")
            for step in scenario["steps"]
            if step.get("result", {}).get("error_message")
        ]
        for message in error_messages:
            story.append(_paragraph(message, styles["ReportError"]))
            story.append(Spacer(1, 2 * mm))

    document.build(story)
