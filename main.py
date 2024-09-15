import llama
import product_hunt
import telegram


def start():
    posts, total_count = product_hunt.get_posts()

    for post in posts:
        post["tagline_ru"] = llama.translate_to_russian(post["tagline"])
        print("Ollama handled the post", post["name"])

    if posts:
        telegram.send_posts(total_count, posts)
    else:
        telegram.send_message_to_telegram("No post for today")


if __name__ == '__main__':
    start()
