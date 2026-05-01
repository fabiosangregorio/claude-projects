# claude-projects

Repo per progetti personali pianificati con Claude. Ogni cartella è un progetto autonomo con una pagina HTML hostata su GitHub Pages.

🔗 **GitHub Pages:** https://fabiosangregorio.github.io/claude-projects/

---

## Tipi di progetto

Il repo ospita diversi tipi di progetto. Ognuno ha le sue convenzioni, documentate nel `README.md` della propria cartella.

| Tipo | Stile | Esempi | Convenzioni in |
|---|---|---|---|
| **DIY / falegnameria** | Pagina statica autoportante. Tutti i dati nell'HTML. | `mobile-lavatrice`, `scaffale-erbe` | Sezione "Progetti DIY" sotto |
| **Sport / allenamento** | Pagina + JSON separati. Layer presentazione vs. dati. | `trail-brenta-2026` | `trail-brenta-2026/README.md` |

**Regola generale:** prima di lavorare in una cartella, leggi il suo `README.md` se esiste, altrimenti applica le convenzioni del tipo che meglio descrive il progetto.

---

## Come usare questa repo

Ogni progetto ha la sua cartella con un `index.html` che viene servito su GitHub Pages.

---

## Progetti DIY — istruzioni per Claude

Quando Fabio ti chiede di pianificare un nuovo progetto di falegnameria/DIY, segui questa procedura. È il risultato di tutto quello che abbiamo imparato facendo i primi progetti.

> Per progetti **non-DIY** (es. allenamento sportivo) leggi il README della cartella specifica — ogni tipo ha le sue convenzioni.

### 1. Raccolta vincoli

Prima di fare qualsiasi cosa, raccogli TUTTI i vincoli fisici:

- **Dimensioni dell'oggetto da contenere** — cerca online le specifiche esatte (non fidarti di misure "a occhio")
- **Vincoli dello spazio** — altezza massima (finestre, mensole sopra), larghezza massima (muri, altri mobili), profondità massima
- **Giochi necessari** — chiedi a Fabio quanto gioco vuole. Il gioco dipende dal progetto: oggetti che vibrano ne richiedono di più, oggetti statici possono stare a filo
- **Finitura desiderata** — colore, se i fissaggi devono essere nascosti o visibili

Fai domande a scelta multipla per le decisioni che Fabio deve prendere.

### 2. Scelta dei materiali — PRIMA cerca i prodotti disponibili

**ERRORE CRITICO DA EVITARE:** Non progettare le misure del mobile e poi cercare il legno. Fai il contrario: cerca PRIMA cosa è disponibile nei negozi (OBI, Leroy Merlin, ecc.) e progetta il mobile attorno alle misure dei pannelli che puoi comprare.

Questo perché:
- I pannelli pretagliati hanno misure standard (es. 100×60, 200×60, 250×60 cm)
- Progettare attorno a queste misure riduce gli sfridi e i tagli (= risparmio)
- Lo spessore del pannello cambia TUTTE le misure derivate

**Regola:** cerca i prezzi online PRIMA di finalizzare le dimensioni. Confronta almeno 2 negozi.

### 3. Scelta dello spessore

- **18mm** — standard per mobili, robusto, più materiale per viti/spinotti
- **16mm** — va bene per carichi leggeri e luci corte (<80cm). Costa meno. Usa spinotti ø6 (non ø8) per avere 5mm di materiale per lato
- **Sotto i 16mm** — solo per schienali (faesite 3-3.5mm) o fondi cassetto

Per decidere: se il risparmio è significativo e il mobile ha carichi leggeri, il 16mm va bene. Altrimenti 18mm.

**IMPORTANTE:** se cambi spessore dopo aver già calcolato le misure, DEVI ricalcolare TUTTO: larghezze esterne, dimensioni ripiani, schienale, piano di taglio, e tutte le misure nelle istruzioni di montaggio.

### 4. Link e prezzi prodotti

**Lezione importante:** i link diretti ai prodotti OBI e Leroy Merlin si rompono spesso, e `web_fetch` è bloccato da entrambi i siti (anti-bot + dominio non nella whitelist di rete). Usa questa strategia:

#### Verifica prezzi con Google snippets

Dato che non è possibile accedere direttamente alle pagine prodotto, usa `web_search` con query mirate per estrarre dati strutturati dagli snippet di Google:

```
site:leroymerlin.it "CODICE_REF" nome prodotto prezzo
```

Oppure senza ref:
```
site:leroymerlin.it bordo preincollato bianco 28mm prezzo
```

Questo restituisce dagli snippet: **nome completo, prezzo, ref, rating, numero recensioni** — senza mai visitare la pagina. Funziona in modo affidabile per:
- ✅ Prodotti con ref noto → risultati molto ricchi
- ✅ Prodotti specifici (marca + dimensione) → trova il prodotto giusto
- ⚠️ Prodotti "su misura" / solo negozio → ref sì, prezzo spesso assente
- ⚠️ Prodotti generici (viti, feltrini) → risultati multipli, serve disambiguare

**Fai SEMPRE questa verifica prima di pubblicare la pagina** per ogni prodotto con prezzo > €3. Permette di:
1. Confermare che il prodotto esiste ancora nel catalogo
2. Verificare che il prezzo sia aggiornato
3. Trovare il ref e il link diretto aggiornato

#### Strategia link nella pagina

