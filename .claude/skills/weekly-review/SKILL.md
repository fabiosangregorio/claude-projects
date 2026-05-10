---
name: weekly-review
description: Run end-of-week retrospective for trail-brenta-2026 training plan. Computes the auto-block from logged activities, asks 6 fixed picker questions plus up to 2 adaptive probes when triggers fire, persists the review under weeks[].review in plan.json. Use when the user says "analizziamo la settimana", "review settimana N", invokes /weekly-review, or asks to close out a training week.
---

# Weekly review — trail-brenta-2026

End-of-week retrospective. Three layers in order: **auto block (no input) → 6 fixed picker questions → 0-2 adaptive probes (only on trigger)**. Output is a structured `review` object persisted into `plan.json` under the matching `weeks[]` entry. No free text from the user.

## Files involved

- `trail-brenta-2026/data/plan.json` — the review is written into `weeks[N].review`. Update `last_updated`.
- `trail-brenta-2026/data/activities/index.json` + `data/activities/*.json` — source for the auto block.
- `trail-brenta-2026/data/weighins.json` — for weekly weight delta in load.
- `trail-brenta-2026/data/profile.json` — for FC zones / race target context.
- `trail-brenta-2026/week.html` — render layer. Section `Retrospettiva` at the bottom of the page renders `review` if present. Add it the first time the skill runs.

## Workflow

### 1. Pick the week

- Default: the most recent week in `plan.json.weeks` whose `end_date` ≤ today. Confirm by saying "Chiudo la settimana N: «label», DD/MM → DD/MM. Procedo?" and wait for ack.
- Override: if the user names a week ("settimana 2", "quella di metà maggio"), use that one.
- If the chosen week already has a `review`, ask whether to overwrite or amend.

### 2. Compute the auto block (zero input)

Read every activity whose `start` falls in the week's `[start_date, end_date]` range, **excluding** `category: "social"` from progress metrics (still counted in raw load). Compute:

```
auto.adherence:
  planned: count of sessions[] in plan.json weeks[N]
  done: count of activities matched by date+type
  long_run: "done" | "missed" | "n/a-this-week"
  swapped: array of {planned, replaced_with, reason?} — infer from gaps + recurring

auto.load:
  trimp: sum of derived.trimp across week (training only)
  ascent_m: sum of totals.ascent_m (incl. social — raw load)
  duration_min: sum of totals.duration_sec / 60
  maf_below_pct: time-weighted avg of derived.maf.time_below_pct
  weight_delta_kg: latest weighin in week minus previous, or null

auto.phase_kpi:
  objective: copy from phases[current].key_objective
  status: "measured" | "not_measurable_this_week" | "out_of_target"
  value: numeric if measured, else null
  note: 1 sentence explaining why not measurable, or interpreting the value

auto.open_concerns: aggregate ai_analysis.concerns[] across activities of the week.
  For each unique area, track: weeks_open (count of consecutive weeks where it appeared), severity_max.

auto.highlights: 1 string. Pull the strongest sentence from ai_analysis.strengths or narrative across the week.
auto.lowlights: 1 string. Same from concerns / failure_modes.
```

**KPI status rule per phase:**
- Phase 1 (rebuild): status = `measured` only if there's a Z2 effort ≥60 min on flat (`ascent_m`<150) terrain. Otherwise `not_measurable_this_week` with note explaining why (e.g. "Linzone è verticale, decoupling 22% è artefatto camminata").
- Phase 2: status = `measured` if a session ≥90 min with D+ ≥400 m exists.
- Phase 3: status = `measured` if a long ≥180 min with D+ ≥700 m and fueling logged exists.
- Phase 4: status = `measured` if subjective freshness checked + 1 short Z3 done.

### 3. Detect adaptive triggers (BEFORE asking)

Run these checks against the auto block + last 3 weeks' reviews:

| Trigger | Fires when |
|---|---|
| `carryover_concern` | Same `concerns[].area` (case-insensitive substring match) appears in ≥2 of last 3 activity groups. |
| `swap_unexplained` | A planned session is missing AND no swap was inferred from recurring (e.g. easy run absent, no padel/bici on that day either). |
| `phase_kpi_off` | KPI status is `out_of_target` or measured value deviates >25% from phase target. |
| `equipment_concern` | Any activity in the week has a concern with `area` matching `/scarp|zaino|airpods|pack|gps|HR/i`. |

Each trigger maps to ONE adaptive question (see § 5). Cap at 2 adaptive probes per review — pick the highest priority: `equipment_concern` > `carryover_concern` > `phase_kpi_off` > `swap_unexplained`.

### 4. Ask the fixed checkin questions

Use the Conductor `mcp__conductor__AskUserQuestion` tool (load via ToolSearch with `select:mcp__conductor__AskUserQuestion`).

