
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _get_bool(name: str, default: str="false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1","true","yes","on")

@dataclass
class Settings:
    # Core
    mode: str = os.getenv("MODE", "paper")
    refresh_seconds: int = int(os.getenv("REFRESH_SECONDS", "60"))
    dashboard_port: int = int(os.getenv("DASHBOARD_PORT", "8080"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Logs / disk
    log_dir: str = os.getenv("LOG_DIR", "/tmp/niketbot_logs")
    log_retention_days: int = int(os.getenv("LOG_RETENTION_DAYS", "3"))

    # Caps & Limits
    investment_cap: float = float(os.getenv("INVESTMENT_CAP", "5000"))
    monthly_gain_target: float = float(os.getenv("MONTHLY_GAIN_TARGET", "2000"))
    monthly_loss_limit: float = float(os.getenv("MONTHLY_LOSS_LIMIT", "500"))
    daily_loss_limit: float = float(os.getenv("DAILY_LOSS_LIMIT", "200"))
    exit_leveraged_min_before_close: int = int(os.getenv("EXIT_LEVERAGED_MIN_BEFORE_CLOSE", "60"))
    allow_urgent_bypass: bool = _get_bool("ALLOW_URGENT_BYPASS", "true")

    # Email / IMAP
    gmail_address: str = os.getenv("GMAIL_ADDRESS", "")
    gmail_app_password: str = os.getenv("GMAIL_APP_PASSWORD", "")
    imap_host: str = os.getenv("IMAP_HOST", "imap.gmail.com")
    imap_port: int = int(os.getenv("IMAP_PORT", "993"))
    confirmation_acct_suffix: str = os.getenv("CONFIRMATION_ACCT_SUFFIX", "0647")

    # SMS
    enable_sms: bool = _get_bool("ENABLE_SMS", "false")
    twilio_sid: str = os.getenv("TWILIO_SID", "")
    twilio_token: str = os.getenv("TWILIO_TOKEN", "")
    twilio_from: str = os.getenv("TWILIO_FROM", "")
    alert_sms_to: str = os.getenv("ALERT_SMS_TO", "")

    # Optional OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Dashboard
    dashboard_refresh_sec: int = int(os.getenv("DASHBOARD_REFRESH_SEC", "15"))
    dashboard_user: str = os.getenv("DASHBOARD_USER", "")
    dashboard_pass: str = os.getenv("DASHBOARD_PASS", "")

    # Daily Summary
    enable_daily_summary: bool = _get_bool("ENABLE_DAILY_SUMMARY", "true")
    summary_hour_et: int = int(os.getenv("SUMMARY_HOUR_ET", "16"))
    summary_minute: int = int(os.getenv("SUMMARY_MINUTE", "5"))

settings = Settings()
