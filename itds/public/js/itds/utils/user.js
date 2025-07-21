itds.user_info = function (uid) {
	if (!uid) uid = itds.session.user;

	let user_info;
	if (!(itds.boot.user_info && itds.boot.user_info[uid])) {
		user_info = { fullname: uid || "Unknown" };
	} else {
		user_info = itds.boot.user_info[uid];
	}

	user_info.abbr = itds.get_abbr(user_info.fullname);
	user_info.color = itds.get_palette(user_info.fullname);

	return user_info;
};

itds.update_user_info = function (user_info) {
	for (let user in user_info) {
		if (itds.boot.user_info[user]) {
			Object.assign(itds.boot.user_info[user], user_info[user]);
		} else {
			itds.boot.user_info[user] = user_info[user];
		}
	}
};

itds.provide("itds.user");

$.extend(itds.user, {
	name: "Guest",
	full_name: function (uid) {
		return uid === itds.session.user
			? __(
					"You",
					null,
					"Name of the current user. For example: You edited this 5 hours ago."
			  )
			: itds.user_info(uid).fullname;
	},
	image: function (uid) {
		return itds.user_info(uid).image;
	},
	abbr: function (uid) {
		return itds.user_info(uid).abbr;
	},
	has_role: function (rl) {
		if (typeof rl == "string") rl = [rl];
		for (var i in rl) {
			if ((itds.boot ? itds.boot.user.roles : ["Guest"]).indexOf(rl[i]) != -1)
				return true;
		}
	},
	get_desktop_items: function () {
		// hide based on permission
		var modules_list = $.map(itds.boot.allowed_modules, function (icon) {
			var m = icon.module_name;
			var type = itds.modules[m] && itds.modules[m].type;

			if (itds.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if (itds.boot.user.allow_modules.indexOf(m) != -1 || itds.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if (itds.boot.allowed_pages.indexOf(itds.modules[m].link) != -1) ret = m;
			} else if (type === "list") {
				if (itds.model.can_read(itds.modules[m]._doctype)) ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if (
					itds.user.has_role("System Manager") ||
					itds.user.has_role("Administrator")
				)
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function () {
		return itds.user.has_role(["Administrator", "System Manager", "Report Manager"]);
	},

	get_formatted_email: function (email) {
		var fullname = itds.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = "";

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl("%(quote)s%(fullname)s%(quote)s <%(email)s>", {
				fullname: fullname,
				email: email,
				quote: quote,
			});
		}
	},

	get_emails: () => {
		return Object.keys(itds.boot.user_info).map((key) => itds.boot.user_info[key].email);
	},

	/* Normally itds.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (itds.user === 'Administrator')
	 *
	 * itds.user will cast to a string
	 * returning itds.user.name
	 */
	toString: function () {
		return this.name;
	},
});

itds.session_alive = true;
$(document).bind("mousemove", function () {
	if (itds.session_alive === false) {
		$(document).trigger("session_alive");
	}
	itds.session_alive = true;
	if (itds.session_alive_timeout) clearTimeout(itds.session_alive_timeout);
	itds.session_alive_timeout = setTimeout("itds.session_alive=false;", 30000);
});
