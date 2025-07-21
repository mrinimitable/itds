import json

from werkzeug.routing import Rule

import itds
from itds import _
from itds.utils.data import sbool


def document_list(doctype: str):
	if itds.form_dict.get("fields"):
		itds.form_dict["fields"] = json.loads(itds.form_dict["fields"])

	# set limit of records for itds.get_list
	itds.form_dict.setdefault(
		"limit_page_length",
		itds.form_dict.limit or itds.form_dict.limit_page_length or 20,
	)

	# convert strings to native types - only as_dict and debug accept bool
	for param in ["as_dict", "debug"]:
		param_val = itds.form_dict.get(param)
		if param_val is not None:
			itds.form_dict[param] = sbool(param_val)

	# evaluate itds.get_list
	return itds.call(itds.client.get_list, doctype, **itds.form_dict)


def handle_rpc_call(method: str):
	import itds.handler

	method = method.split("/")[0]  # for backward compatiblity

	itds.form_dict.cmd = method
	return itds.handler.handle()


def create_doc(doctype: str):
	data = get_request_form_data()
	data.pop("doctype", None)
	return itds.new_doc(doctype, **data).insert()


def update_doc(doctype: str, name: str):
	data = get_request_form_data()

	doc = itds.get_doc(doctype, name, for_update=True)
	if "flags" in data:
		del data["flags"]

	doc.update(data)
	doc.save()

	# check for child table doctype
	if doc.get("parenttype"):
		itds.get_doc(doc.parenttype, doc.parent).save()

	return doc


def delete_doc(doctype: str, name: str):
	# TODO: child doc handling
	itds.delete_doc(doctype, name, ignore_missing=False)
	itds.response.http_status_code = 202
	return "ok"


def read_doc(doctype: str, name: str):
	# Backward compatiblity
	if "run_method" in itds.form_dict:
		return execute_doc_method(doctype, name)

	doc = itds.get_doc(doctype, name)
	doc.check_permission("read")
	doc.apply_fieldlevel_read_permissions()
	return doc


def execute_doc_method(doctype: str, name: str, method: str | None = None):
	method = method or itds.form_dict.pop("run_method")
	doc = itds.get_doc(doctype, name)
	doc.is_whitelisted(method)

	if itds.request.method == "GET":
		doc.check_permission("read")
		return doc.run_method(method, **itds.form_dict)

	elif itds.request.method == "POST":
		doc.check_permission("write")
		return doc.run_method(method, **itds.form_dict)


def get_request_form_data():
	if itds.form_dict.data is None:
		data = itds.safe_decode(itds.request.get_data())
	else:
		data = itds.form_dict.data

	try:
		return itds.parse_json(data)
	except ValueError:
		return itds.form_dict


url_rules = [
	Rule("/method/<path:method>", endpoint=handle_rpc_call),
	Rule("/resource/<doctype>", methods=["GET"], endpoint=document_list),
	Rule("/resource/<doctype>", methods=["POST"], endpoint=create_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["GET"], endpoint=read_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["PUT"], endpoint=update_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["DELETE"], endpoint=delete_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["POST"], endpoint=execute_doc_method),
]
