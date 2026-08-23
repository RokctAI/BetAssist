> **SUPERSEDED (2026-08-23).** This specification predates the fleet single-gateway rule and no longer describes the shipped surface. The mobile client half ships as the `betassist_sdk` Dart SDK (commerce repo, `betassist/dart`) — not as native `.aar`/`.xcframework` binaries — and the backend is not reachable via the direct REST routes below. All backend commands are dispatched through the single platform gateway (`POST /api/v1/method/rokct.platform.api` with `cmd` set to the prefix-free manifest key, e.g. `api.betassist.get_matches_feed`), as declared in this repo's `betassist/frappe/manifest.json`. This file is retained for historical context only — do not implement against it.

# BetAssist Mobile SDK & REST API Specifications

This document outlines the public interface for the compiled BetAssist Mobile SDK (`.aar` and `.xcframework`) and the backend REST API endpoints hosted on the Rokct PAAS stack.

---

## Part 1: Mobile SDK Native Bridge API Spec

When client developers import the compiled binary into Android Studio or Xcode, they interact with the SDK through these native bridges.

### 1. Android Integration (Java / Kotlin)

To launch the AR scanner screen from a native Android Activity:

#### Method Signature (Kotlin):
```kotlin
object BetAssistSDK {
    /**
     * Launches the AR Scanner activity.
     * @param context The hosting Android Context/Activity.
     * @param matchJson A JSON-serialized string matching the SoccerMatch schema.
     * @param isFavorite Set to true if the match involves the user's bias/favorite team.
     * @param isFollowing Set to true if the user actively follows either team.
     * @param recommendedStake The calculated 2% risk stake in ZAR.
     * @param showBetting Set to false to disable all betting limits, budget warnings, and bet placement buttons (useful for generic sports tracking apps).
     * @param callback Handles the checkout callback when the user clicks 'PLACE BET'.
     */
    fun launchScanner(
        context: Context,
        matchJson: String,
        isFavorite: Boolean,
        isFollowing: Boolean,
        recommendedStake: Double,
        showBetting: Boolean = true,
        callback: BetPlaceCallback
    )
}

interface BetPlaceCallback {
    fun onPlaceBet(matchId: String, amount: Double)
}
```

#### Integration Example (Kotlin):
```kotlin
BetAssistSDK.launchScanner(
    context = this,
    matchJson = "{\"id\":\"m1\", \"teamA\":\"Orlando Pirates\", ...}",
    isFavorite = true,
    isFollowing = true,
    recommendedStake = 100.0,
    showBetting = false, // Disables betting UI widgets, showing only match stats
    callback = object : BetPlaceCallback {
        override fun onPlaceBet(matchId: String, amount: Double) {
            // Native app intercepts callback and opens native checkout/betslip
            myBetslipController.openWithSelection(matchId, amount)
        }
    }
)
```

---

### 2. iOS Integration (Swift)

To launch the AR scanner view controller from Xcode.

#### Method Signature (Swift):
```swift
public class BetAssistSDK: NSObject {
    /**
     * Instantiates and returns the AR Scanner View Controller.
     */
    public static func makeScannerViewController(
        matchJson: String,
        isFavorite: Bool,
        isFollowing: Bool,
        recommendedStake: Double,
        showBetting: Bool = true,
        onPlaceBet: @escaping (_ matchId: String, _ amount: Double) -> Void
    ) -> UIViewController
}
```

#### Integration Example (Swift):
```swift
let scannerVC = BetAssistSDK.makeScannerViewController(
    matchJson: "{\"id\":\"m1\", ...}",
    isFavorite: false,
    isFollowing: true,
    recommendedStake: 100.0,
    showBetting: false, // Disables betting buttons/restrictions
    onPlaceBet: { (matchId, amount) in
        // Intercept bet event and launch native iOS betslip sheet
        self.presentBetslip(matchId: matchId, amount: amount)
    }
)
self.present(scannerVC, animated: true, completion: nil)
```

