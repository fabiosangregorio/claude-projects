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
├── weighins.html           ← Lista di tutte le pesate settimanali (con summary + delta).
├── recovery.html           ← Guida pratica al recupero post-attività (statica, no JSON).
├── README.md               ← Questo file.
└── data/
    ├── profile.json        ← Atleta + zone FC calibrate.
    ├── race.json           ← Obiettivo gara (evento, percorso, profilo).
    ├── plan.json           ← Struttura del piano (fasi, milestone, template, regole).
    ├── weeks/             ← Una settimana per file. Manifest in `index.json`, contenuto in `week-NN.json`.
    │   ├── index.json      ← Manifest: elenco dei file settimana. AGGIORNARE quando si pianifica una nuova settimana.
    │   └── week-NN.json    ← Una settimana del piano (sessioni ordinate cronologicamente, strength, review).
    ├── todo.json           ← Task list di preparazione.
    ├── weighins.json       ← Pesate settimanali (LUN mattina) da scala 1byone.
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

Dati dell'atleta. Si modifica quando:
- Cambiano i dati anagrafici (peso, infortuni cronici nuovi, ecc.)
- Si aggiorna lo status di un'attrezzatura (es. "scarpe provate")
- Si ricalibrano le zone di FC dopo un test (FCmax, MAF, bande)

Sezioni: `athlete`, `experience`, `availability`, `health`, `calibration_source`, `training_zones`, `equipment`, `nutrition_experience`.

### `data/race.json`

**Obiettivo gara** — dati ufficiali dell'evento + profilo percorso. Si modifica quando:
- Si cambia gara (raro)
- Viene pubblicato il GPX 2026 ufficiale (sostituire `course_profile_2025` → `course_profile_2026`)

Chiavi top-level: `event`, `edition`, `date`, `location`, `distance_km`, `elevation_gain_m`, `start_time`, `max_time_hours`, `cancello_orario`, `min_age`, `itra_points`, `registration_fee_eur_2025`, `official_url`, `goal`, `route_summary`, `course_profile_2025` (con `gpx_stats_official`, `gpx_stats_computed`, `grade_distribution`).

### `data/plan.json`

**Struttura del piano** — il blueprint prescrittivo (fasi, regole, budget settimanale, template forza/mobility). Si aggiorna quando si ridisegna l'architettura del piano.

**Sempre aggiornare il campo `last_updated`** quando si modifica.

Chiavi top-level: `total_weeks`, `weekly_budget`, `rules`, `phases`, `strength_template`, `mobility_template`. Le settimane vivono in `data/weeks/` (un file per settimana, vedi sotto). La data gara vive in `race.json.date` (canonica), non duplicare qui.

### `data/weeks/`

**Settimane del piano** — calendario delle sessioni, strength e retrospettive. Una settimana per file (`week-NN.json`) + manifest `index.json` che ne elenca i filename in ordine cronologico. Estratto da `plan.json` a partire dalla v1.4 (file unico `weeks.json`); splittato in un file per settimana a partire dalla v1.5 per mantenere i diff focali e i file singoli leggeri.

**Manifest `data/weeks/index.json`**: elenca i filename in `weeks` (array). Aggiungere il filename della nuova settimana quando si pianifica. Lo statico hosting non può listare cartelle, quindi va aggiornato a mano. Aggiornare anche `last_updated`.

**File `data/weeks/week-NN.json`**: un singolo oggetto-settimana. Top-level: `_schema_version`, `number`, `phase_id`, `start_date`, `end_date`, `label`, `narrative`, `sessions[]`, `strength?`, `review?`. Nessun array contenitore — il file È la settimana.

**Ordinamento sessioni:** all'interno di ogni settimana, `sessions[]` è ordinato cronologicamente per data dedotta dal campo `when` (es. `"SAB 2 + DOM 3"` → SAB 2; `"MER 6 o GIO 7"` → MER 6; `"MER"` senza numero → calcolato dal `start_date` della settimana). I consumatori (`week.html`, ecc.) renderizzano nell'ordine dell'array — quindi mantenere l'ordine cronologico in fase di edit.

