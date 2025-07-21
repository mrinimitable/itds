# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os

no_cache = 1

import json
import re
from urllib.parse import urlencode

import itds
import itds.sessions
from itds import _
from itds.utils.jinja_globals import is_rtl

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	if itds.session.user == "Guest":
		itds.response["status_code"] = 403
		itds.msgprint(_("Log in to access this page."))
		itds.redirect(f"/login?{urlencode({'redirect-to': itds.request.path})}")

	elif itds.session.data.user_type == "Website User":
		itds.throw(_("You are not permitted to access this page."), itds.PermissionError)

	try:
		boot = itds.sessions.get()
	except Exception as e:
		raise itds.SessionBootFailed from e

	# this needs commit
	csrf_token = itds.sessions.get_csrf_token()

	itds.db.commit()

	hooks = itds.get_hooks()
	app_include_js = hooks.get("app_include_js", []) + itds.conf.get("app_include_js", [])
	app_include_css = hooks.get("app_include_css", []) + itds.conf.get("app_include_css", [])
	app_include_icons = hooks.get("app_include_icons", [])

	if itds.get_system_settings("enable_telemetry") and os.getenv("ITDS_SENTRY_DSN"):
		app_include_js.append("sentry.bundle.js")

	context.update(
		{
			"no_cache": 1,
			"build_version": itds.utils.get_build_version(),
			"app_include_js": app_include_js,
			"app_include_css": app_include_css,
			"app_include_icons": app_include_icons,
			"layout_direction": "rtl" if is_rtl() else "ltr",
			"lang": itds.local.lang,
			"sounds": hooks["sounds"],
			"boot": boot,
			"desk_theme": boot.get("desk_theme") or "Light",
			"csrf_token": csrf_token,
			"google_analytics_id": itds.conf.get("google_analytics_id"),
			"google_analytics_anonymize_ip": itds.conf.get("google_analytics_anonymize_ip"),
			"app_name": (
				itds.get_website_settings("app_name") or itds.get_system_settings("app_name") or "Itds"
			),
		}
	)

	return context
