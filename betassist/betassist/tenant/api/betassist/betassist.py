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

"""BetAssist tenant gateway endpoints.

Dispatched on the tenant site through the single platform gateway
(POST /api/v1/method/rokct.platform.api with cmd = the prefix-free manifest
key, e.g. 'api.betassist.get_matches_feed'). The four original commands
(register_user, get_matches_feed, log_bet, offboard_partner) keep their
shipped signatures and response shapes byte-for-byte; the newer commands
(update_profile, follow_team, unfollow_team, get_affiliate_link) are strictly
additive. Every endpoint reads the inbound x-trace-id (when present) and
writes a structured stderr log line.
"""

import json
import sys
from typing import Optional
from urllib.parse import quote_plus

import frappe

from ... import api_football, follows


@frappe.whitelist(allow_guest=True)
def register_user(
    partner_id: str,
    partner_user_id: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    email: Optional[str] = None,
    age: Optional[int] = None,
    id_number: Optional[str] = None,
) -> dict:
	"""Registers a new user profile under a specific partner (tenant scope).
	Supports full app-side signup variables or anonymous client tokens.
	If partner_user_id is not provided, a unique anonymous hash is generated.
	On repeat calls for the same user, optionally updates supplied profile fields.
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.register_user", "trace_id": trace_id,
	                  "partner_id": partner_id}), file=sys.stderr)
	if not partner_id:
		frappe.throw("Missing partner_id parameter.")

	if not partner_user_id:
		partner_user_id = "usr_" + frappe.generate_hash(length=12)

	unique_user_id = f"{partner_id}_{partner_user_id}"

	profile_name = frappe.db.get_value("User Profile", {"user": unique_user_id})

	if not profile_name:
		profile = frappe.get_doc({
			"doctype": "User Profile",
			"user": unique_user_id,
			"partner_id": partner_id,
			"partner_user_id": partner_user_id,
			"username": username,
			"password": password,
			"email": email,
			"age": int(age) if age else None,
			"id_number": id_number,
			"monthly_budget": 5000.00,
			"remaining_budget": 5000.00,
			"budget_lock": 0
		})
		profile.insert(ignore_permissions=True)
		frappe.db.commit()
	else:
		profile = frappe.get_doc("User Profile", profile_name)
		updated = False
		if username and profile.username != username:
			profile.username = username
			updated = True
		if password and profile.password != password:
			profile.password = password
			updated = True
		if email and profile.email != email:
			profile.email = email
			updated = True
		if age and profile.age != int(age):
			profile.age = int(age)
			updated = True
		if id_number and profile.id_number != id_number:
			profile.id_number = id_number
			updated = True

		if updated:
			profile.save(ignore_permissions=True)
			frappe.db.commit()

	return {
		"status": "success",
		"partner_id": partner_id,
		"partner_user_id": partner_user_id,
		"unique_user_id": unique_user_id
	}


@frappe.whitelist(allow_guest=True)
def get_matches_feed(partner_id: Optional[str] = None, user_id: Optional[str] = None) -> dict:
	"""Retrieves live and upcoming matches with AI analysis confidence scores
	(tenant scope). Optionally accepts a user_id to annotate each match with
	is_following status based on the user's followed teams in the database.
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.get_matches_feed", "trace_id": trace_id,
	                  "partner_id": partner_id}), file=sys.stderr)
	matches = frappe.get_all(
		"Match",
		filters={"status": ["in", ["Scheduled", "In Play"]]},
		fields=["name", "team_a", "team_b", "kickoff_time", "league", "status", "score"]
	)

	followed_teams = []
	if user_id:
		followed_teams = follows.list_followed_teams(user_id)

	results = []
	for m in matches:
		team_a_name, team_a_logo = frappe.db.get_value("Team", m.team_a, ["team_name", "logo_url"]) or (m.team_a, "⚽")
		team_b_name, team_b_logo = frappe.db.get_value("Team", m.team_b, ["team_name", "logo_url"]) or (m.team_b, "⚽")

		analysis = frappe.db.get_value(
			"Match Analysis",
			{"match": m.name},
			["confidence_score", "prediction", "why_win_text", "why_lose_text"],
			as_dict=True
		) or {}

		is_following = (m.team_a in followed_teams or m.team_b in followed_teams)

		results.append({
			"id": m.name,
			"teamA": team_a_name,
			"teamB": team_b_name,
			"teamALogo": team_a_logo,
			"teamBLogo": team_b_logo,
			"kickoff_time": str(m.kickoff_time),
			"league": m.league,
			"status": m.status,
			"score": m.score or "0-0",
			"is_following": is_following,
			"analysis": {
				"confidence_score": float(analysis.get("confidence_score") or 50.0),
				"prediction": analysis.get("prediction") or "Draw",
				"why_win": analysis.get("why_win_text") or "No analysis available.",
				"why_lose": analysis.get("why_lose_text") or "No vulnerabilities reports."
			}
		})

	return {
		"status": "success",
		"matches": results
	}


