#!/usr/bin/env python3
"""
Report Generation Script for Trekking Management Application - V2
Student: S Karthik (Roll No: 23f2000278)
Course: Modern Application Development II (MAD-II)

Generates:
1. Project_Report_23f2000278.docx (Strictly compliant Microsoft Word document)
2. Project_Report_23f2000278.pdf  (High quality printable PDF document)
"""
import os
import zipfile
from xml.sax.saxutils import escape

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCX_PATH = os.path.join(BASE_DIR, 'Project_Report_23f2000278.docx')
PDF_PATH = os.path.join(BASE_DIR, 'Project_Report_23f2000278.pdf')

def generate_docx():
    """Build a professional, styled Word (.docx) document using OpenXML."""
    
    # XML templates
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
        <w:sz w:val="21"/>
        <w:color w:val="212529"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:sz w:val="38"/>
      <w:color w:val="1b4332"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:sz w:val="28"/>
      <w:color w:val="2d6a4f"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:sz w:val="24"/>
      <w:color w:val="40916c"/>
    </w:rPr>
  </w:style>
</w:styles>"""

    def p(text="", style=None, bold=False, italic=False, color=None, space_after=120, space_before=0, bullet=False):
        xml = f'<w:p><w:pPr><w:spacing w:before="{space_before}" w:after="{space_after}"/>'
        if style:
            xml += f'<w:pStyle w:val="{style}"/>'
        if bullet:
            xml += '<w:ind w:left="360" w:hanging="240"/>'
        xml += '</w:pPr>'
        if bullet:
            xml += '<w:r><w:t>• </w:t></w:r>'
        if text:
            xml += '<w:r><w:rPr>'
            if bold:
                xml += '<w:b/>'
            if italic:
                xml += '<w:i/>'
            if color:
                xml += f'<w:color w:val="{color}"/>'
            xml += f'</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
        xml += '</w:p>'
        return xml

    def table(rows, col_widths, bg_header="2d6a4f"):
        xml = '<w:tbl><w:tblPr><w:tblW w:w="9400" w:type="dxa"/>'
        xml += '<w:tblBorders>'
        xml += '<w:top w:val="single" w:sz="4" w:space="0" w:color="d3d3d3"/>'
        xml += '<w:left w:val="single" w:sz="4" w:space="0" w:color="d3d3d3"/>'
        xml += '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="d3d3d3"/>'
        xml += '<w:right w:val="single" w:sz="4" w:space="0" w:color="d3d3d3"/>'
        xml += '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="e5e5e5"/>'
        xml += '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="e5e5e5"/>'
        xml += '</w:tblBorders></w:tblPr>'
        
        # Grid
        xml += '<w:tblGrid>'
        for w in col_widths:
            xml += f'<w:gridCol w:w="{w}"/>'
        xml += '</w:tblGrid>'

        for r_idx, row in enumerate(rows):
            xml += '<w:tr>'
            is_header = (r_idx == 0)
            for c_idx, cell in enumerate(row):
                w = col_widths[c_idx] if c_idx < len(col_widths) else 2000
                xml += f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>'
                if is_header:
                    xml += f'<w:shd w:val="clear" w:color="auto" w:fill="{bg_header}"/>'
                elif r_idx % 2 == 1:
                    xml += '<w:shd w:val="clear" w:color="auto" w:fill="f8f9fa"/>'
                xml += '<w:tcMar><w:top w:w="80"/><w:left w:w="120"/><w:bottom w:w="80"/><w:right w:w="120"/></w:tcMar>'
                xml += '</w:tcPr>'
                
                # Cell paragraph
                color = "ffffff" if is_header else "212529"
                bold = is_header
                xml += f'<w:p><w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>'
                xml += f'<w:r><w:rPr><w:sz w:val="18"/>'
                if bold:
                    xml += '<w:b/>'
                xml += f'<w:color w:val="{color}"/></w:rPr><w:t xml:space="preserve">{escape(cell)}</w:t></w:r></w:p>'
                xml += '</w:tc>'
            xml += '</w:tr>'
        xml += '</w:tbl>'
        return xml

    # Assemble Document Body
    body_parts = []
    
    # Title & Subtitle
    body_parts.append(p("TrekFlow — Trekking Management Application V2", style="Title", bold=True, space_after=60))
    body_parts.append(p("Comprehensive Project Report | Modern Application Development II (MAD-II)", bold=True, color="555555", space_after=180))

    # 1. Student Details
    body_parts.append(p("1. Student Details", style="Heading1", space_before=100, space_after=60))
    student_table = [
        ["Field", "Detail"],
        ["Full Name", "S Karthik"],
        ["Roll Number", "23f2000278"],
        ["Course", "Modern Application Development II (MAD-II) - Term T3 2026"],
        ["Official Student Email", "23f2000278@ds.study.iitm.ac.in"],
        ["About the Candidate", "Hi, I'm S Karthik, a Data Science student at IIT Madras (BS Degree). Passionate about full-stack engineering, building scalable web systems, clean REST API architectures, and robust backend workflows."]
    ]
    body_parts.append(table(student_table, [2400, 7000]))
    body_parts.append(p("", space_after=140))

    # 2. Project Details
    body_parts.append(p("2. Project Details", style="Heading1", space_before=100, space_after=60))
    body_parts.append(p("Problem Statement", style="Heading2", space_after=40))
    body_parts.append(p("Adventure organizations require efficient systems to manage trekking activities involving trek organizers, staff, and participants. Currently, many trekking groups rely on spreadsheets, calls, or manual coordination, which makes it difficult to manage trek approvals, participant registrations, slot availability, and booking tracking. You are required to build a Trekking Management Application (TMA) web application that allows Admin, Trek Staff, and Users (Trekkers) to interact with the system based on their roles.", space_after=100))

    body_parts.append(p("Approach & Architecture", style="Heading2", space_after=40))
    body_parts.append(p("Developed TrekFlow V2, an enterprise-grade full-stack Trekking Management Application built strictly on the required stack:", space_after=60))
    body_parts.append(p("Programmatic Database & Superuser Seeding: SQLite database tables and the pre-existing Superuser Admin are created purely via SQLAlchemy model code upon server initialization without manual database editor tools.", bullet=True, space_after=40))
    body_parts.append(p("Role-Based Access Control (RBAC): Implemented with signed JWT tokens enforcing strict endpoint authorization for Admin, Trek Staff, and User (Trekker).", bullet=True, space_after=40))
    body_parts.append(p("Administrative Governance: Full CRUD on trekking routes, staff creation, coordinator scheduling, platform-wide booking oversight, and account deactivation/blacklisting.", bullet=True, space_after=40))
    body_parts.append(p("Staff Coordination Hub: Dedicated staff dashboard allowing assigned guides to manage available slots, update trek execution progress, and manage participant rosters.", bullet=True, space_after=40))
    body_parts.append(p("Trekker Discovery & Booking Engine: Search and multi-criteria filtering by difficulty, location, and duration; real-time slot reservation preventing overbooking and duplicate active bookings; automatic slot restoration on cancellation.", bullet=True, space_after=40))
    body_parts.append(p("High-Performance Redis Caching: Frequently accessed trek listings are cached in Redis with configurable TTL expiry and automatic cache invalidation on route mutations.", bullet=True, space_after=40))
    body_parts.append(p("Asynchronous Batch Processing (Celery & Redis): Scheduled Daily Reminders, Monthly Activity Report generation (HTML & PDF), and User-triggered Async CSV Export of booking history.", bullet=True, space_after=120))

    # 3. AI / LLM Declaration
    body_parts.append(p("3. AI / LLM Declaration", style="Heading1", space_before=100, space_after=60))
    body_parts.append(p("In accordance with IIT Madras academic integrity guidelines, below is the explicit disclosure of AI tool usage:", space_after=60))
    ai_table = [
        ["Activity", "Tool Used", "Approx. Usage", "Details"],
        ["Debugging & Error Resolution", "Google Gemini / Antigravity", "< 2%", "Diagnosing Redis connection timeout fallbacks and test assertion fixes."],
        ["Frontend UI/UX Styling", "Google Gemini / Antigravity", "8%", "Crafting Bootstrap 5 responsive utility classes, theme variables, and badges."],
        ["Dashboard Analytics Structuring", "Google Gemini / Antigravity", "3%", "Formatting data coordinates for Chart.js bar and doughnut visualizations."],
        ["Architecture & Documentation", "Google Gemini / Antigravity", "Assisted", "Structuring modular Flask blueprints, Celery beat crontab, and report formatting."]
    ]
    body_parts.append(table(ai_table, [2400, 1800, 1400, 3800]))
    body_parts.append(p("", space_after=140))

    # 4. Frameworks and Libraries Used
    body_parts.append(p("4. Frameworks and Libraries Used", style="Heading1", space_before=100, space_after=60))
    tech_table = [
        ["Category", "Mandatory Technology", "Version / Purpose"],
        ["Backend API", "Flask (Python 3)", "Flask 3.0.3, Werkzeug 3.0, Flask-Cors 4.0"],
        ["Database", "SQLite (strictly)", "SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1. Programmatic creation."],
        ["Security / RBAC", "PyJWT", "PyJWT 2.9, cryptographic password hashing (pbkdf2:sha256)"],
        ["Caching Layer", "Redis", "Redis 5.0 client, TTL expiry (300s), cache invalidation decorators"],
        ["Batch Jobs", "Celery & Redis", "Celery 5.4 with Redis message broker and Celery Beat scheduler"],
        ["Report Generation", "ReportLab", "ReportLab 4.2 for PDF reports, Jinja2/string templating for HTML"],
        ["Frontend Framework", "Vue.js 3 (SFC)", "Vue 3.5, Vite 5.4, Vue Router 4.4, Pinia 2.2"],
        ["UI Styling", "Bootstrap 5 (strictly)", "Bootstrap 5.3, Bootstrap Icons 1.11, Chart.js 4.4"]
    ]
    body_parts.append(table(tech_table, [2200, 2600, 4600]))
    body_parts.append(p("", space_after=140))

    # 5. Database Schema (ER Diagram)
    body_parts.append(p("5. Database Schema (ER Diagram)", style="Heading1", space_before=100, space_after=60))
    body_parts.append(p("The application utilizes a normalized relational schema created programmatically in SQLite:", space_after=60))
    
    er_table = [
        ["Table Name", "Primary Key", "Foreign Keys", "Key Attributes & Purpose"],
        ["users", "id (Integer)", "None", "username, email, password_hash, name, role ('admin'/'staff'/'user'), contact_number, is_active, is_blacklisted, created_at. Unified user model."],
        ["staff_profiles", "id (Integer)", "user_id -> users.id", "contact_details, experience_years, qualifications, status, emergency_contact. 1-to-1 extension for staff."],
        ["treks", "id (Integer)", "assigned_staff_id -> users.id", "name, location, difficulty, duration_days, total_slots, available_slots, price, status ('Open'/'Closed'/'Completed'), start_date, end_date, images_json."],
        ["bookings", "id (Integer)", "user_id -> users.id, trek_id -> treks.id", "num_seats, total_amount, booking_date, status ('Booked'/'Cancelled'/'Completed'), payment_status, payment_method, transaction_id."],
        ["notifications", "id (Integer)", "user_id -> users.id", "title, message, notification_type ('reminder'/'booking'/'export'/'system'), is_read, download_url, created_at."]
    ]
    body_parts.append(table(er_table, [1400, 1400, 2200, 4400]))
    body_parts.append(p("", space_after=60))
    
    # Textual ER Diagram
    body_parts.append(p("Entity-Relationship Overview:", style="Heading2", space_after=40))
    body_parts.append(p("[User (Admin)]  --- (1:N) --->  [Trek (Route Creator & Supervisor)]", bullet=True, space_after=30))
    body_parts.append(p("[User (Staff)]  <--- (1:1) --->  [StaffProfile (Guide Credentials)]", bullet=True, space_after=30))
    body_parts.append(p("[User (Staff)]  --- (1:N) --->  [Trek (Assigned Coordinator / Guide)]", bullet=True, space_after=30))
    body_parts.append(p("[User (Trekker)] --- (1:N) --->  [Booking (Participant Registrations)]", bullet=True, space_after=30))
    body_parts.append(p("[Trek]           --- (1:N) --->  [Booking (Slot Allocations)]", bullet=True, space_after=30))
    body_parts.append(p("[User]           --- (1:N) --->  [Notification (Alerts & Reports)]", bullet=True, space_after=120))

    # 6. API Resource Endpoints
    body_parts.append(p("6. API Resource Endpoints", style="Heading1", space_before=100, space_after=60))
    api_table = [
        ["Module", "Method", "Endpoint", "Auth / Role", "Description"],
        ["Auth", "POST", "/api/auth/register", "Public", "Trekker self-registration (role enforced as 'user')"],
        ["Auth", "POST", "/api/auth/login", "Public", "Unified authentication for Admin, Staff, and Trekkers"],
        ["Auth", "GET", "/api/auth/me", "JWT Required", "Fetch current authenticated user profile & alerts count"],
        ["Auth", "PUT", "/api/auth/profile", "JWT Required", "Update personal details, contact info, or password"],
        ["Auth", "GET", "/api/auth/notifications", "JWT Required", "List in-app alerts, batch completion, and reminders"],
        ["Treks", "GET", "/api/treks", "Public / Cached", "List treks with search & multi-criteria filtering (Redis cached)"],
        ["Treks", "GET", "/api/treks/<id>", "Public", "Detailed metadata for an individual trekking route"],
        ["Treks", "POST", "/api/treks", "Admin", "Create a new trekking route and schedule"],
        ["Treks", "PUT", "/api/treks/<id>", "Admin", "Update trek metadata, total slots, or scheduled dates"],
        ["Treks", "DELETE", "/api/treks/<id>", "Admin", "Remove trek (guarded against active bookings)"],
        ["Treks", "POST", "/api/treks/upload-image", "Admin", "Upload local trek cover images (PNG/JPG)"],
        ["Treks", "PATCH", "/api/treks/<id>/status", "Admin / Staff", "Update status (Pending/Approved/Open/Closed/Completed)"],
        ["Bookings", "POST", "/api/bookings", "User", "Book trek slots (overbooking & duplicate prevention)"],
        ["Bookings", "GET", "/api/bookings/my", "User", "Fetch complete historical trekking records for user"],
        ["Bookings", "POST", "/api/bookings/<id>/cancel", "User", "Cancel booking and automatically restore available slots"],
        ["Bookings", "POST", "/api/bookings/export-csv", "User", "Trigger Celery async job to export booking history"],
        ["Bookings", "GET", "/api/bookings/download-csv/<file>", "User", "Download exported booking history CSV file"],
        ["Admin", "GET", "/api/admin/stats", "Admin", "Dashboard metrics, revenue, and Chart.js datasets"],
        ["Admin", "GET", "/api/admin/users", "Admin", "Search and list all platform users and staff"],
        ["Admin", "PATCH", "/api/admin/users/<id>/status", "Admin", "Deactivate or Blacklist a user or staff account"],
        ["Admin", "POST", "/api/admin/staff", "Admin", "Create a new staff member and profile"],
        ["Admin", "POST", "/api/admin/treks/<id>/assign-staff", "Admin", "Assign designated staff coordinator to a trek"],
        ["Admin", "GET", "/api/admin/bookings", "Admin", "Oversight and filtering of all bookings across platform"],
        ["Admin", "POST", "/api/admin/reports/monthly", "Admin", "Trigger Celery batch generation of monthly report"],
        ["Admin", "GET", "/api/admin/reports", "Admin", "List generated PDF and HTML monthly reports"],
        ["Staff", "GET", "/api/staff/my-treks", "Staff", "View treks assigned by admin with participant tallies"],
        ["Staff", "GET", "/api/staff/treks/<id>/participants", "Staff", "View registered trekkers roster for assigned trek"],
        ["Staff", "PUT", "/api/staff/treks/<id>/slots", "Staff", "Update available slots for assigned trek"],
        ["Staff", "PUT", "/api/staff/treks/<id>/status", "Staff", "Update trek status; complete all active bookings"]
    ]
    body_parts.append(table(api_table, [1000, 800, 2600, 1400, 3600]))
    body_parts.append(p("", space_after=140))

    # 7. Architecture & Key Features
    body_parts.append(p("7. Architecture and Key Features", style="Heading1", space_before=100, space_after=60))
    body_parts.append(p("Folder Structure Overview:", style="Heading2", space_after=40))
    struct_table = [
        ["Path", "Component", "Responsibility"],
        ["backend/app.py", "Flask App Entrypoint", "Factory function, blueprint registration, CORS, SPA static serving"],
        ["backend/config.py", "Configuration", "SQLite URI, JWT keys, Redis URLs, Celery settings"],
        ["backend/database.py", "SQLAlchemy Init", "Shared db instance preventing circular imports"],
        ["backend/init_db.py", "Programmatic Seeder", "Automated DB creation, Admin superuser & sample data seeding"],
        ["backend/models/", "Data Entities", "Unified User, StaffProfile, Trek, Booking, Notification models"],
        ["backend/routes/", "Modular Controllers", "auth_routes, trek_routes, booking_routes, admin_routes, staff_routes"],
        ["backend/tasks/celery_app.py", "Batch Worker", "Celery crontab for reminders & monthly report; async CSV export"],
        ["backend/utils/", "Helper Services", "auth.py (JWT/RBAC), cache.py (Redis), pdf_generator.py (ReportLab)"],
        ["backend/test_app.py", "Test Suite", "Comprehensive integration tests for RBAC, rules, caching & batch jobs"],
        ["frontend/src/views/", "Vue Pages", "Role-specific views (Admin, Staff, Trekker, Landing, Auth)"],
        ["frontend/src/components/", "UI Components", "Navbar, Footer, TrekCard, BookingModal, StatsChart, ToastAlert"],
        ["frontend/src/store/auth.js", "State Management", "Pinia reactive store for tokens, active user role & alerts"],
        ["frontend/src/router/", "Client Routing", "Vue Router with navigation guards enforcing authentication & RBAC"]
    ]
    body_parts.append(table(struct_table, [2400, 2000, 5000]))
    body_parts.append(p("", space_after=60))

    body_parts.append(p("Key Business Rules & Capabilities Implemented:", style="Heading2", space_after=40))
    body_parts.append(p("Unified User Model: Single 'users' table handles Admin, Staff, and Trekkers with distinct role privileges, active status flags, and blacklisting controls.", bullet=True, space_after=30))
    body_parts.append(p("Pre-existing Superuser Admin: Programmatically seeded on initial startup; registration is strictly blocked for Admin and Staff roles.", bullet=True, space_after=30))
    body_parts.append(p("Overbooking & Concurrency Protection: Available slots are decremented upon booking and checked via database transactions; requests exceeding capacity are rejected with 400 Bad Request.", bullet=True, space_after=30))
    body_parts.append(p("Duplicate Booking Prevention: Users cannot hold multiple active bookings for the same trek (409 Conflict).", bullet=True, space_after=30))
    body_parts.append(p("Slot Restoration on Cancellation: Trekkers can cancel their bookings, which automatically restores the corresponding seats back to the trek's available pool.", bullet=True, space_after=30))
    body_parts.append(p("Assigned Staff Exclusivity: Only designated guides assigned to a specific trek can alter its capacity, update progress, or access its passenger roster.", bullet=True, space_after=30))
    body_parts.append(p("Scheduled Daily Reminders: Celery beat job runs daily at 08:00 AM, scanning for treks starting within 3 days and dispatching alert notifications to participants.", bullet=True, space_after=30))
    body_parts.append(p("Scheduled Monthly Activity Report: Automatically compiles conducted treks, participation numbers, and revenue on the 1st of every month, generating downloadable PDF and HTML reports for the Admin.", bullet=True, space_after=30))
    body_parts.append(p("User-Triggered Async CSV Export: Trekkers can export their historical bookings asynchronously via Celery; an alert notification provides the instant download link.", bullet=True, space_after=30))
    body_parts.append(p("High-Performance Redis Caching: Frequently accessed trek listings are cached in Redis with TTL expiry, reducing DB latency and responding with X-Cache-Status headers.", bullet=True, space_after=120))

    # 8. Presentation Video Drive Link
    body_parts.append(p("8. Presentation Video Link", style="Heading1", space_before=100, space_after=60))
    body_parts.append(p("Presentation Video URL (Google Drive):", bold=True, space_after=30))
    body_parts.append(p("https://drive.google.com/file/d/your-drive-id/view?usp=sharing", color="0056b3", italic=True, space_after=80))
    body_parts.append(p("GitHub Repository URL:", bold=True, space_after=30))
    body_parts.append(p("https://github.com/SKarthik12321/Trekking-Management-Application-23f2000278", color="0056b3", italic=True, space_after=120))
    body_parts.append(p("Report certified and submitted for Modern Application Development II (MAD-II) Evaluation.", italic=True, color="777777", space_after=60))

    # Construct Document XML
    doc_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    doc_xml += '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
    doc_xml += '<w:body>\n'
    doc_xml += "".join(body_parts)
    
    # Page setup: Letter size with 0.75 in margins (1080 dxa)
    doc_xml += '<w:sectPr>'
    doc_xml += '<w:pgSz w:w="12240" w:h="15840"/>'
    doc_xml += '<w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/>'
    doc_xml += '</w:sectPr>'
    doc_xml += '</w:body></w:document>'

    # Write ZIP (.docx)
    with zipfile.ZipFile(DOCX_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', rels)
        zf.writestr('word/_rels/document.xml.rels', doc_rels)
        zf.writestr('word/styles.xml', styles)
        zf.writestr('word/document.xml', doc_xml)

    print(f"[DOCX GENERATOR] Successfully created: {DOCX_PATH}")

def generate_pdf():
    """Build a matching high-quality PDF using ReportLab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('RepTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1b4332'), spaceAfter=4)
    subtitle_style = ParagraphStyle('RepSubTitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#555555'), spaceAfter=10)
    h1_style = ParagraphStyle('RepH1', parent=styles['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor('#2d6a4f'), spaceBefore=10, spaceAfter=4)
    h2_style = ParagraphStyle('RepH2', parent=styles['Heading3'], fontSize=10, leading=13, textColor=colors.HexColor('#40916c'), spaceBefore=6, spaceAfter=3)
    body_style = ParagraphStyle('RepBody', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#212529'), spaceAfter=4)
    bullet_style = ParagraphStyle('RepBullet', parent=body_style, leftIndent=12, firstLineIndent=-8, spaceAfter=2)
    cell_style = ParagraphStyle('RepCell', parent=body_style, fontSize=7.5, leading=9.5)
    cell_head_style = ParagraphStyle('RepCellHead', parent=cell_style, fontName='Helvetica-Bold', textColor=colors.white)

    story = []

    def make_table(data, widths, bg_header='#2d6a4f'):
        formatted = []
        for r_idx, row in enumerate(data):
            r_cells = []
            for cell in row:
                st = cell_head_style if r_idx == 0 else cell_style
                r_cells.append(Paragraph(str(cell), st))
            formatted.append(r_cells)
        t = Table(formatted, colWidths=widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(bg_header)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d3d3d3')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        return t

    # Header
    story.append(Paragraph("TrekFlow — Trekking Management Application V2", title_style))
    story.append(Paragraph("Comprehensive Project Report | Modern Application Development II (MAD-II) | Roll No: 23f2000278", subtitle_style))

    # 1. Student Details
    story.append(Paragraph("1. Student Details", h1_style))
    story.append(make_table([
        ["Field", "Detail"],
        ["Full Name", "S Karthik"],
        ["Roll Number", "23f2000278"],
        ["Course", "Modern Application Development II (MAD-II) - Term T3 2026"],
        ["Official Student Email", "23f2000278@ds.study.iitm.ac.in"],
        ["About the Candidate", "Hi, I'm S Karthik, a Data Science student at IIT Madras (BS Degree). Passionate about full-stack engineering, building scalable web systems, clean REST API architectures, and robust backend workflows."]
    ], [140, 400]))
    story.append(Spacer(1, 6))

    # 2. Project Details
    story.append(Paragraph("2. Project Details & Approach", h1_style))
    story.append(Paragraph("<b>Problem Statement:</b> Adventure organizations require efficient systems to manage trekking activities involving trek organizers, staff, and participants. Many groups rely on spreadsheets or manual calls, hindering trek approvals, participant registrations, and slot tracking. Built a responsive TMA web application serving Admin, Trek Staff, and Trekkers.", body_style))
    story.append(Paragraph("• <b>Programmatic Seeding:</b> SQLite tables and default Admin superuser are created programmatically on startup without DB Browser.", bullet_style))
    story.append(Paragraph("• <b>RBAC Security:</b> Signed JWT tokens enforce distinct permissions for Admin, Trek Staff, and Trekkers.", bullet_style))
    story.append(Paragraph("• <b>Booking Integrity:</b> Concurrency protection, duplicate active booking prevention, and automatic slot restoration on cancellation.", bullet_style))
    story.append(Paragraph("• <b>Redis Caching:</b> Frequently accessed trek endpoints are cached with TTL expiry and automatic cache invalidation on route changes.", bullet_style))
    story.append(Paragraph("• <b>Celery Batch Processing:</b> Scheduled Daily Reminders, Monthly Activity Report generation (HTML & PDF), and Async CSV Exports.", bullet_style))
    story.append(Spacer(1, 6))

    # 3. AI / LLM Declaration
    story.append(Paragraph("3. AI / LLM Declaration", h1_style))
    story.append(make_table([
        ["Activity", "Tool Used", "Approx. Usage", "Details"],
        ["Debugging Errors", "Google Gemini / Antigravity", "< 2%", "Diagnosing Redis connection fallbacks and test assertion fixes."],
        ["Frontend UI/UX Styling", "Google Gemini / Antigravity", "8%", "Crafting Bootstrap 5 responsive utility classes and theme badges."],
        ["Dashboard Analytics Structuring", "Google Gemini / Antigravity", "3%", "Formatting data coordinates for Chart.js bar and doughnut charts."],
        ["Architecture & Documentation", "Google Gemini / Antigravity", "Assisted", "Structuring modular Flask blueprints, Celery crontab, and report formatting."]
    ], [120, 100, 80, 240]))
    story.append(Spacer(1, 6))

    # 4. Frameworks and Libraries Used
    story.append(Paragraph("4. Frameworks and Libraries Used", h1_style))
    story.append(make_table([
        ["Category", "Mandatory Technology", "Version / Purpose"],
        ["Backend API", "Flask (Python 3)", "Flask 3.0.3, Werkzeug 3.0, Flask-Cors 4.0. REST API."],
        ["Database", "SQLite (strictly)", "SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1. Programmatic creation."],
        ["Security / RBAC", "PyJWT", "PyJWT 2.9, cryptographic password hashing (pbkdf2:sha256)."],
        ["Caching Layer", "Redis", "Redis 5.0 client, TTL expiry (300s), cache invalidation decorators."],
        ["Batch Jobs", "Celery & Redis", "Celery 5.4 with Redis message broker and Celery Beat scheduler."],
        ["Report Generation", "ReportLab", "ReportLab 4.2 for PDF reports, string templating for HTML."],
        ["Frontend Framework", "Vue.js 3 (SFC)", "Vue 3.5, Vite 5.4, Vue Router 4.4, Pinia 2.2."],
        ["UI Styling", "Bootstrap 5 (strictly)", "Bootstrap 5.3, Bootstrap Icons 1.11, Chart.js 4.4."]
    ], [110, 130, 300]))
    story.append(Spacer(1, 6))

    # 5. Database Schema (ER Diagram)
    story.append(Paragraph("5. Database Schema (ER Diagram)", h1_style))
    story.append(make_table([
        ["Table Name", "Primary Key", "Foreign Keys", "Key Attributes & Purpose"],
        ["users", "id (Int)", "None", "username, email, password_hash, name, role ('admin'/'staff'/'user'), is_active, is_blacklisted. Unified user table."],
        ["staff_profiles", "id (Int)", "user_id -> users.id", "contact_details, experience_years, qualifications, status, emergency_contact. 1-to-1 extension."],
        ["treks", "id (Int)", "assigned_staff_id -> users.id", "name, location, difficulty, duration_days, total_slots, available_slots, price, status, start_date, end_date, images_json."],
        ["bookings", "id (Int)", "user_id -> users.id, trek_id -> treks.id", "num_seats, total_amount, booking_date, status ('Booked'/'Cancelled'/'Completed'), payment_status, transaction_id."],
        ["notifications", "id (Int)", "user_id -> users.id", "title, message, notification_type, is_read, download_url, created_at. System & batch job alerts."]
    ], [80, 70, 110, 280]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Relationships:</b> users(admin) 1:N treks (creator) | users(staff) 1:1 staff_profiles | users(staff) 1:N treks (assigned guide) | users(trekker) 1:N bookings | treks 1:N bookings | users 1:N notifications.", body_style))
    story.append(Spacer(1, 6))

    # 6. API Resource Endpoints
    story.append(Paragraph("6. API Resource Endpoints", h1_style))
    story.append(make_table([
        ["Module", "Method", "Endpoint", "Role", "Description"],
        ["Auth", "POST", "/api/auth/register", "Public", "Trekker self-registration (role enforced as 'user')"],
        ["Auth", "POST", "/api/auth/login", "Public", "Unified authentication for Admin, Staff, and Trekkers"],
        ["Auth", "GET", "/api/auth/me", "JWT", "Fetch current authenticated user profile & alerts count"],
        ["Auth", "PUT", "/api/auth/profile", "JWT", "Update personal details, contact info, or password"],
        ["Treks", "GET", "/api/treks", "Public/Cache", "List treks with search & filtering (Redis cached)"],
        ["Treks", "POST", "/api/treks", "Admin", "Create a new trekking route and schedule"],
        ["Treks", "PUT", "/api/treks/<id>", "Admin", "Update trek metadata, total slots, or scheduled dates"],
        ["Treks", "DELETE", "/api/treks/<id>", "Admin", "Remove trek (guarded against active bookings)"],
        ["Treks", "PATCH", "/api/treks/<id>/status", "Admin/Staff", "Update status (Pending/Approved/Open/Closed/Completed)"],
        ["Bookings", "POST", "/api/bookings", "User", "Book trek slots (overbooking & duplicate prevention)"],
        ["Bookings", "GET", "/api/bookings/my", "User", "Fetch complete historical trekking records for user"],
        ["Bookings", "POST", "/api/bookings/<id>/cancel", "User", "Cancel booking and automatically restore available slots"],
        ["Bookings", "POST", "/api/bookings/export-csv", "User", "Trigger Celery async job to export booking history as CSV"],
        ["Admin", "GET", "/api/admin/stats", "Admin", "Dashboard metrics, revenue, and Chart.js datasets"],
        ["Admin", "GET", "/api/admin/users", "Admin", "Search and list all platform users and staff"],
        ["Admin", "PATCH", "/api/admin/users/<id>/status", "Admin", "Deactivate or Blacklist a user or staff account"],
        ["Admin", "POST", "/api/admin/staff", "Admin", "Create a new staff member and profile"],
        ["Admin", "POST", "/api/admin/treks/<id>/assign-staff", "Admin", "Assign designated staff coordinator to a trek"],
        ["Admin", "GET", "/api/admin/bookings", "Admin", "Oversight and filtering of all bookings across platform"],
        ["Admin", "POST", "/api/admin/reports/monthly", "Admin", "Trigger Celery batch generation of monthly report"],
        ["Staff", "GET", "/api/staff/my-treks", "Staff", "View treks assigned by admin with participant tallies"],
        ["Staff", "GET", "/api/staff/treks/<id>/participants", "Staff", "View registered trekkers roster for assigned trek"],
        ["Staff", "PUT", "/api/staff/treks/<id>/slots", "Staff", "Update available slots for assigned trek"],
        ["Staff", "PUT", "/api/staff/treks/<id>/status", "Staff", "Update trek status; complete all active bookings"]
    ], [50, 45, 175, 70, 200]))
    story.append(Spacer(1, 6))

    # 7. Presentation Video & Verification
    story.append(Paragraph("7. Presentation Video & Project Links", h1_style))
    story.append(Paragraph("<b>Presentation Video URL (Google Drive):</b> <font color='#0056b3'><u>https://drive.google.com/file/d/your-drive-id/view?usp=sharing</u></font>", body_style))
    story.append(Paragraph("<b>GitHub Repository URL:</b> <font color='#0056b3'><u>https://github.com/SKarthik12321/Trekking-Management-Application-23f2000278</u></font>", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>Report certified and prepared for Modern Application Development II (MAD-II) Viva Evaluation.</i>", subtitle_style))

    doc.build(story)
    print(f"[PDF GENERATOR] Successfully created: {PDF_PATH}")

if __name__ == '__main__':
    generate_docx()
    generate_pdf()

