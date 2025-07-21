# Copyright (c) 2020, Itds Technologies and contributors
# License: MIT. See LICENSE

from urllib.parse import urlparse

import itds
import itds.utils
from itds.model.document import Document
from itds.utils.caching import redis_cache


class WebPageView(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		browser: DF.Data | None
		browser_version: DF.Data | None
		campaign: DF.Data | None
		content: DF.Data | None
		is_unique: DF.Data | None
		medium: DF.Data | None
		path: DF.Data | None
		referrer: DF.Data | None
		source: DF.Data | None
		time_zone: DF.Data | None
		user_agent: DF.Data | None
		visitor_id: DF.Data | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=180):
		from itds.query_builder import Interval
		from itds.query_builder.functions import Now

		table = itds.qb.DocType("Web Page View")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@itds.whitelist(allow_guest=True)
def make_view_log(
	referrer=None,
	browser=None,
	version=None,
	user_tz=None,
	source=None,
	campaign=None,
	medium=None,
	content=None,
	visitor_id=None,
):
	if not is_tracking_enabled():
		return

	# real path
	path = itds.request.headers.get("Referer")

	if not itds.utils.is_site_link(path):
		return

	path = urlparse(path).path

	request_dict = itds.request.__dict__
	user_agent = request_dict.get("environ", {}).get("HTTP_USER_AGENT")

	if referrer:
		referrer = referrer.split("?", 1)[0]

	if path != "/" and path.startswith("/"):
		path = path[1:]

	if path.startswith(("api/", "app/", "assets/", "private/files/")):
		return

	is_unique = visitor_id and not bool(itds.db.exists("Web Page View", {"visitor_id": visitor_id}))

	view = itds.new_doc("Web Page View")
	view.path = path
	view.referrer = referrer
	view.browser = browser
	view.browser_version = version
	view.time_zone = user_tz
	view.user_agent = user_agent
	view.is_unique = is_unique
	view.source = source
	view.campaign = campaign
	view.medium = (medium or "").lower()
	view.content = content
	view.visitor_id = visitor_id

	try:
		view.deferred_insert()
	except Exception:
		itds.clear_last_message()


@itds.whitelist()
@redis_cache(ttl=5 * 60)
def get_page_view_count(path):
	return itds.db.count("Web Page View", filters={"path": path})


def is_tracking_enabled():
	return itds.get_website_settings("enable_view_tracking")
