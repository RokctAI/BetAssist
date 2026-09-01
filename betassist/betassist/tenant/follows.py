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

"""Follow-list storage adapter — PENDING FAV SDK WIRING (Ray steer 2026-08-23,
ADR-003 "generic favorites table").

Per the owner steer, BetAssist's follow-team feature is supposed to ride the
generic fav SDK (agent repo, fav/frappe: the 'Favorite' doctype plus the
api.fav.add_favorite / remove_favorite / list_favorites gateway commands)
instead of a bespoke table. The fav SDK exists as a composable module, but it
keys every row to frappe.session.user via a Link to the core User doctype,
while BetAssist's tenant users are anonymous partner-scoped identities
(partner_id + partner_user_id) served over allow_guest gateway commands —
those identities are not frappe Users, so a Favorite row cannot be written
for them today without failing Link validation.

Until the fav SDK grows a partner-scoped identity mode (or BetAssist
provisions shadow Users), this adapter isolates ALL follow-list storage in
one place so the swap is a drop-in:

  follow_team(user)      -> api.fav.add_favorite(favorite_type='team',
                             item_id=<Team docname>, title=<team_name>,
                             image_url=<logo_url>)
  unfollow_team(user)    -> api.fav.remove_favorite('team', <Team docname>)
  list_followed_teams()  -> api.fav.list_favorites('team')

Today it writes the tenant Followed Team / Unfollow Log doctypes (the shapes
the shipped get_matches_feed contract already reads). No public endpoint
signatures change when the wiring lands.
"""

import frappe
from frappe.utils import add_days, getdate, today

# Fav-SDK domain tag this adapter will use once wired ('favorite_type').
FAVORITE_TYPE = "team"


def list_followed_teams(user_id):
	"""Returns the Team docnames on the user's follow list (tenant scope)."""
	return [
		f.team for f in frappe.get_all(
			"Followed Team",
			filters={"user": user_id},
			fields=["team"],
		)
	]


def is_following(user_id, team):
	"""True when the user's follow list contains the team (tenant scope)."""
	return bool(frappe.db.get_value("Followed Team", {"user": user_id, "team": team}))


def add_follow(user_id, partner_id, team):
	"""Adds a team to the user's follow list. Idempotent — an existing row is
	left as-is (mirrors fav SDK add_favorite semantics). Returns True when a
	new row was created (tenant scope)."""
	if is_following(user_id, team):
		return False
	frappe.get_doc({
		"doctype": "Followed Team",
		"user": user_id,
		"partner_id": partner_id,
		"team": team,
		"followed_date": today(),
	}).insert(ignore_permissions=True)
	return True


def remove_follow(user_id, partner_id, team):
	"""Removes a team from the user's follow list and logs the unfollow for
	the weekly churn guard. Raises when the user is not following the team or
	already unfollowed something within the past 7 days (tenant scope)."""
	followed_name = frappe.db.get_value("Followed Team", {"user": user_id, "team": team})
	if not followed_name:
		frappe.throw(f"You are not following {team}.")

	seven_days_ago = add_days(getdate(today()), -7)
	recent_unfollow = frappe.db.get_value(
		"Unfollow Log",
		{"user": user_id, "unfollowed_date": [">=", seven_days_ago]},
	)
	if recent_unfollow:
		frappe.throw("Discipline Guard: you can only unfollow one team every 7 days.")

	frappe.delete_doc("Followed Team", followed_name, ignore_permissions=True)
	frappe.get_doc({
		"doctype": "Unfollow Log",
		"user": user_id,
		"partner_id": partner_id,
		"team": team,
		"unfollowed_date": today(),
	}).insert(ignore_permissions=True)
