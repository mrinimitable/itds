# Copyright (c) 2021, Itds Technologies and contributors
# License: MIT. See LICENSE

import hashlib

import itds
from itds.model.document import Document
from itds.query_builder import DocType
from itds.utils import cint, now_datetime


class TransactionLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		amended_from: DF.Link | None
		chaining_hash: DF.SmallText | None
		checksum_version: DF.Data | None
		data: DF.LongText | None
		document_name: DF.Data | None
		previous_hash: DF.SmallText | None
		reference_doctype: DF.Data | None
		row_index: DF.Data | None
		timestamp: DF.Datetime | None
		transaction_hash: DF.SmallText | None
	# end: auto-generated types

	def before_insert(self):
		index = get_current_index()
		self.row_index = index
		self.timestamp = now_datetime()
		if index != 1:
			prev_hash = itds.get_all(
				"Transaction Log", filters={"row_index": str(index - 1)}, pluck="chaining_hash", limit=1
			)
			if prev_hash:
				self.previous_hash = prev_hash[0]
			else:
				self.previous_hash = "Indexing broken"
		else:
			self.previous_hash = self.hash_line()
		self.transaction_hash = self.hash_line()
		self.chaining_hash = self.hash_chain()
		self.checksum_version = "v1.0.1"

	def hash_line(self):
		sha = hashlib.sha256()
		sha.update(
			itds.safe_encode(str(self.row_index))
			+ itds.safe_encode(str(self.timestamp))
			+ itds.safe_encode(str(self.data))
		)
		return sha.hexdigest()

	def hash_chain(self):
		sha = hashlib.sha256()
		sha.update(
			itds.safe_encode(str(self.transaction_hash)) + itds.safe_encode(str(self.previous_hash))
		)
		return sha.hexdigest()


def get_current_index():
	series = DocType("Series")
	current = (
		itds.qb.from_(series).where(series.name == "TRANSACTLOG").for_update().select("current")
	).run()

	if current and current[0][0] is not None:
		current = current[0][0]

		itds.db.sql(
			"""UPDATE `tabSeries`
			SET `current` = `current` + 1
			where `name` = 'TRANSACTLOG'"""
		)
		current = cint(current) + 1
	else:
		itds.db.sql("INSERT INTO `tabSeries` (name, current) VALUES ('TRANSACTLOG', 1)")
		current = 1
	return current