**`sessions[].activities`** — array opzionale di attività registrate che hanno eseguito quella sessione (consuntivo). Item: `{file, title}` dove `file` è il filename in `data/activities/` senza `.json`. Renderizzato da `week.html` come badge verdi cliccabili sotto il blocco `routes`, link diretto a `activity.html#<file>`. Una sessione può avere più attività (es. hike multi-giorno).

**Niente dati attività-specifici nella sessione.** Gear list ("cosa portare"), piano nutrizione, piano orari e `grade_distribution` pianificata vivono **nel file dell'attività**, non nella sessione della settimana. Vedi "Campi di pianificazione" in `data/activities/`. La sessione resta prescrittiva ad alto livello (tipo, durata, intensità, FC max, when, notes, routes, activities); i dettagli operativi del singolo giorno stanno con l'attività che li esegue.

**`sessions[]` di tipo `check-in` / `cross-training`** — ricorrenze settimanali fisse (cross-training non strutturato, check-in di tracking) **definite per settimana**, vivono nello stesso array delle sessioni di corsa. Non sono sessioni di allenamento prescrittive — sono ancore di baseline. `week.html` le renderizza con lo **stesso layout** delle altre sessioni; il `label` (es. "Pesa", "Padel", "Bici") sostituisce il fallback del tipo nel badge, e il colore del badge resta determinato dal `type`. Definirle per settimana permette di variare in base al contesto (es. vacanza = niente padel, settimana scarico = niente bici). Campi item: `type` (`check-in` | `cross-training`), `label`, `when` (giorno-della-settimana ed eventuale contesto orario, es. `"LUN mattina, a digiuno"` o `"MER"`), `duration_min?`, `intensity?`, `notes?`. Esempi tipici: pesa LUN, padel MER, bici GIO. Non contano per `auto.adherence.done` della review (vedi skill `weekly-review`).

**`strength`** — opzionale. Assente = usa il template (renderer mostra la card "vedi piano principale"). `{ skipped: true, reason: "..." }` = settimana senza forza con motivazione (renderer mostra la card "saltata" con il `reason`). In futuro potrà accettare anche un override in forma di session-object.

**`review`** — retrospettiva di fine settimana, scritta dalla skill `weekly-review` (vedi `.claude/skills/weekly-review/SKILL.md`). Tre layer: `auto` (calcolato da attività + weighins, zero input), `checkin` (5 risposte multiple-choice raccolte via `mcp__conductor__AskUserQuestion`), `adaptive` (max 2 probe attivati da regole). Campi top: `date`, `verdict` (`on-track` | `ahead` | `behind` | `recalibrate`), `headline` (1 frase), `synthesis` (1-2 frasi deterministiche). Sotto `auto`: `adherence`, `load`, `phase_kpi` (status `measured` | `not_measurable_this_week` | `out_of_target`; `value` presente solo se `measured`/`out_of_target`), `open_concerns` (campi `area`, `weeks_open`, `severity_max` — la presenza nell'array implica `open`, niente campo `status`), `highlights`, `lowlights`, `race_day_break_derived` (la "forzante": NON chiesta all'utente, derivata dai dati con `reason`). I campi `checkin.niggles` e `adaptive` sono omessi quando vuoti. Renderizzato da `week.html` come sezione "Retrospettiva" in fondo alla card della settimana, solo se presente.

**Sempre aggiornare il campo `last_updated` di `weeks/index.json`** quando si modifica una settimana o si aggiunge un file.

### `data/todo.json`

**Task list di preparazione** (burocrazia, equipment, test). Si aggiorna ogni volta che si segna una task come completata o se ne aggiunge una nuova.

Chiavi: `last_updated`, `tasks` (array con `category`, `task`, `deadline?`, `status`, `priority?`, `note?`).

### `data/weighins.json`

