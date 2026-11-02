# kid-compass

**An open-source AI skill that helps parents find the right competitions, programmes, camps, workshops and exhibitions for their child — based on what the child actually loves — and never miss a deadline.**

Built India-first: CBSE, ICSE and State boards, Indian national programmes, city packs. It works in any country through web search.

> **You:** My daughter is 11, Class 6 CBSE, Bengaluru. She takes apart old gadgets and built a working lift out of cardboard. About ₹1,500 a month, weekends only. What should she try?
>
> **kid-compass:** builds an **opportunity map** —
> - **Sparks:** *Builder* ("built a working lift out of cardboard") · *How-things-work investigator*
> - **This month:** a science museum visit, a "Lift 2.0" home build, a planetarium sky-watch, a free children's literature festival
> - **Coming deadlines:** CBSE Science Exhibition (school registers; *reported* 14 Nov) and Bebras India (free; school registers by 28 Nov, *confirmed*) — with a ready-to-send note to her class teacher
> - **The ladder:** home builds → school fair → regional exhibition → INSPIRE-MANAK and NCSC → national, and the next rung for her
> - **Missed it?** INSPIRE-MANAK closed 15 Sep 2026; the school nominates; next window ~Jul 2027 — start an idea notebook now
> - **Balance check:** about ₹1,300–1,500 and 10–12 hours in November — right at your budget, and what to drop if it runs over
> - A **calendar file** with reminders, a month ahead for school-route deadlines
>
> **See the full, real output → [examples/bengaluru-class6-builder.md](examples/bengaluru-class6-builder.md)**

## Why

Every Indian parent has heard this one: *"There was a science congress / olympiad / art contest — we found out after the deadline."*

- Good opportunities are scattered across government circulars, school notices and WhatsApp forwards.
- Many of the best national programmes are entered **through the school**, so parents can't apply even when they find out.
- Registration deadlines come months before the event.
- Meanwhile, families get sold expensive contests where every child gets a "gold medal".

kid-compass is the well-informed, honest friend who keeps track of all of it — and cares more about your child enjoying things than about medals.

## What it does

| | |
|---|---|
| **Spark interview** | 2 minutes of questions about what your child does when nobody is directing them — or a fun "this or that" game they play themselves |
| **Opportunity map** | This weekend, coming deadlines, missed-it-plan-next-year, in one phone-sized page |
| **The ladder** | A level-by-level path for each interest: school → district → state → national → international |
| **Deadline radar** | Registration dates (not event dates), each marked *confirmed*, *reported* or *estimated* |
| **School nudge** | A polite, specific note to the class teacher for school-route programmes — English, Hindi, Kannada |
| **Worth-it check** | ⭐ Credible / ⚠️ Check first / 🚩 Pay-to-participate, with the facts behind the label |
| **Balance guard** | Adds up hours and money, flags overload, keeps joy in the mix |
| **Calendar reminders** | An `.ics` file with reminders — a month ahead for school-route programmes |
| **Debrief loop** | Three questions after each event; the next recommendations get better |

## Install

