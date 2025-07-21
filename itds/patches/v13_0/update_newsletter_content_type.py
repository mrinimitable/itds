# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.reload_doc("email", "doctype", "Newsletter")
	itds.db.sql(
		"""
		UPDATE tabNewsletter
		SET content_type = 'Rich Text'
	"""
	)
