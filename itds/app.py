# Copyright (c) 2015, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import functools
import logging
import os

import orjson
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import ClosingIterator

import itds
import itds.api
import itds.handler
import itds.monitor
import itds.rate_limiter
import itds.recorder
import itds.utils.response
from itds import _
from itds.auth import SAFE_HTTP_METHODS, UNSAFE_HTTP_METHODS, HTTPRequest, check_request_ip, validate_auth
from itds.integrations.oauth2 import get_resource_url, handle_wellknown, is_oauth_metadata_enabled
from itds.middlewares import StaticDataMiddleware
from itds.permissions import handle_does_not_exist_error
from itds.utils import CallbackManager, cint, get_site_name
from itds.utils.data import escape_html
from itds.utils.error import log_error, log_error_snapshot
from itds.website.page_renderers.error_page import ErrorPage
from itds.website.serve import get_response

_site = None
_sites_path = os.environ.get("SITES_PATH", ".")


# If gc.freeze is done then importing modules before forking allows us to share the memory
import gettext

import babel
import babel.messages
import bleach
import num2words
import pydantic

import itds.boot
import itds.client
import itds.core.doctype.file.file
import itds.core.doctype.user.user
import itds.database.mariadb.database  # Load database related utils
import itds.database.query
import itds.desk.desktop  # workspace
import itds.desk.form.save
import itds.model.db_query
import itds.query_builder
import itds.utils.background_jobs  # Enqueue is very common
import itds.utils.data  # common utils
import itds.utils.jinja  # web page rendering
import itds.utils.jinja_globals
import itds.utils.redis_wrapper  # Exact redis_wrapper
import itds.utils.safe_exec
import itds.utils.typing_validations  # any whitelisted method uses this
import itds.website.path_resolver  # all the page types and resolver
import itds.website.router  # Website router
import itds.website.website_generator  # web page doctypes

# end: module pre-loading

# better werkzeug default
# this is necessary because itds desk sends most requests as form data
# and some of them can exceed werkzeug's default limit of 500kb
Request.max_form_memory_size = None


def after_response_wrapper(app):
	"""Wrap a WSGI application to call after_response hooks after we have responded.

	This is done to reduce response time by deferring expensive tasks."""

	@functools.wraps(app)
	def application(environ, start_response):
		return ClosingIterator(
			app(environ, start_response),
			(
				itds.rate_limiter.update,
				itds.recorder.dump,
				itds.request.after_response.run,
				itds.destroy,
			),
		)

	return application


@after_response_wrapper
@Request.application
def application(request: Request):
	response = None

	try:
		init_request(request)

		validate_auth()

		if request.method == "OPTIONS":
			response = Response()

		elif itds.form_dict.cmd:
			from itds.deprecation_dumpster import deprecation_warning

			deprecation_warning(
				"unknown",
				"v17",
				f"{itds.form_dict.cmd}: Sending `cmd` for RPC calls is deprecated, call REST API instead `/api/method/cmd`",
			)
			itds.handler.handle()
			response = itds.utils.response.build_response("json")

		elif request.path.startswith("/api/"):
			response = itds.api.handle(request)

		elif request.path.startswith("/backups"):
			response = itds.utils.response.download_backup(request.path)

		elif request.path.startswith("/private/files/"):
			response = itds.utils.response.download_private_file(request.path)

		elif request.path.startswith("/.well-known/") and request.method == "GET":
			response = handle_wellknown(request.path)

		elif request.method in ("GET", "HEAD", "POST"):
			response = get_response()

		else:
			raise NotFound

	except Exception as e:
		response = e.get_response(request.environ) if isinstance(e, HTTPException) else handle_exception(e)
		if db := getattr(itds.local, "db", None):
			db.rollback(chain=True)

	else:
		sync_database()

	finally:
		# Important note:
		# this function *must* always return a response, hence any exception thrown outside of
		# try..catch block like this finally block needs to be handled appropriately.

		try:
			run_after_request_hooks(request, response)
		except Exception:
			# We can not handle exceptions safely here.
			itds.logger().error("Failed to run after request hook", exc_info=True)

	log_request(request, response)
	process_response(response)

	return response


