# Copyright (c) 2022, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import datetime
import functools
import mimetypes
import os
import sys
from collections.abc import Iterable
from decimal import Decimal
from pathlib import Path
from re import Match
from typing import TYPE_CHECKING
from urllib.parse import quote
from uuid import UUID

import orjson
import werkzeug.utils
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.local import LocalProxy
from werkzeug.wrappers import Response
from werkzeug.wsgi import wrap_file

import itds
import itds.model.document
import itds.sessions
import itds.utils
from itds import _
from itds.core.doctype.access_log.access_log import make_access_log
from itds.utils import format_timedelta, orjson_dumps

if TYPE_CHECKING:
	from itds.core.doctype.file.file import File

DateOrTimeTypes = datetime.date | datetime.datetime | datetime.time
timedelta = datetime.timedelta


def report_error(status_code):
	"""Build error. Show traceback in developer mode"""
	from itds.api import ApiVersion, get_api_version

	allow_traceback = is_traceback_allowed() and (status_code != 404 or itds.conf.logging)

	traceback = itds.utils.get_traceback()
	exc_type, exc_value, _ = sys.exc_info()

	match get_api_version():
		case ApiVersion.V1:
			if allow_traceback:
				itds.errprint(traceback)
				itds.response.exception = traceback.splitlines()[-1]
			itds.response["exc_type"] = exc_type.__name__
		case ApiVersion.V2:
			error_log = {"type": exc_type.__name__}
			if allow_traceback:
				print(traceback)
				error_log["exception"] = traceback
			_link_error_with_message_log(error_log, exc_value, itds.message_log)
			itds.local.response.errors = [error_log]

	response = build_response("json")
	response.status_code = status_code

	return response


def is_traceback_allowed():
	from itds.permissions import is_system_user

	return (
		itds.db
		and itds.get_system_settings("allow_error_traceback")
		and (not itds.local.flags.disable_traceback or itds._dev_server)
		and is_system_user()
	)


def _link_error_with_message_log(error_log, exception, message_logs):
	for message in list(message_logs):
		if message.get("__itds_exc_id") == getattr(exception, "__itds_exc_id", None):
			error_log.update(message)
			message_logs.remove(message)
			error_log.pop("raise_exception", None)
			error_log.pop("__itds_exc_id", None)
			return


def build_response(response_type=None):
	if "docs" in itds.local.response and not itds.local.response.docs:
		del itds.local.response["docs"]

	response_type_map = {
		"csv": as_csv,
		"txt": as_txt,
		"download": as_raw,
		"json": as_json,
		"pdf": as_pdf,
		"page": as_page,
		"redirect": redirect,
		"binary": as_binary,
	}

	return response_type_map[itds.response.get("type") or response_type]()


def as_csv():
	response = Response()
	response.mimetype = "text/csv"
	filename = f"{itds.response['doctype']}.csv"
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", "attachment", filename=filename)
	response.data = itds.response["result"]
	return response


def as_txt():
	response = Response()
	response.mimetype = "text"
	filename = f"{itds.response['doctype']}.txt"
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", "attachment", filename=filename)
	response.data = itds.response["result"]
	return response


def as_raw():
	response = Response()
	response.mimetype = (
		itds.response.get("content_type")
		or mimetypes.guess_type(itds.response["filename"])[0]
		or "application/unknown"
	)
	filename = itds.response["filename"].encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add(
		"Content-Disposition",
		itds.response.get("display_content_as", "attachment"),
		filename=filename,
	)
	response.data = itds.response["filecontent"]
	return response


def as_json():
	make_logs()

	response = Response()
	if itds.local.response.http_status_code:
		response.status_code = itds.local.response["http_status_code"]
		del itds.local.response["http_status_code"]

	response.mimetype = "application/json"
	response.data = orjson_dumps(itds.local.response, default=json_handler)
	return response


def as_pdf():
	response = Response()
	response.mimetype = "application/pdf"
	filename = itds.response["filename"].encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", None, filename=filename)
	response.data = itds.response["filecontent"]
	return response


def as_binary():
	response = Response()
	response.mimetype = "application/octet-stream"
	filename = itds.response["filename"]
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", None, filename=filename)
	response.data = itds.response["filecontent"]
	return response


def make_logs():
	"""make strings for msgprint and errprint"""

	from itds.api import ApiVersion, get_api_version

	match get_api_version():
		case ApiVersion.V1:
			_make_logs_v1()
		case ApiVersion.V2:
			_make_logs_v2()


