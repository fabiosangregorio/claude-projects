# claude-projects

Repo per progetti DIY pianificati con Claude. Ogni cartella è un progetto con una pagina HTML hostata su GitHub Pages.

🔗 **GitHub Pages:** https://fabiosangregorio.github.io/claude-projects/

---

## Come usare questa repo

Ogni progetto ha la sua cartella con un `index.html` che viene servito su GitHub Pages. La pagina contiene tutto: dimensioni, distinta, piano taglio, lista spesa interattiva (con localStorage per spuntare in negozio), istruzioni di montaggio, e budget.

---

## Istruzioni per Claude: come creare un piano di progetto DIY

Quando Fabio ti chiede di pianificare un nuovo progetto di falegnameria/DIY, segui questa procedura. È il risultato di tutto quello che abbiamo imparato facendo i primi progetti.

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

### 4. Link ai prodotti

**Lezione importante:** i link diretti ai prodotti OBI e Leroy Merlin si rompono spesso. Usa questa strategia:

1. **Link diretti** dove li trovi e funzionano (verifica con web_fetch se possibile)
2. **Link di ricerca** come fallback: `https://www.leroymerlin.it/search?q=parole+chiave` o `https://www.obi-italia.it/search/parole%20chiave`
3. **Mai inventare URL** — se non trovi il link diretto, usa la ricerca

I link di ricerca funzionano sempre e portano direttamente ai risultati filtrati quando aperti dal telefono in negozio.

### 5. Istruzioni di montaggio

Fabio non sa nulla di falegnameria. Le istruzioni devono essere:

- **Numerate step by step** — un'azione per step
- **Dettagliate** — spiega COME fare ogni cosa (es. "passa il ferro da stiro a 170°C lentamente, premi, rifila con cutter")
- **Con un 💡 Tip per ogni step** — l'errore più comune o il trucco che fa la differenza
- **Con le misure esatte** — non "fora al centro" ma "fora a 8mm dal bordo"
- **Con le regole di sicurezza del materiale** — es. per il truciolare 16mm: pre-fora SEMPRE, mai a meno di 3cm dal bordo, coppia bassa sull'avvitatore

### 6. Output HTML

L'HTML deve contenere:
- **Paragrafo introduttivo** — descrizione del goal del progetto
- **Sezione dimensioni** — con card per ogni misura e stack verticale (o equivalente)
- **Vista esplosa SVG** — schema con i pezzi colorati, le misure e il tipo di fissaggio
- **Distinta base** — tabella con ID pezzo, nome, misure, quantità, fonte
- **Piano di taglio SVG** — visualizzazione grafica di come ricavare i pezzi dai pannelli acquistati, con misure quotate e sfridi evidenziati
- **Lista spesa interattiva** — con checkbox localStorage (per spuntare in negozio dal telefono), link ai prodotti, prezzi
- **Istruzioni di montaggio dettagliate** — step by step per principianti con tip per ogni step
- **Budget** — tabella riepilogativa con totale

Stile: dark theme, font Space Mono + DM Sans, colori GitHub-style. Mobile-first.

### 7. Deploy su GitHub Pages

- Crea la cartella `nome-progetto/` nella repo `fabiosangregorio/claude-projects`
- Metti il file come `index.html`
- Usa l'API GitHub con il PAT per pushare
- La pagina sarà live su `https://fabiosangregorio.github.io/claude-projects/nome-progetto/`

### 8. Double-check finale

**SEMPRE** fare un double-check di TUTTE le misure alla fine:
- Cerca valori vecchi/sbagliati con grep nel file HTML
- Verifica che lo stack verticale torni (somma = altezza totale)
- Verifica coerenza tra: header, card dimensioni, SVG, distinta, piano taglio, istruzioni montaggio, lista spesa
- Se hai cambiato spessore/misure durante il progetto, cerca tutti i valori vecchi nel file e sostituiscili

---

## Progetti

| Progetto | Descrizione | Link |
|---|---|---|
| [mobile-lavatrice](mobile-lavatrice/) | Mobile a ponte per lavatrice LG F10B8NDA | [Live](https://fabiosangregorio.github.io/claude-projects/mobile-lavatrice/) |
