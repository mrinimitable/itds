import itds


def execute():
	itds.reload_doc("website", "doctype", "web_page_view", force=True)
	itds.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
