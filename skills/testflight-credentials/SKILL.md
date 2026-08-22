---
name: testflight-credentials
description: >-
  Registers the Apple Developer and App Store Connect resources an iOS app
  needs before its first TestFlight upload, then loads them into GitHub Actions
  secrets. Creates the App ID and an Apple Distribution certificate through the
  App Store Connect API — building the CSR and .p12 locally with openssl, so no
  Xcode or Keychain GUI is involved — verifies the .p12 imports the way CI
  imports it, and sets ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_P8,
  DIST_CERT_P12_BASE64 and DIST_CERT_PASSWORD via `gh secret set`. Walks the
  user through the only two steps Apple offers no API for: issuing the ASC API
  key and creating the app record. Use when preparing an app for its first
  TestFlight build or fixing a signing or upload failure — "TestFlight 올릴 준비
  해줘", "App ID 등록해줘", "배포 인증서 만들어줘", "p12 만들어줘", "ASC API 키
  발급", "코드사인 시크릿 등록해줘", "set up TestFlight signing", "create a
  distribution certificate". Not for writing the upload workflow YAML (that is
  ios-project-setup), and not for App Store review submission or metadata.
---

# TestFlight Credentials

Take an iOS repo from "no Apple resources registered" to "GitHub Actions can
upload to TestFlight", doing through the API everything the API can do.

**Language rule:** this file is English, but **every question, status line, and
report to the user MUST be in Korean (한국어).**

## What this produces

| # | Resource | Created by | How |
|---|---|---|---|
| 1 | ASC API key — `.p8` + Key ID + Issuer ID | **user** | browser; no API can mint the first key |
| 2 | App ID (bundle ID) | this skill | `scripts/asc.py create-bundle-id` |
| 3 | App record | **user** | browser; App Store Connect has no create-app API |
| 4 | Apple Distribution cert → `.p12` | this skill | `scripts/asc.py create-cert` |
| 5 | 5 GitHub Actions secrets | this skill | `gh secret set` |

Do them in this order. Step 1 unlocks every API call, and step 3 must exist
before the first workflow run because the build-number lookup queries the app
by bundle ID.

`scripts/asc.py` needs only Python 3 stdlib plus `openssl` — no pip installs.

## Step 0 — Scan, then ask only for what is missing

```bash
git rev-parse --show-toplevel; gh auth status 2>&1 | head -3; openssl version
find . -name project.yml -not -path '*/.*' -maxdepth 3
```

Then read the project file for these four facts:

| Fact | Usual source |
|---|---|
| Bundle ID | `PRODUCT_BUNDLE_IDENTIFIER`, or `bundleIdPrefix` + target name |
| Team ID | `DEVELOPMENT_TEAM`, or `TEAM_ID` in the workflow |
| App name | `CFBundleDisplayName`, else ask |
| Repo | `gh repo view --json nameWithOwner -q .nameWithOwner` |

Report the findings in Korean and ask only for what the scan did not yield.

**Never register a bundle ID the user has not confirmed.** Finding
`bundleIdPrefix: com.nepnep` and a target `NepNep` means you propose
`com.nepnep.NepNep` and wait for a yes — you do not pass it to
`create-bundle-id` because it is the obvious composition. A wrong App ID
cannot be deleted, only abandoned.

Stop and say so in Korean if `gh` is unauthenticated (step 5 cannot run) or
`openssl` is missing (step 4 cannot run). Do not proceed to step 1 first and
discover it later.

## Step 1 — ASC API key (user, in browser)

Give the user these instructions verbatim in Korean:

1. https://appstoreconnect.apple.com/access/integrations/api → **팀 키** tab
2. `+` → name it after the consumer (e.g. `github-ci`) → access **App Manager**
3. Download `AuthKey_<KEY_ID>.p8` — **downloadable exactly once**
4. Copy the **Key ID** (10 chars) and the **Issuer ID** (UUID) from that page

App Manager is the minimum. A Developer-role key authenticates but returns 403
on every create call in steps 2 and 4.

Then confirm the key works before going further:

```bash
python3 skills/testflight-credentials/scripts/asc.py check \
  --key-id <KEY_ID> --issuer-id <ISSUER_ID> --key ~/Downloads/AuthKey_<KEY_ID>.p8
```

Expected: `OK: key authenticates. N app record(s) visible.` Anything else —
stop and fix here; every later step uses the same credentials.

## Step 2 — App ID (API)

```bash
python3 .../asc.py create-bundle-id --identifier com.example.MyApp --name "MyApp" ...auth
```

`--name` accepts letters, numbers and spaces only; Apple rejects `.`, `-`, `_`.
Derive it from the app name by stripping punctuation, e.g. `com.nepnep.NepNep`
→ `NepNep`.

The command is idempotent: it prints `ALREADY_EXISTS` and changes nothing when
the identifier is already registered, so re-running after a partial failure is
safe.

App-extension bundle IDs (widgets, share extensions) do **not** need this step
— `xcodebuild -allowProvisioningUpdates` creates them during the first archive.
Register only the main app.

## Step 3 — App record (user, in browser)

No API exists for this; App Store Connect requires the web UI.

1. https://appstoreconnect.apple.com/apps → `+` → **신규 앱**
2. Platform iOS, pick the bundle ID registered in step 2, set name / primary
   language / SKU
3. Note the numeric **Apple ID** shown on the app's 앱 정보 page

Confirm it landed:

```bash
python3 .../asc.py find-app --bundle-id com.example.MyApp ...auth
```

`NOT_FOUND` (exit 2) means the record is not there yet — the app name may have
been rejected as already taken, which the UI reports but the API cannot see.

## Step 4 — Distribution certificate → .p12

