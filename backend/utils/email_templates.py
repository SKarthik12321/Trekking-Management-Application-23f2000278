from html import escape


def build_welcome_email(name, username):
    safe_name = escape(name)
    safe_username = escape(username)
    subject = 'Welcome to TrekFlow'
    text_body = (
        f"Hello {name},\n\n"
        "Welcome to TrekFlow. Your trekker account is ready.\n"
        f"Your username is {username}. You can now explore treks, book a place, "
        "and review your trekking history.\n\n"
        "This is an automated message; please do not reply."
    )
    html_body = f"""\
<!doctype html>
<html>
  <body style="margin:0;padding:24px;background:#f3f6f4;font-family:Arial,sans-serif;color:#20312b;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;">
      <tr>
        <td style="padding:28px 32px;background:#174b3a;color:#ffffff;">
          <div style="font-size:13px;letter-spacing:2px;text-transform:uppercase;color:#c5e8d6;">TrekFlow</div>
          <h1 style="margin:12px 0 0;font-size:26px;line-height:1.25;">Welcome to the trail, {safe_name}!</h1>
        </td>
      </tr>
      <tr>
        <td style="padding:28px 32px;">
          <p style="margin:0 0 16px;font-size:16px;line-height:1.6;">Your trekker account is ready. You can now discover routes, reserve trek slots, and keep your trip details together.</p>
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f8f5;border:1px solid #dcebe2;border-radius:10px;">
            <tr><td style="padding:16px 18px;font-size:14px;line-height:1.8;">
              <strong>Username</strong><br>{safe_username}<br>
              <strong>Next steps</strong><br>Browse open treks, check the dates and available slots, then book when you are ready.
            </td></tr>
          </table>
          <p style="margin:22px 0 0;font-size:13px;line-height:1.6;color:#62736b;">For your security, this email does not contain your password. This is an automated message; please do not reply.</p>
        </td>
      </tr>
      <tr><td style="padding:16px 32px;background:#f7f9f8;color:#718078;font-size:12px;">TrekFlow | Trekking Management Application</td></tr>
    </table>
  </body>
</html>"""
    return subject, text_body, html_body


def build_booking_confirmation_email(booking):
    subject = f"TrekFlow booking confirmed - #{booking['booking_id']}"
    text_body = (
        f"Hello {booking['user_name']},\n\n"
        f"Your booking for {booking['trek_name']} is confirmed.\n"
        f"Location: {booking['location']}\n"
        f"Dates: {booking['start_date']} to {booking['end_date']}\n"
        f"Seats: {booking['num_seats']}\n"
        f"Participants: {booking['participant_names']}\n"
        f"Amount: INR {booking['total_amount']:,.2f}\n"
        f"Payment method: {booking['payment_method']}\n"
        f"Transaction ID: {booking['transaction_id']}\n\n"
        "Payment is simulated for this demo; no real charge was made. "
        "Your booking receipt is attached as a PDF."
    )

    details = (
        ('Booking ID', booking['booking_id']),
        ('Trek', booking['trek_name']),
        ('Location', booking['location']),
        ('Difficulty', booking['difficulty']),
        ('Trek dates', f"{booking['start_date']} to {booking['end_date']}"),
        ('Seats', booking['num_seats']),
        ('Participants', booking['participant_names']),
        ('Payment method', booking['payment_method']),
        ('Payment status', f"{booking['payment_status']} (demo)"),
        ('Transaction ID', booking['transaction_id']),
    )
    detail_rows = ''.join(
        f"""<tr>
          <td style="padding:10px 12px;border-bottom:1px solid #e6eee9;color:#62736b;font-size:13px;">{escape(str(label))}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #e6eee9;color:#20312b;font-size:13px;font-weight:600;">{escape(str(value))}</td>
        </tr>"""
        for label, value in details
    )
    safe_name = escape(str(booking['user_name']))
    amount = escape(f"INR {booking['total_amount']:,.2f}")
    html_body = f"""\
<!doctype html>
<html>
  <body style="margin:0;padding:24px;background:#f3f6f4;font-family:Arial,sans-serif;color:#20312b;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;">
      <tr>
        <td style="padding:26px 30px;background:#174b3a;color:#ffffff;">
          <div style="font-size:13px;letter-spacing:2px;text-transform:uppercase;color:#c5e8d6;">TrekFlow</div>
          <h1 style="margin:12px 0 0;font-size:25px;line-height:1.25;">Booking confirmed</h1>
          <p style="margin:8px 0 0;color:#e3f2e9;font-size:14px;">Booking #{escape(str(booking['booking_id']))}</p>
        </td>
      </tr>
      <tr>
        <td style="padding:26px 30px;">
          <p style="margin:0 0 18px;font-size:15px;line-height:1.6;">Hi {safe_name}, your place on <strong>{escape(str(booking['trek_name']))}</strong> is reserved.</p>
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;border:1px solid #e6eee9;">
            {detail_rows}
          </table>
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-top:18px;background:#edf7f0;border-radius:10px;">
            <tr><td style="padding:16px 18px;">
              <div style="font-size:12px;color:#52705f;text-transform:uppercase;letter-spacing:1px;">Total (demo payment)</div>
              <div style="margin-top:4px;font-size:23px;font-weight:700;color:#174b3a;">{amount}</div>
            </td></tr>
          </table>
          <p style="margin:18px 0 0;padding:12px 14px;background:#fff8e7;border-left:4px solid #e1ad45;font-size:12px;line-height:1.6;color:#6b582c;">
            Payment is simulated for this project demo. No real payment was processed or charged. Your PDF receipt is attached.
          </p>
          <p style="margin:20px 0 0;font-size:12px;color:#718078;">This is an automated message; please do not reply.</p>
        </td>
      </tr>
      <tr><td style="padding:16px 30px;background:#f7f9f8;color:#718078;font-size:12px;">TrekFlow | Trekking Management Application</td></tr>
    </table>
  </body>
</html>"""
    return subject, text_body, html_body
