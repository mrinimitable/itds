# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	"""Set default module for standard Web Template, if none."""
	itds.reload_doc("website", "doctype", "Web Template Field")
	itds.reload_doc("website", "doctype", "web_template")

	standard_templates = itds.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = itds.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
