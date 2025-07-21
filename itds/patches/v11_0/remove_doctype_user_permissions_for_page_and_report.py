# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import itds


def execute():
	itds.delete_doc_if_exists("DocType", "User Permission for Page and Report")
