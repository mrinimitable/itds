import itds


def execute():
	doctype = "Top Bar Item"
	if not itds.db.table_exists(doctype) or not itds.db.has_column(doctype, "target"):
		return

	itds.reload_doc("website", "doctype", "top_bar_item")
	itds.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
