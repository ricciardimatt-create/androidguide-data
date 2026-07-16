# ANDROIDGUIDES.COM — COMPLETE PROJECT HANDOFF (v2)
*Updated 2026-07-13 · Owner: Matt (ricciardi.matt@gmail.com)*
*Purpose: full state capture so any new chat/model continues from this exact point. Supersedes the 2026-07-12 handoff.*

---

## 1. THE PROJECT IN ONE PARAGRAPH

AndroidGuides.com is a **utility-first website** (NOT a blog). Core tool: *"Is my Android phone still getting security updates?"* — update status, end-of-life (EOL) countdown, and a browsable database of all tracked devices. Data auto-updates monthly via a GitHub Actions pipe. Matt is a non-developer building this to learn AI/automation and eventually earn ~$100–300/mo. **Launch strategy (firm decision): pure utility — NO ads, NO affiliate dependency, NO email list at launch.** Monetization (MVNO bounties $20–150/signup, AI-software affiliates 20–50% recurring, deals feeds) is researched and documented but deferred. Email capture (MailerLite) also deferred — ALL email forms were removed from launch pages.

## 2. LIVE INFRASTRUCTURE (all confirmed working)

| Item | State |
|---|---|
| Domain | **androidguides.com (PLURAL)** @ GoDaddy, nameservers → ns1/ns2.siteground.net |
| Hosting | SiteGround StartUp · WordPress installed · SSL working |
| Theme | **Hello Elementor** (Twenty Twenty-Five squeezed custom HTML layouts) |
| Public state | Homepage shows Coming Soon; **/devices is publicly reachable** (fetch-verified) but noindex; WP "Discourage search engines" ON |
| GitHub repo | `ricciardimatt-create/androidguide-data` (public): update_devices.py, devices.json, .github/workflows/update-devices.yml |
| Pipe | GitHub Actions cron `0 9 2 * *` + manual trigger; tested OK; **never hand-edit devices.json** (pipe overwrites; corrections go in the script) |
| Live data | `https://cdn.jsdelivr.net/gh/ricciardimatt-create/androidguide-data@main/devices.json` — **126 devices** (Google Pixel + Samsung S/A/Z), schema: id, brand, model, released, eol, source |

## 3. SITE DESIGN — SETTLED DECISIONS (Matt-approved, do not regress)

