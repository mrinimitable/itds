# Copyright (c) 2020, Itds Technologies and contributors
# License: MIT. See LICENSE

import json

import itds

# import itds
from itds.model.document import Document


class DashboardSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		chart_config: DF.Code | None
		user: DF.Link | None
	# end: auto-generated types

	pass


@itds.whitelist()
def create_dashboard_settings(user):
	if not itds.db.exists("Dashboard Settings", user):
		doc = itds.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		itds.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = itds.session.user

	return f"""(`tabDashboard Settings`.name = {itds.db.escape(user)})"""


@itds.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = itds.parse_json(reset)
	doc = itds.get_doc("Dashboard Settings", itds.session.user)
	chart_config = itds.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = itds.parse_json(config)
		if chart_name not in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	itds.db.set_value("Dashboard Settings", itds.session.user, "chart_config", json.dumps(chart_config))
