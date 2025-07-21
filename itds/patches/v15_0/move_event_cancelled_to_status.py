import itds


def execute():
	Event = itds.qb.DocType("Event")
	query = (
		itds.qb.update(Event)
		.set(Event.event_type, "Private")
		.set(Event.status, "Cancelled")
		.where(Event.event_type == "Cancelled")
	)
	query.run()
