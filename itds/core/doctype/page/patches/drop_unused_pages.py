import itds


def execute():
	for name in ("desktop", "space"):
		itds.delete_doc("Page", name)
