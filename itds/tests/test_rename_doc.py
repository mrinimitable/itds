# Copyright (c) 2022, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from random import choice, sample
from unittest.mock import patch

import itds
from itds.core.doctype.doctype.test_doctype import new_doctype
from itds.exceptions import DoesNotExistError
from itds.model.base_document import get_controller
from itds.model.rename_doc import bulk_rename, update_document_title
from itds.modules.utils import get_doc_path
from itds.tests import IntegrationTestCase
from itds.utils import add_to_date, now


@contextmanager
def patch_db(endpoints: list[str] | None = None):
	patched_endpoints = []

	for point in endpoints:
		x = patch(f"itds.db.{point}", new=lambda: True)
		patched_endpoints.append(x)

	savepoint = "SAVEPOINT_for_test_bulk_rename"
	itds.db.savepoint(save_point=savepoint)
	try:
		for x in patched_endpoints:
			x.start()
		yield
	finally:
		for x in patched_endpoints:
			x.stop()
		itds.db.rollback(save_point=savepoint)


class TestRenameDoc(IntegrationTestCase):
	@classmethod
	def setUpClass(self):
		"""Setting Up data for the tests defined under TestRenameDoc"""
		# set developer_mode to rename doc controllers
		super().setUpClass()
		self._original_developer_flag = itds.conf.developer_mode
		itds.conf.developer_mode = 1

		# data generation: for base and merge tests
		self.available_documents = []
		self.test_doctype = "ToDo"

		for num in range(1, 5):
			doc = itds.get_doc(
				{
					"doctype": self.test_doctype,
					"date": add_to_date(now(), days=num),
					"description": f"this is todo #{num}",
				}
			).insert()
			self.available_documents.append(doc.name)

		#  data generation: for controllers tests
		self.doctype = itds._dict(
			{
				"old": "Test Rename Document Old",
				"new": "Test Rename Document New",
			}
		)

		itds.get_doc(
			{
				"doctype": "DocType",
				"module": "Custom",
				"name": self.doctype.old,
				"custom": 0,
				"fields": [{"label": "Some Field", "fieldname": "some_fieldname", "fieldtype": "Data"}],
				"permissions": [{"role": "System Manager", "read": 1}],
			}
		).insert()

	@classmethod
	def tearDownClass(self):
		"""Deleting data generated for the tests defined under TestRenameDoc"""
		# delete_doc doesnt drop tables
		# this is done to bypass inconsistencies in the db
		itds.delete_doc_if_exists("DocType", "Renamed Doc")
		itds.db.sql_ddl("drop table if exists `tabRenamed Doc`")

		# delete the documents created
		for docname in self.available_documents:
			itds.delete_doc(self.test_doctype, docname)

		for dt in self.doctype.values():
			if itds.db.exists("DocType", dt):
				itds.delete_doc("DocType", dt)
				itds.db.sql_ddl(f"DROP TABLE IF EXISTS `tab{dt}`")

		# reset original value of developer_mode conf
		itds.conf.developer_mode = self._original_developer_flag

	def setUp(self):
		itds.flags.link_fields = {}
		if self._testMethodName == "test_doc_rename_method":
			self.property_setter = itds.get_doc(
				{
					"doctype": "Property Setter",
					"doctype_or_field": "DocType",
					"doc_type": self.test_doctype,
					"property": "allow_rename",
					"property_type": "Check",
					"value": "1",
				}
			).insert()

		super().setUp()

	def tearDown(self) -> None:
		if self._testMethodName == "test_doc_rename_method":
			self.property_setter.delete()
		return super().tearDown()

	def test_rename_doc(self):
		"""Rename an existing document via itds.rename_doc"""
		old_name = choice(self.available_documents)
		new_name = old_name + ".new"
		self.assertEqual(new_name, itds.rename_doc(self.test_doctype, old_name, new_name, force=True))
		self.available_documents.remove(old_name)
		self.available_documents.append(new_name)

	def test_merging_docs(self):
		"""Merge two documents via itds.rename_doc"""
		first_todo, second_todo = sample(self.available_documents, 2)

		second_todo_doc = itds.get_doc(self.test_doctype, second_todo)
		second_todo_doc.priority = "High"
		second_todo_doc.save()

		merged_todo = itds.rename_doc(self.test_doctype, first_todo, second_todo, merge=True, force=True)
		merged_todo_doc = itds.get_doc(self.test_doctype, merged_todo)
		self.available_documents.remove(first_todo)

		with self.assertRaises(DoesNotExistError):
			itds.get_doc(self.test_doctype, first_todo)

		self.assertEqual(merged_todo_doc.priority, second_todo_doc.priority)

	def test_rename_controllers(self):
		"""Rename doctypes with controller code paths"""
		# check if module exists exists;
		# if custom, get_controller will return Document class
		# if not custom, a different class will be returned
		self.assertNotEqual(get_controller(self.doctype.old), itds.model.document.Document)

		old_doctype_path = get_doc_path("Custom", "DocType", self.doctype.old)

		# rename doc via wrapper API accessible via /desk
		itds.rename_doc("DocType", self.doctype.old, self.doctype.new)

		# check if database and controllers are updated
		self.assertTrue(itds.db.exists("DocType", self.doctype.new))
		self.assertFalse(itds.db.exists("DocType", self.doctype.old))
		self.assertFalse(os.path.exists(old_doctype_path))

	def test_rename_doctype(self):
		"""Rename DocType via itds.rename_doc"""
		from itds.core.doctype.doctype.test_doctype import new_doctype

		if not itds.db.exists("DocType", "Rename This"):
			new_doctype(
				"Rename This",
				fields=[
					{
						"label": "Linked To",
						"fieldname": "linked_to_doctype",
						"fieldtype": "Link",
						"options": "DocType",
						"unique": 0,
					}
				],
			).insert()

		to_rename_record = itds.get_doc(
			{"doctype": "Rename This", "linked_to_doctype": "Rename This"}
		).insert()

		# Rename doctype
		self.assertEqual(
			"Renamed Doc", itds.rename_doc("DocType", "Rename This", "Renamed Doc", force=True)
		)

		# Test if Doctype value has changed in Link field
		linked_to_doctype = itds.db.get_value("Renamed Doc", to_rename_record.name, "linked_to_doctype")
		self.assertEqual(linked_to_doctype, "Renamed Doc")

		# Test if there are conflicts between a record and a DocType
		# having the same name
		old_name = to_rename_record.name
		new_name = "ToDo"
		self.assertEqual(new_name, itds.rename_doc("Renamed Doc", old_name, new_name, force=True))

	def test_update_document_title_api(self):
		test_doctype = "Module Def"
		test_doc = itds.get_doc(
			{
				"doctype": test_doctype,
				"module_name": f"Test-test_update_document_title_api-{itds.generate_hash()}",
				"custom": True,
			}
		)
		test_doc.insert(ignore_mandatory=True)

		dt = test_doc.doctype
		dn = test_doc.name
		new_name = f"{dn}-new"

		# pass invalid types to API
		with self.assertRaises(TypeError):
			update_document_title(doctype=dt, docname=dn, title={}, name={"hack": "this"})

		doc_before = itds.get_doc(test_doctype, dn)
		return_value = update_document_title(doctype=dt, docname=dn, new_name=new_name)
		doc_after = itds.get_doc(test_doctype, return_value)

		doc_before_dict = doc_before.as_dict(no_nulls=True, no_default_fields=True)
		doc_after_dict = doc_after.as_dict(no_nulls=True, no_default_fields=True)
		doc_before_dict.pop("module_name")
		doc_after_dict.pop("module_name")

		self.assertEqual(new_name, return_value)
		self.assertDictEqual(doc_before_dict, doc_after_dict)
		self.assertEqual(doc_after.module_name, return_value)

		test_doc.delete()

	def test_bulk_rename(self):
		input_data = [[x, f"{x}-new"] for x in self.available_documents]

		with patch_db(["commit", "rollback"]), patch("itds.enqueue") as enqueue:
			message_log = bulk_rename(self.test_doctype, input_data, via_console=False)
			self.assertEqual(len(message_log), len(self.available_documents))
			self.assertIsInstance(message_log, list)
			enqueue.assert_called_with(
				"itds.utils.global_search.rebuild_for_doctype",
				doctype=self.test_doctype,
			)

	def test_doc_rename_method(self):
		name = choice(self.available_documents)
		new_name = f"{name}-{itds.generate_hash(length=4)}"
		doc = itds.get_doc(self.test_doctype, name)
		doc.rename(new_name, merge=itds.db.exists(self.test_doctype, new_name))
		self.assertEqual(doc.name, new_name)
		self.available_documents.append(new_name)
		self.available_documents.remove(name)

	def test_parenttype(self):
		child = new_doctype(istable=1).insert()
		table_field = {
			"label": "Test Table",
			"fieldname": "test_table",
			"fieldtype": "Table",
			"options": child.name,
		}

		parent_a = new_doctype(fields=[table_field], allow_rename=1, autoname="Prompt").insert()
		parent_b = new_doctype(fields=[table_field], allow_rename=1, autoname="Prompt").insert()

		parent_a_instance = itds.get_doc(
			doctype=parent_a.name, test_table=[{"some_fieldname": "x"}], name="XYZ"
		).insert()

		parent_b_instance = itds.get_doc(
			doctype=parent_b.name, test_table=[{"some_fieldname": "x"}], name="XYZ"
		).insert()

		parent_b_instance.rename("ABC")
		parent_a_instance.reload()

		self.assertEqual(len(parent_a_instance.test_table), 1)
		self.assertEqual(len(parent_b_instance.test_table), 1)

	def test_rename_autoincrement_doc(self):
		if not itds.db.exists("DocType", "Autoincrement DocType"):
			new_doctype(
				"Autoincrement DocType",
				naming_rule="Autoincrement",
				autoname="autoincrement",
				fields=[
					{
						"label": "First Name",
						"fieldname": "first_name",
						"fieldtype": "Data",
					}
				],
			).insert()

		if not itds.db.exists("DocType", "Autoincrement Linked DocType"):
			new_doctype(
				"Autoincrement Linked DocType",
				fields=[
					{
						"label": "Autoincrement DocType",
						"fieldname": "autoincrement_doctype",
						"fieldtype": "Link",
						"options": "Autoincrement DocType",
					}
				],
			).insert()

		# create records
		mary = itds.new_doc("Autoincrement DocType", first_name="Mary").insert()
		marilyn = itds.new_doc("Autoincrement DocType", first_name="Marilyn").insert()
		linked_with_marilyn = itds.new_doc(
			"Autoincrement Linked DocType", autoincrement_doctype=marilyn.name
		).insert()
		self.assertEqual(marilyn.name, linked_with_marilyn.autoincrement_doctype)

		# rename marilyn to mary
		itds.rename_doc("Autoincrement DocType", marilyn.name, mary.name, merge=True)
		linked_with_marilyn.reload()

		self.assertTrue(itds.db.exists("Autoincrement DocType", marilyn.name) is None)
		self.assertEqual(linked_with_marilyn.autoincrement_doctype, itds.utils.cstr(mary.name))
