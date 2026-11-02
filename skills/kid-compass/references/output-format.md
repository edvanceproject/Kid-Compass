# Output format

## The opportunity map

Use this structure every time, in this order. Keep the whole map to what a parent can read in two minutes on a phone: 10–12 opportunities at most, one or two lines each. Use the child's nickname or "your child".

```markdown
# Opportunity map for [nickname] · [class], [city] · [date]

## Sparks
- **[Spark]** — [evidence in the parent's words]
- **[Spark]** — [evidence]
(A starting guess; the debrief after each event will sharpen it.)

## This weekend / this month
| What | When · where | Cost | Fit | Worth it | Why |
|---|---|---|---|---|---|
| [Event](official link) | [Sat 14 Nov, 11 am · area] | ₹[x] / Free | Easy win | ⭐ Credible | [one line] |

## Coming deadlines (next 90 days)
| Programme | Register by | Route | Fit | Worth it | Next step |
|---|---|---|---|---|---|
| [Name](official link) | [date] — confirmed / estimated | Parent / School / Self | Sweet spot | ⭐ Credible | [one action] |

## The ladder: [top spark]
[Rung 1: where the child is now] → **[next rung, with programme]** → [rung after] → [national] → [international]
[One line on what moves the child up each rung.]

## Missed it? Plan for next time
- [Programme](link) — closed [date]; next window expected ~[month year]. [What to start now.]

## Balance check
About [n] hours and ₹[x] a month for everything above. [Within / over] what you said works for your family. [If over: what to drop.]

## This week
1. [Action]
2. [Action]
3. [Action]

---
Dates marked "estimated" come from last year's cycle — check the official link before acting.
```

### "Fun only" families

When the parent says they want nothing competitive, the same structure changes like this:

- **Coming deadlines** becomes **Coming up** — dated events and sign-ups for workshops, festivals, exhibitions and clubs. No contests, olympiads or judged events, and no "Stretch" items.
- **The ladder** becomes a **growth path** built on making and sharing rather than winning — use the non-competitive version in `interest-ladders.md` (try → make → finish → share → show → collaborate or teach).
- **Missed it?** lists festivals, exhibitions and camps, not competitions.
- Keep the Fit and Worth-it labels — a paid workshop still deserves a worth-it check.

If you can't confirm any local, dated event, it's fine to lead with at-home or online tasters (a free drawing app, a library visit, a mini-project) and say clearly that you couldn't confirm local events this month.

### Writing rules

- **Dates**: write `15 Sep 2026`. Mark each one *confirmed* (with the date you checked the official page) or *estimated*.
- **Money**: ₹ with Indian grouping (₹1,500; ₹1,25,000). Free is "Free".
- **Links**: every programme name links to its official page, not a listing site.
- **Labels**: Fit (Sweet spot / Stretch / Easy win) and Worth it (⭐ Credible / ⚠️ Check first / 🚩 Pay-to-participate) from `fit-and-worth-it.md`. If an item is 🚩, it normally doesn't belong in the map — mention it only when the parent asked about it.
- **Empty sections**: leave a section out rather than padding it. If there's nothing local this month, say so in one line and point to the city pack venues.
- **Language**: reply in the parent's language. Programme names stay as officially written.

## The profile file

Write this only when the parent asks. Save it as `kid-compass-profile.yaml` in the working folder (or give it to the parent to keep if you can't write files). It contains only minimal, non-identifying data.

```yaml
# kid-compass profile — kept by the family; contains no full name, school or address
nickname: Chinnu
age: 9
birth_month: 2017-06        # optional; helps with "age as of" cut-offs
class: 4
board: ICSE
city: mysuru
area: Kuvempunagar          # neighbourhood level only
travel: "up to 8 km for weekends; Bengaluru once a term for big events"
languages: [English, Kannada]
budget_per_month_inr: 800
free_days: [Sunday]
competition_appetite: fun-only   # fun-only | some-challenge | serious
sparks:
  - name: Explorer
    evidence: "names every bird on the morning walk"
  - name: Artist
    evidence: "draws comics about the birds"
avoid:
  - "stage performances — would rather not"
history:
  - date: 2026-12-06
    what: "Bird walk with a local nature group"
    debrief: loved it
    surprise: "liked writing the bird list more than spotting"
    certificate: false
last_updated: 2026-11-01
```
