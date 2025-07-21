# Copyright (c) 2024, Itds Technologies and Contributors
# See license.txt

import itds
from itds.tests import IntegrationTestCase


class TestSystemHealthReport(IntegrationTestCase):
	def test_it_works(self):
		itds.get_doc("System Health Report")
