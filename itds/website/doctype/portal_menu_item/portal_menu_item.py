# Copyright (c) 2015, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds.model.document import Document


class PortalMenuItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		enabled: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_doctype: DF.Link | None
		role: DF.Link | None
		route: DF.Data
		target: DF.Data | None
		title: DF.Data
	# end: auto-generated types

	pass
