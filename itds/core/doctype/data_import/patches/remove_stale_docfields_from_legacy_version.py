import itds


def execute():
	"""Remove stale docfields from legacy version"""
	itds.db.delete("DocField", {"options": "Data Import", "parent": "Data Import Legacy"})
