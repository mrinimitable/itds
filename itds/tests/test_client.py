# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors

from unittest.mock import patch

import itds
from itds.tests import IntegrationTestCase
from itds.utils import get_site_url


class TestClient(IntegrationTestCase):
	def test_set_value(self):
		todo = itds.get_doc(doctype="ToDo", description="test").insert()
		itds.set_value("ToDo", todo.name, "description", "test 1")
		self.assertEqual(itds.get_value("ToDo", todo.name, "description"), "test 1")

		itds.set_value("ToDo", todo.name, {"description": "test 2"})
		self.assertEqual(itds.get_value("ToDo", todo.name, "description"), "test 2")

	def test_delete(self):
		from itds.client import delete
		from itds.desk.doctype.note.note import Note

		note = itds.get_doc(
			doctype="Note",
			title=itds.generate_hash(length=8),
			content="test",
			seen_by=[{"user": "Administrator"}],
		).insert()

		child_row_name = note.seen_by[0].name

		with patch.object(Note, "save") as save:
			delete("Note Seen By", child_row_name)
			save.assert_called()

		delete("Note", note.name)

		self.assertFalse(itds.db.exists("Note", note.name))
		self.assertRaises(itds.DoesNotExistError, delete, "Note", note.name)
		self.assertRaises(itds.DoesNotExistError, delete, "Note Seen By", child_row_name)

	def test_http_valid_method_access(self):
		from itds.client import delete
		from itds.handler import execute_cmd

		itds.set_user("Administrator")

		itds.local.request = itds._dict()
		itds.local.request.method = "POST"

		itds.local.form_dict = itds._dict(
			{"doc": dict(doctype="ToDo", description="Valid http method"), "cmd": "itds.client.save"}
		)
		todo = execute_cmd("itds.client.save")

		self.assertEqual(todo.get("description"), "Valid http method")

		delete("ToDo", todo.name)

	def test_http_invalid_method_access(self):
		from itds.handler import execute_cmd

		itds.set_user("Administrator")

		itds.local.request = itds._dict()
		itds.local.request.method = "GET"

		itds.local.form_dict = itds._dict(
			{"doc": dict(doctype="ToDo", description="Invalid http method"), "cmd": "itds.client.save"}
		)

		self.assertRaises(itds.PermissionError, execute_cmd, "itds.client.save")

	def test_run_doc_method(self):
		from itds.handler import execute_cmd

		report = itds.get_doc(
			{
				"doctype": "Report",
				"ref_doctype": "User",
				"report_name": itds.generate_hash(),
				"report_type": "Query Report",
				"is_standard": "No",
				"roles": [{"role": "System Manager"}],
			}
		).insert()

		itds.local.request = itds._dict()
		itds.local.request.method = "GET"

		# Whitelisted, works as expected
		itds.local.form_dict = itds._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "toggle_disable",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		execute_cmd(itds.local.form_dict.cmd)

		# Not whitelisted, throws permission error
		itds.local.form_dict = itds._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "create_report_py",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		self.assertRaises(itds.PermissionError, execute_cmd, itds.local.form_dict.cmd)

	def test_array_values_in_request_args(self):
		import requests

		from itds.auth import CookieManager, LoginManager

		itds.utils.set_request(path="/")
		itds.local.cookie_manager = CookieManager()
		itds.local.login_manager = LoginManager()
		itds.local.login_manager.login_as("Administrator")
		params = {
			"doctype": "DocType",
			"fields": ["name", "modified"],
			"sid": itds.session.sid,
		}
		headers = {
			"accept": "application/json",
			"content-type": "application/json",
		}
		url = get_site_url(itds.local.site)
		url += "/api/method/itds.client.get_list"

		res = requests.post(url, json=params, headers=headers)
		self.assertEqual(res.status_code, 200)
		data = res.json()
		first_item = data["message"][0]
		self.assertTrue("name" in first_item)
		self.assertTrue("modified" in first_item)

	def test_client_get(self):
		from itds.client import get

		todo = itds.get_doc(doctype="ToDo", description="test").insert()
		filters = {"name": todo.name}
		filters_json = itds.as_json(filters)

		self.assertEqual(get("ToDo", filters=filters).description, "test")
		self.assertEqual(get("ToDo", filters=filters_json).description, "test")
		self.assertEqual(get("System Settings", "", "").doctype, "System Settings")
		self.assertEqual(get("ToDo", filters={}), get("ToDo", filters="{}"))
		todo.delete()

	def test_client_validatate_link(self):
		from itds.client import validate_link

		# Basic test
		self.assertTrue(validate_link("User", "Guest"))

		# fixes capitalization
		if itds.db.db_type == "mariadb":
			self.assertEqual(validate_link("User", "GueSt"), {"name": "Guest"})

		# Fetch
		self.assertEqual(validate_link("User", "Guest", fields=["enabled"]), {"name": "Guest", "enabled": 1})

		# Permissions
		with self.set_user("Guest"), self.assertRaises(itds.PermissionError):
			self.assertEqual(
				validate_link("User", "Guest", fields=["enabled"]), {"name": "Guest", "enabled": 1}
			)

	def test_client_insert(self):
		from itds.client import insert

		def get_random_title():
			return f"test-{itds.generate_hash()}"

		# test insert dict
		doc = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(doc)
		self.assertTrue(note1)

		# test insert json
		doc["title"] = get_random_title()
		json_doc = itds.as_json(doc)
		note2 = insert(json_doc)
		self.assertTrue(note2)

		# test insert child doc without parent fields
		child_doc = {"doctype": "Note Seen By", "user": "Administrator"}
		with self.assertRaises(itds.ValidationError):
			insert(child_doc)

		# test insert child doc with parent fields
		child_doc = {
			"doctype": "Note Seen By",
			"user": "Administrator",
			"parenttype": "Note",
			"parent": note1.name,
			"parentfield": "seen_by",
		}
		note3 = insert(child_doc)
		self.assertTrue(note3)

		# cleanup
		itds.delete_doc("Note", note1.name)
		itds.delete_doc("Note", note2.name)

	def test_client_insert_many(self):
		from itds.client import insert, insert_many

		def get_random_title():
			return f"test-{itds.generate_hash(length=5)}"

		# insert a (parent) doc
		note1 = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(note1)

		doc_list = [
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{"doctype": "Note", "title": "not-a-random-title", "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": "another-note-title", "content": "test"},
		]

		# insert all docs
		docs = insert_many(doc_list)

		self.assertEqual(len(docs), 7)
		self.assertEqual(itds.db.get_value("Note", docs[3], "title"), "not-a-random-title")
		self.assertEqual(itds.db.get_value("Note", docs[6], "title"), "another-note-title")
		self.assertIn(note1.name, docs)

		# cleanup
		for doc in docs:
			itds.delete_doc("Note", doc)
