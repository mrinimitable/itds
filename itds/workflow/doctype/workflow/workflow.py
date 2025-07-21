# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds
from itds import _
from itds.model.document import Document
from itds.utils import cint


class Workflow(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF
		from itds.workflow.doctype.workflow_document_state.workflow_document_state import (
			WorkflowDocumentState,
		)
		from itds.workflow.doctype.workflow_transition.workflow_transition import WorkflowTransition

		document_type: DF.Link
		is_active: DF.Check
		override_status: DF.Check
		send_email_alert: DF.Check
		states: DF.Table[WorkflowDocumentState]
		transitions: DF.Table[WorkflowTransition]
		workflow_data: DF.JSON | None
		workflow_name: DF.Data
		workflow_state_field: DF.Data
	# end: auto-generated types

	def validate(self):
		self.set_active()
		self.validate_docstatus()

	def on_update(self):
		self.create_custom_field_for_workflow_state()
		self.update_default_workflow_status()

	def create_custom_field_for_workflow_state(self):
		itds.clear_cache(doctype=self.document_type)
		meta = itds.get_meta(self.document_type)
		if not meta.get_field(self.workflow_state_field):
			# create custom field
			itds.get_doc(
				{
					"doctype": "Custom Field",
					"dt": self.document_type,
					"__islocal": 1,
					"fieldname": self.workflow_state_field,
					"label": self.workflow_state_field.replace("_", " ").title(),
					"hidden": 1,
					"allow_on_submit": 1,
					"no_copy": 1,
					"fieldtype": "Link",
					"options": "Workflow State",
					"owner": "Administrator",
				}
			).save()

			itds.msgprint(
				_("Created Custom Field {0} in {1}").format(self.workflow_state_field, self.document_type)
			)

	def update_default_workflow_status(self):
		docstatus_map = {}
		states = self.get("states")
		for d in states:
			if d.doc_status not in docstatus_map:
				itds.db.sql(
					f"""
					UPDATE `tab{self.document_type}`
					SET `{self.workflow_state_field}` = %s
					WHERE ifnull(`{self.workflow_state_field}`, '') = ''
					AND `docstatus` = %s
				""",
					(d.state, d.doc_status),
				)

				docstatus_map[d.doc_status] = d.state

	def validate_docstatus(self):
		def get_state(state):
			for s in self.states:
				if s.state == state:
					return s

			itds.throw(itds._("{0} not a valid State").format(state))

		for t in self.transitions:
			state = get_state(t.state)
			next_state = get_state(t.next_state)

			if state.doc_status == "2":
				itds.throw(
					itds._("Cannot change state of Cancelled Document. Transition row {0}").format(t.idx)
				)

			if state.doc_status == "1" and next_state.doc_status == "0":
				itds.throw(
					itds._(
						"Submitted Document cannot be converted back to draft. Transition row {0}"
					).format(t.idx)
				)

			if state.doc_status == "0" and next_state.doc_status == "2":
				itds.throw(itds._("Cannot cancel before submitting. See Transition {0}").format(t.idx))

	def set_active(self):
		if cint(self.is_active):
			# clear all other
			itds.db.sql(
				"""UPDATE `tabWorkflow` SET `is_active`=0
				WHERE `document_type`=%s""",
				self.document_type,
			)


@itds.whitelist()
def get_workflow_state_count(doctype, workflow_state_field, states):
	itds.has_permission(doctype=doctype, ptype="read", throw=True)
	states = itds.parse_json(states)

	if workflow_state_field in itds.get_meta(doctype).get_valid_columns():
		result = itds.get_all(
			doctype,
			fields=[workflow_state_field, "count(*) as count"],
			filters={workflow_state_field: ["not in", states]},
			group_by=workflow_state_field,
		)
		return [r for r in result if r[workflow_state_field]]
