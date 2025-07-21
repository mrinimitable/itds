import itds


def execute():
	itds.reload_doctype("Translation")
	itds.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
