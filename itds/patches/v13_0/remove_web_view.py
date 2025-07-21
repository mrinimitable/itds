import itds


def execute():
	itds.delete_doc_if_exists("DocType", "Web View")
	itds.delete_doc_if_exists("DocType", "Web View Component")
	itds.delete_doc_if_exists("DocType", "CSS Class")
