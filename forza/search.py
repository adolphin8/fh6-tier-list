"""On-demand web refresh agent (free by default).

Goal: scan the live web for FH6 meta shifts and tunes, and report what's new.

DESIGN PRINCIPLE — never silently corrupt the curated data. The original guide
warned that most web "FH6 codes" are fake/auto-generated. So this agent does NOT
overwrite your dataset with scraped strings. Instead it gathers findings and
prints *proposed* updates to the terminal for you to review (and, with the Claude
upgrade, structured suggestions with citations + a "verify in-game" flag).

Tiers of capability:
  * Free (default): DuckDuckGo (via `ddgs`) + Reddit public JSON. No key, $0.
  * Turbo (optional): set ANTHROPIC_API_KEY and `pip install anthropic` to have
    Claude synthesise the gathered snippets into structured, cited suggestions.

Everything degrades gracefully: no network / missing deps just means "no findings
this run" and the workbook still builds from existing data.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from typing import Optional

from .models import Car

GAME = "Forza Horizon 6"

QUERIES = [
    f"{GAME} best cars tier list 2026",
    f"{GAME} fastest car each class",
    f"{GAME} meta nerf buff patch notes",
    f"{GAME} best drift car tune setup",
    f"{GAME} best drag car",
    f"{GAME} best rally car",
    f"{GAME} best cross country car",
    f"{GAME} tune share code",
    f"{GAME} new cars added playlist",
]

SUBREDDITS = ["ForzaHorizon", "ForzaHorizon6", "forza"]

# Keywords that hint a finding is meta-relevant enough to surface for review.
SIGNAL_WORDS = [
    "tier", "best", "meta", "patch", "update", "nerf", "buff", "fastest",
    "tune", "code", "build", "broken", "op", "season", "playlist", "festival",
]

# Substrings that mean the result is about a DIFFERENT Forza game (noise).
OTHER_GAME_MARKERS = ["horizon 5", "horizon 4", "horizon 3", "fh5", "fh4", "fh3",
                      "motorsport", "forza 7", "fm "]


def _is_other_game(text: str) -> bool:
    low = text.lower()
    if "horizon 6" in low or "fh6" in low:
        return False
    return any(m in low for m in OTHER_GAME_MARKERS)


def _classify(text: str) -> str:
    low = text.lower()
    if "code" in low:
        return "Tune-code lead"
    if any(w in low for w in ("nerf", "buff", "patch", "update", "hotfix")):
        return "Patch / meta shift"
    if any(w in low for w in ("new car", "added", "playlist", "season", "festival")):
        return "New content"
    if "tune" in low or "build" in low or "setup" in low:
        return "Tuning guide"
    return "Tier-list source"


def _today() -> str:
    return _dt.date.today().isoformat()


# --- Free search backends ----------------------------------------------------

def _search_duckduckgo(query: str, max_results: int = 6) -> list[dict]:
    try:
        from ddgs import DDGS
    except Exception:
        return []
    try:
        with DDGS() as ddgs:
            return [
                {"title": r.get("title", ""), "url": r.get("href", ""),
                 "snippet": r.get("body", ""), "via": "duckduckgo"}
                for r in ddgs.text(query, max_results=max_results)
            ]
    except Exception:
        return []


def _search_reddit(query: str, subreddit: str, limit: int = 6) -> list[dict]:
    try:
        import requests
    except Exception:
        return []
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {"q": query, "restrict_sr": 1, "sort": "new", "limit": limit, "t": "month"}
    headers = {"User-Agent": "fh6-tierlist/1.0 (personal use)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        children = resp.json().get("data", {}).get("children", [])
        out = []
        for ch in children:
            d = ch.get("data", {})
            out.append({
                "title": d.get("title", ""),
                "url": "https://www.reddit.com" + d.get("permalink", ""),
                "snippet": (d.get("selftext", "") or "")[:400],
                "via": f"reddit/{subreddit}",
            })
        return out
    except Exception:
        return []


def gather_findings(verbose: bool = True) -> list[dict]:
    """Run all free searches; return deduped findings."""
    seen: set[str] = set()
    findings: list[dict] = []

    def add(items: list[dict]):
        for it in items:
            u = it.get("url", "")
            if u and u not in seen:
                seen.add(u)
                findings.append(it)

    for q in QUERIES:
        add(_search_duckduckgo(q))
    for sub in SUBREDDITS:
        add(_search_reddit(f"{GAME} best", sub))
        add(_search_reddit(f"{GAME} tune", sub))

    if verbose:
        print(f"  gathered {len(findings)} unique web results")
    return findings


# --- Rule-based synthesis (free) --------------------------------------------

def _relevant(text: str) -> bool:
    low = text.lower()
    return any(w in low for w in SIGNAL_WORDS)


def synthesize_rulebased(findings: list[dict], cars: list[Car]) -> list[dict]:
    """Surface the most relevant findings as proposed entries, grouped by type.

    Conservative: it flags things for *you* to review; it does not edit data.
    Filters out other-Forza-game noise and ranks code/patch leads first.
    """
    priority = {"Tune-code lead": 0, "Patch / meta shift": 1, "New content": 2,
                "Tuning guide": 3, "Tier-list source": 4}
    entries: list[dict] = []
    for f in findings:
        blob = f"{f.get('title','')} {f.get('snippet','')}"
        if not _relevant(blob) or _is_other_game(blob):
            continue
        kind = _classify(blob)
        entries.append({
            "date": _today(),
            "type": kind,
            "summary": f.get("title", "")[:200],
            "source": f.get("url", ""),
            "_rank": priority.get(kind, 9),
        })
    entries.sort(key=lambda e: e.pop("_rank"))
    # Keep it digestible.
    return entries[:25]


# --- Optional Claude synthesis (turbo) --------------------------------------

def synthesize_claude(findings: list[dict], cars: list[Car]) -> Optional[list[dict]]:
    """Use Claude to turn raw findings into structured, cited suggestions.

    Returns None if the optional dependency / key is unavailable, so the caller
    can fall back to the rule-based path.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except Exception:
        print("  (ANTHROPIC_API_KEY set but `anthropic` not installed — run: pip install anthropic)")
        return None

    known = sorted({c.display_name() for c in cars})
    corpus = "\n".join(
        f"- {f.get('title','')} :: {f.get('snippet','')[:300]} :: {f.get('url','')}"
        for f in findings[:60]
    )
    prompt = (
        f"You are maintaining a {GAME} car tier list. Below are web search results.\n"
        f"Cars already tracked:\n{', '.join(known)}\n\n"
        f"Search results:\n{corpus}\n\n"
        "Identify genuine meta changes ONLY (new top cars, rank shifts, confirmed "
        "patch/nerf/buff, or tune share codes posted by NAMED reputable tuners). "
        "Ignore SEO-farm sites and any fabricated 'telemetry'. For share codes, never "
        "invent them and always mark them 'verify in-game'. "
        "Return STRICT JSON: a list of objects with keys "
        "{date, type, summary, source}. type is one of "
        "'New car','Rank change','Patch','Tune code','Note'. "
        "Keep summary under 160 chars. If nothing credible, return []."
    )
    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        start, end = text.find("["), text.rfind("]")
        if start == -1 or end == -1:
            return []
        data = json.loads(text[start:end + 1])
        out = []
        for d in data:
            if isinstance(d, dict) and d.get("summary"):
                out.append({
                    "date": d.get("date") or _today(),
                    "type": "Claude: " + str(d.get("type", "Note")),
                    "summary": str(d.get("summary"))[:200],
                    "source": str(d.get("source", "")),
                })
        return out
    except Exception as exc:  # noqa: BLE001 - network/API errors shouldn't crash a build
        print(f"  (Claude synthesis failed: {exc})")
        return None


