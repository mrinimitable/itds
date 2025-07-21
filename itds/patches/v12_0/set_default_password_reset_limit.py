# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.reload_doc("core", "doctype", "system_settings", force=1)
	itds.db.set_single_value("System Settings", "password_reset_limit", 3)
