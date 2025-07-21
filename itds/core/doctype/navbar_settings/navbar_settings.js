// Copyright (c) 2020, Itds Technologies and contributors
// For license information, please see license.txt

itds.ui.form.on("Navbar Settings", {
	after_save: function (frm) {
		itds.ui.toolbar.clear_cache();
	},
});
