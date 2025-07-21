# Copyright (c) 2018, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds.model.document import Document


class ViewLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		viewed_by: DF.Data | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=180):
		from itds.query_builder import Interval
		from itds.query_builder.functions import Now

		table = itds.qb.DocType("View Log")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
