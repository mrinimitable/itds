from contextlib import suppress

import itds


def execute():
	"""Remove invalid fetch from expressions"""
	with suppress(Exception):
		property_setters = itds.get_all(
			"Property Setter", {"doctype_or_field": "DocField", "property": "fetch_from"}, ["name", "value"]
		)
		for ps in property_setters:
			if not is_valid_expression(ps.value):
				itds.db.delete("Property Setter", {"name": ps.name})

		custom_fields = itds.get_all("Custom Field", {"fetch_from": ("is", "set")}, ["name", "fetch_from"])
		for cf in custom_fields:
			if not is_valid_expression(cf.fetch_from):
				itds.db.set_value("Custom Field", cf.name, "fetch_from", "")


def is_valid_expression(expr) -> bool:
	if not expr or "." not in expr:
		return False
	source_field, target_field = expr.split(".", maxsplit=1)
	if not source_field or not target_field:
		return False
	return True
