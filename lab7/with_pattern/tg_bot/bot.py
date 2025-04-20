from dotenv import find_dotenv, load_dotenv
import requests
import time
import os


load_dotenv(find_dotenv())
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(f"{API_URL}/getUpdates", params=params)
        return response.json().get("result", [])
    except Exception as e:
        print(f"Ошибка при получении обновлений: {e}")
        return []


def send_message(chat_id, text):
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(f"{API_URL}/sendMessage", data=data)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


def bot_dispatcher():
    last_update_id = 0
    while True:
        updates = get_updates(offset=last_update_id + 1)

        for update in updates:
            last_update_id = update["update_id"]

            if "message" not in update:
                continue

            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            if text == "/whoami":
                user_id = message["from"]["id"]
                send_message(chat_id, f"Ваш ID: {user_id}")

        time.sleep(1)


if __name__ == "__main__":
    bot_dispatcher()
