import re

import itds
from itds.core.doctype.user.user import create_contact


def execute():
	"""Create Contact for each User if not present"""
	itds.reload_doc("integrations", "doctype", "google_contacts")
	itds.reload_doc("contacts", "doctype", "contact")
	itds.reload_doc("core", "doctype", "dynamic_link")

	contact_meta = itds.get_meta("Contact")
	if contact_meta.has_field("phone_nos") and contact_meta.has_field("email_ids"):
		itds.reload_doc("contacts", "doctype", "contact_phone")
		itds.reload_doc("contacts", "doctype", "contact_email")

	users = itds.get_all("User", filters={"name": ("not in", "Administrator, Guest")}, fields=["*"])
	for user in users:
		if itds.db.exists("Contact", {"email_id": user.email}) or itds.db.exists(
			"Contact Email", {"email_id": user.email}
		):
			continue
		if user.first_name:
			user.first_name = re.sub("[<>]+", "", itds.safe_decode(user.first_name))
		if user.last_name:
			user.last_name = re.sub("[<>]+", "", itds.safe_decode(user.last_name))
		create_contact(user, ignore_links=True, ignore_mandatory=True)
