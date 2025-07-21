# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

from os.path import abspath, splitext
from os.path import exists as path_exists
from os.path import join as join_path
from pathlib import Path
from typing import Optional

import itds
from itds import _
from itds.model.document import Document


class WebsiteTheme(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF
		from itds.website.doctype.website_theme_ignore_app.website_theme_ignore_app import (
			WebsiteThemeIgnoreApp,
		)

		background_color: DF.Link | None
		button_gradients: DF.Check
		button_rounded_corners: DF.Check
		button_shadows: DF.Check
		custom: DF.Check
		custom_overrides: DF.Code | None
		custom_scss: DF.Code | None
		dark_color: DF.Link | None
		font_properties: DF.Data | None
		font_size: DF.Data | None
		google_font: DF.Data | None
		ignored_apps: DF.Table[WebsiteThemeIgnoreApp]
		js: DF.Code | None
		light_color: DF.Link | None
		module: DF.Link
		primary_color: DF.Link | None
		text_color: DF.Link | None
		theme: DF.Data
		theme_scss: DF.Code | None
		theme_url: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.validate_if_customizable()
		self.generate_bootstrap_theme()

	def on_update(self):
		if (
			not self.custom
			and itds.local.conf.get("developer_mode")
			and not itds.flags.in_import
			and not itds.in_test
		):
			self.export_doc()

		self.clear_cache_if_current_theme()

	def is_standard_and_not_valid_user(self):
		return (
			not self.custom
			and not itds.local.conf.get("developer_mode")
			and not (itds.flags.in_import or itds.in_test or itds.flags.in_migrate)
		)

	def on_trash(self):
		if self.is_standard_and_not_valid_user():
			itds.throw(_("You are not allowed to delete a standard Website Theme"), itds.PermissionError)

	def validate_if_customizable(self):
		if self.is_standard_and_not_valid_user():
			itds.throw(_("Please Duplicate this Website Theme to customize."))

	def export_doc(self):
		"""Export to standard folder `[module]/website_theme/[name]/[name].json`."""
		from itds.modules.export_file import export_to_files

		export_to_files(record_list=[["Website Theme", self.name]], create_init=True)

	def clear_cache_if_current_theme(self):
		if itds.flags.in_install == "itds":
			return
		website_settings = itds.get_doc("Website Settings", "Website Settings")
		if getattr(website_settings, "website_theme", None) == self.name:
			website_settings.clear_cache()

	def generate_bootstrap_theme(self):
		from subprocess import PIPE, Popen

		# create theme file in site public files folder
		folder_path = abspath(itds.utils.get_files_path("website_theme", is_private=False))
		# create folder if not exist
		itds.create_folder(folder_path)

		if self.custom:
			self.delete_old_theme_files(folder_path)

		# add a random suffix
		suffix = itds.generate_hash(length=8) if self.custom else "style"
		file_name = itds.scrub(self.name) + "_" + suffix + ".css"
		output_path = join_path(folder_path, file_name)

		self.theme_scss = content = get_scss(self)
		content = content.replace("\n", "\\n")
		command = ["node", "generate_bootstrap_theme.js", output_path, content]

		process = Popen(command, cwd=itds.get_app_source_path("itds"), stdout=PIPE, stderr=PIPE)

		stderr = process.communicate()[1]

		if stderr:
			stderr = itds.safe_decode(stderr)
			stderr = stderr.replace("\n", "<br>")
			itds.throw(f'<div style="font-family: monospace;">{stderr}</div>')
		else:
			self.theme_url = "/files/website_theme/" + file_name

		itds.msgprint(_("Compiled Successfully"), alert=True)

	def delete_old_theme_files(self, folder_path):
		import os

		theme_files: list[Path] = []
		for fname in os.listdir(folder_path):
			if fname.startswith(itds.scrub(self.name) + "_") and fname.endswith(".css"):
				theme_files.append(Path(folder_path) / fname)

		theme_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
		# Keep 3 recent files
		for old_file in theme_files[2:]:
			old_file.unlink()

	@itds.whitelist()
	def set_as_default(self):
		self.save()
		website_settings = itds.get_doc("Website Settings")
		website_settings.website_theme = self.name
		website_settings.ignore_validate = True
		website_settings.save()

	@itds.whitelist()
	def get_apps(self):
		from itds.utils.change_log import get_versions

		apps = get_versions()
		return [{"name": app, "title": values["title"]} for app, values in apps.items()]


def get_active_theme() -> Optional["WebsiteTheme"]:
	if website_theme := itds.get_website_settings("website_theme"):
		try:
			return itds.client_cache.get_doc("Website Theme", website_theme)
		except itds.DoesNotExistError:
			itds.clear_last_message()
			pass


def get_scss(website_theme):
	"""
	Render `website_theme_template.scss` with the values defined in Website Theme.

	params:
	website_theme - instance of a Website Theme
	"""
	apps_to_ignore = tuple((d.app + "/") for d in website_theme.ignored_apps)
	available_imports = get_scss_paths()
	imports_to_include = [d for d in available_imports if not d.startswith(apps_to_ignore)]
	context = website_theme.as_dict()
	context["website_theme_scss"] = imports_to_include
	return itds.render_template("itds/website/doctype/website_theme/website_theme_template.scss", context)


def get_scss_paths():
	"""
	Return a set of SCSS import paths from all apps that provide `website.scss`.

	If `$SHASHI_PATH/apps/itds/itds/public/scss/website[.bundle].scss` exists, the
	returned set will contain 'itds/public/scss/website[.bundle]'.
	"""
	import_path_list = []

	scss_files = ["public/scss/website.scss", "public/scss/website.bundle.scss"]
	for app in itds.get_installed_apps():
		for scss_file in scss_files:
			full_path = itds.get_app_path(app, scss_file)
			if path_exists(full_path):
				import_path = splitext(join_path(app, scss_file))[0]
				import_path_list.append(import_path)

	return import_path_list


def after_migrate():
	"""
	Regenerate Active Theme CSS file after migration.

	Necessary to reflect possible changes in the imported SCSS files. Called at
	the end of every `shashi migrate`.
	"""
	website_theme = itds.db.get_single_value("Website Settings", "website_theme")
	if not website_theme or website_theme == "Standard":
		return

	doc = itds.get_doc("Website Theme", website_theme)
	doc.save()  # Just re-saving re-generates the theme.
