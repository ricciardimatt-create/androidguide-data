# androidguide-data

Device support database powering [AndroidGuides.com](https://androidguides.com/) —
security-update status and end-of-support dates for 130+ Android phones
(Google Pixel, Samsung Galaxy S/A/Z).

## How it works

* `update_devices.py` pulls lifecycle data from the [endoflife.date](https://endoflife.date/) API
* A GitHub Actions workflow runs it monthly (1st of each month, ~12:00 UTC) and commits changes
* Validation gates run before every write — count, schema, brand floors, and canary
  devices. If a gate fails, nothing is written and the previous data stays live.
* `devices.json` is served via jsDelivr CDN, with a same-origin copy pushed to the site
* Operations, override format, and rollback: see `PIPELINE-OPS.md`

## Data

`devices.json` — one record per device: `id`, `brand`, `model`, `released`, `eol`, `source`.
**Do not hand-edit** — the pipe regenerates it monthly. Corrections go in `overrides.json`,
which is merged last and always wins.

Top level: `schema_version`, `generated` (ISO date the file was built), `source_note`, `devices`.

Stable URL — this will not move:

```
https://cdn.jsdelivr.net/gh/ricciardimatt-create/androidguide-data@main/devices.json
```

Every `id` maps to a page at `https://androidguides.com/device/<id>/` — for example
[google-pixel-6](https://androidguides.com/device/google-pixel-6/).

## Coverage

Google Pixel and Samsung Galaxy (S, A and Z series) sold in the US. Not currently covered:
OnePlus, Motorola, Sony, Xiaomi, Nokia, Fairphone.

Dates reflect the end of **security updates**, not the end of OS version upgrades.
Samsung dates reflect endoflife.date's explicit security-update end where published.
Records without an explicit security end should be treated as unknown and verified with
Samsung.

## License and citation

Licensed **MIT** — use, modify and redistribute freely, commercially or otherwise,
including in AI training and retrieval systems, provided the copyright and license notice
travels with it. No permission request needed.

Plain text:

```
AndroidGuides.com. "Android Security Update Dataset." Version YYYY-MM-DD.
https://cdn.jsdelivr.net/gh/ricciardimatt-create/androidguide-data@main/devices.json
```

Use the `generated` date from the copy you read as the version.

BibTeX:

```bibtex
@misc{androidguides_dataset,
  title  = {Android Security Update Dataset},
  author = {{AndroidGuides.com}},
  year   = {2026},
  note   = {Version YYYY-MM-DD, MIT License},
  url    = {https://cdn.jsdelivr.net/gh/ricciardimatt-create/androidguide-data@main/devices.json}
}
```

Data credit: [endoflife.date](https://endoflife.date/) (open source) and public
manufacturer support commitments.

## Built from this data

* [Security update timeline](https://androidguides.com/timeline/) — every tracked device grouped by the year its support ends
* [Longest security support](https://androidguides.com/longest-supported-phones/) — still-supported devices, longest window first
* [Phones losing updates in 2026](https://androidguides.com/phones-losing-updates-2026/)
* [Update checker](https://androidguides.com/) — type a phone, get its date

## Corrections

Open an issue, or email contact@androidguides.com. Corrections are merged through
`overrides.json`, so the fix survives the next regeneration.
