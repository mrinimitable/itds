# Copyright (c) 2021, Itds Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE
"""
itds.coverage
~~~~~~~~~~~~~~~~

Coverage settings for itds
"""

STANDARD_INCLUSIONS = ["*.py"]

STANDARD_EXCLUSIONS = [
	"*.js",
	"*.xml",
	"*.pyc",
	"*.css",
	"*.less",
	"*.scss",
	"*.vue",
	"*.html",
	"*/test_*",
	"*/node_modules/*",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]

# tested via commands' test suite
TESTED_VIA_CLI = [
	"*/itds/installer.py",
	"*/itds/utils/install.py",
	"*/itds/utils/scheduler.py",
	"*/itds/utils/doctor.py",
	"*/itds/build.py",
	"*/itds/database/__init__.py",
	"*/itds/database/db_manager.py",
	"*/itds/database/**/setup_db.py",
]

ITDS_EXCLUSIONS = [
	"*/tests/*",
	"*/commands/*",
	"*/itds/change_log/*",
	"*/itds/exceptions*",
	"*/itds/desk/page/setup_wizard/setup_wizard.py",
	"*/itds/coverage.py",
	"*itds/setup.py",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
	*TESTED_VIA_CLI,
]


class CodeCoverage:
	"""
	Context manager for handling code coverage.

	This class sets up code coverage measurement for a specific app,
	applying the appropriate inclusion and exclusion patterns.
	"""

	def __init__(self, with_coverage, app, outfile="coverage.xml"):
		self.with_coverage = with_coverage
		self.app = app or "itds"
		self.outfile = outfile

	def __enter__(self):
		if self.with_coverage:
			import os

			from coverage import Coverage

			from itds.utils import get_shashi_path

			# Generate coverage report only for app that is being tested
			source_path = os.path.join(get_shashi_path(), "apps", self.app)
			omit = STANDARD_EXCLUSIONS[:]

			if self.app == "itds":
				omit.extend(ITDS_EXCLUSIONS)

			self.coverage = Coverage(source=[source_path], omit=omit, include=STANDARD_INCLUSIONS)
			self.coverage.start()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if self.with_coverage:
			self.coverage.stop()
			self.coverage.save()
			self.coverage.xml_report(outfile=self.outfile)
			print("Saved Coverage")
