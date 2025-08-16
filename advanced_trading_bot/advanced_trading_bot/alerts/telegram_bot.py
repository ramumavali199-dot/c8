import requests
from typing import Optional

def send_telegram_message(token: str, chat_id: str, text: str) -> Optional[dict]:
    """
    Sends a plain text Telegram message via Bot API.
    Returns the Telegram API response JSON (dict) or None if not sent.
    """
    if not token or not chat_id:
        print("[alerts] TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing; printing instead:\n", text)
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.ok:
            return r.json()
        else:
            print("[alerts] Telegram API error:", r.text)
            return None
    except Exception as e:
        print("[alerts] Telegram send error:", e)
        return None
