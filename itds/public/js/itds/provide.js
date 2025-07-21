// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if (!window.itds) window.itds = {};

itds.provide = function (namespace) {
	// docs: create a namespace //
	var nsl = namespace.split(".");
	var parent = window;
	for (var i = 0; i < nsl.length; i++) {
		var n = nsl[i];
		if (!parent[n]) {
			parent[n] = {};
		}
		parent = parent[n];
	}
	return parent;
};

itds.provide("locals");
itds.provide("itds.flags");
itds.provide("itds.settings");
itds.provide("itds.utils");
itds.provide("itds.ui.form");
itds.provide("itds.modules");
itds.provide("itds.templates");
itds.provide("itds.test_data");
itds.provide("itds.utils");
itds.provide("itds.model");
itds.provide("itds.user");
itds.provide("itds.session");
itds.provide("itds._messages");
itds.provide("locals.DocType");

// for listviews
itds.provide("itds.listview_settings");
itds.provide("itds.tour");
itds.provide("itds.listview_parent_route");

// constants
window.NEWLINE = "\n";
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm = null;
