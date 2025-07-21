import itds
from itds.model.rename_doc import rename_doc


def execute():
	if itds.db.table_exists("Workflow Action") and not itds.db.table_exists("Workflow Action Master"):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		itds.reload_doc("workflow", "doctype", "workflow_action_master")