@frappe.whitelist(allow_guest=True)
def log_bet(
    partner_id: str,
    user_id: str,
    match_id: str,
    bet_amount: float,
    selection: str,
    bookmaker: Optional[str] = None,
) -> dict:
	"""Logs a placed bet for an anonymous user under a specific partner
	(tenant scope). Enforces three discipline rules before recording:
	  1. The bet amount must not exceed 2% of the user's monthly budget.
	  2. The user's budget must not be exhausted or locked.
	  3. The match must not involve the user's favorite (bias-locked) team.
	On success, deducts the amount from remaining_budget and tracks 5% affiliate commission.
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.log_bet", "trace_id": trace_id,
	                  "partner_id": partner_id, "match_id": match_id}), file=sys.stderr)
	if not partner_id or not user_id:
		frappe.throw("Parameters partner_id and user_id are required.")

	profile_name = frappe.db.get_value("User Profile", {"user": user_id, "partner_id": partner_id})
	if not profile_name:
		frappe.throw(f"User Profile not found for {user_id} under partner {partner_id}.")

	profile = frappe.get_doc("User Profile", profile_name)
	amount = float(bet_amount)

	max_allowed_stake = profile.monthly_budget * 0.02
	if amount > max_allowed_stake:
		frappe.throw(f"Disciplined Bet Cap violation: Bet R{amount:.2f} exceeds your 2% maximum limit of R{max_allowed_stake:.2f}.")

	if profile.budget_lock or amount > profile.remaining_budget:
		frappe.throw("Budget Exhausted: Your account's betting budget limit has been reached.")

	match_doc = frappe.get_doc("Match", match_id)
	is_bias_match = (profile.local_favorite_team in [match_doc.team_a, match_doc.team_b] or
	                  profile.intl_favorite_team in [match_doc.team_a, match_doc.team_b])

	if is_bias_match:
		frappe.throw("Personal Bias Block: You are prohibited from betting on matches involving your favorite locked teams.")

	commission = amount * 0.05
	bet_rec = frappe.get_doc({
		"doctype": "Bet Record",
		"user": user_id,
		"partner_id": partner_id,
		"match": match_id,
		"amount": amount,
		"selection": selection,
		"outcome": "Pending",
		"commission_earned": commission,
		"bookmaker": bookmaker or "Partner Bookmaker"
	})
	bet_rec.insert(ignore_permissions=True)

	profile.remaining_budget = profile.remaining_budget - amount
	if profile.remaining_budget <= 0:
		profile.budget_lock = 1
	profile.save(ignore_permissions=True)

	frappe.db.commit()

	return {
		"status": "success",
		"bet_record_id": bet_rec.name,
		"commission_tracked": commission
	}


@frappe.whitelist()
def offboard_partner(partner_id: str) -> dict:
	"""Purges all user profiles and transaction records for a given partner_id
	(tenant scope). Restricted to System Manager administrators only
	(checked against frappe.session.user roles).
	Deletes User Profile, Bet Record, Followed Team, Unfollow Log, and
	Affiliate Outflow rows matching the partner_id. Shared Match and Match
	Analysis data is preserved.
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.offboard_partner", "trace_id": trace_id,
	                  "partner_id": partner_id}), file=sys.stderr)
	if "System Manager" not in frappe.get_roles(frappe.session.user):
		frappe.throw("Unauthorized. System Manager role required.", frappe.PermissionError)

	if not partner_id:
		frappe.throw("Partner ID is required.")

	frappe.db.delete("User Profile", {"partner_id": partner_id})
	frappe.db.delete("Bet Record", {"partner_id": partner_id})
	frappe.db.delete("Followed Team", {"partner_id": partner_id})
	frappe.db.delete("Unfollow Log", {"partner_id": partner_id})
	frappe.db.delete("Affiliate Outflow", {"partner_id": partner_id})

	frappe.db.commit()

	return {
		"status": "success",
		"message": f"Successfully purged all user data for offboarded partner: {partner_id}"
	}


