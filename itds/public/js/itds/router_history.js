itds.route_history_queue = [];
const routes_to_skip = ["Form", "social", "setup-wizard", "recorder"];

const save_routes = itds.utils.debounce(() => {
	if (itds.session.user === "Guest") return;
	const routes = itds.route_history_queue;
	if (!routes.length) return;

	itds.route_history_queue = [];

	itds
		.xcall("itds.desk.doctype.route_history.route_history.deferred_insert", {
			routes: routes,
		})
		.catch(() => {
			itds.route_history_queue.concat(routes);
		});
}, 10000);

itds.router.on("change", () => {
	const route = itds.get_route();
	if (is_route_useful(route)) {
		itds.route_history_queue.push({
			creation: itds.datetime.now_datetime(),
			route: itds.get_route_str(),
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === "List" && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}
