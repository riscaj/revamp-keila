from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
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

from src.pages.transactions.monitoring.monitoring_locators import (
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


def _scenario_data(results):
    scenarios = []
    for feature in results:
        feature_tags = set(feature.get("tags", []))
        for element in feature.get("elements", []):
            if element.get("type") != "scenario":
                continue
            tags = feature_tags | set(element.get("tags", []))
            scenarios.append(
                {
                    "feature": feature.get("name", ""),
                    "name": element.get("name", ""),
                    "status": element.get("status", "untested"),
                    "role": next(
                        (
                            tag.upper()
                            for tag in ("ao", "mbi", "ksr")
                            if tag in tags
                        ),
                        "AO",
                    ),
                    "steps": element.get("steps", []),
                }
            )
    return scenarios


def _status_counts(scenarios):
    passed = sum(scenario["status"] == "passed" for scenario in scenarios)
    failed = sum(
        scenario["status"] in {"failed", "error"}
        for scenario in scenarios
    )
    skipped = sum(
        scenario["status"] in {"skipped", "untested"}
        for scenario in scenarios
    )
    return passed, failed, skipped


def _outcome(passed, failed, skipped):
    if failed:
        return "FAILED"
    if skipped:
        return "REVIEW REQUIRED"
    if passed:
        return "PASSED"
    return "NO SCENARIOS"


def _format_duration(seconds):
    return f"{seconds:.3f} seconds"


def _draw_page(canvas, document, run_id):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(GREEN)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(document.leftMargin, height - 12 * mm, "QUALITY / AUTOMATION")
    canvas.setStrokeColor(GRID)
    canvas.line(
        document.leftMargin,
        height - 15 * mm,
        width - document.rightMargin,
        height - 15 * mm,
    )
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(
        document.leftMargin,
        10 * mm,
        f"Run {run_id}",
    )
    canvas.drawRightString(
        width - document.rightMargin,
        10 * mm,
        f"Page {document.page}",
    )
    canvas.restoreState()


def create_pdf_report(
    results,
    run_id,
    started_at,
    duration_seconds,
    output_path,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scenarios = _scenario_data(results)
    passed, failed, skipped = _status_counts(scenarios)
    total = len(scenarios)
    pass_rate = (passed / total * 100) if total else 0
    outcome = _outcome(passed, failed, skipped)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=GREEN,
            alignment=TA_LEFT,
            spaceAfter=2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
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
            fontSize=13,
            leading=16,
            textColor=GREEN,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCellBold",
            parent=styles["SmallCell"],
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["SmallCellBold"],
            textColor=colors.white,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ErrorText",
            parent=styles["SmallCell"],
            textColor=FAILED,
            leftIndent=4 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetricLabel",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            textColor=MUTED,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetricValue",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=20,
            textColor=GREEN,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RightSmall",
            parent=styles["SmallCell"],
            alignment=TA_RIGHT,
        )
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=22 * mm,
        bottomMargin=17 * mm,
        title=f"Automation Keila - {run_id}",
        author="Automation Keila",
    )
    story = [
        _paragraph("Automation Keila", styles["ReportTitle"]),
        _paragraph(
            "TEST EXECUTION REPORT - Selenium + Python + Behave",
            styles["ReportSubtitle"],
        ),
    ]

    metadata = [
        [
            _paragraph("Run ID", styles["SmallCell"]),
            _paragraph(run_id, styles["SmallCellBold"]),
            _paragraph("Outcome", styles["SmallCell"]),
            _paragraph(outcome, styles["SmallCellBold"]),
        ],
        [
            _paragraph("Started", styles["SmallCell"]),
            _paragraph(started_at.strftime("%d %B %Y"), styles["SmallCell"]),
            _paragraph("Duration", styles["SmallCell"]),
            _paragraph(_format_duration(duration_seconds), styles["SmallCell"]),
        ],
        [
            _paragraph("Environment", styles["SmallCell"]),
            _paragraph("dev", styles["SmallCell"]),
            _paragraph("Browser", styles["SmallCell"]),
            _paragraph("Chrome", styles["SmallCell"]),
        ],
        [
            _paragraph("Target", styles["SmallCell"]),
            _paragraph(LOGIN_URL, styles["SmallCell"]),
            _paragraph("Roles", styles["SmallCell"]),
            _paragraph("AO", styles["SmallCell"]),
        ],
    ]
    metadata_table = Table(
        metadata,
        colWidths=[18 * mm, 67 * mm, 20 * mm, 67 * mm],
        repeatRows=0,
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

    metrics = [
        ("TOTAL SCENARIOS", str(total)),
        ("PASSED", str(passed)),
        ("FAILED", str(failed)),
        ("SKIPPED / UNTESTED", str(skipped)),
        ("PASS RATE", f"{pass_rate:.1f}%"),
    ]
    metric_cells = []
    for label, value in metrics:
        metric_cells.append(
            [
                _paragraph(label, styles["MetricLabel"]),
                _paragraph(value, styles["MetricValue"]),
            ]
        )
    metric_table = Table(
        [metric_cells],
        colWidths=[34 * mm, 30 * mm, 30 * mm, 39 * mm, 39 * mm],
    )
    metric_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
                ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend(
        [
            metric_table,
            _paragraph("Results distribution", styles["SectionTitle"]),
            _paragraph(
                f"Passed: {passed} - Failed: {failed} - Skipped / untested: {skipped}",
                styles["SmallCell"],
            ),
        ]
    )

    previous_feature = None
    for index, scenario in enumerate(scenarios, start=1):
        scenario_passed = scenario["status"] == "passed"
        status = scenario["status"].upper()
        status_color = (
            PASSED
            if scenario_passed
            else MUTED
            if scenario["status"] in {"skipped", "untested"}
            else FAILED
        )
        if scenario["feature"] != previous_feature:
            story.append(
                _paragraph(scenario["feature"], styles["SectionTitle"])
            )
            previous_feature = scenario["feature"]
        title_row = Table(
            [
                [
                    _paragraph(scenario["name"], styles["SmallCellBold"]),
                    Paragraph(
                        status,
                        ParagraphStyle(
                            name=f"ScenarioStatus{index}",
                            parent=styles["SmallCellBold"],
                            alignment=TA_RIGHT,
                            textColor=status_color,
                        ),
                    ),
                ]
            ],
            colWidths=[145 * mm, 27 * mm],
        )
        title_row.setStyle(
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
        story.extend(
            [
                title_row,
                Spacer(1, 1.5 * mm),
            ]
        )

        rows = [
            [
                _paragraph("Step", styles["TableHeader"]),
                _paragraph("Result", styles["TableHeader"]),
                _paragraph("Time", styles["TableHeader"]),
            ]
        ]
        for step in scenario["steps"]:
            result = step.get("result", {})
            step_status = result.get(
                "status", step.get("status", "untested")
            ).upper()
            step_status_color = (
                PASSED
                if step_status == "PASSED"
                else MUTED
                if step_status in {"SKIPPED", "UNTESTED"}
                else FAILED
            )
            rows.append(
                [
                    _paragraph(
                        f"{step.get('keyword', '')} {step.get('name', '')}",
                        styles["SmallCell"],
                    ),
                    Paragraph(
                        step_status,
                        ParagraphStyle(
                            name=f"StepStatus{len(rows)}",
                            parent=styles["SmallCellBold"],
                            textColor=step_status_color,
                        ),
                    ),
                    _paragraph(
                        f"{result.get('duration', 0):.3f} s",
                        styles["RightSmall"],
                    ),
                ]
            )
        step_table = Table(
            rows,
            colWidths=[128 * mm, 27 * mm, 17 * mm],
            repeatRows=1,
        )
        step_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREEN]),
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

        for step in scenario["steps"]:
            error_message = step.get("result", {}).get("error_message")
            if error_message:
                story.append(
                    _paragraph(
                        f"Error in {step.get('name', 'step')}: {error_message}",
                        styles["ErrorText"],
                    )
                )
                story.append(Spacer(1, 2 * mm))

    document.build(
        story,
        onFirstPage=lambda canvas, doc: _draw_page(canvas, doc, run_id),
        onLaterPages=lambda canvas, doc: _draw_page(canvas, doc, run_id),
    )
