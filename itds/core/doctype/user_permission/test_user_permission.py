# Copyright (c) 2021, Itds Technologies and Contributors
# See LICENSE
import itds
from itds.core.doctype.doctype.test_doctype import new_doctype
from itds.core.doctype.user_permission.user_permission import (
	add_user_permissions,
	remove_applicable,
)
from itds.permissions import add_permission, has_user_permission
from itds.tests import IntegrationTestCase
from itds.website.doctype.blog_post.test_blog_post import make_test_blog


class TestUserPermission(IntegrationTestCase):
	def setUp(self):
		test_users = (
			"test_bulk_creation_update@example.com",
			"test_user_perm1@example.com",
			"nested_doc_user@example.com",
		)
		itds.db.delete("User Permission", {"user": ("in", test_users)})
		itds.delete_doc_if_exists("DocType", "Person")
		itds.db.sql_ddl("DROP TABLE IF EXISTS `tabPerson`")
		itds.delete_doc_if_exists("DocType", "Doc A")
		itds.db.sql_ddl("DROP TABLE IF EXISTS `tabDoc A`")

	def test_default_user_permission_validation(self):
		user = create_user("test_default_permission@example.com")
		param = get_params(user, "User", user.name, is_default=1)
		add_user_permissions(param)
		# create a duplicate entry with default
		perm_user = create_user("test_user_perm@example.com")
		param = get_params(user, "User", perm_user.name, is_default=1)
		self.assertRaises(itds.ValidationError, add_user_permissions, param)

	def test_default_user_permission_corectness(self):
		user = create_user("test_default_corectness_permission_1@example.com")
		param = get_params(user, "User", user.name, is_default=1, hide_descendants=1)
		add_user_permissions(param)
		# create a duplicate entry with default
		perm_user = create_user("test_default_corectness2@example.com")
		test_blog = make_test_blog()
		param = get_params(perm_user, "Blog Post", test_blog.name, is_default=1, hide_descendants=1)
		add_user_permissions(param)
		itds.db.delete("User Permission", filters={"for_value": test_blog.name})
		itds.delete_doc("Blog Post", test_blog.name)

	def test_default_user_permission(self):
		itds.set_user("Administrator")
		user = create_user("test_user_perm1@example.com", "Website Manager")
		for category in ["general", "public"]:
			if not itds.db.exists("Blog Category", category):
				itds.get_doc({"doctype": "Blog Category", "title": category}).insert()

		param = get_params(user, "Blog Category", "general", is_default=1)
		add_user_permissions(param)

		param = get_params(user, "Blog Category", "public")
		add_user_permissions(param)

		itds.set_user("test_user_perm1@example.com")
		doc = itds.new_doc("Blog Post")

		self.assertEqual(doc.blog_category, "general")
		itds.set_user("Administrator")

	def test_apply_to_all(self):
		"""Create User permission for User having access to all applicable Doctypes"""
		user = create_user("test_bulk_creation_update@example.com")
		param = get_params(user, "User", user.name)
		is_created = add_user_permissions(param)
		self.assertEqual(is_created, 1)

	def test_for_apply_to_all_on_update_from_apply_all(self):
		user = create_user("test_bulk_creation_update@example.com")
		param = get_params(user, "User", user.name)

		# Initially create User Permission document with apply_to_all checked
		is_created = add_user_permissions(param)

		self.assertEqual(is_created, 1)
		is_created = add_user_permissions(param)

		# User Permission should not be changed
		self.assertEqual(is_created, 0)

	def test_for_applicable_on_update_from_apply_to_all(self):
		"""Update User Permission from all to some applicable Doctypes"""
		user = create_user("test_bulk_creation_update@example.com")
		param = get_params(user, "User", user.name, applicable=["Comment", "Contact"])

		# Initially create User Permission document with apply_to_all checked
		is_created = add_user_permissions(get_params(user, "User", user.name))

		self.assertEqual(is_created, 1)

		is_created = add_user_permissions(param)
		itds.db.commit()

		removed_apply_to_all = itds.db.exists("User Permission", get_exists_param(user))
		is_created_applicable_first = itds.db.exists(
			"User Permission", get_exists_param(user, applicable="Comment")
		)
		is_created_applicable_second = itds.db.exists(
			"User Permission", get_exists_param(user, applicable="Contact")
		)

		# Check that apply_to_all is removed
		self.assertIsNone(removed_apply_to_all)

		# Check that User Permissions for applicable is created
		self.assertIsNotNone(is_created_applicable_first)
		self.assertIsNotNone(is_created_applicable_second)
		self.assertEqual(is_created, 1)

	def test_for_apply_to_all_on_update_from_applicable(self):
		"""Update User Permission from some to all applicable Doctypes"""
		user = create_user("test_bulk_creation_update@example.com")
		param = get_params(user, "User", user.name)

		# create User permissions that with applicable
		is_created = add_user_permissions(
			get_params(user, "User", user.name, applicable=["Comment", "Contact"])
		)

		self.assertEqual(is_created, 1)

		is_created = add_user_permissions(param)
		is_created_apply_to_all = itds.db.exists("User Permission", get_exists_param(user))
		removed_applicable_first = itds.db.exists(
			"User Permission", get_exists_param(user, applicable="Comment")
		)
		removed_applicable_second = itds.db.exists(
			"User Permission", get_exists_param(user, applicable="Contact")
		)

		# To check that a User permission with apply_to_all exists
		self.assertIsNotNone(is_created_apply_to_all)

		# Check that all User Permission with applicable is removed
		self.assertIsNone(removed_applicable_first)
		self.assertIsNone(removed_applicable_second)
		self.assertEqual(is_created, 1)

	def test_user_perm_for_nested_doctype(self):
		"""Test if descendants' visibility is controlled for a nested DocType."""
		from itds.core.doctype.doctype.test_doctype import new_doctype

		user = create_user("nested_doc_user@example.com", "Blogger")
		if not itds.db.exists("DocType", "Person"):
			doc = new_doctype(
				"Person",
				fields=[{"label": "Person Name", "fieldname": "person_name", "fieldtype": "Data"}],
				unique=0,
			)
			doc.is_tree = 1
			doc.insert()

		parent_record = itds.get_doc({"doctype": "Person", "person_name": "Parent", "is_group": 1}).insert()

		child_record = itds.get_doc(
			{
				"doctype": "Person",
				"person_name": "Child",
				"is_group": 0,
				"parent_person": parent_record.name,
			}
		).insert()

		add_user_permissions(get_params(user, "Person", parent_record.name))

		# check if adding perm on a group record, makes child record visible
		self.assertTrue(has_user_permission(itds.get_doc("Person", parent_record.name), user.name))
		self.assertTrue(has_user_permission(itds.get_doc("Person", child_record.name), user.name))

		#  give access of Parent DocType to Blogger role
		add_permission("Person", "Blogger")
		itds.set_user(user.name)
		visible_names = itds.get_list(
			doctype="Person",
			pluck="person_name",
		)

		user_permission = itds.get_doc(
			"User Permission", {"allow": "Person", "for_value": parent_record.name}
		)
		user_permission.hide_descendants = 1
		user_permission.save(ignore_permissions=True)

		# check if adding perm on a group record with hide_descendants enabled,
		# hides child records
		self.assertTrue(has_user_permission(itds.get_doc("Person", parent_record.name), user.name))
		self.assertFalse(has_user_permission(itds.get_doc("Person", child_record.name), user.name))

		visible_names_after_hide_descendants = itds.get_list(
			"Person",
			pluck="person_name",
		)
		self.assertEqual(visible_names, ["Child", "Parent"])
		self.assertEqual(visible_names_after_hide_descendants, ["Parent"])
		itds.set_user("Administrator")

	def test_user_perm_on_new_doc_with_field_default(self):
		"""Test User Perm impact on itds.new_doc. with *field* default value"""
		itds.set_user("Administrator")
		user = create_user("new_doc_test@example.com", "Blogger")

		# make a doctype "Doc A" with 'doctype' link field and default value ToDo
		if not itds.db.exists("DocType", "Doc A"):
			doc = new_doctype(
				"Doc A",
				fields=[
					{
						"label": "DocType",
						"fieldname": "doc",
						"fieldtype": "Link",
						"options": "DocType",
						"default": "ToDo",
					}
				],
				unique=0,
			)
			doc.insert()

		# make User Perm on DocType 'ToDo' in Assignment Rule (unrelated doctype)
		add_user_permissions(get_params(user, "DocType", "ToDo", applicable=["Assignment Rule"]))
		itds.set_user("new_doc_test@example.com")

		new_doc = itds.new_doc("Doc A")

		# User perm is created on ToDo but for doctype Assignment Rule only
		# it should not have impact on Doc A
		self.assertEqual(new_doc.doc, "ToDo")

		itds.set_user("Administrator")
		remove_applicable(["Assignment Rule"], "new_doc_test@example.com", "DocType", "ToDo")

	def test_user_perm_on_new_doc_with_user_default(self):
		"""Test User Perm impact on itds.new_doc. with *user* default value"""
		from itds.core.doctype.session_default_settings.session_default_settings import (
			clear_session_defaults,
			set_session_default_values,
		)

		itds.set_user("Administrator")
		user = create_user("user_default_test@example.com", "Blogger")

		# make a doctype "Doc A" with 'doctype' link field
		if not itds.db.exists("DocType", "Doc A"):
			doc = new_doctype(
				"Doc A",
				fields=[
					{
						"label": "DocType",
						"fieldname": "doc",
						"fieldtype": "Link",
						"options": "DocType",
					}
				],
				unique=0,
			)
			doc.insert()

		# create a 'DocType' session default field
		if not itds.db.exists("Session Default", {"ref_doctype": "DocType"}):
			settings = itds.get_single("Session Default Settings")
			settings.append("session_defaults", {"ref_doctype": "DocType"})
			settings.save()

		# make User Perm on DocType 'ToDo' in Assignment Rule (unrelated doctype)
		add_user_permissions(get_params(user, "DocType", "ToDo", applicable=["Assignment Rule"]))

		# User default Doctype value is ToDo via Session Defaults
		itds.set_user("user_default_test@example.com")
		set_session_default_values({"doc": "ToDo"})

		new_doc = itds.new_doc("Doc A")

		# User perm is created on ToDo but for doctype Assignment Rule only
		# it should not have impact on Doc A
		self.assertEqual(new_doc.doc, "ToDo")

		itds.set_user("Administrator")
		clear_session_defaults()
		remove_applicable(["Assignment Rule"], "user_default_test@example.com", "DocType", "ToDo")


def create_user(email, *roles):
	"""create user with role system manager"""
	if itds.db.exists("User", email):
		return itds.get_doc("User", email)

	user = itds.new_doc("User")
	user.email = email
	user.first_name = email.split("@", 1)[0]

	if not roles:
		roles = ("System Manager",)

	# this triggers doc.save, so explicit save is not needed
	user.add_roles(*roles)
	return user


def get_params(user, doctype, docname, is_default=0, hide_descendants=0, applicable=None):
	"""Return param to insert"""
	param = {
		"user": user.name,
		"doctype": doctype,
		"docname": docname,
		"is_default": is_default,
		"apply_to_all_doctypes": 1,
		"applicable_doctypes": [],
		"hide_descendants": hide_descendants,
	}
	if applicable:
		param.update({"apply_to_all_doctypes": 0})
		param.update({"applicable_doctypes": applicable})
	return param


def get_exists_param(user, applicable=None):
	"""param to check existing Document"""
	param = {
		"user": user.name,
		"allow": "User",
		"for_value": user.name,
	}
	if applicable:
		param.update({"applicable_for": applicable})
	else:
		param.update({"apply_to_all_doctypes": 1})
	return param
