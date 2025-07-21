import itds


def execute():
	if itds.db.db_type == "mariadb":
		itds.db.sql(
			"ALTER TABLE __UserSettings CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
		)
