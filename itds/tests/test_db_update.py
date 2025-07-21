import random

import itds
from itds.core.doctype.doctype.test_doctype import new_doctype
from itds.core.utils import find
from itds.custom.doctype.property_setter.property_setter import make_property_setter
from itds.query_builder.utils import db_type_is
from itds.tests import IntegrationTestCase
from itds.tests.test_query_builder import run_only_if
from itds.utils import cstr


class TestDBUpdate(IntegrationTestCase):
	def test_db_update(self):
		doctype = "User"
		itds.reload_doctype("User", force=True)
		itds.model.meta.trim_tables("User")
		make_property_setter(doctype, "bio", "fieldtype", "Text", "Data")
		make_property_setter(doctype, "middle_name", "fieldtype", "Data", "Text")
		make_property_setter(doctype, "enabled", "default", "1", "Int")

		itds.db.updatedb(doctype)

		field_defs = get_field_defs(doctype)
		table_columns = itds.db.get_table_columns_description(f"tab{doctype}")

		self.assertEqual(len(field_defs), len(table_columns))

		for field_def in field_defs:
			fieldname = field_def.get("fieldname")
			table_column = find(table_columns, lambda d: d.get("name") == fieldname)

			fieldtype = get_fieldtype_from_def(field_def)

			fallback_default = (
				"0" if field_def.get("fieldtype") in itds.model.numeric_fieldtypes else "NULL"
			)
			default = field_def.default if field_def.default is not None else fallback_default

			self.assertIn(fieldtype, table_column.type, msg=f"Types not matching for {fieldname}")
			self.assertIn(cstr(table_column.default) or "NULL", [cstr(default), f"'{default}'"])

	def test_index_and_unique_constraints(self):
		doctype = "User"
		itds.reload_doctype("User", force=True)
		itds.model.meta.trim_tables("User")

		make_property_setter(doctype, "middle_name", "unique", "1", "Check")
		itds.db.updatedb(doctype)
		middle_name_in_table = get_table_column("User", "middle_name")
		self.assertTrue(middle_name_in_table.unique)

		make_property_setter(doctype, "middle_name", "unique", "0", "Check")
		itds.db.updatedb(doctype)
		middle_name_in_table = get_table_column("User", "middle_name")
		self.assertFalse(middle_name_in_table.unique)

		make_property_setter(doctype, "middle_name", "search_index", "1", "Check")
		itds.db.updatedb(doctype)
		middle_name_in_table = get_table_column("User", "middle_name")
		self.assertTrue(middle_name_in_table.index)

		make_property_setter(doctype, "middle_name", "search_index", "0", "Check")
		itds.db.updatedb(doctype)
		middle_name_in_table = get_table_column("User", "middle_name")
		self.assertFalse(middle_name_in_table.index)

		make_property_setter(doctype, "middle_name", "search_index", "1", "Check")
		make_property_setter(doctype, "middle_name", "unique", "1", "Check")
		itds.db.updatedb(doctype)
		middle_name_in_table = get_table_column("User", "middle_name")
		self.assertTrue(middle_name_in_table.index)
		self.assertTrue(middle_name_in_table.unique)

		make_property_setter(doctype, "middle_name", "search_index", "1", "Check")
		make_property_setter(doctype, "middle_name", "unique", "0", "Check")
		itds.db.updatedb(doctype)
		middle_name_in_table = get_table_column("User", "middle_name")
		self.assertTrue(middle_name_in_table.index)
		self.assertFalse(middle_name_in_table.unique)

		make_property_setter(doctype, "middle_name", "search_index", "0", "Check")
		make_property_setter(doctype, "middle_name", "unique", "1", "Check")
		itds.db.updatedb(doctype)
		middle_name_in_table = get_table_column("User", "middle_name")
		self.assertFalse(middle_name_in_table.index)
		self.assertTrue(middle_name_in_table.unique)

		# explicitly make a text index
		itds.db.add_index(doctype, ["email_signature(200)"])
		itds.db.updatedb(doctype)
		email_sig_column = get_table_column("User", "email_signature")
		self.assertEqual(email_sig_column.index, 1)

	def check_unique_indexes(self, doctype: str, field: str):
		indexes = itds.db.sql(
			f"""show index from `tab{doctype}` where column_name = '{field}' and Non_unique = 0""",
			as_dict=1,
		)
		self.assertEqual(
			len(indexes), 1, msg=f"There should be 1 index on {doctype}.{field}, found {indexes}"
		)

	def test_bigint_conversion(self):
		doctype = new_doctype(fields=[{"fieldname": "int_field", "fieldtype": "Int"}]).insert()

		with self.assertRaises(itds.CharacterLengthExceededError):
			itds.get_doc(doctype=doctype.name, int_field=2**62 - 1).insert()

		doctype.fields[0].length = 14
		doctype.save()
		itds.get_doc(doctype=doctype.name, int_field=2**62 - 1).insert()

	@run_only_if(db_type_is.MARIADB)
	def test_unique_index_on_install(self):
		"""Only one unique index should be added"""
		for dt in itds.get_all("DocType", {"is_virtual": 0, "issingle": 0}, pluck="name"):
			doctype = itds.get_meta(dt)
			fields = doctype.get("fields", filters={"unique": 1})
			for field in fields:
				with self.subTest(f"Checking index {doctype.name} - {field.fieldname}"):
					self.check_unique_indexes(doctype.name, field.fieldname)

	@run_only_if(db_type_is.MARIADB)
	def test_unique_index_on_alter(self):
		"""Only one unique index should be added"""

		doctype = new_doctype(unique=1).insert()
		field = "some_fieldname"

		self.check_unique_indexes(doctype.name, field)
		doctype.fields[0].length = 142
		doctype.save()
		self.check_unique_indexes(doctype.name, field)

		doctype.fields[0].unique = 0
		doctype.save()

		doctype.fields[0].unique = 1
		doctype.save()
		self.check_unique_indexes(doctype.name, field)

		# New column with a unique index
		# This works because index name is same as fieldname.
		new_field = itds.copy_doc(doctype.fields[0])
		new_field.fieldname = "duplicate_field"
		doctype.append("fields", new_field)
		doctype.save()
		self.check_unique_indexes(doctype.name, new_field.fieldname)

		doctype.delete()
		itds.db.commit()

	def test_uuid_varchar_migration(self):
		doctype = new_doctype().insert()
		doctype.autoname = "UUID"
		doctype.save()
		self.assertEqual(itds.db.get_column_type(doctype.name, "name"), "uuid")

		doc = itds.new_doc(doctype.name).insert()

		doctype.autoname = "hash"
		doctype.save()
		varchar = "varchar" if itds.db.db_type == "mariadb" else "character varying"
		self.assertIn(varchar, itds.db.get_column_type(doctype.name, "name"))
		doc.reload()  # ensure that docs are still accesible

	def test_uuid_link_field(self):
		uuid_doctype = new_doctype().update({"autoname": "UUID"}).insert()
		self.assertEqual(itds.db.get_column_type(uuid_doctype.name, "name"), "uuid")

		link = "link_field"
		referring_doctype = new_doctype(
			fields=[{"fieldname": link, "fieldtype": "Link", "options": uuid_doctype.name}]
		).insert()

		self.assertEqual(itds.db.get_column_type(referring_doctype.name, link), "uuid")


