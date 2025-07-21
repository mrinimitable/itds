import itds
from itds.website.page_renderers.template_page import TemplatePage


class ListPage(TemplatePage):
	def can_render(self):
		return itds.db.exists("DocType", self.path, True)

	def render(self):
		itds.local.form_dict.doctype = self.path
		self.set_standard_path("list")
		return super().render()
