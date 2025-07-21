# Copyright (c) 2020, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	itds.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	itds.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
