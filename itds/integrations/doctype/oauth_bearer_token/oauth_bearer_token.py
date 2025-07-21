# Copyright (c) 2015, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds.model.document import Document
from itds.query_builder import Interval
from itds.query_builder.functions import Now
from itds.utils.data import add_to_date


class OAuthBearerToken(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		access_token: DF.Data | None
		client: DF.Link | None
		expiration_time: DF.Datetime | None
		expires_in: DF.Int
		refresh_token: DF.Data | None
		scopes: DF.Text | None
		status: DF.Literal["Active", "Revoked"]
		user: DF.Link
	# end: auto-generated types

	def validate(self):
		if not self.expiration_time:
			self.expiration_time = add_to_date(self.creation, seconds=self.expires_in, as_datetime=True)

	@staticmethod
	def clear_old_logs(days=30):
		table = itds.qb.DocType("OAuth Bearer Token")
		itds.db.delete(
			table,
			filters=(table.expiration_time < (Now() - Interval(days=days))),
		)
