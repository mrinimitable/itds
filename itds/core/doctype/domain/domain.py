# Copyright (c) 2017, Itds Technologies and contributors
# License: MIT. See LICENSE

import itds
from itds.custom.doctype.custom_field.custom_field import create_custom_fields
from itds.model.document import Document
from itds.utils import cint


class Domain(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		domain: DF.Data
	# end: auto-generated types

	"""Domain documents are created automatically when DocTypes
	with "Restricted" domains are imported during
	installation or migration"""

	def setup_domain(self):
		"""Setup domain icons, permissions, custom fields etc."""
		self.setup_data()
		self.setup_roles()
		self.setup_properties()
		self.set_values()

		if not cint(itds.defaults.get_defaults().setup_complete):
			# if setup not complete, setup desktop etc.
			self.setup_sidebar_items()
			self.set_default_portal_role()

		if self.data.custom_fields:
			create_custom_fields(self.data.custom_fields)

		if self.data.on_setup:
			# custom on_setup method
			itds.get_attr(self.data.on_setup)()

	def remove_domain(self):
		"""Unset domain settings"""
		self.setup_data()

		if self.data.restricted_roles:
			for role_name in self.data.restricted_roles:
				if itds.db.exists("Role", role_name):
					role = itds.get_doc("Role", role_name)
					role.disabled = 1
					role.save()

		self.remove_custom_field()

	def remove_custom_field(self):
		"""Remove custom_fields when disabling domain"""
		if self.data.custom_fields:
			for doctype in self.data.custom_fields:
				custom_fields = self.data.custom_fields[doctype]

				# custom_fields can be a list or dict
				if isinstance(custom_fields, dict):
					custom_fields = [custom_fields]

				for custom_field_detail in custom_fields:
					custom_field_name = itds.db.get_value(
						"Custom Field", dict(dt=doctype, fieldname=custom_field_detail.get("fieldname"))
					)
					if custom_field_name:
						itds.delete_doc("Custom Field", custom_field_name)

	def setup_roles(self):
		"""Enable roles that are restricted to this domain"""
		if self.data.restricted_roles:
			user = itds.get_doc("User", itds.session.user)
			for role_name in self.data.restricted_roles:
				user.append("roles", {"role": role_name})
				if not itds.db.get_value("Role", role_name):
					itds.get_doc(doctype="Role", role_name=role_name).insert()
					continue

				role = itds.get_doc("Role", role_name)
				role.disabled = 0
				role.save()
			user.save()

	def setup_data(self, domain=None):
		"""Load domain info via hooks"""
		self.data = itds.get_domain_data(self.name)

	def get_domain_data(self, module):
		return itds.get_attr(itds.get_hooks("domains")[self.name] + ".data")

	def set_default_portal_role(self):
		"""Set default portal role based on domain"""
		if self.data.get("default_portal_role"):
			itds.db.set_single_value(
				"Portal Settings", "default_role", self.data.get("default_portal_role")
			)

	def setup_properties(self):
		if self.data.properties:
			for args in self.data.properties:
				itds.make_property_setter(args)

	def set_values(self):
		"""set values based on `data.set_value`"""
		if self.data.set_value:
			for args in self.data.set_value:
				itds.reload_doctype(args[0])
				doc = itds.get_doc(args[0], args[1] or args[0])
				doc.set(args[2], args[3])
				doc.save()

	def setup_sidebar_items(self):
		"""Enable / disable sidebar items"""
		if self.data.allow_sidebar_items:
			# disable all
			itds.db.sql("update `tabPortal Menu Item` set enabled=0")

			# enable
			itds.db.sql(
				"""update `tabPortal Menu Item` set enabled=1
				where route in ({})""".format(", ".join(f'"{d}"' for d in self.data.allow_sidebar_items))
			)

		if self.data.remove_sidebar_items:
			# disable all
			itds.db.sql("update `tabPortal Menu Item` set enabled=1")

			# enable
			itds.db.sql(
				"""update `tabPortal Menu Item` set enabled=0
				where route in ({})""".format(", ".join(f'"{d}"' for d in self.data.remove_sidebar_items))
			)
