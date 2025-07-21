// Copyright (c) 2022, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See LICENSE

itds.ui.form.on("Role", {
	refresh: function (frm) {
		if (frm.doc.name === "All") {
			frm.dashboard.add_comment(
				__("Role 'All' will be given to all system + website users."),
				"yellow"
			);
		} else if (frm.doc.name === "Desk User") {
			frm.dashboard.add_comment(
				__("Role 'Desk User' will be given to all system users."),
				"yellow"
			);
		}

		frm.set_df_property("is_custom", "read_only", itds.session.user !== "Administrator");

		frm.add_custom_button("Role Permissions Manager", function () {
			itds.route_options = { role: frm.doc.name };
			itds.set_route("permission-manager");
		});
		frm.add_custom_button("Show Users", function () {
			itds.route_options = { role: frm.doc.name };
			itds.set_route("List", "User", "Report");
		});
	},
});
