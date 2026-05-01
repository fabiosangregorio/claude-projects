# trail-brenta-2026

Piano di allenamento personale per la **XTERRA Dolomiti di Brenta Trail – SHORT 21K** (5 settembre 2026).

🔗 **Live:** https://fabiosangregorio.github.io/claude-projects/trail-brenta-2026/

---

## Architettura

Questa sezione segue un'architettura **data-driven** diversa dai progetti DIY: i dati vivono in JSON separati, la pagina è puro layer di presentazione che li carica via `fetch`. Non si modifica la pagina per aggiornare i dati. Si modificano i JSON.

```
trail-brenta-2026/
├── index.html              ← Home. Sintesi piano + tasks + profilo.
├── runs.html               ← Lista di tutti gli allenamenti.
├── run.html                ← Dettaglio singolo allenamento (?id=<filename-senza-.json>).
├── README.md               ← Questo file.
└── data/
    ├── profile.json        ← Dati statici (atleta + obiettivo gara). Cambia raramente.
    ├── parameters.json     ← Parametri di calibrazione del piano. Cambia spesso.
    └── runs/
        ├── index.json      ← Manifest: elenco dei file run. AGGIORNARE a ogni nuovo run.
        └── <date>_<uuid>.json  ← Un file per allenamento (workout + analisi AI).
```

### Perché questa separazione

- **Evolvibilità:** aggiungere nuovi dati = nuovo JSON + un blocco di rendering, senza toccare il resto.
- **Storia:** i diff dei JSON tracciano l'evoluzione della preparazione (volumi, sensazioni, infortuni).
- **AI-friendly:** una sessione futura può leggere solo i JSON per capire lo stato senza decifrare l'HTML.

---

## File map

### `data/profile.json`

Dati **statici** dell'atleta e dell'obiettivo gara. Si modifica solo quando:
- Cambiano i dati anagrafici (peso, infortuni cronici nuovi, ecc.)
- Si aggiorna lo status di un'attrezzatura (es. "scarpe provate")
- Si cambia obiettivo gara (raro)

Sezioni: `athlete`, `experience`, `availability`, `health`, `equipment`, `race_target`, `nutrition_experience`.

### `data/parameters.json`

**Parametri di calibrazione** del piano — la parte viva. Si aggiorna ogni volta che:
- Si segna una task come completata (es. visita medica fatta)
- Si calibra il piano dopo un test (quando il piano sarà definito)

**Sempre aggiornare il campo `last_updated`** quando si modifica.

Sezioni (schema 2.0):
- `preparation_tasks` — checklist burocrazia + attrezzatura, con `priority` e `deadline`.
- `training_zones` — zone FC (5 zone Karvonen), `fcmax_bpm`, `maf_ceiling_bpm`, sorgente FCmax.
- `plan` — piano completo:
  - `total_weeks`, `race_week_number`
  - `weekly_budget` — `running_sessions`, `strength_sessions`, `philosophy`
  - `rules` — array di regole d'ingaggio
  - `phases` — 4 fasi (Ricostruzione, Base montagna, Build specifico, Peak+Taper) con `weeks_range`, `long_run_min`, `vertical_target_m`, `focus`, `key_objective`
  - `milestones` — eventi puntuali (test, deadline burocrazia, race) con `type`
  - `weeks` — 18 settimane: ognuna ha `phase_id`, `start_date`, `end_date`, `label`, `narrative`, `sessions[]`, `strength` (bool), `strength_note`, `milestone`
  - `strength_template` — 1 routine riusabile (7 esercizi, 25 min)
  - `mobility_template` — 5 esercizi post-corsa

Tipi di sessione validi: `easy`, `long`, `test`, `hike_baseline`, `strength`. La pagina rende automaticamente la settimana corrente (o la prossima/ultima definita).

### `data/runs/`

Cartella con un JSON per allenamento (workout grezzo + analisi AI). Filename: `<YYYY-MM-DD>_<uuid>.json`.

- **Sorgenti**: i JSON sono generati esternamente (parsing Garmin/Strava + analisi AI). Non si modificano a mano.
- **Manifest `data/runs/index.json`**: elenca i filename. Lo statico hosting non può listare cartelle, quindi **ogni nuovo run va aggiunto qui**.
- **Schema**: ogni run contiene `start`, `totals`, `derived`, `decoupling`, `splits`, `walk_breaks`, `hr_zones`, e `ai_analysis` (headline, classification, execution, concerns, strengths, narrative, next_session).

---

## Convenzioni per evoluzioni future

### Aggiungere un nuovo tipo di dato

Es. log allenamenti, diario sensazioni, lista spesa attrezzatura dettagliata.

1. Crea `data/<nome>.json` con un campo `_schema_version` e `_description`.
2. In `index.html`, aggiungi una `fetch` nel blocco di caricamento iniziale.
3. Aggiungi una funzione `render<Nome>()` che produce il markup.
4. Aggiungi una sezione nel layout HTML.
5. **Aggiorna questo README** con il nuovo file e la sua semantica.

### NON fare

- ❌ Mai mettere dati nell'HTML. Se vedi un valore hardcoded nella pagina che dovrebbe vivere nei JSON, spostalo.
- ❌ Mai modificare l'HTML per aggiornare i dati: modifica il JSON.
- ❌ Mai duplicare dati tra `profile.json` e `parameters.json`. Se non sai dove mettere un campo, vince `parameters.json` se può cambiare.

### Stile codice

- Vanilla JS, no framework, no build step (la pagina deve funzionare aprendola direttamente o via GitHub Pages).
- Stessi font e palette del resto del repo (Space Mono + DM Sans, dark theme GitHub-style — vedi `../README.md`).
- Mobile-first: la pagina deve essere ottima su iPhone.
- Niente `localStorage` per i dati (vivono nei JSON, versionati). `localStorage` solo per UI ephemera (es. accordion aperti).

---

## Come aggiornare la calibrazione (per Fabio)

Quando vuoi calibrare il piano dopo un test/lungo/sensazione:

1. Apri una nuova chat con Claude.
2. Dì cosa è successo (es. "ho fatto il primo lungo di 80 min, sensazioni ottime — passo medio 6:30/km").
3. Claude leggerà `parameters.json`, applicherà la modifica, aggiornerà `last_updated`, pusherà su GitHub.

La pagina si aggiorna automaticamente al prossimo refresh (i JSON vengono fetchati ogni volta).

---

## Note per Claude (sessioni future)

- **Prima di modificare:** leggi sempre lo stato corrente di `profile.json` e `parameters.json`.
- **Patch chirurgiche:** modifica solo i campi rilevanti, non riscrivere l'intero JSON.
- **`last_updated`:** aggiornalo a ogni modifica di `parameters.json`.
- **Validazione:** dopo ogni push, verifica che la pagina renderizzi senza errori (apri la URL live).
- **Domande chirurgiche:** se Fabio dice "ho fatto un lungo", chiedi solo i dati mancanti (durata, dislivello, sensazioni, passo medio). Non rifare l'intake.
- **Calibrazione conservativa:** se i numeri vanno meglio del previsto, alza i volumi al massimo del +10%. Mai di più.
- **Infortuni:** se Fabio segnala dolore, **non** suggerire di "spingere comunque". Riposo + valutazione medica.
