# Copyright (c) 2015, Itds Technologies and contributors
# License: MIT. See LICENSE

import re

import itds
from itds import _
from itds.defaults import clear_default, set_default
from itds.model.document import Document


class Language(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		based_on: DF.Link | None
		date_format: DF.Literal[
			"", "yyyy-mm-dd", "dd-mm-yyyy", "dd/mm/yyyy", "dd.mm.yyyy", "mm/dd/yyyy", "mm-dd-yyyy"
		]
		enabled: DF.Check
		first_day_of_the_week: DF.Literal[
			"", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
		]
		flag: DF.Data | None
		language_code: DF.Data
		language_name: DF.Data
		number_format: DF.Literal[
			"",
			"#,###.##",
			"#.###,##",
			"# ###.##",
			"# ###,##",
			"#'###.##",
			"#, ###.##",
			"#,##,###.##",
			"#,###.###",
			"#.###",
			"#,###",
		]
		time_format: DF.Literal["", "HH:mm:ss", "HH:mm"]
	# end: auto-generated types

	def validate(self):
		validate_with_regex(self.language_code, "Language Code")

	def before_rename(self, old, new, merge=False):
		validate_with_regex(new, "Name")

	def on_update(self):
		itds.cache.delete_value("languages_with_name")
		itds.client_cache.delete_value("languages")
		self.update_user_defaults()

	def update_user_defaults(self):
		"""Update user defaults for date, time, number format and first day of the week.

		When we change any settings of a language, the defaults for all users with that language
		should be updated.
		"""
		users = itds.get_all("User", filters={"language": self.name}, pluck="name")
		for key in ("date_format", "time_format", "number_format", "first_day_of_the_week"):
			if self.has_value_changed(key):
				for user in users:
					if new_value := self.get(key):
						set_default(key, new_value, user)
					else:
						clear_default(key, parent=user)


def validate_with_regex(name, label):
	pattern = re.compile("^[a-zA-Z]+[-_]*[a-zA-Z]+$")
	if not pattern.match(name):
		itds.throw(
			_(
				"""{0} must begin and end with a letter and can only contain letters, hyphen or underscore."""
			).format(label)
		)


def sync_languages():
	"""Create Language records from itds/geo/languages.csv"""
	from csv import DictReader

	with open(itds.get_app_path("itds", "geo", "languages.csv")) as f:
		reader = DictReader(f)
		for row in reader:
			if not itds.db.exists("Language", row["language_code"]):
				doc = itds.new_doc("Language")
				doc.update(row)
				doc.insert()
