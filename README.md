# JARVIS CODE ASSISTANT

Un assistente di intelligenza artificiale per revisionare il tuo codice python.  
---

## Funzionalità

Sfruttando modelli di vari LLM (sia via API Gemini che in locale con Ollama), Jarvis:

- Individua errori sintattici nel tuo codice;
- Individua errori di logica che impediscono il corretto funzionamento del tuo codice;
- Aggiunge per te i docstring alle tue funzioni;
- Ti suggerisce miglioramenti stilistici basati sulle convenzioni PEP8, standardizzando la forma del tuo codice.

Il tutto attraverso una comoda interfaccia web che permette di fornire il tuo codice e copiare i suggerimenti e i docstring che ti verrano forniti,  
e sfruttando le potenzialità di isolamento di Docker, così da non interferire con il tuo OS.  
---

## Requisiti

- Docker e Docker Compose installati sul tuo dispositivo. Qui le guide all'installazione di:
  - Docker: https://docs.docker.com/get-started/get-docker/
  - Docker Compose: https://docs.docker.com/compose/install/
- Una chiave API di Gemini. Qui gli indirizzi per:
  - La chiave API: https://aistudio.google.com/apikey
  - L'endpoint url è: https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
  - N.B.: L'endpoint fornito è ESCLUSIVAMENTE per il modello 2.5-flash, per usare altri modelli dovrai usare un altro endpoint
- Installare GIT sul proprio dispositivo:
  - https://git-scm.com/downloads  
---

## Installazione

1. Clonare il repository di Github sul proprio dispositivo:
   - `git clone https://github.com/tuo-utente/ai-code-reviewer.git`
2. Accedere alla cartella in locale:
   - `cd ai-code-reviewer`
3. Crea un file `.env` nella cartella (IL NOME DEVE ESSERE `.env`)
4. Imposta i valori del file `.env`: Ricorda di impostare una sola coppia di valori, commentando l'altra con '#' ad inizio riga.
    - OLLAMA_MODEL_NAME=codegemma
    - OLLAMA_API_BASE_URL=http://ollama_server:11434
    - GEMINI_API_KEY='Tua_chiave_API_di_Gemini'
    - GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
5. Costruisci l'immagine di docker:
- `docker compose up --build`
6. Avvia l'applicazione:
- Apri il tuo browser e naviga all'indirizzo: `http://127.0.0.1:5000/`  
---

## Personalizzazione

1. Cambiare modello Ollama:
1. Apri il file `docker-compose.yml`
2. Naviga alla riga 16 del file
3. Modifica `codegemma` con un modello di Ollama a tua scelta
4. Nel file `.env` modifica la voce `OLLAMA_MODEL_NAME="codegemma"` con `OLLAMA_MODEL_NAME="nome_modello_scelto"`
5. Salva il file `.env` e riavvia l'applicazione

2. Cambiare modello Gemini:
1. Scegli il tuo modello di Gemini
2. Genera la chiave API per il modello che hai scelto
3. Cerca l'endpoint dedicato a quel modello
4. Inserisci la chiave API di Gemini nel file `.env`
5. Sostituisci l'endpoint fornito con quello dedicato al modello che hai scelto
6. Salva il file `.env` e riavvia l'app  
---

## Troubleshooting

### Errore: Failed to connect to Ollama

- Verifica che Ollama sia accessibile navigando all'indirizzo `http://localhost:11434/`

### Errore: Docker non riesce a trovare il modello

- Ricordati di modificare il file `.env` e il `docker-compose.yml` come indicato in 'Personalizzazione'

### Errore Ollama: RAM insufficiente

- Libera la RAM del tuo dispositivo e riavvia il container

### Errore modelli: Sia gemini che Ollama sono configurati
- Verifica che entrambe siano settate le tue variabili di ambiente con il comando 'env' su terminale. Poi 'unset "valori da non usare"'
