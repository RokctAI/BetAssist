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

"""API-Football (api-sports.io) client for the BetAssist tenant backend.

Runs inside scheduled tenant tasks (no interactive session.user); the API key
is read from the BetAssist Settings single doctype (Password field) with a
frappe.conf fallback — per-repo secrets are forbidden, keys live in
settings / site config only. Every outgoing request forwards an x-trace-id
header and emits a structured stderr log line for observability.
"""

import json
import sys
import uuid

import frappe
import requests

DEFAULT_BASE_URL = "https://v3.football.api-sports.io"
REQUEST_TIMEOUT = 30

# Match doctype league label -> API-Football league id. Overridable via the
# BetAssist Settings "sync_league_ids" JSON field; ids are public identifiers,
# not secrets.
DEFAULT_LEAGUE_IDS = {
	"PSL": 288,
	"EPL": 39,
	"La Liga": 140,
	"UCL": 2,
	"Bundesliga": 78,
	"Serie A": 135,
}

# API-Football fixture status -> Match doctype status.
_STATUS_MAP = {
	"TBD": "Scheduled",
	"NS": "Scheduled",
	"1H": "In Play",
	"HT": "In Play",
	"2H": "In Play",
	"ET": "In Play",
	"BT": "In Play",
	"P": "In Play",
	"SUSP": "In Play",
	"INT": "In Play",
	"LIVE": "In Play",
	"FT": "Completed",
	"AET": "Completed",
	"PEN": "Completed",
	"PST": "Postponed",
	"CANC": "Postponed",
	"ABD": "Postponed",
	"AWD": "Completed",
	"WO": "Completed",
}


def new_trace_id():
	"""Generates a trace_id for background/scheduled work, or reuses the
	inbound x-trace-id header when running inside a request context."""
	if getattr(frappe.local, "request", None):
		inbound = frappe.request.headers.get("x-trace-id")
		if inbound:
			return inbound
	return uuid.uuid4().hex


def log_event(event, trace_id, **fields):
	"""Structured stderr logging with trace_id propagation (Layer 12)."""
	payload = {"module": "betassist", "event": event, "trace_id": trace_id}
	payload.update(fields)
	print(json.dumps(payload, default=str), file=sys.stderr)


def get_settings():
	"""Returns the BetAssist Settings single document (tenant site scope)."""
	return frappe.get_single("BetAssist Settings")


def get_api_key(settings=None):
	"""Resolves the API-Football key.

	Priority: BetAssist Settings password field, then the tenant site config
	key 'betassist_api_football_key'. Returns None when unconfigured.
	"""
	try:
		from frappe.utils.password import get_decrypted_password

		key = get_decrypted_password(
			"BetAssist Settings", "BetAssist Settings", "api_football_key",
			raise_exception=False,
		)
		if key:
			return key
	except Exception:
		pass
	return frappe.conf.get("betassist_api_football_key")


def get_league_ids(settings):
	"""Returns the league label -> API-Football id map from settings JSON,
	falling back to DEFAULT_LEAGUE_IDS on empty or invalid JSON."""
	raw = (settings.sync_league_ids or "").strip() if settings else ""
	if raw:
		try:
			parsed = json.loads(raw)
			if isinstance(parsed, dict) and parsed:
				return {str(k): int(v) for k, v in parsed.items()}
		except (ValueError, TypeError):
			pass
	return dict(DEFAULT_LEAGUE_IDS)


def api_get(path, params, trace_id, settings=None):
	"""Performs one authenticated GET against API-Football.

	Forwards the trace_id as an x-trace-id header on the outgoing call and
	logs the request/response pair to stderr. Returns the parsed 'response'
	list, or None when the key is missing or the call fails.
	"""
	settings = settings or get_settings()
	api_key = get_api_key(settings)
	if not api_key:
		log_event("api_football.skipped_no_key", trace_id, path=path)
		return None

	base_url = (settings.api_football_base_url or DEFAULT_BASE_URL).rstrip("/")
	headers = {
		"x-apisports-key": api_key,
		"x-trace-id": trace_id,
	}
	try:
		resp = requests.get(
			f"{base_url}/{path.lstrip('/')}",
			params=params,
			headers=headers,
			timeout=REQUEST_TIMEOUT,
		)
		resp.raise_for_status()
		body = resp.json()
	except Exception as exc:
		log_event("api_football.request_failed", trace_id, path=path, error=str(exc))
		frappe.log_error(f"API-Football request failed ({path}): {exc}", "BetAssist Sync")
		return None

	errors = body.get("errors")
	if errors and (errors if isinstance(errors, list) else list(errors.values())):
		log_event("api_football.api_error", trace_id, path=path, errors=errors)
		return None

	log_event("api_football.ok", trace_id, path=path, results=body.get("results"))
	return body.get("response") or []


