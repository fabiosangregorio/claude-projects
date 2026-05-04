# trail-brenta-2026

Piano di allenamento personale per la **XTERRA Dolomiti di Brenta Trail – SHORT 21K** (5 settembre 2026).

🔗 **Live:** https://fabiosangregorio.github.io/claude-projects/trail-brenta-2026/

---

## Architettura

Questa sezione segue un'architettura **data-driven** diversa dai progetti DIY: i dati vivono in JSON separati, la pagina è puro layer di presentazione che li carica via `fetch`. Non si modifica la pagina per aggiornare i dati. Si modificano i JSON.

```
trail-brenta-2026/
├── index.html              ← Home. Tasks + obiettivo gara + profilo + link a piano e attività.
├── plan.html               ← Indice del piano (fasi, milestone, riferimenti tecnici, link a settimana).
├── week.html               ← Dettaglio piano settimanale (#<numero-settimana>).
├── activities.html         ← Lista di tutte le attività (run + hike).
├── activity.html           ← Dettaglio singola attività (#<filename-senza-.json>).
├── recovery.html           ← Guida pratica al recupero post-attività (statica, no JSON).
├── README.md               ← Questo file.
└── data/
    ├── profile.json        ← Atleta + obiettivo gara + zone FC calibrate.
    ├── plan.json           ← Struttura del piano (fasi, settimane, milestone, template).
    ├── todo.json           ← Task list di preparazione.
    └── activities/
        ├── index.json      ← Manifest: elenco dei file attività. AGGIORNARE a ogni nuovo log.
        └── <date>_<uuid>.json  ← Un file per attività (run o hike).
```

### Perché questa separazione

- **Evolvibilità:** aggiungere nuovi dati = nuovo JSON + un blocco di rendering, senza toccare il resto.
- **Storia:** i diff dei JSON tracciano l'evoluzione della preparazione (volumi, sensazioni, infortuni).
- **AI-friendly:** una sessione futura può leggere solo i JSON per capire lo stato senza decifrare l'HTML.

---

## File map

### `data/profile.json`

Dati dell'atleta e dell'obiettivo gara. Si modifica quando:
- Cambiano i dati anagrafici (peso, infortuni cronici nuovi, ecc.)
- Si aggiorna lo status di un'attrezzatura (es. "scarpe provate")
- Si cambia obiettivo gara (raro)
- Si ricalibrano le zone di FC dopo un test (FCmax, MAF, bande)

Sezioni: `athlete`, `experience`, `availability`, `health`, `calibration_source`, `training_zones`, `equipment`, `race_target`, `nutrition_experience`.

### `data/plan.json`

**Struttura del piano** — il blueprint prescrittivo. Si aggiorna quando si ridisegna il piano (fasi, settimane, milestone, template forza/mobility).

**Sempre aggiornare il campo `last_updated`** quando si modifica.

Chiavi top-level: `total_weeks`, `race_date`, `weekly_budget`, `rules`, `phases`, `weeks`, `milestones`, `strength_template`, `mobility_template`.

### `data/todo.json`

**Task list di preparazione** (burocrazia, equipment, test). Si aggiorna ogni volta che si segna una task come completata o se ne aggiunge una nuova.

Chiavi: `last_updated`, `tasks` (array con `category`, `task`, `deadline?`, `status`, `priority?`, `note?`).

### `data/activities/`

Cartella con un JSON per attività (run o hike). Filename: `<YYYY-MM-DD>_<uuid>.json`.

**Schema unificato (schema_version: 2)**: un solo formato per run e hike, distinti dal campo `activity_type`.

Campi top-level comuni:
- `schema_version`, `activity_type` (`"run"` | `"hike"`), `id`, `start`, `end`, `title?`, `source?`, `source_url?`, `user_notes?`
- `category?` (`"training"` default omesso | `"social"` | `"test"`) — vedi sotto
- `totals` — distanza, durate, dislivello (vedi sotto per differenze run/hike)
- `derived` — metriche calcolate (vertical, race_match, eccetera)
- `ai_analysis?` — headline, classification, execution, trail_specificity, strengths, concerns, narrative, next_session. **Assente per attività `category: "social"`.**

**Campo `category`:**
- Omesso o `"training"` → attività di allenamento, contribuisce al piano e alle analisi di progresso.
- `"social"` → uscita non strutturata (es. hike con amici, niente FC). Si registra solo per il **carico settimanale grezzo** (km, tempo, dislivello). **NON contribuisce** a: analisi di progresso, calcolo trend, metriche di specificità trail, calibrazione zone, valutazione esecuzione. Niente `ai_analysis`, niente `derived.race_match`.
- `"test"` → attività usata come benchmark per calibrare il piano (es. ripetizione del baseline). Riservato per uso futuro.

