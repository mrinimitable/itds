# Copyright (c) 2018, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	signatures = itds.db.get_list("User", {"email_signature": ["!=", ""]}, ["name", "email_signature"])
	itds.reload_doc("core", "doctype", "user")
	for d in signatures:
		signature = d.get("email_signature")
		signature = signature.replace("\n", "<br>")
		signature = "<div>" + signature + "</div>"
		itds.db.set_value("User", d.get("name"), "email_signature", signature)
