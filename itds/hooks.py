import os

from . import __version__ as app_version

app_name = "itds"
app_title = "Itds Framework"
app_publisher = "Itds Technologies"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
app_license = "MIT"
app_logo_url = "/assets/itds/images/itds-framework-logo.svg"
develop_version = "15.x.x-develop"
app_home = "/app/build"

app_email = "developers@itds.io"

before_install = "itds.utils.install.before_install"
after_install = "itds.utils.install.after_install"

page_js = {"setup-wizard": "public/js/itds/setup_wizard.js"}

# website
app_include_js = [
	"libs.bundle.js",
	"desk.bundle.js",
	"list.bundle.js",
	"form.bundle.js",
	"controls.bundle.js",
	"report.bundle.js",
	"telemetry.bundle.js",
	"billing.bundle.js",
]

app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]
app_include_icons = [
	"/assets/itds/icons/timeless/icons.svg",
	"/assets/itds/icons/espresso/icons.svg",
]

doctype_js = {
	"Web Page": "public/js/itds/utils/web_template.js",
	"Website Settings": "public/js/itds/utils/web_template.js",
}

web_include_js = ["website_script.js"]
web_include_css = []
web_include_icons = [
	"/assets/itds/icons/timeless/icons.svg",
	"/assets/itds/icons/espresso/icons.svg",
]

email_css = ["email.bundle.css"]

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "itds.core.notifications.get_notification_config"

before_tests = "itds.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

calendars = ["Event"]

# login

on_session_creation = [
	"itds.core.doctype.activity_log.feed.login_feed",
	"itds.core.doctype.user.user.notify_admin_access_to_system_manager",
]

on_login = "itds.desk.doctype.note.note._get_unseen_notes"
on_logout = "itds.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"

# PDF
pdf_header_html = "itds.utils.pdf.pdf_header_html"
pdf_body_html = "itds.utils.pdf.pdf_body_html"
pdf_footer_html = "itds.utils.pdf.pdf_footer_html"

# permissions

permission_query_conditions = {
	"Event": "itds.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "itds.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "itds.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "itds.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "itds.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "itds.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "itds.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "itds.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "itds.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "itds.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "itds.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "itds.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "itds.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "itds.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "itds.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "itds.core.doctype.prepared_report.prepared_report.get_permission_query_condition",
	"File": "itds.core.doctype.file.file.get_permission_query_conditions",
}

has_permission = {
	"Event": "itds.desk.doctype.event.event.has_permission",
	"ToDo": "itds.desk.doctype.todo.todo.has_permission",
	"Note": "itds.desk.doctype.note.note.has_permission",
	"User": "itds.core.doctype.user.user.has_permission",
	"Dashboard Chart": "itds.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "itds.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "itds.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "itds.contacts.address_and_contact.has_permission",
	"Address": "itds.contacts.address_and_contact.has_permission",
	"Communication": "itds.core.doctype.communication.communication.has_permission",
	"Workflow Action": "itds.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "itds.core.doctype.file.file.has_permission",
	"Prepared Report": "itds.core.doctype.prepared_report.prepared_report.has_permission",
	"Notification Settings": "itds.desk.doctype.notification_settings.notification_settings.has_permission",
}

has_website_permission = {"Address": "itds.contacts.doctype.address.address.has_website_permission"}

jinja = {
	"methods": "itds.utils.jinja_globals",
	"filters": [
		"itds.utils.data.global_date_format",
		"itds.utils.markdown",
		"itds.website.utils.abs_url",
	],
}

standard_queries = {"User": "itds.core.doctype.user.user.user_query"}

doc_events = {
	"*": {
		"on_update": [
			"itds.desk.notifications.clear_doctype_notifications",
			"itds.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"itds.core.doctype.file.utils.attach_files_to_document",
			"itds.automation.doctype.assignment_rule.assignment_rule.apply",
			"itds.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"itds.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type",
			"itds.core.doctype.permission_log.permission_log.make_perm_log",
		],
		"after_rename": "itds.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"itds.desk.notifications.clear_doctype_notifications",
			"itds.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"itds.automation.doctype.assignment_rule.assignment_rule.apply",
		],
		"on_trash": [
			"itds.desk.notifications.clear_doctype_notifications",
			"itds.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
		],
		"on_update_after_submit": [
			"itds.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"itds.automation.doctype.assignment_rule.assignment_rule.apply",
			"itds.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"itds.core.doctype.file.utils.attach_files_to_document",
		],
		"on_change": [
			"itds.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone",
		],
		"after_delete": ["itds.core.doctype.permission_log.permission_log.make_perm_log"],
	},
	"Event": {
		"after_insert": "itds.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "itds.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "itds.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "itds.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "itds.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"on_update": "itds.cache_manager.build_domain_restricted_doctype_cache",
	},
	"Page": {
		"on_update": "itds.cache_manager.build_domain_restricted_page_cache",
	},
}

