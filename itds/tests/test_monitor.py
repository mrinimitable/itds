# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds
import itds.monitor
from itds.monitor import MONITOR_REDIS_KEY, get_trace_id
from itds.tests import IntegrationTestCase
from itds.utils import set_request
from itds.utils.response import build_response


class TestMonitor(IntegrationTestCase):
	def setUp(self):
		itds.conf.monitor = 1
		itds.cache.delete_value(MONITOR_REDIS_KEY)

	def tearDown(self):
		itds.conf.monitor = 0
		itds.cache.delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/itds.ping")
		response = build_response("json")

		itds.monitor.start()
		itds.monitor.stop(response)

		logs = itds.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = itds.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_no_response(self):
		set_request(method="GET", path="/api/method/itds.ping")

		itds.monitor.start()
		itds.monitor.stop(response=None)

		logs = itds.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = itds.parse_json(logs[0].decode())
		self.assertEqual(log.request["status_code"], 500)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		itds.utils.background_jobs.execute_job(
			itds.local.site, "itds.ping", None, None, {}, is_async=False
		)

		logs = itds.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = itds.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "itds.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/itds.ping")
		response = build_response("json")
		itds.monitor.start()
		itds.monitor.stop(response)

		open(itds.monitor.log_file(), "w").close()
		itds.monitor.flush()

		with open(itds.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = itds.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def test_trace_ids(self):
		set_request(method="GET", path="/api/method/itds.ping")
		response = build_response("json")
		itds.monitor.start()
		itds.db.sql("select 1")
		self.assertIn(get_trace_id(), str(itds.db.last_query))
		itds.monitor.stop(response)
