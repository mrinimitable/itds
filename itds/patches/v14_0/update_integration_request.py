import itds


def execute():
	doctype = "Integration Request"

	if not itds.db.has_column(doctype, "integration_type"):
		return

	itds.db.set_value(
		doctype,
		{"integration_type": "Remote", "integration_request_service": ("!=", "PayPal")},
		"is_remote_request",
		1,
	)
	itds.db.set_value(
		doctype,
		{"integration_type": "Subscription Notification"},
		"request_description",
		"Subscription Notification",
	)
