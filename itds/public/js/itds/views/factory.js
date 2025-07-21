// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

itds.provide("itds.pages");
itds.provide("itds.views");

itds.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		this.route = itds.get_route();
		this.page_name = itds.get_route_str();

		if (this.before_show && this.before_show() === false) return;

		if (itds.pages[this.page_name]) {
			itds.container.change_to(this.page_name);
			if (this.on_show) {
				this.on_show();
			}
		} else {
			if (this.route[1]) {
				this.make(this.route);
			} else {
				itds.show_not_found(this.route);
			}
		}
	}

	make_page(double_column, page_name, sidebar_postition) {
		return itds.make_page(double_column, page_name, sidebar_postition);
	}
};

itds.make_page = function (double_column, page_name, sidebar_position) {
	if (!page_name) {
		page_name = itds.get_route_str();
	}

	const page = itds.container.add_page(page_name);

	itds.ui.make_app_page({
		parent: page,
		single_column: !double_column,
		sidebar_position: sidebar_position,
		disable_sidebar_toggle: !sidebar_position,
	});

	itds.container.change_to(page_name);
	return page;
};
