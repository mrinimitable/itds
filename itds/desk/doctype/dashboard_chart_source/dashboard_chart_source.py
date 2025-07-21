# Copyright (c) 2019, Itds Technologies and contributors
# License: MIT. See LICENSE

import shutil
from pathlib import Path

import itds
from itds import _
from itds.model.document import Document
from itds.modules import get_module_path, scrub
from itds.modules.export_file import export_to_files

FOLDER_NAME = "dashboard_chart_source"


@itds.whitelist()
def get_config(name: str) -> str:
	doc: DashboardChartSource = itds.get_doc("Dashboard Chart Source", name)
	return doc.read_config()


class DashboardChartSource(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		module: DF.Link
		source_name: DF.Data
		timeseries: DF.Check
	# end: auto-generated types

	def on_update(self):
		if not itds.request:
			return

		if not itds.conf.developer_mode:
			itds.throw(_("Creation of this document is only permitted in developer mode."))

		export_to_files(record_list=[[self.doctype, self.name]], record_module=self.module, create_init=True)

	def on_trash(self):
		if not itds.conf.developer_mode and not itds.flags.in_migrate:
			itds.throw(_("Deletion of this document is only permitted in developer mode."))

		itds.db.after_commit.add(self.delete_folder)

	def read_config(self) -> str:
		"""Return the config JS file for this dashboard chart source."""
		config_path = self.get_folder_path() / f"{scrub(self.name)}.js"
		return config_path.read_text() if config_path.exists() else ""

	def delete_folder(self):
		"""Delete the folder for this dashboard chart source."""
		path = self.get_folder_path()
		if path.exists():
			shutil.rmtree(path, ignore_errors=True)

	def get_folder_path(self) -> Path:
		"""Return the path of the folder for this dashboard chart source."""
		return Path(get_module_path(self.module)) / FOLDER_NAME / itds.scrub(self.name)
