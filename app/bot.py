
import time, csv, os, json
from datetime import datetime, timezone, timedelta
import pandas as pd
from .config import settings
from .logging_utils import get_logger, ensure_log_dir
from .data_provider import get_history
from .strategies.registry import get_strategy
from .portfolio import Portfolio
from .notifiers import send_email, send_sms
from .imap_parser import fetch_confirmations

logger = get_logger("bot")

STATE_PATH = os.path.join(settings.log_dir, "state.json")
LAST_SUMMARY_FLAG = os.path.join(settings.log_dir, ".last_summary_date")

def load_tickers_csv(path="data/tickers.csv"):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def alert_html(message: str) -> str:
    return f"<html><body><pre style='font-size:14px'>{message}</pre></body></html>"

def write_state(portfolio: Portfolio, last_run_utc: str, notes: str=""):
    ensure_log_dir()
    positions = {k: {"qty": v.qty, "cost_basis": v.cost_basis} for k,v in portfolio.positions.items()}
    state = {
        "mode": settings.mode,
        "last_run_utc": last_run_utc,
        "caps": {
            "investment_cap": settings.investment_cap,
            "cash_spent": portfolio.cash_spent,
            "pnl_day": portfolio.realized_pnl_day,
            "pnl_month": portfolio.realized_pnl_month
        },
        "positions": positions,
        "notes": notes
    }
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def should_send_daily_summary(now_utc: datetime) -> bool:
    if not settings.enable_daily_summary:
        return False
    # Convert ET to UTC: ET = UTC-4 (no DST logic here; simple for Phase-2 test)
    target_hour_utc = settings.summary_hour_et + 4  # crude; works in EDT
    if target_hour_utc >= 24:
        target_hour_utc -= 24
    if now_utc.hour == target_hour_utc and now_utc.minute >= settings.summary_minute and now_utc.minute <= settings.summary_minute + 2:
        # Check last summary date flag
        today = now_utc.strftime("%Y-%m-%d")
        if os.path.exists(LAST_SUMMARY_FLAG):
            with open(LAST_SUMMARY_FLAG, "r") as f:
                if f.read().strip() == today:
                    return False
        with open(LAST_SUMMARY_FLAG, "w") as f:
            f.write(today)
        return True
    return False

def send_daily_summary():
    if not os.path.exists(STATE_PATH):
        return
    with open(STATE_PATH, "r") as f:
        state = json.load(f)
    html = f"""<h3>NiketBot Daily Summary ({state.get('mode','')})</h3>
    <p><b>Last Run (UTC):</b> {state.get('last_run_utc','')}</p>
    <ul>
      <li>Cash Spent: {state['caps'].get('cash_spent',0):.2f}</li>
      <li>PnL Day: {state['caps'].get('pnl_day',0):.2f}</li>
      <li>PnL Month: {state['caps'].get('pnl_month',0):.2f}</li>
    </ul>
    <pre>{json.dumps(state.get('positions',{}), indent=2)}</pre>
    """
    send_email("NiketBot Daily Summary", html)

def run_once(portfolio: Portfolio):
    tickers = load_tickers_csv()
    for row in tickers:
        tkr = row["ticker"].strip().upper()
        strat_name = row.get("strategy", "ma_crossover")
        strat = get_strategy(strat_name)

        df = get_history(tkr, period="6mo", interval="1d")
        sig = strat(df)  # +1 buy, -1 sell, 0 none
        latest = float(df.tail(1)["close"].values[0])

        # Near-close leveraged heuristic (UTC ~19 = 3pm ET)
        now = datetime.utcnow()
        if ("2X" in tkr or "3X" in tkr) and now.hour >= 19:
            logger.info(f"Skipping leveraged {tkr} near close due to rule.")
            continue

        if sig > 0:
            budget_each = min(500.0, settings.investment_cap - portfolio.cash_spent)
            qty = max(1, int(budget_each // latest)) if budget_each > 0 else (1 if settings.allow_urgent_bypass else 0)
            if qty > 0:
                portfolio.apply_buy(tkr, qty, latest)
                msg = f"[{settings.mode.upper()}] BUY {tkr} x {qty} @ {latest:.2f} | cash_spent={portfolio.cash_spent:.2f}"
                logger.info(msg); send_email(f"NiketBot BUY {tkr}", alert_html(msg)); send_sms(msg)
        elif sig < 0 and tkr in portfolio.positions:
            qty = portfolio.positions[tkr].qty
            if qty > 0:
                portfolio.apply_sell(tkr, qty, latest)
                msg = f"[{settings.mode.upper()}] SELL {tkr} x {qty} @ {latest:.2f} | realized_day={portfolio.realized_pnl_day:.2f}"
                logger.info(msg); send_email(f"NiketBot SELL {tkr}", alert_html(msg)); send_sms(msg)

        if portfolio.breach_daily_loss():
            send_email("NiketBot DAILY LOSS LIMIT BREACH", alert_html(f"PnL day = {portfolio.realized_pnl_day:.2f}"))
        if portfolio.breach_monthly_loss():
            send_email("NiketBot MONTHLY LOSS LIMIT BREACH", alert_html(f"PnL month = {portfolio.realized_pnl_month:.2f}"))
        if portfolio.reached_monthly_gain():
            send_email("NiketBot MONTHLY GAIN TARGET REACHED", alert_html(f"PnL month = {portfolio.realized_pnl_month:.2f}"))

    confirmations = fetch_confirmations(limit=20)
    if confirmations:
        logger.info(f"Parsed {len(confirmations)} confirmations (acct suffix {settings.confirmation_acct_suffix}).")

    write_state(portfolio, datetime.utcnow().isoformat())

def main_loop():
    logger.info(f"Starting NiketBot | mode={settings.mode} refresh={settings.refresh_seconds}s")
    portfolio = Portfolio()
    while True:
        try:
            run_once(portfolio)
            now_utc = datetime.utcnow()
            if should_send_daily_summary(now_utc):
                send_daily_summary()
        except Exception as e:
            logger.exception(f"Run error: {e}")
        time.sleep(settings.refresh_seconds)

if __name__ == "__main__":
    main_loop()
