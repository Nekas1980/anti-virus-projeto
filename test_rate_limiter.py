"""
Unit tests para rate_limiter (RateLimiter + retry).
"""
from __future__ import annotations

import time
import unittest

from rate_limiter import RateLimiter, retry


class TestRateLimiter(unittest.TestCase):
    def test_invalid_max_per_minute_raises(self):
        with self.assertRaises(ValueError):
            RateLimiter(0)

    def test_acquire_enforces_min_interval(self):
        rl = RateLimiter(max_per_minute=120)
        start = time.monotonic()
        rl.acquire()
        rl.acquire()
        elapsed = time.monotonic() - start
        self.assertGreaterEqual(elapsed, rl.min_interval - 0.01)

    def test_context_manager(self):
        rl = RateLimiter(max_per_minute=600)
        with rl:
            pass


class TestRetryDecorator(unittest.TestCase):
    def test_succeeds_on_first_try(self):
        calls = []

        @retry(max_attempts=3, base_delay=0.001)
        def fn():
            calls.append(1)
            return "ok"

        self.assertEqual(fn(), "ok")
        self.assertEqual(len(calls), 1)

    def test_retries_then_succeeds(self):
        calls = []

        @retry(max_attempts=3, base_delay=0.001)
        def fn():
            calls.append(1)
            if len(calls) < 3:
                raise ValueError("fail")
            return "ok"

        self.assertEqual(fn(), "ok")
        self.assertEqual(len(calls), 3)

    def test_raises_after_exhausting_attempts(self):
        @retry(max_attempts=2, base_delay=0.001, exceptions=(ValueError,))
        def fn():
            raise ValueError("always fails")

        with self.assertRaises(ValueError):
            fn()

    def test_does_not_retry_unmatched_exception(self):
        calls = []

        @retry(max_attempts=3, base_delay=0.001, exceptions=(ValueError,))
        def fn():
            calls.append(1)
            raise TypeError("not retryable")

        with self.assertRaises(TypeError):
            fn()
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
