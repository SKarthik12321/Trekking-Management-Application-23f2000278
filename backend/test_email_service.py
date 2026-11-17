import smtplib
import unittest
from unittest.mock import patch

from flask import Flask

from utils.email_service import send_email


class EmailServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            SMTP_ENABLED=True,
            SMTP_HOST='127.0.0.1',
            SMTP_PORT=1025,
            SMTP_USERNAME=None,
            SMTP_PASSWORD=None,
            SMTP_USE_TLS=False,
            SMTP_FROM_EMAIL='no-reply@trekflow.local',
            SMTP_FROM_NAME='TrekFlow',
            SMTP_TIMEOUT_SECONDS=10,
        )

    def test_sends_plain_and_html_message_through_smtp(self):
        with self.app.app_context(), patch('utils.email_service.smtplib.SMTP') as smtp:
            smtp.return_value.__enter__.return_value = smtp.return_value

            sent = send_email(
                'trekker@example.com',
                'Welcome',
                'Welcome to TrekFlow.',
                '<p>Welcome to TrekFlow.</p>',
                attachments=[('receipt.pdf', b'%PDF-demo', 'application', 'pdf')]
            )

        self.assertTrue(sent)
        smtp.assert_called_once_with('127.0.0.1', 1025, timeout=10)
        message = smtp.return_value.send_message.call_args.args[0]
        self.assertEqual(message['To'], 'trekker@example.com')
        self.assertEqual(message['Subject'], 'Welcome')
        self.assertEqual(message.get_body(preferencelist=('plain',)).get_content().strip(), 'Welcome to TrekFlow.')
        self.assertEqual(message.get_body(preferencelist=('html',)).get_content().strip(), '<p>Welcome to TrekFlow.</p>')
        attachment, = message.iter_attachments()
        self.assertEqual(attachment.get_filename(), 'receipt.pdf')
        self.assertEqual(attachment.get_content(), b'%PDF-demo')

    def test_disabled_smtp_does_not_attempt_delivery(self):
        self.app.config['SMTP_ENABLED'] = False
        with self.app.app_context(), patch('utils.email_service.smtplib.SMTP') as smtp:
            sent = send_email('trekker@example.com', 'Welcome', 'Welcome.')

        self.assertFalse(sent)
        smtp.assert_not_called()

    def test_supports_authenticated_starttls_smtp(self):
        self.app.config.update(
            SMTP_USERNAME='sender@example.com',
            SMTP_PASSWORD='test-app-password',
            SMTP_USE_TLS=True
        )
        with self.app.app_context(), patch('utils.email_service.smtplib.SMTP') as smtp:
            smtp.return_value.__enter__.return_value = smtp.return_value
            send_email('trekker@example.com', 'Welcome', 'Welcome.')

        smtp.return_value.starttls.assert_called_once()
        smtp.return_value.login.assert_called_once_with('sender@example.com', 'test-app-password')

    def test_smtp_errors_are_not_silently_suppressed(self):
        with self.app.app_context(), patch('utils.email_service.smtplib.SMTP') as smtp:
            smtp.return_value.__enter__.return_value = smtp.return_value
            smtp.return_value.send_message.side_effect = smtplib.SMTPException('SMTP unavailable')

            with self.assertRaises(smtplib.SMTPException):
                send_email('trekker@example.com', 'Welcome', 'Welcome.')


if __name__ == '__main__':
    unittest.main()
