# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import itds
from itds.core.page.permission_manager.permission_manager import add, reset, update
from itds.custom.doctype.property_setter.property_setter import make_property_setter
from itds.desk.form.load import get_docinfo, getdoc, getdoctype
from itds.tests import IntegrationTestCase
from itds.utils.file_manager import save_file

EXTRA_TEST_RECORD_DEPENDENCIES = ["Blog Category", "Blogger"]


class TestFormLoad(IntegrationTestCase):
	def test_load(self):
		getdoctype("DocType")
		meta = next(filter(lambda d: d.name == "DocType", itds.response.docs))
		self.assertEqual(meta.name, "DocType")
		self.assertTrue(meta.get("__js"))

		itds.response.docs = []
		getdoctype("Event")
		meta = next(filter(lambda d: d.name == "Event", itds.response.docs))
		self.assertTrue(meta.get("__calendar_js"))

	def test_fieldlevel_permissions_in_load(self):
		blog = itds.get_doc(
			{
				"doctype": "Blog Post",
				"blog_category": "-test-blog-category-1",
				"blog_intro": "Test Blog Intro",
				"blogger": "_Test Blogger 1",
				"content": "Test Blog Content",
				"title": f"_Test Blog Post {itds.utils.now()}",
				"published": 0,
			}
		)

		blog.insert()

		user = itds.get_doc("User", "test@example.com")

		user_roles = itds.get_roles()
		user.remove_roles(*user_roles)
		user.add_roles("Blogger")

		blog_post_property_setter = make_property_setter("Blog Post", "published", "permlevel", 1, "Int")
		reset("Blog Post")

		# test field level permission before role level permissions are defined
		itds.set_user(user.name)
		blog_doc = get_blog(blog.name)

		with self.assertRaises(AttributeError):
			blog_doc.published

		# this will be ignored because user does not
		# have write access on `published` field (or on permlevel 1 fields)
		blog_doc.published = 1
		blog_doc.save()

		# since published field has higher permlevel
		self.assertEqual(blog_doc.published, 0)

		# test field level permission after role level permissions are defined
		itds.set_user("Administrator")
		add("Blog Post", "Website Manager", 1)
		update("Blog Post", "Website Manager", 1, "write", 1)

		itds.set_user(user.name)
		blog_doc = get_blog(blog.name)

		self.assertEqual(blog_doc.name, blog.name)
		# since published field has higher permlevel
		with self.assertRaises(AttributeError):
			blog_doc.published

		# this will be ignored because user does not
		# have write access on `published` field (or on permlevel 1 fields)
		blog_doc.published = 1
		blog_doc.save()

		# since published field has higher permlevel
		self.assertEqual(blog_doc.published, 0)

		itds.set_user("Administrator")
		user.add_roles("Website Manager")
		itds.set_user(user.name)

		doc = itds.get_doc("Blog Post", blog.name)
		doc.published = 1
		doc.save()

		blog_doc = get_blog(blog.name)
		# now user should be allowed to read field with higher permlevel
		# (after adding Website Manager role)
		self.assertEqual(blog_doc.published, 1)

		itds.set_user("Administrator")

		# reset user roles
		user.remove_roles("Blogger", "Website Manager")
		user.add_roles(*user_roles)

		blog_doc.delete()
		itds.delete_doc(blog_post_property_setter.doctype, blog_post_property_setter.name)

	def test_fieldlevel_permissions_in_load_for_child_table(self):
		contact = itds.new_doc("Contact")
		contact.first_name = "_Test Contact 1"
		contact.append("phone_nos", {"phone": "123456"})
		contact.insert()

		user = itds.get_doc("User", "test@example.com")

		user_roles = itds.get_roles()
		user.remove_roles(*user_roles)
		user.add_roles("Accounts User")

		make_property_setter("Contact Phone", "phone", "permlevel", 1, "Int")
		reset("Contact Phone")
		add("Contact", "Sales User", 1)
		update("Contact", "Sales User", 1, "write", 1)

		itds.set_user(user.name)

		contact = itds.get_doc("Contact", "_Test Contact 1")

		contact.phone_nos[0].phone = "654321"
		contact.save()

		self.assertEqual(contact.phone_nos[0].phone, "123456")

		itds.set_user("Administrator")
		user.add_roles("Sales User")
		itds.set_user(user.name)

		contact.phone_nos[0].phone = "654321"
		contact.save()

		contact = itds.get_doc("Contact", "_Test Contact 1")
		self.assertEqual(contact.phone_nos[0].phone, "654321")

		itds.set_user("Administrator")

		# reset user roles
		user.remove_roles("Accounts User", "Sales User")
		user.add_roles(*user_roles)

		contact.delete()

	def test_get_doc_info(self):
		note = itds.new_doc("Note")
		note.content = "some content"
		note.title = itds.generate_hash(length=20)
		note.insert()

		note.content = "new content"
		# trigger a version
		note.save(ignore_version=False)

		note.add_comment(text="test")

		note.add_tag("test_tag")
		note.add_tag("more_tag")

		# empty attachment
		save_file("test_file", b"", note.doctype, note.name, decode=True)

		itds.get_doc(
			{
				"doctype": "Communication",
				"communication_type": "Communication",
				"content": "test email",
				"reference_doctype": note.doctype,
				"reference_name": note.name,
			}
		).insert()

		get_docinfo(note)
		docinfo = itds.response["docinfo"]

		self.assertEqual(len(docinfo.comments), 1)
		self.assertIn("test", docinfo.comments[0].content)

		self.assertGreaterEqual(len(docinfo.versions), 1)

		self.assertEqual(set(docinfo.tags.split(",")), {"more_tag", "test_tag"})

		self.assertEqual(len(docinfo.attachments), 1)
		self.assertIn("test_file", docinfo.attachments[0].file_name)

		self.assertEqual(len(docinfo.communications), 1)
		self.assertIn("email", docinfo.communications[0].content)
		note.delete()


def get_blog(blog_name):
	itds.response.docs = []
	getdoc("Blog Post", blog_name)
	return itds.response.docs[0]
