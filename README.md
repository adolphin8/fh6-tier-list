# Forza Horizon 6 — Tier List Agent

A free, on-demand tool that turns curated + web-sourced meta data into a
**polished, sortable Excel tier list** for Forza Horizon 6, and can **scan the
web** (blogs, Reddit, guide sites) for new metas and tunes whenever you run it.

> Note: the data is **Forza Horizon 6** (open-world, Japan map, released
> 2026‑05‑19), despite the repo name `Forza6Cars`.

---

## Just want to see it? (works on your phone)

Open **[`output/FH6_Tier_List.xlsx`](output/FH6_Tier_List.xlsx)** in this repo and
download it. It opens in Excel, Google Sheets, Numbers, or the free mobile Excel
app. No setup needed — it's the generated result.

The workbook has six tabs:

| Sheet | What's in it |
|---|---|
| **Overview** | What this is, the confidence key, class‑tier colour legend, PI bands. |
| **Tier List** | Every ranked car. **Tap the filter arrows** to sort by class, price, confidence, or discipline. Class and confidence cells are colour‑coded. |
| **Quick Reference** | A discipline × class grid — the top pick in each cell. |
| **Tuning** | Per‑discipline baseline setups, the new **Mechanical Balance** stat, per‑car tune notes, and **how to get real codes in‑game**. |
| **Sources** | What was cross‑referenced, and which low‑quality sites to distrust. |
| **Changelog** | Auto‑appended every time you run a web refresh. |

---

## About tune share codes (please read)

You asked for tuning codes. Here's the honest situation, carried over from the
original guide and verified by the sources:

- **Working FH6 tunes live inside the in‑game "Find Tuning Setups" marketplace**,
  not on the open web.
- Most websites advertising "FH6 tune codes" are **auto‑generated, invented, or
  recycled Forza Horizon 5 codes that don't transfer**.

So this tool **does not fabricate codes**. Instead it gives you, for every top car:

1. **Concrete tune specs** you can dial in yourself (tyre PSI, gearing, camber,
   ARBs, diff, brake bias) — reliable and future‑proof.
2. A **Share‑code column** that stays honest: empty with a "build in‑game" status
   until a *verified* code is found. When you run the web refresh, it can pull
   codes **only from named, reputable tuners** and tags each **"verify in‑game."**

The **Tuning** sheet also has a 4‑step recipe for grabbing real, current codes
from inside the game in under a minute.

---

## Running it yourself (free, on your own device)

You don't need any paid API. It runs 100% free using DuckDuckGo + Reddit.

### Step 1 — Install Python (one time)

- **Windows:** install from <https://www.python.org/downloads/> and tick
  **"Add Python to PATH"** during setup. Or run `winget install Python.Python.3.12`.
- **Mac:** install from python.org, or `brew install python`.
- Check it worked — open a terminal (Windows: "Command Prompt"; Mac: "Terminal")
  and run:
  ```
  python --version
  ```
  (If `python` isn't found on Mac/Linux, try `python3`.)

### Step 2 — Download this repo

On the GitHub page, click the green **Code** button → **Download ZIP**, then
unzip it. Or, if you have git: `git clone <repo-url>`.

### Step 3 — Install the dependencies (one time)

In a terminal, move into the project folder and run:

```
cd path/to/Forza6Cars
pip install -r requirements.txt
```

(On Mac/Linux use `pip3` if `pip` isn't found.)

### Step 4 — Build the tier list

```
python generate_tierlist.py
```

The Excel file appears at **`output/FH6_Tier_List.xlsx`**. Open it. Done.

### Step 5 — Refresh from the web (optional)

To scan the web for new metas/tunes and rebuild:

```
python generate_tierlist.py --refresh
```

New findings are added to the **Changelog** sheet as **proposed updates** for you
to review — they don't silently overwrite the curated rankings.

---

## Command reference

```
python generate_tierlist.py                # build from current data
python generate_tierlist.py --refresh      # web search, then build
python generate_tierlist.py --reseed       # reset to the curated seed (discards local edits)
python generate_tierlist.py --no-claude    # force free mode even if a Claude key is set
python generate_tierlist.py --out path.xlsx
```

---

## Optional "turbo mode" (Claude)

Free mode flags findings for you using keyword rules. If you want **much smarter
synthesis** — Claude reading the search results and writing structured, cited
suggestions (new top cars, rank shifts, codes from named tuners) — add a key:

```
pip install anthropic
# Windows:  set ANTHROPIC_API_KEY=sk-ant-...
# Mac/Linux: export ANTHROPIC_API_KEY=sk-ant-...
python generate_tierlist.py --refresh
```

**Cost:** roughly **$0.30–$1.50 per refresh**. Totally optional — without a key it
stays free forever.

---

## "Constantly updating" — how that actually works

A program can't run 24/7 on your own machine unless the machine is on. So this is
**on‑demand**: every time you run `--refresh`, it pulls the latest web chatter and
rebuilds. If you ever want it to update on a true schedule with no machine of your
own running, it can be wired to a free **GitHub Action** (e.g. weekly) that
regenerates and commits the Excel automatically — just ask.

---

## How it's built

```
forza/
  seed.py        curated FH6 dataset + tune baselines + sources
  models.py      Car data model + JSON load/save
  workbook.py    builds the styled Excel
  search.py      free web-refresh agent (+ optional Claude)
generate_tierlist.py   command-line entry point
data/            canonical data (cars.json, changelog.json) — edits accumulate here
output/          the generated FH6_Tier_List.xlsx
```
