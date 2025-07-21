# Copyright (c) 2021, Itds Technologies and contributors
# License: MIT. See LICENSE
from tenacity import retry, retry_if_exception_type, stop_after_attempt

import itds
from itds.model.document import Document
from itds.utils import cstr


class AccessLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		columns: DF.HTMLEditor | None
		export_from: DF.Data | None
		file_type: DF.Data | None
		filters: DF.Code | None
		method: DF.Data | None
		page: DF.HTMLEditor | None
		reference_document: DF.Data | None
		report_name: DF.Data | None
		timestamp: DF.Datetime | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from itds.query_builder import Interval
		from itds.query_builder.functions import Now

		table = itds.qb.DocType("Access Log")
		itds.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@itds.whitelist()
@itds.write_only()
@retry(
	stop=stop_after_attempt(3),
	retry=retry_if_exception_type(itds.DuplicateEntryError),
	reraise=True,
)
def make_access_log(
	doctype=None,
	document=None,
	method=None,
	file_type=None,
	report_name=None,
	filters=None,
	page=None,
	columns=None,
):
	access_log = itds.get_doc(
		{
			"doctype": "Access Log",
			"user": itds.session.user,
			"export_from": doctype,
			"reference_document": document,
			"file_type": file_type,
			"report_name": report_name,
			"page": page,
			"method": method,
			"filters": cstr(filters) or None,
			"columns": columns,
		}
	)

	if not itds.in_test:
		access_log.deferred_insert()
	else:
		access_log.db_insert()


# only for backward compatibility
_make_access_log = make_access_log
