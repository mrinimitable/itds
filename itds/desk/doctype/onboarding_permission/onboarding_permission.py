# Copyright (c) 2020, Itds Technologies and contributors
# License: MIT. See LICENSE

# import itds
from itds.model.document import Document


class OnboardingPermission(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		role: DF.Link
	# end: auto-generated types

	pass
