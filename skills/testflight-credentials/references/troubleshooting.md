# TestFlight upload failures

Read this when the credentials exist but a run fails. Ordered by the stage the
failure appears in.

## Setup stage — `asc.py` itself

| Symptom | Cause | Fix |
|---|---|---|
| `HTTP 401` on every call | key ID, issuer ID and `.p8` are not from the same team key | re-copy all three from the same row of the Integrations page |
| `HTTP 403` on `create-bundle-id` / `create-cert` | key has Developer role | reissue the key with **App Manager**; role cannot be edited after creation |
| `does not look like a .p8 private key` | the downloaded file was renamed or is the certificate, not the key | the `.p8` is downloadable once; if lost, revoke the key and issue a new one |
| `ECDSA signature ... not a DER SEQUENCE` | `.p8` is corrupt (often line endings mangled by copy-paste) | re-download, or write it with `printf '%s\n'` rather than an editor |

## Build-number lookup stage

| Symptom | Cause | Fix |
|---|---|---|
| `App Store Connect에 <bundle id> 앱이 없다` | app record missing, or the key cannot see it | complete SKILL.md step 3; confirm with `asc.py find-app` |
| Build number collides / upload rejected as duplicate | two workflow runs raced | the workflow's `concurrency` group must serialize runs; re-run the failed one |

## Signing / archive stage

| Symptom | Cause | Fix |
|---|---|---|
| `MAC verification failed during PKCS12 import` | `.p12` built with OpenSSL 3 defaults | rebuild with `repackage-p12` (it passes `-legacy`) and re-run `verify-p12` — no new certificate needed |
| `No signing certificate "Apple Development" found` | archive is using automatic signing without a distribution cert in the keychain | confirm `DIST_CERT_P12_BASE64` decodes and imports; run `verify-p12` locally on the same file |
| Base64 decode error importing the cert | secret value was line-wrapped | re-set it with `openssl base64 -A -in dist.p12` |
| Provisioning profile missing for an app extension | `-allowProvisioningUpdates` absent, or the API key lacks App Manager | extensions do not need manual registration; fix the flag or the key role |
| Certificate limit reached | team already has 3 Apple Distribution certificates | if the private key from an existing one is on hand, `asc.py repackage-p12` needs no new certificate; otherwise `list-certs` and let the **user** decide what to revoke |

## Upload stage — `altool` / `xcrun notarytool`

| Symptom | Cause | Fix |
|---|---|---|
| `90186` / `90062` — version already used | that marketing version's pre-release train is closed by an approved App Store version | raise `MARKETING_VERSION`; a CI step that queries approved versions can pick this automatically |
| `ITSAppUsesNonExemptEncryption` missing | key absent from Info.plist | add `ITSAppUsesNonExemptEncryption: false` for apps using only HTTPS; otherwise answer the ASC prompt per build |
| `Invalid Bundle. Missing Info.plist value CFBundleIconName` | asset catalog has no `AppIcon` set, or the icon set is empty | add a 1024pt icon and set `ASSETCATALOG_COMPILER_APPICON_NAME` |
| Upload succeeds but nothing appears in TestFlight | still processing | ASC takes 5–15 minutes; then check the build's 수출 규정 status |

## After the build appears

- **"규정 준수 정보 누락"** blocks distribution until answered. The Info.plist
  key above removes the prompt permanently.
- **Internal testers** (up to 100) install immediately, no review. **External
  testers** (up to 10,000) need Beta App Review on the first build of each
  version — allow 1–2 days.
- A build expires 90 days after upload.

## Rotating a leaked credential

1. Revoke the ASC API key in the Integrations page, or the certificate via
   `asc.py list-certs` plus the developer portal.
2. Re-run SKILL.md step 1 (key) or step 4 (certificate).
3. Overwrite the affected secrets with `gh secret set`; the old values are not
   recoverable and do not need deleting first.
4. A leaked `.p12` also means every build signed with it is suspect — say so
   plainly rather than only rotating.