def _make_logs_v1():
	from itds.utils.error import guess_exception_source

	response = itds.local.response

	if itds.error_log and is_traceback_allowed():
		if source := guess_exception_source(itds.local.error_log and itds.local.error_log[0]["exc"]):
			response["_exc_source"] = source
		response["exc"] = orjson.dumps([itds.utils.cstr(d["exc"]) for d in itds.local.error_log]).decode()

	if itds.local.message_log:
		response["_server_messages"] = orjson.dumps(
			[orjson.dumps(d).decode() for d in itds.local.message_log]
		).decode()

	if itds.debug_log:
		response["_debug_messages"] = orjson.dumps(itds.local.debug_log).decode()

	if itds.flags.error_message:
		response["_error_message"] = itds.flags.error_message


def _make_logs_v2():
	response = itds.local.response

	if itds.local.message_log:
		response["messages"] = itds.local.message_log

	if itds.debug_log:
		response["debug"] = [{"message": m} for m in itds.local.debug_log]


def json_handler(obj):
	"""serialize non-serializable data for json"""

	if isinstance(obj, DateOrTimeTypes):
		return str(obj)

	elif isinstance(obj, timedelta):
		return format_timedelta(obj)

	elif isinstance(obj, LocalProxy):
		return str(obj)

	elif hasattr(obj, "__json__"):
		return obj.__json__()

	elif isinstance(obj, Iterable):
		return list(obj)

	elif isinstance(obj, Decimal):
		return float(obj)

	elif isinstance(obj, Match):
		return obj.string

	elif type(obj) is type or isinstance(obj, Exception):
		return repr(obj)

	elif callable(obj):
		return repr(obj)

	elif isinstance(obj, Path):
		return str(obj)

	# orjson does this already
	# but json_handler needs to be compatible with built-in json module also
	elif isinstance(obj, UUID):
		return str(obj)

	else:
		raise TypeError(f"""Object of type {type(obj)} with value of {obj!r} is not JSON serializable""")


def as_page():
	"""print web page"""
	from itds.website.serve import get_response

	return get_response(itds.response["route"], http_status_code=itds.response.get("http_status_code"))


def redirect():
	return werkzeug.utils.redirect(itds.response.location)


def download_backup(path):
	try:
		itds.only_for(("System Manager", "Administrator"))
		make_access_log(report_name="Backup")
	except itds.PermissionError:
		raise Forbidden(
			_("You need to be logged in and have System Manager Role to be able to access backups.")
		)

	return send_private_file(path)


def download_private_file(path: str) -> Response:
	"""Checks permissions and sends back private file"""
	from itds.core.doctype.file.utils import find_file_by_url

	if itds.session.user == "Guest":
		raise Forbidden(_("You don't have permission to access this file"))

	file = find_file_by_url(path, name=itds.form_dict.fid)
	if not file:
		raise Forbidden(_("You don't have permission to access this file"))

	make_access_log(doctype="File", document=file.name, file_type=os.path.splitext(path)[-1][1:])
	return send_private_file(path.split("/private", 1)[1])


def send_private_file(path: str) -> Response:
	path = os.path.join(itds.local.conf.get("private_path", "private"), path.strip("/"))
	filename = os.path.basename(path)

	if itds.local.request.headers.get("X-Use-X-Accel-Redirect"):
		path = "/protected/" + path
		response = Response()
		response.headers["X-Accel-Redirect"] = quote(itds.utils.encode(path))
		response.headers["Cache-Control"] = "private,max-age=3600,stale-while-revalidate=86400"

	else:
		filepath = itds.utils.get_site_path(path)
		try:
			f = open(filepath, "rb")
		except OSError:
			raise NotFound

		response = Response(wrap_file(itds.local.request.environ, f), direct_passthrough=True)

	# no need for content disposition and force download. let browser handle its opening.
	# Except for those that can be injected with scripts.

	extension = os.path.splitext(path)[1]
	blacklist = [".svg", ".html", ".htm", ".xml"]

	if extension.lower() in blacklist:
		response.headers.add("Content-Disposition", "attachment", filename=filename)

	response.mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"

	return response


def handle_session_stopped():
	from itds.website.serve import get_response

	itds.respond_as_web_page(
		_("Updating"),
		_("The system is being updated. Please refresh again after a few moments."),
		http_status_code=503,
		indicator_color="orange",
		fullpage=True,
		primary_action=None,
	)
	return get_response("message", http_status_code=503)
