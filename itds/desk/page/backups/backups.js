itds.pages["backups"].on_page_load = function (wrapper) {
	var page = itds.ui.make_app_page({
		parent: wrapper,
		title: __("Download Backups"),
		single_column: true,
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		itds.set_route("Form", "System Settings").then(() => {
			cur_frm.scroll_to_field("backup_limit");
		});
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		itds.call({
			method: "itds.desk.page.backups.backups.schedule_files_backup",
			args: { user_email: itds.session.user_email },
		});
	});

	page.add_inner_button(__("Get Backup Encryption Key"), function () {
		if (itds.user.has_role("System Manager")) {
			itds.verify_password(function () {
				itds.call({
					method: "itds.utils.backups.get_backup_encryption_key",
					callback: function (r) {
						itds.msgprint({
							title: __("Backup Encryption Key"),
							message: __(r.message),
							indicator: "blue",
						});
					},
				});
			});
		} else {
			itds.msgprint({
				title: __("Error"),
				message: __("System Manager privileges required."),
				indicator: "red",
			});
		}
	});

	itds.breadcrumbs.add("Setup");

	$(itds.render_template("backups")).appendTo(page.body.addClass("no-border"));
};
