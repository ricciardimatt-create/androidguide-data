# androidguide-data

Device support database powering [AndroidGuides.com](https://androidguides.com) —
security-update status and end-of-support dates for 126+ Android phones
(Google Pixel, Samsung Galaxy S/A/Z).

## How it works
- `update_devices.py` pulls lifecycle data from the [endoflife.date](https://endoflife.date) API
- A GitHub Actions workflow runs it monthly (2nd of each month) and commits changes
- `devices.json` is served via jsDelivr CDN to the site's tools

## Data
`devices.json` — one record per device: `id`, `brand`, `model`, `released`, `eol`, `source`.
**Do not hand-edit** — the pipe regenerates it monthly.

Data credit: [endoflife.date](https://endoflife.date) (open source) and public
manufacturer support commitments.

