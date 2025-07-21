from itds.gettext.translate import (
	generate_pot,
	get_is_gitignored_function_for_app,
	get_method_map,
	get_mo_path,
	get_po_path,
	get_pot_path,
	new_catalog,
	new_po,
	write_binary,
	write_catalog,
)
from itds.tests import IntegrationTestCase


class TestTranslate(IntegrationTestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_generate_pot(self):
		pot_path = get_pot_path("itds")
		pot_path.unlink(missing_ok=True)

		generate_pot("itds")

		self.assertTrue(pot_path.exists())
		self.assertIn("msgid", pot_path.read_text())

	def test_write_catalog(self):
		po_path = get_po_path("itds", "test")
		po_path.unlink(missing_ok=True)

		catalog = new_catalog("itds", "test")
		write_catalog("itds", catalog, "test")

		self.assertTrue(po_path.exists())
		self.assertIn("msgid", po_path.read_text())

	def test_write_binary(self):
		mo_path = get_mo_path("itds", "test")
		mo_path.unlink(missing_ok=True)

		catalog = new_catalog("itds", "test")
		write_binary("itds", catalog, "test")

		self.assertTrue(mo_path.exists())

	def test_get_method_map(self):
		method_map = get_method_map("itds")
		self.assertTrue(len(method_map) > 0)
		self.assertTrue(len(method_map[0]) == 2)
		self.assertTrue(isinstance(method_map[0][0], str))
		self.assertTrue(isinstance(method_map[0][1], str))

	def test_new_po(self):
		po_path = get_po_path("itds", "test")
		po_path.unlink(missing_ok=True)

		new_po("test", target_app="itds")

		self.assertTrue(po_path.exists())
		self.assertIn("msgid", po_path.read_text())

	def test_gitignore(self):
		import os

		import itds

		is_gitignored = get_is_gitignored_function_for_app("itds")

		file_name = "itds/public/dist/test_translate_test_gitignore.js"
		file_path = itds.get_app_source_path("itds", file_name)
		self.assertTrue(is_gitignored("itds/public/node_modules"))
		self.assertTrue(is_gitignored("itds/public/dist"))
		self.assertTrue(is_gitignored("itds/public/dist/sub"))
		self.assertTrue(is_gitignored(file_name))
		self.assertTrue(is_gitignored(file_path))
		self.assertFalse(is_gitignored("itds/public/dist2"))
		self.assertFalse(is_gitignored("itds/public/dist2/sub"))

		# Make directory if not exist
		os.makedirs(os.path.dirname(file_path), exist_ok=True)
		with open(file_path, "w") as f:
			f.write('__("test_translate_test_gitignore")')

		pot_path = get_pot_path("itds")
		pot_path.unlink(missing_ok=True)

		generate_pot("itds")

		self.assertTrue(pot_path.exists())
		self.assertNotIn("test_translate_test_gitignore", pot_path.read_text())

		os.remove(file_path)

		self.assertTrue(get_is_gitignored_function_for_app(None)("itds/public/dist"))
