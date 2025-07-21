import itds


def execute():
	itds.db.delete("DocType", {"name": "Feedback Request"})
