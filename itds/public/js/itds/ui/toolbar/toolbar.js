// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

itds.provide("itds.ui.toolbar");
itds.provide("itds.search");

itds.ui.toolbar.Toolbar = class {
	constructor() {
		$("header").replaceWith(
			itds.render_template("navbar", {
				avatar: itds.avatar(itds.session.user, "avatar-medium"),
				navbar_settings: itds.boot.navbar_settings,
			})
		);
		$(".dropdown-toggle").dropdown();
		$("#toolbar-user a[href]").click(function () {
			$(this).closest(".dropdown-menu").prev().dropdown("toggle");
		});

		this.setup_awesomebar();
		this.setup_notifications();
		this.setup_help();
		this.setup_read_only_mode();
		this.setup_announcement_widget();
		this.make();
	}

	make() {
		this.bind_events();
		$(document).trigger("toolbar_setup");
		this.navbar = $(".navbar-brand");
		this.app_logo = this.navbar.find(".app-logo");
		this.bind_click();
	}
	bind_click() {
		$(".navbar-brand .app-logo").on("click", (event) => {
			itds.app.sidebar.set_height();
			itds.app.sidebar.toggle_sidebar();
			itds.app.sidebar.prevent_scroll();
		});
	}
	bind_events() {
		// clear all custom menus on page change
		$(document).on("page-change", function () {
			$("header .navbar .custom-menu").remove();
		});

		//focus search-modal on show in mobile view
		$("#search-modal").on("shown.bs.modal", function () {
			var search_modal = $(this);
			setTimeout(function () {
				search_modal.find("#modal-search").focus();
			}, 300);
		});
	}

	setup_read_only_mode() {
		if (!itds.boot.read_only) return;

		$("header .read-only-banner").tooltip({
			delay: { show: 600, hide: 100 },
			trigger: "hover",
		});
	}

	setup_announcement_widget() {
		let current_announcement = itds.boot.navbar_settings.announcement_widget;

		if (!current_announcement) return;

		// If an unseen announcement is added, overlook dismiss flag
		if (current_announcement != localStorage.getItem("announcement_widget")) {
			localStorage.removeItem("dismissed_announcement_widget");
			localStorage.setItem("announcement_widget", current_announcement);
		}

		// When an announcement is closed, add dismiss flag
		if (!localStorage.getItem("dismissed_announcement_widget")) {
			let announcement_widget = $(".announcement-widget");
			let close_message = announcement_widget.find(".close-message");
			close_message.on(
				"click",
				() =>
					localStorage.setItem("dismissed_announcement_widget", true) ||
					announcement_widget.addClass("hidden")
			);
		}
	}

	setup_help() {
		if (!itds.boot.desk_settings.notifications) {
			// hide the help section
			$(".navbar .vertical-bar").removeClass("d-sm-block");
			$(".dropdown-help").removeClass("d-lg-block");
			return;
		}
		itds.provide("itds.help");
		itds.help.show_results = show_results;

		this.search = new itds.search.SearchDialog();
		itds.provide("itds.searchdialog");
		itds.searchdialog.search = this.search;

		$(".dropdown-help .dropdown-toggle").on("click", function () {
			$(".dropdown-help input").focus();
		});

		$(".dropdown-help .dropdown-menu").on("click", "input, button", function (e) {
			e.stopPropagation();
		});

		$("#input-help").on("keydown", function (e) {
			if (e.which == 13) {
				$(this).val("");
			}
		});

		$(document).on("page-change", function () {
			var $help_links = $(".dropdown-help #help-links");
			$help_links.html("");

			var route = itds.get_route_str();
			var breadcrumbs = route.split("/");

			var links = [];
			for (let i = 0; i < breadcrumbs.length; i++) {
				var r = route.split("/", i + 1);
				var key = r.join("/");
				var help_links = itds.help.help_links[key] || [];
				links = $.merge(links, help_links);
			}

			if (links.length === 0) {
				$help_links.next().hide();
			} else {
				$help_links.next().show();
			}

			for (let i = 0; i < links.length; i++) {
				var link = links[i];
				var url = link.url;
				$("<a>", {
					href: url,
					class: "dropdown-item",
					text: __(link.label),
					target: "_blank",
				}).appendTo($help_links);
			}

			$(".dropdown-help .dropdown-menu").on("click", "a", show_results);
		});

		var $result_modal = itds.get_modal("", "");
		$result_modal.addClass("help-modal");

		$(document).on("click", ".help-modal a", show_results);

		function show_results(e) {
			//edit links
			var href = e.target.href;
			if (href.indexOf("blob") > 0) {
				window.open(href, "_blank");
			}
			var path = $(e.target).attr("data-path");
			if (path) {
				e.preventDefault();
			}
		}
	}

	setup_awesomebar() {
		if (itds.boot.desk_settings.search_bar) {
			let awesome_bar = new itds.search.AwesomeBar();
			awesome_bar.setup("#navbar-search");

			itds.search.utils.make_function_searchable(
				itds.utils.generate_tracking_url,
				__("Generate Tracking URL")
			);
			if (itds.model.can_read("RQ Job")) {
				itds.search.utils.make_function_searchable(function () {
					itds.set_route("List", "RQ Job");
				}, __("Background Jobs"));
			}
		}
	}

	setup_notifications() {
		if (itds.boot.desk_settings.notifications && itds.session.user !== "Guest") {
			this.notifications = new itds.ui.Notifications();
		}
	}

	add_back_button() {
		if (!itds.is_mobile()) return;
		this.navbar = $(".navbar-brand");
		let list_view_route = `/app/${itds.get_route()[1].toLowerCase()}`;
		this.navbar.attr("href", list_view_route);
		this.navbar.html("");
		this.navbar.html(itds.utils.icon("arrow-left", "md"));
	}
	show_app_logo() {
		let route = itds.get_route();
		if (route[0] == "List") {
			this.navbar.html("");
			this.navbar.html(this.app_logo);
			this.navbar.attr("href", "");
			this.bind_click();
		} else if (route[0] == "Form") {
			this.add_back_button();
		}
	}
	set_app_logo(logo_url) {
		$(".navbar-brand .app-logo").attr("src", logo_url);
	}
};

