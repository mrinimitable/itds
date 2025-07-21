# Copyright (c) 2022, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds.deferred_insert import deferred_insert as _deferred_insert
from itds.model.document import Document


class RouteHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		route: DF.Data | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from itds.query_builder import Interval
		from itds.query_builder.functions import Now

		table = itds.qb.DocType("Route History")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@itds.whitelist()
def deferred_insert(routes):
	routes = [
		{
			"user": itds.session.user,
			"route": route.get("route"),
			"creation": route.get("creation"),
		}
		for route in itds.parse_json(routes)
	]

	_deferred_insert("Route History", routes)


@itds.whitelist()
def frequently_visited_links():
	return itds.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": itds.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)
