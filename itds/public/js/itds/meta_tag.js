itds.provide("itds.model");
itds.provide("itds.utils");

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
itds.utils.set_meta_tag = function (route) {
	itds.db.exists("Website Route Meta", route).then((exists) => {
		if (exists) {
			itds.set_route("Form", "Website Route Meta", route);
		} else {
			// new doc
			const doc = itds.model.get_new_doc("Website Route Meta");
			doc.__newname = route;
			itds.set_route("Form", doc.doctype, doc.name);
		}
	});
};
