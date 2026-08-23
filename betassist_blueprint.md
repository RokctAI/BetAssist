# BetAssist — Combined Product Blueprint & System Architecture

This document serves as the master blueprint for **BetAssist**, a betting intelligence and risk management platform under the Rokct ecosystem. It integrates the standard mobile dashboard with the interactive AR TV-tracking scanner.

---

## 1. Product positioning & The "Responsible Gambling" B2B Pitch
BetAssist acts as a "financial trading terminal" for sports, transitioning casual fans into analytical, disciplined experts.

### The Pitch to Betting Operators (e.g., Betway, Hollywoodbets):
*   **Compliance & CSR Shield:** Regulators demand strict "Responsible Gambling" practices. Operators can sponsor or license BetAssist to prove they actively protect users with the 2% monthly budget cap and favorite-team bias block tools.
*   **Customer Lifetime Value (LTV):** Instead of users losing their bankroll on day one and churning, BetAssist guides them to place disciplined, analytical bets. This creates sustainable, long-term active bettors.
*   **Conversion Optimization:** The live TV AR scanner breaks down complex rules, stats, and odds into plain English, giving casual fans the confidence to place their first bet.
*   **Redirection, Not Restriction:** When the app blocks a user from betting on their favorite team due to bias, it redirects them to high-confidence objective matches happening the same day.

---

## 2. Combined App Modes & User Experience Flow

```
+-------------------------------------------------------------------+
|                           BETASSIST APP                           |
+-------------------------------------------------------------------+
                                  |
         +------------------------+------------------------+
         |                                                 |
         v                                                 v
  [2D Dashboard Mode]                             [AR Camera Mode]
 (Default / Off-Match)                         (Pointed at live TV)
  - Profile & Budget (2% Rule)                  - Automatic content scan
  - Bias lock setup (Permanent)                 - 3D floating Match Card
  - Upcoming match cards (Followed)             - Plain English live stats
  - Snaps from AR on tilt down                  - Snap-down to 2D on tilt
```

### Onboarding Flow (One-time, Sequential)
1.  **Local Favorite Team (PSL):** Locked permanently. Activates favorite team bias rules.
2.  **International Favorite Team (Europe):** Locked permanently. Activates international bias rules.
3.  **Follow List:** User selects objective teams they understand. Bets are *only* permitted on followed teams to prevent blind gambling.
4.  **Risk Profile (Monthly Budget):** Enforces the **2% Rule** (e.g., R5,000 monthly budget limits individual bets to R100 max). 

### Mode A: 2D Dashboard (Daily Utility)
*   Visual design mimics a high-end investment portfolio (deep obsidian dark themes, neon green tracking accents, clean HSL palettes).
*   Displays matches involving **followed teams** and **league leaders** of followed leagues.
*   Shows current remaining monthly budget with progress indicators (alerts trigger at 50%, 80%, and 100% usage).

### Mode B: Live TV AR Scanner (Active Broadcast)
*   **Activation:** The user taps the camera icon on the dashboard.
*   **Detection:** The app scans the TV screen. Using light OCR or logo recognition (e.g., PSL scoreboard/team crests or sponsor logos like Betway), it identifies the match.
*   **3D Overlay:** A floating 3D Match Card is projected directly next to the TV on the user's screen showing:
    *   Match Time & Live Score
    *   Real-time Odds
    *   AI Confidence Score (e.g., 82% Home Win)
*   **3D Flip Interaction:** Tapping the card performs a physical 3D flip animation in place, showing plain-English reasoning (Why Team A wins / Why Team B loses).
*   **Snapping Fallback:** Since holding the phone up is tiring, tilting the phone downward (detected via gyroscope) automatically closes the camera and transitions the card seamlessly into a standard 2D betting placement screen on the dashboard.

---

## 3. The Bias Protection Rules (In Action)

The app prevents emotional betting on favorite teams by hiding the action buttons:

| Scenario | App Prediction | UI Behavior & Rules |
| :--- | :--- | :--- |
| **Favorite Team Match** | Win | Displays bias reminder warning. **Betting buttons hidden.** User is advised to skip or redirect to objective matches. |
| **Favorite Team Match** | Lose | Strong bias warning. **Betting buttons blocked completely.** User cannot bet against the analysis on their favorite team. |
| **Objective Followed Team** | Any | Shows standard analysis. Enables betting buttons with recommended stake based on 2% risk limit and confidence level. |

---

## 4. Technical Architecture

### A. Mobile Client (Flutter 3.38.5)
*   **State Management:** Riverpod for modular, testable reactive states (handling budget counters and bias checks).
*   **AR & Sensor Layer:**
    *   `sensors_plus` package to read gyroscope pitch and handle the 2D snap-down transition.
    *   `flip_card` or custom vector transforms for the 3D flipping animation.
    *   Lightweight localized OCR for scoreboard reading.
*   **Communication:** WebSockets connection to the Frappe backend for streaming odds adjustments and live match milestones.

### B. Backend (Frappe Framework) — IMPLEMENTED (2026-08, `betassist/frappe` module in this repo)
*   **Match Analysis Engine:** A scheduled job (`trigger_match_analysis`, daily) fetches pre-match data (48 hours prior, configurable) from **API-Football (api-sports.io)** — team form and head-to-head via `api_football.py` — assembles it into a role-separated context prompt, and calls the insight provider hook (`insights.py`) to generate the plain English "Why Win / Why Lose" analysis and confidence baseline. The LLM endpoint, key, and model are configured in the **BetAssist Settings** doctype / site config (nothing vendor-specific is hardcoded); when no provider is configured a deterministic statistical fallback writes the analysis from the same real stats.
*   **Data Sync:** `sync_fixtures` (daily) upserts upcoming fixtures for the configured leagues into the Match/Team cache doctypes; `sync_match_results` (hourly) syncs live/final scores and settles pending Bet Records.
*   **Affiliate Outflow:** The `api.betassist.get_affiliate_link` gateway command constructs tracking deep-links containing affiliate codes for Betway SA and Hollywoodbets SA (codes/base URLs in BetAssist Settings), pre-filling the user's betslip on their web platform, and records each outflow in the **Affiliate Outflow** doctype for commission auditing. Bias-locked matches never get links.

---

## 5. Next Steps & Phase 1 Scope — STATUS
1.  ~~Initialize custom Frappe App (`betassist`) inside the Monorepo.~~ **Done** — this repo is the app shell; the composable SDK module lives at `betassist/frappe/` (see `composer.json`).
2.  ~~Build out the database schemas (User Profile, Match, Match Analysis, Bet Record, Team).~~ **Done** — plus Followed Team, Unfollow Log, Affiliate Outflow, and the BetAssist Settings single doctype (API keys live in settings/site config, never in the repo).
3.  ~~Implement the API-Football synchronization service.~~ **Done** — `src/tenant/api_football.py` + the `sync_fixtures`/`sync_match_results` scheduled tasks.
4.  ~~Build the AI prompt template that structures the plain-English analysis response.~~ **Done** — `src/tenant/insights.py` (provider hook + deterministic fallback).

Remaining follow-ups: retire the superseded mock module at `commerce/betassist/frappe` (separate commerce PR); wire the Dart client's data layer to the gateway commands listed in `betassist/frappe/manifest.json`; and re-point the follow-team storage adapter (`src/tenant/follows.py`) at the generic fav SDK (`agent/fav/frappe`, ADR-003) once the fav SDK supports BetAssist's anonymous partner-scoped identities (per Ray, 2026-08-23).
