# Copyright (c) 2025, Itds Technologies and contributors
# For license information, please see license.txt

import itds
from itds.model.document import Document


class APIRequestLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		method: DF.Data | None
		path: DF.Data | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days: int = 90):
		from itds.query_builder import Interval
		from itds.query_builder.functions import Now

		table = itds.qb.DocType("API Request Log")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
