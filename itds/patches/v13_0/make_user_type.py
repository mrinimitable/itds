import itds
from itds.utils.install import create_user_type


def execute():
	itds.reload_doc("core", "doctype", "role")
	itds.reload_doc("core", "doctype", "user_document_type")
	itds.reload_doc("core", "doctype", "user_type_module")
	itds.reload_doc("core", "doctype", "user_select_document_type")
	itds.reload_doc("core", "doctype", "user_type")

	create_user_type()