**Pesate settimanali** durante la preparazione. Una entry per settimana, presa il LUN mattina a digiuno con la scala 1byone Health (ricorrenza fissa nel piano). Sorgente dei valori: `onebyone-cli` (`onebyone records --type body-fat`).

Chiavi: `last_updated`, `source` (`device`, `mac`, `cli`), `entries` (array). Campi entry: `date` (YYYY-MM-DD), `weight_kg`, `body_fat_pct?`, `bmi?`, `muscle_kg?`, `body_water_pct?`, `visceral_fat?`, `bmr_kcal?`. Tutti i campi oltre a `date` e `weight_kg` sono opzionali (per supportare scale future più semplici).

Render:
- **`index.html` → "Profilo atleta"**: il blocco "Peso × Altezza" preferisce l'ultima entry (fallback `profile.json.athlete.weight_kg`); "BMI" preferisce l'ultima entry, fallback **calcolato** da `weight_kg / (height_cm/100)²`; aggiunge una cella "Body Fat" e una sub-line con la data + delta vs baseline (quando `entries.length >= 2`).
- **`index.html` → nav-card "Pesate"**: link a `weighins.html` con counter e ultima pesata in subline.
- **`week.html` → sessione `check-in` "Pesa LUN"**: mostra `66.4 kg · 13.1% BF · BMI 19.8` se l'entry cade nel range della settimana, "in attesa" se settimana corrente senza entry, "— saltata" se settimana passata senza entry.
- **`weighins.html`**: lista completa delle pesate (desc per data) con summary in alto (ultimo peso, body fat, BMI, Δ vs inizio) e card per entry con `Δ vs precedente` e `Δ vs inizio`. Mappa ogni entry alla settimana del piano via `plan.json`.

`profile.json.athlete.weight_kg` resta come **baseline iniziale** (al via del piano, non si aggiorna). La home preferisce `weighins.json` quando disponibile, altrimenti fa fallback a `profile.json`. Il BMI viene **calcolato** dal peso + altezza (non duplicato in `profile.json`). Niente duplicazione: profile = baseline anagrafico, weighins = serie longitudinale.

### `data/activities/`

Cartella con un JSON per attività (run o hike). Filename: `<YYYY-MM-DD>_<uuid>.json`.

**Schema unificato (schema_version: 2)**: un solo formato per run e hike, distinti dal campo `activity_type`.

Campi top-level comuni:
- `schema_version`, `activity_type` (`"run"` | `"hike"`), `id`, `start`, `end`, `title?`, `source?`, `source_url?`, `user_notes?`
- `category?` (`"training"` default omesso | `"social"` | `"test"`) — vedi sotto
- `totals` — distanza, durate, dislivello (vedi sotto per differenze run/hike)
- `derived` — metriche calcolate (vertical, race_match, eccetera)
- `ai_analysis?` — headline, classification, execution, trail_specificity, strengths, concerns, narrative, next_session. **Assente per attività `category: "social"`.**
- **Pianificazione (opzionali, valgono per uscite "preparate"):** `gear_checklist?`, `grade_distribution?`, `nutrition_plan?`, `schedule?`. Vedi "Campi di pianificazione" sotto.

**Campo `category`:**
- Omesso o `"training"` → attività di allenamento, contribuisce al piano e alle analisi di progresso.
- `"social"` → uscita non strutturata (es. hike con amici, niente FC). Si registra solo per il **carico settimanale grezzo** (km, tempo, dislivello). **NON contribuisce** a: analisi di progresso, calcolo trend, metriche di specificità trail, calibrazione zone, valutazione esecuzione. Niente `ai_analysis`, niente `derived.race_match`.
- `"test"` → attività usata come benchmark per calibrare il piano (es. ripetizione del baseline). Riservato per uso futuro.

