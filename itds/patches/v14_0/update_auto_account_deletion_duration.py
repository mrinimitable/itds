import itds


def execute():
	days = itds.db.get_single_value("Website Settings", "auto_account_deletion")
	itds.db.set_single_value("Website Settings", "auto_account_deletion", days * 24)
