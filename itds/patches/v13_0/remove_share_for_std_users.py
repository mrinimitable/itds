import itds
import itds.share


def execute():
	for user in itds.STANDARD_USERS:
		itds.share.remove("User", user, user)