1. **Link diretti verificati** — quando il metodo snippet sopra restituisce un URL `/prodotti/...nome-prodotto-REF.html`, usalo come link nella shopping list. Questi URL contengono il ref numerico e puntano alla pagina prodotto esatta.
2. **Link di ricerca** come fallback per prodotti generici o quando il link diretto non emerge dagli snippet: `https://www.leroymerlin.it/search?q=parole+chiave` o `https://www.obi-italia.it/search/parole%20chiave`
3. **Mai inventare URL** — se non trovi il link diretto, usa la ricerca
4. **Vecchi URL `/catalogo/`** — sono deprecati e bloccati da robots.txt. Se li trovi, sostituiscili con il formato `/prodotti/` equivalente.

I link di ricerca funzionano sempre e portano direttamente ai risultati filtrati quando aperti dal telefono in negozio. I link diretti verificati sono preferibili perché portano alla scheda prodotto con prezzo, disponibilità e recensioni.

### 5. Istruzioni di montaggio

Fabio non sa nulla di falegnameria. Le istruzioni devono essere:

- **Numerate step by step** — un'azione per step
- **Dettagliate** — spiega COME fare ogni cosa (es. "passa il ferro da stiro a 170°C lentamente, premi, rifila con cutter")
- **Con un 💡 Tip per ogni step** — l'errore più comune o il trucco che fa la differenza
- **Con le misure esatte** — non "fora al centro" ma "fora a 8mm dal bordo"
- **Con le regole di sicurezza del materiale** — es. per il truciolare 16mm: pre-fora SEMPRE, mai a meno di 3cm dal bordo, coppia bassa sull'avvitatore

### 6. Output HTML

L'HTML deve contenere:
- **Freccia "← Progetti" nell'header** — link di ritorno all'indice (`https://fabiosangregorio.github.io/claude-projects/`). Usa questo snippet nell'header, subito prima dell'`<h1>`:
  ```html
  <a class="back" href="https://fabiosangregorio.github.io/claude-projects/"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>Progetti</a>
  ```
  E nel CSS la classe `.back`:
  ```css
  .back{display:inline-flex;align-items:center;gap:.35rem;font-family:'Space Mono',monospace;font-size:.75rem;color:var(--tx2);text-decoration:none;padding:.35rem .6rem;border-radius:6px;border:1px solid var(--bd);background:var(--sf);transition:border-color .2s,color .2s;margin-bottom:1rem}
  .back:hover{border-color:var(--ac);color:var(--ac)}
  .back svg{width:14px;height:14px}
  ```
- **Paragrafo introduttivo** — descrizione del goal del progetto
- **Sezione dimensioni** — con card per ogni misura e stack verticale (o equivalente)
- **Vista esplosa SVG** — schema con i pezzi colorati, le misure e il tipo di fissaggio
- **Distinta base** — tabella con ID pezzo, nome, misure, quantità, fonte. Le misure usano sempre la notazione **A×L×P** (Altezza × Larghezza × Profondità), dove:
  - Per pezzi verticali (fianchi, gambe): A=altezza in opera, L=larghezza, P=spessore del pannello
  - Per pezzi orizzontali (ripiani): A=altezza in opera (= spessore del pannello), L=larghezza, P=profondità
  - L'intestazione colonna nella tabella deve essere `mm (A×L×P)`
- **Piano di taglio SVG** — visualizzazione grafica di come ricavare i pezzi dai pannelli acquistati, con misure quotate e sfridi evidenziati
- **Lista spesa interattiva** — con checkbox localStorage (per spuntare in negozio dal telefono), link ai prodotti, prezzi
- **Istruzioni di montaggio dettagliate** — step by step per principianti con tip per ogni step
- **Budget** — tabella riepilogativa con totale

Stile: dark theme, font Space Mono + DM Sans, colori GitHub-style. Mobile-first.

### 7. Deploy su GitHub Pages

- Crea la cartella `nome-progetto/` nella repo `fabiosangregorio/claude-projects`
- Metti il file come `index.html`
- Usa l'API GitHub con il PAT per pushare
- **Aggiorna il dizionario `META` in `index.html`** (nella root) aggiungendo una entry per il nuovo progetto con descrizione e tag
- La pagina sarà live su `https://fabiosangregorio.github.io/claude-projects/nome-progetto/`

### 8. Double-check finale

**SEMPRE** fare un double-check di TUTTE le misure alla fine:
- Cerca valori vecchi/sbagliati con grep nel file HTML
- Verifica che lo stack verticale torni (somma = altezza totale)
- Verifica coerenza tra: header, card dimensioni, SVG, distinta, piano taglio, istruzioni montaggio, lista spesa
- Se hai cambiato spessore/misure durante il progetto, cerca tutti i valori vecchi nel file e sostituiscili

---

## Progetti

| Progetto | Tipo | Descrizione | Link |
|---|---|---|---|
| [mobile-lavatrice](mobile-lavatrice/) | DIY | Mobile a ponte per lavatrice LG F10B8NDA | [Live](https://fabiosangregorio.github.io/claude-projects/mobile-lavatrice/) |
| [scaffale-erbe](scaffale-erbe/) | DIY | Scaffale a scala per erbe aromatiche sul balcone | [Live](https://fabiosangregorio.github.io/claude-projects/scaffale-erbe/) |
| [trail-brenta-2026](trail-brenta-2026/) | Sport | Piano allenamento per la Dolomiti di Brenta Trail 21K | [Live](https://fabiosangregorio.github.io/claude-projects/trail-brenta-2026/) |

