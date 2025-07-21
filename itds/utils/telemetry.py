"""Basic telemetry for improving apps.

WARNING: Everything in this file should be treated "internal" and is subjected to change or get
removed without any warning.
"""

from contextlib import suppress
from functools import lru_cache

import itds
from itds.utils import getdate
from itds.utils.caching import site_cache

from posthog import Posthog  # isort: skip

POSTHOG_PROJECT_FIELD = "posthog_project_id"
POSTHOG_HOST_FIELD = "posthog_host"


def add_bootinfo(bootinfo):
	bootinfo.telemetry_site_age = site_age()

	if not itds.get_system_settings("enable_telemetry"):
		return

	bootinfo.enable_telemetry = True
	bootinfo.posthog_host = itds.conf.get(POSTHOG_HOST_FIELD)
	bootinfo.posthog_project_id = itds.conf.get(POSTHOG_PROJECT_FIELD)


@site_cache(ttl=60 * 60 * 12)
def site_age():
	try:
		est_creation = itds.db.get_value("User", "Administrator", "creation")
		return (getdate() - getdate(est_creation)).days + 1
	except Exception:
		pass


def init_telemetry():
	"""Init posthog for server side telemetry."""
	if hasattr(itds.local, "posthog"):
		return

	if not itds.get_system_settings("enable_telemetry"):
		return

	posthog_host = itds.conf.get(POSTHOG_HOST_FIELD)
	posthog_project_id = itds.conf.get(POSTHOG_PROJECT_FIELD)

	if not posthog_host or not posthog_project_id:
		return

	with suppress(Exception):
		itds.local.posthog = _get_posthog_instance(posthog_project_id, posthog_host)

	# Background jobs might exit before flushing telemetry, so explicitly flush queue
	if itds.job:
		itds.job.after_job.add(flush_telemetry)


@lru_cache
def _get_posthog_instance(project_id, host):
	return Posthog(project_id, host=host, timeout=5, max_retries=3)


def flush_telemetry():
	ph: Posthog = getattr(itds.local, "posthog", None)
	with suppress(Exception):
		ph and ph.flush()


def capture(event, app, **kwargs):
	init_telemetry()
	ph: Posthog = getattr(itds.local, "posthog", None)
	with suppress(Exception):
		ph and ph.capture(distinct_id=itds.local.site, event=f"{app}_{event}", **kwargs)


def capture_doc(doc, action):
	with suppress(Exception):
		age = site_age()
		if not age or age > 15:
			return

		if doc.get("__islocal") or not doc.get("name"):
			capture("document_created", "itds", properties={"doctype": doc.doctype, "action": "Insert"})
		else:
			capture("document_modified", "itds", properties={"doctype": doc.doctype, "action": action})
