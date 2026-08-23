# API Reference: follows

Source file: `betassist/frappe/src/tenant/follows.py`

## Module Description

Follow-list storage adapter — PENDING FAV SDK WIRING (Ray steer 2026-08-23,
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

## Documented Module Functions

### `def list_followed_teams(user_id)`

Returns the Team docnames on the user's follow list (tenant scope).

### `def is_following(user_id, team)`

True when the user's follow list contains the team (tenant scope).

### `def add_follow(user_id, partner_id, team)`

Adds a team to the user's follow list. Idempotent — an existing row is
left as-is (mirrors fav SDK add_favorite semantics). Returns True when a
new row was created (tenant scope).

### `def remove_follow(user_id, partner_id, team)`

Removes a team from the user's follow list and logs the unfollow for
the weekly churn guard. Raises when the user is not following the team or
already unfollowed something within the past 7 days (tenant scope).
