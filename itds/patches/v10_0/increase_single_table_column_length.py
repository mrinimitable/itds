"""
Run this after updating country_info.json and or
"""

import itds


def execute():
	for col in ("field", "doctype"):
		itds.db.sql_ddl(f"alter table `tabSingles` modify column `{col}` varchar(255)")
