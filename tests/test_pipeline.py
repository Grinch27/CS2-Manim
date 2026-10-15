# TODO: Add provider contract tests when an approved real-price source is selected.
# RISK: Test fixture prices are fabricated and must never be presented as quotes.
# VERIFY: Execute with 'python -m unittest discover -s tests -v'.
"""Offline pipeline tests; no market HTTP requests or credentials are used."""

import tempfile
import unittest
from pathlib import Path

from cs2_manim.pipeline import (
    catalog_from_api, chapters_from_data, load_prices, prepare, read,
)


class CatalogTests(unittest.TestCase):
    def test_collection_and_only_weapon_cases(self):
        variants = [
            {"skin_id": "skin-1", "name": "Rifle FN",
             "market_hash_name": "Rifle FN", "stattrak": False,
             "souvenir": False, "rarity": {"name": "Covert"}},
            {"skin_id": "skin-1", "name": "StatTrak Rifle FN",
             "market_hash_name": "StatTrak Rifle FN", "stattrak": True},
        ]
        grouped = [{"id": "skin-1"}]
        source = catalog_from_api(
            [{"id": "collection-1", "name": "Collection", "contains": grouped}],
            [{"id": "crate-1", "type": "Case", "name": "Case", "contains": grouped},
             {"id": "crate-2", "type": "Capsule", "name": "Capsule"}], variants)
        self.assertEqual([item["type"] for item in source["series"]],
                         ["collection", "case"])
        for item in source["series"]:
            self.assertEqual(len(item["items"]), 1)
            self.assertEqual(item["items"][0]["market_hash_name"], "Rifle FN")

    def test_fixture_ranking_history_and_missing_prices(self):
        catalog = read("data/demo/catalog.json")
        prices = load_prices("data/demo/prices.csv")
        self.assertEqual(len(prices["Demo Rifle | Azure (Factory New)"]), 3)
        chapters = chapters_from_data(catalog, prices)
        self.assertEqual([entry["kind"] for entry in chapters],
                         ["collection", "case"])
        self.assertTrue(all(entry["demo"] for entry in chapters))
        self.assertEqual(chapters[0]["items"][0]["latest_usd"], 128.5)
        self.assertEqual(chapters[1]["items"][0]["latest_usd"], 47.9)
        missing = chapters_from_data(
            {"schema_version": 1, "dataset_type": "catalog", "series": [
                {"id": "m", "type": "case", "name": "Missing", "items": [
                    {"name": "Not listed", "market_hash_name": "Missing item"}
                ]}
            ]}, prices)
        self.assertIsNone(missing[0]["items"][0]["latest_usd"])

    def test_preparation_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            prepare("data/demo/catalog.json", "data/demo/prices.csv", tmp)
            manifest = read(Path(tmp) / "manifest.json")
            self.assertEqual(len(manifest["chapters"]), 2)
            for entry in manifest["chapters"]:
                self.assertTrue((Path(tmp) / entry["data_file"]).is_file())


if __name__ == "__main__":
    unittest.main()