def run_after_request_hooks(request, response):
	if not getattr(itds.local, "initialised", False):
		return

	for after_request_task in itds.get_hooks("after_request"):
		itds.call(after_request_task, response=response, request=request)


def init_request(request):
	itds.local.request = request
	itds.local.request.after_response = CallbackManager()

	itds.local.is_ajax = itds.get_request_header("X-Requested-With") == "XMLHttpRequest"

	site = _site or request.headers.get("X-Itds-Site-Name") or get_site_name(request.host)
	itds.init(site, sites_path=_sites_path, force=True)

	if not (itds.local.conf and itds.local.conf.db_name):
		# site does not exist
		raise NotFound

	itds.connect(set_admin_as_user=False)
	if itds.local.conf.maintenance_mode:
		if itds.local.conf.allow_reads_during_maintenance:
			setup_read_only_mode()
		else:
			raise itds.SessionStopped("Session Stopped")

	if request.path.startswith("/api/method/upload_file"):
		from itds.core.api.file import get_max_file_size

		request.max_content_length = get_max_file_size()
	else:
		request.max_content_length = cint(itds.local.conf.get("max_file_size")) or 25 * 1024 * 1024
	make_form_dict(request)

	if request.method != "OPTIONS":
		itds.local.http_request = HTTPRequest()

	for before_request_task in itds.get_hooks("before_request"):
		itds.call(before_request_task)


def setup_read_only_mode():
	"""During maintenance_mode reads to DB can still be performed to reduce downtime. This
	function sets up read only mode

	- Setting global flag so other pages, desk and database can know that we are in read only mode.
	- Setup read only database access either by:
	    - Connecting to read replica if one exists
	    - Or setting up read only SQL transactions.
	"""
	itds.flags.read_only = True

	# If replica is available then just connect replica, else setup read only transaction.
	if itds.conf.read_from_replica:
		itds.connect_replica()
	else:
		itds.db.begin(read_only=True)


def log_request(request, response):
	if hasattr(itds.local, "conf") and itds.local.conf.enable_itds_logger:
		itds.logger("itds.web", allow_site=itds.local.site).info(
			{
				"site": get_site_name(request.host),
				"remote_addr": getattr(request, "remote_addr", "NOTFOUND"),
				"pid": os.getpid(),
				"user": getattr(itds.local.session, "user", "NOTFOUND"),
				"base_url": getattr(request, "base_url", "NOTFOUND"),
				"full_path": getattr(request, "full_path", "NOTFOUND"),
				"method": getattr(request, "method", "NOTFOUND"),
				"scheme": getattr(request, "scheme", "NOTFOUND"),
				"http_status_code": getattr(response, "status_code", "NOTFOUND"),
			}
		)


NO_CACHE_HEADERS = {"Cache-Control": "no-store,no-cache,must-revalidate,max-age=0"}


def process_response(response: Response):
	if not response:
		return

	# Default for all requests is no-cache unless explicitly opted-in by endpoint
	response.headers.setdefault("Cache-Control", NO_CACHE_HEADERS["Cache-Control"])

	# rate limiter headers
	if hasattr(itds.local, "rate_limiter"):
		response.headers.update(itds.local.rate_limiter.headers())

	if trace_id := itds.monitor.get_trace_id():
		response.headers.update({"X-Itds-Request-Id": trace_id})

	# CORS headers
	if hasattr(itds.local, "conf"):
		set_cors_headers(response)

	if response.status_code in (401, 403) and is_oauth_metadata_enabled("resource"):
		set_authenticate_headers(response)

	# Update custom headers added during request processing
	response.headers.update(itds.local.response_headers)

	# Set cookies, only if response is non-cacheable to avoid proxy cache invalidation
	public_cache = any("public" in h for h in response.headers.getlist("Cache-Control"))
	if hasattr(itds.local, "cookie_manager") and not public_cache:
		itds.local.cookie_manager.flush_cookies(response=response)

	if itds._dev_server:
		response.headers.update(NO_CACHE_HEADERS)


