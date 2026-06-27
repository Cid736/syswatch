import os
import logging
import requests

log = logging.getLogger(__name__)


def send(msg: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat  = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"},
            timeout=10,
        )
        if not resp.ok:
            log.warning("[syswatch] Telegram API error %s: %s", resp.status_code, resp.text[:200])
    except Exception as exc:
        log.warning("[syswatch] Failed to send Telegram alert: %s", exc)


def alert(hostname: str, issues: list[str]):
    lines = "\n".join(f"  • {i}" for i in issues)
    send(f"⚠️ *syswatch alert* — `{hostname}`\n{lines}")
