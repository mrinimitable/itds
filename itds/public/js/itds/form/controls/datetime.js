itds.ui.form.ControlDatetime = class ControlDatetime extends itds.ui.form.ControlDate {
	set_formatted_input(value) {
		if (this.timepicker_only) return;
		if (!this.datepicker) return;
		if (!value) {
			this.datepicker.clear();
			return;
		} else if (value.toLowerCase() === "today") {
			value = this.get_now_date();
		} else if (value.toLowerCase() === "now") {
			value = itds.datetime.now_datetime();
		}
		let should_refresh = this.last_value && this.last_value !== value;
		value = this.format_for_input(value);
		this.$input && this.$input.val(value);
		if (should_refresh) {
			this.datepicker.selectDate(itds.datetime.user_to_obj(value));
		}
	}

	get_start_date() {
		this.value = this.value == null || this.value == "" ? undefined : this.value;
		let value = itds.datetime.convert_to_user_tz(this.value);
		return itds.datetime.str_to_obj(value);
	}
	set_date_options() {
		super.set_date_options();
		this.today_text = __("Now");
		let sysdefaults = itds.boot.sysdefaults;
		this.date_format = itds.defaultDatetimeFormat;
		let time_format =
			sysdefaults && sysdefaults.time_format ? sysdefaults.time_format : "HH:mm:ss";
		$.extend(this.datepicker_options, {
			timepicker: true,
			timeFormat: time_format.toLowerCase().replace("mm", "ii"),
		});
	}
	get_now_date() {
		return itds.datetime.now_datetime(true);
	}
	parse(value) {
		if (value) {
			value = this.eval_expression(value, "datetime");

			if (!itds.datetime.is_system_time_zone()) {
				value = itds.datetime.convert_to_system_tz(value, true);
			}

			if (value == "Invalid date") {
				value = "";
			}
		}
		return value;
	}
	format_for_input(value) {
		if (!value) return "";
		return itds.datetime.str_to_user(value, false);
	}
	set_description() {
		const description = this.df.description;
		const time_zone = this.get_user_time_zone();

		if (!this.df.hide_timezone) {
			// Always show the timezone when rendering the Datetime field since the datetime value will
			// always be in system_time_zone rather then local time.

			if (!description) {
				this.df.description = time_zone;
			} else if (!description.includes(time_zone)) {
				this.df.description += "<br>" + time_zone;
			}
		}
		super.set_description();
	}
	get_user_time_zone() {
		return itds.boot.time_zone ? itds.boot.time_zone.user : itds.sys_defaults.time_zone;
	}
	set_datepicker() {
		super.set_datepicker();
		if (this.datepicker.opts.timeFormat.indexOf("s") == -1) {
			// No seconds in time format
			const $tp = this.datepicker.timepicker;
			$tp.$seconds.parent().css("display", "none");
			$tp.$secondsText.css("display", "none");
			$tp.$secondsText.prev().css("display", "none");
		}
	}

	get_model_value() {
		let value = super.get_model_value();
		if (!value && !this.doc) {
			value = this.last_value;
		}
		return !value ? "" : itds.datetime.get_datetime_as_string(value);
	}
};
