# Copyright (c) 2023, Itds Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import itds
from itds import _
from itds.apps import get_apps


def get_context():
	all_apps = get_apps()

	system_default_app = itds.get_system_settings("default_app")
	user_default_app = itds.db.get_value("User", itds.session.user, "default_app")
	default_app = user_default_app if user_default_app else system_default_app

	if len(all_apps) == 0:
		itds.local.flags.redirect_location = "/app"
		raise itds.Redirect

	for app in all_apps:
		app["is_default"] = True if app.get("name") == default_app else False

	return {"apps": all_apps}
