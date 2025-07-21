# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json
from typing import TYPE_CHECKING

import itds
import itds.desk.form.load
import itds.desk.form.meta
from itds import _
from itds.core.doctype.file.utils import extract_images_from_html
from itds.desk.form.document_follow import follow_document

if TYPE_CHECKING:
	from itds.core.doctype.comment.comment import Comment


@itds.whitelist(methods=["DELETE", "POST"])
def remove_attach():
	"""remove attachment"""
	fid = itds.form_dict.get("fid")
	itds.delete_doc("File", fid)


@itds.whitelist(methods=["POST", "PUT"])
def add_comment(
	reference_doctype: str, reference_name: str, content: str, comment_email: str, comment_by: str
) -> "Comment":
	"""Allow logged user with permission to read document to add a comment"""
	reference_doc = itds.get_lazy_doc(reference_doctype, reference_name)
	reference_doc.check_permission()

	comment = itds.new_doc("Comment")
	comment.update(
		{
			"comment_type": "Comment",
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"comment_email": comment_email,
			"comment_by": comment_by,
			"content": extract_images_from_html(reference_doc, content, is_private=True),
		}
	)
	comment.insert(ignore_permissions=True)

	if itds.get_cached_value("User", itds.session.user, "follow_commented_documents"):
		follow_document(comment.reference_doctype, comment.reference_name, itds.session.user)

	return comment


@itds.whitelist()
def update_comment(name, content):
	"""allow only owner to update comment"""
	doc = itds.get_doc("Comment", name)

	if itds.session.user not in ["Administrator", doc.owner]:
		itds.throw(_("Comment can only be edited by the owner"), itds.PermissionError)

	if doc.reference_doctype and doc.reference_name:
		reference_doc = itds.get_lazy_doc(doc.reference_doctype, doc.reference_name)
		reference_doc.check_permission()

		doc.content = extract_images_from_html(reference_doc, content, is_private=True)
	else:
		doc.content = content

	doc.save(ignore_permissions=True)


@itds.whitelist()
def update_comment_publicity(name: str, publish: bool):
	doc = itds.get_doc("Comment", name)
	if itds.session.user != doc.owner and "System Manager" not in itds.get_roles():
		itds.throw(_("Comment publicity can only be updated by the original author or a System Manager."))

	doc.published = int(publish)
	doc.save(ignore_permissions=True)


@itds.whitelist()
def get_next(doctype, value, prev, filters=None, sort_order="desc", sort_field="creation"):
	prev = int(prev)
	if not filters:
		filters = []
	if isinstance(filters, str):
		filters = json.loads(filters)

	# # condition based on sort order
	condition = ">" if sort_order.lower() == "asc" else "<"

	# switch the condition
	if prev:
		sort_order = "asc" if sort_order.lower() == "desc" else "desc"
		condition = "<" if condition == ">" else ">"

	# # add condition for next or prev item
	filters.append([doctype, sort_field, condition, itds.get_value(doctype, value, sort_field)])

	res = itds.get_list(
		doctype,
		fields=["name"],
		filters=filters,
		order_by=f"`tab{doctype}`.{sort_field}" + " " + sort_order,
		limit_start=0,
		limit_page_length=1,
		as_list=True,
	)

	if not res:
		itds.msgprint(_("No further records"))
		return None
	else:
		return res[0][0]


def get_pdf_link(doctype, docname, print_format="Standard", no_letterhead=0):
	return f"/api/method/itds.utils.print_format.download_pdf?doctype={doctype}&name={docname}&format={print_format}&no_letterhead={no_letterhead}"
