import itds


def execute():
	"""
	Rename the Marketing Campaign table to UTM Campaign table
	"""
	if itds.db.exists("DocType", "UTM Campaign"):
		return

	if not itds.db.exists("DocType", "Marketing Campaign"):
		return

	itds.rename_doc("DocType", "Marketing Campaign", "UTM Campaign", force=True)
	itds.reload_doctype("UTM Campaign", force=True)
