# 🪟 Windows Build Errors

The following syntax errors were found during the build process:

Could not parse specific file errors from the log. Please review the raw logs.

## Failure record

| Field | Value |
|---|---|
| Failure class | `build` |
| SDK | _unknown_ |
| SDK version | _unknown_ |
| Consumer | `RokctAI/BetAssist` |
| Commit | `04a2527e062dd0e0f30c2f7f55278c88fd399e01` |
| Workflow / job | `Build (Smart) / build-windows` |
| Stage | `dependencies` |
| API cmd | _unknown_ |
| Screenshot artifact | _unknown_ |
| Runner | `Windows, X64, win25-vs2026, 20261123.321.1` |
| Run | https://github.com/RokctAI/BetAssist/actions/runs/46170885650 |

### Composed SDKs

| SDK | Installed version | Source | Ref |
|---|---|---|---|
| `betassist_sdk` | `1.5.0` | `https://github.com/RokctAI/commerce` | `main` |
| `fav_sdk` | `1.1.3` | `https://github.com/RokctAI/agent` | `main` |
| `base_sdk` | `1.116.1` | `https://github.com/RokctAI/core` | `main` |
| `auth_sdk` | `1.25.0` | `https://github.com/RokctAI/Users` | `main` |
| `users_sdk` | `1.5.4` | `https://github.com/RokctAI/Users` | `main` |
| `wallet_sdk` | `1.9.5` | `https://github.com/RokctAI/pay` | `main` |
| `comms_sdk` | `1.23.7` | `https://github.com/RokctAI/core` | `main` |
| `telemetry_sdk` | `1.1.2` | `https://github.com/RokctAI/core` | `main` |
| `processing_sdk` | `1.0.2` | `https://github.com/RokctAI/productivity` | `main` |
| `corporate_sdk` | `1.2.1` | `https://github.com/RokctAI/corporate` | `main` |
| `desktop_sdk` | `1.2.3` | `https://github.com/RokctAI/hardware` | `main` |
| `hms_sdk` | `1.1.1` | `https://github.com/RokctAI/hardware` | `main` |

### Error summary

`So, because betassist depends on betassist_sdk from path, version solving failed.`

<details><summary>Log tail</summary>

````
Resolving dependencies...
Because every version of betassist_sdk from path depends on onboarding_sdk from path which doesn't exist (could not find package onboarding_sdk at ".rokct\cache\onboarding"), betassist_sdk from path is forbidden.
So, because betassist depends on betassist_sdk from path, version solving failed.
Failed to update packages.
````

</details>
