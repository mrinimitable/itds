# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import time

from werkzeug.wrappers import Response

import itds
import itds.rate_limiter
from itds.rate_limiter import RateLimiter
from itds.tests import IntegrationTestCase
from itds.utils import cint


class TestRateLimiter(IntegrationTestCase):
	def test_apply_with_limit(self):
		itds.conf.rate_limit = {"window": 86400, "limit": 1}
		itds.rate_limiter.apply()

		self.assertTrue(hasattr(itds.local, "rate_limiter"))
		self.assertIsInstance(itds.local.rate_limiter, RateLimiter)

		itds.cache.delete(itds.local.rate_limiter.key)
		delattr(itds.local, "rate_limiter")

	def test_apply_without_limit(self):
		itds.conf.rate_limit = None
		itds.rate_limiter.apply()

		self.assertFalse(hasattr(itds.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(1, 86400)
		time.sleep(1)
		limiter.update()

		itds.conf.rate_limit = {"window": 86400, "limit": 1}
		self.assertRaises(itds.TooManyRequestsError, itds.rate_limiter.apply)
		itds.rate_limiter.update()

		response = itds.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = itds.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		itds.cache.delete(limiter.key)
		itds.cache.delete(itds.local.rate_limiter.key)
		delattr(itds.local, "rate_limiter")

	def test_respond_under_limit(self):
		itds.conf.rate_limit = {"window": 86400, "limit": 0.01}
		itds.rate_limiter.apply()
		itds.rate_limiter.update()
		response = itds.rate_limiter.respond()
		self.assertEqual(response, None)

		itds.cache.delete(itds.local.rate_limiter.key)
		delattr(itds.local, "rate_limiter")

	def test_headers_under_limit(self):
		itds.conf.rate_limit = {"window": 86400, "limit": 1}
		itds.rate_limiter.apply()
		itds.rate_limiter.update()
		headers = itds.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 1000000)

		itds.cache.delete(itds.local.rate_limiter.key)
		delattr(itds.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(itds.TooManyRequestsError, limiter.apply)

		itds.cache.delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		itds.cache.delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(itds.cache.get(limiter.key)))

		itds.cache.delete(limiter.key)

	def test_window_expires(self):
		limiter = RateLimiter(1000, 1)
		self.assertTrue(itds.cache.exists(limiter.key, shared=True))
		limiter.update()
		self.assertTrue(itds.cache.exists(limiter.key, shared=True))
		time.sleep(1.1)
		self.assertFalse(itds.cache.exists(limiter.key, shared=True))
		itds.cache.delete(limiter.key)