- **Two-color scheme ONLY**: dark green (hero/toolbar/footer, gradient #0f1b13→#16301f→#1d4a2c) + pure WHITE everything else. No light-grey bands, no third background, no hairline dividers above the stats.
- **Headers identical on every page**: white bar, logo "AndroidGuides.com" 26px / weight 850 / letter-spacing -0.4px, green "Guides", aligned to the shared **1100px content edge** (all containers are 1100px — never mix 1200/1100).
- **Homepage** (= storefront): white header → dark hero with h1 "Is your Android still getting security updates?" (NO kicker line) + search with white Check button (Matt hates big bright-green buttons — "cheesy") → 3 live widget panels overlapping hero bottom (Losing support soon / Recently ended / Safest bets; clicking a device opens it in the checker; NO footer links in panels) → stats row on plain white (numbers dark-green) → dark footer with legal. NO tools section, NO email forms, NO #alerts anywhere.
- **/devices** (= workbench, Layout A "slim utility", the template for ALL future tool pages): white header → slim sticky dark toolbar (compact ~280px search whose placeholder shows live count "Search 126 devices…", segmented Status filters with live counts inside buttons, segmented Brand filters; all aligned to 1100px edge; hidden screen-reader h1) → one-line intro (static HTML for SEO: "Every Android phone we track, and the date its security updates stop…") → sortable table (human dates "Oct 2026", lifetime bars, ▲▼ sort indicators) → card view <700px with sort dropdown → empty state → dark footer.
- **Nav links**: Home: Update Tracker(#checker) · All Devices(/devices) · CTA Check My Phone(#checker). Devices: Home(/) · Check My Phone(/#checker). No Alerts links (no email yet).
- **Footer legal (required on every page)**: affiliate disclosure (generic/future), data-source note (manufacturer commitments + endoflife.date, refreshed monthly), "Android is a trademark of Google LLC. AndroidGuides.com is an independent publication and is not affiliated with, endorsed by, or sponsored by Google LLC.", © year.

## 4. WORDPRESS INTEGRATION — HARD-WON GOTCHAS

1. Each page = ONE Custom HTML block on a blank/full-width page. **Batch all edits per page into one regenerated file so Matt re-pastes exactly once.** Always tell him explicitly which blocks to re-paste.
2. Required CSS in every page block (already in the FINAL files): hide WP titles (.entry-title, .page-title, .elementor-page-title, .wp-block-post-title); full-bleed breakout (width:100vw + margin-left/right calc(50% - 50vw), background:#fff); strip theme content padding — **CRITICAL: only padding, border, and VERTICAL margins. Zeroing horizontal margins broke WP's container centering and shifted whole pages left (happened twice).**
3. Buttons/inputs inside blocks need !important resets or Elementor restyles them.
4. `.sugs:empty{display:none}` — the empty autocomplete dropdown otherwise renders as a white 2px line under the homepage search box (fixed).
5. **OPEN ISSUE:** a thin gray line appears at the top of pages in Matt's preview. Not yet diagnosed. Next step agreed: view in incognito (if gone → it's the WP admin toolbar, ignore); if present logged-out → Inspect the element and target its exact class. Do NOT throw broad CSS at it (that caused the left-shift bug).
6. Stale pastes are a recurring failure mode: if a page misbehaves after a fix, first check WP has the LATEST file version.

## 5. CURRENT FILES (in Cowork outputs folder — the two ALL-CAPS ones are the deploy artifacts)

| File | Status |
|---|---|
| **`androidguides-wp-homepage-LAUNCH.html`** | CURRENT homepage block. Latest fixes: search frame removed, .sugs:empty fix, stats on white no divider, header standardized 26px/1100px, widgets 3-across (minmax 280px), vertical-only theme strip |
| **`androidguides-wp-devices-FINAL.html`** | CURRENT /devices block. Layout A final: sticky toolbar, live-count filters, intro line, human dates, lifetime bars, mobile cards, empty state, noscript, white bg, corrected theme strip |
| `androidguide-homepage-v2.html` | Source-of-truth homepage (full standalone HTML; LAUNCH file is generated from it by stripping the document wrapper and prepending WP fixes) |
| `devices-layout-A/B/C-*.html` | Design mockups (A chosen; B = future mobile/cards inspiration; C = future /timeline page — strong shareable/Reddit concept) |
| `androidguide-strategy.md`, `androidguide-build-plan.md`, `pipe-setup-guide.md` | Research, monetization math, pipe architecture, future pipes curriculum |
| `update_devices.py`, `update-devices-workflow.yml`, `devices.json` | Pipe artifacts (live copies in GitHub repo; repo's update_devices.py has cosmetic stale user-agent "androidguide.com" — fix pending) |
| `ANDROIDGUIDES-HANDOFF.md` | This file |

Regeneration recipe (homepage): edit `androidguide-homepage-v2.html` → extract `<style>` contents + `<body>` contents → prepend WP-fixes CSS (title hide, vertical-only theme strip, #agdhome breakout with background:#fff) → wrap body in `<div id="agdhome">` → save as LAUNCH file.

## 6. LAUNCH CHECKLIST (exact remaining steps)

1. Matt: re-paste BOTH current files into their WP blocks (some pastes are stale)
2. Diagnose gray line via incognito/Inspect (see §4.5)
3. Matt: Settings → Reading → static front page = Home; verify /devices link flow
4. Optional pre-launch: About + Data Sources pages (credibility); Privacy can wait until email collection starts
5. Launch flip: SiteGround Coming Soon OFF → WP "Discourage search engines" OFF → Google Search Console + sitemap
6. Post-launch roadmap (deferred by explicit choice): MailerLite + restore email capture (removed sections are preserved in this doc's design spec), Plan Finder page, deals pipe (Best Buy API), pipe #2 Samsung scraper, /timeline page (launch article: "Every phone losing updates in 2026"), Reddit r/Android distribution, affiliate applications (Impact/CJ/ShareASale/Best Buy/Amazon — Amazon Creators API needs 10 sales/30 days)

## 7. CONTINUATION PROMPT — PASTE INTO A NEW CHAT

> I'm continuing an in-progress project. Attached is `ANDROIDGUIDES-HANDOFF.md` (v2, 2026-07-13) — read it fully first; it has all decisions, infrastructure, design specs, WordPress gotchas, and remaining steps. Also attach if possible: `androidguides-wp-homepage-LAUNCH.html`, `androidguides-wp-devices-FINAL.html`, `androidguide-homepage-v2.html`.
>
> Context: I'm Matt, non-developer. AndroidGuides.com (PLURAL) = utility site telling Android owners if their phone still gets security updates. Live: GitHub pipe (`ricciardimatt-create/androidguide-data`) feeding 126 devices via jsDelivr CDN; WordPress on SiteGround, Hello Elementor theme, behind Coming Soon, noindex on. Two pages exist as single Custom HTML blocks: Home (checker + live widgets) and /devices (sortable database). Launch = pure utility: no ads, no affiliates, no email forms (all deferred — do not re-add without me asking).
>
> Where we are: final design polish done (two-color scheme, 1100px alignment, identical headers). Remaining: (1) an undiagnosed thin gray line at the top of pages in my preview — next step is incognito test, then Inspect and target the exact element; do NOT apply broad CSS to theme wrappers, that previously broke page centering; (2) re-paste latest files into WP blocks; (3) launch checklist in handoff §6.
>
> Working rules: batch all edits per page into ONE regenerated paste-file and tell me exactly which WP blocks to re-paste; never hand-edit devices.json; keep the design spec in handoff §3 (no bright-green buttons, two colors only, 1100px everywhere); be concise. Start by confirming you've absorbed the handoff, then help me finish the gray-line diagnosis and the launch checklist.

---
*End of handoff v2 — current as of 2026-07-13.*
