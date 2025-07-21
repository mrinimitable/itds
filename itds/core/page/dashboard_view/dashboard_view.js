// Copyright (c) 2019, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

itds.provide("itds.dashboards");
itds.provide("itds.dashboards.chart_sources");

itds.pages["dashboard-view"].on_page_load = function (wrapper) {
	itds.ui.make_app_page({
		parent: wrapper,
		title: __("Dashboard"),
		single_column: true,
	});

	itds.dashboard = new Dashboard(wrapper);
	$(wrapper).bind("show", function () {
		itds.dashboard.show();
	});
};

class Dashboard {
	constructor(wrapper) {
		this.wrapper = $(wrapper);
		$(`<div class="dashboard" style="overflow: visible; margin: var(--margin-sm);">
			<div class="dashboard-graph"></div>
		</div>`).appendTo(this.wrapper.find(".page-content").empty());
		this.container = this.wrapper.find(".dashboard-graph");
		this.page = wrapper.page;
	}

	show() {
		this.route = itds.get_route();
		this.set_breadcrumbs();
		if (this.route.length > 1) {
			// from route
			this.show_dashboard(this.route.slice(-1)[0]);
		} else {
			// last opened
			if (itds.last_dashboard) {
				itds.set_re_route("dashboard-view", itds.last_dashboard);
			} else {
				// default dashboard
				itds.db.get_list("Dashboard", { filters: { is_default: 1 } }).then((data) => {
					if (data && data.length) {
						itds.set_re_route("dashboard-view", data[0].name);
					} else {
						// no default, get the latest one
						itds.db.get_list("Dashboard", { limit: 1 }).then((data) => {
							if (data && data.length) {
								itds.set_re_route("dashboard-view", data[0].name);
							} else {
								// create a new dashboard!
								itds.new_doc("Dashboard");
							}
						});
					}
				});
			}
		}
	}

	show_dashboard(current_dashboard_name) {
		if (this.dashboard_name !== current_dashboard_name) {
			this.dashboard_name = current_dashboard_name;
			let title = this.dashboard_name;
			if (!this.dashboard_name.toLowerCase().includes(__("dashboard"))) {
				// ensure dashboard title has "dashboard"
				title = __("{0} Dashboard", [__(title)]);
			}
			this.page.set_title(__(title));
			this.set_dropdown();
			this.container.empty();
			this.refresh();
		}
		this.charts = {};
		itds.last_dashboard = current_dashboard_name;
	}

	set_breadcrumbs() {
		itds.breadcrumbs.add("Desk", "Dashboard");
	}

	refresh() {
		itds.run_serially([() => this.render_cards(), () => this.render_charts()]);
	}

	render_charts() {
		return this.get_permitted_items(
			"itds.desk.doctype.dashboard.dashboard.get_permitted_charts"
		).then((charts) => {
			if (!charts.length) {
				itds.msgprint(
					__("No Permitted Charts on this Dashboard"),
					__("No Permitted Charts")
				);
			}

			itds.dashboard_utils.get_dashboard_settings().then((settings) => {
				let chart_config = settings.chart_config ? JSON.parse(settings.chart_config) : {};
				this.charts = charts.map((chart) => {
					return {
						chart_name: chart.chart,
						label: chart.chart,
						chart_settings: chart_config[chart.chart] || {},
						...chart,
					};
				});

				this.chart_group = new itds.widget.WidgetGroup({
					title: null,
					container: this.container,
					type: "chart",
					columns: 2,
					options: {
						allow_sorting: false,
						allow_create: false,
						allow_delete: false,
						allow_hiding: false,
						allow_edit: false,
					},
					widgets: this.charts,
				});
			});
		});
	}

	render_cards() {
		return this.get_permitted_items(
			"itds.desk.doctype.dashboard.dashboard.get_permitted_cards"
		).then((cards) => {
			if (!cards.length) {
				return;
			}

			this.number_cards = cards.map((card) => {
				return {
					name: card.card,
				};
			});

			this.number_card_group = new itds.widget.WidgetGroup({
				container: this.container,
				type: "number_card",
				columns: 3,
				options: {
					allow_sorting: false,
					allow_create: false,
					allow_delete: false,
					allow_hiding: false,
					allow_edit: false,
				},
				widgets: this.number_cards,
			});
		});
	}

	get_permitted_items(method) {
		return itds
			.xcall(method, {
				dashboard_name: this.dashboard_name,
			})
			.then((items) => {
				return items;
			});
	}

	set_dropdown() {
		this.page.clear_menu();

		this.page.add_menu_item(__("Edit"), () => {
			itds.set_route("Form", "Dashboard", itds.dashboard.dashboard_name);
		});

		this.page.add_menu_item(__("New"), () => {
			itds.new_doc("Dashboard");
		});

		this.page.add_menu_item(__("Refresh All"), () => {
			this.chart_group && this.chart_group.widgets_list.forEach((chart) => chart.refresh());
			this.number_card_group &&
				this.number_card_group.widgets_list.forEach((card) => card.render_card());
		});

		itds.db.get_list("Dashboard").then((dashboards) => {
			dashboards.map((dashboard) => {
				let name = dashboard.name;
				if (name != this.dashboard_name) {
					this.page.add_menu_item(
						name,
						() => itds.set_route("dashboard-view", name),
						1
					);
				}
			});
		});
	}
}
