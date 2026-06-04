app_name = "betassist"
app_title = "BetAssist"
app_publisher = "Rokct"
app_description = "Betting intelligence and risk management platform"
app_email = "hello@rokct.io"
app_license = "mit"

# Installation Hooks
# ------------------
after_install = "betassist.install.after_install"


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
