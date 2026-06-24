import os
import requests


def send(msg: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat  = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception:
        pass


def alert(hostname: str, issues: list[str]):
    lines = "\n".join(f"  • {i}" for i in issues)
    send(f"⚠️ *syswatch alert* — `{hostname}`\n{lines}")
