// Copyright (c) 2022, Itds Technologies and contributors
// For license information, please see license.txt

itds.ui.form.on("RQ Worker", {
	refresh: function (frm) {
		// Nothing in this form is supposed to be editable.
		frm.disable_form();
	},
});
