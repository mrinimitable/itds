# Copyright (c) 2015, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds import _
from itds.core.doctype.submission_queue.submission_queue import queue_submission
from itds.model.document import Document
from itds.utils import cint
from itds.utils.scheduler import is_scheduler_inactive


class BulkUpdate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		condition: DF.SmallText | None
		document_type: DF.Link
		field: DF.Literal[None]
		limit: DF.Int
		update_value: DF.SmallText
	# end: auto-generated types

	@itds.whitelist()
	def bulk_update(self):
		self.check_permission("write")
		limit = self.limit if self.limit and cint(self.limit) < 500 else 500

		condition = ""
		if self.condition:
			if ";" in self.condition:
				itds.throw(_("; not allowed in condition"))

			condition = f" where {self.condition}"

		docnames = itds.db.sql_list(
			f"""select name from `tab{self.document_type}`{condition} limit {limit} offset 0"""
		)
		return submit_cancel_or_update_docs(
			self.document_type, docnames, "update", {self.field: self.update_value}
		)


@itds.whitelist()
def submit_cancel_or_update_docs(doctype, docnames, action="submit", data=None, task_id=None):
	if isinstance(docnames, str):
		docnames = itds.parse_json(docnames)

	if len(docnames) < 20:
		return _bulk_action(doctype, docnames, action, data, task_id)
	elif len(docnames) <= 500:
		itds.msgprint(_("Bulk operation is enqueued in background."), alert=True)
		itds.enqueue(
			_bulk_action,
			doctype=doctype,
			docnames=docnames,
			action=action,
			data=data,
			task_id=task_id,
			queue="short",
			timeout=1000,
		)
	else:
		itds.throw(_("Bulk operations only support up to 500 documents."), title=_("Too Many Documents"))


def _bulk_action(doctype, docnames, action, data, task_id=None):
	if data:
		data = itds.parse_json(data)

	failed = []
	num_documents = len(docnames)

	for idx, docname in enumerate(docnames, 1):
		doc = itds.get_doc(doctype, docname)
		try:
			message = ""
			if action == "submit" and doc.docstatus.is_draft():
				if doc.meta.queue_in_background and not is_scheduler_inactive():
					queue_submission(doc, action)
					message = _("Queuing {0} for Submission").format(doctype)
				else:
					doc.submit()
					message = _("Submitting {0}").format(doctype)
			elif action == "cancel" and doc.docstatus.is_submitted():
				doc.cancel()
				message = _("Cancelling {0}").format(doctype)
			elif action == "update" and not doc.docstatus.is_cancelled():
				doc.update(data)
				doc.save()
				message = _("Updating {0}").format(doctype)
			else:
				failed.append(docname)
			itds.db.commit()
			itds.publish_progress(
				percent=idx / num_documents * 100,
				title=message,
				description=docname,
				task_id=task_id,
			)

		except Exception:
			failed.append(docname)
			itds.db.rollback()

	return failed


from itds.deprecation_dumpster import show_progress
