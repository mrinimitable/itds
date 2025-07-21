itds.listview_settings["Notification Log"] = {
	onload: function (listview) {
		itds.require("logtypes.bundle.js", () => {
			itds.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
