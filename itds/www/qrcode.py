# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from urllib.parse import parse_qsl

import itds
from itds import _
from itds.twofactor import get_qr_svg_code


def get_context(context):
	context.no_cache = 1
	context.qr_code_user, context.qrcode_svg = get_user_svg_from_cache()


def get_query_key():
	"""Return query string arg."""
	query_string = itds.local.request.query_string
	query = dict(parse_qsl(query_string))
	query = {key.decode(): val.decode() for key, val in query.items()}
	if "k" not in list(query):
		itds.throw(_("Not Permitted"), itds.PermissionError)
	query = (query["k"]).strip()
	if False in [i.isalpha() or i.isdigit() for i in query]:
		itds.throw(_("Not Permitted"), itds.PermissionError)
	return query


def get_user_svg_from_cache():
	"""Get User and SVG code from cache."""
	key = get_query_key()
	totp_uri = itds.cache.get_value(f"{key}_uri")
	user = itds.cache.get_value(f"{key}_user")
	if not totp_uri or not user:
		itds.throw(_("Page has expired!"), itds.PermissionError)
	if not itds.db.exists("User", user):
		itds.throw(_("Not Permitted"), itds.PermissionError)
	user = itds.get_doc("User", user)
	svg = get_qr_svg_code(totp_uri)
	return (user, svg.decode())
