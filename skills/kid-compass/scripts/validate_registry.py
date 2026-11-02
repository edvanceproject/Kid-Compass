#!/usr/bin/env python3
"""Validate every registry file. Exit code 1 if there are errors.

  python scripts/validate_registry.py            # errors + warnings
  python scripts/validate_registry.py --strict   # warnings count as errors
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date

from registry_lib import (APPLY_VIA, CITIES_DIR, CREDIBILITY, CYCLE, INTEREST_TAGS,
                          NATIONAL_DIR, TEAM, load_yaml, to_date)

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED = ["id", "name", "organiser", "interests", "format", "level_path", "eligibility",
            "apply_via", "cost_inr", "window", "credibility", "official_url", "source_urls",
            "last_verified"]


def check_url(value, field, errors):
    if not isinstance(value, str) or not value.startswith("https://"):
        errors.append(f"{field} must be an https:// URL (got {value!r})")


def check_programme(path, data, today, seen):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return [f"{path.name}: not a YAML mapping"], []
    for key in REQUIRED:
        if key not in data:
            errors.append(f"missing field '{key}'")
    pid = data.get("id")
    if pid:
        if not ID_RE.match(str(pid)):
            errors.append(f"id '{pid}' must be kebab-case")
        if path.stem != pid:
            errors.append(f"file name '{path.name}' must be '{pid}.yaml'")
        if pid in seen:
            errors.append(f"duplicate id '{pid}' (also in {seen[pid]})")
        seen[pid] = path.name
    bad = set(data.get("interests") or []) - INTEREST_TAGS
    if bad:
        errors.append(f"unknown interests: {sorted(bad)}")
    if not data.get("interests"):
        errors.append("interests must not be empty")
    if data.get("apply_via") not in APPLY_VIA:
        errors.append(f"apply_via must be one of {sorted(APPLY_VIA)}")
    if data.get("credibility") not in CREDIBILITY:
        errors.append(f"credibility must be one of {sorted(CREDIBILITY)}")
    cost = data.get("cost_inr")
    if cost is not None and (not isinstance(cost, int) or cost < 0):
        errors.append("cost_inr must be a non-negative integer or null")

    el = data.get("eligibility") or {}
    for k in ("class_min", "class_max", "age_min", "age_max"):
        v = el.get(k)
        if v is not None and not isinstance(v, int):
            errors.append(f"eligibility.{k} must be an integer or null")
    for lo, hi in (("class_min", "class_max"), ("age_min", "age_max")):
        if isinstance(el.get(lo), int) and isinstance(el.get(hi), int) and el[lo] > el[hi]:
            errors.append(f"eligibility.{lo} > {hi}")
    if el.get("team") not in TEAM:
        errors.append(f"eligibility.team must be one of {sorted(TEAM)}")
    if all(el.get(k) is None for k in ("class_min", "class_max", "age_min", "age_max")):
        warnings.append("no class or age bounds — matches will say 'check eligibility'")

    w = data.get("window") or {}
    if w.get("cycle") not in CYCLE:
        errors.append(f"window.cycle must be one of {sorted(CYCLE)}")
    for k in ("opens_month", "closes_month"):
        v = w.get(k)
        if v is not None and (not isinstance(v, int) or not 1 <= v <= 12):
            errors.append(f"window.{k} must be 1–12 or null")
    for k in ("opens_day", "closes_day"):
        v = w.get(k)
        if v is not None and (not isinstance(v, int) or not 1 <= v <= 31):
            errors.append(f"window.{k} must be 1–31 or null")
    src = w.get("last_seen_close_source")
    if src is not None and src not in ("official", "secondary"):
        errors.append("window.last_seen_close_source must be 'official', 'secondary' or omitted")
    bo = el.get("boards_only")
    if bo is not None and (not isinstance(bo, list) or not all(isinstance(b, str) for b in bo)):
        errors.append("eligibility.boards_only must be a list of board names or omitted")
    for k in ("last_seen_open", "last_seen_close"):
        try:
            to_date(w.get(k))
        except ValueError:
            errors.append(f"window.{k} must be YYYY-MM-DD or null")
    if w.get("cycle") == "annual" and not (w.get("closes_month") or w.get("last_seen_close")):
        warnings.append("annual programme without closes_month or last_seen_close — no deadline estimate possible")

    check_url(data.get("official_url"), "official_url", errors)
    srcs = data.get("source_urls") or []
    if not srcs:
        errors.append("source_urls must list at least one page used to verify the entry")
    for i, u in enumerate(srcs):
        check_url(u, f"source_urls[{i}]", errors)

    try:
        lv = to_date(data.get("last_verified"))
        if lv is None:
            errors.append("last_verified is required")
        elif lv > today:
            errors.append("last_verified is in the future")
        elif (today - lv).days > 365:
            warnings.append(f"last verified {lv} — more than a year ago, please re-check")
    except ValueError:
        errors.append("last_verified must be YYYY-MM-DD")
    return errors, warnings


def check_city(path, data):
    errors, warnings = [], []
    if not isinstance(data, dict) or "sources" not in data:
        return [f"{path.name}: needs 'city' and 'sources'"], []
    if data.get("city") != path.stem:
        errors.append(f"city '{data.get('city')}' must match file name '{path.stem}'")
    ids = set()
    for i, s in enumerate(data.get("sources") or []):
        where = f"sources[{i}] ({s.get('id')})"
        for k in ("id", "name", "type", "interests", "look_for", "url"):
            if not s.get(k):
                errors.append(f"{where}: missing '{k}'")
        if s.get("id") in ids:
            errors.append(f"{where}: duplicate id")
        ids.add(s.get("id"))
        bad = set(s.get("interests") or []) - INTEREST_TAGS
        if bad:
            errors.append(f"{where}: unknown interests {sorted(bad)}")
        check_url(s.get("url"), f"{where}.url", errors)
        if s.get("events_url"):
            check_url(s["events_url"], f"{where}.events_url", errors)
    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)
    today = date.today()
    seen, n_err, n_warn, n_files = {}, 0, 0, 0

    groups = [(sorted(NATIONAL_DIR.glob("*.yaml")), "programme"), (sorted(CITIES_DIR.glob("*.yaml")), "city")]
    for paths, kind in groups:
        for path in paths:
            n_files += 1
            try:
                data = load_yaml(path)
            except Exception as exc:  # YAML syntax errors
                print(f"✗ {path.name}: YAML error: {exc}")
                n_err += 1
                continue
            errs, warns = check_programme(path, data, today, seen) if kind == "programme" else check_city(path, data)
            for e in errs:
                print(f"✗ {path.parent.name}/{path.name}: {e}")
            for w in warns:
                print(f"! {path.parent.name}/{path.name}: {w}")
            n_err += len(errs)
            n_warn += len(warns)

    print(f"\n{n_files} file(s) checked · {n_err} error(s) · {n_warn} warning(s)")
    if n_err or (args.strict and n_warn):
        sys.exit(1)


if __name__ == "__main__":
    main()
