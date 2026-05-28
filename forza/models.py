"""Data model for the tier list, plus JSON load/save.

The canonical data lives in ``data/cars.json``. On first run it is seeded from
``forza.seed``. Refreshes (``forza.search``) update the JSON in place and append
to ``data/changelog.json`` so your edits and new metas accumulate over time.
"""

from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import dataclass, field
from typing import Optional

# --- Fixed vocabularies (FH6) ------------------------------------------------

# Ordered worst -> best so sorting/colouring is consistent.
CAR_CLASSES = ["D", "C", "B", "A", "S1", "S2", "R"]

DISCIPLINES = [
    "Road & Street",
    "Drag & Top Speed",
    "Drift",
    "Dirt & Rally",
    "Cross-Country",
]

CONFIDENCE_LEVELS = ["Strong", "Moderate", "Tentative"]

# Tier-band colours (ARGB hex, no leading '#') used by the workbook.
CLASS_COLORS = {
    "R": "B10DC9",   # purple — track prototypes / factory race cars
    "S2": "FF4136",  # red
    "S1": "FF851B",  # orange
    "A": "FFD400",   # yellow
    "B": "2ECC40",   # green
    "C": "0074D9",   # blue
    "D": "9AA5B1",   # grey
}

CONFIDENCE_COLORS = {
    "Strong": "2ECC40",    # green
    "Moderate": "FFC400",  # amber
    "Tentative": "FF4136",  # red
}

# Rank order for "best in class" sorting.
def class_rank(car_class: str) -> int:
    try:
        return CAR_CLASSES.index(car_class)
    except ValueError:
        return -1


@dataclass
class Car:
    """One ranked car within a discipline."""

    name: str
    discipline: str
    car_class: str
    rank: int = 99                       # 1 = best pick in its discipline/class block
    year: Optional[int] = None
    pi: str = ""                         # e.g. "S2 ~850" or "999"
    price_cr: Optional[int] = None       # credits; None = not purchasable for credits
    acquisition: str = "Autoshow"        # how you get it
    confidence: str = "Moderate"
    strengths: str = ""
    weaknesses: str = ""
    notes: str = ""
    sources: str = ""                    # comma-separated source names
    # Tuning
    tune_summary: str = ""               # car-specific tune tweaks (plain English)
    share_code: str = ""                 # in-game share code, if a verified one exists
    code_status: str = ""                # provenance / "verify in-game" / "no public code"

    def display_name(self) -> str:
        return f"{self.year} {self.name}".strip() if self.year else self.name

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Car":
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


# --- Persistence -------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
CARS_PATH = os.path.join(DATA_DIR, "cars.json")
CHANGELOG_PATH = os.path.join(DATA_DIR, "changelog.json")


def load_cars(path: str = CARS_PATH) -> list[Car]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [Car.from_dict(d) for d in raw["cars"]]


def save_cars(cars: list[Car], meta: dict, path: str = CARS_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"meta": meta, "cars": [c.to_dict() for c in cars]}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def load_meta(path: str = CARS_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["meta"]


def load_changelog(path: str = CHANGELOG_PATH) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def append_changelog(entries: list[dict], path: str = CHANGELOG_PATH) -> None:
    log = load_changelog(path)
    log.extend(entries)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)
