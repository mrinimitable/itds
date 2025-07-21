# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import itds


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	itds.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	itds.db.delete("Custom Field", {"dt": doctype})
	itds.clear_cache(doctype=doctype)
