import itds


def execute():
	item = itds.db.exists("Navbar Item", {"item_label": "Background Jobs"})
	if not item:
		return

	itds.delete_doc("Navbar Item", item)
