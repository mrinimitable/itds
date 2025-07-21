import itds


# no context object is accepted
def get_context():
	context = itds._dict()
	context.body = "Custom Content"
	return context
