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

"""Scheduled tasks for the BetAssist tenant backend.

All tasks run as system background jobs on the tenant site (no session.user
or interactive tenant request context); each run carries its own trace_id and
emits structured stderr logs via api_football.log_event.
"""

import frappe
from frappe.utils import add_days, add_to_date, getdate, now_datetime, today

from . import api_football, insights


# =========================================================================
# Scheduled Task: API-Football Fixture Sync (Runs daily)
# =========================================================================
def sync_fixtures():
	"""Pulls upcoming fixtures for every configured league from API-Football
	into the tenant Match/Team cache doctypes (upsert by api_id).
	Bypass: system background task, no session.user tenant context."""
	trace_id = api_football.new_trace_id()
	settings = api_football.get_settings()
	if not api_football.get_api_key(settings):
		api_football.log_event("sync_fixtures.skipped_no_key", trace_id)
		return

	season = api_football.current_season()
	horizon = int(settings.fixture_horizon_days or 7)
	date_from = getdate(today())
	date_to = add_days(date_from, horizon)

	created = 0
	updated = 0
	for league_label, league_id in api_football.get_league_ids(settings).items():
		fixtures = api_football.fetch_fixtures(
			league_id, season, date_from, date_to, trace_id, settings=settings
		)
		if not fixtures:
			continue
		for fixture in fixtures:
			try:
				was_created = _upsert_fixture(fixture, league_label)
			except Exception as exc:
				api_football.log_event(
					"sync_fixtures.fixture_failed", trace_id, error=str(exc)
				)
				frappe.log_error(f"Fixture upsert failed: {exc}", "BetAssist Sync")
				continue
			if was_created:
				created += 1
			else:
				updated += 1

	frappe.db.commit()
	api_football.log_event("sync_fixtures.done", trace_id, created=created, updated=updated)


def _upsert_fixture(fixture, league_label):
	"""Upserts one API-Football fixture payload into Team + Match rows.
	Returns True when a new Match row was created."""
	fixture_info = fixture.get("fixture") or {}
	api_id = fixture_info.get("id")
	if not api_id:
		return False

	teams = fixture.get("teams") or {}
	team_a = _upsert_team(teams.get("home") or {}, league_label)
	team_b = _upsert_team(teams.get("away") or {}, league_label)
	if not team_a or not team_b:
		return False

	kickoff = (fixture_info.get("date") or "").replace("T", " ")[:19]
	status = api_football.map_fixture_status(
		((fixture_info.get("status") or {}).get("short"))
	)
	score = api_football.extract_score(fixture)

	existing = frappe.db.get_value("Match", {"api_id": api_id})
	if existing:
		frappe.db.set_value("Match", existing, {
			"team_a": team_a,
			"team_b": team_b,
			"kickoff_time": kickoff,
			"status": status,
			"score": score,
		})
		return False

	frappe.get_doc({
		"doctype": "Match",
		"team_a": team_a,
		"team_b": team_b,
		"kickoff_time": kickoff,
		"league": league_label,
		"status": status,
		"score": score,
		"api_id": api_id,
	}).insert(ignore_permissions=True)
	return True


def _upsert_team(team_payload, league_label):
	"""Upserts one Team row from an API-Football team payload; returns the
	Team docname (autoname field:team_name) or None on missing data."""
	api_id = team_payload.get("id")
	team_name = team_payload.get("name")
	if not api_id or not team_name:
		return None

	existing = frappe.db.get_value("Team", {"api_id": api_id})
	if existing:
		if team_payload.get("logo"):
			frappe.db.set_value("Team", existing, "logo_url", team_payload["logo"])
		return existing

	# Team may pre-exist without an api_id (seeded by name) — adopt it.
	by_name = frappe.db.get_value("Team", {"team_name": team_name})
	if by_name:
		frappe.db.set_value("Team", by_name, {
			"api_id": api_id,
			"logo_url": team_payload.get("logo") or "",
		})
		return by_name

	doc = frappe.get_doc({
		"doctype": "Team",
		"team_name": team_name,
		"league": league_label,
		"logo_url": team_payload.get("logo") or "",
		"type": "Local" if league_label == "PSL" else "International",
		"api_id": api_id,
	})
	doc.insert(ignore_permissions=True)
	return doc.name


