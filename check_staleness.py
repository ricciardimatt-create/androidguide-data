#!/usr/bin/env python3
"""
AndroidGuides.com — Weekly staleness alarm (P1)

Runs weekly via GitHub Actions. Fails (= GitHub emails the owner) if:
  1. devices.json 'generated' date is older than MAX_AGE_DAYS
     (the monthly pipe has silently stopped producing fresh data), or
  2. the jsDelivr CDN copy visitors actually load lags the repo copy
     by more than CDN_LAG_DAYS (CDN serving stale data).

No data is modified. This is a smoke detector, not a sprinkler.
"""

import json
import sys
import urllib.request
from datetime import date, datetime

REPO_FILE = "devices.json"
CDN_URL = "https://cdn.jsdelivr.net/gh/ricciardimatt-create/androidguide-data@main/devices.json"
PURGE_URL = "https://purge.jsdelivr.net/gh/ricciardimatt-create/androidguide-data@main/devices.json"
MAX_AGE_DAYS = 40   # monthly pipe + slack
CDN_LAG_DAYS = 7


def gen_date(payload: dict) -> date:
    return datetime.fromisoformat(payload["generated"]).date()


def main() -> int:
    fails = []
    today = date.today()

    repo = json.load(open(REPO_FILE))
    repo_age = (today - gen_date(repo)).days
    print(f"repo devices.json generated {repo['generated']} ({repo_age} days ago), "
          f"{len(repo['devices'])} devices")
    if repo_age > MAX_AGE_DAYS:
        fails.append(
            f"repo data is {repo_age} days old (limit {MAX_AGE_DAYS}) — "
            "the monthly update pipe has likely stopped running. "
            "Check the 'Update device database' workflow runs.")

    try:
        req = urllib.request.Request(CDN_URL, headers={"User-Agent": "AndroidGuidesStalenessCheck/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            cdn = json.load(r)
        lag = (gen_date(repo) - gen_date(cdn)).days
        print(f"CDN devices.json generated {cdn['generated']} (lags repo by {lag} days)")
        if lag > CDN_LAG_DAYS:
            fails.append(
                f"CDN copy lags repo by {lag} days (limit {CDN_LAG_DAYS}) — "
                f"visitors are seeing stale data. Purge it by opening: {PURGE_URL}")
    except Exception as e:
        fails.append(f"CDN fetch failed: {e} — visitors may not be getting data at all")

    if fails:
        print("\n[STALE] alarm triggered:")
        for f in fails:
            print(f"  ✗ {f}")
        return 1
    print("[OK] data is fresh, CDN in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
