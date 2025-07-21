import itds


def execute():
	singles = itds.qb.Table("tabSingles")
	itds.qb.from_(singles).delete().where(
		(singles.doctype == "System Settings") & (singles.field == "is_first_startup")
	).run()
