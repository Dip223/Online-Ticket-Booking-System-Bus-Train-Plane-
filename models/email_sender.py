import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL, PASSWORD


def send_email(to_email, subject, otp, name="User"):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    # ================= HTML TEMPLATE =================
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f4f6f8; padding:20px;">
        <div style="max-width:500px; margin:auto; background:white; padding:25px; border-radius:12px; box-shadow:0 0 10px #ddd;">
            
            <h2 style="color:#4facfe; text-align:center;">
                🎫 Online Ticket Booking System
            </h2>

            <p>Hi <b>{name}</b>,</p>

            <p>Welcome! Please use the OTP below to verify your account:</p>

            <div style="text-align:center; margin:20px 0;">
                <span style="
                    font-size:32px;
                    font-weight:bold;
                    letter-spacing:5px;
                    color:#333;
                    background:#f1f1f1;
                    padding:10px 20px;
                    border-radius:8px;
                    display:inline-block;
                ">
                    {otp}
                </span>
            </div>

            <p style="text-align:center;">
                ⏳ This OTP will expire in <b>5 minutes</b>
            </p>

            <hr>

            <p style="font-size:12px; color:gray; text-align:center;">
                If you didn’t request this, you can safely ignore this email.
            </p>

        </div>
    </body>
    </html>
    """

    # Fallback text version (IMPORTANT for email clients)
    text = f"""
Hi {name},

Your OTP is: {otp}

This OTP will expire in 5 minutes.

If you didn't request this, ignore this email.

- Online Ticket System
"""

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # ================= SEND EMAIL =================
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully to", to_email)

    except Exception as e:
        print("❌ Email sending failed:", e)