import os
import requests
from dotenv import load_dotenv
import sys

# Load environment variables from .env in the same folder
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CLIENT_CHAT_ID")
GEMINI_KEY = os.getenv("MODEL_API_KEY")
GEMINI_MODEL = os.getenv("MODEL_NAME")
GEMINI_BASE = os.getenv("MODEL_API_BASE")

LAST_UPDATE_FILE = "last_update_id.txt"


def load_last_update_id():
    try:
        with open(LAST_UPDATE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def save_last_update_id(update_id):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(update_id))


def get_recent_messages(limit=10):
    params = {}
    last_update_id = load_last_update_id()
    if last_update_id is not None:
        # Only get updates after the last one we processed
        params["offset"] = last_update_id + 1

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    resp = requests.get(url, params=params)
    data = resp.json()

    messages = []
    max_update_id = last_update_id

    for update in data.get("result", []):
        update_id = update.get("update_id")
        if max_update_id is None or (update_id is not None and update_id > max_update_id):
            max_update_id = update_id

        msg = update.get("message") or update.get("edited_message")
        if not msg:
            continue

        chat = msg.get("chat", {})
        if str(chat.get("id")) != str(CHAT_ID):
            continue

        text = msg.get("text")
        if not text:
            continue

        messages.append(text)

    # Remember the highest update_id so we don't see these again next run
    if max_update_id is not None:
        save_last_update_id(max_update_id)

    # Limit to the last N messages from this run
    return messages[-limit:]


def summarize_with_gemini(messages, mode="daily"):
    if not messages:
        return "No messages to summarise today."


    if mode == "weekly":


        content = (
            "You are an executive briefing assistant for a retired senior corporate leader.\n"
            "This week, he sent you a set of Telegram messages containing links and articles that caught his attention.\n"
            "Each item may contain:\n"
            "- one or more URLs (links or articles)\n"
            "- some free-text notes about why it interested him\n\n"
            "Important:\n"
            "- The items are informal and not guaranteed to follow any fixed format.\n"
            "- When possible, treat anything that looks like a URL as the link.\n"
            "- Treat the remaining text in that item as his note/context.\n\n"
            "Your task:\n"
            "1. First, write a short 2–3 sentence overview under the heading \"Summary\" that explains what this week's links and articles are broadly about.\n"
            "2. Then identify 2–4 main themes that run across this week's links and notes.\n"
            "3. For each theme, write:\n"
            "   - a short theme title\n"
            "   - 2–4 bullet points explaining what the links and notes say about this theme, "
            "in calm, clear language.\n"
            "4. When helpful, use his notes to infer why a link or article mattered to him "
            "(for example, India context, investing angle, or leadership/management lens) "
            "and reflect that in the wording.\n"
            "5. After the themes, add a section titled \"Questions to consider\" with 2–4 reflective questions "
            "he might use for reflection or future reading.\n"
            "6. If there are any clear practical follow-ups suggested by the material, you may optionally add "
            "a very short \"Possible actions\" section with 1–3 bullet points; if not, omit this section.\n"
            "7. Keep the total length under 600 words.\n"
            "8. Write in a concise, non‑jargony tone suitable for someone who has been a CEO or senior leader "
            "but is now retired and exploring ideas.\n\n"
            "Here is this week's list of items (each line is one Telegram item he sent, often a link plus a note):\n"
        )

        for i, m in enumerate(messages, 1):
            content += f"{i}. {m}\n"

        url = f"{GEMINI_BASE}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": content}
                    ]
                }
            ]
        }
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return f"Gemini response could not be parsed: {data}"


    else:
    # default: daily
        content = (
                "You are an executive briefing assistant for a retired senior corporate leader.\n"
                "Today, he sent you a set of Telegram messages containing links and articles that caught his attention.\n"
                "Each item may contain:\n"
                "- one or more URLs (links or articles)\n"
                "- some free-text notes about why it interested him\n\n"
                "Important:\n"
                "- The items are informal and not guaranteed to follow any fixed format.\n"
                "- When possible, treat anything that looks like a URL as the link.\n"
                "- Treat the remaining text in that item as his note/context.\n\n"
                "Your task:\n"
                "1. First, write a short 2–3 sentence overview under the heading \"Summary\" that explains what today's links and articles are broadly about.\n"
                "2. Then identify 2–4 main themes that run across today's links and notes.\n"
                "3. For each theme, write:\n"
                "   - a short theme title\n"
                "   - 2–4 bullet points explaining what the links and notes say about this theme, "
                "in calm, clear language.\n"
                "4. When helpful, use his notes to infer why a link or article mattered to him "
                "(for example, India context, investing angle, or leadership/management lens) "
                "and reflect that in the wording.\n"
                "5. After the themes, add a section titled \"Questions to consider\" with 2–4 reflective questions "
                "he might use for reflection or future reading.\n"
                "6. If there are any clear practical follow-ups suggested by the material, you may optionally add "
                "a very short \"Possible actions\" section with 1–3 bullet points; if not, omit this section.\n"
                "7. Keep the total length under 450 words.\n"
                "8. Write in a concise, non‑jargony tone suitable for someone who has been a CEO or senior leader "
                "but is now retired and exploring ideas.\n\n"
                "Here is today's list of items (each line is one Telegram item he sent, often a link plus a note):\n"
            )

        for i, m in enumerate(messages, 1):
            content += f"{i}. {m}\n"

        url = f"{GEMINI_BASE}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
        payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": content}
                        ]
                    }
                ]
            }
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return f"Gemini response could not be parsed: {data}"











def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)


if __name__ == "__main__":
    mode = "daily"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

    msgs = get_recent_messages(limit=25)

    recap = summarize_with_gemini(msgs, mode=mode)

    if mode == "weekly":
        send_message("Here is your weekly briefing:\n\n" + recap)
    if mode == "daily":
        send_message("Here is your daily briefing:\n\n" + recap)
