# TODO: Verify typography at 1080p and add appropriately licensed skin images.
# RISK: Synthetic fixture prices are for renderer validation only, not trading.
# VERIFY: Both collection and case scenes render, including absent history.
"""One deterministic market-series chapter: title, ranking and history."""

import json
import os
from pathlib import Path

from manim import (
    BLUE_C, Create, Dot, FadeIn, FadeOut, GrowFromEdge, LEFT, Line,
    Rectangle, Scene, Text, VGroup, WHITE, YELLOW,
)

BG = "#101723"
ACCENT = "#5CD3D4"


def caption(value, size, width=12):
    text = Text(str(value), font="DejaVu Sans", font_size=size, color=WHITE)
    if text.width > width:
        text.scale_to_fit_width(width)
    return text


class MarketChapter(Scene):
    def construct(self):
        info = json.loads(Path(os.environ["CS2_CHAPTER_FILE"]).read_text(encoding="utf-8"))
        self.camera.background_color = BG
        kind = "WEAPON COLLECTION" if info["kind"] == "collection" else "WEAPON CASE"
        banner = caption(f"CS2 MARKET MOTION  /  {kind}", 25)
        banner.move_to((0, 3.2, 0))
        title = caption(info["title"], 40, 12)
        title.move_to((0, 2.5, 0))
        note = caption(f"{info['total_variants']} normal wear variants  |  USD", 22)
        note.move_to((0, 1.9, 0))
        self.play(FadeIn(banner), FadeIn(title), FadeIn(note), run_time=0.9)
        self.wait(0.3)
        self.play(FadeOut(note), run_time=0.2)

        listed = info["items"]
        priced = [item for item in listed if item["latest_usd"] is not None]
        maximum = max((item["latest_usd"] for item in priced), default=1) or 1
        rows = VGroup()
        for position, item in enumerate(listed[:5]):
            y = 1.15 - position * 0.72
            name = caption(item["name"], 16, 8)
            name.move_to((-1.7, y + 0.18, 0))
            value = item["latest_usd"]
            price = caption(f"USD {value:,.2f}" if value is not None else "NO PRICE DATA", 18, 3)
            price.move_to((4.85, y - 0.12, 0))
            length = max(0.08, (value or 0) / maximum * 6)
            bar = Rectangle(width=length, height=0.18, color=BLUE_C, fill_opacity=0.8,
                            stroke_width=0)
            bar.move_to((-4.9 + length / 2, y - 0.15, 0))
            rows.add(name, bar, price)
        self.play(FadeIn(rows), run_time=0.8)
        self.wait(0.8)

        self.play(FadeOut(rows), run_time=0.35)
        history_item = next((item for item in listed if len(item["history"]) >= 2), None)
        if history_item is not None:
            history = history_item["history"]
            chart_title = caption("PRICE HISTORY  /  " + history_item["name"], 24)
            chart_title.move_to((0, 1.4, 0))
            amounts = [point["price_usd"] for point in history]
            bottom, top = min(amounts), max(amounts)
            span = top - bottom
            coords = [
                (-5 + 10 * index / (len(history) - 1),
                 -1.45 + (amount - bottom) / span * 2.0 if span else -0.45, 0)
                for index, amount in enumerate(amounts)
            ]
            graph = VGroup(*[Line(a, b, color=ACCENT, stroke_width=5)
                             for a, b in zip(coords, coords[1:])])
            dots = VGroup(*[Dot(point, color=ACCENT, radius=0.06) for point in coords])
            period = caption(
                f"{history[0]['observed_at']}  to  {history[-1]['observed_at']} "
                f"| USD {amounts[0]:,.2f} -> USD {amounts[-1]:,.2f}", 19)
            period.move_to((0, -2.4, 0))
            self.play(FadeIn(chart_title), Create(graph), FadeIn(dots),
                      FadeIn(period), run_time=1.4)
        else:
            empty = caption("HISTORICAL PRICES UNAVAILABLE", 28)
            empty.move_to((0, -0.3, 0))
            self.play(FadeIn(empty), run_time=0.7)
        source = "SYNTHETIC DEMO / NOT STEAM PRICES" if info["demo"] else "SOURCE: " + info["source"]
        label = caption(source, 17)
        label.move_to((0, -3.2, 0))
        self.play(FadeIn(label), run_time=0.3)
        self.wait(0.8)
