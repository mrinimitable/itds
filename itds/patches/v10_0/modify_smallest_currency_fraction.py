# Copyright (c) 2018, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
