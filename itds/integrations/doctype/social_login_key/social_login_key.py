# Copyright (c) 2017, Itds Technologies and contributors
# License: MIT. See LICENSE

import json

import itds
from itds import _
from itds.model.document import Document


class BaseUrlNotSetError(itds.ValidationError):
	pass


class AuthorizeUrlNotSetError(itds.ValidationError):
	pass


class AccessTokenUrlNotSetError(itds.ValidationError):
	pass


class RedirectUrlNotSetError(itds.ValidationError):
	pass


class ClientIDNotSetError(itds.ValidationError):
	pass


class ClientSecretNotSetError(itds.ValidationError):
	pass


class SocialLoginKey(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from itds.types import DF

		access_token_url: DF.Data | None
		api_endpoint: DF.Data | None
		api_endpoint_args: DF.Code | None
		auth_url_data: DF.Code | None
		authorize_url: DF.Data | None
		base_url: DF.Data | None
		client_id: DF.Data | None
		client_secret: DF.Password | None
		custom_base_url: DF.Check
		enable_social_login: DF.Check
		icon: DF.Data | None
		provider_name: DF.Data
		redirect_url: DF.Data | None
		show_in_resource_metadata: DF.Check
		sign_ups: DF.Literal["", "Allow", "Deny"]
		social_login_provider: DF.Literal[
			"Custom",
			"Facebook",
			"Itds",
			"GitHub",
			"Google",
			"Office 365",
			"Salesforce",
			"fairlogin",
			"Keycloak",
		]
		user_id_property: DF.Data | None
	# end: auto-generated types

	def autoname(self):
		self.name = itds.scrub(self.provider_name)

	def validate(self):
		self.set_icon()
		if self.custom_base_url and not self.base_url:
			itds.throw(_("Please enter Base URL"), exc=BaseUrlNotSetError)
		if not self.authorize_url:
			itds.throw(_("Please enter Authorize URL"), exc=AuthorizeUrlNotSetError)
		if not self.access_token_url:
			itds.throw(_("Please enter Access Token URL"), exc=AccessTokenUrlNotSetError)
		if not self.redirect_url:
			itds.throw(_("Please enter Redirect URL"), exc=RedirectUrlNotSetError)
		if self.enable_social_login and not self.client_id:
			itds.throw(_("Please enter Client ID before social login is enabled"), exc=ClientIDNotSetError)
		if self.enable_social_login and not self.client_secret:
			itds.throw(
				_("Please enter Client Secret before social login is enabled"), exc=ClientSecretNotSetError
			)

	def set_icon(self):
		icon_map = {
			"Google": "google.svg",
			"Itds": "itds.svg",
			"Facebook": "facebook.svg",
			"Office 365": "office_365.svg",
			"GitHub": "github.svg",
			"Salesforce": "salesforce.svg",
			"fairlogin": "fair.svg",
		}

		if self.provider_name in icon_map:
			icon_file = icon_map[self.provider_name]
			self.icon = f"/assets/itds/icons/social/{icon_file}"

	@itds.whitelist()
	def get_social_login_provider(self, provider, initialize=False):
		providers = {}

		providers["Office 365"] = {
			"provider_name": "Office 365",
			"enable_social_login": 1,
			"base_url": "https://login.microsoftonline.com",
			"custom_base_url": 0,
			"icon": "fa fa-windows",
			"authorize_url": "https://login.microsoftonline.com/common/oauth2/authorize",
			"access_token_url": "https://login.microsoftonline.com/common/oauth2/token",
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_office365",
			"api_endpoint": None,
			"api_endpoint_args": None,
			"auth_url_data": json.dumps({"response_type": "code", "scope": "openid"}),
		}

		providers["GitHub"] = {
			"provider_name": "GitHub",
			"enable_social_login": 1,
			"base_url": "https://api.github.com/",
			"custom_base_url": 0,
			"icon": "fa fa-github",
			"authorize_url": "https://github.com/login/oauth/authorize",
			"access_token_url": "https://github.com/login/oauth/access_token",
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_github",
			"api_endpoint": "user",
			"api_endpoint_args": None,
			"auth_url_data": json.dumps({"scope": "user:email"}),
		}

		providers["Google"] = {
			"provider_name": "Google",
			"enable_social_login": 1,
			"base_url": "https://www.googleapis.com",
			"custom_base_url": 0,
			"icon": "fa fa-google",
			"authorize_url": "https://accounts.google.com/o/oauth2/auth",
			"access_token_url": "https://accounts.google.com/o/oauth2/token",
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_google",
			"api_endpoint": "oauth2/v2/userinfo",
			"api_endpoint_args": None,
			"auth_url_data": json.dumps(
				{
					"scope": "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
					"response_type": "code",
				}
			),
		}

		providers["Facebook"] = {
			"provider_name": "Facebook",
			"enable_social_login": 1,
			"base_url": "https://graph.facebook.com",
			"custom_base_url": 0,
			"icon": "fa fa-facebook",
			"authorize_url": "https://www.facebook.com/dialog/oauth",
			"access_token_url": "https://graph.facebook.com/oauth/access_token",
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_facebook",
			"api_endpoint": "/v2.5/me",
			"api_endpoint_args": json.dumps(
				{"fields": "first_name,last_name,email,gender,location,verified,picture"}
			),
			"auth_url_data": json.dumps(
				{"display": "page", "response_type": "code", "scope": "email,public_profile"}
			),
		}

		providers["Itds"] = {
			"provider_name": "Itds",
			"enable_social_login": 1,
			"custom_base_url": 1,
			"icon": "/assets/itds/images/itds-favicon.svg",
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_itds",
			"api_endpoint": "/api/method/itds.integrations.oauth2.openid_profile",
			"api_endpoint_args": None,
			"authorize_url": "/api/method/itds.integrations.oauth2.authorize",
			"access_token_url": "/api/method/itds.integrations.oauth2.get_token",
			"auth_url_data": json.dumps({"response_type": "code", "scope": "openid"}),
		}

		providers["Salesforce"] = {
			"provider_name": "Salesforce",
			"enable_social_login": 1,
			"base_url": "https://login.salesforce.com",
			"custom_base_url": 0,
			"icon": "fa fa-cloud",  # https://github.com/FortAwesome/Font-Awesome/issues/1744
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_salesforce",
			"api_endpoint": "https://login.salesforce.com/services/oauth2/userinfo",
			"api_endpoint_args": None,
			"authorize_url": "https://login.salesforce.com/services/oauth2/authorize",
			"access_token_url": "https://login.salesforce.com/services/oauth2/token",
			"auth_url_data": json.dumps({"response_type": "code", "scope": "openid"}),
		}

		providers["fairlogin"] = {
			"provider_name": "fairlogin",
			"enable_social_login": 1,
			"base_url": "https://id.fairkom.net/auth/realms/fairlogin/",
			"custom_base_url": 0,
			"icon": "fa fa-key",
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_fairlogin",
			"api_endpoint": "https://id.fairkom.net/auth/realms/fairlogin/protocol/openid-connect/userinfo",
			"api_endpoint_args": None,
			"authorize_url": "https://id.fairkom.net/auth/realms/fairlogin/protocol/openid-connect/auth",
			"access_token_url": "https://id.fairkom.net/auth/realms/fairlogin/protocol/openid-connect/token",
			"auth_url_data": json.dumps({"response_type": "code", "scope": "openid"}),
		}

		providers["Keycloak"] = {
			"provider_name": "Keycloak",
			"enable_social_login": 1,
			"custom_base_url": 1,
			"redirect_url": "/api/method/itds.integrations.oauth2_logins.login_via_keycloak",
			"api_endpoint": "/protocol/openid-connect/userinfo",
			"api_endpoint_args": None,
			"authorize_url": "/protocol/openid-connect/auth",
			"access_token_url": "/protocol/openid-connect/token",
			"user_id_property": "preferred_username",
			"auth_url_data": json.dumps({"response_type": "code", "scope": "openid"}),
		}

		# Initialize the doc and return, used in patch
		# Or can be used for creating key from controller
		if initialize and provider:
			for k, v in providers[provider].items():
				setattr(self, k, v)
			return

		return providers.get(provider) if provider else providers


def provider_allows_signup(provider: str) -> bool:
	from itds.website.utils import is_signup_disabled

	sign_up_config = itds.db.get_value("Social Login Key", provider, "sign_ups")

	if not sign_up_config:  # fallback to global settings
		return not is_signup_disabled()
	return sign_up_config == "Allow"
