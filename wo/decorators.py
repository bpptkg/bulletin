import logging
import time

logger = logging.getLogger(__name__)


def retry(max_retries=5, retry_delay=5):
    """
    Retry execution of a function if operation failed until max_retries reached.
    The function must return boolean value. True if operation succeeded,
    otherwise False if operation failed.
    """

    if int(max_retries) < 1:
        raise ValueError('max_retries value must be a positive integer '
                         'and at least 1.')

    def inner(func):
        def wrapper(*args, **kwargs):
            status = False

            for _ in range(int(max_retries)):
                status = func(*args, **kwargs)
                if status:
                    break
                else:
                    logger.error(
                        '%s function execution failed. Retrying in %ss...',
                        func.__name__,
                        retry_delay)
                    time.sleep(retry_delay)
            return status
        return wrapper
    return inner
