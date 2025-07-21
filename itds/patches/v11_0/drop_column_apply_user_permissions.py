import itds


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if itds.db.table_exists(doctype):
			if column in itds.db.get_table_columns(doctype):
				itds.db.sql(f"alter table `tab{doctype}` drop column {column}")

	itds.reload_doc("core", "doctype", "docperm", force=True)
	itds.reload_doc("core", "doctype", "custom_docperm", force=True)