# --- Entry point -------------------------------------------------------------

def refresh(cars: list[Car], use_claude: bool = True) -> list[dict]:
    """Scan the web and PRINT any proposed updates for the user to review.

    Deliberately does not edit the dataset — scraped strings (especially "tune
    codes") are too unreliable to apply automatically. You read the proposals and
    decide what to fold into forza/seed.py.
    """
    print("Refreshing from the web (free search)...")
    findings = gather_findings()
    if not findings:
        print("  No web results (offline, rate-limited, or deps missing). "
              "Existing data is unchanged.")
        return []

    entries = None
    if use_claude:
        entries = synthesize_claude(findings, cars)
        if entries is not None:
            print(f"  Claude synthesised {len(entries)} structured suggestion(s).")
    if entries is None:
        entries = synthesize_rulebased(findings, cars)
        print(f"  Flagged {len(entries)} finding(s) for review (rule-based).")

    print(f"\n--- Proposed updates ({len(entries)}) — review, then edit forza/seed.py ---")
    if not entries:
        print("  Nothing meta-relevant surfaced this run.")
    for e in entries:
        line = f"  [{e.get('type','')}] {e.get('summary','')}"
        if e.get("source"):
            line += f"\n      {e['source']}"
        print(line)
    print("--- end proposed updates ---\n")
    return entries
