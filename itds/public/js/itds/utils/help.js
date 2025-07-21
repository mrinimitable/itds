// Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

itds.provide("itds.help");

itds.help.youtube_id = {};

itds.help.has_help = function (doctype) {
	return itds.help.youtube_id[doctype];
};

itds.help.show = function (doctype) {
	if (itds.help.youtube_id[doctype]) {
		itds.help.show_video(itds.help.youtube_id[doctype]);
	}
};

itds.help.show_video = function (youtube_id, title) {
	if (itds.utils.is_url(youtube_id)) {
		const expression =
			'(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (itds.help_feedback_link || "")
	let dialog = new itds.ui.Dialog({
		title: title || __("Help"),
		size: "large",
	});

	let video = $(
		`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`
	);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr;
	itds.utils.load_video_player().then(() => {
		plyr = new itds.Plyr(video[0], {
			hideControls: true,
			resetOnEnd: true,
		});
	});

	dialog.onhide = () => {
		plyr?.destroy();
	};
};

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && itds.help.show(doctype);
});
