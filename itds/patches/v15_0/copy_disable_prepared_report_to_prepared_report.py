import itds


def execute():
	table = itds.qb.DocType("Report")
	itds.qb.update(table).set(table.prepared_report, 0).where(table.disable_prepared_report == 1)
