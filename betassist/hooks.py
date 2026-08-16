# Copyright (c) 2026 RokctAI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
