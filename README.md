# Kid Compass

**Kid Compass** is a [Claude Skill](https://docs.claude.com/en/docs/claude-code/skills) that helps parents, guardians and teachers in India find the right competitions, olympiads, programmes, camps, workshops, exhibitions and events for a child — based on the child's interests, age, class, city, budget and schedule.

It turns what a parent knows about their child into an **opportunity map**: things to try this weekend, deadlines coming up this term, and a level-by-level growth path ("ladder") for each of the child's strongest interests.

## Why it exists

Parents usually find out about good opportunities by accident, often after the deadline — and many of the best national programmes in India run through schools rather than families. At the same time, parents are regularly sold expensive, low-value contests. Kid Compass acts as the well-informed, honest friend who keeps track of all of this, and who cares more about the child enjoying things than about medals.

It's India-first (CBSE/ICSE/State boards, national programmes, city packs) but works anywhere via web search.

## What it does

Ask it things like:

- "What should my child try? She's 11, class 6, in Bengaluru, loves building things."
- "Is this competition my friend forwarded on WhatsApp actually worth it?"
- "When's the deadline for INSPIRE Awards?"
- "Help me write a note to the school about NCSC."
- "She just did a robotics workshop, what's next?"

It responds with an honest, dated opportunity map:

1. **Sparks** — a 2–4 line interest map, grounded in what the parent actually said.
2. **This weekend / this month** — low-cost things nearby, including a free or ₹0–500 "taster" when one exists.
3. **Coming deadlines** — the next 90 days, soonest first, with registration dates and the application route.
4. **The ladder** — the path from school level to national (and beyond) for the child's top interests.
5. **Missed it?** — anything whose window just closed, with the next expected cycle.
6. **Balance check** — total hours/money per month, flagging overload and making sure there's joy as well as challenge.
7. **Next steps** — at most three concrete actions for the week.

Every date carries a status — **confirmed** (checked on the official page), **reported** (news/third-party only) or **estimated** (projected from last year) — so parents never act on a guess dressed up as a fact.

## How it's built

```
kid-compass/
├── SKILL.md                     # the skill definition Claude reads
├── references/                  # guidance Claude loads as needed
│   ├── child-safety.md          # data, privacy and tone rules
│   ├── spark-interview.md       # interview questions, "this or that" game, debrief
│   ├── fit-and-worth-it.md      # fit labels, eligibility checks, worth-it checks
│   ├── interest-ladders.md     # level-by-level paths per interest area
│   ├── finding-local-events.md # search queries + verification for local events
│   ├── output-format.md        # the opportunity map template and profile file format
│   └── school-nudge.md          # notes to teachers, in English, Hindi, Kannada
├── registry/                    # the community-maintained data
│   ├── national/*.yaml          # verified national programmes, one per file
│   ├── cities/*.yaml            # city packs of reputable venues
│   └── SCHEMA.md                # registry file format
└── scripts/
    ├── find_matches.py          # filter the registry for a specific child
    ├── upcoming.py               # list all deadlines in the next N days
    ├── make_ics.py               # generate a calendar file with reminders
    ├── validate_registry.py     # check registry files are well-formed
    └── registry_lib.py           # shared loading/parsing helpers
```

### The registry

The registry is the structured, verifiable core of the skill — one YAML file per national programme (eligibility, cost, application route, deadline windows, and whether each date is confirmed or just reported) plus a city pack per city of reputable venues that regularly run children's programmes. Every entry carries a `last_verified` date so stale information gets flagged rather than trusted blindly. See [`kid-compass/registry/SCHEMA.md`](kid-compass/registry/SCHEMA.md) for the full format.

### The scripts

The scripts need **Python 3.9+** and **PyYAML**:

```bash
pip install pyyaml
```

```bash
# Find programmes that fit a specific child
python scripts/find_matches.py --interests science,engineering --class 6 --age 11 \
    --board CBSE --max-cost 1500 --city bengaluru

# List everything with a deadline in the next 90 days
python scripts/upcoming.py --days 90 --interests science

# Build a calendar file with 7-day and 1-day reminders
python scripts/make_ics.py --ids inspire-manak,ncsc --out kid-compass-reminders.ics

# Validate the registry after editing it
python scripts/validate_registry.py --strict
```

Run any script with `--help` for the full list of options.

## Installing the skill

The packaged skill ships as [`kid-compass.skill`](kid-compass.skill) — a zip archive containing the `kid-compass/` folder above. Unzip it into your Claude Skills directory, or load it directly in a Claude Code / Claude.ai session that supports Skills:

```bash
unzip kid-compass.skill
```

Once installed, Claude will use it automatically whenever a parent, teacher or guardian asks what their child could take part in — even if they never use the word "competition".

## Principles

- **Joy first, then growth.** Recommend things the child is likely to enjoy; competitions are one tool among many, and fear of missing out is never used to push a family.
- **Free and nearby before expensive and far.** Cost is always stated honestly, including travel.
- **Verify, then recommend.** Dates older than a year, or that look off, are checked against the official source before being stated.
- **Say what you don't know.** An unconfirmed date, eligibility rule or fee is labelled as such, with a link to check.
- **Respect the family's choices.** "Fun only" stays fun; "serious preparation" gets a serious path.
- **Child data stays minimal.** Only a nickname, age, class, board, city and interests are needed — never a full name, school name, photos, address or health information.

## Contributing

The registry is the part of Kid Compass meant to grow with community input — new national programmes, new city packs, corrected or re-verified dates. Add or edit a YAML file under `kid-compass/registry/`, following [`SCHEMA.md`](kid-compass/registry/SCHEMA.md), then run:

```bash
python kid-compass/scripts/validate_registry.py --strict
```

before opening a pull request.