class TestDBUpdateSanityChecks(IntegrationTestCase):
	@run_only_if(db_type_is.MARIADB)
	def test_no_unnecessary_migrates(self):
		doctypes = itds.get_all("DocType", {"is_virtual": 0, "custom": 0}, pluck="name")

		# Migrating all doctypes takes way too long of a time.
		# NOTE: This test mostly won't be flaky, if it fails randomly, it is because it tests
		# randomly.
		# DO NOT IGNORE FAILURES.
		random.shuffle(doctypes)
		doctypes = doctypes[:20]

		for doctype in doctypes:
			with self.subTest(f"Check {doctype}"):
				itds.reload_doctype(doctype, force=True)
				with self.assertQueryCount(0, query_type=("alter",)):
					itds.reload_doctype(doctype, force=True)


def get_fieldtype_from_def(field_def):
	fieldtuple = itds.db.type_map.get(field_def.fieldtype, ("", 0))
	fieldtype = fieldtuple[0]
	if fieldtype in ("varchar", "datetime"):
		fieldtype += f"({field_def.length or fieldtuple[1]})"
	return fieldtype


def get_field_defs(doctype):
	meta = itds.get_meta(doctype, cached=False)
	field_defs = meta.get_fieldnames_with_value(True)
	field_defs += get_other_fields_meta(meta)
	return field_defs


def get_other_fields_meta(meta):
	default_fields_map = {
		"name": ("Data", 0),
		"owner": ("Data", 0),
		"modified_by": ("Data", 0),
		"creation": ("Datetime", 0),
		"modified": ("Datetime", 0),
		"idx": ("Int", 8),
		"docstatus": ("Check", 0),
	}

	optional_fields = itds.db.OPTIONAL_COLUMNS
	if meta.track_seen:
		optional_fields.append("_seen")

	child_table_fields_map = {}
	if meta.istable:
		child_table_fields_map.update({field: ("Data", 0) for field in itds.db.CHILD_TABLE_COLUMNS})

	optional_fields_map = {field: ("Text", 0) for field in optional_fields}
	fields = dict(default_fields_map, **optional_fields_map, **child_table_fields_map)
	return [
		itds._dict({"fieldname": field, "fieldtype": _type, "length": _length})
		for field, (_type, _length) in fields.items()
	]


def get_table_column(doctype, fieldname):
	table_columns = itds.db.get_table_columns_description(f"tab{doctype}")
	return find(table_columns, lambda d: d.get("name") == fieldname)
