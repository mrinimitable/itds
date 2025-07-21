import itds
from itds.utils import cint

no_cache = 1


def get_context(context):
	itds.db.commit()  # nosemgrep
	context = itds._dict()
	context.boot = get_boot()
	return context


def get_boot():
	return itds._dict(
		{
			"site_name": itds.local.site,
			"read_only_mode": itds.flags.read_only,
			"csrf_token": itds.sessions.get_csrf_token(),
			"setup_complete": itds.is_setup_complete(),
		}
	)
