import itds
from itds.model.rename_doc import rename_doc


def execute():
	if itds.db.table_exists("Email Alert Recipient") and not itds.db.table_exists(
		"Notification Recipient"
	):
		rename_doc("DocType", "Email Alert Recipient", "Notification Recipient")
		itds.reload_doc("email", "doctype", "notification_recipient")

	if itds.db.table_exists("Email Alert") and not itds.db.table_exists("Notification"):
		rename_doc("DocType", "Email Alert", "Notification")
		itds.reload_doc("email", "doctype", "notification")
