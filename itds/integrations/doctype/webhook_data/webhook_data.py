# Copyright (c) 2017, Itds Technologies and contributors
# License: MIT. See LICENSE

# import itds
from itds.model.document import Document


class WebhookData(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		fieldname: DF.Literal[None]
		key: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
