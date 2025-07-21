# Copyright (c) 2021, Itds Technologies and contributors
# License: MIT. See LICENSE

# import itds
from itds.model.document import Document


class WorkspaceChart(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		chart_name: DF.Link
		label: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
