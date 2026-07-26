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

Stdlib only (no pip installs needed).
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

WP_BASE = "https://androidguides.com"
ENDPOINT = WP_BASE + "/wp-json/androidguide/v1/push"
FILES = ["devices.json", "devices-static.html"]
HERE = Path(__file__).parent

# A browser-like User-Agent: some managed hosts (SiteGround included) return
# an empty/challenge page to the default "Python-urllib" agent. This is our
# own authenticated API, so identifying as a normal client is appropriate.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36 AndroidGuidesPipe/1.0")


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
            print(f"[FAIL] {name}: HTTP {e.code} — {detail!r}")
            fails += 1
            continue
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            fails += 1
            continue

        try:
            resp = json.loads(raw)
        except json.JSONDecodeError:
            print(f"[FAIL] {name}: HTTP {status} at {final_url} — "
                  f"response was not JSON. First 400 chars: {raw[:400]!r}")
            fails += 1
            continue

        if not (isinstance(resp, dict) and resp.get("ok")):
            print(f"[FAIL] {name}: endpoint returned {resp}")
            fails += 1
            continue

        print(f"[OK] pushed {name} -> {resp.get('url')} "
              f"({resp.get('bytes')} bytes)")

    if fails:
        print(f"[FAIL] {fails} file(s) failed to push to WordPress")
        return 1
    print("[OK] same-origin copies pushed to WordPress")
    return 0


if __name__ == "__main__":
    sys.exit(main())
