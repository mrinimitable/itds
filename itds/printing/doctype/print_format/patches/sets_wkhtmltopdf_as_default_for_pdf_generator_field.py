import itds


def execute():
	"""sets "wkhtmltopdf" as default for pdf_generator field"""
	for pf in itds.get_all("Print Format", pluck="name"):
		itds.db.set_value("Print Format", pf, "pdf_generator", "wkhtmltopdf", update_modified=False)
