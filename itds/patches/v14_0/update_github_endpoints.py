import json

import itds


def execute():
	if itds.db.exists("Social Login Key", "github"):
		itds.db.set_value(
			"Social Login Key", "github", "auth_url_data", json.dumps({"scope": "user:email"})
		)
