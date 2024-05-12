import logging
import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError as e:
            logging.error(f"Somehow there was a zero division in {func.__name__}, this should not be possible")
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {str(e)}")

    return wrapper