#!/usr/bin/env python3
"""List registration deadlines coming up in the next N days, plus recently missed ones.

Examples:
  python scripts/upcoming.py                      # next 90 days, all programmes
  python scripts/upcoming.py --days 60 --interests maths,science
  python scripts/upcoming.py --class 8
"""
from __future__ import annotations

import argparse
from datetime import timedelta

from registry_lib import date_tag, fmt, load_programmes, next_window, parse_today


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--interests", default="", help="comma-separated tags to filter by")
    p.add_argument("--class", dest="klass", type=int)
    p.add_argument("--today", help="YYYY-MM-DD, for testing")
    args = p.parse_args(argv)

    today = parse_today(args.today)
    horizon = today + timedelta(days=args.days)
    wanted = {t.strip() for t in args.interests.split(",") if t.strip()}

    coming, missed = [], []
    for e in load_programmes():
        if wanted and not wanted & set(e.get("interests") or []):
            continue
        el = e.get("eligibility") or {}
        if args.klass is not None:
            lo, hi = el.get("class_min"), el.get("class_max")
            if (lo is not None and args.klass < lo) or (hi is not None and args.klass > hi):
                continue
        nw = next_window(e, today)
        if nw["closes"] and nw["closes"] <= horizon:
            coming.append((nw["closes"], e, nw))
        if nw["recently_missed"]:
            missed.append((nw["last_close"], e, nw))

    print(f"Deadlines from {fmt(today)} to {fmt(horizon)}:")
    if not coming:
        print("  none in the registry — check city venues and web search")
    for closes, e, nw in sorted(coming, key=lambda x: x[0]):
        tag = date_tag(nw)
        opens = f" (opens ~{fmt(nw['opens'])})" if nw["opens"] and nw["opens"] > today else ""
        print(f"  {fmt(closes):>12}  {e['name']} — {tag}{opens} · apply via {e.get('apply_via')} · {e.get('official_url')}")

    if missed:
        print("\nRecently closed (plan for the next cycle):")
        for last, e, nw in sorted(missed, key=lambda x: x[0]):
            nxt = f"next expected ~{fmt(nw['closes'])}" if nw["closes"] else "next cycle: check the site"
            when = f"~{fmt(last)} (estimated)" if nw["last_close_estimated"] else fmt(last)
            print(f"  closed {when}  {e['name']} — {nxt}")


if __name__ == "__main__":
    main()
