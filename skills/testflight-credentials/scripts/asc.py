#!/usr/bin/env python3
"""App Store Connect API helper for TestFlight credential setup.

Stdlib + the `openssl` and `security` CLIs only — no pip packages, so it runs
on a clean machine without touching the user's Python environment.

Subcommands:
  check              verify the API key authenticates
  find-app           look up an app record by bundle ID
  create-bundle-id   register an App ID (idempotent)
  list-certs         list the team's certificates
  create-cert        private key + CSR -> Apple Distribution cert -> .p12
  repackage-p12      rebuild a .p12 from a certificate that already exists
  verify-p12         prove the .p12 imports the same way CI imports it

Credentials are read from --key-id/--issuer-id/--key or the environment
(ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_PATH). When --key is omitted the script
looks for ~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8.

Every failure exits non-zero with an explanation. Nothing is left for the
caller to debug.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.appstoreconnect.apple.com/v1"


# --------------------------------------------------------------------------
# process helpers
# --------------------------------------------------------------------------

def die(message: str, *, hint: str = "") -> "NoReturn":  # type: ignore[name-defined]
    print(f"ERROR: {message}", file=sys.stderr)
    if hint:
        print(f"HINT:  {hint}", file=sys.stderr)
    sys.exit(1)


def try_run(cmd: list[str]) -> bool:
    """Run a command, returning success instead of exiting."""
    if shutil.which(cmd[0]) is None:
        return False
    done = subprocess.run(cmd, capture_output=True, check=False)
    return done.returncode == 0


def run(cmd: list[str], *, stdin: bytes | None = None, why: str) -> bytes:
    """Run a command, converting any failure into a readable error."""
    exe = shutil.which(cmd[0])
    if exe is None:
        die(f"`{cmd[0]}` not found on PATH ({why}).",
            hint="Install it, or run this on a machine that has it.")
    try:
        done = subprocess.run(cmd, input=stdin, capture_output=True, check=False)
    except OSError as exc:
        die(f"could not run `{cmd[0]}` ({why}): {exc}")
    if done.returncode != 0:
        detail = done.stderr.decode("utf-8", "replace").strip() or "(no stderr)"
        die(f"`{' '.join(cmd[:3])}...` failed while {why}:\n{detail}")
    return done.stdout


# --------------------------------------------------------------------------
# ES256 JWT, signed via the openssl CLI (no `cryptography` / PyJWT needed)
# --------------------------------------------------------------------------

def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def der_sig_to_raw(der: bytes) -> bytes:
    """Convert a DER ECDSA signature to the fixed-width r||s JOSE encoding."""
    if len(der) < 8 or der[0] != 0x30:
        die("ECDSA signature from openssl was not a DER SEQUENCE — "
            "the .p8 file is probably not a valid App Store Connect key.")
    # Skip SEQUENCE header (handles both short and long length forms).
    idx = 2 if der[1] < 0x80 else 2 + (der[1] & 0x7F)

    def read_int(pos: int) -> tuple[int, int]:
        if der[pos] != 0x02:
            die("malformed DER signature: expected INTEGER tag.")
        length = der[pos + 1]
        start = pos + 2
        value = der[start:start + length].lstrip(b"\x00")
        return int.from_bytes(value, "big"), start + length

    r, idx = read_int(idx)
    s, _ = read_int(idx)
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def make_token(key_path: Path, key_id: str, issuer_id: str) -> str:
    if not key_path.is_file():
        die(f"private key not found: {key_path}",
            hint="Pass --key /path/to/AuthKey_<KEY_ID>.p8, or place it at "
                 "~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8")
    text = key_path.read_text(errors="replace")
    if "BEGIN PRIVATE KEY" not in text:
        die(f"{key_path} does not look like a .p8 private key.",
            hint="Download the key again from App Store Connect -> Users and "
                 "Access -> Integrations. It is downloadable only once.")

    now = int(time.time())
    header = {"alg": "ES256", "kid": key_id, "typ": "JWT"}
    payload = {"iss": issuer_id, "iat": now, "exp": now + 600,
               "aud": "appstoreconnect-v1"}
    signing_input = ".".join(
        b64url(json.dumps(part, separators=(",", ":")).encode())
        for part in (header, payload)
    ).encode()

    der = run(["openssl", "dgst", "-sha256", "-sign", str(key_path)],
              stdin=signing_input, why="signing the API token")
    return f"{signing_input.decode()}.{b64url(der_sig_to_raw(der))}"


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def request(token: str, method: str, path: str,
            body: dict | None = None) -> dict:
    url = path if path.startswith("http") else f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        try:
            errors = json.loads(detail).get("errors", [])
            detail = "\n".join(
                f"  [{e.get('status')}] {e.get('title')}: {e.get('detail')}"
                for e in errors
            ) or detail
        except json.JSONDecodeError:
            pass
        hint = ""
        if exc.code == 401:
            hint = ("The key, key ID, and issuer ID must all come from the "
                    "same App Store Connect team key.")
        elif exc.code == 403:
            hint = ("The API key needs the App Manager role (Admin also "
                    "works). A Developer-role key cannot create resources.")
        die(f"{method} {url} -> HTTP {exc.code}\n{detail}", hint=hint)
    except urllib.error.URLError as exc:
        die(f"could not reach App Store Connect: {exc.reason}")


def resolve_auth(args: argparse.Namespace) -> str:
    key_id = args.key_id or os.environ.get("ASC_KEY_ID")
    issuer_id = args.issuer_id or os.environ.get("ASC_ISSUER_ID")
    if not key_id:
        die("missing key ID.", hint="Pass --key-id or set ASC_KEY_ID.")
    if not issuer_id:
        die("missing issuer ID.", hint="Pass --issuer-id or set ASC_ISSUER_ID.")
    raw_key = args.key or os.environ.get("ASC_KEY_PATH")
    key_path = Path(raw_key).expanduser() if raw_key else (
        Path.home() / ".appstoreconnect/private_keys" / f"AuthKey_{key_id}.p8"
    )
    return make_token(key_path, key_id, issuer_id)


# --------------------------------------------------------------------------
# subcommands
# --------------------------------------------------------------------------

def cmd_check(args: argparse.Namespace) -> None:
    token = resolve_auth(args)
    apps = request(token, "GET", "/apps?limit=200")["data"]
    print(f"OK: key authenticates. {len(apps)} app record(s) visible.")
    for app in apps[:20]:
        attrs = app["attributes"]
        print(f"  {attrs.get('bundleId')}  ({attrs.get('name')})  id={app['id']}")


def cmd_find_app(args: argparse.Namespace) -> None:
    token = resolve_auth(args)
    query = urllib.parse.quote(args.bundle_id, safe="")
    apps = request(token, "GET", f"/apps?filter[bundleId]={query}")["data"]
    if not apps:
        print(f"NOT_FOUND: no app record for {args.bundle_id}")
        sys.exit(2)
    app = apps[0]
    print(f"FOUND: {args.bundle_id}")
    print(f"  appleId={app['id']}  name={app['attributes'].get('name')}")


def cmd_create_bundle_id(args: argparse.Namespace) -> None:
    token = resolve_auth(args)
    query = urllib.parse.quote(args.identifier, safe="")
    existing = request(
        token, "GET", f"/bundleIds?filter[identifier]={query}")["data"]
    if existing:
        print(f"ALREADY_EXISTS: {args.identifier} (id={existing[0]['id']})")
        return
    created = request(token, "POST", "/bundleIds", {
        "data": {
            "type": "bundleIds",
            "attributes": {
                "identifier": args.identifier,
                "name": args.name,
                "platform": args.platform,
            },
        }
    })
    print(f"CREATED: {args.identifier} (id={created['data']['id']})")


def cmd_list_certs(args: argparse.Namespace) -> None:
    token = resolve_auth(args)
    certs = request(token, "GET", "/certificates?limit=200")["data"]
    if not certs:
        print("no certificates on this team.")
        return
    for cert in certs:
        a = cert["attributes"]
        print(f"  {a.get('certificateType'):<24} {a.get('displayName')}  "
              f"expires={a.get('expirationDate')}  id={cert['id']}")
    dist = [c for c in certs
            if c["attributes"].get("certificateType") == "DISTRIBUTION"]
    print(f"\nApple Distribution certificates: {len(dist)} "
          f"(Apple caps this at 3 per team)")


def cmd_create_cert(args: argparse.Namespace) -> None:
    token = resolve_auth(args)
    out = Path(args.out_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    key_pem, csr_pem = out / "dist-private-key.pem", out / "dist.csr"
    cert_pem, p12 = out / "dist-cert.pem", out / "dist.p12"
    pw_file = out / "p12-password.txt"

    for path in (key_pem, p12):
        if path.exists() and not args.force:
            die(f"{path} already exists.",
                hint="Re-run with --force to overwrite, but only after "
                     "confirming the old key is not still in use anywhere.")

    run(["openssl", "genrsa", "-out", str(key_pem), "2048"],
        why="generating the private key")
    key_pem.chmod(0o600)
    run(["openssl", "req", "-new", "-key", str(key_pem), "-out", str(csr_pem),
         "-subj", f"/CN={args.common_name}/C=US"],
        why="generating the certificate signing request")

    csr_b64 = base64.b64encode(csr_pem.read_bytes()).decode()
    created = request(token, "POST", "/certificates", {
        "data": {
            "type": "certificates",
            "attributes": {"certificateType": args.type, "csrContent": csr_b64},
        }
    })
    attrs = created["data"]["attributes"]
    der = base64.b64decode(attrs["certificateContent"])
    (out / "dist-cert.cer").write_bytes(der)
    run(["openssl", "x509", "-inform", "DER", "-in", str(out / "dist-cert.cer"),
         "-out", str(cert_pem)], why="converting the certificate to PEM")

    build_p12(key_pem, cert_pem, p12, pw_file,
              attrs.get("displayName", "Apple Distribution"))

    print(f"CREATED: {attrs.get('certificateType')} "
          f"'{attrs.get('displayName')}' expires {attrs.get('expirationDate')}")
    report_p12(p12, pw_file, key_pem)


def build_p12(key_pem: Path, cert_pem: Path, p12: Path, pw_file: Path,
              friendly_name: str) -> None:
    """Package a key + certificate into a .p12 `security import` accepts."""
    for path in (key_pem, cert_pem):
        if not path.is_file():
            die(f"missing input: {path}")
    password = secrets.token_urlsafe(24)
    export = ["openssl", "pkcs12", "-export", "-inkey", str(key_pem),
              "-in", str(cert_pem), "-out", str(p12),
              "-name", friendly_name, "-passout", f"pass:{password}"]
    # OpenSSL 3 defaults to AES-256 + PBKDF2, which `security import` rejects
    # outright — measured on macOS 15 / OpenSSL 3.6: default export imports
    # FAIL, -legacy export imports OK. The CI workflow uses `security import`,
    # so -legacy is required, not merely preferred. The trade-off is that
    # reading the file back also needs -legacy (see cmd_verify_p12).
    version = run(["openssl", "version"], why="checking the openssl version")
    if version.decode().startswith("OpenSSL 3"):
        export.append("-legacy")
    run(export, why="packaging the .p12")
    p12.chmod(0o600)
    pw_file.write_text(password + "\n")
    pw_file.chmod(0o600)


def report_p12(p12: Path, pw_file: Path, key_pem: Path) -> None:
    print(f"  p12:      {p12}")
    print(f"  password: {pw_file}  (not printed here on purpose)")
    print(f"  key:      {key_pem}  (losing this makes the certificate useless)")
    print("\nNext: verify it imports, then load both into GitHub secrets:")
    print(f"  python3 {Path(__file__).name} verify-p12 --p12 {p12} "
          f"--password-file {pw_file}")


def cmd_repackage_p12(args: argparse.Namespace) -> None:
    """Rebuild a .p12 from a certificate that is already issued.

    For when the certificate itself is fine but the .p12 around it was built
    with encryption `security import` rejects. Touches no Apple resource, so
    it works at the 3-certificate limit where create-cert cannot.
    """
    out = Path(args.out_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    key_src = Path(args.key_pem).expanduser()
    cert_src = Path(args.cert).expanduser()
    key_pem, cert_pem = out / "dist-private-key.pem", out / "dist-cert.pem"
    p12, pw_file = out / "dist.p12", out / "p12-password.txt"

    if p12.exists() and not args.force:
        die(f"{p12} already exists.", hint="Re-run with --force to overwrite.")
    if key_src.resolve() != key_pem.resolve():
        shutil.copyfile(key_src, key_pem)
        key_pem.chmod(0o600)
    # Accept either PEM or Apple's DER .cer without making the caller convert.
    if cert_src.read_bytes().lstrip().startswith(b"-----BEGIN"):
        if cert_src.resolve() != cert_pem.resolve():
            shutil.copyfile(cert_src, cert_pem)
    else:
        run(["openssl", "x509", "-inform", "DER", "-in", str(cert_src),
             "-out", str(cert_pem)], why="converting the certificate to PEM")

    build_p12(key_pem, cert_pem, p12, pw_file, args.common_name)
    print("REPACKAGED: no Apple resource was created or revoked.")
    report_p12(p12, pw_file, key_pem)


def cmd_verify_p12(args: argparse.Namespace) -> None:
    """Import the .p12 exactly the way the CI workflow does."""
    p12 = Path(args.p12).expanduser()
    if not p12.is_file():
        die(f"no such file: {p12}")
    password = Path(args.password_file).expanduser().read_text().strip()

    # A -legacy-encrypted .p12 needs -legacy to read back; a default-encrypted
    # one needs it absent. Accept either, and only complain if both fail.
    base = ["openssl", "pkcs12", "-in", str(p12), "-noout",
            "-passin", f"pass:{password}"]
    if not (try_run(base + ["-legacy"]) or try_run(base)):
        die("openssl could not open the .p12 with the supplied password.",
            hint="The password file and the .p12 must be the matching pair "
                 "produced by the same `create-cert` run.")

    if sys.platform != "darwin":
        print("OK: .p12 opens. (Keychain import check skipped — not macOS.)")
        return

    keychain = Path(tempfile.gettempdir()) / f"asc-verify-{os.getpid()}.keychain"
    kc_password = secrets.token_urlsafe(16)
    run(["security", "create-keychain", "-p", kc_password, str(keychain)],
        why="creating a throwaway keychain")
    try:
        run(["security", "unlock-keychain", "-p", kc_password, str(keychain)],
            why="unlocking the throwaway keychain")
        run(["security", "import", str(p12), "-k", str(keychain),
             "-P", password, "-T", "/usr/bin/codesign"],
            why="importing the .p12 the way the CI workflow does")
        identities = run(["security", "find-identity", "-v", "-p", "codesigning",
                          str(keychain)], why="listing signing identities")
        found = [line.strip() for line in
                 identities.decode("utf-8", "replace").splitlines()
                 if ")" in line and '"' in line]
        if found:
            print("OK: .p12 imports and yields a code-signing identity.")
            for line in found:
                print(f"  {line}")
        else:
            print("PARTIAL: .p12 imports, but no code-signing identity was "
                  "found in it.")
            print("  A real Apple Distribution certificate always yields one. "
                  "If this is one, the private key did not travel with the "
                  "certificate — rebuild with `repackage-p12` (or "
                  "`create-cert` if the certificate itself is gone).")
            sys.exit(3)
    finally:
        subprocess.run(["security", "delete-keychain", str(keychain)],
                       capture_output=True, check=False)


# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--key-id", help="ASC key ID (env: ASC_KEY_ID)")
    parser.add_argument("--issuer-id", help="ASC issuer ID (env: ASC_ISSUER_ID)")
    parser.add_argument("--key", help="path to AuthKey_<KEY_ID>.p8 "
                                      "(env: ASC_KEY_PATH)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="verify the API key authenticates")

    p = sub.add_parser("find-app", help="look up an app record by bundle ID")
    p.add_argument("--bundle-id", required=True)

    p = sub.add_parser("create-bundle-id", help="register an App ID")
    p.add_argument("--identifier", required=True, help="e.g. com.example.App")
    p.add_argument("--name", required=True,
                   help="letters, numbers and spaces only — Apple rejects "
                        "punctuation such as '.' or '-'")
    p.add_argument("--platform", default="IOS",
                   choices=["IOS", "MAC_OS", "UNIVERSAL"])

    sub.add_parser("list-certs", help="list the team's certificates")

    p = sub.add_parser("create-cert", help="create a distribution cert + .p12")
    p.add_argument("--out-dir", required=True,
                   help="a directory OUTSIDE any git repo")
    p.add_argument("--common-name", default="Apple Distribution")
    p.add_argument("--type", default="DISTRIBUTION",
                   choices=["DISTRIBUTION", "IOS_DISTRIBUTION"])
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("repackage-p12",
                       help="rebuild a .p12 from an already-issued certificate "
                            "(no Apple resource touched)")
    p.add_argument("--key-pem", required=True, help="the existing private key")
    p.add_argument("--cert", required=True, help="the issued certificate, "
                                                 "PEM or DER .cer")
    p.add_argument("--out-dir", required=True,
                   help="a directory OUTSIDE any git repo")
    p.add_argument("--common-name", default="Apple Distribution")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("verify-p12", help="prove the .p12 imports like CI does")
    p.add_argument("--p12", required=True)
    p.add_argument("--password-file", required=True)

    args = parser.parse_args()
    {
        "check": cmd_check,
        "find-app": cmd_find_app,
        "create-bundle-id": cmd_create_bundle_id,
        "list-certs": cmd_list_certs,
        "create-cert": cmd_create_cert,
        "repackage-p12": cmd_repackage_p12,
        "verify-p12": cmd_verify_p12,
    }[args.command](args)


if __name__ == "__main__":
    main()
