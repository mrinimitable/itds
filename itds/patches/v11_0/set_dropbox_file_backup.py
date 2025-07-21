import itds
from itds.utils import cint


def execute():
	itds.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(itds.db.get_single_value("Dropbox Settings", "enabled"))
	if check_dropbox_enabled == 1:
		itds.db.set_single_value("Dropbox Settings", "file_backup", 1)
