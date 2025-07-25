# Copyright (c) 2022, Itds Technologies and Contributors
# See license.txt

import itds
from itds.core.doctype.rq_worker.rq_worker import RQWorker
from itds.tests import IntegrationTestCase


class TestRQWorker(IntegrationTestCase):
	def test_get_worker_list(self):
		workers = RQWorker.get_list()
		self.assertGreaterEqual(len(workers), 1)
		self.assertTrue(any("short" in w.queue_type for w in workers))

	def test_worker_serialization(self):
		workers = RQWorker.get_list()
		itds.get_doc("RQ Worker", workers[0].name)
