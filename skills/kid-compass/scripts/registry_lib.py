"""Shared helpers for the kid-compass scripts: load the registry and work out windows.

Python 3.9+, needs PyYAML (pip install pyyaml).
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

SKILL_DIR = Path(__file__).resolve().parent.parent
REGISTRY_DIR = SKILL_DIR / "registry"
NATIONAL_DIR = REGISTRY_DIR / "national"
CITIES_DIR = REGISTRY_DIR / "cities"

INTEREST_TAGS = {
    "science", "maths", "innovation", "engineering", "space", "environment",
    "coding", "robotics", "art", "writing", "reading", "music", "dance",
    "theatre", "quiz", "sports", "chess", "debate", "entrepreneurship",
    "social-impact", "all-round",
}
# Everyday words parents use, mapped to registry tags.
INTEREST_ALIASES = {
    "comics": "art", "comic": "art", "drawing": "art", "painting": "art", "sketching": "art",
    "illustration": "art", "craft": "art", "crafts": "art", "anime": "art", "manga": "art",
    "astronomy": "space", "stars": "space", "planets": "space",
    "programming": "coding", "computers": "coding", "apps": "coding",
    "math": "maths", "mathematics": "maths", "puzzles": "maths",
    "physics": "science", "chemistry": "science", "biology": "science", "experiments": "science",
    "building": "engineering", "lego": "engineering", "making": "engineering", "inventing": "innovation",
    "nature": "environment", "birds": "environment", "birding": "environment", "animals": "environment",
    "books": "reading", "stories": "writing", "poetry": "writing",
    "singing": "music", "acting": "theatre", "drama": "theatre",
    "trivia": "quiz", "gk": "quiz", "general-knowledge": "quiz",
    "cricket": "sports", "football": "sports", "athletics": "sports", "swimming": "sports",
    "business": "entrepreneurship", "volunteering": "social-impact", "community": "social-impact",
}

APPLY_VIA = {"parent", "self", "school", "district", "coach"}
CREDIBILITY = {"official", "established"}
TEAM = {"individual", "team", "either"}
CYCLE = {"annual", "rolling", "one-off"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def to_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def parse_today(value: str | None) -> date:
    return date.fromisoformat(value) if value else date.today()


def load_programmes() -> list[dict]:
    items = []
    for path in sorted(NATIONAL_DIR.glob("*.yaml")):
        data = load_yaml(path) or {}
        data["_path"] = str(path.relative_to(SKILL_DIR))
        items.append(data)
    return items


def load_city(city: str) -> dict | None:
    path = CITIES_DIR / f"{city.strip().lower()}.yaml"
    return load_yaml(path) if path.exists() else None


def fmt(d: date | None) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}" if d else "?"


def _safe_date(year: int, month: int, day: int) -> date:
    # Clamp the day so 29-31 never breaks in short months.
    for d in (day, 30, 29, 28):
        try:
            return date(year, month, d)
        except ValueError:
            continue
    return date(year, month, 28)


def next_window(entry: dict, today: date) -> dict:
    """Best estimate of the next registration window.

    Returns a dict with:
      opens, closes   – dates or None
      quality         – confirmed (future deadline from the official source)
                        | reported (future deadline from news/secondary sources only)
                        | estimated (projected from the last cycle)
      confirmed       – True only when quality == confirmed
      status          – open | upcoming | open-or-upcoming | rolling | unknown
      last_close      – the most recent known deadline (may be in the past)
      last_close_estimated – True when last_close is itself an estimate (no published date)
      recently_missed – True when the last (known or estimated) deadline passed within 120 days
    """
    w = entry.get("window") or {}
    cycle = w.get("cycle")
    last_close = to_date(w.get("last_seen_close"))
    last_open = to_date(w.get("last_seen_open"))
    secondary = w.get("last_seen_close_source") == "secondary"
    result = {"opens": None, "closes": None, "confirmed": False, "quality": "estimated",
              "status": "unknown", "last_close": last_close, "last_close_estimated": False,
              "recently_missed": False}

    if cycle == "rolling":
        result["status"] = "rolling"
        return result

    if last_close and last_close >= today:
        closes = last_close
        result["quality"] = "reported" if secondary else "confirmed"
        result["confirmed"] = not secondary
    else:
        month = last_close.month if last_close else w.get("closes_month")
        if not month:
            return result
        day = last_close.day if last_close else (w.get("closes_day") or 15)
        closes = _safe_date(today.year, month, day)
        if closes < today:
            closes = _safe_date(today.year + 1, month, day)
        if cycle == "one-off":
            return result
    result["closes"] = closes

    if last_close and last_close < today and (today - last_close).days <= 120:
        result["recently_missed"] = True
    elif not last_close and result["quality"] == "estimated":
        # No published date: the same window a year earlier may have just passed.
        prev = _safe_date(closes.year - 1, closes.month, closes.day)
        if prev < today and (today - prev).days <= 120:
            result.update(recently_missed=True, last_close=prev, last_close_estimated=True)

    open_month = last_open.month if last_open else w.get("opens_month")
    if open_month:
        open_day = last_open.day if last_open else (w.get("opens_day") or 1)
        opens = _safe_date(closes.year, open_month, open_day)
        if opens > closes:
            opens = _safe_date(closes.year - 1, open_month, open_day)
        if result["quality"] != "estimated" and last_open and last_open <= closes:
            opens = last_open
        result["opens"] = opens

    opens = result["opens"]
    if opens and today < opens:
        result["status"] = "upcoming"
    elif opens and opens <= today <= closes:
        result["status"] = "open"
    elif not opens:
        result["status"] = "open-or-upcoming"
    else:
        result["status"] = "upcoming"
    return result


def venue_age_ok(ages, age: int | None) -> bool:
    """Best-effort check of a city-pack 'ages' string ("6+", "5–16", "up to 12", "15+")."""
    import re
    if age is None or not ages:
        return True
    text = str(ages).lower().replace("—", "-").replace("–", "-")
    if "month" in text and "-" in text:          # "20 months-16 years"
        text = "0-" + text.split("-", 1)[1]
    if m := re.search(r"(\d+)\s*-\s*(\d+)", text):
        return int(m.group(1)) <= age <= int(m.group(2))
    if m := re.search(r"(\d+)\s*\+", text):
        return age >= int(m.group(1))
    if m := re.search(r"up to\s*(\d+)", text):
        return age <= int(m.group(1))
    return True


def date_tag(nw: dict) -> str:
    return {"confirmed": "confirmed", "reported": "reported in news — confirm on the official site",
            "estimated": "estimated"}[nw["quality"]]


def describe_window(entry: dict, today: date) -> str:
    nw = next_window(entry, today)
    if nw["status"] == "rolling":
        return "rolling / year-round"
    if not nw["closes"]:
        return "dates not known — check the official site"
    tag = date_tag(nw)
    if nw["status"] == "open":
        return f"open now · closes {fmt(nw['closes'])} ({tag})"
    if nw["opens"] and nw["status"] == "upcoming":
        approx = "~" if nw["quality"] == "estimated" else ""
        return f"opens {approx}{fmt(nw['opens'])} · closes {approx}{fmt(nw['closes'])} ({tag})"
    return f"closes {fmt(nw['closes'])} ({tag})"
