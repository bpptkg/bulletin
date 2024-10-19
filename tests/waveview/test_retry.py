import unittest

from waveview.retry import retry


class TestRetryDecorator(unittest.TestCase):

    def test_success_on_first_try(self):
        @retry(max_retries=3, retry_delay=1)
        def always_succeeds():
            return "success"

        self.assertEqual(always_succeeds(), "success")

    def test_success_after_retries(self):
        self.attempts = 0

        @retry(max_retries=3, retry_delay=1)
        def succeeds_after_two_tries():
            self.attempts += 1
            if self.attempts < 3:
                raise ValueError("Failing attempt")
            return "success"

        self.assertEqual(succeeds_after_two_tries(), "success")
        self.assertEqual(self.attempts, 3)

    def test_failure_after_max_retries(self):
        self.attempts = 0

        @retry(max_retries=3, retry_delay=1)
        def always_fails():
            self.attempts += 1
            raise ValueError("Always fails")

        always_fails()

        self.assertEqual(self.attempts, 3)


if __name__ == "__main__":
    unittest.main()
