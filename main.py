import product_hunt
import telegram


def start():
    posts, total_count = product_hunt.get_posts()

    if posts:
        telegram.send_posts(total_count, posts)
    else:
        telegram.send_message_to_telegram("No post for today")


if __name__ == '__main__':
    start()
