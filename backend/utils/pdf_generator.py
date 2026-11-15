"""
PDF and HTML Monthly Activity Report Generator for Admin.
Utilizes ReportLab to generate professional PDF documents for trekking activity.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_monthly_pdf(report_data: dict, output_filepath: str) -> str:
    """Generate a high quality PDF report for trekking administration."""
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1b4332'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2d6a4f'),
        spaceBefore=15,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.black
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Trekking Management Application - Monthly Activity Report", title_style))
    story.append(Paragraph(f"Generated on: {report_data.get('generated_at', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))} | Period: {report_data.get('period', 'Current Month')}", subtitle_style))
    story.append(Spacer(1, 10))

    # Executive Summary Metrics Table
    summary_data = [
        ["Key Metric", "Total Value"],
        ["Total Treks Conducted / Scheduled", str(report_data.get('total_treks', 0))],
        ["Completed Treks", str(report_data.get('completed_treks', 0))],
        ["Total Bookings Registered", str(report_data.get('total_bookings', 0))],
        ["Total Trekkers / Participants", str(report_data.get('total_participants', 0))],
        ["Total Revenue Generated", f"INR {report_data.get('total_revenue', 0.0):,.2f}"]
    ]
    t_summary = Table(summary_data, colWidths=[320, 180])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d3d3d3')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white])
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))

    # Popular Treks Section
    story.append(Paragraph("Popular Treks and Booking Distribution", section_heading))
    popular_treks = report_data.get('popular_treks', [])
    if popular_treks:
        pop_table_data = [["Trek Name", "Location", "Difficulty", "Total Bookings", "Seats Filled"]]
        for t in popular_treks:
            pop_table_data.append([
                t.get('name', ''),
                t.get('location', ''),
                t.get('difficulty', ''),
                str(t.get('booking_count', 0)),
                str(t.get('seats_booked', 0))
            ])
        t_pop = Table(pop_table_data, colWidths=[150, 130, 80, 80, 60])
        t_pop.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#40916c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d3d3d3')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white])
        ]))
        story.append(t_pop)
    else:
        story.append(Paragraph("No trek booking data recorded for this period.", body_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Report verified programmatically by Trekking Management Application Batch System.", subtitle_style))

    doc.build(story)
    return output_filepath

def generate_monthly_html(report_data: dict) -> str:
    """Generate clean responsive HTML version of the monthly activity report."""
    popular_rows = "".join([
        f"<tr><td>{t.get('name')}</td><td>{t.get('location')}</td><td>{t.get('difficulty')}</td><td>{t.get('booking_count')}</td><td>{t.get('seats_booked')}</td></tr>"
        for t in report_data.get('popular_treks', [])
    ]) or "<tr><td colspan='5' class='text-center'>No activity recorded</td></tr>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Monthly Trekking Activity Report</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 30px; color: #212529; }}
            .header {{ background: #1b4332; color: #fff; padding: 20px; border-radius: 8px; }}
            h1 {{ margin: 0; font-size: 24px; }}
            .meta {{ color: #d8f3dc; font-size: 14px; margin-top: 5px; }}
            .card {{ border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #dee2e6; padding: 10px; text-align: left; }}
            th {{ background: #2d6a4f; color: white; }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Trekking Management Application - Monthly Activity Report</h1>
            <div class="meta">Generated: {report_data.get('generated_at')} | Period: {report_data.get('period')}</div>
        </div>
        <div class="card">
            <h2>Executive Summary</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Treks</td><td>{report_data.get('total_treks', 0)}</td></tr>
                <tr><td>Completed Treks</td><td>{report_data.get('completed_treks', 0)}</td></tr>
                <tr><td>Total Bookings</td><td>{report_data.get('total_bookings', 0)}</td></tr>
                <tr><td>Total Trekkers</td><td>{report_data.get('total_participants', 0)}</td></tr>
                <tr><td>Total Revenue</td><td>INR {report_data.get('total_revenue', 0.0):,.2f}</td></tr>
            </table>
        </div>
        <div class="card">
            <h2>Popular Treks</h2>
            <table>
                <tr><th>Trek Name</th><th>Location</th><th>Difficulty</th><th>Bookings</th><th>Participants</th></tr>
                {popular_rows}
            </table>
        </div>
    </body>
    </html>
    """
