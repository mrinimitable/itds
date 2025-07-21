# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds
from itds.utils import strip_html_tags
from itds.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = itds._dict()
	if hasattr(itds.local, "message"):
		message_context["header"] = itds.local.message_title
		message_context["title"] = strip_html_tags(itds.local.message_title)
		message_context["message"] = itds.local.message
		if hasattr(itds.local, "message_success"):
			message_context["success"] = itds.local.message_success

	elif itds.local.form_dict.id:
		message_id = itds.local.form_dict.id
		key = f"message_id:{message_id}"
		message = itds.cache.get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				itds.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(itds.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(itds.form_dict.message)

	return message_context
