"""
PDF Report Generator for SEO Audit Reports
"""

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from io import BytesIO

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from datetime import datetime


def generate_seo_report_pdf(report):
    """Generate comprehensive SEO report PDF"""

    if not PDF_AVAILABLE:
        raise ImportError("PDF generation requires reportlab package")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch
    )

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f2937"),
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor("#374151"),
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=6,
        textColor=colors.HexColor("#4b5563"),
    )

    # Build document content
    content = []
    audit_data = report.audit_data

    # Title Page
    content.append(Paragraph("SEO Audit Report", title_style))
    content.append(Spacer(1, 0.3 * inch))

    # Report Overview
    overview_data = [
        ["Website", report.website_url],
        ["Domain", report.domain],
        ["Overall Score", f"{report.overall_score}/100 ({report.score_grade})"],
        ["Pages Analyzed", str(report.pages_analyzed)],
        ["Issues Found", str(report.issues_found)],
        ["Audit Date", report.created_at.strftime("%B %d, %Y at %I:%M %p")],
        ["Audit Duration", f"{report.audit_duration:.1f} seconds"],
    ]

    overview_table = Table(overview_data, colWidths=[2 * inch, 4 * inch])
    overview_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#374151")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.gray),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.gray),
                (
                    "ROWBACKGROUNDS",
                    (0, 0),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f9fafb")],
                ),
            ]
        )
    )

    content.append(overview_table)
    content.append(Spacer(1, 0.3 * inch))

    # Score Breakdown
    content.append(Paragraph("Score Breakdown", heading_style))

    score_color = (
        colors.green
        if report.overall_score >= 80
        else colors.orange if report.overall_score >= 60 else colors.red
    )
    score_text = (
        f'<font color="{score_color.hexval()}"><b>{report.overall_score}/100</b></font>'
    )

    content.append(Paragraph(f"Overall SEO Score: {score_text}", body_style))
    content.append(Spacer(1, 0.2 * inch))

    # Technical SEO Section
    if "technical_analysis" in audit_data:
        content.append(Paragraph("Technical SEO Analysis", heading_style))
        technical = audit_data["technical_analysis"]

        technical_data = []
        if "https_usage" in technical:
            https_data = technical["https_usage"]
            technical_data.append(
                ["HTTPS Usage", f"{https_data.get('https_percentage', 0)}%"]
            )

        if "canonical_tags" in technical:
            canonical_data = technical["canonical_tags"]
            technical_data.append(
                ["Canonical Tags", f"{canonical_data.get('canonical_percentage', 0)}%"]
            )

        if "structured_data" in technical:
            schema_data = technical["structured_data"]
            technical_data.append(
                ["Schema Markup", f"{schema_data.get('schema_percentage', 0)}%"]
            )

        if technical_data:
            technical_table = Table(technical_data, colWidths=[2.5 * inch, 1.5 * inch])
            technical_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#dbeafe")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#374151")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.gray),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.gray),
                    ]
                )
            )
            content.append(technical_table)

    content.append(Spacer(1, 0.2 * inch))

    # Recommendations Section
    if "recommendations" in audit_data and audit_data["recommendations"]:
        content.append(Paragraph("Recommendations", heading_style))

        for i, rec in enumerate(
            audit_data["recommendations"][:10], 1
        ):  # Limit to top 10
            priority_color = (
                colors.red
                if rec.get("priority") == "high"
                else colors.orange if rec.get("priority") == "medium" else colors.blue
            )
            priority_text = f'<font color="{priority_color.hexval()}"><b>{rec.get("priority", "low").upper()}</b></font>'

            content.append(
                Paragraph(
                    f"{i}. [{priority_text}] {rec.get('category', 'General')}",
                    body_style,
                )
            )
            content.append(
                Paragraph(
                    f"   {rec.get('message', 'No description available')}", body_style
                )
            )
            content.append(Spacer(1, 0.1 * inch))

    # Page Analysis Summary
    if "pages_analysis" in audit_data:
        content.append(PageBreak())
        content.append(Paragraph("Page Analysis Summary", heading_style))

        pages_data = audit_data["pages_analysis"].get("pages", {})
        if pages_data:
            page_summary = []
            for url, page_data in list(pages_data.items())[
                :10
            ]:  # Limit to first 10 pages
                score = page_data.get("page_score", 0)
                title_len = len(page_data.get("title", {}).get("text", ""))
                meta_len = len(
                    page_data.get("meta", {}).get("description", {}).get("text", "")
                )

                page_summary.append(
                    [
                        url[:50] + "..." if len(url) > 50 else url,
                        f"{score}/100",
                        f"{title_len} chars",
                        f"{meta_len} chars",
                    ]
                )

            if page_summary:
                # Add header
                page_summary.insert(
                    0, ["Page URL", "Score", "Title Length", "Meta Desc Length"]
                )

                page_table = Table(
                    page_summary, colWidths=[3 * inch, 0.8 * inch, 1 * inch, 1.2 * inch]
                )
                page_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.gray),
                            ("BOX", (0, 0), (-1, -1), 0.25, colors.gray),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [colors.white, colors.HexColor("#f9fafb")],
                            ),
                        ]
                    )
                )
                content.append(page_table)

    # Footer
    content.append(Spacer(1, 0.5 * inch))
    content.append(
        Paragraph(
            f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.gray,
                alignment=TA_CENTER,
            ),
        )
    )

    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()


def is_pdf_available():
    """Check if PDF generation is available"""
    return PDF_AVAILABLE
