import itds


def execute():
	itds.reload_doc("core", "doctype", "doctype_link")
	itds.reload_doc("core", "doctype", "doctype_action")
	itds.reload_doc("core", "doctype", "doctype")
	itds.model.delete_fields({"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1)

	itds.db.delete("Property Setter", {"property": "read_only_onload"})
