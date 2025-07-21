// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// License: See license.txt

itds.ui.form.on("Currency", {
	refresh(frm) {
		frm.set_intro("");
		if (!frm.doc.enabled) {
			frm.set_intro(__("This Currency is disabled. Enable to use in transactions"));
		}
	},
});
