// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

itds.provide("itds.workflow");

itds.workflow = {
	state_fields: {},
	workflows: {},
	avoid_status_override: {},
	setup: function (doctype) {
		var wf = itds.get_list("Workflow", { document_type: doctype });
		if (wf.length) {
			itds.workflow.workflows[doctype] = wf[0];
			itds.workflow.state_fields[doctype] = wf[0].workflow_state_field;
			itds.workflow.avoid_status_override[doctype] = wf[0].states
				.filter((row) => row.avoid_status_override)
				.map((d) => d.state);
		} else {
			itds.workflow.state_fields[doctype] = null;
		}
	},
	get_state_fieldname: function (doctype) {
		if (itds.workflow.state_fields[doctype] === undefined) {
			itds.workflow.setup(doctype);
		}
		return itds.workflow.state_fields[doctype];
	},
	get_default_state: function (doctype, docstatus) {
		itds.workflow.setup(doctype);
		var value = null;
		$.each(itds.workflow.workflows[doctype].states, function (i, workflow_state) {
			if (cint(workflow_state.doc_status) === cint(docstatus)) {
				value = workflow_state.state;
				return false;
			}
		});
		return value;
	},
	get_transitions: function (doc) {
		itds.workflow.setup(doc.doctype);
		return itds.xcall("itds.model.workflow.get_transitions", { doc: doc });
	},
	get_document_state_roles: function (doctype, state) {
		itds.workflow.setup(doctype);
		let workflow_states =
			itds.get_children(itds.workflow.workflows[doctype], "states", { state: state }) ||
			[];
		return workflow_states.map((d) => d.allow_edit);
	},
	is_self_approval_enabled: function (doctype) {
		return itds.workflow.workflows[doctype].allow_self_approval;
	},
	is_read_only: function (doctype, name) {
		var state_fieldname = itds.workflow.get_state_fieldname(doctype);
		if (state_fieldname) {
			var doc = locals[doctype][name];
			if (!doc) return false;
			if (doc.__islocal) return false;

			var state =
				doc[state_fieldname] || itds.workflow.get_default_state(doctype, doc.docstatus);
			if (!state) return false;

			let allow_edit_roles = itds.workflow.get_document_state_roles(doctype, state);
			let has_common_role = itds.user_roles.some((role) =>
				allow_edit_roles.includes(role)
			);
			return !has_common_role;
		}
		return false;
	},
	get_update_fields: function (doctype) {
		var update_fields = $.unique(
			$.map(itds.workflow.workflows[doctype].states || [], function (d) {
				return d.update_field;
			})
		);
		return update_fields;
	},
	get_state(doc) {
		const state_field = this.get_state_fieldname(doc.doctype);
		let state = doc[state_field];
		if (!state) {
			state = this.get_default_state(doc.doctype, doc.docstatus);
		}
		return state;
	},
	get_all_transitions(doctype) {
		return itds.workflow.workflows[doctype].transitions || [];
	},
	get_all_transition_actions(doctype) {
		const transitions = this.get_all_transitions(doctype);
		return transitions.map((transition) => {
			return transition.action;
		});
	},
};
