import itds
from itds.desk.utils import slug


def execute():
	for doctype in itds.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			itds.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
