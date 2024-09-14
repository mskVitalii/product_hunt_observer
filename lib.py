import time

from requests import RequestException


def retry(retries: list[int]):
    def wrapper(func):
        def wrapper_retry(*args, **kwargs):
            for seconds in retries:
                try:
                    return func(*args, **kwargs)
                except RequestException:
                    print(f"Failed to get data. Retrying in {seconds} seconds")
                    time.sleep(seconds)
            return func(*args, **kwargs)

        return wrapper_retry

    return wrapper
