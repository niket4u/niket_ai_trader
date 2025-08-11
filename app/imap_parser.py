
import imaplib, email, re
from datetime import datetime, timezone
from .config import settings

CONFIRM_RE = re.compile(r"Account\s+\*+([0-9]{4})", re.IGNORECASE)

def fetch_confirmations(limit: int = 50):
    if not settings.gmail_address or not settings.gmail_app_password:
        return []
    M = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    M.login(settings.gmail_address, settings.gmail_app_password)
    M.select("INBOX")
    typ, data = M.search(None, 'ALL')
    ids = data[0].split()[-limit:]
    events = []
    for i in ids[::-1]:
        typ, msg_data = M.fetch(i, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                if ct in ("text/plain","text/html"):
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        m = CONFIRM_RE.search(body)
        if not m:
            continue
        suffix = m.group(1)
        if suffix != settings.confirmation_acct_suffix:
            continue
        events.append({"date": datetime.now(timezone.utc).isoformat(),
                       "subject": msg.get("Subject",""),
                       "from": msg.get("From","")})
    M.logout()
    return events