scheduler_events = {
	"cron": {
		# 5 minutes
		"0/5 * * * *": [
			"itds.email.doctype.notification.notification.trigger_offset_alerts",
		],
		# 15 minutes
		"0/15 * * * *": [
			"itds.email.doctype.email_account.email_account.notify_unreplied",
			"itds.utils.global_search.sync_global_search",
			"itds.deferred_insert.save_to_db",
			"itds.automation.doctype.reminder.reminder.send_reminders",
			"itds.model.utils.link_count.update_link_count",
		],
		# 10 minutes
		"0/10 * * * *": [
			"itds.email.doctype.email_account.email_account.pull",
		],
		# Hourly but offset by 30 minutes
		"30 * * * *": [],
		# Daily but offset by 45 minutes
		"45 0 * * *": [],
	},
	"all": [
		"itds.email.queue.flush",
		"itds.email.queue.retry_sending_emails",
		"itds.monitor.flush",
		"itds.integrations.doctype.google_calendar.google_calendar.sync",
	],
	"hourly": [],
	# Maintenance queue happen roughly once an hour but don't align with wall-clock time of *:00
	# Use these for when you don't care about when the job runs but just need some guarantee for
	# frequency.
	"hourly_maintenance": [
		"itds.model.utils.user_settings.sync_user_settings",
		"itds.desk.page.backups.backups.delete_downloadable_backups",
		"itds.desk.form.document_follow.send_hourly_updates",
		"itds.website.doctype.personal_data_deletion_request.personal_data_deletion_request.process_data_deletion_request",
		"itds.core.doctype.prepared_report.prepared_report.expire_stalled_report",
		"itds.twofactor.delete_all_barcodes_for_users",
		"itds.oauth.delete_oauth2_data",
		"itds.website.doctype.web_page.web_page.check_publish_status",
	],
	"daily": [
		"itds.desk.doctype.event.event.send_event_digest",
		"itds.email.doctype.notification.notification.trigger_daily_alerts",
		"itds.desk.form.document_follow.send_daily_updates",
	],
	"daily_long": [],
	"daily_maintenance": [
		"itds.email.doctype.auto_email_report.auto_email_report.send_daily",
		"itds.desk.notifications.clear_notifications",
		"itds.sessions.clear_expired_sessions",
		"itds.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"itds.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
		"itds.core.doctype.log_settings.log_settings.run_log_clean_up",
	],
	"weekly_long": [
		"itds.desk.form.document_follow.send_weekly_updates",
		"itds.utils.change_log.check_for_update",
		"itds.desk.doctype.changelog_feed.changelog_feed.fetch_changelog_feed",
	],
	"monthly": [
		"itds.email.doctype.auto_email_report.auto_email_report.send_monthly",
	],
}

sounds = [
	{"name": "email", "src": "/assets/itds/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/itds/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/itds/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/itds/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/itds/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/itds/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/itds/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/itds/sounds/chime.mp3"},
]

setup_wizard_exception = [
	"itds.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"itds.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception",
]

before_migrate = ["itds.core.doctype.patch_log.patch_log.before_migrate"]
after_migrate = ["itds.website.doctype.website_theme.website_theme.after_migrate"]

otp_methods = ["OTP App", "Email", "SMS"]

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"},
	]
}

override_whitelisted_methods = {
	# Legacy File APIs
	"itds.utils.file_manager.download_file": "download_file",
	"itds.core.doctype.file.file.download_file": "download_file",
	"itds.core.doctype.file.file.unzip_file": "itds.core.api.file.unzip_file",
	"itds.core.doctype.file.file.get_attached_images": "itds.core.api.file.get_attached_images",
	"itds.core.doctype.file.file.get_files_in_folder": "itds.core.api.file.get_files_in_folder",
	"itds.core.doctype.file.file.get_files_by_search_text": "itds.core.api.file.get_files_by_search_text",
	"itds.core.doctype.file.file.get_max_file_size": "itds.core.api.file.get_max_file_size",
	"itds.core.doctype.file.file.create_new_folder": "itds.core.api.file.create_new_folder",
	"itds.core.doctype.file.file.move_file": "itds.core.api.file.move_file",
	"itds.core.doctype.file.file.zip_files": "itds.core.api.file.zip_files",
	# Legacy (& Consistency) OAuth2 APIs
	"itds.www.login.login_via_google": "itds.integrations.oauth2_logins.login_via_google",
	"itds.www.login.login_via_github": "itds.integrations.oauth2_logins.login_via_github",
	"itds.www.login.login_via_facebook": "itds.integrations.oauth2_logins.login_via_facebook",
	"itds.www.login.login_via_itds": "itds.integrations.oauth2_logins.login_via_itds",
	"itds.www.login.login_via_office365": "itds.integrations.oauth2_logins.login_via_office365",
	"itds.www.login.login_via_salesforce": "itds.integrations.oauth2_logins.login_via_salesforce",
	"itds.www.login.login_via_fairlogin": "itds.integrations.oauth2_logins.login_via_fairlogin",
}