kid-compass is a standard [Agent Skill](https://agentskills.io) (a folder with a `SKILL.md`), so it works in any agent that supports skills. Pick one way:

### Quick install — any agent

**macOS / Linux / WSL**

```bash
curl -fsSL https://raw.githubusercontent.com/brainydarts/kid-compass/main/install.sh | bash
```

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/brainydarts/kid-compass/main/install.ps1 | iex
```

This copies the skill into two folders, which together cover every major agent:

| Folder | Read by |
|---|---|
| `~/.claude/skills/kid-compass` | Claude Code (and Cursor) |
| `~/.agents/skills/kid-compass` | OpenAI Codex, Cursor, GitHub Copilot, Gemini CLI and other agents that follow the shared `.agents/skills` convention |

Options: `--agent codex` (or `claude`, `cursor`, `copilot`, `gemini`, comma-separated), `--project` to install into the current project instead of your home folder, `--uninstall` to remove it. On Windows: `-Agent codex`, `-Project`, `-Uninstall`.

### With the skills CLI (18+ agents)

```bash
npx skills add brainydarts/kid-compass              # pick your agents interactively
npx skills add brainydarts/kid-compass -g           # install for your user, across all projects
npx skills add brainydarts/kid-compass -a cursor    # one agent: claude-code, codex, cursor, github-copilot, gemini-cli…
```

### Claude Code (as a plugin)

```text
/plugin install kid-compass --marketplace brainydarts/kid-compass
```

The one-step form needs Claude Code 2.1.275 or later. On older versions, use two steps: `/plugin marketplace add brainydarts/kid-compass`, then `/plugin install kid-compass@brainydarts`. Run `/plugin marketplace update` to get new registry entries.

### Claude apps (claude.ai, desktop, mobile)

Download **`kid-compass.skill`** from the [latest release](https://github.com/brainydarts/kid-compass/releases/latest) and upload it as a custom skill in your settings (see Anthropic's help centre on skills).

### Agent-specific commands

| Agent | Command |
|---|---|
| Gemini CLI | `gemini skills install https://github.com/brainydarts/kid-compass.git --path skills/kid-compass` (add `--scope workspace` for one project) |
| OpenAI Codex | Ask Codex: *"use $skill-installer to install the skill at https://github.com/brainydarts/kid-compass/tree/main/skills/kid-compass"* — or quick install with `--agent codex` |
| Cursor, GitHub Copilot | Quick install with `--agent cursor` / `--agent copilot`, or `npx skills add … -a cursor` |
| Any other agent | Copy `skills/kid-compass` into the folder your agent loads skills from |

### Manual install

```bash
git clone https://github.com/brainydarts/kid-compass.git
cp -r kid-compass/skills/kid-compass ~/.claude/skills/     # Claude Code
cp -r kid-compass/skills/kid-compass ~/.agents/skills/     # Codex, Cursor, Copilot, Gemini CLI
```

For a single project, copy it into `.claude/skills/` or `.agents/skills/` at the project root instead, and commit it so your whole team gets it.

### Chat apps without skills support

Paste the contents of `skills/kid-compass/SKILL.md` into a custom-instructions or project-instructions box and attach the `references/` and `registry/` files as knowledge. You lose the helper scripts, but the guidance and the verified registry still work.

### Optional: helper scripts

The skill includes small Python scripts (matching, deadlines, calendar files). They need Python 3.9+ and PyYAML:

```bash
python3 -m pip install pyyaml
```

Without them the skill still works: the agent reads the registry files directly.

### Check it works

Restart your agent, then ask:

> *"My son is in Class 4 in Pune and loves space — what can he take part in this year?"*

You should get an opportunity map with "Sparks", deadlines marked confirmed / reported / estimated, and a ladder.

## Try these

- *"My 9-year-old in Hyderabad draws all the time. Any art competitions or workshops this winter?"*
- *"Is the 'XYZ International Olympiad' worth ₹1,950 for my Class 3 son?"*
- *"Which science programmes need the school to nominate, and when should I talk to the teacher?"*
- *"Make me a calendar of every deadline for a Class 8 student who likes maths and coding."*
- *"My 14-year-old is shy and hates competitions but loves comics. Ideas in Pune?"*

## The registry

The skill draws on a community-maintained registry of recurring programmes, each verified against the organiser's official page and stamped with the date it was checked.

**13 national programmes** at launch:

| Programme | Interests | Who | Applied via | Registration closes | Cost |
|---|---|---|---|---|---|
| [Bebras India Computational Thinking Challenge](https://www.bebras.in) | coding, maths | Class 3–12 | School | ~Nov | Free |
| [CBSE Science Exhibition](https://academic.cbseit.in/science_ex) | science, maths, innovation | Class 6–11 (CBSE) | School | ~Nov | Free to families (school pays) |
| [INSPIRE Awards – MANAK](https://inspireawards-dst.gov.in) | science, innovation, engineering | Class 6–12 | School | ~Sep | Free |
| [IRIS National Fair](https://iris.exstemplar.com/) | science, engineering, innovation | Class 5–12 | Child/parent | ~Oct | ₹5,000 |
| [ISRO YUVIKA – Young Scientist Programme](https://www.isro.gov.in/Young_Scientist_YUVIKA2026.html) | space, science, engineering | Class 9 | Child/parent | ~Mar | Free |
| [Indian Olympiad Qualifier in Mathematics](https://ioqm.mtai.org.in/) | maths | Class 8–12 | School | ~Jul | ₹300 |
| [National Children's Science Congress](https://n-csc.in/) | science, environment, innovation | Age 10–17 | School | ~Aug | Free |
| [National Standard Examination in Junior Science](https://www.iapt.org.in/) | science | Class 8–10 | School | ~Sep | ₹300 |
| [Pradhan Mantri Rashtriya Bal Puraskar](https://awards.gov.in) | all-round, social-impact, environment | Age 5–18 | Child/parent | ~Jul | Free |
| [School Innovation Marathon](https://aim.gov.in/) | innovation, engineering, entrepreneurship | Class 6–12 | School | ~Oct | check |
| [Shankar's International Children's Competition](https://childrensbooktrust.com/sicc.html) | art, writing | Under 16 | Parent | ~Oct | Free |
| [TCS InQuizitive](https://www.tcs.com/inquizitive) | quiz, science, coding | Class 8–12 | School | varies | Free |
| [World Robot Olympiad India](https://wroindia.org/season-2026/) | robotics, engineering, coding | Age 8–22 | Coach/club | varies | ₹20,000 per team (one category free) |

City packs (reputable venues that regularly run children's programmes): **Bengaluru**. Your city next? See [CONTRIBUTING.md](CONTRIBUTING.md).

Every date kid-compass shows carries one of three labels:

- **confirmed** — checked on the organiser's official page
- **reported** — found only in news or third-party pages; confirm before acting
- **estimated** — projected from last year's cycle until someone confirms the new circular

Refreshing a deadline when the new circular comes out is the single most useful contribution you can make.

## Privacy and child safety

- The **parent** is the user. kid-compass drafts; it never contacts, messages or registers anyone.
- It asks only for a nickname, age, class, board, city and interests — never full name, school name, address or photos.
- The optional profile file stays on your machine, holds only those fields, and is never put into web searches.
- No ranking, labelling or comparing children. Competitions are presented as optional; "fun only" is a respected choice.
- No ads, no affiliate links, no paid listings.

Read the full rules in [`references/child-safety.md`](skills/kid-compass/references/child-safety.md).

## Helper scripts

```bash
cd skills/kid-compass
python scripts/find_matches.py --interests science,engineering --class 6 --age 11 --city bengaluru
python scripts/upcoming.py --days 90 --class 8
python scripts/make_ics.py --ids inspire-manak,ncsc --out reminders.ics
python scripts/validate_registry.py
```

## Contributing

The best way to help is to **add your city** or **refresh a deadline** when a new circular comes out. No coding needed for most contributions — see [CONTRIBUTING.md](CONTRIBUTING.md). Issues labelled `good first issue` are a good place to start.

## Roadmap

- City packs for Mumbai, Delhi NCR, Pune, Chennai, Hyderabad, Kolkata
- State-level programmes (state science councils, state board competitions)
- Sports pathways and arts examinations
- Spark interview in more Indian languages
- WhatsApp deadline reminders

## Disclaimer

kid-compass is not affiliated with any programme or organiser it lists. Dates, fees and eligibility change; always confirm on the official link before applying.

## Built by

**Shashank Hegde** at **BrainyDarts Technologies**, Bengaluru — makers of Brainy Reminders (WhatsApp reminders for Indian families) and Brainy Sheets (practice worksheets for CBSE classes 1–10).

If kid-compass helped your family, a ⭐ on GitHub helps other parents find it.

MIT licensed.
