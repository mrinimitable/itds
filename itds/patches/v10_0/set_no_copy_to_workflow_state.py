import itds


def execute():
	for dt in itds.get_all("Workflow", fields=["name", "document_type", "workflow_state_field"]):
		fieldname = itds.db.get_value(
			"Custom Field", filters={"dt": dt.document_type, "fieldname": dt.workflow_state_field}
		)

		if fieldname:
			custom_field = itds.get_doc("Custom Field", fieldname)
			custom_field.no_copy = 1
			custom_field.save()
