import itds


def execute():
	itds.db.change_column_type("__Auth", column="password", type="TEXT")
