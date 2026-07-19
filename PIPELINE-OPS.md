# PIPELINE OPS — Guarded Pipeline (P1)

How the AndroidGuides.com data pipeline protects itself, how to correct bad data,
and how to roll back. Written for Matt (non-developer, GitHub web UI only).

## How the guard works

Every monthly run of `update_devices.py` now does, in order:

1. Fetch fresh data from endoflife.date (unchanged)
2. Merge `overrides.json` LAST — your manual corrections always win
3. Run validation gates:
   - device count ≥ 100 and ≤ 500
   - count moved no more than ±10% vs the current devices.json
   - every record has all 6 fields, valid ISO dates, eol after released, no duplicate ids
   - brand floors: ≥ 15 Google, ≥ 40 Samsung
   - 4 canary devices exist with their known release dates
     (pixel-8, pixel-6, galaxy-s24, galaxy-z-fold5)
4. ANY gate fails → devices.json is NOT written, the workflow run fails,
   **GitHub emails you**, and the previous good data stays live. Bad data
   cannot reach visitors.

A second workflow, **Data staleness check**, runs every Monday and fails
(= emails you) if the data is over 40 days old (pipe silently dead) or the
jsDelivr CDN copy lags the repo by over 7 days (visitors seeing stale data).

Silence = healthy. Email = something needs a look. Nothing auto-fixes itself
by design — a smoke detector, not a sprinkler.

> One-time check: github.com → Settings → Notifications → Actions →
> make sure "Email" is ticked for failed workflows.

## Correcting a wrong date (overrides.json)

Never edit devices.json — the next monthly run overwrites it. Instead, edit
`overrides.json` on the GitHub website (pencil icon), add an entry inside the
`"overrides": [ ]` list, and commit. It applies on the next run (or trigger
one manually: Actions → Update device database → Run workflow).

**Fix a wrong EOL date:**
```json
{
  "id": "samsung-galaxy-s22",
  "fields": { "eol": "2027-06-30" },
  "reason": "Samsung security page shows June 2027, endoflife.date lags",
  "added": "2026-07-18"
}
```

**Add a device the source is missing:**
```json
{
  "id": "samsung-galaxy-a99",
  "add": true,
  "fields": {
    "brand": "Samsung", "model": "Galaxy A99",
    "released": "2026-06-01", "eol": "2032-06-01"
  },
  "reason": "Missing upstream; dates from samsung.com press release",
  "added": "2026-07-18"
}
```

**Remove a device that shouldn't be listed:**
```json
{
  "id": "samsung-galaxy-a13-sm-a137",
  "remove": true,
  "reason": "Regional variant, confusing US visitors",
  "added": "2026-07-18"
}
```

Rules: `id` and `reason` are required. Multiple entries are separated by
commas. Overridden records get `"source": "override"` so we can always tell
human facts from automated ones. Overrides are validated too — a typo'd date
here trips the gate and emails you rather than shipping.

## Rollback ritual (bad data got committed anyway)

1. Repo → `devices.json` → **History** (clock icon) → click the last GOOD commit
2. Click **Raw**, select all, copy
3. Back on `main`: `devices.json` → pencil icon → select all → paste → commit
   with message `Rollback to <date> data`
4. Force the CDN to pick it up now instead of in ~12h: open
   `https://purge.jsdelivr.net/gh/ricciardimatt-create/androidguide-data@main/devices.json`
   in your browser (a page of JSON = success)
5. Then fix the root cause via overrides.json — otherwise the next monthly
   run may recommit the same bad data (the gates should catch it, but don't rely on luck)

## Monthly rhythm

- 1st of the month ~12:00 UTC: pipe runs. No email = success.
- Any Monday email from "Data staleness check" = investigate that day.
- Canary trip after an endoflife.date format change: check their site; if the
  new value is actually correct, update the CANARIES dict in update_devices.py.
