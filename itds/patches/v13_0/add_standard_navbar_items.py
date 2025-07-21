import itds
from itds.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for OKAYBlue in Navbar Settings
	itds.reload_doc("core", "doctype", "navbar_settings")
	itds.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