@frappe.whitelist(allow_guest=True)
def update_profile(
    partner_id: str,
    user_id: str,
    local_favorite_team: Optional[str] = None,
    intl_favorite_team: Optional[str] = None,
    monthly_budget: Optional[float] = None,
) -> dict:
	"""Stores the onboarding selections for a user profile (tenant scope):
	permanent favorite-team bias locks and the monthly budget for the 2% rule.
	Favorite teams are write-once — once locked they can never be changed
	(blueprint: 'Locked permanently. Activates favorite team bias rules.').
	Changing the monthly budget adjusts the remaining budget by the same delta
	and re-evaluates the budget lock.
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.update_profile", "trace_id": trace_id,
	                  "partner_id": partner_id}), file=sys.stderr)
	if not partner_id or not user_id:
		frappe.throw("Parameters partner_id and user_id are required.")

	profile_name = frappe.db.get_value("User Profile", {"user": user_id, "partner_id": partner_id})
	if not profile_name:
		frappe.throw(f"User Profile not found for {user_id} under partner {partner_id}.")

	profile = frappe.get_doc("User Profile", profile_name)

	if local_favorite_team:
		if profile.local_favorite_team and profile.local_favorite_team != local_favorite_team:
			frappe.throw("Bias Lock: your local favorite team is locked permanently and cannot be changed.")
		if not frappe.db.exists("Team", local_favorite_team):
			frappe.throw(f"Unknown team: {local_favorite_team}.")
		profile.local_favorite_team = local_favorite_team

	if intl_favorite_team:
		if profile.intl_favorite_team and profile.intl_favorite_team != intl_favorite_team:
			frappe.throw("Bias Lock: your international favorite team is locked permanently and cannot be changed.")
		if not frappe.db.exists("Team", intl_favorite_team):
			frappe.throw(f"Unknown team: {intl_favorite_team}.")
		profile.intl_favorite_team = intl_favorite_team

	if monthly_budget is not None:
		new_budget = float(monthly_budget)
		if new_budget <= 0:
			frappe.throw("Monthly budget must be a positive amount.")
		delta = new_budget - (profile.monthly_budget or 0)
		profile.monthly_budget = new_budget
		profile.remaining_budget = max(0.0, (profile.remaining_budget or 0) + delta)
		profile.budget_lock = 0 if profile.remaining_budget > 0 else 1

	profile.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"status": "success",
		"user_id": user_id,
		"local_favorite_team": profile.local_favorite_team,
		"intl_favorite_team": profile.intl_favorite_team,
		"monthly_budget": profile.monthly_budget,
		"remaining_budget": profile.remaining_budget,
	}


@frappe.whitelist(allow_guest=True)
def follow_team(partner_id: str, user_id: str, team: str) -> dict:
	"""Adds a team to the user's objective follow list (tenant scope). Bets
	are only permitted on followed teams. Favorite (bias-locked) teams cannot
	be followed — the app redirects users to objective matches instead.
	Storage rides the follows adapter (PENDING FAV SDK per Ray 2026-08-23 /
	ADR-003 — see src/tenant/follows.py for the planned api.fav wiring).
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.follow_team", "trace_id": trace_id,
	                  "partner_id": partner_id, "team": team}), file=sys.stderr)
	if not partner_id or not user_id or not team:
		frappe.throw("Parameters partner_id, user_id and team are required.")

	profile_name = frappe.db.get_value("User Profile", {"user": user_id, "partner_id": partner_id})
	if not profile_name:
		frappe.throw(f"User Profile not found for {user_id} under partner {partner_id}.")
	if not frappe.db.exists("Team", team):
		frappe.throw(f"Unknown team: {team}.")

	profile = frappe.get_doc("User Profile", profile_name)
	if team in (profile.local_favorite_team, profile.intl_favorite_team):
		frappe.throw("Bias Block: favorite teams cannot join the objective follow list.")

	created = follows.add_follow(user_id, partner_id, team)
	frappe.db.commit()

	return {"status": "success", "team": team, "already_following": not created}


