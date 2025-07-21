// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

itds.provide("itds.views.formview");

itds.views.FormFactory = class FormFactory extends itds.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = itds.router.doctype_layout || doctype;

		if (!itds.views.formview[doctype_layout]) {
			itds.model.with_doctype(doctype, () => {
				this.page = itds.container.add_page(doctype_layout);
				itds.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (itds.router.doctype_layout) {
			itds.model.with_doc("DocType Layout", itds.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new itds.ui.form.Form(
			doctype,
			this.page,
			true,
			itds.router.doctype_layout
		);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function () {
				itds.ui.form.close_grid_form();
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = itds.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (itds.model.new_names[name]) {
			// document has been renamed, reroute
			name = itds.model.new_names[name];
			itds.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = itds.get_doc(doctype, name);
		if (
			doc &&
			itds.model.get_docinfo(doctype, name) &&
			(doc.__islocal || itds.model.is_fresh(doc))
		) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		itds.model.with_doc(doctype, name, (name, r) => {
			if (r && r["403"]) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === "new") {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					itds.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = itds.model.make_new_doc_and_get_name(doctype, true);
		if (new_name === name) {
			this.render(doctype_layout, name);
		} else {
			itds.route_flags.replace_route = true;
			itds.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		itds.container.change_to(doctype_layout);
		itds.views.formview[doctype_layout].frm.refresh(name);
	}
};
