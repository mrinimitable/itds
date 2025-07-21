# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os
import unittest
from unittest.mock import patch

import itds
from itds.tests import IntegrationTestCase


class TestPage(IntegrationTestCase):
	def test_naming(self):
		self.assertRaises(
			itds.NameError,
			itds.get_doc(doctype="Page", page_name="DocType", module="Core").insert,
		)

	@unittest.skipUnless(
		os.access(itds.get_app_path("itds"), os.W_OK), "Only run if itds app paths is writable"
	)
	@patch.dict(itds.conf, {"developer_mode": 1})
	def test_trashing(self):
		page = itds.new_doc("Page", page_name=itds.generate_hash(), module="Core").insert()

		page.delete()
		itds.db.commit()

		module_path = itds.get_module_path(page.module)
		dir_path = os.path.join(module_path, "page", itds.scrub(page.name))

		self.assertFalse(os.path.exists(dir_path))