---

## Part 2: Backend REST API Spec (Frappe Tenant Method)

For the client app to populate the SDK inputs, their app backend must query their dedicated tenant site hosted on your Rokct PAAS platform.

### 1. Get Live Matches Telemetry Feed
Retrieves upcoming and live matches with AI confidence metrics and plain English analysis text.

*   **Endpoint:** `GET https://[tenant-name].paas.rokct.io/api/v1/matches`
*   **Headers:**
    *   `Authorization: Token [API_KEY]:[API_SECRET]`
    *   `Content-Type: application/json`

#### Response JSON Schema (`200 OK`):
```json
{
  "message": {
    "status": "success",
    "matches": [
      {
        "id": "m1",
        "teamA": "Orlando Pirates",
        "teamB": "Kaizer Chiefs",
        "teamALogo": "🏴‍☠️",
        "teamBLogo": "✌️",
        "kickoff_time": "2026-06-07 15:00:00",
        "league": "PSL",
        "status": "Scheduled",
        "score": "0-0",
        "analysis": {
          "confidence_score": 78.0,
          "prediction": "Team A Win",
          "why_win": "Orlando Pirates has a 4-match winning streak at home, while Kaizer Chiefs faces suspensions for their two key central defenders.",
          "why_lose": "Kaizer Chiefs excels at quick counter-attacks. If Pirates overcommit their fullbacks early, they risk conceding on transition."
        }
      }
    ]
  }
}
```

---

### 2. Log Placed Bet & Track Affiliate Commission
When a bet is successfully processed, the client app notifies your PAAS instance to log the transaction, audit risk behaviors, and update commission metrics.

*   **Endpoint:** `POST https://[tenant-name].paas.rokct.io/api/v1/bets`
*   **Headers:**
    *   `Authorization: Token [API_KEY]:[API_SECRET]`
    *   `Content-Type: application/json`

#### Request Payload JSON:
```json
{
  "match_id": "m1",
  "bet_amount": 100.0,
  "selection": "Team A Win",
  "bookmaker": "Betway SA"
}
```

#### Response JSON Schema (`200 OK`):
```json
{
  "message": {
    "status": "success",
    "bet_record_id": "bet_b8f9a2c1d3",
    "commission_tracked": 5.0
  }
}
```

---

## Part 3: Versioning Strategy

### 1. REST API Versioning
To maintain backward compatibility and keep the API structure clean, all public endpoints are mapped through route rewrites on the Frappe PAAS stack, keeping internal file layouts hidden:

*   **Version 1 Endpoints:**
    *   `GET /api/v1/matches` -> (Internal: `betassist.api.v1.get_matches_feed`)
    *   `POST /api/v1/bets` -> (Internal: `betassist.api.v1.log_bet`)
*   **Version 2 Endpoints (If introduced):**
    *   `GET /api/v2/matches` -> (Internal: `betassist.api.v2.get_matches_feed`)
    *   `POST /api/v2/bets` -> (Internal: `betassist.api.v2.log_bet`)

### 2. Client SDK Versioning
The compiled mobile SDK packages (`.aar` and `.xcframework`) utilize **Semantic Versioning (SemVer)**:
`MAJOR.MINOR.PATCH` (e.g., `1.2.0`)

*   **MAJOR version (e.g., `2.0.0`):** Changes that break backward compatibility in the native method signatures (e.g., removing parameters or renaming classes).
*   **MINOR version (e.g., `1.3.0`):** Adding backward-compatible features, such as adding optional flags like `showBetting`.
*   **PATCH version (e.g., `1.2.1`):** Backward-compatible bug fixes (e.g., fixing gyroscope sensor drift or layout issues).

*   *Android (Gradle):* `implementation 'com.rokct.betassist:sdk:1.2.+'`
*   *iOS (Cocoapods):* `pod 'BetAssistSDK', '~> 1.2.0'`
