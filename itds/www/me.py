# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds
import itds.www.list
from itds import _

no_cache = 1


def get_context(context):
	if itds.session.user == "Guest":
		itds.throw(_("You need to be logged in to access this page"), itds.PermissionError)

	context.current_user = itds.get_doc("User", itds.session.user)
	context.show_sidebar = False
