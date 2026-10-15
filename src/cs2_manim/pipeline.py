# TODO: Confirm licensed price provider, rate limits, image rights and long-term retention.
# RISK: No Steam Market scraping is implemented. Synthetic data must stay labelled.
# VERIFY: Unit-test variant joins, missing prices, price order and both series types.
"""Catalog normalization and chapter preparation, using only Python stdlib."""

import argparse
import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import urllib.request

ROOT = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en"


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def catalog_from_api(collections, crates, variants):
    by_skin = defaultdict(list)
    for skin in variants:
        market = skin.get("market_hash_name")
        if market and skin.get("skin_id") and not skin.get("stattrak") and not skin.get("souvenir"):
            by_skin[skin["skin_id"]].append({
                "name": skin.get("name", market), "market_hash_name": market,
                "rarity": (skin.get("rarity") or {}).get("name", "Unknown"),
                "image": skin.get("image"),
            })

    series = []
    for kind, group in (("collection", collections), ("case", crates)):
        for entry in group:
            if kind == "case" and entry.get("type") != "Case":
                continue
            items = {}
            for member in entry.get("contains", []):
                for variant in by_skin.get(member["id"], []):
                    items[variant["market_hash_name"]] = variant
            series.append({
                "id": entry["id"], "type": kind, "name": entry["name"],
                "items": sorted(items.values(), key=lambda x: x["market_hash_name"]),
            })
    return {"schema_version": 1, "dataset_type": "catalog",
            "source": "ByMykel/CSGO-API metadata", "series": series}


def fetch_catalog(output):
    documents = []
    for name in ("collections", "crates", "skins_not_grouped"):
        request = urllib.request.Request(f"{ROOT}/{name}.json",
                                         headers={"User-Agent": "CS2-Manim/0.1 catalog reader"})
        with urllib.request.urlopen(request, timeout=30) as response:
            documents.append(json.load(response))
    result = catalog_from_api(*documents)
    save(output, result)
    print(f"Saved {len(result['series'])} collection/case series to {output}")


def load_prices(path):
    prices = defaultdict(list)
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fields = {"market_hash_name", "observed_at", "price_usd", "source"}
        if not fields.issubset(reader.fieldnames or []):
            raise ValueError(f"Expected CSV columns: {sorted(fields)}")
        for row in reader:
            day = date.fromisoformat(row["observed_at"]).isoformat()
            amount = Decimal(row["price_usd"])
            if not amount.is_finite() or amount < 0 or not row["source"].strip():
                raise ValueError("Price must be finite, nonnegative and sourced")
            prices[row["market_hash_name"]].append({
                "observed_at": day, "price_usd": float(amount),
                "source": row["source"].strip(),
            })
    for records in prices.values():
        records.sort(key=lambda x: x["observed_at"])
    return prices


def chapters_from_data(catalog, prices, max_series=2, max_items=5, ids=None):
    if catalog.get("schema_version") != 1:
        raise ValueError("Unsupported catalog schema")
    result = []
    for item in catalog["series"]:
        if ids and item["id"] not in ids:
            continue
        variants = []
        for skin in item["items"]:
            history = prices.get(skin["market_hash_name"], [])
            variants.append({
                "name": skin["name"], "rarity": skin.get("rarity", "Unknown"),
                "market_hash_name": skin["market_hash_name"],
                "history": history,
                "latest_usd": history[-1]["price_usd"] if history else None,
            })
        variants.sort(key=lambda v: (v["latest_usd"] is None,
                       -(v["latest_usd"] or 0), v["market_hash_name"]))
        result.append({
            "id": item["id"], "kind": item["type"], "title": item["name"],
            "demo": catalog.get("dataset_type") == "demo",
            "source": catalog.get("source", "unknown"),
            "total_variants": len(variants), "items": variants[:max_items],
        })
        if len(result) >= max_series:
            break
    if not result:
        raise ValueError("No matching series")
    return result


def prepare(catalog, prices, output, max_series=2, max_items=5, ids=""):
    if max_series < 1 or max_items < 1:
        raise ValueError("Limits must be positive")
    out = Path(output)
    chapters = chapters_from_data(read(catalog), load_prices(prices), max_series,
                                  max_items, set(ids.split(",")) if ids else None)
    manifest = {"schema_version": 1, "chapters": []}
    for index, chapter in enumerate(chapters):
        slug = f"chapter_{index:03d}_{chapter['kind']}"
        save(out / f"{slug}.json", chapter)
        manifest["chapters"].append({
            "slug": slug, "data_file": f"{slug}.json",
            "title": chapter["title"], "kind": chapter["kind"],
        })
    save(out / "manifest.json", manifest)
    print(f"Prepared {len(chapters)} chapters")


def main():
    parser = argparse.ArgumentParser(description="CS2-Manim data pipeline")
    sub = parser.add_subparsers(dest="task", required=True)
    fetch = sub.add_parser("fetch-catalog")
    fetch.add_argument("--output", default="build/catalog.json")
    prep = sub.add_parser("prepare")
    prep.add_argument("--catalog", default="data/demo/catalog.json")
    prep.add_argument("--prices", default="data/demo/prices.csv")
    prep.add_argument("--output", default="build")
    prep.add_argument("--max-series", type=int, default=2)
    prep.add_argument("--max-items", type=int, default=5)
    prep.add_argument("--ids", default="")
    args = parser.parse_args()
    if args.task == "fetch-catalog":
        fetch_catalog(args.output)
    else:
        prepare(args.catalog, args.prices, args.output,
                args.max_series, args.max_items, args.ids)


if __name__ == "__main__":
    main()
