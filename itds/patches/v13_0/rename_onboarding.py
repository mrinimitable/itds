# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	if itds.db.exists("DocType", "Onboarding"):
		itds.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
