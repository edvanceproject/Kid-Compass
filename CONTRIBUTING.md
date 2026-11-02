# Contributing to kid-compass

Thank you for helping. kid-compass is only as good as its registry, and every parent and teacher knows something the registry doesn't yet: a reliable science fair in Indore, a children's theatre festival in Kochi, the month a state art competition opens.

There are three ways to help, from easiest to most involved.

## 1. Tell us about an opportunity (no code)

Open an issue with the **Add an opportunity** template. Give the official link and what you know; a maintainer will turn it into a registry entry.

## 2. Add or update a registry entry

1. Copy an existing file in `skills/kid-compass/registry/national/` and rename it to `<id>.yaml` (kebab-case, e.g. `ncsc.yaml`).
2. Fill it in following [`registry/SCHEMA.md`](skills/kid-compass/registry/SCHEMA.md).
3. Run the validator:
   ```bash
   pip install pyyaml
   python skills/kid-compass/scripts/validate_registry.py
   ```
4. Open a pull request. Say in the description which pages you checked.

**The registry rules** (the reason parents can trust it):

- **Official sources only.** Every value comes from the organiser's own site or an official circular, listed in `source_urls`. Reputable news is acceptable only when the organiser publishes nothing.
- **Unknown stays `null`.** Never guess a date, fee or age limit. Explain gaps in `notes`.
- **Registration deadline, not event date**, goes in `last_seen_close`.
- **Update `last_verified`** whenever you re-check an entry, even if nothing changed.
- **No pay-to-participate contests.** If the main product is the certificate or medal, it doesn't belong here. When in doubt, open an issue first.
- **No affiliate or referral links**, and no entries you are paid to promote. Declare any connection to an organiser in the PR.

### Updating a deadline

The most valuable contribution of all is the yearly refresh: when a programme announces this year's window, update `last_seen_open`, `last_seen_close` and `last_verified`, and add the new circular to `source_urls`.

## 3. Add a city pack

A city pack lists long-running, reputable venues that regularly run programmes for children — science museums, planetariums, bal bhavans, children's theatres, libraries, art councils, nature groups — with the page where they post events. See the city pack section in `SCHEMA.md` and `registry/cities/bengaluru.yaml` as an example. Please list venues, not individual dated events.

Ideal: 8–12 venues, a mix of interests (science, arts, nature, performance), each with an official URL you've opened.

## Improving the skill itself

Changes to `SKILL.md`, the `references/` files or the scripts are welcome. Please:

- Keep `SKILL.md` short; detail belongs in `references/`.
- Keep the child-safety rules intact. Changes that collect more data about children, or that add pressure or ranking, won't be merged.
- Run the scripts and the validator before opening the PR, and describe how you tested.

**Test cases** live in `evals/` at the repo root (kept outside the skill folder so an agent using the skill never sees the expected answers). Each case has the parent's prompt (`prompt.md`), what a good answer looks like (`case.yaml`) and one check per file in `graders/`. Before a PR that changes the skill's behaviour, run the affected prompts with the skill installed and check the answers against the graders. The layout follows the format `claude plugin eval` reads, so you can also copy the cases into `skills/kid-compass/evals/` temporarily and run them with that tool.

Translations of `references/school-nudge.md` into more Indian languages are especially welcome — please have a native speaker review them.

## Conduct

Be kind and patient. Many contributors are parents and teachers, not developers. Disagree about facts with sources, not tone.

## Reporting a problem

Wrong date, broken link, an organiser you think shouldn't be listed, or a recommendation that felt pushy or unsafe? Open an issue with the **Report a problem** template. Problems with child safety are treated as the highest priority.
