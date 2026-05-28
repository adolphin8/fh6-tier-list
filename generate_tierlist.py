#!/usr/bin/env python3
"""Forza Horizon 6 tier-list generator.

Typical use (on your own machine, free):

    python generate_tierlist.py            # build the Excel from current data
    python generate_tierlist.py --refresh  # scan the web first, then build

The first run seeds the dataset from the curated guide. A web refresh prints any
*proposed* updates it finds to the terminal for you to review — it never silently
overwrites the curated data.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os

from forza import models, seed, search, workbook

OUTPUT_PATH = os.path.join(models.REPO_ROOT, "output", "FH6_Tier_List.xlsx")


def _seed_cars() -> list[models.Car]:
    cars = []
    for d in seed.SEED_CARS:
        car = models.Car.from_dict(d)
        if not car.share_code:
            car.share_code = seed.CODE_SOURCES.get(car.discipline, "In-game Find Tuning Setups *")
        if not car.code_status:
            car.code_status = seed.DEFAULT_CODE_STATUS
        cars.append(car)
    return cars


def _ensure_data(reseed: bool) -> tuple[list[models.Car], dict]:
    if reseed or not os.path.exists(models.CARS_PATH):
        cars = _seed_cars()
        meta = dict(seed.META)
        models.save_cars(cars, meta)
        print(f"Seeded dataset: {len(cars)} cars -> {models.CARS_PATH}")
        return cars, meta
    cars = models.load_cars()
    meta = models.load_meta()
    return cars, meta


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the FH6 Excel tier list.")
    ap.add_argument("--refresh", action="store_true",
                    help="Scan the web for meta updates before building.")
    ap.add_argument("--reseed", action="store_true",
                    help="Reset the dataset from the curated seed (discards local edits).")
    ap.add_argument("--no-claude", action="store_true",
                    help="Force free rule-based refresh even if ANTHROPIC_API_KEY is set.")
    ap.add_argument("--out", default=OUTPUT_PATH, help="Output .xlsx path.")
    args = ap.parse_args()

    cars, meta = _ensure_data(args.reseed)

    if args.refresh:
        search.refresh(cars, use_claude=not args.no_claude)
        meta["last_updated"] = _dt.date.today().isoformat()
        models.save_cars(cars, meta)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    path = workbook.build_workbook(cars, meta, args.out)
    print(f"Built tier list: {path}")
    print(f"  {len(cars)} cars across {len({c.discipline for c in cars})} disciplines.")


if __name__ == "__main__":
    main()
