itds.ui.form.ControlHTMLEditor = class ControlHTMLEditor extends (
	itds.ui.form.ControlMarkdownEditor
) {
	static editor_class = "html";
	set_language() {
		this.df.options = "HTML";
		super.set_language();
	}
	update_preview() {
		if (!this.markdown_preview) return;
		let value = this.get_value() || "";
		value = itds.dom.remove_script_and_style(value);
		this.markdown_preview.html(value);
	}
};
