import itds
from itds import format
from itds.tests import IntegrationTestCase


class TestFormatter(IntegrationTestCase):
	def test_currency_formatting(self):
		df = itds._dict({"fieldname": "amount", "fieldtype": "Currency", "options": "currency"})

		doc = itds._dict({"amount": 5})
		itds.db.set_default("currency", "INR")

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "₹ 100,000.00")

		doc.currency = "USD"
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "$ 100,000.00")

		itds.db.set_default("currency", None)