def set_cors_headers(response):
	allowed_origins = itds.conf.allow_cors
	if hasattr(itds.local, "allow_cors"):
		allowed_origins = itds.local.allow_cors

	if not (
		allowed_origins and (request := itds.local.request) and (origin := request.headers.get("Origin"))
	):
		return

	if allowed_origins != "*":
		if not isinstance(allowed_origins, list):
			allowed_origins = [allowed_origins]

		if origin not in allowed_origins:
			return

	cors_headers = {
		"Access-Control-Allow-Credentials": "true",
		"Access-Control-Allow-Origin": origin,
		"Vary": "Origin",
	}

	# only required for preflight requests
	if request.method == "OPTIONS":
		cors_headers["Access-Control-Allow-Methods"] = request.headers.get("Access-Control-Request-Method")

		if allowed_headers := request.headers.get("Access-Control-Request-Headers"):
			cors_headers["Access-Control-Allow-Headers"] = allowed_headers

		# allow browsers to cache preflight requests for upto a day
		if not itds.conf.developer_mode:
			cors_headers["Access-Control-Max-Age"] = "86400"

	response.headers.update(cors_headers)


def set_authenticate_headers(response: Response):
	headers = {
		"WWW-Authenticate": f'Bearer resource_metadata="{get_resource_url()}/.well-known/oauth-protected-resource"'
	}
	response.headers.update(headers)


def make_form_dict(request: Request):
	request_data = request.get_data(as_text=True)
	if request_data and request.is_json:
		args = orjson.loads(request_data)
	else:
		args = {}
		args.update(request.args or {})
		args.update(request.form or {})

	if isinstance(args, dict):
		itds.local.form_dict = itds._dict(args)
		# _ is passed by $.ajax so that the request is not cached by the browser. So, remove _ from form_dict
		itds.local.form_dict.pop("_", None)
	elif isinstance(args, list):
		itds.local.form_dict["data"] = args
	else:
		itds.throw(_("Invalid request arguments"))


@handle_does_not_exist_error
def handle_exception(e):
	response = None
	http_status_code = getattr(e, "http_status_code", 500)
	accept_header = itds.get_request_header("Accept") or ""
	respond_as_json = (
		itds.get_request_header("Accept") and (itds.local.is_ajax or "application/json" in accept_header)
	) or (itds.local.request.path.startswith("/api/") and not accept_header.startswith("text"))

	if not itds.session.user:
		# If session creation fails then user won't be unset. This causes a lot of code that
		# assumes presence of this to fail. Session creation fails => guest or expired login
		# usually.
		itds.session.user = "Guest"

	if respond_as_json:
		# handle ajax responses first
		# if the request is ajax, send back the trace or error message
		response = itds.utils.response.report_error(http_status_code)

	elif isinstance(e, itds.SessionStopped):
		response = itds.utils.response.handle_session_stopped()

	elif (
		http_status_code == 500
		and (itds.db and isinstance(e, itds.db.InternalError))
		and (itds.db and (itds.db.is_deadlocked(e) or itds.db.is_timedout(e)))
	):
		http_status_code = 508

	elif http_status_code == 401:
		response = ErrorPage(
			http_status_code=http_status_code,
			title=_("Session Expired"),
			message=_("Your session has expired, please login again to continue."),
		).render()

	elif http_status_code == 403:
		response = ErrorPage(
			http_status_code=http_status_code,
			title=_("Not Permitted"),
			message=_("You do not have enough permissions to complete the action"),
		).render()

	elif http_status_code == 404:
		response = ErrorPage(
			http_status_code=http_status_code,
			title=_("Not Found"),
			message=_("The resource you are looking for is not available"),
		).render()

	elif http_status_code == 429:
		response = itds.rate_limiter.respond()

	else:
		response = ErrorPage(
			http_status_code=http_status_code, title=_("Server Error"), message=_("Uncaught Exception")
		).render()

	if e.__class__ == itds.AuthenticationError:
		if hasattr(itds.local, "login_manager"):
			itds.local.login_manager.clear_cookies()

	if http_status_code >= 500 or itds.conf.developer_mode:
		log_error_snapshot(e)

	if itds.conf.get("developer_mode") and not respond_as_json:
		# don't fail silently for non-json response errors
		print(itds.get_traceback())

	return response


