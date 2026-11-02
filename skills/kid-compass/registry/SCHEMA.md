# Registry format

The registry is the part of kid-compass that the community builds. It has two kinds of files:

- `national/<id>.yaml` — one recurring programme per file (competitions, olympiads, awards, selection programmes).
- `cities/<city>.yaml` — a city pack: reputable venues and organisations that regularly run children's programmes, with the page where they list events.

Run `python scripts/validate_registry.py` after any change. CI runs it on every pull request.

## Programme file (`national/<id>.yaml`)

```yaml
id: inspire-manak                      # kebab-case; must match the file name
name: INSPIRE Awards – MANAK
organiser: Department of Science & Technology (DST), Government of India
interests: [science, innovation]       # from the list below
format: Child submits an original idea; shortlisted students build a model for exhibitions
level_path: [school, district, state, national]
eligibility:
  class_min: 6                          # integer or null
  class_max: 12
  age_min: null                         # integer years or null
  age_max: null
  age_as_of: null                       # e.g. "31 December of the competition year"
  boards: all                           # "all" or a short description
  boards_only: [CBSE]                   # optional; only when restricted to specific boards
  team: individual                      # individual | team | either
  details: Classes 11–12 science stream only
apply_via: school                       # parent | self | school | district | coach
cost_inr: 0                             # integer, 0 = free, null = varies/unknown
reward: ₹10,000 to about 1 lakh shortlisted students
window:
  opens_month: 7                        # 1–12 or null
  closes_month: 9
  closes_day: null                      # optional fixed day, e.g. 31 for "every 31 October"
  opens_day: null                       # optional fixed day for the opening
  last_seen_open: 2026-07-15            # most recent confirmed opening date, or null
  last_seen_close: 2026-09-15           # most recent known deadline, or null
  last_seen_close_source: official      # optional: "secondary" when the date comes only from news/third-party
                                        # pages — the scripts then say "reported", never "confirmed"
  event_months: "Dec–Feb"               # free text or null
  cycle: annual                         # annual | rolling | one-off
credibility: official                   # official | established
official_url: https://inspireawards-dst.gov.in
source_urls:
  - https://...                         # pages actually opened to verify this entry
last_verified: 2026-11-01               # date someone checked the official source
notes: Entries are submitted by the principal or an authorised teacher, not by parents.
```

### Field rules

- **Only verified facts.** Every non-null value must be supported by a page in `source_urls`, preferably the organiser's own site. If you can't confirm something, use `null` and explain in `notes`.
- **`credibility`**: `official` = government, statutory or recognised academic body; `established` = long-running reputable organisation (NGO, society, company programme) with published rules and results. Commercial pay-to-participate contests don't belong in the registry.
- **Dates** use `YYYY-MM-DD`. `last_seen_close` is the **registration** deadline, not the event date.
- **`last_verified`** must be updated whenever someone re-checks the entry. Entries older than 12 months are flagged by the validator.

### Interest tags

`science, maths, innovation, engineering, space, environment, coding, robotics, art, writing, reading, music, dance, theatre, quiz, sports, chess, debate, entrepreneurship, social-impact, all-round`

## City pack (`cities/<city>.yaml`)

```yaml
city: bengaluru
last_verified: 2026-11-01
sources:
  - id: vitm
    name: Visvesvaraya Industrial & Technological Museum
    type: science museum
    interests: [science, engineering]
    ages: "6+"
    look_for: Weekend workshops, science shows, summer camps
    cost: low                     # free | low | paid | varies
    area: Kasturba Road
    url: https://...
    events_url: https://... or null
    notes: ...
```

City packs list venues, not individual dated events: events change weekly, venues last for decades. The skill searches each venue's events page live.
