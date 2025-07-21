import itds


def execute():
	providers = itds.get_all("Social Login Key")

	for provider in providers:
		doc = itds.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
