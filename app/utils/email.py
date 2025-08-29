from email.mime.text import MIMEText

import aiosmtplib

from app.config.main import settings


async def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body, "html")
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
