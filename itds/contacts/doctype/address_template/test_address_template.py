# Copyright (c) 2015, Itds Technologies and Contributors
# License: MIT. See LICENSE
import itds
from itds.contacts.doctype.address_template.address_template import get_default_address_template
from itds.tests import IntegrationTestCase
from itds.utils.jinja import validate_template


class TestAddressTemplate(IntegrationTestCase):
	def setUp(self) -> None:
		itds.db.delete("Address Template", {"country": "India"})
		itds.db.delete("Address Template", {"country": "Brazil"})

	def test_default_address_template(self):
		validate_template(get_default_address_template())

	def test_default_is_unset(self):
		itds.get_doc({"doctype": "Address Template", "country": "India", "is_default": 1}).insert()

		self.assertEqual(itds.db.get_value("Address Template", "India", "is_default"), 1)

		itds.get_doc({"doctype": "Address Template", "country": "Brazil", "is_default": 1}).insert()

		self.assertEqual(itds.db.get_value("Address Template", "India", "is_default"), 0)
		self.assertEqual(itds.db.get_value("Address Template", "Brazil", "is_default"), 1)

	def test_delete_address_template(self):
		india = itds.get_doc({"doctype": "Address Template", "country": "India", "is_default": 0}).insert()

		brazil = itds.get_doc(
			{"doctype": "Address Template", "country": "Brazil", "is_default": 1}
		).insert()

		india.reload()  # might have been modified by the second template
		india.delete()  # should not raise an error

		self.assertRaises(itds.ValidationError, brazil.delete)
