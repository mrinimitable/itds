# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = itds.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = itds._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		itds.response["403"] = 1
		raise itds.PermissionError("No read permission for Page %s" % (page.title or name))


@itds.whitelist(allow_guest=True)
def getpage(name: str):
	"""
	Load the page from `itds.form` and send it via `itds.response`
	"""

	doc = get(name)
	itds.response.docs.append(doc)
