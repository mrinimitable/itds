// Copyright (c) 2024, Itds Technologies and contributors
// For license information, please see license.txt

itds.ui.form.on("Role Replication", {
	refresh(frm) {
		frm.disable_save();
		frm.page.set_primary_action(__("Replicate"), ($btn) => {
			$btn.text(__("Replicating..."));
			itds.run_serially([
				() => itds.dom.freeze("Replicating..."),
				() => frm.call("replicate_role"),
				() => itds.dom.unfreeze(),
				() => itds.msgprint(__("Replication completed.")),
				() => $btn.text(__("Replicate")),
			]);
		});
	},
});
