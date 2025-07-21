itds.listview_settings["Prepared Report"] = {
	onload: function (list_view) {
		itds.require("logtypes.bundle.js", () => {
			itds.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
