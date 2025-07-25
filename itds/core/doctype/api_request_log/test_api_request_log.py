# Copyright (c) 2025, Itds Technologies and Contributors
# See license.txt

# import itds
from itds.tests import IntegrationTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestAPIRequestLog(IntegrationTestCase):
	"""
	Integration tests for APIRequestLog.
	Use this class for testing interactions between multiple components.
	"""

	pass
