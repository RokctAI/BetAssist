# API Reference: betassist

Source file: `betassist/frappe/src/tenant/api/betassist/betassist.py`

## Module Description

BetAssist tenant gateway endpoints.

Dispatched on the tenant site through the single platform gateway
(POST /api/v1/method/rokct.platform.api with cmd = the prefix-free manifest
key, e.g. 'api.betassist.get_matches_feed'). The four original commands
(register_user, get_matches_feed, log_bet, offboard_partner) keep their
shipped signatures and response shapes byte-for-byte; the newer commands
(update_profile, follow_team, unfollow_team, get_affiliate_link) are strictly
additive. Every endpoint reads the inbound x-trace-id (when present) and
writes a structured stderr log line.

## Whitelisted API Endpoints

### `def register_user`

```python
def register_user(
  partner_id,
  partner_user_id=None,
  username=None,
  password=None,
  email=None,
  age=None,
  id_number=None
)
```

Registers a new user profile under a specific partner (tenant scope).
Supports full app-side signup variables or anonymous client tokens.
If partner_user_id is not provided, a unique anonymous hash is generated.
On repeat calls for the same user, optionally updates supplied profile fields.

### `def get_matches_feed(partner_id=None, user_id=None)`

Retrieves live and upcoming matches with AI analysis confidence scores
(tenant scope). Optionally accepts a user_id to annotate each match with
is_following status based on the user's followed teams in the database.

### `def log_bet`

```python
def log_bet(
  partner_id,
  user_id,
  match_id,
  bet_amount,
  selection,
  bookmaker=None
)
```

Logs a placed bet for an anonymous user under a specific partner
(tenant scope). Enforces three discipline rules before recording:
  1. The bet amount must not exceed 2% of the user's monthly budget.
  2. The user's budget must not be exhausted or locked.
  3. The match must not involve the user's favorite (bias-locked) team.
On success, deducts the amount from remaining_budget and tracks 5% affiliate
commission.

### `def offboard_partner(partner_id)`

Purges all user profiles and transaction records for a given partner_id
(tenant scope). Restricted to System Manager administrators only
(checked against frappe.session.user roles).
Deletes User Profile, Bet Record, Followed Team, Unfollow Log, and
Affiliate Outflow rows matching the partner_id. Shared Match and Match
Analysis data is preserved.

### `def update_profile`

```python
def update_profile(
  partner_id,
  user_id,
  local_favorite_team=None,
  intl_favorite_team=None,
  monthly_budget=None
)
```

Stores the onboarding selections for a user profile (tenant scope):
permanent favorite-team bias locks and the monthly budget for the 2% rule.
Favorite teams are write-once — once locked they can never be changed
(blueprint: 'Locked permanently. Activates favorite team bias rules.').
Changing the monthly budget adjusts the remaining budget by the same delta
and re-evaluates the budget lock.

### `def follow_team(partner_id, user_id, team)`

Adds a team to the user's objective follow list (tenant scope). Bets
are only permitted on followed teams. Favorite (bias-locked) teams cannot
be followed — the app redirects users to objective matches instead.
Storage rides the follows adapter (PENDING FAV SDK per Ray 2026-08-23 /
ADR-003 — see src/tenant/follows.py for the planned api.fav wiring).

### `def unfollow_team(partner_id, user_id, team)`

Removes a team from the user's follow list (tenant scope). Unfollowing
is rate-limited to once per 7 days per user (Unfollow Log; the daily
reset task clears expired rows) to discourage impulsive churn.
Storage rides the follows adapter (PENDING FAV SDK per Ray 2026-08-23 /
ADR-003 — see src/tenant/follows.py for the planned api.fav wiring).

### `def get_affiliate_link`

```python
def get_affiliate_link(
  partner_id,
  user_id,
  match_id,
  selection,
  stake=None,
  bookmaker=None
)
```

Builds the affiliate outflow deep-link for a betting button (tenant
scope): a tracking URL for Betway SA or Hollywoodbets SA carrying the
tenant's affiliate code, pre-filling the user's betslip on the bookmaker's
platform. Applies the same bias protection as log_bet (no links for
matches involving the user's locked favorite teams) and records an
Affiliate Outflow row for commission auditing.
