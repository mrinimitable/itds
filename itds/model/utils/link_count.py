# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from collections import defaultdict
from random import random

import itds

ignore_doctypes = {
	"DocType",
	"Print Format",
	"Role",
	"Module Def",
	"Communication",
	"ToDo",
	"Version",
	"Error Log",
	"Scheduled Job Log",
	"Event Sync Log",
	"Event Update Log",
	"Access Log",
	"View Log",
	"Activity Log",
	"Notification Log",
	"Email Queue",
	"DocShare",
	"Document Follow",
	"Console Log",
	"User",
}


LINK_COUNT_BUFFER_SIZE = 256


def notify_link_count(doctype, name):
	"""updates link count for given document"""

	if doctype in ignore_doctypes or not itds.request or random() < 0.9:  # Sample 10%
		return

	if not hasattr(itds.local, "_link_count"):
		itds.local._link_count = defaultdict(int)
		itds.db.after_commit.add(flush_local_link_count)

	itds.local._link_count[(doctype, name)] += 1


def flush_local_link_count():
	"""flush from local before ending request"""
	new_links = getattr(itds.local, "_link_count", None)
	if not new_links:
		return

	link_count = itds.cache.get_value("_link_count") or {}

	flush = False
	for key, value in new_links.items():
		if key in link_count:
			link_count[key] += value
		elif len(link_count) < LINK_COUNT_BUFFER_SIZE:
			link_count[key] = value
		else:
			continue
		flush = True

	if flush:
		itds.cache.set_value("_link_count", link_count)
	new_links.clear()


def update_link_count():
	"""increment link count in the `idx` column for the given document"""
	link_count = itds.cache.get_value("_link_count")

	if link_count:
		for (doctype, name), count in link_count.items():
			try:
				table = itds.qb.DocType(doctype)
				itds.qb.update(table).set(table.idx, table.idx + count).where(table.name == name).run()
				itds.db.commit()
			except Exception as e:
				if not itds.db.is_table_missing(e):  # table not found, single
					raise e
	# reset the count
	itds.cache.delete_value("_link_count")
