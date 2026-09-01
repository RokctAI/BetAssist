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

app_name = "betassist"
app_title = "BetAssist"
app_publisher = "Rokct"
app_description = "Betting intelligence and risk management platform"
app_email = "hello@rokct.io"
app_license = "mit"

# Installation Hooks
# ------------------
# NOTE: This shell file intentionally declares identity keys only. The backend
# implementation lives in the composable SDK module at betassist/frappe/ in
# this repo (see composer.json): the frappe composer copies the module into the
# target app shell and appends its scheduler_events and whitelisted method
# aliases from betassist/frappe/manifest.json to the composed hooks.py.
# Do not hand-register scheduler jobs or routes here — they would point at
# modules that only exist post-compose.

# DocType Configurations
# ---------------------
# Document events or overrides can go here


# --- BEG OF DYNAMIC SDK HOOKS ---

# --- Module: betassist (tenant) ---
scheduler_events = globals().get('scheduler_events', {})
scheduler_events.setdefault('hourly', [])
for _t in ['betassist.betassist.tenant.tasks.sync_match_results']:
    if _t not in scheduler_events['hourly']: scheduler_events['hourly'].append(_t)
scheduler_events = globals().get('scheduler_events', {})
scheduler_events.setdefault('daily', [])
for _t in ['betassist.betassist.tenant.tasks.sync_fixtures', 'betassist.betassist.tenant.tasks.trigger_match_analysis', 'betassist.betassist.tenant.tasks.reset_weekly_unfollows']:
    if _t not in scheduler_events['daily']: scheduler_events['daily'].append(_t)
scheduler_events = globals().get('scheduler_events', {})
scheduler_events.setdefault('monthly', [])
for _t in ['betassist.betassist.tenant.tasks.reset_monthly_budgets']:
    if _t not in scheduler_events['monthly']: scheduler_events['monthly'].append(_t)
whitelisted_methods = globals().get('whitelisted_methods', {})
override_whitelisted_methods = globals().get('override_whitelisted_methods', {})
whitelisted_methods['betassist.api.betassist.register_user'] = 'betassist.betassist.tenant.api.betassist.register_user'
override_whitelisted_methods['betassist.api.betassist.register_user'] = 'betassist.betassist.tenant.api.betassist.register_user'
whitelisted_methods['betassist.api.betassist.get_matches_feed'] = 'betassist.betassist.tenant.api.betassist.get_matches_feed'
override_whitelisted_methods['betassist.api.betassist.get_matches_feed'] = 'betassist.betassist.tenant.api.betassist.get_matches_feed'
whitelisted_methods['betassist.api.betassist.log_bet'] = 'betassist.betassist.tenant.api.betassist.log_bet'
override_whitelisted_methods['betassist.api.betassist.log_bet'] = 'betassist.betassist.tenant.api.betassist.log_bet'
whitelisted_methods['betassist.api.betassist.offboard_partner'] = 'betassist.betassist.tenant.api.betassist.offboard_partner'
override_whitelisted_methods['betassist.api.betassist.offboard_partner'] = 'betassist.betassist.tenant.api.betassist.offboard_partner'
whitelisted_methods['betassist.api.betassist.update_profile'] = 'betassist.betassist.tenant.api.betassist.update_profile'
override_whitelisted_methods['betassist.api.betassist.update_profile'] = 'betassist.betassist.tenant.api.betassist.update_profile'
whitelisted_methods['betassist.api.betassist.follow_team'] = 'betassist.betassist.tenant.api.betassist.follow_team'
override_whitelisted_methods['betassist.api.betassist.follow_team'] = 'betassist.betassist.tenant.api.betassist.follow_team'
whitelisted_methods['betassist.api.betassist.unfollow_team'] = 'betassist.betassist.tenant.api.betassist.unfollow_team'
override_whitelisted_methods['betassist.api.betassist.unfollow_team'] = 'betassist.betassist.tenant.api.betassist.unfollow_team'
whitelisted_methods['betassist.api.betassist.get_affiliate_link'] = 'betassist.betassist.tenant.api.betassist.get_affiliate_link'
override_whitelisted_methods['betassist.api.betassist.get_affiliate_link'] = 'betassist.betassist.tenant.api.betassist.get_affiliate_link'
# --- END OF DYNAMIC SDK HOOKS ---
