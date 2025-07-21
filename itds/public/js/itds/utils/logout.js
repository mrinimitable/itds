itds.logout = function () {
	itds.call({
		method: "logout",
		callback: function (r) {
			if (r.exc) {
				return;
			}
			window.location.href = "/login";
		},
	});
};
