import itds

base_template_path = "www/robots.txt"


def get_context(context):
	robots_txt = (
		itds.db.get_single_value("Website Settings", "robots_txt")
		or (itds.local.conf.robots_txt and itds.read_file(itds.local.conf.robots_txt))
		or ""
	)

	return {"robots_txt": robots_txt}
