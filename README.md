# androidguide-data

Device support database powering [AndroidGuides.com](https://androidguides.com) —
security-update status and end-of-support dates for 130+ Android phones
(Google Pixel, Samsung Galaxy S/A/Z).

## How it works
- `update_devices.py` pulls lifecycle data from the [endoflife.date](https://endoflife.date) API
- A GitHub Actions workflow runs it monthly (1st of each month) and commits changes
- Validation gates run before every write — count, schema, brand floors, and canary
  devices. If a gate fails, nothing is written and the previous data stays live.
- `devices.json` is served via jsDelivr CDN, with a same-origin copy pushed to the site
- Operations, override format, and rollback: see `PIPELINE-OPS.md`

## Data
`devices.json` — one record per device: `id`, `brand`, `model`, `released`, `eol`, `source`.
**Do not hand-edit** — the pipe regenerates it monthly. Corrections go in `overrides.json`,
which is merged last and always wins.

Licensed MIT. Data credit: [endoflife.date](https://endoflife.date) (open source) and
public manufacturer support commitments.