ignore_links_on_delete = [
	"Communication",
	"ToDo",
	"DocShare",
	"Email Unsubscribe",
	"Activity Log",
	"File",
	"Version",
	"Document Follow",
	"Comment",
	"View Log",
	"Tag Link",
	"Notification Log",
	"Email Queue",
	"Document Share Key",
	"Integration Request",
	"Unhandled Email",
	"Webhook Request Log",
	"Workspace",
	"Route History",
	"Access Log",
	"Permission Log",
]

# Request Hooks
before_request = [
	"itds.recorder.record",
	"itds.monitor.start",
	"itds.rate_limiter.apply",
	"itds.integrations.oauth2.set_cors_for_privileged_requests",
]

after_request = [
	"itds.monitor.stop",
]

# Background Job Hooks
before_job = [
	"itds.recorder.record",
	"itds.monitor.start",
]

if os.getenv("ITDS_SENTRY_DSN") and (
	os.getenv("ENABLE_SENTRY_DB_MONITORING")
	or os.getenv("SENTRY_TRACING_SAMPLE_RATE")
	or os.getenv("SENTRY_PROFILING_SAMPLE_RATE")
):
	before_request.append("itds.utils.sentry.set_sentry_context")
	before_job.append("itds.utils.sentry.set_sentry_context")

after_job = [
	"itds.recorder.dump",
	"itds.monitor.stop",
	"itds.utils.file_lock.release_document_locks",
]

extend_bootinfo = [
	"itds.utils.telemetry.add_bootinfo",
	"itds.core.doctype.user_permission.user_permission.send_user_permissions",
]

get_changelog_feed = "itds.desk.doctype.changelog_feed.changelog_feed.get_feed"

export_python_type_annotations = True

standard_navbar_items = [
	{
		"item_label": "User Settings",
		"item_type": "Action",
		"action": "itds.ui.toolbar.route_to_user()",
		"is_standard": 1,
	},
	{
		"item_label": "Workspace Settings",
		"item_type": "Action",
		"action": "itds.quick_edit('Workspace Settings')",
		"is_standard": 1,
	},
	{
		"item_label": "Session Defaults",
		"item_type": "Action",
		"action": "itds.ui.toolbar.setup_session_defaults()",
		"is_standard": 1,
	},
	{
		"item_label": "Reload",
		"item_type": "Action",
		"action": "itds.ui.toolbar.clear_cache()",
		"is_standard": 1,
	},
	{
		"item_label": "View Website",
		"item_type": "Action",
		"action": "itds.ui.toolbar.view_website()",
		"is_standard": 1,
	},
	{
		"item_label": "Apps",
		"item_type": "Route",
		"route": "/apps",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Full Width",
		"item_type": "Action",
		"action": "itds.ui.toolbar.toggle_full_width()",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Theme",
		"item_type": "Action",
		"action": "new itds.ui.ThemeSwitcher().show()",
		"is_standard": 1,
	},
	{
		"item_type": "Separator",
		"is_standard": 1,
		"item_label": "",
	},
	{
		"item_label": "Log out",
		"item_type": "Action",
		"action": "itds.app.logout()",
		"is_standard": 1,
	},
]

standard_help_items = [
	{
		"item_label": "About",
		"item_type": "Action",
		"action": "itds.ui.toolbar.show_about()",
		"is_standard": 1,
	},
	{
		"item_label": "Keyboard Shortcuts",
		"item_type": "Action",
		"action": "itds.ui.toolbar.show_shortcuts(event)",
		"is_standard": 1,
	},
	{
		"item_label": "System Health",
		"item_type": "Route",
		"route": "/app/system-health-report",
		"is_standard": 1,
	},
	{
		"item_label": "Itds Support",
		"item_type": "Route",
		"route": "https://itds.io/support",
		"is_standard": 1,
	},
]

# log doctype cleanups to automatically add in log settings
default_log_clearing_doctypes = {
	"Error Log": 14,
	"Email Queue": 30,
	"Scheduled Job Log": 7,
	"Submission Queue": 7,
	"Prepared Report": 14,
	"Webhook Request Log": 30,
	"Unhandled Email": 30,
	"Reminder": 30,
	"Integration Request": 90,
	"Activity Log": 90,
	"Route History": 90,
	"OAuth Bearer Token": 30,
	"API Request Log": 90,
}

# These keys will not be erased when doing itds.clear_cache()
persistent_cache_keys = [
	"changelog-*",  # version update notifications
	"insert_queue_for_*",  # Deferred Insert
	"recorder-*",  # Recorder
	"global_search_queue",
	"monitor-transactions",
	"rate-limit-counter-*",
	"rl:*",
]
