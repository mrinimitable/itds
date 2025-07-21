# Copyright (c) 2022, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os
from mimetypes import guess_type
from typing import TYPE_CHECKING

from werkzeug.wrappers import Response

import itds
import itds.sessions
import itds.utils
from itds import _, is_whitelisted, ping
from itds.core.doctype.server_script.server_script_utils import get_server_script_map
from itds.monitor import add_data_to_monitor
from itds.permissions import check_doctype_permission
from itds.utils import cint
from itds.utils.csvutils import build_csv_response
from itds.utils.deprecations import deprecated
from itds.utils.image import optimize_image
from itds.utils.response import build_response

if TYPE_CHECKING:
	from itds.core.doctype.file.file import File
	from itds.core.doctype.user.user import User

ALLOWED_MIMETYPES = (
	"image/png",
	"image/jpeg",
	"application/pdf",
	"application/msword",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"application/vnd.ms-excel",
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"application/vnd.oasis.opendocument.text",
	"application/vnd.oasis.opendocument.spreadsheet",
	"text/plain",
	"video/quicktime",
	"video/mp4",
	"text/csv",
)


def handle():
	"""handle request"""

	cmd = itds.local.form_dict.cmd
	data = None

	if cmd != "login":
		data = execute_cmd(cmd)

	# data can be an empty string or list which are valid responses
	if data is not None:
		if isinstance(data, Response):
			# method returns a response object, pass it on
			return data

		# add the response to `message` label
		itds.response["message"] = data


def execute_cmd(cmd, from_async=False):
	"""execute a request as python module"""
	cmd = itds.override_whitelisted_method(cmd)

	# via server script
	server_script = get_server_script_map().get("_api", {}).get(cmd)
	if server_script:
		return run_server_script(server_script)

	try:
		method = get_attr(cmd)
	except Exception as e:
		itds.throw(_("Failed to get method for command {0} with {1}").format(cmd, e))

	if from_async:
		method = method.queue

	if method != run_doc_method:
		is_whitelisted(method)
		is_valid_http_method(method)

	return itds.call(method, **itds.form_dict)


def run_server_script(server_script):
	response = itds.get_doc("Server Script", server_script).execute_method()

	# some server scripts return output using flags (empty dict by default),
	# while others directly modify itds.response
	# return flags if not empty dict (this overwrites itds.response.message)
	if response != {}:
		return response


def is_valid_http_method(method):
	if itds.flags.in_safe_exec:
		return

	http_method = itds.local.request.method

	if http_method not in itds.allowed_http_methods_for_whitelisted_func[method]:
		itds.throw_permission_error()


@itds.whitelist(allow_guest=True)
def logout():
	itds.local.login_manager.logout()
	itds.db.commit()


@itds.whitelist(allow_guest=True)
def web_logout():
	itds.local.login_manager.logout()
	itds.db.commit()
	itds.respond_as_web_page(
		_("Logged Out"), _("You have been successfully logged out"), indicator_color="green"
	)


@itds.whitelist(allow_guest=True)
def upload_file():
	user = None
	if itds.session.user == "Guest":
		if itds.get_system_settings("allow_guests_to_upload_files"):
			ignore_permissions = True
		else:
			raise itds.PermissionError
	else:
		user: User = itds.get_lazy_doc("User", itds.session.user)
		ignore_permissions = False

	files = itds.request.files
	is_private = itds.form_dict.is_private
	doctype = itds.form_dict.doctype
	docname = itds.form_dict.docname
	fieldname = itds.form_dict.fieldname
	file_url = itds.form_dict.file_url
	folder = itds.form_dict.folder or "Home"
	method = itds.form_dict.method
	filename = itds.form_dict.file_name
	optimize = itds.form_dict.optimize
	content = None

	if library_file := itds.form_dict.get("library_file_name"):
		itds.has_permission("File", doc=library_file, throw=True)
		doc = itds.get_value(
			"File",
			itds.form_dict.library_file_name,
			["is_private", "file_url", "file_name"],
			as_dict=True,
		)
		is_private = doc.is_private
		file_url = doc.file_url
		filename = doc.file_name

	if not ignore_permissions:
		check_write_permission(doctype, docname)

	if "file" in files:
		file = files["file"]
		content = file.stream.read()
		filename = file.filename

		content_type = guess_type(filename)[0]
		if optimize and content_type and content_type.startswith("image/"):
			args = {"content": content, "content_type": content_type}
			if itds.form_dict.max_width:
				args["max_width"] = int(itds.form_dict.max_width)
			if itds.form_dict.max_height:
				args["max_height"] = int(itds.form_dict.max_height)
			content = optimize_image(**args)

	itds.local.uploaded_file_url = file_url
	itds.local.uploaded_file = content
	itds.local.uploaded_filename = filename

	if content is not None and (itds.session.user == "Guest" or (user and not user.has_desk_access())):
		filetype = guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			itds.throw(_("You can only upload JPG, PNG, PDF, TXT, CSV or Microsoft documents."))

	if method:
		method = itds.get_attr(method)
		is_whitelisted(method)
		return method()
	else:
		return itds.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": doctype,
				"attached_to_name": docname,
				"attached_to_field": fieldname,
				"folder": folder,
				"file_name": filename,
				"file_url": file_url,
				"is_private": cint(is_private),
				"content": content,
			}
		).save(ignore_permissions=ignore_permissions)


