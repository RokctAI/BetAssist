app_name = "betassist"
app_title = "BetAssist"
app_publisher = "Rokct"
app_description = "Betting intelligence and risk management platform"
app_email = "hello@rokct.io"
app_license = "mit"

# Installation Hooks
# ------------------
# NOTE: This standalone app currently ships no Python modules beyond hooks.py.
# The previous after_install, scheduler_events, and website_route_rules entries
# pointed at modules (betassist.install, betassist.betassist.tasks,
# betassist.betassist.api) that do not exist in this repository — installing the
# app registered scheduler jobs and routes that crashed on import. The working
# implementations live in the composed betassist module inside rokctai/commerce.
# Re-add these hooks only together with the corresponding modules.

# DocType Configurations
# ---------------------
# Document events or overrides can go here
