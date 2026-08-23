# API Reference: tasks

Source file: `betassist/frappe/src/tenant/tasks.py`

## Module Description

Scheduled tasks for the BetAssist tenant backend.

All tasks run as system background jobs on the tenant site (no session.user
or interactive tenant request context); each run carries its own trace_id and
emits structured stderr logs via api_football.log_event.

## Documented Module Functions

### `def sync_fixtures()`

Pulls upcoming fixtures for every configured league from API-Football
into the tenant Match/Team cache doctypes (upsert by api_id).
Bypass: system background task, no session.user tenant context.

### `def sync_match_results()`

Syncs live/final scores for matches past kickoff from API-Football,
marks finished matches Completed, and settles their pending Bet Records.
Bypass: system background task, no session.user tenant context.

### `def trigger_match_analysis()`

Generates the "Why Win / Why Lose" analysis for scheduled matches whose
kickoff falls within the configured lead window (blueprint: 48h) and that
have no Match Analysis yet.
Bypass: system background task, no session.user tenant context.

### `def reset_monthly_budgets()`

Resets every User Profile's remaining budget and unlocks accounts at
the start of the month (2% rule cycle).
Bypass: system background task, no session.user tenant context.

### `def reset_weekly_unfollows()`

Deletes Unfollow Log rows older than 7 days so users become eligible
to unfollow teams again (weekly churn guard).
Bypass: system background task, no session.user tenant context.
