# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def get_notification_config():
	return {
		"for_doctype": {
			"Error Log": {"seen": 0},
			"Communication": {"status": "Open", "communication_type": "Communication"},
			"ToDo": "itds.core.notifications.get_things_todo",
			"Event": "itds.core.notifications.get_todays_events",
			"Workflow Action": {"status": "Open"},
		},
	}


def get_things_todo(as_list=False):
	"""Return a count of incomplete ToDos."""
	data = itds.get_list(
		"ToDo",
		fields=["name", "description"] if as_list else "count(*)",
		filters=[["ToDo", "status", "=", "Open"]],
		or_filters=[
			["ToDo", "allocated_to", "=", itds.session.user],
			["ToDo", "assigned_by", "=", itds.session.user],
		],
		as_list=True,
	)

	if as_list:
		return data
	return data[0][0]


def get_todays_events(as_list: bool = False):
	"""Return a count of today's events in calendar."""
	from itds.desk.doctype.event.event import get_events
	from itds.utils import getdate

	today = getdate()
	events = get_events(today, today)
	return events if as_list else len(events)
