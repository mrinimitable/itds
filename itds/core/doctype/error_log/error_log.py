# Copyright (c) 2015, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds.model.document import Document
from itds.query_builder import Interval
from itds.query_builder.functions import Now


class ErrorLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		error: DF.Code | None
		method: DF.Data | None
		reference_doctype: DF.Link | None
		reference_name: DF.Data | None
		seen: DF.Check
		trace_id: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.method = str(self.method)
		self.error = str(self.error)

		if len(self.method) > 140:
			self.error = f"{self.method}\n{self.error}"
			self.method = self.method[:140]

	def onload(self):
		if not self.seen and not itds.flags.read_only:
			self.db_set("seen", 1, update_modified=0)
			itds.db.commit()

	@staticmethod
	def clear_old_logs(days=30):
		table = itds.qb.DocType("Error Log")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@itds.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	itds.only_for("System Manager")
	itds.db.truncate("Error Log")
