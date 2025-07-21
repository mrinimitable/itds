// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for translation
itds._ = function (txt, replace, context = null) {
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = "";

	let key = txt; // txt.replace(/\n/g, "");
	if (context) {
		translated_text = itds._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = itds._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = itds._;

itds.get_languages = function () {
	if (!itds.languages) {
		itds.languages = [];
		$.each(itds.boot.lang_dict, function (lang, value) {
			itds.languages.push({ label: lang, value: value });
		});
		itds.languages = itds.languages.sort(function (a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return itds.languages;
};
