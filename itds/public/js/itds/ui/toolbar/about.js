itds.provide("itds.ui.misc");
itds.ui.misc.about = function () {
	if (!itds.ui.misc.about_dialog) {
		var d = new itds.ui.Dialog({ title: __("Itds Framework") });

		$(d.body).html(
			repl(
				`<div>
					<p>${__("Open Source Applications for the Web")}</p>
					<p><i class='fa fa-globe fa-fw'></i>
						${__("Website")}:
						<a href='https://itdsframework.com' target='_blank'>https://itdsframework.com</a></p>
					<p><i class='fa fa-github fa-fw'></i>
						${__("Source")}:
						<a href='https://github.com/mrinimitable' target='_blank'>https://github.com/mrinimitable</a></p>
					<p><i class='fa fa-graduation-cap fa-fw'></i>
						Itds School: <a href='https://itds.school' target='_blank'>https://itds.school</a></p>
					<p><i class='fa fa-linkedin fa-fw'></i>
						Linkedin: <a href='https://linkedin.com/company/itds-tech' target='_blank'>https://linkedin.com/company/itds-tech</a></p>
					<p><i class='fa fa-twitter fa-fw'></i>
						Twitter: <a href='https://twitter.com/itdstech' target='_blank'>https://twitter.com/itdstech</a></p>
					<p><i class='fa fa-youtube fa-fw'></i>
						YouTube: <a href='https://www.youtube.com/@itdstech' target='_blank'>https://www.youtube.com/@itdstech</a></p>
					<hr>
					<h4>${__("Installed Apps")}</h4>
					<div id='about-app-versions'>${__("Loading versions...")}</div>
					<p>
						<b>
							<a href="/attribution" target="_blank" class="text-muted">
								${__("Dependencies & Licenses")}
							</a>
						</b>
					</p>
					<hr>
					<p class='text-muted'>${__("&copy; Itds Technologies Pvt. Ltd. and contributors")} </p>
					</div>`,
				itds.app
			)
		);

		itds.ui.misc.about_dialog = d;

		itds.ui.misc.about_dialog.on_page_show = function () {
			if (!itds.versions) {
				itds.call({
					method: "itds.utils.change_log.get_versions",
					callback: function (r) {
						show_versions(r.message);
					},
				});
			} else {
				show_versions(itds.versions);
			}
		};

		var show_versions = function (versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function (i, key) {
				var v = versions[key];
				let text;
				if (v.branch) {
					text = $.format("<p><b>{0}:</b> v{1} ({2})<br></p>", [
						v.title,
						v.branch_version || v.version,
						v.branch,
					]);
				} else {
					text = $.format("<p><b>{0}:</b> v{1}<br></p>", [v.title, v.version]);
				}
				$(text).appendTo($wrap);
			});

			itds.versions = versions;
		};
	}

	itds.ui.misc.about_dialog.show();
};
