"""
Celery configuration and batch job worker for Trekking Management Application - V2.
Handles scheduled daily reminders, monthly activity reports, and async CSV exports.
"""
import os
import csv
import html
import smtplib
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from config import Config
from utils.email_service import send_email

# Initialize Celery
celery_app = Celery(
    'tma_batch_tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)

# Celery Configuration
celery_app.conf.update(
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_track_started=True,
    beat_schedule={
        # Scheduled Job 1: Daily reminders at 08:00 AM
        'daily-trek-reminders': {
            'task': 'tasks.celery_app.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        # Scheduled Job 2: Monthly report on 1st of every month at midnight
        'monthly-activity-report': {
            'task': 'tasks.celery_app.generate_monthly_report',
            'schedule': crontab(day_of_month=1, hour=0, minute=0),
        }
    }
)

def get_flask_app():
    """
    Lazily imports and creates the Flask app inside each Celery task.
    Can't import at module level here — Celery workers start without a Flask context,
    so we defer the app creation until the task actually runs.
    """
    from app import create_app
    return create_app()

@celery_app.task(name='tasks.celery_app.send_daily_reminders')
def send_daily_reminders():
    """
    Scheduled Job (a): Daily Reminders.
    Finds upcoming treks within the next 3 days and sends instructions/reminders to registered users.
    Records in-app notifications and sends email when SMTP is enabled.
    """
    app = get_flask_app()
    with app.app_context():
        from database import db
        from models import Trek, Booking, User, Notification

        today = datetime.utcnow().date()
        reminder_window_end = today + timedelta(days=3)

        upcoming_treks = Trek.query.filter(
            Trek.start_date >= today,
            Trek.start_date <= reminder_window_end,
            Trek.status.in_(['Open', 'Approved'])
        ).all()

        reminders_sent = 0
        logs = []
        email_messages = []

        for trek in upcoming_treks:
            active_bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
            for booking in active_bookings:
                user = booking.user
                if user and user.is_active and not user.is_blacklisted:
                    days_left = (trek.start_date - today).days
                    msg = (
                        f"Hello {user.name}! Your upcoming trek '{trek.name}' at {trek.location} "
                        f"is scheduled to begin in {days_left} day(s) on {trek.start_date.isoformat()}. "
                        f"Instructions: Carry valid ID, water bottles, thermal wear, and first-aid supplies. "
                        f"Guide Contact: {trek.assigned_staff.name if trek.assigned_staff else 'Support desk'}."
                    )

                    # Persist in-app notification
                    notif = Notification(
                        user_id=user.id,
                        title=f"Reminder: {trek.name} starts in {days_left} day(s)",
                        message=msg,
                        notification_type='reminder'
                    )
                    db.session.add(notif)
                    reminders_sent += 1
                    email_messages.append({
                        'user_id': user.id,
                        'email': user.email,
                        'subject': f"Reminder: {trek.name} starts in {days_left} day(s)",
                        'message': msg
                    })
                    logs.append({
                        'user_id': user.id,
                        'email': user.email,
                        'trek': trek.name,
                        'start_date': trek.start_date.isoformat()
                    })

        db.session.commit()
        emails_sent = 0
        email_failures = 0
        if app.config.get('SMTP_ENABLED'):
            for item in email_messages:
                try:
                    send_email(
                        item['email'],
                        item['subject'],
                        item['message'],
                        f"<p>{html.escape(item['message'])}</p>"
                    )
                    emails_sent += 1
                except (OSError, smtplib.SMTPException, ValueError):
                    app.logger.exception(
                        'Failed to send a trek reminder email to user id %s.',
                        item['user_id']
                    )
                    email_failures += 1

        print(
            f"[CELERY REMINDER] Created {reminders_sent} in-app reminders; "
            f"emails sent: {emails_sent}, email failures: {email_failures}."
        )
        return {
            'status': 'SUCCESS',
            'reminders_sent': reminders_sent,
            'emails_sent': emails_sent,
            'email_failures': email_failures,
            'email_status': 'disabled' if not app.config.get('SMTP_ENABLED') else 'enabled',
            'logs': logs
        }

@celery_app.task(name='tasks.celery_app.generate_monthly_report')
def generate_monthly_report():
    """
    Scheduled Job (b): Monthly Activity Report.
    Generates comprehensive summary of treks conducted, participants, revenue, and popular treks.
    Creates both HTML and PDF reports and notifies Admin.
    """
    app = get_flask_app()
    with app.app_context():
        from database import db
        from models import Trek, Booking, User, Notification
        from utils.pdf_generator import generate_monthly_pdf, generate_monthly_html

        total_treks = Trek.query.count()
        completed_treks = Trek.query.filter_by(status='Completed').count()
        total_bookings = Booking.query.filter_by(status='Booked').count()

        # Total participants and revenue
        bookings = Booking.query.filter_by(status='Booked').all()
        total_participants = sum(b.num_seats for b in bookings)
        total_revenue = sum(b.total_amount for b in bookings)

        # Popular treks
        treks = Trek.query.all()
        popular_treks = []
        for t in treks:
            t_bookings = [b for b in t.bookings if b.status == 'Booked']
            seats = sum(b.num_seats for b in t_bookings)
            popular_treks.append({
                'name': t.name,
                'location': t.location,
                'difficulty': t.difficulty,
                'booking_count': len(t_bookings),
                'seats_booked': seats
            })
        popular_treks.sort(key=lambda x: x['booking_count'], reverse=True)
        top_popular = popular_treks[:5]

        now = datetime.utcnow()
        month_str = now.strftime('%B %Y')
        timestamp_str = now.strftime('%Y%m%d_%H%M%S')

        report_data = {
            'period': month_str,
            'generated_at': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'total_treks': total_treks,
            'completed_treks': completed_treks,
            'total_bookings': total_bookings,
            'total_participants': total_participants,
            'total_revenue': total_revenue,
            'popular_treks': top_popular
        }

        # Generate PDF file
        pdf_filename = f"monthly_report_{timestamp_str}.pdf"
        pdf_path = os.path.join(Config.REPORTS_DIR, pdf_filename)
        generate_monthly_pdf(report_data, pdf_path)

        # Generate HTML file
        html_filename = f"monthly_report_{timestamp_str}.html"
        html_path = os.path.join(Config.REPORTS_DIR, html_filename)
        html_report = generate_monthly_html(report_data)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

        # Notify all Admin users
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            notif = Notification(
                user_id=admin.id,
                title=f"Monthly Activity Report Generated ({month_str})",
                message=f"Monthly report for {month_str} has been generated. Total participants: {total_participants}, Revenue: INR {total_revenue:,.2f}.",
                notification_type='system',
                download_url=f"/api/admin/reports/download/{pdf_filename}"
            )
            db.session.add(notif)
        db.session.commit()

        emails_sent = 0
        email_failures = 0
        if app.config.get('SMTP_ENABLED'):
            for admin in admins:
                try:
                    send_email(
                        admin.email,
                        f"Monthly Activity Report - {month_str}",
                        (
                            f"Monthly report for {month_str} is ready. "
                            f"Completed treks: {completed_treks}; "
                            f"participants: {total_participants}; "
                            f"revenue: INR {total_revenue:,.2f}."
                        ),
                        html_report
                    )
                    emails_sent += 1
                except (OSError, smtplib.SMTPException, ValueError):
                    app.logger.exception(
                        'Failed to send the monthly report email to admin user id %s.',
                        admin.id
                    )
                    email_failures += 1

        print(f"[CELERY REPORT] Monthly report created: {pdf_filename}")
        return {
            'status': 'SUCCESS',
            'pdf_file': pdf_filename,
            'html_file': html_filename,
            'emails_sent': emails_sent,
            'email_failures': email_failures,
            'email_status': 'disabled' if not app.config.get('SMTP_ENABLED') else 'enabled',
            'report_data': report_data
        }

@celery_app.task(name='tasks.celery_app.export_booking_history_csv')
def export_booking_history_csv(user_id: int):
    """
    User Triggered Async Job (c): Export Booking History as CSV.
    Asynchronously extracts user's booking history into a CSV file and alerts the user.
    """
    app = get_flask_app()
    with app.app_context():
        from database import db
        from models import User, Booking, Notification

        user = db.session.get(User, user_id)
        if not user:
            return {'status': 'FAILED', 'error': 'User not found'}

        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

        os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"bookings_user_{user_id}_{timestamp}.csv"
        filepath = os.path.join(Config.EXPORTS_DIR, filename)

        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Mandatory fields specified: User ID, Trek Name, Location, Booking Status, Dates
            writer.writerow([
                'Booking ID',
                'User ID',
                'User Name',
                'Trek Name',
                'Location',
                'Difficulty',
                'Start Date',
                'End Date',
                'Booking Date',
                'Seats Booked',
                'Total Amount (INR)',
                'Booking Status',
                'Payment Status',
                'Transaction ID'
            ])

            for b in bookings:
                t = b.trek
                writer.writerow([
                    b.id,
                    user.id,
                    user.name,
                    t.name if t else 'N/A',
                    t.location if t else 'N/A',
                    t.difficulty if t else 'N/A',
                    t.start_date.isoformat() if (t and t.start_date) else 'N/A',
                    t.end_date.isoformat() if (t and t.end_date) else 'N/A',
                    b.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
                    b.num_seats,
                    b.total_amount,
                    b.status,
                    b.payment_status,
                    b.transaction_id or 'N/A'
                ])

        # Alert the user via Notification table
        download_url = f"/api/bookings/download-csv/{filename}"
        notif = Notification(
            user_id=user_id,
            title="Booking History Export Ready",
            message=f"Your booking history export containing {len(bookings)} record(s) is ready for download.",
            notification_type='export',
            download_url=download_url
        )
        db.session.add(notif)
        db.session.commit()

        print(f"[CELERY EXPORT] Exported {len(bookings)} bookings for user {user_id} to {filename}")
        return {
            'status': 'SUCCESS',
            'filename': filename,
            'download_url': download_url,
            'record_count': len(bookings)
        }
