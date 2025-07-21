// Copyright (c) 2017, Itds Technologies and contributors
// For license information, please see license.txt

itds.ui.form.on("Print Style", {
	refresh: function (frm) {
		frm.add_custom_button(__("Print Settings"), () => {
			itds.set_route("Form", "Print Settings");
		});
	},
});
