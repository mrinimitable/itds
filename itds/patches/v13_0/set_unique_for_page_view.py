import itds


def execute():
	itds.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = itds.utils.get_site_url(itds.local.site)
	itds.db.sql(f"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{site_url}%'""")
