# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# pre loaded

import itds
from itds.tests import IntegrationTestCase


class TestUser(IntegrationTestCase):
	def test_default_currency_on_setup(self):
		usd = itds.get_doc("Currency", "USD")
		self.assertDocumentEqual({"enabled": 1, "fraction": "Cent"}, usd)
