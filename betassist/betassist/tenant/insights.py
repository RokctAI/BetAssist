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

"""BetAssist "Why Win / Why Lose" insight engine (tenant backend).

Pipeline per the blueprint: assemble real pre-match context from API-Football
(team form + head-to-head), then author the plain-English analysis. The LLM
call site is a clean provider hook configured entirely from BetAssist
Settings / site config — no AI vendor endpoint, key, or model identifier is
hardcoded here. When no provider is configured (or the call fails after a
retry), a deterministic statistical fallback writer produces the analysis
from the same context, so tenants get usable insight cards either way.
"""

import json
import sys

import frappe
import requests
from frappe.utils import now_datetime

from . import api_football

PROVIDER_TIMEOUT = 60
DEFAULT_MAX_TOKENS = 1024

# Role-separated prompt template for the provider hook. The user prompt is
# rendered from the assembled context; the model must answer with strict JSON.
SYSTEM_PROMPT = (
	"You are a disciplined football betting analyst writing for casual fans. "
	"Given pre-match statistics, respond ONLY with a JSON object of the shape "
	'{"confidence_score": <0-100 number>, "prediction": "Team A Win"|"Team B Win"|"Draw", '
	'"why_win": "<plain-English reasons the predicted side wins>", '
	'"why_lose": "<plain-English risks that could flip the result>"}. '
	"Keep why_win and why_lose to two sentences each, plain English, no jargon."
)

USER_PROMPT_TEMPLATE = (
	"League: {league}\n"
	"Team A (home): {team_a}\n"
	"Team B (away): {team_b}\n"
	"Team A form (last 5): {team_a_form}\n"
	"Team B form (last 5): {team_b_form}\n"
	"Head-to-head: {h2h}\n"
	"Kickoff: {kickoff_time}\n"
	"Produce the JSON analysis now."
)


def assemble_match_context(match, trace_id, settings=None):
	"""Assembles the AI prompt context for one Match row from the tenant cache
	plus live API-Football form and head-to-head statistics."""
	settings = settings or api_football.get_settings()
	team_a = frappe.get_doc("Team", match.team_a)
	team_b = frappe.get_doc("Team", match.team_b)

	team_a_form = None
	team_b_form = None
	h2h = None
	if team_a.api_id and team_b.api_id:
		team_a_form = api_football.fetch_team_form(team_a.api_id, trace_id, settings=settings)
		team_b_form = api_football.fetch_team_form(team_b.api_id, trace_id, settings=settings)
		h2h = api_football.fetch_h2h_data(team_a.api_id, team_b.api_id, trace_id, settings=settings)

	return {
		"league": match.league,
		"team_a": team_a.team_name,
		"team_b": team_b.team_name,
		"kickoff_time": str(match.kickoff_time),
		"team_a_form": team_a_form or {"last_five": "N/A", "goals_scored": 0, "goals_conceded": 0},
		"team_b_form": team_b_form or {"last_five": "N/A", "goals_scored": 0, "goals_conceded": 0},
		"h2h": h2h or {"matches_played": 0, "team_a_wins": 0, "team_b_wins": 0, "draws": 0},
		"has_live_stats": bool(team_a_form and team_b_form),
	}


def generate_match_analysis(match, trace_id=None, settings=None):
	"""Generates and stores the Match Analysis row for one Match: assembles
	the context, asks the configured insight provider, falls back to the
	deterministic statistical writer, and inserts the record (tenant scope,
	scheduled task — no session.user)."""
	trace_id = trace_id or api_football.new_trace_id()
	settings = settings or api_football.get_settings()

	context = assemble_match_context(match, trace_id, settings=settings)
	analysis = call_insight_provider(context, trace_id, settings=settings)
	if not analysis:
		analysis = heuristic_insight(context)

	analysis_doc = frappe.get_doc({
		"doctype": "Match Analysis",
		"match": match.name,
		"confidence_score": analysis.get("confidence_score", 50),
		"prediction": analysis.get("prediction", "Draw"),
		"why_win_text": analysis.get("why_win", ""),
		"why_lose_text": analysis.get("why_lose", ""),
		"generated_at": now_datetime(),
	})
	analysis_doc.insert(ignore_permissions=True)
	api_football.log_event(
		"insights.analysis_generated", trace_id,
		match=match.name, prediction=analysis.get("prediction"),
		source=analysis.get("source", "provider"),
	)
	return analysis_doc