def sync_database():
	db = getattr(itds.local, "db", None)
	if not db:
		# db isn't initialized, can't commit or rollback
		return

	# if HTTP method would change server state, commit if necessary
	if itds.local.request.method in UNSAFE_HTTP_METHODS or itds.local.flags.commit:
		db.commit(chain=True)
	else:
		db.rollback(chain=True)

	# update session
	if session := getattr(itds.local, "session_obj", None):
		itds.request.after_response.add(session.update)


# Always initialize sentry SDK if the DSN is sent
if sentry_dsn := os.getenv("ITDS_SENTRY_DSN"):
	import sentry_sdk
	from sentry_sdk.integrations.argv import ArgvIntegration
	from sentry_sdk.integrations.atexit import AtexitIntegration
	from sentry_sdk.integrations.dedupe import DedupeIntegration
	from sentry_sdk.integrations.excepthook import ExcepthookIntegration
	from sentry_sdk.integrations.modules import ModulesIntegration
	from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

	from itds.utils.sentry import ItdsIntegration, before_send

	integrations = [
		AtexitIntegration(),
		ExcepthookIntegration(),
		DedupeIntegration(),
		ModulesIntegration(),
		ArgvIntegration(),
	]

	experiments = {}
	kwargs = {}

	if os.getenv("ENABLE_SENTRY_DB_MONITORING"):
		integrations.append(ItdsIntegration())
		experiments["record_sql_params"] = True

	if tracing_sample_rate := os.getenv("SENTRY_TRACING_SAMPLE_RATE"):
		kwargs["traces_sample_rate"] = float(tracing_sample_rate)
		application = SentryWsgiMiddleware(application)

	if profiling_sample_rate := os.getenv("SENTRY_PROFILING_SAMPLE_RATE"):
		kwargs["profiles_sample_rate"] = float(profiling_sample_rate)

	sentry_sdk.init(
		dsn=sentry_dsn,
		before_send=before_send,
		attach_stacktrace=True,
		release=itds.__version__,
		auto_enabling_integrations=False,
		default_integrations=False,
		integrations=integrations,
		_experiments=experiments,
		**kwargs,
	)


def serve(
	port=8000,
	profile=False,
	no_reload=False,
	no_threading=False,
	site=None,
	sites_path=".",
	proxy=False,
):
	global application, _site, _sites_path
	_site = site
	_sites_path = sites_path

	from werkzeug.serving import run_simple

	if profile or os.environ.get("USE_PROFILER"):
		application = ProfilerMiddleware(application, sort_by=("cumtime", "calls"), restrictions=(200,))

	if not os.environ.get("NO_STATICS"):
		application = application_with_statics()

	if proxy or os.environ.get("USE_PROXY"):
		application = ProxyFix(application, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

	application.debug = True
	application.config = {"SERVER_NAME": "127.0.0.1:8000"}

	log = logging.getLogger("werkzeug")
	log.propagate = False

	in_test_env = os.environ.get("CI")
	if in_test_env:
		log.setLevel(logging.ERROR)

	run_simple(
		"0.0.0.0",
		int(port),
		application,
		exclude_patterns=["test_*"],
		use_reloader=False if in_test_env else not no_reload,
		use_debugger=not in_test_env,
		use_evalex=not in_test_env,
		threaded=not no_threading,
	)


def application_with_statics():
	global application, _sites_path

	application = SharedDataMiddleware(application, {"/assets": str(os.path.join(_sites_path, "assets"))})

	application = StaticDataMiddleware(application, {"/files": str(os.path.abspath(_sites_path))})

	return application
