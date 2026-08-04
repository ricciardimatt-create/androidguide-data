#!/usr/bin/env python3
"""
AndroidGuides.com — same-origin push (P3)

Pushes the freshly-validated devices.json and devices-static.html to the
WordPress endpoint (/wp-json/androidguide/v1/push) so /devices has a
same-origin fallback when the jsDelivr CDN is unreachable.

Auth: WordPress application password, supplied via the GitHub Actions
secrets WP_APP_USER and WP_APP_PASSWORD. Nothing is stored in the repo.

Runs LAST in the workflow — devices.json is already committed and the CDN
already purged by the time this runs, so a WordPress hiccup here never
blocks the primary CDN path. A non-zero exit still turns the run red so
the owner gets an email that the fallback push needs a look.

RETRIES (added 2026-08-04): SiteGround's firewall intermittently answers the
GitHub runner with an sgcaptcha challenge page instead of our JSON — it did
exactly that on 2026-08-01, which left the same-origin copy a cycle behind
while the CDN was fine. The challenge is rate/IP based and clears on its own,
so each file now gets up to PUSH_ATTEMPTS tries spaced RETRY_WAIT seconds
apart before the run is called a failure. Same philosophy as the CDN purge
step: don't fire and hope — confirm, and retry before crying wolf.

Stdlib only (no pip installs needed).
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

WP_BASE = "https://androidguides.com"
ENDPOINT = WP_BASE + "/wp-json/androidguide/v1/push"
FILES = ["devices.json", "devices-static.html"]
HERE = Path(__file__).parent

# Retry policy. Three attempts over ~2 minutes comfortably outlasts the
# short-lived firewall challenges we have actually seen, without making a
# genuinely broken endpoint take forever to report failure.
PUSH_ATTEMPTS = 3
RETRY_WAIT = 60  # seconds between attempts

# A browser-like User-Agent: some managed hosts (SiteGround included) return
# an empty/challenge page to the default "Python-urllib" agent. This is our
# own authenticated API, so identifying as a normal client is appropriate.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36 AndroidGuidesPipe/1.0")


def push_once(name, body, auth):
    """One attempt. Returns (ok: bool, retryable: bool, message: str)."""
    req = urllib.request.Request(ENDPOINT, data=body, method="POST")
    req.add_header("Authorization", "Basic " + auth)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", UA)

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
            final_url = r.geturl()
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        # 5xx and 429 are transient; 4xx (bad auth, rejected filename) is not.
        retryable = e.code >= 500 or e.code == 429
        return False, retryable, f"HTTP {e.code} — {detail!r}"
    except Exception as e:
        # Network/DNS/timeout — always worth another go.
        return False, True, str(e)

    try:
        resp = json.loads(raw)
    except json.JSONDecodeError:
        # This is the sgcaptcha case: HTTP 200/202 with an HTML challenge page.
        # Always retryable — it is the exact failure this retry loop exists for.
        return False, True, (f"HTTP {status} at {final_url} — response was not "
                             f"JSON (firewall challenge?). "
                             f"First 400 chars: {raw[:400]!r}")

    if not (isinstance(resp, dict) and resp.get("ok")):
        return False, False, f"endpoint returned {resp}"

    return True, False, f"-> {resp.get('url')} ({resp.get('bytes')} bytes)"


def push_file(name, body, auth):
    """Push one file, retrying transient failures. Returns True on success."""
    for attempt in range(1, PUSH_ATTEMPTS + 1):
        ok, retryable, msg = push_once(name, body, auth)
        if ok:
            note = "" if attempt == 1 else f" (succeeded on attempt {attempt})"
            print(f"[OK] pushed {name} {msg}{note}")
            return True

        last = attempt >= PUSH_ATTEMPTS
        if not retryable:
            print(f"[FAIL] {name}: {msg}")
            print(f"[FAIL] {name}: not a transient error — not retrying")
            return False
        if last:
            print(f"[FAIL] {name}: {msg}")
            print(f"[FAIL] {name}: still failing after {PUSH_ATTEMPTS} attempts")
            return False

        print(f"[WARN] {name}: attempt {attempt}/{PUSH_ATTEMPTS} failed — {msg}")
        print(f"[WARN] {name}: retrying in {RETRY_WAIT}s")
        time.sleep(RETRY_WAIT)

    return False


def main() -> int:
    user = os.environ.get("WP_APP_USER", "").strip()
    pw = os.environ.get("WP_APP_PASSWORD", "")
    if not user or not pw:
        print("[FAIL] WP_APP_USER / WP_APP_PASSWORD not set in the environment")
        return 1

    # WordPress accepts the application password with or without spaces.
    auth = base64.b64encode(f"{user}:{pw}".encode()).decode()

    fails = 0
    for name in FILES:
        p = HERE / name
        if not p.exists():
            print(f"[FAIL] {name}: not found in repo")
            fails += 1
            continue

        body = json.dumps({
            "name": name,
            "content_b64": base64.b64encode(p.read_bytes()).decode(),
        }).encode()

        if not push_file(name, body, auth):
            fails += 1

    if fails:
        print(f"[FAIL] {fails} file(s) failed to push to WordPress")
        return 1
    print("[OK] same-origin copies pushed to WordPress")
    return 0


if __name__ == "__main__":
    sys.exit(main())
