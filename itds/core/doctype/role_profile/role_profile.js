// Copyright (c) 2017, Itds Technologies and contributors
// For license information, please see license.txt

itds.ui.form.on("Role Profile", {
	refresh: function (frm) {
		if (has_common(itds.user_roles, ["Administrator", "System Manager"])) {
			if (!frm.roles_editor) {
				const role_area = $(frm.fields_dict.roles_html.wrapper);
				frm.roles_editor = new itds.RoleEditor(role_area, frm);
			}
			frm.roles_editor.show();
		}
	},

	validate: function (frm) {
		if (frm.roles_editor) {
			frm.roles_editor.set_roles_in_table();
		}
	},
});
