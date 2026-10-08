#!/usr/bin/env python3
"""release-tag helper — deterministic parts of tagging an App Store release.

Subcommands
  find  <version> [--build N] [--workflow testflight.yml] [--limit 30]
        Lists the successful TestFlight uploads on main that shipped marketing
        version <version>, newest first, and marks the default pick (the last
        one, or the one whose build number is N), plus whether the vX.Y tag
        and its GitHub release already exist. Reads the workflow's job
        logs through `gh api`, so no App Store Connect key is needed.
        Output: JSON {"pick": {...}, "candidates": [...]}.

  notes <version> --summary FILE [--previous TAG]
        Prints a release body: the summary file, then GitHub's auto-generated
        notes since TAG (default: the highest existing v-tag below <version>).
        Uses the REST generate-notes endpoint because old `gh` lacks
        `--notes-start-tag`.

Requires: git, gh (authenticated). Exits non-zero with a one-line reason on
any failure — never leaves the agent to debug.
"""
import argparse
import json
import re
import subprocess
import sys

MARKETING_RE = re.compile(r"마케팅 버전: (\d+(?:\.\d+)+) \(")
BUILD_RE = re.compile(r"이번 빌드 번호: (\d+) ")


def die(msg, code=1):
    print(f"release_tag: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        die(f"{' '.join(cmd[:3])} 실패: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
    return r.stdout


def gh_json(path):
    return json.loads(run(["gh", "api", path]))


def repo_slug():
    url = run(["git", "remote", "get-url", "origin"]).strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        die(f"origin이 GitHub 저장소가 아니다: {url}")
    return m.group(1)


def vtuple(s):
    return tuple(int(p) for p in s.split("."))


# ---------------------------------------------------------------- find
def cmd_find(a):
    slug = repo_slug()
    runs = gh_json(
        f"repos/{slug}/actions/workflows/{a.workflow}/runs"
        f"?branch=main&status=success&per_page={a.limit}"
    ).get("workflow_runs", [])
    if not runs:
        die(f"{a.workflow}의 main 성공 실행이 없다 (워크플로 파일명을 --workflow로 확인)", 2)

    cands = []
    for r in runs:
        jobs = gh_json(f"repos/{slug}/actions/runs/{r['id']}/jobs").get("jobs", [])
        if not jobs:
            continue
        log = subprocess.run(
            ["gh", "api", f"repos/{slug}/actions/jobs/{jobs[0]['id']}/logs"],
            capture_output=True, text=True, errors="replace",
        ).stdout
        mv = [m.group(1) for m in MARKETING_RE.finditer(log)
              if not m.group(0).startswith("print(")]
        # 코드 echo 줄은 "print(f\"마케팅 버전: {marketing}" 꼴이라 숫자가 없어 매치되지 않는다
        bn = BUILD_RE.findall(log)
        if not mv:
            continue
        cands.append({
            "version": mv[-1],
            "build": int(bn[-1]) if bn else None,
            "sha": r["head_sha"][:7],
            "sha_full": r["head_sha"],
            "date": r["created_at"][:10],
            "run_url": r["html_url"],
        })

    same = [c for c in cands if c["version"] == a.version]
    if not same:
        seen = sorted({c["version"] for c in cands}, key=vtuple, reverse=True)
        die(f"버전 {a.version} 업로드를 최근 {len(runs)}개 실행에서 찾지 못했다. 보인 버전: {', '.join(seen) or '없음'}", 2)

    pick = same[0]
    if a.build is not None:
        hit = [c for c in same if c["build"] == a.build]
        if not hit:
            die(f"버전 {a.version} 빌드 {a.build} 업로드가 없다. 있는 빌드: {[c['build'] for c in same]}", 2)
        pick = hit[0]

    run(["git", "fetch", "-q", "origin", "main"])
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", pick["sha_full"], "origin/main"])
    if anc.returncode != 0:
        die(f"{pick['sha']}가 origin/main 이력에 없다 — bump-dev-version이 거부한다", 2)

    tag = f"v{a.version}"
    existing = run(["git", "tag", "-l", tag]).strip()
    rel = subprocess.run(["gh", "api", f"repos/{slug}/releases/tags/{tag}"], capture_output=True, text=True)
    release_url = json.loads(rel.stdout).get("html_url") if rel.returncode == 0 else None
    print(json.dumps({"tag": tag, "tag_exists": bool(existing), "release_url": release_url,
                      "pick": pick, "candidates": same}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- notes
def cmd_notes(a):
    slug = repo_slug()
    prev = a.previous
    if prev is None:
        tags = [t for t in run(["git", "tag", "-l", "v[0-9]*"]).split()
                if vtuple(t[1:]) < vtuple(a.version)]
        prev = max(tags, key=lambda t: vtuple(t[1:])) if tags else None
    try:
        summary = open(a.summary, encoding="utf-8").read().rstrip() + "\n\n"
    except OSError as e:
        die(f"요약 파일을 읽지 못했다: {e}")
    args = ["gh", "api", f"repos/{slug}/releases/generate-notes", "-f", f"tag_name=v{a.version}"]
    if prev:
        args += ["-f", f"previous_tag_name={prev}"]
    body = json.loads(run(args))["body"]
    sys.stdout.write(summary + body)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("version")
    f.add_argument("--build", type=int)
    f.add_argument("--workflow", default="testflight.yml")
    f.add_argument("--limit", type=int, default=30)
    f.set_defaults(fn=cmd_find)
    n = sub.add_parser("notes")
    n.add_argument("version")
    n.add_argument("--summary", required=True)
    n.add_argument("--previous")
    n.set_defaults(fn=cmd_notes)
    a = p.parse_args()
    if not re.fullmatch(r"\d+\.\d+(\.\d+)?", a.version):
        die(f"버전 형식이 아니다: {a.version} (예: 1.3)")
    a.fn(a)


if __name__ == "__main__":
    main()
