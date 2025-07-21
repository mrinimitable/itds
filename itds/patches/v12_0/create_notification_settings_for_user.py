import itds
from itds.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	itds.reload_doc("desk", "doctype", "notification_settings")
	itds.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = itds.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
