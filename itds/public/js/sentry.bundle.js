import * as Sentry from "@sentry/browser";

Sentry.init({
	dsn: itds.boot.sentry_dsn,
	release: itds?.boot?.versions?.itds,
	autoSessionTracking: false,
	initialScope: {
		// don't use itds.session.user, it's set much later and will fail because of async loading
		user: { id: itds.boot.sitename },
		tags: { itds_user: itds.boot.user.name ?? "Unidentified" },
	},
	beforeSend(event, hint) {
		// Check if it was caused by itds.throw()
		if (
			hint.originalException instanceof Error &&
			hint.originalException.stack &&
			hint.originalException.stack.includes("itds.throw")
		) {
			return null;
		}
		return event;
	},
});
