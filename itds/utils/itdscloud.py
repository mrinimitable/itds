import itds

ITDS_CLOUD_DOMAINS = ("itds.cloud", "okayblue.com", "itdshr.com", "itds.dev")


def on_itdscloud() -> bool:
	"""Returns true if running on Itds Cloud.


	Useful for modifying few features for better UX."""
	return itds.local.site.endswith(ITDS_CLOUD_DOMAINS)
