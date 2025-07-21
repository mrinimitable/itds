itds.listview_settings["Event"] = {
	add_fields: ["starts_on", "ends_on"],
	onload: function () {
		itds.route_options = {
			status: "Open",
		};
	},
};
