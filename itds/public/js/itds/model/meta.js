// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

itds.provide("itds.meta.docfield_map");
itds.provide("itds.meta.docfield_copy");
itds.provide("itds.meta.docfield_list");
itds.provide("itds.meta.doctypes");
itds.provide("itds.meta.precision_map");

itds.get_meta = function (doctype) {
	if (doctype === "DocType" && itds.meta.__doctype_meta) {
		return itds.meta.__doctype_meta;
	}
	return locals["DocType"] ? locals["DocType"][doctype] : null;
};

$.extend(itds.meta, {
	sync: function (doc) {
		$.each(doc.fields, function (i, df) {
			itds.meta.add_field(df);
		});

		if (doc.__print_formats?.length) itds.model.sync(doc.__print_formats);
		if (doc.__workflow_docs?.length) itds.model.sync(doc.__workflow_docs);
	},

	// build docfield_map and docfield_list
	add_field: function (df) {
		itds.provide("itds.meta.docfield_map." + df.parent);
		itds.meta.docfield_map[df.parent][df.fieldname || df.label] = df;

		if (!itds.meta.docfield_list[df.parent]) itds.meta.docfield_list[df.parent] = [];

		// check for repeat
		for (var i in itds.meta.docfield_list[df.parent]) {
			var d = itds.meta.docfield_list[df.parent][i];
			if (df.fieldname == d.fieldname) return; // no repeat
		}
		itds.meta.docfield_list[df.parent].push(df);
	},

	make_docfield_copy_for: function (doctype, docname, docfield_list = null) {
		var c = itds.meta.docfield_copy;
		if (!c[doctype]) c[doctype] = {};
		if (!c[doctype][docname]) c[doctype][docname] = {};

		docfield_list = docfield_list || itds.meta.docfield_list[doctype] || [];
		for (var i = 0, j = docfield_list.length; i < j; i++) {
			var df = docfield_list[i];
			c[doctype][docname][df.fieldname || df.label] = copy_dict(df);
		}
	},

	get_field: function (doctype, fieldname, name) {
		var out = itds.meta.get_docfield(doctype, fieldname, name);

		// search in standard fields
		if (!out) {
			itds.model.std_fields.every(function (d) {
				if (d.fieldname === fieldname) {
					out = d;
					return false;
				} else {
					return true;
				}
			});
		}
		return out;
	},

	get_docfield: function (doctype, fieldname, name) {
		var fields_dict = itds.meta.get_docfield_copy(doctype, name);
		return fields_dict ? fields_dict[fieldname] : null;
	},

	set_formatter: function (doctype, fieldname, name, formatter) {
		itds.meta.get_docfield(doctype, fieldname, name).formatter = formatter;
	},

	set_indicator_formatter: function (doctype, fieldname, name, get_text, get_color) {
		itds.meta.get_docfield(doctype, fieldname, name).formatter = function (
			value,
			df,
			options,
			doc
		) {
			return repl('<span class="indicator %(color)s">%(name)s</span>', {
				color: get_color(),
				name: get_text(),
			});
		};
	},

	get_docfields: function (doctype, name, filters) {
		var docfield_map = itds.meta.get_docfield_copy(doctype, name);

		var docfields = itds.meta.sort_docfields(docfield_map);

		if (filters) {
			docfields = itds.utils.filter_dict(docfields, filters);
		}

		return docfields;
	},

	get_linked_fields: function (doctype) {
		return $.map(itds.get_meta(doctype).fields, function (d) {
			return d.fieldtype == "Link" ? d.options : null;
		});
	},

	get_fields_to_check_permissions: function (doctype) {
		var fields = $.map(itds.meta.get_docfields(doctype, name), function (df) {
			return df.fieldtype === "Link" && df.ignore_user_permissions !== 1 ? df : null;
		});
		fields = fields.concat({ label: "ID", fieldname: name, options: doctype });
		return fields;
	},

	sort_docfields: function (docs) {
		return $.map(docs, function (d) {
			return d;
		}).sort(function (a, b) {
			return a.idx - b.idx;
		});
	},

	get_docfield_copy: function (doctype, name) {
		if (!name) return itds.meta.docfield_map[doctype];

		if (!(itds.meta.docfield_copy[doctype] && itds.meta.docfield_copy[doctype][name])) {
			itds.meta.make_docfield_copy_for(doctype, name);
		}

		return itds.meta.docfield_copy[doctype][name];
	},

	get_fieldnames: function (doctype, name, filters) {
		return $.map(
			itds.utils.filter_dict(itds.meta.docfield_map[doctype], filters),
			function (df) {
				return df.fieldname;
			}
		);
	},

	has_field: function (dt, fn) {
		let docfield_map = itds.meta.docfield_map[dt];
		return docfield_map && docfield_map[fn];
	},

	get_table_fields: function (dt) {
		return $.map(itds.meta.docfield_list[dt], function (d) {
			return itds.model.table_fields.includes(d.fieldtype) ? d : null;
		});
	},

	get_doctype_for_field: function (doctype, key) {
		var out = null;
		if (itds.model.std_fields_list.includes(key)) {
			// standard
			out = doctype;
		} else if (itds.meta.has_field(doctype, key)) {
			// found in parent
			out = doctype;
		} else {
			itds.meta.get_table_fields(doctype).every(function (d) {
				if (
					itds.meta.has_field(d.options, key) ||
					itds.model.child_table_field_list.includes(key)
				) {
					out = d.options;
					return false;
				}
				return true;
			});

			if (!out) {
				console.log(
					__("Warning: Unable to find {0} in any table related to {1}", [
						key,
						__(doctype),
					])
				);
			}
		}
		return out;
	},

	get_parentfield: function (parent_dt, child_dt) {
		var df = (itds.get_meta(parent_dt).fields || []).filter(
			(df) => itds.model.table_fields.includes(df.fieldtype) && df.options === child_dt
		);
		if (!df.length) throw "parentfield not found for " + parent_dt + ", " + child_dt;
		return df[0].fieldname;
	},

	get_label: function (dt, fn, dn) {
		var standard = {
			name: __("ID"),
			creation: __("Created On"),
			docstatus: __("Document Status"),
			idx: __("Index"),
			modified: __("Last Updated On"),
			modified_by: __("Last Updated By"),
			owner: __("Created By"),
			_user_tags: __("Tags"),
			_liked_by: __("Liked By"),
			_comments: __("Comments"),
			_assign: __("Assigned To"),
		};
		if (standard[fn]) {
			return standard[fn];
		} else {
			var df = this.get_docfield(dt, fn, dn);
			return (df ? df.label : "") || fn;
		}
	},

	get_print_sizes: function () {
		return [
			"A0",
			"A1",
			"A2",
			"A3",
			"A4",
			"A5",
			"A6",
			"A7",
			"A8",
			"A9",
			"B0",
			"B1",
			"B2",
			"B3",
			"B4",
			"B5",
			"B6",
			"B7",
			"B8",
			"B9",
			"B10",
			"C5E",
			"Comm10E",
			"DLE",
			"Executive",
			"Folio",
			"Ledger",
			"Legal",
			"Letter",
			"Tabloid",
			"Custom",
		];
	},

	get_print_formats: function (doctype) {
		var print_format_list = ["Standard"];
		var default_print_format = locals.DocType[doctype].default_print_format;
		let enable_raw_printing = itds.model.get_doc(
			":Print Settings",
			"Print Settings"
		).enable_raw_printing;
		var print_formats = itds
			.get_list("Print Format", { doc_type: doctype })
			.sort(function (a, b) {
				return a > b ? 1 : -1;
			});
		$.each(print_formats, function (i, d) {
			if (
				!print_format_list.includes(d.name) &&
				d.print_format_type !== "JS" &&
				(cint(enable_raw_printing) || !d.raw_printing)
			) {
				print_format_list.push(d.name);
			}
		});

		if (default_print_format && default_print_format != "Standard") {
			var index = print_format_list.indexOf(default_print_format);
			print_format_list.splice(index, 1).sort();
			print_format_list.unshift(default_print_format);
		}

		return print_format_list;
	},

	get_field_currency: function (df, doc) {
		var currency = itds.boot.sysdefaults.currency || "USD";
		if (!doc && cur_frm) doc = cur_frm.doc;
		if (df && df.options) {
			if (df.options.indexOf(":") != -1) {
				var options = df.options.split(":");
				if (options.length == 3) {
					let docname = null;
					if (doc) {
						// get reference record e.g. Company
						docname = doc[options[1]];
						if (!docname && cur_frm) {
							docname = cur_frm.doc[options[1]];
						}
					}
					if (!docname) {
						// Try to get default value, useful for cases like Company overridden in session defaults
						docname = itds.defaults.get_user_default(options[1]);
					}
					currency =
						itds.model.get_value(options[0], docname, options[2]) ||
						itds.model.get_value(":" + options[0], docname, options[2]) ||
						currency;
				}
			} else if (doc && doc[df.options]) {
				currency = doc[df.options];
			} else if (cur_frm && cur_frm.doc[df.options]) {
				currency = cur_frm.doc[df.options];
			}
		}
		return currency;
	},

	get_field_precision: function (df, doc) {
		var precision = null;
		if (df && df.precision) {
			precision = cint(df.precision);
		} else if (df && df.fieldtype === "Currency") {
			precision = cint(itds.defaults.get_default("currency_precision"));
			if (!precision) {
				var number_format = get_number_format();
				var number_format_info = get_number_format_info(number_format);
				precision = number_format_info.precision;
			}
		} else {
			precision = cint(itds.defaults.get_default("float_precision")) || 3;
		}
		return precision;
	},
});