**Tool constraints (hard limits, do not violate):**
- Max **4 questions** per call → batch in groups of ≤4.
- Max **4 options** per question → compress accordingly.
- The tool auto-appends an "Other" free-form option, so do NOT include "altro" yourself.

**Style rules** learned from real runs:
- Use **inline descriptions** in option labels for any non-obvious word (`neutro — riposato ma serve un giorno facile`). The athlete is not a coach: never assume jargon is understood.
- **Plain Italian, no anglicisms**. `ok ma qualcosa da sistemare`, not `glitch ma usabile`. `niggle` needs to be explained inline (`piccoli dolori/fastidi non bloccanti`).
- If a concern is already detailed in an activity's `user_notes`, **do not re-ask** it as adaptive probe — read it from the note.

**The 5 fixed questions** (always asked, in this order):

1. **Recupero attuale (freschezza generale, oggi)?** — single
   - `fresco — pronto a un altro lavoro duro`
   - `neutro — riposato ma serve un giorno facile`
   - `stanco — recupero attivo o riposo`
   - `svuotato — riposo totale, qualcosa non va`
2. **DOMS post-carico: andamento?** — single (collapses peak+cleared into one question)
   - `leggeri, spariti in 1-2 gg`
   - `tipici (3-4 gg)`
   - `pesanti, oltre 4 gg / ancora aperti`
   - `nessuno`
3. **Sonno medio settimana?** — single: `<6h` · `6-7h` · `7-8h` · `>8h`
4. **Niggle (piccoli dolori/fastidi non bloccanti) aperti adesso?** — multi-select. Always include `nessuno` plus 3 most likely body parts inferred from the week's activities and existing `concerns[]`. Tool's auto-Other handles atypical sites.
5. **Carico extra-sport (lavoro/vita) della settimana?** — single
   - `leggero — settimana tranquilla`
   - `normale — routine standard`
   - `pesante — lavoro intenso ma gestito`
   - `molto pesante — mi ha mangiato energie`

**Race-day forcing question — DO NOT ask the user.** "Cosa si romperebbe per primo?" is meta-cognitive: the athlete can't reliably compare their current state to a race they've never run. Instead, **derive** it from data in step 6 and write it to `auto.race_day_break_derived` with a `reason` field. Keep the value space stable across weeks for grep-pability: `motore aerobico` · `gambe (salita o discesa)` · `nutrizione/idratazione` · `equipment` · `testa/pacing`.

**Suggested batching** (with current 4-question limit):
- Batch 1 (4): recupero · DOMS · sonno · niggle
- Batch 2 (1): life_load — alone, OR combined with adaptive probes if any.

### 5. Ask adaptive probes (if any triggered, 4-option max)

**Skip rule**: if the relevant detail is already in `user_notes` of an activity from the week, do NOT re-ask. Quote the note in the synthesis instead.

| Trigger | Question | Options (max 4) |
|---|---|---|
| `carryover_concern` | "<area> torna per la Nª settimana. Stato:" | `risolto` · `migliorato` · `uguale` · `peggiorato` |
| `swap_unexplained` | "<sessione> saltata. Motivo:" | `DOMS` · `vita/lavoro` · `scelta lucida` · `dimenticanza` |
| `phase_kpi_off` | "<KPI> fuori target. Causa:" | `sonno` · `caldo/condizioni` · `gambe scariche` · `non so` |
| `equipment_concern` | "Setup <oggetto>:" | `perfetto` · `ok ma da sistemare` · `problemi seri` · `da cambiare` |

### 6. Compose verdict + headline + synthesis

**Verdict** — single word, deterministic from auto + checkin:

- `recalibrate` — if any of: phase_kpi `out_of_target`, niggle severity ≥3 open ≥2 weeks, recovery `svuotato`, two consecutive weeks with same `race_day_break`.
- `behind` — long run missed AND adherence done/planned <0.6.
- `ahead` — adherence ≥1.0 AND recovery `fresco` AND phase_kpi measured & on target.
- `on-track` — default otherwise.

**Headline** — 1 sentence. Tie the dominant signal of the week: e.g. "Carico montano assorbito, KPI di fase rinviato per terreno verticale." Avoid emojis. Italian.

**Synthesis** — 1-2 sentences. Deterministic recipe:
- Sentence 1: load summary in plain words (not numbers): "Settimana di carico [leggero/medio/alto] con [N] uscite e [X] m di D+."
- Sentence 2: the most actionable signal — either the `race_day_break` answer turned into an imperative ("Equipment in cima alle preoccupazioni: rivedere allacciatura/numero scarpe prima del prossimo trail.") or a carryover-concern callout, or the DOMS/recovery state.

