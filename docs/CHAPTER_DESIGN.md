# CS2-Manim design baseline (2026-10-15)

This document specifies the target system. Only the **synthetic two-chapter preview** is currently implemented and CI-tested; all other items below are not implemented until explicitly marked.

## 1. Series taxonomy

| Family | Series identity | Members | Future special fields |
| --- | --- | --- | --- |
| Weapon collection | Source collection ID | Contained skin IDs joined to specific normal wear variants | Release date, rarity distribution, source collection art |
| Weapon case | Case/crate ID where `type=Case` | Contained skin IDs joined to specific normal wear variants | Case market price, case release date, rare-special drops |

Never merge a collection and a case based on similar names. A weapon skin may occur in several containers; shared skins are not unique inventory assets. `market_hash_name` is the initial market identity, while grouped `skin_id` identifies the base finish. Future variation keys should include edition, wear, phase, and any relevant subtype. Do not infer market values from rarity or loot probabilities.

## 2. Planned complete chapter storyboard

| Order | Collection scene | Case scene | Target duration |
| --- | --- | --- | --- |
| 1 | Title, series identity, as-of date | Case title, release, as-of date | 4–6 s |
| 2 | Skin count and rarity histogram | Contained skins and rarity histogram | 6–10 s |
| 3 | Weapon artwork and editions | Weapon artwork, rare special-drop category if verified | 12–20 s |
| 4 | Price ranking by normalized variant | Price ranking plus separately quoted container price | 10–15 s |
| 5 | Price movement: 7d/30d/90d | Price movement for case and top components | 12–20 s |
| 6 | Source, coverage and missing-data notes | Source, coverage and missing-data notes | 4–6 s |

Target independent chapter MP4s and a compilation with exact chapter timecodes. The smoke prototype implements a reduced title/ranking/history subset of this storyboard, using only text/graphics. Rarity charts, authentic skins, case-price lines, narration and transitions are **not yet delivered**.

## 3. Price data provider decision

| Source | Current use | Historical prices | Important limitation |
| --- | --- | --- | --- |
| ByMykel/CSGO-API | Catalog and skin/series mapping | None (catalog only) | Unofficial metadata; artwork rights separate |
| User-supplied/provider-authorized CSV | Supported by stage-1 compiler | Yes, if the CSV really contains observations | Importer currently assumes USD, daily observations and a source label |
| Steam market/community endpoints | Not implemented | Not implemented | Automation restrictions; no assumption of a public supported historical API |
| Licensed third-party provider, e.g. Pricempire | Research candidate only | Provider says historical service requires Enterprise tier | Paid service and access/redistribution terms require separate review |

Provider comparison links:
- https://github.com/ByMykel/CSGO-API
- https://partner.steamgames.com/doc/webapi/IEconMarketService
- https://store.steampowered.com/subscriber_agreement/
- https://pricempire.com/docs
- https://pricempire.com/api

## 4. Data semantics for future extensions

The production record should include `provider`, `market_hash_name`, `edition`, `wear`, `price_type` (listing/sale/bid/etc.), `currency`, `observed_at` with timezone, `value`, `fee_policy`, `volume`, and `source_url` or licensed feed identifier. Treat this as a future schema, NOT the current CSV format. All money comparisons require a uniform price definition and conversion convention; do not compare sale median to listing minimum, or silently mix regular, souvenir and StatTrak prices.

Missing history, unavailable variants, paused market listings and insufficient volume must be shown explicitly. Price lines require two or more genuine observations, not synthetic interpolation. Snapshots accumulated after project activation cannot substantiate older historical data. Source-attribution and extraction-time information must persist in the render report.

## 5. Verification and rollout gates

**Implemented stage-1 acceptance:** checkout main; install Manim 0.22.0; run offline unit tests; prepare one collection and one case; render both; check FFmpeg compilation with ffprobe; upload all MP4 files, report and timecodes to GitHub Actions artifacts.

**Before stage-2 (real-data) acceptance:** select and approve an authorized provider; test catalog coverage against provider identifiers; verify at least one actual collection and case; compare chosen quotes to traceable source observations; handle missing data, outliers and price definition. Preserve synthetic and live datasets as separately named runs.

**Before publishing:** verify rights to skin artwork/music, venue permissions and attribution, data-reuse terms, secret handling, production quota limits, production render duration, and user approval for paid API usage, scheduled data acquisition, GitHub Releases or third-party uploads. No auto-publishing enabled in stage 1.

## 6. Current gaps and risks

- **HIGH:** a legally and operationally suitable source for current and historic Steam market prices is unselected.
- **MEDIUM:** case special drops, Souvenir and StatTrak variants are not modeled in the first adapter.
- **MEDIUM:** video rendering at 1080p over every series may exceed runner constraints; benchmark before scheduling.
- **MEDIUM:** market-price comparability requires currency, time, listing-vs-trade definition and fee normalization.
- **LOW:** demo uses fake skins/prices and does not download protected image assets.
