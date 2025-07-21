# Copyright (c) 2018, Itds Technologies and Contributors
# License: MIT. See LICENSE
import itds
from itds.tests import IntegrationTestCase


class TestViewLog(IntegrationTestCase):
	def tearDown(self):
		itds.set_user("Administrator")

	def test_if_user_is_added(self):
		ev = itds.get_doc(
			{
				"doctype": "Event",
				"subject": "test event for view logs",
				"starts_on": "2018-06-04 14:11:00",
				"event_type": "Public",
			}
		).insert()

		itds.set_user("test@example.com")

		from itds.desk.form.load import getdoc

		# load the form
		getdoc("Event", ev.name)
		a = itds.get_value(
			doctype="View Log",
			filters={"reference_doctype": "Event", "reference_name": ev.name},
			fieldname=["viewed_by"],
		)

		self.assertEqual("test@example.com", a)
		self.assertNotEqual("test1@example.com", a)