Do not write more than 2 sentences. The narrative used to be free text; it is no longer. The skill writes this for the user.

### 7. Persist

Write to `trail-brenta-2026/data/plan.json` under `weeks[N].review`:

```json
"review": {
  "date": "<YYYY-MM-DD of week.end_date>",
  "verdict": "on-track" | "ahead" | "behind" | "recalibrate",
  "headline": "...",
  "synthesis": "...",
  "auto": {
    "adherence": { "planned": 3, "done": 2, "long_run": "done", "swapped": [...] },
    "load": { "trimp_training": 272, "ascent_m_total": 2010, "duration_min_total": 656, "maf_below_pct_training": 36, "weight_delta_kg": null, "weight_kg_latest": 66.4 },
    "phase_kpi": { "objective": "...", "status": "not_measurable_this_week", "value": null, "note": "..." },
    "open_concerns": [{ "area": "vestibilità scarpa in discesa", "weeks_open": 1, "severity_max": 3, "status": "open" }],
    "highlights": "...",
    "lowlights": "...",
    "race_day_break_derived": { "value": "motore aerobico", "reason": "Phase 1 KPI not measured; baseline piatto 1 mag a 12.6% decoupling; rientro 13 mesi." }
  },
  "checkin": {
    "recovery": "stanco",
    "doms": "tipici (3-4 gg)",
    "sleep_avg": "6-7h",
    "niggles": ["pollicione"],
    "life_load": "pesante"
  },
  "adaptive": [
    { "trigger": "equipment_concern", "q": "Setup La Sportiva", "a": "ok ma da sistemare" }
  ]
}
```

Update `plan.json.last_updated` to today's date. Don't reformat unrelated keys.

### 8. Verify the page renders

If `week.html` does not yet have a `Retrospettiva` section, add one. It should render — only when `weeks[N].review` exists:

- Verdict badge + headline (large)
- Stat strip from `auto.load`: TRIMP, D+, durata, MAF%
- Phase KPI line with status pill
- Checkin chips: 1 chip per picker answer, plus the `race_day_break` as a pull-quote
- Open concerns as orange chips with `weeks_open` counter
- Synthesis as the closing line
- Adaptive probes inside a `<details>` if any
- Highlight + lowlight in a small two-column block

Style consistent with the rest of `week.html` (Space Mono / DM Sans, dark theme, mobile-first).

### 9. Commit (only if asked)

Don't auto-commit. Show the diff summary and ask: "Committo la review della settimana N?" — then use the standard commit flow.

## Things to never do

- Never ask free-text questions. The skill is multiple-choice only. The single optional `note` field has been intentionally omitted — if the user wants narrative, they can add it manually later.
- Never ask the user to forecast race-day failure modes. That's `race_day_break_derived` — the skill computes it from data with a `reason`.
- Never re-ask something already detailed in an activity's `user_notes` or `ai_analysis.concerns`. The skill reads, it doesn't double-check.
- Never use anglicisms (`glitch`, `niggle` without explanation, `recovery score`). Plain Italian, with inline definitions for any non-obvious word.
- Never use Likert scales (1-5). All answers are categorical.
- Never invent activities or sessions. If a session was planned but no matching activity exists, the auto block records it as missed/swapped. The skill does not "fill in" estimates.
- Never mark `phase_kpi.status = "measured"` on a session that doesn't fit the phase rule (see § 2). It's better to record `not_measurable_this_week` than to fake a measurement on the wrong terrain.
- Never overwrite a previous week's `review` without explicit user confirmation.
- Never duplicate the per-activity `ai_analysis`. The auto block aggregates and trends — it does not retell single sessions.
- Never push to remote unless the user explicitly asks.

## Sharp edges

- **Phase boundary weeks**: when a week straddles two phases (rare), the KPI rule uses the phase of `week.end_date`.
- **First week of plan**: no carryover possible, `weeks_open` = 1 for any concern. Trigger `carryover_concern` won't fire (good).
- **Recurring (padel/bici)**: don't count in `adherence.done`. They live in `weeks[N].recurring`, not in `sessions[]`.
- **Multi-day sessions** (e.g. hike sab+dom in week 1): one logical session in `sessions[]`, two activity files. Match by the `when` field — count as 1 done if ≥1 file logged.
- **Social activities** (`category: "social"`): excluded from adherence done count, decoupling/MAF aggregates, KPI status — but their `ascent_m` and `duration_sec` count in raw `auto.load`.

## When NOT to use this skill

- Mid-week adjustments (use the calibration flow described in `trail-brenta-2026/README.md`).
- Single-activity logging (different flow — adding a JSON to `data/activities/`).
- Plan-wide changes (phase reshuffles, milestone moves) — those edit `plan.json` outside `review`.
