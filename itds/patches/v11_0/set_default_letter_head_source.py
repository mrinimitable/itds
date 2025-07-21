import itds


def execute():
	itds.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	itds.db.sql("update `tabLetter Head` set source = 'HTML'")
