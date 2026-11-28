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
| Commit | `41c01ed2b31eaa463962d31545b8409058894c19` |
| Workflow / job | `Build (Smart) / build-windows` |
| Stage | `dependencies` |
| API cmd | _unknown_ |
| Screenshot artifact | _unknown_ |
| Runner | `Windows, X64, win25-vs2026, 20261123.321.1` |
| Run | https://github.com/RokctAI/BetAssist/actions/runs/46174699828 |

### Composed SDKs

| SDK | Installed version | Source | Ref |
|---|---|---|---|
| `betassist_sdk` | `1.5.0` | `https://github.com/RokctAI/commerce` | `main` |
| `fav_sdk` | `1.1.3` | `https://github.com/RokctAI/agent` | `main` |
| `base_sdk` | `1.116.1` | `https://github.com/RokctAI/core` | `main` |
| `auth_sdk` | `1.25.0` | `https://github.com/RokctAI/Users` | `main` |
| `users_sdk` | `1.5.4` | `https://github.com/RokctAI/Users` | `main` |
| `onboarding_sdk` | `1.4.1` | `https://github.com/RokctAI/Users` | `main` |
| `wallet_sdk` | `1.9.5` | `https://github.com/RokctAI/pay` | `main` |
| `comms_sdk` | `1.23.7` | `https://github.com/RokctAI/core` | `main` |
| `telemetry_sdk` | `1.1.2` | `https://github.com/RokctAI/core` | `main` |
| `processing_sdk` | `1.0.2` | `https://github.com/RokctAI/productivity` | `main` |
| `corporate_sdk` | `1.2.1` | `https://github.com/RokctAI/corporate` | `main` |
| `hardware_sdk` | `1.1.4` | `https://github.com/RokctAI/hardware` | `main` |
| `desktop_sdk` | `1.2.3` | `https://github.com/RokctAI/hardware` | `main` |
| `hms_sdk` | `1.1.1` | `https://github.com/RokctAI/hardware` | `main` |

### Error summary

`Could not find package `build_runner` or file `build_runner``

<details><summary>Log tail</summary>

