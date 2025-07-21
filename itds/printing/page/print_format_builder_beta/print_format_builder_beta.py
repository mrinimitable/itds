# Copyright (c) 2021, Itds Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import functools

import itds


@itds.whitelist()
def get_google_fonts():
	return _get_google_fonts()


@functools.lru_cache
def _get_google_fonts():
	file_path = itds.get_app_path("itds", "data", "google_fonts.json")
	return itds.parse_json(itds.read_file(file_path))
