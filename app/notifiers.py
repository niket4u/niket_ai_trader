
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings

def send_email(subject: str, html_body: str, to_addrs: list[str] | None = None):
    if not settings.gmail_address or not settings.gmail_app_password:
        return
    to_addrs = to_addrs or [settings.gmail_address]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.gmail_address
    msg["To"] = ", ".join(to_addrs)

    part = MIMEText(html_body, "html")
    msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(settings.gmail_address, settings.gmail_app_password)
        server.sendmail(settings.gmail_address, to_addrs, msg.as_string())

def send_sms(body: str):
    if not settings.enable_sms:
        return
    from twilio.rest import Client
    client = Client(settings.twilio_sid, settings.twilio_token)
    client.messages.create(to=settings.alert_sms_to, from_=settings.twilio_from, body=body)
