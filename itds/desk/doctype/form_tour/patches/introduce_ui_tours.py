import json

import itds


def execute():
	"""Handle introduction of UI tours"""
	completed = {}
	for tour in itds.get_all("Form Tour", {"ui_tour": 1}, pluck="name"):
		completed[tour] = {"is_complete": True}

	User = itds.qb.DocType("User")
	itds.qb.update(User).set("onboarding_status", json.dumps(completed)).run()
