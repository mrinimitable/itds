import itds
from itds.cache_manager import clear_defaults_cache


def execute():
	itds.db.set_default(
		"suspend_email_queue",
		itds.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	itds.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