````
Resolving dependencies...
Downloading packages...
  _flutterfire_internals 1.3.59 (1.4.0 available)
  auto_route 9.3.0+1 (11.2.0 available)
  battery_plus 4.1.0 (7.1.2 available)
  battery_plus_platform_interface 1.2.2 (2.0.1 available)
  cached_network_image 3.4.1 (4.0.7 available)
  cached_network_image_platform_interface 4.1.1 (5.0.4 available)
  cached_network_image_web 1.3.1 (2.0.5 available)
  calendar_date_picker2 1.1.9 (4.0.0 available)
  camera 0.11.4 (0.12.2 available)
  camera_android_camerax 0.6.30 (0.7.6+2 available)
  camera_avfoundation 0.9.23+2 (0.11.1 available)
  clock 1.1.2 (1.1.3 available)
  cloud_firestore 5.6.12 (7.2.0 available)
  cloud_firestore_platform_interface 6.6.12 (8.2.0 available)
  cloud_firestore_web 4.4.12 (5.9.0 available)
  code_assets 1.2.1 (2.2.0 available)
  connectivity_plus 6.1.5 (7.3.2 available)
  cross_file 0.3.5+5 (0.4.0 available)
  cupertino_icons 1.0.9 (2.0.0 available)
  dbus 0.7.15 (0.8.1 available)
  facebook_auth_desktop 2.1.1 (2.3.1 available)
  file_picker 8.3.7 (13.4.1 available)
  file_selector_macos 0.9.5+1 (0.9.5+2 available)
  firebase_auth 5.7.0 (7.1.0 available)
  firebase_auth_platform_interface 7.7.3 (9.2.0 available)
  firebase_auth_web 5.15.3 (6.4.0 available)
  firebase_core 3.15.2 (5.2.0 available)
  firebase_core_platform_interface 6.0.3 (8.2.0 available)
  firebase_core_web 2.24.1 (4.2.0 available)
  firebase_messaging 15.2.10 (17.1.0 available)
  firebase_messaging_platform_interface 4.6.10 (4.12.0 available)
  firebase_messaging_web 3.10.10 (4.4.0 available)
  firebase_remote_config 5.5.0 (7.1.0 available)
  firebase_remote_config_platform_interface 2.0.0 (3.1.0 available)
  firebase_remote_config_web 1.8.9 (1.11.0 available)
  flutter_advanced_switch 3.1.0 (3.2.2 available)
  flutter_app_group_directory 1.1.0 (2.0.0 available)
  flutter_cache_manager 3.4.1 (3.5.0 available)
  flutter_facebook_auth 7.1.5 (7.3.3 available)
  flutter_local_notifications 19.5.0 (23.0.4 available)
  flutter_local_notifications_linux 6.0.0 (9.0.0 available)
  flutter_local_notifications_platform_interface 9.1.0 (13.0.0 available)
  flutter_local_notifications_windows 1.0.3 (4.0.1 available)
  flutter_pos_printer_platform_image_3_sdt 1.2.12 (1.2.32 available)
  flutter_riverpod 2.6.1 (3.5.0 available)
  flutter_secure_storage 9.2.4 (11.2.0 available)
  flutter_secure_storage_linux 1.2.3 (3.0.3 available)
  flutter_secure_storage_macos 3.1.3 (4.0.0 available)
  flutter_secure_storage_platform_interface 1.1.2 (2.1.1 available)
  flutter_secure_storage_web 1.2.1 (2.1.1 available)
  flutter_secure_storage_windows 3.1.2 (4.2.2 available)
  geolocator 13.0.4 (14.1.2 available)
  geolocator_android 4.6.2 (5.2.1 available)
  get_it 8.3.0 (9.3.0 available)
  google_fonts 6.3.3 (9.0.0 available)
  google_maps_flutter 2.18.1 (2.19.0 available)
  google_sign_in 6.3.0 (7.2.0 available)
  google_sign_in_android 6.2.1 (7.2.19 available)
  google_sign_in_ios 5.9.0 (6.4.0 available)
  google_sign_in_platform_interface 2.5.0 (3.1.0 available)
  google_sign_in_web 0.12.4+4 (1.1.3 available)
  hooks 2.0.2 (2.2.0 available)
  image_cropper 8.1.0 (14.0.0 available)
  image_cropper_for_web 6.1.0 (8.0.1 available)
  image_cropper_platform_interface 7.2.0 (9.0.0 available)
  image_picker_ios 0.8.13+10 (0.8.13+16 available)
  intl 0.19.0 (0.20.3 available)
  jiffy 6.3.2 (6.4.5 available)
  js 0.6.7 (0.7.2 available)
  live_activities 2.4.3 (2.6.1 available)
  lottie 3.7.0 (3.8.2 available)
  matcher 0.12.19 (0.12.20 available)
  material_color_utilities 0.13.0 (0.13.1 available)
  meta 1.18.0 (1.19.0 available)
  mobile_scanner 6.0.11 (7.5.0 available)
  network_info_plus 6.1.4 (8.2.2 available)
  network_info_plus_platform_interface 2.0.2 (3.1.0 available)
  nm 0.5.0 (0.6.0 available)
  objective_c 9.5.0 (9.6.4 available)
  package_info_plus 8.3.1 (10.2.2 available)
  package_info_plus_platform_interface 3.2.1 (4.1.0 available)
! permission_handler 12.0.3 (overridden) (13.0.2 available)
  permission_handler_android 13.0.1 (14.1.1 available)
  petitparser 7.0.2 (7.1.0 available)
  record_use 0.6.0 (1.1.1 available)
  remixicon 1.4.1 (4.9.3 available)
  riverpod 2.6.1 (3.5.0 available)
  rxdart 0.27.7 (0.28.0 available)
  sensors_plus 5.0.1 (7.1.1 available)
  sensors_plus_platform_interface 1.2.0 (2.0.2 available)
  share_plus 10.1.4 (13.3.1 available)
  share_plus_platform_interface 5.0.2 (7.2.0 available)
  shared_preferences_foundation 2.5.7 (2.6.2 available)
  shimmer 2.0.0 (4.0.0 available)
  sign_in_with_apple 6.1.4 (8.2.0 available)
  sign_in_with_apple_platform_interface 1.1.0 (2.0.0 available)
  sign_in_with_apple_web 2.1.1 (3.0.0 available)
  sms_autofill 2.5.0 (2.6.1 available)
! sqlite3 2.9.4 (overridden) (3.9.2 available)
  sqlite3_flutter_libs 0.5.42 (0.6.0+eol available)
  stack_trace 1.12.1 (1.12.2 available)
  test_api 0.7.11 (0.7.15 available)
  timezone 0.10.1 (0.11.2 available)
  top_snackbar_flutter 3.4.0 (3.5.0 available)
  upower 0.7.0 (0.8.0 available)
  vector_math 2.2.0 (2.4.4 available)
  web 1.1.1 (1.1.2 available)
  webview_flutter_wkwebview 3.26.2 (3.27.2 available)
  win32 5.15.0 (6.4.0 available)
  xml 6.6.1 (7.1.0 available)
Got dependencies!
110 packages have newer versions incompatible with dependency constraints.
Try `flutter pub outdated` for more information.
Could not find package `build_runner` or file `build_runner`
````

</details>
