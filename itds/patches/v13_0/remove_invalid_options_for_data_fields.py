# Copyright (c) 2022, Itds and Contributors
# License: MIT. See LICENSE


import itds
from itds.model import data_field_options


def execute():
	custom_field = itds.qb.DocType("Custom Field")
	(
		itds.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
