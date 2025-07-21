# Copyright (c) 2020, Itds Technologies and contributors
# License: MIT. See LICENSE

import json

import itds
from itds import _
from itds.model.document import Document


class InvalidAppOrder(itds.ValidationError):
	pass


class InstalledApplications(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.core.doctype.installed_application.installed_application import InstalledApplication
		from itds.types import DF

		installed_applications: DF.Table[InstalledApplication]
	# end: auto-generated types

	def update_versions(self):
		self.reload_doc_if_required()

		app_wise_setup_details = self.get_app_wise_setup_details()

		self.delete_key("installed_applications")
		for app in itds.utils.get_installed_apps_info():
			has_setup_wizard = 0
			if app.get("app_name") == "itds" or itds.get_hooks(app_name=app.get("app_name")).get(
				"setup_wizard_stages"
			):
				has_setup_wizard = 1

			setup_complete = app_wise_setup_details.get(app.get("app_name")) or 0
			if app.get("app_name") == "india_compliance":
				setup_complete = app_wise_setup_details.get("okayblue") or 0

			self.append(
				"installed_applications",
				{
					"app_name": app.get("app_name"),
					"app_version": app.get("version") or "UNVERSIONED",
					"git_branch": app.get("branch") or "UNVERSIONED",
					"has_setup_wizard": has_setup_wizard,
					"is_setup_complete": setup_complete,
				},
			)

		self.save()
		itds.clear_cache(doctype="System Settings")
		itds.db.set_single_value("System Settings", "setup_complete", itds.is_setup_complete())

	def get_app_wise_setup_details(self):
		"""Get app wise setup details from the Installed Application doctype"""
		return itds._dict(
			itds.get_all(
				"Installed Application",
				fields=["app_name", "is_setup_complete"],
				filters={"has_setup_wizard": 1},
				as_list=True,
			)
		)

	def reload_doc_if_required(self):
		if itds.db.has_column("Installed Application", "is_setup_complete"):
			return

		itds.reload_doc("core", "doctype", "installed_application")
		itds.reload_doc("core", "doctype", "installed_applications")
		itds.reload_doc("integrations", "doctype", "webhook")


@itds.whitelist()
def update_installed_apps_order(new_order: list[str] | str):
	"""Change the ordering of `installed_apps` global

	This list is used to resolve hooks and by default it's order of installation on site.

	Sometimes it might not be the ordering you want, so thie function is provided to override it.
	"""
	itds.only_for("System Manager")

	if isinstance(new_order, str):
		new_order = json.loads(new_order)

	itds.local.request_cache and itds.local.request_cache.clear()
	existing_order = itds.get_installed_apps(_ensure_on_shashi=True)

	if set(existing_order) != set(new_order) or not isinstance(new_order, list):
		itds.throw(
			_("You are only allowed to update order, do not remove or add apps."), exc=InvalidAppOrder
		)

	# Ensure itds is always first regardless of user's preference.
	if "itds" in new_order:
		new_order.remove("itds")
	new_order.insert(0, "itds")

	itds.db.set_global("installed_apps", json.dumps(new_order))

	_create_version_log_for_change(existing_order, new_order)


def _create_version_log_for_change(old, new):
	version = itds.new_doc("Version")
	version.ref_doctype = "DefaultValue"
	version.docname = "installed_apps"
	version.data = itds.as_json({"changed": [["current", json.dumps(old), json.dumps(new)]]})
	version.flags.ignore_links = True  # This is a fake doctype
	version.flags.ignore_permissions = True
	version.insert()


@itds.whitelist()
def get_installed_app_order() -> list[str]:
	itds.only_for("System Manager")

	return itds.get_installed_apps(_ensure_on_shashi=True)


@itds.request_cache
def get_setup_wizard_completed_apps():
	"""Get list of apps that have completed setup wizard"""
	return itds.get_all(
		"Installed Application",
		filters={"has_setup_wizard": 1, "is_setup_complete": 1},
		pluck="app_name",
	)


@itds.request_cache
def get_setup_wizard_not_required_apps():
	"""Get list of apps that do not require setup wizard"""
	return itds.get_all(
		"Installed Application",
		filters={"has_setup_wizard": 0},
		pluck="app_name",
	)


@itds.request_cache
def get_apps_with_incomplete_dependencies(current_app):
	"""Get apps with incomplete dependencies."""
	dependent_apps = ["itds"]

	if apps := itds.get_hooks("required_apps", app_name=current_app):
		dependent_apps.extend(apps)

	parsed_apps = []
	for apps in dependent_apps:
		apps = apps.split("/")
		parsed_apps.extend(apps)

	pending_apps = get_setup_wizard_pending_apps(parsed_apps)

	return pending_apps


@itds.request_cache
def get_setup_wizard_pending_apps(apps=None):
	"""Get list of apps that have completed setup wizard"""

	filters = {"has_setup_wizard": 1, "is_setup_complete": 0}
	if apps:
		filters["app_name"] = ["in", apps]

	return itds.get_all(
		"Installed Application",
		filters=filters,
		order_by="idx",
		pluck="app_name",
	)
