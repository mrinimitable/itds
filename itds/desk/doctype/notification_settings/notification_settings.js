// Copyright (c) 2019, Itds Technologies and contributors
// For license information, please see license.txt

itds.ui.form.on("Notification Settings", {
	onload: (frm) => {
		frm.set_query("subscribed_documents", () => {
			return {
				filters: {
					istable: 0,
				},
			};
		});
	},

	refresh: (frm) => {
		if (itds.user.has_role("System Manager")) {
			frm.add_custom_button(__("Go to Notification Settings List"), () => {
				itds.set_route("List", "Notification Settings");
			});
		}
	},
});