```bash
python3 .../asc.py create-cert --out-dir ~/.private/<app>-signing ...auth
python3 .../asc.py verify-p12 --p12 <p12> --password-file <pw file>
```

`create-cert` generates the private key and CSR locally, sends only the CSR to
Apple, and packages the returned certificate into `dist.p12` with a random
password. The private key never leaves the machine.

`verify-p12` imports the file into a throwaway keychain exactly the way the
workflow does, then deletes that keychain. **Never skip it.** OpenSSL 3's
default PKCS#12 encryption is silently rejected by `security import` — the
file looks fine, `openssl` reads it back happily, and the CI job fails at the
signing step twenty minutes into the run. `create-cert` passes `-legacy` to
avoid this, and `verify-p12` is what proves it worked.

Expected output: `OK: .p12 imports and yields a code-signing identity.`
`PARTIAL` (exit 3) means the certificate arrived without its private key —
rebuild rather than uploading it.

### When the certificate already exists

Reach for `repackage-p12` — never for `openssl pkcs12` by hand — whenever the
certificate is fine and only the packaging is wrong: the team is at the
3-certificate limit, the old `.p12` was built without `-legacy`, or its
password was lost. It rebuilds `dist.p12` from a private key plus an already
issued certificate and creates or revokes nothing at Apple.

```bash
python3 .../asc.py repackage-p12 --key-pem <key.pem> --cert <cert.cer or .pem> \
  --out-dir ~/.private/<app>-signing
python3 .../asc.py verify-p12 --p12 <p12> --password-file <pw file>
```

`--cert` takes PEM or DER (`.cer` downloads from the developer portal are DER).
It refuses to overwrite an existing `dist.p12` without `--force`.

Hand-rolling the equivalent `openssl pkcs12 -export` goes wrong quietly: the
`-legacy` flag gets forgotten, and `-passout file:~/dir/pw.txt` does not expand
the tilde inside that argument, so the file lands with a literal `~` path or an
empty password.

**Choose `--out-dir` outside every git repo, named after the app in front of
you.** `--out-dir ./signing` is wrong even with a `.gitignore` entry: a later
`git add -f` or an archive of the working tree publishes the signing key, and a
leaked distribution key lets anyone ship builds signed as this team. Equally
wrong is `--out-dir ~/.private/nepnep-signing` while setting up an app called
TuneGlass — that path is copied from this file's worked example, not derived
from the project, and it hides one app's signing key under another app's name.

**Never revoke an existing certificate to make room.** Apple caps a team at 3
Apple Distribution certificates; at the limit `create-cert` fails with Apple's
error. Run `list-certs`, show the user what exists in Korean, and let them
choose — revoking breaks every other machine and pipeline still signing with
that certificate. If they only need a `.p12` on this machine and the private
key from the original issuance is available, `repackage-p12` avoids the
question entirely.

## Step 5 — GitHub secrets

```bash
gh secret set ASC_KEY_ID --body "<KEY_ID>"
gh secret set ASC_ISSUER_ID --body "<ISSUER_ID>"
gh secret set ASC_KEY_P8 < ~/Downloads/AuthKey_<KEY_ID>.p8
gh secret set DIST_CERT_P12_BASE64 --body "$(openssl base64 -A -in <dir>/dist.p12)"
gh secret set DIST_CERT_PASSWORD < <dir>/p12-password.txt
```

`openssl base64 -A` emits one unwrapped line; plain `base64` wraps on some
platforms and the wrapped value fails to decode in the runner.

Confirm with `gh secret list` — it prints names and timestamps, never values.

**Never echo a secret to check it.** No `cat AuthKey_*.p8`, no
`echo $P12_PASSWORD`, no `--body "$(cat pw.txt)"` written out in a message.
Session transcripts persist; pipe from the file instead, as above.

## Step 6 — Hand back

Report in Korean: which of the five resources now exist, the app's numeric
Apple ID, and what the user should do next (merge to the branch the workflow
watches, or run it via `workflow_dispatch`). State plainly that the first
upload takes 20–35 minutes and that ASC needs another 5–15 minutes of
processing before the build appears in TestFlight.

For failures after the upload starts, see
[references/troubleshooting.md](references/troubleshooting.md).

## Worked example

Input: repo `JKPark83/nepnep`, `project.yml` with `bundleIdPrefix: com.nepnep`,
target `NepNep`, `DEVELOPMENT_TEAM: WDNVP9B8A9`; user supplies key ID
`ABCD123456`, issuer `abc-123-def`, and `~/Downloads/AuthKey_ABCD123456.p8`.

Output — after confirming `com.nepnep.NepNep` with the user:

```
$ asc.py check ...
OK: key authenticates. 0 app record(s) visible.

$ asc.py create-bundle-id --identifier com.nepnep.NepNep --name "NepNep" ...
CREATED: com.nepnep.NepNep (id=A1B2C3D4E5)

  → 앱 레코드는 API로 못 만듭니다. 브라우저에서 만들어 주세요: (step 3 안내)

$ asc.py find-app --bundle-id com.nepnep.NepNep ...
FOUND: com.nepnep.NepNep
  appleId=6748291043  name=넵넵

$ asc.py create-cert --out-dir ~/.private/nepnep-signing ...
CREATED: DISTRIBUTION 'Apple Distribution' expires 2027-08-22T...

$ asc.py verify-p12 ...
OK: .p12 imports and yields a code-signing identity.
  1) A1B2... "Apple Distribution: Jinkon Park (WDNVP9B8A9)"

$ gh secret list
ASC_ISSUER_ID  ASC_KEY_ID  ASC_KEY_P8  DIST_CERT_P12_BASE64  DIST_CERT_PASSWORD
```

Then the Korean report: 5개 리소스 준비 완료, Apple ID `6748291043`,
`main` 머지 시 업로드 시작.
