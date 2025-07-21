import json

import itds


@itds.whitelist()
def get_onboarding_status():
	onboarding_status = itds.db.get_value("User", itds.session.user, "onboarding_status")
	return itds.parse_json(onboarding_status) if onboarding_status else {}


@itds.whitelist()
def update_user_onboarding_status(steps: str, appName: str):
	steps = json.loads(steps)

	# get the current onboarding status
	onboarding_status = itds.db.get_value("User", itds.session.user, "onboarding_status")
	onboarding_status = itds.parse_json(onboarding_status)

	# update the onboarding status
	onboarding_status[appName + "_onboarding_status"] = steps

	itds.db.set_value(
		"User", itds.session.user, "onboarding_status", json.dumps(onboarding_status), update_modified=False
	)
