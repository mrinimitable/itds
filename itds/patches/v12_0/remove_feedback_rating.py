import itds


def execute():
	"""
	Deprecate Feedback Trigger and Rating. This feature was not customizable.
	Now can be achieved via custom Web Forms
	"""
	itds.delete_doc("DocType", "Feedback Trigger")
	itds.delete_doc("DocType", "Feedback Rating")
