# Copyright (c) 2024, Itds Technologies and contributors
# For license information, please see license.txt

import itds
from itds import _
from itds.model.document import Document
from itds.utils import get_url

from .providers.geoapify import Geoapify
from .providers.here import Here
from .providers.nomatim import Nomatim


class GeolocationSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		api_key: DF.Password | None
		base_url: DF.Data | None
		enable_address_autocompletion: DF.Check
		provider: DF.Literal["Geoapify", "Nomatim", "HERE"]
	# end: auto-generated types

	pass


@itds.whitelist()
def autocomplete(txt: str) -> list[dict]:
	if not txt:
		return []

	settings = itds.get_single("Geolocation Settings")
	if not settings.enable_address_autocompletion:
		return []

	if settings.provider == "Geoapify":
		provider = Geoapify(settings.get_password("api_key"), itds.local.lang)
	elif settings.provider == "Nomatim":
		provider = Nomatim(
			base_url=settings.base_url,
			referer=get_url(),
			lang=itds.local.lang,
		)
	elif settings.provider == "HERE":
		provider = Here(settings.get_password("api_key"), itds.local.lang)
	else:
		itds.throw(_("This geolocation provider is not supported yet."))

	return list(provider.autocomplete(txt))
