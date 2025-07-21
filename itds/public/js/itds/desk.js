// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

itds.start_app = function () {
	if (!itds.Application) return;
	itds.assets.check();
	itds.provide("itds.app");
	itds.provide("itds.desk");
	itds.app = new itds.Application();
};

$(document).ready(function () {
	if (!itds.utils.supportsES6) {
		itds.msgprint({
			indicator: "red",
			title: __("Browser not supported"),
			message: __(
				"Some of the features might not work in your browser. Please update your browser to the latest version."
			),
		});
	}
	itds.start_app();
});

itds.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		itds.realtime.init();
		itds.model.init();

		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.make_sidebar();
		this.set_favicon();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_copy_doc_listener();
		this.setup_broadcast_listeners();

		itds.ui.keys.setup();

		this.setup_theme();

		// page container
		this.make_page_container();
		this.setup_tours();
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");
		$(document).trigger("app_ready");

		this.show_notices();
		this.show_notes();

		if (itds.ui.startup_setup_dialog && !itds.boot.setup_complete) {
			itds.ui.startup_setup_dialog.pre_show();
			itds.ui.startup_setup_dialog.show();
		}

		// listen to build errors
		this.setup_build_events();

		if (itds.sys_defaults.email_user_password) {
			var email_list = itds.sys_defaults.email_user_password.split(",");
			for (var u in email_list) {
				if (email_list[u] === itds.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new itds.ui.LinkPreview();

		itds.broadcast.emit("boot", {
			csrf_token: itds.csrf_token,
			user: itds.session.user,
		});
	}

	make_sidebar() {
		this.sidebar = new itds.ui.Sidebar({});
	}

	setup_theme() {
		itds.ui.keys.add_shortcut({
			shortcut: "shift+ctrl+g",
			description: __("Switch Theme"),
			action: () => {
				if (itds.theme_switcher && itds.theme_switcher.dialog.is_visible) {
					itds.theme_switcher.hide();
				} else {
					itds.theme_switcher = new itds.ui.ThemeSwitcher();
					itds.theme_switcher.show();
				}
			},
		});

		itds.ui.add_system_theme_switch_listener();
		const root = document.documentElement;

		const observer = new MutationObserver(() => {
			itds.ui.set_theme();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode"],
		});

		itds.ui.set_theme();
	}

	setup_tours() {
		if (
			!window.Cypress &&
			itds.boot.onboarding_tours &&
			itds.boot.user.onboarding_status != null
		) {
			let pending_tours = !itds.boot.onboarding_tours.every(
				(tour) => itds.boot.user.onboarding_status[tour[0]]?.is_complete
			);
			if (pending_tours && itds.boot.onboarding_tours.length > 0) {
				itds.require("onboarding_tours.bundle.js", () => {
					itds.utils.sleep(1000).then(() => {
						itds.ui.init_onboarding_tour();
					});
				});
			}
		}
	}

	show_notices() {
		if (itds.boot.messages) {
			itds.msgprint(itds.boot.messages);
		}

		if (itds.user_roles.includes("System Manager")) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!itds.boot.developer_mode) {
			let console_security_message = __(
				"Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand."
			);
			console.log(`%c${console_security_message}`, "font-size: large");
		}

		itds.realtime.on("version-update", function () {
			var dialog = itds.msgprint({
				message: __(
					"The application has been updated to a new version, please refresh this page"
				),
				indicator: "green",
				title: __("Version Updated"),
			});
			dialog.set_primary_action(__("Refresh"), function () {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});
	}

	set_route() {
		if (itds.boot && localStorage.getItem("session_last_route")) {
			itds.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			itds.router.route();
		}
		itds.router.on("change", () => {
			$(".tooltip").hide();
			if (itds.itds_toolbar && itds.is_mobile()) itds.itds_toolbar.show_app_logo();
		});
	}

	set_password(user) {
		var me = this;
		itds.call({
			method: "itds.core.doctype.user.user.get_email_awaiting",
			args: {
				user: user,
			},
			callback: function (email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt(email_account, user, i);
					}
				}
			},
		});
	}

	email_password_prompt(email_account, user, i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new itds.ui.Dialog({
			title: __("Password missing in Email Account"),
			fields: [
				{
					fieldname: "password",
					fieldtype: "Password",
					label: __(
						"Please enter the password for: <b>{0}</b>",
						[email_id],
						"Email Account"
					),
					reqd: 1,
				},
				{
					fieldname: "submit",
					fieldtype: "Button",
					label: __("Submit", null, "Submit password for Email Account"),
				},
			],
		});
		d.get_input("submit").on("click", function () {
			//setup spinner
			d.hide();
			var s = new itds.ui.Dialog({
				title: __("Checking one moment"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "checking",
					},
				],
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			itds.call({
				method: "itds.email.doctype.email_account.email_account.set_email_password",
				args: {
					email_account: email_account[i]["email_account"],
					password: d.get_value("password"),
				},
				callback: function (passed) {
					s.hide();
					d.hide(); //hide waiting indication
					if (!passed["message"]) {
						itds.show_alert(
							{ message: __("Login Failed please try again"), indicator: "error" },
							5
						);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}
				},
			});
		});
		d.show();
	}
	load_bootinfo() {
		if (itds.boot) {
			this.setup_workspaces();
			itds.model.sync(itds.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			itds.router.setup();
			this.setup_moment();
			if (itds.boot.print_css) {
				itds.dom.set_style(itds.boot.print_css, "print-style");
			}

			let current_app = localStorage.current_app;
			if (current_app) {
				itds.boot.setup_complete =
					itds.boot.setup_wizard_not_required_apps?.includes(current_app) ||
					itds.boot.setup_wizard_completed_apps?.includes(current_app);
			}

			itds.user.name = itds.boot.user.name;
			itds.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		itds.modules = {};
		itds.workspaces = {};
		itds.boot.allowed_workspaces = itds.boot.sidebar_pages.pages;

		for (let page of itds.boot.allowed_workspaces || []) {
			itds.modules[page.module] = page;
			itds.workspaces[itds.router.slug(page.name)] = page;
		}
	}

	load_user_permissions() {
		itds.defaults.load_user_permission_from_boot();

		itds.realtime.on(
			"update_user_permissions",
			itds.utils.debounce(() => {
				itds.defaults.update_user_permissions();
			}, 500)
		);
	}

	check_metadata_cache_status() {
		if (itds.boot.metadata_version != localStorage.metadata_version) {
			itds.assets.clear_local_storage();
			itds.assets.init_local_storage();
		}
	}

	set_globals() {
		itds.session.user = itds.boot.user.name;
		itds.session.logged_in_user = itds.boot.user.name;
		itds.session.user_email = itds.boot.user.email;
		itds.session.user_fullname = itds.user_info().fullname;

		itds.user_defaults = itds.boot.user.defaults;
		itds.user_roles = itds.boot.user.roles;
		itds.sys_defaults = itds.boot.sysdefaults;

		itds.ui.py_date_format = itds.boot.sysdefaults.date_format
			.replace("dd", "%d")
			.replace("mm", "%m")
			.replace("yyyy", "%Y");
		itds.boot.user.last_selected_values = {};
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if (localStorage["page_info"]) {
			itds.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(itds.boot.page_info, function (name, p) {
				if (!page_info[name] || page_info[name].modified != p.modified) {
					delete localStorage["_page:" + name];
				}
				itds.boot.allowed_pages.push(name);
			});
		} else {
			itds.boot.allowed_pages = Object.keys(itds.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(itds.boot.page_info);
	}
	set_as_guest() {
		itds.session.user = "Guest";
		itds.session.user_email = "";
		itds.session.user_fullname = "Guest";

		itds.user_defaults = {};
		itds.user_roles = ["Guest"];
		itds.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			itds.temp_container = $("<div id='temp-container' style='display: none;'>").appendTo(
				"body"
			);
			itds.container = new itds.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if (itds.boot && itds.boot.home_page !== "setup-wizard") {
			itds.itds_toolbar = new itds.ui.toolbar.Toolbar();
		}
	}
	logout() {
		var me = this;
		me.logged_out = true;
		return itds.call({
			method: "logout",
			callback: function (r) {
				if (r.exc) {
					return;
				}

				me.redirect_to_login();
			},
		});
	}
	handle_session_expired() {
		itds.app.redirect_to_login();
	}
	redirect_to_login() {
		window.location.href = `/login?redirect-to=${encodeURIComponent(
			window.location.pathname + window.location.search
		)}`;
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display && !cur_dialog.is_minimized) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(":visible")) {
				cur_frm.page.btn_primary.trigger("click");
			} else if (itds.container.page.save_action) {
				itds.container.page.save_action();
			}
		}, 100);
	}

	show_change_log() {
		var me = this;
		let change_log = itds.boot.change_log;

		// itds.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "OKAYBlue",
		// 	"version": "12.2.0"
		// }];

		if (
			!Array.isArray(change_log) ||
			!change_log.length ||
			window.Cypress ||
			cint(itds.boot.sysdefaults.disable_change_log_notification)
		) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = itds.msgprint({
			message: itds.render_template("change_log", { change_log: change_log }),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function () {
			itds.call({
				method: "itds.utils.change_log.update_last_known_versions",
			});
			me.show_notes();
		};
	}

	show_update_available() {
		if (!itds.boot.has_app_updates) return;
		itds.xcall("itds.utils.change_log.show_update_popup");
	}

	add_browser_class() {
		$("html").addClass(itds.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		itds.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if (itds.boot.notes.length) {
			itds.boot.notes.forEach(function (note) {
				if (!note.seen || note.notify_on_every_login) {
					var d = new itds.ui.Dialog({ content: note.content, title: note.title });
					d.keep_open = true;
					d.msg_area = $('<div class="msgprint">').appendTo(d.body);
					d.msg_area.append(note.content);
					d.onhide = function () {
						note.seen = true;
						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							itds.call({
								method: "itds.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						} else {
							itds.call({
								method: "itds.desk.doctype.note.note.reset_notes",
							});
						}
					};
					d.show();
				}
			});
		}
	}

	setup_build_events() {
		if (itds.boot.developer_mode) {
			itds.require("build_events.bundle.js");
		}
	}

	setup_copy_doc_listener() {
		$("body").on("paste", (e) => {
			try {
				let pasted_data = itds.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					const sleep = itds.utils.sleep;

					itds.dom.freeze(__("Creating {0}", [doc.doctype]) + "...");
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = itds.model.with_doctype(doc.doctype, () => {
							let newdoc = itds.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							newdoc.on_paste_event = true;
							newdoc = JSON.parse(JSON.stringify(newdoc));
							itds.set_route("Form", newdoc.doctype, newdoc.name);
							itds.dom.unfreeze();
						});
						res && res.fail?.(itds.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}

	/// Setup event listeners for events across browser tabs / web workers.
	setup_broadcast_listeners() {
		// booted in another tab -> refresh csrf to avoid invalid requests.
		itds.broadcast.on("boot", ({ csrf_token, user }) => {
			if (user && user != itds.session.user) {
				itds.msgprint({
					message: __(
						"You've logged in as another user from another tab. Refresh this page to continue using system."
					),
					title: __("User Changed"),
					primary_action: {
						label: __("Refresh"),
						action: () => {
							window.location.reload();
						},
					},
				});
				return;
			}

			if (csrf_token) {
				// If user re-logged in then their other tabs won't be usable without this update.
				itds.csrf_token = csrf_token;
			}
		});
	}

	setup_moment() {
		moment.updateLocale("en", {
			week: {
				dow: itds.datetime.get_first_day_of_the_week_index(),
			},
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (itds.boot.timezone_info) {
			moment.tz.add(itds.boot.timezone_info);
		}
	}
};

itds.get_module = function (m, default_module) {
	var module = itds.modules[m] || default_module;
	if (!module) {
		return;
	}

	if (module._setup) {
		return module;
	}

	if (!module.label) {
		module.label = m;
	}

	if (!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
