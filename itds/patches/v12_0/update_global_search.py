import itds
from itds.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes


def execute():
	itds.reload_doc("desk", "doctype", "global_search_doctype")
	itds.reload_doc("desk", "doctype", "global_search_settings")
	update_global_search_doctypes()