def check_write_permission(doctype: str | None = None, name: str | None = None):
	if not doctype:
		return

	if not name:
		itds.has_permission(doctype, "write", throw=True)
		return

	try:
		doc = itds.get_lazy_doc(doctype, name)
	except itds.DoesNotExistError:
		# doc has not been inserted yet, name is set to "new-some-doctype"
		# If doc inserts fine then only this attachment will be linked see file/utils.py:relink_mismatched_files
		itds.new_doc(doctype).check_permission("write")
		return

	doc.check_permission("write")


@itds.whitelist(allow_guest=True)
def download_file(file_url: str):
	"""
	Download file using token and REST API. Valid session or
	token is required to download private files.

	Method : GET
	Endpoints : download_file, itds.core.doctype.file.file.download_file
	URL Params : file_name = /path/to/file relative to site path
	"""
	file: File = itds.get_doc("File", {"file_url": file_url})
	if not file.is_downloadable():
		raise itds.PermissionError

	itds.local.response.filename = os.path.basename(file_url)
	itds.local.response.filecontent = file.get_content()
	itds.local.response.type = "download"


def get_attr(cmd):
	"""get method object from cmd"""
	if "." in cmd:
		method = itds.get_attr(cmd)
	else:
		from itds.deprecation_dumpster import deprecation_warning

		deprecation_warning(
			"unknown",
			"v17",
			f"Calling shorthand for {cmd} is deprecated, please specify full path in RPC call.",
		)
		method = globals()[cmd]
	return method


def run_doc_method(method, docs=None, dt=None, dn=None, arg=None, args=None):
	"""run a whitelisted controller method"""
	from inspect import signature

	if not args and arg:
		args = arg

	if dt:  # not called from a doctype (from a page)
		if not dn:
			dn = dt  # single
		doc = itds.get_doc(dt, dn)

	else:
		docs = itds.parse_json(docs)
		doc = itds.get_doc(docs)
		doc._original_modified = doc.modified
		doc.check_if_latest()

	if not doc:
		itds.throw_permission_error()

	doc.check_permission("read")

	try:
		args = itds.parse_json(args)
	except ValueError:
		pass

	method_obj = getattr(doc, method)
	fn = getattr(method_obj, "__func__", method_obj)
	is_whitelisted(fn)
	is_valid_http_method(fn)

	fnargs = list(signature(method_obj).parameters)

	if not fnargs or (len(fnargs) == 1 and fnargs[0] == "self"):
		response = doc.run_method(method)

	elif "args" in fnargs or not isinstance(args, dict):
		response = doc.run_method(method, args)

	else:
		response = doc.run_method(method, **args)

	itds.response.docs.append(doc)
	if response is None:
		return

	# build output as csv
	if cint(itds.form_dict.get("as_csv")):
		build_csv_response(response, _(doc.doctype).replace(" ", ""))
		return

	itds.response["message"] = response

	add_data_to_monitor(methodname=method)


runserverobj = deprecated(run_doc_method)
