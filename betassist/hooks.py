app_name = "betassist"
app_title = "BetAssist"
app_publisher = "Rokct"
app_description = "Betting intelligence and risk management platform"
app_email = "hello@rokct.io"
app_license = "mit"

# Installation Hooks
# ------------------
# No shell-owned install hook: betassist/install.py does not exist (in this
# shell or in the composed commerce module), so a hardcoded
# after_install = "betassist.install.after_install" made every
# `bench install-app betassist` fail with an ImportError before the app
# could finish installing. Modules that need install steps declare
# after_install in their manifest.json; the backend composer merges those
# in additively.


# DocType Configurations
# ---------------------
# Document events or overrides can go here

# Scheduled Tasks
# ---------------
scheduler_events = {
	"hourly": [
		"betassist.betassist.tasks.trigger_match_analysis"
	],
	"daily": [
		"betassist.betassist.tasks.check_match_results",
		"betassist.betassist.tasks.reset_weekly_unfollows"
	],
	"cron": {
		"0 0 1 * *": [
			"betassist.betassist.tasks.reset_monthly_budgets"
		]
	}
}

# API Route Overrides
# -------------------
website_route_rules = [
	{"from_route": "/api/v1/matches", "to_route": "betassist.betassist.api.get_matches_feed"},
	{"from_route": "/api/v1/bets", "to_route": "betassist.betassist.api.log_bet"},
	{"from_route": "/api/v1/user/register", "to_route": "betassist.betassist.api.register_user"},
	{"from_route": "/api/v1/user/offboard", "to_route": "betassist.betassist.api.offboard_partner"}
]
