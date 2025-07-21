import itds


def execute():
	if itds.db.table_exists("Prepared Report"):
		itds.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = itds.get_all("Prepared Report")
		for report in prepared_reports:
			itds.delete_doc("Prepared Report", report.name)
