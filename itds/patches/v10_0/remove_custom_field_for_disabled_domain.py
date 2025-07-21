import itds


def execute():
	itds.reload_doc("core", "doctype", "domain")
	itds.reload_doc("core", "doctype", "has_domain")
	active_domains = itds.get_active_domains()
	all_domains = itds.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = itds.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
