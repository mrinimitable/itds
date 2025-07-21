import itds
from itds.model.rename_doc import rename_doc


def execute():
	if itds.db.table_exists("Standard Reply") and not itds.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		itds.reload_doc("email", "doctype", "email_template")
