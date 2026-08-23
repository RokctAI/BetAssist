# API Reference: api_football

Source file: `betassist/frappe/src/tenant/api_football.py`

## Module Description

API-Football (api-sports.io) client for the BetAssist tenant backend.

Runs inside scheduled tenant tasks (no interactive session.user); the API key
is read from the BetAssist Settings single doctype (Password field) with a
frappe.conf fallback — per-repo secrets are forbidden, keys live in
settings / site config only. Every outgoing request forwards an x-trace-id
header and emits a structured stderr log line for observability.

## Documented Module Functions

### `def new_trace_id()`

Generates a trace_id for background/scheduled work, or reuses the
inbound x-trace-id header when running inside a request context.

### `def log_event(event, trace_id, **fields)`

Structured stderr logging with trace_id propagation (Layer 12).

### `def get_settings()`

Returns the BetAssist Settings single document (tenant site scope).

### `def get_api_key(settings=None)`

Resolves the API-Football key.

Priority: BetAssist Settings password field, then the tenant site config
key 'betassist_api_football_key'. Returns None when unconfigured.

### `def get_league_ids(settings)`

Returns the league label -> API-Football id map from settings JSON,
falling back to DEFAULT_LEAGUE_IDS on empty or invalid JSON.

### `def current_season(on_date=None)`

API-Football seasons are keyed by their starting year (Aug-May cycles):
before July the running season started the previous calendar year.

### `def map_fixture_status(short_status)`

Maps an API-Football fixture.status.short code to a Match status.

### `def extract_score(fixture)`

Builds the 'H-A' score string from a fixture payload's goals block.

### `def extract_winner_selection(fixture)`

Derives the Bet Record selection string for a finished fixture:
'Team A Win' (home), 'Team B Win' (away) or 'Draw'.

### `def fetch_fixtures`

```python
def fetch_fixtures(
  league_id,
  season,
  date_from,
  date_to,
  trace_id,
  settings=None
)
```

Fetches scheduled fixtures for one league in an inclusive date window.

### `def fetch_fixture_by_id(fixture_api_id, trace_id, settings=None)`

Fetches a single fixture (live score / final result) by API id.

### `def fetch_team_form(team_api_id, trace_id, settings=None, last=5)`

Summarizes a team's last N finished fixtures into form metrics used by
the insight engine: W/D/L string, goals scored and conceded.

### `def fetch_h2h_data`

```python
def fetch_h2h_data(
  team_a_api_id,
  team_b_api_id,
  trace_id,
  settings=None,
  last=10
)
```

Aggregates the head-to-head record between two teams (last N meetings).