**Per `activity_type: "run"`** — `totals` include `duration_sec`, `avg_pace_min_per_km`, `gap_min_per_km`, `avg_hr`, `max_hr_observed`, `avg_cadence_spm`, `ef`, `steps`, ecc. Top-level: `splits`, `hr_zones`, `decoupling`, `walk_breaks`, `walks_summary`, `pace_variability`. Sorgente: parsing Garmin/Strava + analisi AI esterna.

**Per `activity_type: "hike"`** — `totals` include `duration_sec` (= totale, start→end), `duration_moving_sec`, `pause_sec`, `descent_m`, `avg_speed_kmh_moving`. Niente `splits`/`hr_zones`/`decoupling`. Sorgente tipica: GPX da Komoot.

**Manifest `data/activities/index.json`**: elenca i filename. Lo statico hosting non può listare cartelle, quindi **ogni nuova attività va aggiunta qui** nell'array `activities`.

---

## Convenzioni per evoluzioni future

### Aggiungere un nuovo tipo di attività

Se in futuro servono altri tipi (es. `bike`, `strength_log`, `swim`), basta:
1. Aggiungere il valore a `activity_type`
2. Definire i campi specifici nel `totals` (mantenendo i comuni)
3. In `activity.html`, gestire le sezioni nel dispatcher `render()` con la guard appropriata
4. **Aggiornare questo README** con il nuovo tipo

### Aggiungere un nuovo tipo di dato (non attività)

Es. log sensazioni, lista spesa attrezzatura dettagliata.

1. Crea `data/<nome>.json` con un campo `_schema_version` e `_description`.
2. In `index.html`, aggiungi una `fetch` nel blocco di caricamento iniziale.
3. Aggiungi una funzione `render<Nome>()` che produce il markup.
4. Aggiungi una sezione nel layout HTML.
5. **Aggiorna questo README** con il nuovo file e la sua semantica.

### NON fare

- ❌ Mai mettere dati nell'HTML. Se vedi un valore hardcoded nella pagina che dovrebbe vivere nei JSON, spostalo.
- ❌ Mai modificare l'HTML per aggiornare i dati: modifica il JSON.
- ❌ Mai duplicare dati tra `profile.json` e `plan.json`. Profilo = chi sei (anagrafica + zone FC + obiettivo gara); plan = come ti alleni (fasi/settimane/template).
- ❌ Mai aggiungere file/sezioni "appena utili": il principio del progetto è preferire rimuovere/modificare invece di aggiungere. Mantenere i file leggeri.

### Stile codice

- Vanilla JS, no framework, no build step (la pagina deve funzionare aprendola direttamente o via GitHub Pages).
- Stessi font e palette del resto del repo (Space Mono + DM Sans, dark theme GitHub-style — vedi `../README.md`).
- Mobile-first: la pagina deve essere ottima su iPhone.
- Niente `localStorage` per i dati (vivono nei JSON, versionati). `localStorage` solo per UI ephemera.

---

## Come aggiornare la calibrazione (per Fabio)

Quando vuoi calibrare il piano dopo un test/lungo/sensazione:

1. Apri una nuova chat con Claude.
2. Dì cosa è successo (es. "ho fatto il primo lungo di 80 min, sensazioni ottime — passo medio 6:30/km").
3. Claude leggerà `plan.json` (e/o `profile.json` se cambiano le zone FC), applicherà la modifica, aggiornerà `last_updated`, pusherà su GitHub.

La pagina si aggiorna automaticamente al prossimo refresh (i JSON vengono fetchati ogni volta).

---

## Note per Claude (sessioni future)

- **Prima di modificare:** leggi sempre lo stato corrente di `profile.json`, `plan.json`, `todo.json` e `data/activities/index.json`.
- **Patch chirurgiche:** modifica solo i campi rilevanti, non riscrivere l'intero JSON.
- **`last_updated`:** aggiornalo nel file modificato (`plan.json`, `profile.json` o `todo.json`).
- **Validazione:** dopo ogni push, verifica che la pagina renderizzi senza errori (apri la URL live).
- **Domande chirurgiche:** se Fabio dice "ho fatto un lungo", chiedi solo i dati mancanti (durata, dislivello, sensazioni, passo medio). Non rifare l'intake.
- **Calibrazione conservativa:** se i numeri vanno meglio del previsto, alza i volumi al massimo del +10%. Mai di più.
- **Infortuni:** se Fabio segnala dolore, **non** suggerire di "spingere comunque". Riposo + valutazione medica.
- **Hike sociali (`category: "social"`):** ignora questi file quando calcoli progressi, trend, decoupling, polarizzazione, specificità trail. Contano *solo* come carico settimanale grezzo (km/tempo/D+). Non scrivere `ai_analysis` per loro né farne riferimento nelle analisi di altre attività.
- **GPX da Komoot/Garmin/Strava:** parsing locale (Python) — distanza haversine, dislivello con smoothing 5-pt + dead-band 0.5 m, pause = sample con velocità < 0.3 m/s.
