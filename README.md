# Forza Horizon 6 — Best Cars Tier List & Tuning Agent

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Cost](https://img.shields.io/badge/cost-free-brightgreen.svg)

A free, on-demand tool that turns curated + web-sourced meta data into a
**polished, sortable Excel tier list** for Forza Horizon 6 — complete with PI
bands, acquisition info, per-car tuning specs, and community share codes. It can
also **scan the web** (guide sites, Reddit) for new metas and tunes whenever you
run it.

> The data is **Forza Horizon 6** (open-world, Japan map, released 2026‑05‑19),
> despite the repo name. It is *not* Forza Motorsport 6.

---

## Preview

A ready-made snapshot lives at
**[`examples/FH6_Tier_List_sample.xlsx`](examples/FH6_Tier_List_sample.xlsx)** —
download it to see exactly what the tool produces. Opens in Excel, Google Sheets,
Numbers, or the free mobile Excel app. (Run the tool yourself for the latest data.)

The workbook has **five tabs**:

| Sheet | What's in it |
|---|---|
| **Overview** | What this is, the confidence key, class-tier colour legend, PI bands. |
| **Tier List** | Every ranked car (56+). **Use the filter arrows** to sort by class, PI, price, confidence, or discipline. Class and confidence cells are colour-coded. |
| **Quick Reference** | A discipline × class grid — the top pick in each cell. |
| **Tuning** | Per-discipline baseline setups, the new **Mechanical Balance** stat, a **Tune Codes** table with community share codes (marked `*`), per-car tune notes, and links to where codes live. |
| **Sources** | What was cross-referenced, and which low-quality sites to distrust. |

---

## Features

- **Sortable & filterable** Excel, not a static PDF — slice the meta any way you like.
- **Every discipline, every class** — Road/Street, Drag, Drift, Dirt/Rally, Cross-Country across D → R.
- **Honest confidence grading** (Strong / Moderate / Tentative) with sources cited.
- **Real tuning specs** per car (tyre PSI, gearing, camber, ARBs, diff, brake bias) — reliable even when a code goes stale.
- **Community share codes** marked `*`, never fabricated.
- **Free web refresh** ($0, no API key) with an optional Claude "turbo mode".

---

## Quick start

You don't need any paid API — it runs 100% free.

```bash
# 1. Install Python 3.10+  (Windows: python.org and tick "Add Python to PATH")
# 2. Get the code:
git clone https://github.com/adolphin8/Forza6Cars.git
cd Forza6Cars

# 3. Install dependencies (one time):
pip install -r requirements.txt        # use pip3 / python3 on macOS/Linux

# 4. Build the tier list:
python generate_tierlist.py
```

The Excel file appears at **`output/FH6_Tier_List.xlsx`** — open it. Done.

No git? On the GitHub page, click the green **Code** button → **Download ZIP**, unzip, then start from step 3.

---

## Refresh from the web (optional)

```bash
python generate_tierlist.py --refresh
```

Scans DuckDuckGo + Reddit and **prints proposed updates to the terminal** (new
cars, patch/nerf chatter, tune-code leads), then rebuilds the Excel. It
deliberately **does not auto-edit the rankings** — scraped data (especially
"codes") is too unreliable to trust blindly. Keep what's worth keeping by editing
`forza/seed.py`.

### Command reference

```bash
python generate_tierlist.py                # build from current data
python generate_tierlist.py --refresh      # web search, then build
python generate_tierlist.py --reseed       # reset to the curated seed
python generate_tierlist.py --no-claude    # force free mode even if a Claude key is set
python generate_tierlist.py --out path.xlsx
```

### Optional "turbo mode" (Claude)

Free mode flags findings with keyword rules. For smarter, cited synthesis, add a key:

```bash
pip install anthropic
# Windows:   set ANTHROPIC_API_KEY=sk-ant-...
# macOS/Linux: export ANTHROPIC_API_KEY=sk-ant-...
python generate_tierlist.py --refresh
```

Cost is roughly **$0.30–$1.50 per refresh**. Without a key it stays free forever.

---

## About tune share codes

The **Tuning** sheet has a **Tune Codes** table with community-sourced share codes
(e.g. from Dexerto), each marked `*`. The `*` means: community-sourced, **not
verified — enter it in-game and confirm before trusting it**. Codes are never
fabricated.

Most sites that host FH6 codes block automated reading, so codes are added by hand
(from screenshots) plus whatever the refresh can pull. Working FH6 codes ultimately
live **in-game** under *Find Tuning Setups* — the Tuning sheet links straight to the
best sources and explains how to grab top-rated tunes in under a minute.

---

## "Constantly updating" — how it works

It's **on-demand**: each `--refresh` pulls the latest web chatter and rebuilds. A
program can't run 24/7 on your own machine, so for true hands-off updates it can be
wired to a free scheduled **GitHub Action** — open an issue if you want that.

---

## Project structure

```
forza/
  seed.py        curated FH6 dataset + tune baselines + codes + sources (source of truth)
  models.py      Car data model + JSON load/save
  workbook.py    builds the styled Excel
  search.py      free web-refresh agent (+ optional Claude)
generate_tierlist.py   command-line entry point
examples/        a committed sample workbook (preview)
data/, output/   generated locally on each run (gitignored)
```

All curated data lives in `forza/seed.py`. `data/` and `output/` are regenerated on
every run and are never committed.

---

## Contributing

Issues and pull requests welcome — especially:

- **New/updated tune codes** → add an entry to `TUNE_CODES` in `forza/seed.py`.
- **Meta corrections** (rankings, PI, prices) → edit `SEED_CARS` in `forza/seed.py`.

Please cite a source for ranking changes, and never add fabricated share codes.

---

## License

[MIT](LICENSE) — free to use, modify, and share with attribution.

This is an unofficial fan-made project, not affiliated with or endorsed by
Microsoft, Xbox Game Studios, Playground Games, or the Forza franchise. Car
rankings are community opinion compiled from public sources.
