# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.reload_doc("core", "doctype", "DocField")

	if itds.db.has_column("DocField", "show_days"):
		itds.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		itds.db.sql_ddl("alter table tabDocField drop column show_days")

	if itds.db.has_column("DocField", "show_seconds"):
		itds.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		itds.db.sql_ddl("alter table tabDocField drop column show_seconds")

	itds.clear_cache(doctype="DocField")
