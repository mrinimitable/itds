# Copyright (c) 2024, Itds Technologies and contributors
# For license information, please see license.txt

import itds
from itds.model.document import Document


class UTMMedium(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		description: DF.SmallText | None
		slug: DF.Data | None
	# end: auto-generated types

	def before_save(self):
		if self.slug:
			self.slug = itds.utils.slug(self.slug)