$.extend(itds.ui.toolbar, {
	add_dropdown_button: function (parent, label, click, icon) {
		var menu = itds.ui.toolbar.get_menu(parent);
		if (menu.find("li:not(.custom-menu)").length && !menu.find(".divider").length) {
			itds.ui.toolbar.add_menu_divider(menu);
		}

		return $(
			'<li class="custom-menu"><a><i class="fa-fw ' + icon + '"></i> ' + label + "</a></li>"
		)
			.insertBefore(menu.find(".divider"))
			.find("a")
			.click(function () {
				click.apply(this);
			});
	},
	get_menu: function (label) {
		return $("#navbar-" + label.toLowerCase());
	},
	add_menu_divider: function (menu) {
		menu = typeof menu == "string" ? itds.ui.toolbar.get_menu(menu) : menu;

		$('<li class="divider custom-menu"></li>').prependTo(menu);
	},
	add_icon_link(route, icon, index, class_name) {
		let parent_element = $(".navbar-right").get(0);
		let new_element = $(`<li class="${class_name}">
			<a class="btn" href="${route}" title="${itds.utils.to_title_case(
			class_name,
			true
		)}" aria-haspopup="true" aria-expanded="true">
				<div>
					<i class="octicon ${icon}"></i>
				</div>
			</a>
		</li>`).get(0);

		parent_element.insertBefore(new_element, parent_element.children[index]);
	},
	toggle_full_width() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || "false");
		fullwidth = !fullwidth;
		localStorage.container_fullwidth = fullwidth;
		itds.ui.toolbar.set_fullwidth_if_enabled();
		$(document.body).trigger("toggleFullWidth");
	},
	set_fullwidth_if_enabled() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || "false");
		$(document.body).toggleClass("full-width", fullwidth);
	},
	show_shortcuts(e) {
		e.preventDefault();
		itds.ui.keys.show_keyboard_shortcut_dialog();
		return false;
	},
});

itds.ui.toolbar.clear_cache = itds.utils.throttle(function () {
	itds.assets.clear_local_storage();
	itds.xcall("itds.sessions.clear").then((message) => {
		itds.show_alert({
			message: message,
			indicator: "info",
		});
		location.reload(true);
	});
}, 10000);

itds.ui.toolbar.show_about = function () {
	try {
		itds.ui.misc.about();
	} catch (e) {
		console.log(e);
	}
	return false;
};

itds.ui.toolbar.route_to_user = function () {
	itds.set_route("Form", "User", itds.session.user);
};

itds.ui.toolbar.view_website = function () {
	let website_tab = window.open();
	website_tab.opener = null;
	website_tab.location = "/index";
};

itds.ui.toolbar.setup_session_defaults = function () {
	let fields = [];
	itds.call({
		method: "itds.core.doctype.session_default_settings.session_default_settings.get_session_default_values",
		callback: function (data) {
			fields = JSON.parse(data.message);
			let perms = itds.perm.get_perm("Session Default Settings");
			//add settings button only if user is a System Manager or has permission on 'Session Default Settings'
			if (itds.user_roles.includes("System Manager") || perms[0].read == 1) {
				fields[fields.length] = {
					fieldname: "settings",
					fieldtype: "Button",
					label: __("Settings"),
					click: () => {
						itds.set_route(
							"Form",
							"Session Default Settings",
							"Session Default Settings"
						);
					},
				};
			}
			itds.prompt(
				fields,
				function (values) {
					//if default is not set for a particular field in prompt
					fields.forEach(function (d) {
						if (!values[d.fieldname]) {
							values[d.fieldname] = "";
						}
					});
					itds.call({
						method: "itds.core.doctype.session_default_settings.session_default_settings.set_session_default_values",
						args: {
							default_values: values,
						},
						callback: function (data) {
							if (data.message == "success") {
								itds.show_alert({
									message: __("Session Defaults Saved"),
									indicator: "green",
								});
								itds.ui.toolbar.clear_cache();
							} else {
								itds.show_alert({
									message: __(
										"An error occurred while setting Session Defaults"
									),
									indicator: "red",
								});
							}
						},
					});
				},
				__("Session Defaults"),
				__("Save")
			);
		},
	});
};
