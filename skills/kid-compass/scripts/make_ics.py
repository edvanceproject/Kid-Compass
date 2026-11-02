#!/usr/bin/env python3
"""Create a calendar (.ics) file with registration reminders for chosen programmes.

Each programme gets an all-day event on its (next) registration deadline, an
event on the estimated opening date when that is still ahead, and alarms
before the deadline. Estimated dates are labelled inside the event so nobody
mistakes them for confirmed ones.

Examples:
  python scripts/make_ics.py --ids inspire-manak,ncsc --out reminders.ics
  python scripts/make_ics.py --from-json matches.json --reminder-days 14,7,1
  python scripts/make_ics.py --custom "Science fair at school|2026-12-05|https://example.org"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from registry_lib import load_programmes, next_window, parse_today, to_date


def esc(text: str) -> str:
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def fold(line: str) -> str:
    """Fold lines longer than 75 octets, as RFC 5545 requires."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    parts, chunk = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(chunk) + len(b) > (75 if not parts else 74):
            parts.append(chunk.decode("utf-8"))
            chunk = b""
        chunk += b
    parts.append(chunk.decode("utf-8"))
    return "\r\n ".join(parts)


def event(uid: str, day, summary: str, description: str, url: str | None, alarms: list[int]) -> list[str]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{stamp}",
        f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{(day + timedelta(days=1)).strftime('%Y%m%d')}",
        f"SUMMARY:{esc(summary)}",
        f"DESCRIPTION:{esc(description)}",
    ]
    if url:
        lines.append(f"URL:{url}")
    for d in alarms:
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(summary)}",
                  f"TRIGGER:-P{d}D", "END:VALARM"]
    lines.append("END:VEVENT")
    return lines


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ids", default="", help="comma-separated registry ids")
    p.add_argument("--from-json", help="JSON produced by find_matches.py --json (uses all programmes in it)")
    p.add_argument("--custom", action="append", default=[],
                   help='extra event "Title|YYYY-MM-DD|url" (repeatable), e.g. a local event found by search')
    p.add_argument("--reminder-days", default="7,1", help="alarms before each deadline, in days")
    p.add_argument("--out", default="kid-compass-reminders.ics")
    p.add_argument("--today", help="YYYY-MM-DD, for testing")
    args = p.parse_args(argv)

    today = parse_today(args.today)
    alarms = [int(x) for x in args.reminder_days.split(",") if x.strip()]
    ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    if args.from_json:
        data = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        ids += [m["id"] for m in data.get("programmes", [])]

    registry = {e.get("id"): e for e in load_programmes()}
    missing = [i for i in ids if i not in registry]
    if missing:
        print(f"warning: not in registry, skipped: {', '.join(missing)}", file=sys.stderr)

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//BrainyDarts//kid-compass//EN",
             "CALSCALE:GREGORIAN", "X-WR-CALNAME:kid-compass reminders"]
    count = 0
    for pid in dict.fromkeys(i for i in ids if i in registry):
        e = registry[pid]
        nw = next_window(e, today)
        if not nw["closes"]:
            print(f"note: {pid} has no known window — no event created", file=sys.stderr)
            continue
        status = {"confirmed": "confirmed on the official site",
                  "reported": "REPORTED in news, not yet confirmed on the official site — verify",
                  "estimated": "ESTIMATED from last year's cycle — verify on the official site"}[nw["quality"]]
        route = e.get("apply_via")
        how = "The school must submit the entry — talk to the class teacher early." if route == "school" else f"Apply via: {route}."
        desc = f"{e.get('organiser')}. Deadline {status}. {how} {e.get('official_url')}"
        # Schools set their own earlier cut-off, so school-route programmes get a month's notice too.
        close_alarms = sorted(set(alarms + ([30] if route == "school" else [])), reverse=True)
        lines += event(f"{pid}-close-{nw['closes'].isoformat()}@kid-compass", nw["closes"],
                       f"Last date: {e.get('name')}", desc, e.get("official_url"), close_alarms)
        count += 1
        if nw["opens"] and nw["opens"] > today:
            lines += event(f"{pid}-open-{nw['opens'].isoformat()}@kid-compass", nw["opens"],
                           f"Registration opens (est.): {e.get('name')}",
                           f"Expected opening, estimated from last cycle — verify. {e.get('official_url')}",
                           e.get("official_url"), [])
            count += 1

    for spec in args.custom:
        try:
            title, day, *rest = spec.split("|")
            d = to_date(day.strip())
        except ValueError:
            sys.exit(f'bad --custom value: {spec!r} (use "Title|YYYY-MM-DD|url")')
        url = rest[0].strip() if rest else None
        # Stable UID (same title + date → same event), so re-importing updates instead of duplicating.
        digest = hashlib.sha1(f"{title.strip()}|{d.isoformat()}".encode("utf-8")).hexdigest()[:12]
        lines += event(f"custom-{d.isoformat()}-{digest}@kid-compass", d, title.strip(),
                       f"Added from kid-compass. Confirm details with the organiser. {url or ''}", url, alarms)
        count += 1

    lines.append("END:VCALENDAR")
    Path(args.out).write_text("\r\n".join(fold(l) for l in lines) + "\r\n", encoding="utf-8")
    print(f"wrote {count} event(s) to {args.out}")


if __name__ == "__main__":
    main()
