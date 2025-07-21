# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	if not itds.db.table_exists("Data Import"):
		return

	meta = itds.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	itds.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	itds.rename_doc("DocType", "Data Import", "Data Import Legacy")
	itds.db.commit()
	itds.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	itds.rename_doc("DocType", "Data Import Beta", "Data Import")
