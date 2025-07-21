import itds
from itds.utils import cint


def execute():
	expiry_period = (
		cint(itds.db.get_singles_dict("System Settings").get("prepared_report_expiry_period")) or 30
	)
	itds.get_single("Log Settings").register_doctype("Prepared Report", expiry_period)
