import itds


def _(msg: str, lang: str | None = None, context: str | None = None) -> str:
	"""Return translated string in current lang, if exists.
	Usage:
	        _('Change')
	        _('Change', context='Coins')
	"""
	from itds.translate import get_all_translations
	from itds.utils import is_html, strip_html_tags

	if not hasattr(itds.local, "lang"):
		itds.local.lang = lang or "en"

	if not lang:
		lang = itds.local.lang

	non_translated_string = msg

	if is_html(msg):
		msg = strip_html_tags(msg)

	# msg should always be unicode
	msg = itds.as_unicode(msg).strip()

	translated_string = ""

	all_translations = get_all_translations(lang)
	if context:
		string_key = f"{msg}:{context}"
		translated_string = all_translations.get(string_key)

	if not translated_string:
		translated_string = all_translations.get(msg)

	return translated_string or non_translated_string


def _lt(msg: str, lang: str | None = None, context: str | None = None):
	"""Lazily translate a string.


	This function returns a "lazy string" which when casted to string via some operation applies
	translation first before casting.

	This is only useful for translating strings in global scope or anything that potentially runs
	before `itds.init()`

	Note: Result is not guaranteed to equivalent to pure strings for all operations.
	"""
	from itds.types.lazytranslatedstring import _LazyTranslate

	return _LazyTranslate(msg, lang, context)


def set_user_lang(user: str, user_language: str | None = None) -> None:
	"""Guess and set user language for the session. `itds.local.lang`"""
	from itds.translate import get_user_lang

	itds.local.lang = get_user_lang(user) or user_language
