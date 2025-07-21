# Copyright (c) 2024, Itds Technologies and contributors
# For license information, please see license.txt

import itds
from itds.core.page.permission_manager.permission_manager import get_permissions
from itds.model.document import Document


class RoleReplication(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		existing_role: DF.Link | None
		new_role: DF.Data | None
	# end: auto-generated types

	@itds.whitelist()
	def replicate_role(self):
		itds.only_for("System Manager")

		new_role = itds.db.get_value("Role", self.new_role, "name")
		if not new_role:
			new_role = itds.get_doc({"doctype": "Role", "role_name": self.new_role}).insert().name

		perms = get_permissions(role=self.existing_role)
		for perm in perms:
			perm.update(
				{
					"name": None,
					"creation": None,
					"modified": None,
					"modified_by": None,
					"owner": None,
					"linked_doctypes": None,
					"role": new_role,
				}
			)
			itds.get_doc({"doctype": "Custom DocPerm", **perm}).insert()
