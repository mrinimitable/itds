import itds
from itds.query_builder.functions import Coalesce, GroupConcat


def execute():
	itds.reload_doc("desk", "doctype", "todo")

	ToDo = itds.qb.DocType("ToDo")
	assignees = GroupConcat("owner").distinct().as_("assignees")

	assignments = (
		itds.qb.from_(ToDo)
		.select(ToDo.name, ToDo.reference_type, assignees)
		.where(Coalesce(ToDo.reference_type, "") != "")
		.where(Coalesce(ToDo.reference_name, "") != "")
		.where(ToDo.status != "Cancelled")
		.groupby(ToDo.reference_type, ToDo.reference_name)
	).run(as_dict=True)

	for doc in assignments:
		assignments = doc.assignees.split(",")
		itds.db.set_value(
			doc.reference_type,
			doc.reference_name,
			"_assign",
			itds.as_json(assignments),
			update_modified=False,
		)
