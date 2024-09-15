import os

import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
MAX_MESSAGE_LENGTH = 4096


def send_posts(total_count: int, posts: list):
    current_message = f"<b>Today's Product Hunt Projects ({total_count}):</b>\n\n"
    for index, post in enumerate(posts, start=1):
        post_message = format_post(index, post)

        if len(current_message) + len(post_message) < MAX_MESSAGE_LENGTH:
            current_message += post_message
        else:
            send_message_to_telegram(current_message)
            current_message = post_message

    if current_message:
        send_message_to_telegram(current_message)


def format_post(index: int, post: dict) -> str:
    return f"""
<a href="{post['url']}"><b>{index}. {post['name']}</b></a>
{post['tagline']}
<blockquote>{post['tagline_ru']}</blockquote>
"""


def send_message_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {response.status_code}, {response.text}")
