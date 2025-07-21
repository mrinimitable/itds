# Copyright (c) 2019, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds.model.document import Document
from itds.query_builder import Interval
from itds.query_builder.functions import Now


class ScheduledJobLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		debug_log: DF.Code | None
		details: DF.Code | None
		scheduled_job_type: DF.Link
		status: DF.Literal["Scheduled", "Complete", "Failed"]
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=90):
		table = itds.qb.DocType("Scheduled Job Log")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