def call_insight_provider(context, trace_id, settings=None):
	"""LLM CALL SITE (provider hook).

	Posts the role-separated prompt to the chat-completions-compatible
	endpoint configured in BetAssist Settings (insight_provider_url +
	insight_provider_key + insight_model), with a max_tokens budget and one
	retry as failover. Returns the parsed analysis dict, or None when the
	provider is unconfigured or fails — the caller then uses the
	deterministic fallback. Nothing vendor-specific is hardcoded: endpoint,
	bearer key, and model identifier all come from settings / site config.
	"""
	settings = settings or api_football.get_settings()
	provider_url = (settings.insight_provider_url or "").strip()
	model = (settings.insight_model or "").strip()
	if not provider_url or not model:
		return None

	api_key = None
	try:
		from frappe.utils.password import get_decrypted_password

		api_key = get_decrypted_password(
			"BetAssist Settings", "BetAssist Settings", "insight_provider_key",
			raise_exception=False,
		)
	except Exception:
		pass
	api_key = api_key or frappe.conf.get("betassist_insight_provider_key")

	headers = {
		"Content-Type": "application/json",
		"x-trace-id": trace_id,
	}
	if api_key:
		headers["Authorization"] = f"Bearer {api_key}"

	payload = {
		"model": model,
		"max_tokens": int(settings.insight_max_tokens or DEFAULT_MAX_TOKENS),
		"messages": [
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": USER_PROMPT_TEMPLATE.format(
				league=context["league"],
				team_a=context["team_a"],
				team_b=context["team_b"],
				team_a_form=json.dumps(context["team_a_form"]),
				team_b_form=json.dumps(context["team_b_form"]),
				h2h=json.dumps(context["h2h"]),
				kickoff_time=context["kickoff_time"],
			)},
		],
		"stream": False,
	}

	for attempt in range(2):  # one retry on transient failure
		try:
			resp = requests.post(
				provider_url, json=payload, headers=headers, timeout=PROVIDER_TIMEOUT
			)
			resp.raise_for_status()
			body = resp.json()
			choices = body.get("choices") or []
			content = (choices[0].get("message") or {}).get("content", "") if choices else ""
			parsed = _parse_analysis_json(content)
			if parsed:
				parsed["source"] = "provider"
				return parsed
			api_football.log_event(
				"insights.provider_bad_payload", trace_id, attempt=attempt
			)
		except Exception as exc:
			api_football.log_event(
				"insights.provider_failed", trace_id, attempt=attempt, error=str(exc)
			)
			print(
				json.dumps({"event": "insights.provider_retry", "trace_id": trace_id}),
				file=sys.stderr,
			)
	return None


def _parse_analysis_json(content):
	"""Parses the provider's JSON reply, tolerating surrounding prose or code
	fences; validates the required keys and clamps the confidence score."""
	if not content:
		return None
	text = content.strip()
	start = text.find("{")
	end = text.rfind("}")
	if start == -1 or end == -1 or end <= start:
		return None
	try:
		data = json.loads(text[start:end + 1])
	except ValueError:
		return None
	if not isinstance(data, dict):
		return None
	if not all(k in data for k in ("confidence_score", "prediction", "why_win", "why_lose")):
		return None
	try:
		score = float(data["confidence_score"])
	except (TypeError, ValueError):
		return None
	data["confidence_score"] = max(0.0, min(100.0, score))
	if data["prediction"] not in ("Team A Win", "Team B Win", "Draw"):
		return None
	return data


def heuristic_insight(context):
	"""Deterministic statistical fallback writer.

	Scores each side from real form (wins weighted over draws, goal
	difference) plus the head-to-head record, picks the prediction, and
	renders template-based plain-English why-win / why-lose text. Used when
	no insight provider is configured or the provider call fails.
	"""
	team_a = context["team_a"]
	team_b = context["team_b"]
	form_a = context["team_a_form"]
	form_b = context["team_b_form"]
	h2h = context["h2h"]

	score_a = _form_points(form_a) + (form_a["goals_scored"] - form_a["goals_conceded"]) * 0.5
	score_b = _form_points(form_b) + (form_b["goals_scored"] - form_b["goals_conceded"]) * 0.5
	score_a += h2h["team_a_wins"] * 1.0
	score_b += h2h["team_b_wins"] * 1.0
	score_a += 1.0  # modest home advantage for Team A (home side)

	gap = score_a - score_b
	if abs(gap) < 1.5:
		prediction = "Draw"
		winner, loser = team_a, team_b
		confidence = 50.0 + min(abs(gap) * 2, 5.0)
	else:
		if gap > 0:
			prediction = "Team A Win"
			winner, loser = team_a, team_b
			winner_form, loser_form = form_a, form_b
		else:
			prediction = "Team B Win"
			winner, loser = team_b, team_a
			winner_form, loser_form = form_b, form_a
		confidence = min(85.0, 55.0 + abs(gap) * 3.0)

	if prediction == "Draw":
		why_win = (
			f"{team_a} and {team_b} are evenly matched on recent form "
			f"({form_a['last_five']} vs {form_b['last_five']}), and their last "
			f"{h2h['matches_played']} meetings produced {h2h['draws']} draws."
		)
		why_lose = (
			f"A single moment of quality could still separate them: {team_a} has scored "
			f"{form_a['goals_scored']} and {team_b} {form_b['goals_scored']} goals over "
			f"their last five games, so a narrow win either way is the main risk."
		)
	else:
		why_win = (
			f"{winner} arrives in better shape ({winner_form['last_five']} in their last five, "
			f"{winner_form['goals_scored']} scored vs {winner_form['goals_conceded']} conceded) "
			f"and holds the edge in recent head-to-heads "
			f"({h2h['team_a_wins']}-{h2h['draws']}-{h2h['team_b_wins']} across "
			f"{h2h['matches_played']} meetings)."
		)
		why_lose = (
			f"{loser} has still found the net {loser_form['goals_scored']} times in their last "
			f"five matches, so if {winner} starts loosely or chases the game, "
			f"{loser} has the firepower to punish them on the counter."
		)

	if not context.get("has_live_stats"):
		confidence = 50.0

	return {
		"confidence_score": round(confidence, 1),
		"prediction": prediction,
		"why_win": why_win,
		"why_lose": why_lose,
		"source": "heuristic",
	}


def _form_points(form):
	"""Converts a W-D-L form string into weighted points (W=3, D=1)."""
	last_five = form.get("last_five") or ""
	return last_five.count("W") * 3 + last_five.count("D") * 1
