import itds


def execute():
	itds.reload_doc("core", "doctype", "user")
	itds.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