@frappe.whitelist(allow_guest=True)
def unfollow_team(partner_id: str, user_id: str, team: str) -> dict:
	"""Removes a team from the user's follow list (tenant scope). Unfollowing
	is rate-limited to once per 7 days per user (Unfollow Log; the daily
	reset task clears expired rows) to discourage impulsive churn.
	Storage rides the follows adapter (PENDING FAV SDK per Ray 2026-08-23 /
	ADR-003 — see src/tenant/follows.py for the planned api.fav wiring).
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.unfollow_team", "trace_id": trace_id,
	                  "partner_id": partner_id, "team": team}), file=sys.stderr)
	if not partner_id or not user_id or not team:
		frappe.throw("Parameters partner_id, user_id and team are required.")

	follows.remove_follow(user_id, partner_id, team)
	frappe.db.commit()

	return {"status": "success", "team": team}


@frappe.whitelist(allow_guest=True)
def get_affiliate_link(
    partner_id: str,
    user_id: str,
    match_id: str,
    selection: str,
    stake: Optional[float] = None,
    bookmaker: Optional[str] = None,
) -> dict:
	"""Builds the affiliate outflow deep-link for a betting button (tenant
	scope): a tracking URL for Betway SA or Hollywoodbets SA carrying the
	tenant's affiliate code, pre-filling the user's betslip on the bookmaker's
	platform. Applies the same bias protection as log_bet (no links for
	matches involving the user's locked favorite teams) and records an
	Affiliate Outflow row for commission auditing.
	"""
	trace_id = api_football.new_trace_id()
	print(json.dumps({"event": "api.get_affiliate_link", "trace_id": trace_id,
	                  "partner_id": partner_id, "match_id": match_id}), file=sys.stderr)
	if not partner_id or not user_id:
		frappe.throw("Parameters partner_id and user_id are required.")
	if selection not in ("Team A Win", "Team B Win", "Draw"):
		frappe.throw("Invalid selection. Use 'Team A Win', 'Team B Win' or 'Draw'.")

	profile_name = frappe.db.get_value("User Profile", {"user": user_id, "partner_id": partner_id})
	if not profile_name:
		frappe.throw(f"User Profile not found for {user_id} under partner {partner_id}.")

	profile = frappe.get_doc("User Profile", profile_name)
	match_doc = frappe.get_doc("Match", match_id)

	is_bias_match = (profile.local_favorite_team in [match_doc.team_a, match_doc.team_b] or
	                  profile.intl_favorite_team in [match_doc.team_a, match_doc.team_b])
	if is_bias_match:
		frappe.throw("Personal Bias Block: affiliate links are disabled for matches involving your favorite locked teams.")

	settings = api_football.get_settings()
	chosen = bookmaker or settings.default_bookmaker or "Betway SA"
	if chosen == "Hollywoodbets SA":
		base_url = (settings.hollywoodbets_base_url or "https://www.hollywoodbets.net").rstrip("/")
		affiliate_code = settings.hollywoodbets_affiliate_code or ""
	elif chosen == "Betway SA":
		base_url = (settings.betway_base_url or "https://www.betway.co.za").rstrip("/")
		affiliate_code = settings.betway_affiliate_code or ""
	else:
		frappe.throw(f"Unsupported bookmaker: {chosen}. Use 'Betway SA' or 'Hollywoodbets SA'.")

	stake_value = float(stake) if stake is not None else None
	params = [
		("event", str(match_doc.api_id or match_doc.name)),
		("market", selection),
	]
	if stake_value is not None:
		params.append(("stake", f"{stake_value:.2f}"))
	if affiliate_code:
		params.append(("btag", affiliate_code))
	query = "&".join(f"{k}={quote_plus(v)}" for k, v in params)
	deep_link = f"{base_url}/betslip?{query}"

	outflow = frappe.get_doc({
		"doctype": "Affiliate Outflow",
		"user": user_id,
		"partner_id": partner_id,
		"match": match_id,
		"bookmaker": chosen,
		"selection": selection,
		"stake": stake_value,
		"affiliate_code": affiliate_code,
		"deep_link": deep_link,
		"status": "Generated",
	})
	outflow.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"status": "success",
		"outflow_id": outflow.name,
		"bookmaker": chosen,
		"deep_link": deep_link,
	}
