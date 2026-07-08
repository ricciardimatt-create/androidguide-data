#!/usr/bin/env python3
"""
AndroidGuide.com — Device EOL database updater (Pipe #1)

Pulls device support data from the endoflife.date API and regenerates
devices.json. Designed to run monthly via GitHub Actions.

Usage:
    python update_devices.py            # fetch live, write devices.json
    python update_devices.py --dry-run  # fetch live, print diff, write nothing
"""

import json
import re
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path

API_BASE = "https://endoflife.date/api"
SOURCES = {
    "Google": "pixel.json",
    "Samsung": "samsung-mobile.json",
}
OUTPUT = Path(__file__).parent / "devices.json"
USER_AGENT = "AndroidGuideBot/1.0 (androidguide.com; contact: ricciardi.matt@gmail.com)"

# Only keep US-relevant Samsung lines; Pixel keeps everything phone-shaped.
SAMSUNG_KEEP = re.compile(
    r"^Galaxy (S\d{2}|Z (Fold|Flip)|A\d{2}\b)", re.IGNORECASE
)
PIXEL_SKIP = re.compile(r"(Tablet|Watch|Buds)", re.IGNORECASE)


def fetch(endpoint: str) -> list:
    """Fetch one product list from the endoflife.date API."""
    url = f"{API_BASE}/{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def slugify(brand: str, model: str) -> str:
    s = f"{brand}-{model}".lower()
    s = re.sub(r"[+]", "-plus", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def normalize(brand: str, raw: list) -> list:
    """Convert endoflife.date records to our schema. Facts only."""
    out = []
    for item in raw:
        model = item.get("releaseLabel") or item.get("cycle", "")
        eol = item.get("eol") or item.get("support")
        released = item.get("releaseDate")
        if not (model and released and isinstance(eol, str)):
            continue  # skip records without hard dates
        if brand == "Samsung" and not SAMSUNG_KEEP.match(model):
            continue
        if brand == "Google" and PIXEL_SKIP.search(model):
            continue
        if brand == "Google" and not model.startswith("Pixel"):
            model = f"Pixel {model}"
        out.append({
            "id": slugify(brand, model),
            "brand": brand,
            "model": model,
            "released": released,
            "eol": eol,
            "source": "endoflife.date",
        })
    return out


def load_existing() -> dict:
    if OUTPUT.exists():
        return {d["id"]: d for d in json.loads(OUTPUT.read_text())["devices"]}
    return {}


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    existing = load_existing()

    devices = []
    for brand, endpoint in SOURCES.items():
        try:
            devices += normalize(brand, fetch(endpoint))
        except Exception as e:  # one source failing shouldn't kill the run
            print(f"[WARN] {brand} fetch failed: {e} — keeping existing entries")
            devices += [d for d in existing.values() if d["brand"] == brand]

    # De-dupe on id, newest release first
    seen, deduped = set(), []
    for d in sorted(devices, key=lambda x: x["released"], reverse=True):
        if d["id"] not in seen:
            seen.add(d["id"])
            deduped.append(d)

    # Diff report — this becomes your monthly changelog / newsletter fodder
    new_ids = seen - set(existing)
    changed = [
        d["id"] for d in deduped
        if d["id"] in existing and existing[d["id"]]["eol"] != d["eol"]
    ]
    today = date.today().isoformat()
    print(f"[{today}] {len(deduped)} devices | {len(new_ids)} new | {len(changed)} EOL changes")
    for i in sorted(new_ids):
        print(f"  + NEW: {i}")
    for i in changed:
        print(f"  ~ EOL CHANGED: {i}: {existing[i]['eol']} -> "
              f"{next(d['eol'] for d in deduped if d['id'] == i)}")

    # Devices going EOL within 12 months — content/alert opportunities
    soon = [d for d in deduped if 0 <= (
        datetime.fromisoformat(d["eol"]).date() - date.today()).days <= 365]
    print(f"  ! {len(soon)} devices reach EOL within 12 months (alert/content targets)")

    if dry_run:
        print("[DRY RUN] devices.json not written")
        return 0

    OUTPUT.write_text(json.dumps({
        "schema_version": "1.0",
        "generated": today,
        "source_note": "EOL data from endoflife.date API. Samsung dates = security-update end; "
                       "spot-check against security.samsungmobile.com. Auto-generated — do not hand-edit.",
        "devices": deduped,
    }, indent=1))
    print(f"[OK] wrote {OUTPUT} ({len(deduped)} devices)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
