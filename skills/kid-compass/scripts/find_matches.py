#!/usr/bin/env python3
"""Find registry programmes that fit a child.

Examples:
  python scripts/find_matches.py --interests science,engineering --class 6 --age 11
  python scripts/find_matches.py --interests art --age 8 --max-cost 500 --city bengaluru
  python scripts/find_matches.py --interests maths --class 9 --json > matches.json

Filters out programmes the child is clearly not eligible for, then sorts by
interest overlap and the next registration deadline. Fields the registry
doesn't know (null) never exclude a programme; they are flagged instead.
"""
from __future__ import annotations

import argparse
import json
import sys

from registry_lib import (INTEREST_ALIASES, INTEREST_TAGS, describe_window, fmt, load_city,
                          load_programmes, next_window, parse_today, venue_age_ok)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--interests", default="", help="comma-separated interest tags, e.g. science,art")
    p.add_argument("--class", dest="klass", type=int, help="school class/grade, e.g. 6")
    p.add_argument("--age", type=int, help="age in years (cut-off dates vary; matches are flagged to check)")
    p.add_argument("--board", help="CBSE | ICSE | State | IB ... (drops board-restricted programmes for other boards)")
    p.add_argument("--max-cost", type=int, help="maximum entry fee in INR")
    p.add_argument("--apply-via", default="any", help="any | parent | self | school | district | coach (comma-separated allowed)")
    p.add_argument("--team", default="any", help="any | individual | team")
    p.add_argument("--credibility", default="any", help="any | official | established")
    p.add_argument("--city", help="also list city-pack venues matching the interests, e.g. bengaluru")
    p.add_argument("--all", action="store_true", help="ignore interests; list every eligible programme")
    p.add_argument("--today", help="YYYY-MM-DD, for testing (default: today)")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    return p.parse_args(argv)


def in_range(value, lo, hi) -> bool | None:
    """True/False when bounds exist, None when the registry doesn't say."""
    if value is None or (lo is None and hi is None):
        return None
    if lo is not None and value < lo:
        return False
    if hi is not None and value > hi:
        return False
    return True


def evaluate(entry: dict, args, wanted: set[str], today):
    elig = entry.get("eligibility") or {}
    flags = []

    class_ok = in_range(args.klass, elig.get("class_min"), elig.get("class_max"))
    age_ok = in_range(args.age, elig.get("age_min"), elig.get("age_max"))
    if class_ok is False or age_ok is False:
        return None
    if args.klass is not None and class_ok is None and age_ok is None:
        flags.append("eligibility not in registry — check")
    if age_ok is True and elig.get("age_as_of"):
        flags.append(f"age counted as of {elig['age_as_of']}")
    if elig.get("details"):
        flags.append(elig["details"])

    only = [b.lower() for b in (elig.get("boards_only") or [])]
    if only:
        if args.board and args.board.lower() not in only:
            return None
        if not args.board:
            flags.append(f"only for {', '.join(elig['boards_only'])} schools")

    cost = entry.get("cost_inr")
    if args.max_cost is not None and cost is not None and cost > args.max_cost:
        return None
    if cost is None:
        flags.append("fee varies or unknown")

    if args.apply_via != "any":
        allowed = {v.strip() for v in args.apply_via.split(",")}
        if entry.get("apply_via") not in allowed:
            return None
    if args.team != "any":
        team = elig.get("team")
        if team and team != "either" and team != args.team:
            return None
    if args.credibility != "any" and entry.get("credibility") != args.credibility:
        return None

    tags = set(entry.get("interests") or [])
    overlap = sorted(tags & wanted)
    if wanted and not overlap and not args.all:
        return None

    nw = next_window(entry, today)
    if entry.get("apply_via") == "school":
        flags.append("school must nominate/register — draft a school nudge")
    if elig.get("team") == "team":
        flags.append("team entry — needs teammates")

    return {
        "id": entry.get("id"),
        "name": entry.get("name"),
        "organiser": entry.get("organiser"),
        "interest_overlap": overlap,
        "all_interests": sorted(tags),
        "format": entry.get("format"),
        "apply_via": entry.get("apply_via"),
        "cost_inr": cost,
        "credibility": entry.get("credibility"),
        "level_path": entry.get("level_path"),
        "window": describe_window(entry, today),
        "next_close": nw["closes"].isoformat() if nw["closes"] else None,
        "next_close_confirmed": nw["confirmed"],
        "date_quality": nw["quality"],
        "last_close_estimated": nw["last_close_estimated"],
        "next_open": nw["opens"].isoformat() if nw["opens"] else None,
        "recently_missed": nw["recently_missed"],
        "last_close": nw["last_close"].isoformat() if nw["last_close"] else None,
        "official_url": entry.get("official_url"),
        "last_verified": str(entry.get("last_verified")),
        "flags": flags,
        "file": entry.get("_path"),
    }


def main(argv=None):
    args = parse_args(argv)
    today = parse_today(args.today)
    wanted = {INTEREST_ALIASES.get(t, t) for t in
              (t.strip().lower() for t in args.interests.split(",")) if t}
    unknown = wanted - INTEREST_TAGS
    if unknown:
        print(f"note: unknown interest tags ignored: {', '.join(sorted(unknown))}", file=sys.stderr)
        print(f"      valid tags: {', '.join(sorted(INTEREST_TAGS))}", file=sys.stderr)
        wanted &= INTEREST_TAGS
    if not wanted and not args.all:
        sys.exit("give --interests (e.g. science,art) or --all")

    matches = [m for e in load_programmes() if (m := evaluate(e, args, wanted, today))]
    matches.sort(key=lambda m: (-len(m["interest_overlap"]), m["next_close"] or "9999"))

    venues = []
    if args.city:
        pack = load_city(args.city)
        if pack is None:
            print(f"note: no city pack for '{args.city}' yet — use web search (and consider contributing one)", file=sys.stderr)
        else:
            for s in pack.get("sources") or []:
                if not venue_age_ok(s.get("ages"), args.age):
                    continue
                if args.all or not wanted or set(s.get("interests") or []) & wanted:
                    venues.append(s)

    if args.json:
        print(json.dumps({"today": today.isoformat(), "programmes": matches, "city_venues": venues},
                         ensure_ascii=False, indent=2, default=str))
        return

    print(f"kid-compass matches · {fmt(today)} · {len(matches)} programme(s)\n")
    for m in matches:
        fee = "Free" if m["cost_inr"] == 0 else (f"₹{m['cost_inr']:,}" if m["cost_inr"] else "fee: check")
        print(f"• {m['name']}  [{m['id']}]")
        print(f"  {m['organiser']} · {m['credibility']} · apply via {m['apply_via']} · {fee}")
        shown = m["interest_overlap"] or m["all_interests"]
        print(f"  interests: {', '.join(shown)} · path: {' → '.join(m['level_path'] or [])}")
        print(f"  window: {m['window']}")
        if m["recently_missed"]:
            est = " (estimated — no published date)" if m["last_close_estimated"] else ""
            print(f"  ! last deadline {m['last_close']}{est} has passed — show under 'Missed it?'")
        for f in m["flags"]:
            print(f"  - {f}")
        print(f"  {m['official_url']}  (verified {m['last_verified']})\n")
    if venues:
        print(f"City venues ({args.city}):")
        for v in venues:
            print(f"• {v.get('name')} — {v.get('look_for')} [{v.get('cost') or '?'}] {v.get('events_url') or v.get('url')}")
    if not matches:
        print("No registry programmes match. Use web search (references/finding-local-events.md).")


if __name__ == "__main__":
    main()
