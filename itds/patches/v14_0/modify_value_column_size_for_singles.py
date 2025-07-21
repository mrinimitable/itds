import itds


def execute():
	if itds.db.db_type == "mariadb":
		itds.db.sql_ddl("alter table `tabSingles` modify column `value` longtext")
