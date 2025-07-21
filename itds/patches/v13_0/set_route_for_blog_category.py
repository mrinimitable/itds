import itds


def execute():
	categories = itds.get_list("Blog Category")
	for category in categories:
		doc = itds.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
