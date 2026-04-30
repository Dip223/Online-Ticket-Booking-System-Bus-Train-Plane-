import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL, PASSWORD


def send_email(to_email: str, subject: str, otp: str, name: str = "User") -> None:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"BD Ticket <{EMAIL}>"
        msg["To"]      = to_email

        html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;">
  <div style="max-width:520px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.10);">
    <div style="background:linear-gradient(135deg,#0d1b2a 0%,#1a3a2a 100%);padding:36px 32px;text-align:center;">
      <div style="display:inline-flex;align-items:center;gap:10px;background:rgba(255,255,255,.07);border-radius:12px;padding:10px 20px;">
        <span style="font-size:22px;">🎫</span>
        <span style="font-size:20px;font-weight:900;color:#fff;letter-spacing:-.5px;">BD<span style="color:#1db954;">Ticket</span></span>
      </div>
      <p style="color:rgba(255,255,255,.55);margin:12px 0 0;font-size:13px;letter-spacing:.5px;text-transform:uppercase;">Secure Verification</p>
    </div>
    <div style="padding:36px 32px;">
      <p style="font-size:16px;color:#2d3748;margin:0 0 6px;">Hi <strong>{name}</strong> 👋</p>
      <p style="font-size:14px;color:#718096;line-height:1.7;margin:0 0 28px;">Use the one-time code below to verify your identity. This code is valid for <strong>5 minutes</strong> and can only be used once.</p>
      <div style="background:#f0fff4;border:2px solid #9ae6b4;border-radius:14px;padding:30px;text-align:center;margin-bottom:24px;">
        <p style="font-size:11px;font-weight:800;color:#276749;letter-spacing:3px;text-transform:uppercase;margin:0 0 14px;">Your Verification Code</p>
        <div style="font-size:46px;font-weight:900;color:#1db954;letter-spacing:14px;font-family:monospace;line-height:1;">{otp}</div>
      </div>
      <div style="background:#fffbeb;border-left:4px solid #f6ad55;border-radius:8px;padding:14px 18px;margin-bottom:20px;">
        <p style="color:#744210;font-size:13px;margin:0;font-weight:600;">🔒 Never share this code. BD Ticket staff will never ask for your OTP.</p>
      </div>
      <p style="font-size:12px;color:#a0aec0;text-align:center;margin:0;">If you didn't request this, please ignore this email safely.</p>
    </div>
    <div style="background:#f7fafc;padding:18px 32px;border-top:1px solid #e2e8f0;text-align:center;">
      <p style="font-size:12px;color:#a0aec0;margin:0;">© 2024 BD Ticket · Bangladesh's Trusted Booking Platform</p>
    </div>
  </div>
</body>
</html>"""

        plain = f"Hi {name},\n\nYour BD Ticket OTP is: {otp}\n\nExpires in 5 minutes. Do not share.\n\n— BD Ticket Team"

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent → {to_email}")

    except Exception as e:
        print(f"❌ Email error: {e}")