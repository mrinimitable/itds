# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from contextlib import contextmanager
from pathlib import Path

import itds
from itds.tests import IntegrationTestCase
from itds.website.doctype.website_theme.website_theme import (
	after_migrate,
	get_active_theme,
	get_scss_paths,
)


@contextmanager
def website_theme_fixture(**theme):
	test_theme = "test-theme"

	itds.delete_doc_if_exists("Website Theme", test_theme)
	theme = itds.get_doc(doctype="Website Theme", theme=test_theme, **theme)
	theme.insert()
	yield theme
	itds.db.set_single_value("Website Settings", "website_theme", "Standard")
	theme.delete()


def get_theme_file(theme):
	return Path(itds.get_site_path("public", theme.theme_url[1:]))


class TestWebsiteTheme(IntegrationTestCase):
	def test_website_theme(self):
		with website_theme_fixture(
			google_font="Inter",
			custom_scss="body { font-size: 16.5px; }",  # this will get minified!
		) as theme:
			theme_path = get_theme_file(theme)
			with open(theme_path) as theme_file:
				css = theme_file.read()

			self.assertTrue("body{font-size:16.5px}" in css)
			self.assertTrue("fonts.googleapis.com" in css)

	def test_get_scss_paths(self):
		self.assertIn("itds/public/scss/website.bundle", get_scss_paths())

	def test_imports_to_ignore(self):
		with website_theme_fixture(ignored_apps=[{"app": "itds"}]) as theme:
			self.assertTrue('@import "itds/public/scss/website"' not in theme.theme_scss)

	def test_backup_files(self):
		with website_theme_fixture(custom_scss="body { font-size: 16.5px; }") as theme:
			first = get_theme_file(theme)
			second = get_theme_file(theme.save())
			self.assertTrue(first.exists() and second.exists())

			third = get_theme_file(theme.save())
			fourth = get_theme_file(theme.save())
			self.assertFalse(first.exists())
			self.assertTrue(second.exists() and third.exists() and fourth.exists())

	def test_after_migrate_hook(self):
		with website_theme_fixture(google_font="Inter") as theme:
			theme.set_as_default()
			before = get_active_theme().theme_url
			after_migrate()
			after = get_active_theme().theme_url
			self.assertNotEqual(before, after)
