import itds
from itds.model.utils.rename_field import rename_field


def execute():
	if not itds.db.table_exists("Dashboard Chart"):
		return

	itds.reload_doc("desk", "doctype", "dashboard_chart")

	if itds.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
