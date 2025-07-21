// Copyright (c) 2017, Itds Technologies and contributors
// For license information, please see license.txt

itds.ui.form.on("Activity Log", {
	refresh: function (frm) {
		// Nothing in this form is supposed to be editable.
		frm.disable_form();
	},
});