# =========================================================================
# Scheduled Task: Match Result Sync & Bet Settlement (Runs hourly)
# =========================================================================
def sync_match_results():
	"""Syncs live/final scores for matches past kickoff from API-Football,
	marks finished matches Completed, and settles their pending Bet Records.
	Bypass: system background task, no session.user tenant context."""
	trace_id = api_football.new_trace_id()
	settings = api_football.get_settings()
	if not api_football.get_api_key(settings):
		api_football.log_event("sync_match_results.skipped_no_key", trace_id)
		return

	active_matches = frappe.get_all(
		"Match",
		filters={
			"status": ["in", ["Scheduled", "In Play"]],
			"kickoff_time": ["<=", now_datetime()],
			"api_id": ["is", "set"],
		},
		fields=["name", "api_id"],
	)

	settled = 0
	for m in active_matches:
		fixture = api_football.fetch_fixture_by_id(m.api_id, trace_id, settings=settings)
		if not fixture:
			continue
		status = api_football.map_fixture_status(
			(((fixture.get("fixture") or {}).get("status")) or {}).get("short")
		)
		score = api_football.extract_score(fixture)
		frappe.db.set_value("Match", m.name, {"status": status, "score": score})

		if status == "Completed":
			winner_selection = api_football.extract_winner_selection(fixture)
			settled += settle_bets(m.name, winner_selection)

	frappe.db.commit()
	api_football.log_event(
		"sync_match_results.done", trace_id,
		checked=len(active_matches), bets_settled=settled,
	)


def settle_bets(match_id, winner_selection):
	"""Settles pending Bet Records for a completed match against the winning
	selection ('Team A Win' / 'Team B Win' / 'Draw'). Returns the count."""
	bets = frappe.get_all(
		"Bet Record",
		filters={"match": match_id, "outcome": "Pending"},
		fields=["name", "selection"],
	)
	for b in bets:
		outcome = "Won" if b.selection == winner_selection else "Lost"
		frappe.db.set_value("Bet Record", b.name, "outcome", outcome)
	return len(bets)


# =========================================================================
# Scheduled Task: Trigger Match Analysis (Runs daily)
# =========================================================================
def trigger_match_analysis():
	"""Generates the "Why Win / Why Lose" analysis for scheduled matches whose
	kickoff falls within the configured lead window (blueprint: 48h) and that
	have no Match Analysis yet.
	Bypass: system background task, no session.user tenant context."""
	trace_id = api_football.new_trace_id()
	settings = api_football.get_settings()
	lead_hours = int(settings.analysis_lead_hours or 48)
	lead_time_limit = add_to_date(now_datetime(), hours=lead_hours)

	matches = frappe.get_all(
		"Match",
		filters={"status": "Scheduled", "kickoff_time": ["<=", lead_time_limit]},
		fields=["name", "team_a", "team_b", "league", "kickoff_time"],
	)

	generated = 0
	for match in matches:
		if frappe.db.exists("Match Analysis", {"match": match.name}):
			continue
		try:
			insights.generate_match_analysis(match, trace_id=trace_id, settings=settings)
			generated += 1
		except Exception as exc:
			api_football.log_event(
				"trigger_match_analysis.failed", trace_id,
				match=match.name, error=str(exc),
			)
			frappe.log_error(
				f"Match analysis generation failed for {match.name}: {exc}",
				"BetAssist Insights",
			)

	frappe.db.commit()
	api_football.log_event("trigger_match_analysis.done", trace_id, generated=generated)


# =========================================================================
# Scheduled Task: Monthly Budget Reset (Runs on the 1st of every month)
# =========================================================================
def reset_monthly_budgets():
	"""Resets every User Profile's remaining budget and unlocks accounts at
	the start of the month (2% rule cycle).
	Bypass: system background task, no session.user tenant context."""
	trace_id = api_football.new_trace_id()
	users = frappe.get_all("User Profile", fields=["name", "monthly_budget"])
	for u in users:
		frappe.db.set_value("User Profile", u.name, {
			"remaining_budget": u.monthly_budget,
			"budget_lock": 0,
		})
	frappe.db.commit()
	api_football.log_event("reset_monthly_budgets.done", trace_id, profiles=len(users))


# =========================================================================
# Scheduled Task: Reset Weekly Unfollow Statuses (Runs daily)
# =========================================================================
def reset_weekly_unfollows():
	"""Deletes Unfollow Log rows older than 7 days so users become eligible
	to unfollow teams again (weekly churn guard).
	Bypass: system background task, no session.user tenant context."""
	trace_id = api_football.new_trace_id()
	seven_days_ago = add_days(getdate(today()), -7)
	frappe.db.delete("Unfollow Log", {"unfollowed_date": ["<", seven_days_ago]})
	frappe.db.commit()
	api_football.log_event("reset_weekly_unfollows.done", trace_id)
