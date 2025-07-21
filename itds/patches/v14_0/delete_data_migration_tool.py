# Copyright (c) 2022, Itds Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import itds


def execute():
	doctypes = itds.get_all("DocType", {"module": "Data Migration", "custom": 0}, pluck="name")
	for doctype in doctypes:
		itds.delete_doc("DocType", doctype, ignore_missing=True)

	itds.delete_doc("Module Def", "Data Migration", ignore_missing=True, force=True)
