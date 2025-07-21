import click

import itds


def execute():
	itds.delete_doc_if_exists("DocType", "Chat Message")
	itds.delete_doc_if_exists("DocType", "Chat Message Attachment")
	itds.delete_doc_if_exists("DocType", "Chat Profile")
	itds.delete_doc_if_exists("DocType", "Chat Token")
	itds.delete_doc_if_exists("DocType", "Chat Room User")
	itds.delete_doc_if_exists("DocType", "Chat Room")
	itds.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from Itds in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/mrinimitable/chat",
		fg="yellow",
	)
