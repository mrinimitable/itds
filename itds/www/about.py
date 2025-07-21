# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds

sitemap = 1


def get_context(context):
	context.doc = itds.get_cached_doc("About Us Settings")

	return context
