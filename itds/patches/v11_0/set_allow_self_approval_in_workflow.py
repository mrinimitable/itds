import itds


def execute():
	itds.reload_doc("workflow", "doctype", "workflow_transition")
	itds.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
