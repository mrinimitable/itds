# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.reload_doc("Email", "doctype", "Notification")

	notifications = itds.get_all("Notification", {"is_standard": 1}, {"name", "channel"})
	for notification in notifications:
		if not notification.channel:
			itds.db.set_value("Notification", notification.name, "channel", "Email", update_modified=False)
			itds.db.commit()
