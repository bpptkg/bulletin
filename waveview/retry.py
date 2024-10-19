import logging
import time

logger = logging.getLogger(__name__)


def retry(max_retries=5, retry_delay=5):
    """
    Retry execution of a function if operation failed until max_retries reached.
    """

    if int(max_retries) < 1:
        raise ValueError("max_retries value must be a positive integer and at least 1.")

    def inner(func):
        def wrapper(*args, **kwargs):
            for _ in range(int(max_retries)):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        "%s function execution failed: %s. Retrying in %ss...",
                        func.__name__,
                        e,
                        retry_delay,
                    )
                    time.sleep(retry_delay)

        return wrapper

    return inner
