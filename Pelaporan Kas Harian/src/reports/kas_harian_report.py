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
            if element.get("type") != "scenario":
                continue
            tags = set(feature.get("tags", [])) | set(element.get("tags", []))
            role = (
                "Pemimpin Cabang"
                if "persetujuan_kas_harian" in tags
                else "Kasir"
            )
            scenarios.append(
                {
                    "feature": feature.get("name", ""),
                    "name": element.get("name", ""),
                    "status": element.get("status", "untested"),
                    "role": role,
                    "steps": element.get("steps", []),
                }
            )
    return scenarios


def _status_counts(scenarios):
    passed = sum(scenario["status"] == "passed" for scenario in scenarios)
    failed = sum(
        scenario["status"] in {"failed", "error"} for scenario in scenarios
    )
    skipped = sum(
        scenario["status"] in {"skipped", "untested"} for scenario in scenarios
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


def _draw_page(canvas, document, run_id):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(GREEN)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(
        document.leftMargin, height - 12 * mm, "QUALITY / AUTOMATION"
    )
    canvas.setStrokeColor(GRID)
    canvas.line(
        document.leftMargin,
        height - 15 * mm,
        width - document.rightMargin,
        height - 15 * mm,
    )
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(document.leftMargin, 10 * mm, f"Run {run_id}")
    canvas.drawRightString(
        width - document.rightMargin, 10 * mm, f"Page {document.page}"
    )
    canvas.restoreState()


def create_pdf_report(results, run_id, started_at, duration_seconds, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scenarios = _scenarios(results)
    passed, failed, skipped = _status_counts(scenarios)
    total = len(scenarios)
    pass_rate = (passed / total * 100) if total else 0
    outcome = _outcome(passed, failed, skipped)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="KasReportTitle",
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
            name="KasReportSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            textColor=MUTED,
            spaceAfter=5 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasSectionTitle",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=GREEN,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasSmallCell",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasSmallCellBold",
            parent=styles["KasSmallCell"],
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasTableHeader",
            parent=styles["KasSmallCellBold"],
            textColor=colors.white,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasErrorText",
            parent=styles["KasSmallCell"],
            textColor=FAILED,
            leftIndent=4 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasMetricLabel",
            parent=styles["Normal"],
            fontSize=7,
            textColor=MUTED,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasMetricValue",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=20,
            textColor=GREEN,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KasRightSmall",
            parent=styles["KasSmallCell"],
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
        title=f"Pelaporan Kas Harian - {run_id}",
        author="Automation Keila",
    )
    story = [
        _paragraph("Pelaporan Kas Harian", styles["KasReportTitle"]),
        _paragraph(
            "TEST EXECUTION REPORT - Selenium + Python + Behave",
            styles["KasReportSubtitle"],
        ),
    ]

    metadata = [
        [
            _paragraph("Run ID", styles["KasSmallCell"]),
            _paragraph(run_id, styles["KasSmallCellBold"]),
            _paragraph("Outcome", styles["KasSmallCell"]),
            _paragraph(outcome, styles["KasSmallCellBold"]),
        ],
        [
            _paragraph("Started", styles["KasSmallCell"]),
            _paragraph(
                started_at.strftime("%d %B %Y %H:%M:%S"),
                styles["KasSmallCell"],
            ),
            _paragraph("Duration", styles["KasSmallCell"]),
            _paragraph(
                f"{duration_seconds:.3f} seconds", styles["KasSmallCell"]
            ),
        ],
        [
            _paragraph("Environment", styles["KasSmallCell"]),
            _paragraph("dev", styles["KasSmallCell"]),
            _paragraph("Browser", styles["KasSmallCell"]),
            _paragraph("Chrome", styles["KasSmallCell"]),
        ],
        [
            _paragraph("Roles", styles["KasSmallCell"]),
            _paragraph("Kasir, Pemimpin Cabang", styles["KasSmallCell"]),
            _paragraph("Feature", styles["KasSmallCell"]),
            _paragraph(
                scenarios[0]["feature"] if scenarios else "-",
                styles["KasSmallCell"],
            ),
        ],
    ]
    metadata_table = Table(
        metadata,
        colWidths=[20 * mm, 65 * mm, 20 * mm, 67 * mm],
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
    metric_cells = [
        [
            _paragraph(label, styles["KasMetricLabel"]),
            _paragraph(value, styles["KasMetricValue"]),
        ]
        for label, value in metrics
    ]
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
            _paragraph("Results distribution", styles["KasSectionTitle"]),
            _paragraph(
                f"Passed: {passed} - Failed: {failed} - "
                f"Skipped / untested: {skipped}",
                styles["KasSmallCell"],
            ),
        ]
    )

    previous_feature = None
    for index, scenario in enumerate(scenarios, start=1):
        scenario_passed = scenario["status"] == "passed"
        status = "PASSED" if scenario_passed else scenario["status"].upper()
        status_color = PASSED if scenario_passed else FAILED
        if scenario["feature"] != previous_feature:
            story.append(
                _paragraph(scenario["feature"], styles["KasSectionTitle"])
            )
            previous_feature = scenario["feature"]

        title_table = Table(
            [[
                _paragraph(scenario["name"], styles["KasSmallCellBold"]),
                _paragraph(scenario["role"], styles["KasRightSmall"]),
                Paragraph(
                    status,
                    ParagraphStyle(
                        name=f"KasScenarioStatus{index}",
                        parent=styles["KasSmallCellBold"],
                        alignment=TA_RIGHT,
                        textColor=status_color,
                    ),
                ),
            ]],
            colWidths=[112 * mm, 35 * mm, 25 * mm],
        )
        title_table.setStyle(
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
        story.extend([title_table, Spacer(1, 1.5 * mm)])

        rows = [[
            _paragraph("Step", styles["KasTableHeader"]),
            _paragraph("Result", styles["KasTableHeader"]),
            _paragraph("Time", styles["KasTableHeader"]),
        ]]
        for step in scenario["steps"]:
            result = step.get("result", {})
            step_status = result.get("status", "untested")
            step_color = PASSED if step_status == "passed" else FAILED
            rows.append(
                [
                    _paragraph(
                        f"{step.get('keyword', '')} {step.get('name', '')}",
                        styles["KasSmallCell"],
                    ),
                    Paragraph(
                        step_status.upper(),
                        ParagraphStyle(
                            name=f"KasStepStatus{len(rows)}",
                            parent=styles["KasSmallCellBold"],
                            textColor=step_color,
                        ),
                    ),
                    _paragraph(
                        f"{result.get('duration', 0):.3f} s",
                        styles["KasRightSmall"],
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
                        styles["KasErrorText"],
                    )
                )
                story.append(Spacer(1, 2 * mm))

    document.build(
        story,
        onFirstPage=lambda canvas, doc: _draw_page(canvas, doc, run_id),
        onLaterPages=lambda canvas, doc: _draw_page(canvas, doc, run_id),
    )
