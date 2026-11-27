# BetAssist app

The BetAssist app shell. It is composed from `base_sdk` and `betassist_sdk` (see
`composer.json`); the sports-betting code lives in the commerce repo's
`betassist/dart`.

<!-- @generated-store-description-start -->
<!-- @generated-store-description-end -->

The previous standalone tree (backend, docs, workflows and SOC2 evidence) is
kept under `commerce/betassist/old/` in the commerce repo.

<!-- @generated-recompose-start -->
## Recomposing this app

`lib/` is fully installer-generated and disposable - it is safe to delete
and is gitignored. Anything app-specific lives in tracked manifests
(`app_routes`, or `host_routes` in `composer.json`), never in `lib/` itself.

To regenerate it:

```sh
python3 .rokct/initiate.py   # provisions the composer under .rokct/skills/
python3 .rokct/skills/.rok/flutter/scripts/compose.py
```

Session cleanup (`python3 .rokct/end_protocol.py`) wipes the provisioned
tools again.
<!-- @generated-recompose-end -->
