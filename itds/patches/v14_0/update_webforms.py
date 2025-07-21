# Copyright (c) 2021, Itds Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import itds


def execute():
	itds.reload_doc("website", "doctype", "web_form_list_column")
	itds.reload_doctype("Web Form")

	for web_form in itds.get_all("Web Form", fields=["*"]):
		if web_form.allow_multiple and not web_form.show_list:
			itds.db.set_value("Web Form", web_form.name, "show_list", True)
