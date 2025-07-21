# Copyright (c) 2020, Itds Technologies and Contributors
# License: MIT. See LICENSE

import itds
from itds.core.doctype.installed_applications.installed_applications import (
	InvalidAppOrder,
	update_installed_apps_order,
)
from itds.tests import IntegrationTestCase


class TestInstalledApplications(IntegrationTestCase):
	def test_order_change(self):
		update_installed_apps_order(["itds"])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, [])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, ["itds", "deepmind"])
