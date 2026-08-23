# API Reference: insights

Source file: `betassist/frappe/src/tenant/insights.py`

## Module Description

BetAssist "Why Win / Why Lose" insight engine (tenant backend).

Pipeline per the blueprint: assemble real pre-match context from API-Football
(team form + head-to-head), then author the plain-English analysis. The LLM
call site is a clean provider hook configured entirely from BetAssist
Settings / site config — no AI vendor endpoint, key, or model identifier is
hardcoded here. When no provider is configured (or the call fails after a
retry), a deterministic statistical fallback writer produces the analysis
from the same context, so tenants get usable insight cards either way.

## Documented Module Functions

### `def generate_match_analysis(match, trace_id=None, settings=None)`

Generates and stores the Match Analysis row for one Match: assembles
the context, asks the configured insight provider, falls back to the
deterministic statistical writer, and inserts the record (tenant scope,
scheduled task — no session.user).
