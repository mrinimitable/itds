# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.reload_doc("core", "doctype", "system_settings")
	itds.db.set_single_value("System Settings", "allow_login_after_fail", 60)