def current_season(on_date=None):
	"""API-Football seasons are keyed by their starting year (Aug-May cycles):
	before July the running season started the previous calendar year."""
	from frappe.utils import getdate, today

	d = getdate(on_date or today())
	return d.year if d.month >= 7 else d.year - 1


def map_fixture_status(short_status):
	"""Maps an API-Football fixture.status.short code to a Match status."""
	return _STATUS_MAP.get((short_status or "").upper(), "Scheduled")


def extract_score(fixture):
	"""Builds the 'H-A' score string from a fixture payload's goals block."""
	goals = fixture.get("goals") or {}
	home = goals.get("home")
	away = goals.get("away")
	if home is None or away is None:
		return "0-0"
	return f"{home}-{away}"


def extract_winner_selection(fixture):
	"""Derives the Bet Record selection string for a finished fixture:
	'Team A Win' (home), 'Team B Win' (away) or 'Draw'."""
	teams = fixture.get("teams") or {}
	if (teams.get("home") or {}).get("winner"):
		return "Team A Win"
	if (teams.get("away") or {}).get("winner"):
		return "Team B Win"
	return "Draw"


def fetch_fixtures(league_id, season, date_from, date_to, trace_id, settings=None):
	"""Fetches scheduled fixtures for one league in an inclusive date window."""
	return api_get(
		"fixtures",
		{
			"league": league_id,
			"season": season,
			"from": str(date_from),
			"to": str(date_to),
			"timezone": "UTC",
		},
		trace_id,
		settings=settings,
	)


def fetch_fixture_by_id(fixture_api_id, trace_id, settings=None):
	"""Fetches a single fixture (live score / final result) by API id."""
	response = api_get("fixtures", {"id": fixture_api_id}, trace_id, settings=settings)
	if response:
		return response[0]
	return None


def fetch_team_form(team_api_id, trace_id, settings=None, last=5):
	"""Summarizes a team's last N finished fixtures into form metrics used by
	the insight engine: W/D/L string, goals scored and conceded."""
	response = api_get(
		"fixtures",
		{"team": team_api_id, "last": last, "status": "FT-AET-PEN"},
		trace_id,
		settings=settings,
	)
	if response is None:
		return None

	results = []
	scored = 0
	conceded = 0
	for fixture in response:
		teams = fixture.get("teams") or {}
		goals = fixture.get("goals") or {}
		home = teams.get("home") or {}
		away = teams.get("away") or {}
		is_home = home.get("id") == team_api_id
		own_goals = goals.get("home") if is_home else goals.get("away")
		opp_goals = goals.get("away") if is_home else goals.get("home")
		scored += own_goals or 0
		conceded += opp_goals or 0
		side = home if is_home else away
		if side.get("winner") is True:
			results.append("W")
		elif side.get("winner") is False:
			results.append("L")
		else:
			results.append("D")

	return {
		"last_five": "-".join(results) if results else "N/A",
		"goals_scored": scored,
		"goals_conceded": conceded,
	}


def fetch_h2h_data(team_a_api_id, team_b_api_id, trace_id, settings=None, last=10):
	"""Aggregates the head-to-head record between two teams (last N meetings)."""
	response = api_get(
		"fixtures/headtohead",
		{"h2h": f"{team_a_api_id}-{team_b_api_id}", "last": last},
		trace_id,
		settings=settings,
	)
	if response is None:
		return None

	team_a_wins = 0
	team_b_wins = 0
	draws = 0
	played = 0
	for fixture in response:
		status = ((fixture.get("fixture") or {}).get("status") or {}).get("short")
		if map_fixture_status(status) != "Completed":
			continue
		played += 1
		teams = fixture.get("teams") or {}
		home = teams.get("home") or {}
		away = teams.get("away") or {}
		winner_id = None
		if home.get("winner") is True:
			winner_id = home.get("id")
		elif away.get("winner") is True:
			winner_id = away.get("id")
		if winner_id == team_a_api_id:
			team_a_wins += 1
		elif winner_id == team_b_api_id:
			team_b_wins += 1
		else:
			draws += 1

	return {
		"matches_played": played,
		"team_a_wins": team_a_wins,
		"team_b_wins": team_b_wins,
		"draws": draws,
	}
