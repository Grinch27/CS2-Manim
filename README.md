# CS2-Manim

Automatic Counter-Strike 2 weapon-collection and weapon-case market **video prototype**, built with Python, Manim Community and GitHub Actions.

**Status:** Stage-1 reproducible demonstration. The included prices and item names are deliberately fictional. This project does **not** fetch Steam Market prices, authenticate to Steam, run scheduled scraping, or publish releases.

## Outputs

The preview workflow renders:
- `chapter_000_collection.mp4`: fictional collection price ranking and price-history animation.
- `chapter_001_case.mp4`: fictional weapon-case series with the same format.
- `CS2-Market-Compilation.mp4`: concatenated video.
- `chapters.txt`: chapter timestamps; `report.json`: durations and files.
- `build/*.json`: replayable render inputs and series manifest.

Outputs are uploaded as private-to-run GitHub Actions **artifacts**, not committed to the repository or published as Releases. Download them from the [Actions tab](../../actions/workflows/video.yml).

## Local preview

Use Python 3.12 and install Manim's Linux dependencies, including `ffmpeg`, `build-essential`, `pkg-config`, `libcairo2-dev`, `libpango1.0-dev`, and `fonts-dejavu-core`.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m cs2_manim.pipeline prepare --catalog data/demo/catalog.json --prices data/demo/prices.csv --output build
python -m cs2_manim.render --manifest build/manifest.json --output dist --quality low
```

`--quality medium` or `high` gives larger outputs; start with `low` for smoke testing. CI uses the same commands. Workflow-dispatch supports manual quality selection, and pushes to `main` perform an automated demo render.

## Data contracts

The independent catalog adapter can retrieve **metadata only** (collections, crates and ordinary skin variations) from [ByMykel/CSGO-API](https://github.com/ByMykel/CSGO-API):

```bash
python -m cs2_manim.pipeline fetch-catalog --output build/catalog.json
python -m cs2_manim.pipeline prepare --catalog build/catalog.json --prices data/demo/prices.csv --output build --max-series 2
```

Catalog mode is exploratory: the synthetic demo's deliberately fictional market names do not match the real catalog, so the renderer must show missing prices, **not invent prices or substitute unrelated items**. The adapter includes only crates with `type == "Case"`, and normal, non-StatTrak, non-Souvenir variations; rare special drops, market prices of the case/container itself and image download are not implemented.

Imported price CSV requires:

```csv
market_hash_name,observed_at,price_usd,source
Example Name (Factory New),2026-10-14,12.34,AUTHORIZED_PROVIDER_NAME
```

`observed_at` is a YYYY-MM-DD observation date and `price_usd` is a nonnegative price in USD. Store original provenance outside the video too; this simple schema does not represent volume, bid/ask spread, sale counts, conversion fees, or exact observation time. Series prices rank **variants** rather than claiming a whole collection's investment value. An item without an imported price is displayed as **NO PRICE DATA**.

## Next milestones

1. Verify real catalog schema and all collection/case inventory mappings, plus coverage of rare container drops.
2. Select a market data source with clear permission to automate collection and republish derived visuals; define currency, fees, timestamps and request quotas.
3. Add licensed CS2 artwork, rarity grouping, wear normalization, image cache, case-market-price and volume/sales metrics where available.
4. Implement flexible 60–90 second chapter templates and a catalog-wide render matrix, keeping independent MP4 chapters and a timestamped compilation.
5. Establish realistic runner-minute budgets and release permissions before enabling periodic jobs, third-party uploads or production publishing.

## Usage rights and risk notes

The ByMykel catalog is unofficial. Its repository license is separate from rights to Counter-Strike/Valve media. The Steam Subscriber Agreement and any market data-provider terms must be reviewed before enabling automated market collection or redistribution. No credentials or Steam session cookies are needed for this proof of concept.

References: [CSGO-API](https://github.com/ByMykel/CSGO-API), [Manim installation](https://docs.manim.community/en/stable/installation.html), [GitHub Actions](https://docs.github.com/en/actions), [Steam Subscriber Agreement](https://store.steampowered.com/subscriber_agreement/).
