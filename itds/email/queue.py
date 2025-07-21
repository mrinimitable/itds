# Copyright (c) 2022, Itds Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
from datetime import timedelta

import itds
from itds import _, msgprint
from itds.utils import cint, cstr, get_url, now_datetime
from itds.utils.data import getdate
from itds.utils.verified_command import get_signed_params, verify_request

# After this percent of failures in every batch, entire batch is aborted.
# This usually indicates a systemic failure so we shouldn't keep trying to send emails.
EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_PERCENT = 0.33
EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_COUNT = 10


def get_emails_sent_this_month(email_account=None):
	"""Get count of emails sent from a specific email account.

	:param email_account: name of the email account used to send mail

	if email_account=None, email account filter is not applied while counting
	"""
	today = getdate()
	month_start = today.replace(day=1)

	filters = {
		"status": "Sent",
		"creation": [">=", str(month_start)],
	}
	if email_account:
		filters["email_account"] = email_account

	return itds.db.count("Email Queue", filters=filters)


def get_emails_sent_today(email_account=None):
	"""Get count of emails sent from a specific email account.

	:param email_account: name of the email account used to send mail

	if email_account=None, email account filter is not applied while counting
	"""
	q = """
		SELECT
			COUNT(`name`)
		FROM
			`tabEmail Queue`
		WHERE
			`status` in ('Sent', 'Not Sent', 'Sending')
			AND
			`creation` > (NOW() - INTERVAL '24' HOUR)
	"""

	q_args = {}
	if email_account is not None:
		if email_account:
			q += " AND email_account = %(email_account)s"
			q_args["email_account"] = email_account
		else:
			q += " AND (email_account is null OR email_account='')"

	return itds.db.sql(q, q_args)[0][0]


def get_unsubscribe_message(unsubscribe_message: str, expose_recipients: str) -> "itds._dict[str, str]":
	unsubscribe_message = unsubscribe_message or _("Unsubscribe")
	unsubscribe_link = f'<a href="<!--unsubscribe_url-->" target="_blank">{unsubscribe_message}</a>'
	unsubscribe_html = _("{0} to stop receiving emails of this type").format(unsubscribe_link)
	html = f"""<div class="email-unsubscribe">
			<!--cc_message-->
			<div>
				{unsubscribe_html}
			</div>
		</div>"""

	text = f"\n\n{unsubscribe_message}: <!--unsubscribe_url-->\n"
	if expose_recipients == "footer":
		text = f"\n<!--cc_message-->{text}"

	return itds._dict(html=html, text=text)


def get_unsubcribed_url(reference_doctype, reference_name, email, unsubscribe_method, unsubscribe_params):
	params = {
		"email": cstr(email),
		"doctype": cstr(reference_doctype),
		"name": cstr(reference_name),
	}
	if unsubscribe_params:
		params.update(itds.parse_json(unsubscribe_params))

	return get_url(unsubscribe_method + "?" + get_signed_params(params))


@itds.whitelist(allow_guest=True)
def unsubscribe(doctype, name, email):
	# unsubsribe from comments and communications
	if not itds.in_test and not verify_request():
		return

	try:
		itds.get_doc(
			{
				"doctype": "Email Unsubscribe",
				"email": email,
				"reference_doctype": doctype,
				"reference_name": name,
			}
		).insert(ignore_permissions=True)

	except itds.DuplicateEntryError:
		itds.db.rollback()

	else:
		itds.db.commit()

	return_unsubscribed_page(email, doctype, name)


def return_unsubscribed_page(email, doctype, name):
	itds.respond_as_web_page(
		_("Unsubscribed"),
		_("{0} has left the conversation in {1} {2}").format(email, _(doctype), name),
		indicator_color="green",
	)


def flush():
	"""flush email queue, every time: called from scheduler.

	This should not be called outside of background jobs.
	"""
	from itds.email.doctype.email_queue.email_queue import EmailQueue

	# To avoid running jobs inside unit tests
	if itds.are_emails_muted():
		msgprint(_("Emails are muted"))

	if cint(itds.db.get_default("suspend_email_queue")) == 1:
		return

	email_queue_batch = get_queue()
	if not email_queue_batch:
		return

	failed_email_queues = []
	for row in email_queue_batch:
		try:
			email_queue: EmailQueue = itds.get_doc("Email Queue", row.name)
			email_queue.send()
		except Exception:
			itds.get_doc("Email Queue", row.name).log_error()
			failed_email_queues.append(row.name)

			if (
				len(failed_email_queues) / len(email_queue_batch)
				> EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_PERCENT
				and len(failed_email_queues) > EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_COUNT
			):
				itds.throw(_("Email Queue flushing aborted due to too many failures."))


def get_queue():
	batch_size = cint(itds.conf.email_queue_batch_size) or 500

	return itds.db.sql(
		f"""select
			name, sender
		from
			`tabEmail Queue`
		where
			(status='Not Sent' or status='Partially Sent') and
			(send_after is null or send_after < %(now)s)
		order
			by priority desc, retry asc, creation asc
		limit {batch_size}""",
		{"now": now_datetime()},
		as_dict=True,
	)


def retry_sending_emails():
	emails_in_sending = itds.get_all(
		"Email Queue", filters={"status": "Sending"}, fields=["name", "modified"]
	)
	for e in emails_in_sending:
		if now_datetime() - e["modified"] > timedelta(minutes=15):
			update_fields = {}
			email_queue = itds.get_doc("Email Queue", e["name"])
			sent_to_atleast_one_recipient = any(
				rec.recipient for rec in email_queue.recipients if rec.is_mail_sent()
			)
			if email_queue.retry < cint(itds.db.get_system_setting("email_retry_limit")) or 3:
				update_fields.update(
					{
						"status": "Partially Sent" if sent_to_atleast_one_recipient else "Not Sent",
						"retry": email_queue.retry + 1,
					}
				)
			else:
				update_fields.update({"status": "Error"})
				update_fields.update({"error": "Retry Limit Exceeded"})
			email_queue.update_status(**update_fields, commit=True)
