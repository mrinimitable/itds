# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	"""Enable all the existing Client script"""

	itds.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
