# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	itds.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	itds.delete_doc("Web Template", "Footer Horizontal", force=1)