**Per `activity_type: "run"`** — `totals` include `duration_sec`, `avg_pace_min_per_km`, `gap_min_per_km`, `avg_hr`, `max_hr_observed`, `avg_cadence_spm`, `ef`, `steps`, ecc. Top-level: `splits`, `hr_zones`, `decoupling`, `walk_breaks`, `walks_summary`, `pace_variability`. Sorgente: parsing Garmin/Strava + analisi AI esterna.

**Per `activity_type: "hike"`** — `totals` include `duration_sec` (= totale, start→end), `duration_moving_sec`, `pause_sec`, `descent_m`, `avg_speed_kmh_moving`. Niente `splits`/`hr_zones`/`decoupling`. Sorgente tipica: GPX da Komoot.

**Campi di pianificazione (top-level, opzionali):** vivono nell'attività perché sono *attività-specifici* (cosa portare/mangiare/fare per **questa** uscita), non nella settimana. Si popolano in fase di pianificazione (anche prima dell'esecuzione, su un file attività skeleton) e restano come record.
- `gear_checklist[]` — array di `{category, items[]}`. "Cosa portare" per categoria (Indosso, Zaino, Opzionali, ecc.). Renderizzato da `activity.html` come sezione "Cosa portare".
- `grade_distribution` — distribuzione **pianificata** delle pendenze (calcolata dalle coordinate del percorso scelto, p.es. tour Komoot). Campi: `flat_lt_2`, `rolling_2_5`, `uphill_5_10`, `steep_gt_10`, `down_2_5`, `down_5_10`, `down_gt_10` (percentuali del tracciato, sommano ~100%) + `_source?`, `vs_race_note?`. Da non confondere con `derived.grade_distribution`, che è la distribuzione **misurata** dal GPS post-esecuzione. `activity.html` renderizza la pianificata come "Distribuzione pendenza vs gara" (confronto con `race.json.course_profile_2025.grade_distribution`).
- `nutrition_plan[]` — array di `{category, items[]}`. Piano nutrizione e idratazione (Colazione, Pre-run, Durante, ecc.). Renderizzato come sezione "Piano nutrizione e idratazione".
- `schedule[]` — array di `{time, what}`. Sequenza oraria della giornata di gara/uscita. Renderizzato come sezione "Piano orari".

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
- ❌ Mai duplicare dati tra `profile.json`, `race.json`, `plan.json` e `weeks/`. Profilo = chi sei (anagrafica + zone FC); race = dove vai (gara + percorso); plan = come ti alleni (fasi/template/regole); weeks = il calendario (settimane, sessioni, review).
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

- **Prima di modificare:** leggi sempre lo stato corrente di `profile.json`, `race.json`, `plan.json`, `weeks/index.json` (e i file `week-NN.json` rilevanti), `todo.json` e `data/activities/index.json`.
- **Patch chirurgiche:** modifica solo i campi rilevanti, non riscrivere l'intero JSON.
- **`last_updated`:** aggiornalo nel file modificato (`plan.json`, `weeks/index.json`, `profile.json` o `todo.json`).
- **Validazione:** dopo ogni push, verifica che la pagina renderizzi senza errori (apri la URL live).
- **Domande chirurgiche:** se Fabio dice "ho fatto un lungo", chiedi solo i dati mancanti (durata, dislivello, sensazioni, passo medio). Non rifare l'intake.
- **Calibrazione conservativa:** se i numeri vanno meglio del previsto, alza i volumi al massimo del +10%. Mai di più.
- **Infortuni:** se Fabio segnala dolore, **non** suggerire di "spingere comunque". Riposo + valutazione medica.
- **Hike sociali (`category: "social"`):** ignora questi file quando calcoli progressi, trend, decoupling, polarizzazione, specificità trail. Contano *solo* come carico settimanale grezzo (km/tempo/D+). Non scrivere `ai_analysis` per loro né farne riferimento nelle analisi di altre attività.
- **GPX da Komoot/Garmin/Strava:** parsing locale (Python) — distanza haversine, dislivello con smoothing 5-pt + dead-band 0.5 m, pause = sample con velocità < 0.3 m/s.
