import itds


def execute():
	itds.delete_doc_if_exists("DocType", "Post")
	itds.delete_doc_if_exists("DocType", "Post Comment")
