import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from flask import current_app


def send_email(to_email, subject, text_body, html_body=None, attachments=None):
    """Send an email through the configured SMTP server; return False when disabled."""
    config = current_app.config
    if not config.get('SMTP_ENABLED'):
        return False

    host = config.get('SMTP_HOST')
    from_email = config.get('SMTP_FROM_EMAIL')
    username = config.get('SMTP_USERNAME')
    password = config.get('SMTP_PASSWORD')

    if not host or not from_email:
        raise ValueError('SMTP_HOST and SMTP_FROM_EMAIL are required when SMTP is enabled.')
    if bool(username) != bool(password):
        raise ValueError('SMTP_USERNAME and SMTP_PASSWORD must either both be set or both be empty.')

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = formataddr((config.get('SMTP_FROM_NAME', 'TrekFlow'), from_email))
    message['To'] = to_email
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype='html')
    for filename, content, maintype, subtype in attachments or ():
        message.add_attachment(
            content,
            maintype=maintype,
            subtype=subtype,
            filename=filename
        )

    with smtplib.SMTP(
        host,
        config.get('SMTP_PORT', 1025),
        timeout=config.get('SMTP_TIMEOUT_SECONDS', 10)
    ) as server:
        if config.get('SMTP_USE_TLS'):
            server.starttls(context=ssl.create_default_context())
        if username:
            server.login(username, password)
        server.send_message(message)
    return True
