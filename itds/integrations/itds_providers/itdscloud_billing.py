import requests

import itds
from itds import _


def get_base_url():
	url = "https://itdscloud.com"
	if itds.conf.developer_mode and itds.conf.get("fc_base_url"):
		url = itds.conf.get("fc_base_url")
	return url


def get_site_login_url():
	return f"{get_base_url()}/dashboard/site-login"


def get_site_name():
	site_name = itds.local.site
	if itds.conf.developer_mode and itds.conf.get("saas_billing_site_name"):
		site_name = itds.conf.get("saas_billing_site_name")
	return site_name


def get_headers():
	# check if user is system manager
	if itds.get_roles(itds.session.user).count("System Manager") == 0:
		itds.throw(_("You are not allowed to access this resource"))

	# check if communication secret is set
	if not itds.conf.get("fc_communication_secret"):
		itds.throw(_("Communication secret not set"))

	return {
		"X-Site-Token": itds.conf.get("fc_communication_secret"),
		"X-Site-User": itds.session.user,
		"X-Site": get_site_name(),
	}


@itds.whitelist()
def current_site_info():
	from itds.utils import cint

	request = requests.post(f"{get_base_url()}/api/method/press.saas.api.site.info", headers=get_headers())
	if request.status_code == 200:
		res = request.json().get("message")
		if not res:
			return None

		return {
			**res,
			"site_name": get_site_name(),
			"base_url": get_base_url(),
			"setup_complete": cint(itds.get_system_settings("setup_complete")),
		}

	else:
		itds.throw(_("Failed to get site info"))


@itds.whitelist()
def api(method, data=None):
	if data is None:
		data = {}
	request = requests.post(
		f"{get_base_url()}/api/method/press.saas.api.{method}",
		headers=get_headers(),
		json=data,
	)
	if request.status_code == 200:
		return request.json().get("message")
	else:
		itds.throw(_("Failed while calling API {0}", method))


@itds.whitelist()
def is_fc_site() -> bool:
	is_system_manager = itds.get_roles(itds.session.user).count("System Manager")
	return bool(is_system_manager and itds.conf.get("fc_communication_secret"))


# login to itds cloud dashboard
@itds.whitelist()
def send_verification_code():
	request = requests.post(
		f"{get_base_url()}/api/method/press.api.developer.saas.send_verification_code",
		headers=get_headers(),
		json={"domain": get_site_name()},
	)
	if request.status_code == 200:
		return request.json().get("message")
	else:
		itds.throw(_("Failed to request login to Itds Cloud"))


@itds.whitelist()
def verify_verification_code(verification_code: str, route: str):
	request = requests.post(
		f"{get_base_url()}/api/method/press.api.developer.saas.verify_verification_code",
		headers=get_headers(),
		json={"domain": get_site_name(), "verification_code": verification_code, "route": route},
	)

	if request.status_code == 200:
		return {
			"base_url": get_base_url(),
			"login_token": request.json()["login_token"],
		}
	else:
		itds.throw(_("Invalid Code. Please try again."))
