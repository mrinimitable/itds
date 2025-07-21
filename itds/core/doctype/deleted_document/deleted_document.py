# Copyright (c) 2015, Itds Technologies and contributors
# License: MIT. See LICENSE

import json

import itds
from itds import _
from itds.desk.doctype.bulk_update.bulk_update import show_progress
from itds.model.document import Document
from itds.model.workflow import get_workflow_name


class DeletedDocument(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		data: DF.Code | None
		deleted_doctype: DF.Data | None
		deleted_name: DF.Data | None
		new_name: DF.ReadOnly | None
		restored: DF.Check
	# end: auto-generated types

	no_feed_on_delete = True

	@staticmethod
	def clear_old_logs(days=180):
		from itds.query_builder import Interval
		from itds.query_builder.functions import Now

		table = itds.qb.DocType("Deleted Document")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@itds.whitelist()
def restore(name, alert=True):
	deleted = itds.get_doc("Deleted Document", name)

	if deleted.restored:
		itds.throw(_("Document {0} Already Restored").format(name), exc=itds.DocumentAlreadyRestored)

	doc = itds.get_doc(json.loads(deleted.data))

	try:
		doc.insert()
	except itds.DocstatusTransitionError:
		itds.msgprint(_("Cancelled Document restored as Draft"))
		doc.docstatus = 0
		active_workflow = get_workflow_name(doc.doctype)
		if active_workflow:
			workflow_state_fieldname = itds.get_value("Workflow", active_workflow, "workflow_state_field")
			if doc.get(workflow_state_fieldname):
				doc.set(workflow_state_fieldname, None)
		doc.insert()

	doc.add_comment("Edit", _("restored {0} as {1}").format(deleted.deleted_name, doc.name))

	deleted.new_name = doc.name
	deleted.restored = 1
	deleted.db_update()

	if alert:
		itds.msgprint(_("Document Restored"))


@itds.whitelist()
def bulk_restore(docnames):
	docnames = itds.parse_json(docnames)
	message = _("Restoring Deleted Document")
	restored, invalid, failed = [], [], []

	for i, d in enumerate(docnames):
		try:
			show_progress(docnames, message, i + 1, d)
			restore(d, alert=False)
			itds.db.commit()
			restored.append(d)

		except itds.DocumentAlreadyRestored:
			itds.clear_last_message()
			invalid.append(d)

		except Exception:
			itds.clear_last_message()
			failed.append(d)
			itds.db.rollback()

	return {"restored": restored, "invalid": invalid, "failed": failed}
