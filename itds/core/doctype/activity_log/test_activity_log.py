# Copyright (c) 2015, Itds Technologies and Contributors
# License: MIT. See LICENSE
import time

import itds
from itds.auth import CookieManager, LoginManager
from itds.tests import IntegrationTestCase


class TestActivityLog(IntegrationTestCase):
	def setUp(self) -> None:
		itds.set_user("Administrator")

	def test_activity_log(self):
		# test user login log
		itds.local.form_dict = itds._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": self.ADMIN_PASSWORD or "admin",
				"usr": "Administrator",
			}
		)

		itds.local.request_ip = "127.0.0.1"
		itds.local.cookie_manager = CookieManager()
		itds.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(itds.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		itds.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		itds.form_dict.update({"pwd": "password"})
		self.assertRaises(itds.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		itds.local.form_dict = itds._dict()

	def get_auth_log(self, operation="Login"):
		names = itds.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		return itds.get_doc("Activity Log", name)

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		itds.local.form_dict = itds._dict(
			{"cmd": "login", "sid": "Guest", "pwd": self.ADMIN_PASSWORD, "usr": "Administrator"}
		)

		itds.local.request_ip = "127.0.0.1"
		itds.local.cookie_manager = CookieManager()
		itds.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		itds.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		itds.form_dict.update({"pwd": "password"})
		self.assertRaises(itds.AuthenticationError, LoginManager)
		self.assertRaises(itds.AuthenticationError, LoginManager)
		self.assertRaises(itds.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(itds.AuthenticationError, LoginManager)
		self.assertRaises(itds.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(itds.AuthenticationError, LoginManager)

		itds.local.form_dict = itds._dict()


def update_system_settings(args):
	doc = itds.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
