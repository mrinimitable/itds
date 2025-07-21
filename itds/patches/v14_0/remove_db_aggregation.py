import re

import itds
from itds.query_builder import DocType


def execute():
	"""Replace temporarily available Database Aggregate APIs on itds (develop)

	APIs changed:
	        * itds.db.max => itds.qb.max
	        * itds.db.min => itds.qb.min
	        * itds.db.sum => itds.qb.sum
	        * itds.db.avg => itds.qb.avg
	"""
	ServerScript = DocType("Server Script")
	server_scripts = (
		itds.qb.from_(ServerScript)
		.where(
			ServerScript.script.like("%itds.db.max(%")
			| ServerScript.script.like("%itds.db.min(%")
			| ServerScript.script.like("%itds.db.sum(%")
			| ServerScript.script.like("%itds.db.avg(%")
		)
		.select("name", "script")
		.run(as_dict=True)
	)

	for server_script in server_scripts:
		name, script = server_script["name"], server_script["script"]

		for agg in ["avg", "max", "min", "sum"]:
			script = re.sub(f"itds.db.{agg}\\(", f"itds.qb.{agg}(", script)

		itds.db.set_value("Server Script", name, "script", script)
