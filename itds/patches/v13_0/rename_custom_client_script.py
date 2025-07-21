import itds
from itds.model.rename_doc import rename_doc


def execute():
	if itds.db.exists("DocType", "Client Script"):
		return

	itds.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	itds.flags.ignore_route_conflict_validation = False

	itds.reload_doctype("Client Script", force=True)
