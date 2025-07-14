import os
import sys
import subprocess
import time

import requests

from dotenv import load_dotenv

ENV_FILE = "/app/.env"
OLLAMA_SERVER_URL = "http://ollama_server:11434"
OLLAMA_MODEL_NAME = "codegemma" 


def create_env_file():
    """Crea un file di configurazione .env predefinito se non esiste.

    Questa funzione verifica l'esistenza del file specificato da `ENV_FILE`.
    Se il file non viene trovato, ne crea uno nuovo con un contenuto predefinito,
    che include placeholder per chiavi API remote e configurazioni per Ollama.
    Dopo la creazione, stampa istruzioni importanti per l'utente sulla modifica manuale
    del file e quindi termina l'applicazione con un codice di uscita per forzare un
    riavvio e la configurazione da parte dell'utente.

    Returns:
        None: La funzione non restituisce alcun valore, ma termina l'applicazione
              tramite `sys.exit()`.

    Raises:
        SystemExit: Termina l'applicazione con codice 1 sia in caso di successo
                    (per richiedere all'utente la configurazione) che in caso di errore
                    durante la creazione del file.
    """
    print(f"File '{ENV_FILE}' non trovato. Creazione di un file di .env ...")
    env_content = f"""# Variabili d'ambiente per Jarvis Code Assistant

# --- Configurazione per API remota ---
GEMINI_API_KEY="Inserisci la tua api key qui"
GEMINI_API_BASE_URL="Inserisci Il tuo endpoint url qui"

# --- Configurazione per Ollama (modello locale) ---
# Il nome del modello scaricato da Ollama. Quello predefinito è codegemma, ma potete scaricarne un altro e cambiare qua il nome)
MODEL_NAME="{OLLAMA_MODEL_NAME}"
# L'URL per comunicare con il servizio Ollama all'interno della rete Docker Compose
LOCAL_BASE_URL="{OLLAMA_SERVER_URL}"
"""
    try:
        with open(ENV_FILE, 'w') as f:
            f.write(env_content)
        print(f"File '{ENV_FILE}' creato con successo nella directory del progetto host.")
        print("******************************************************************")
        print("ATTENZIONE: Il file .env è stato creato. DEVI modificarlo manualmente.")
        print(f"Apri il file '{ENV_FILE}' nella directory del tuo progetto sul tuo computer host.")
        print("Inserisci le tue API Key e/o configura i dettagli di Ollama.")
        print("Salva il file e poi riavvia 'docker-compose up'.")
        print("******************************************************************")
        sys.exit(1) # Esce con errore per fermare il container e segnalare all'utente di configurare
    except Exception as e:
        print(f"Errore durante la creazione del file '{ENV_FILE}': {e}")
        print("Si prega di creare manualmente il file .env e riavviare l'applicazione.")
        sys.exit(1) # Esce con errore se la creazione fallisce


def wait_for_ollama():
    """Attende che il servizio Ollama sia disponibile.

    Questa funzione tenta ripetutamente di connettersi all'URL del server Ollama
    specificato da `OLLAMA_SERVER_URL` fino a quando non è accessibile.
    Esegue richieste HEAD e verifica uno stato di risposta HTTP 200.
    In caso di fallimento della connessione (`requests.exceptions.ConnectionError`),
    timeout (`requests.exceptions.Timeout`) o altri errori, attende 5 secondi
    e riprova.

    Returns:
        None: La funzione termina quando Ollama è disponibile e non restituisce alcun valore.
    """
    print(f"Attendendo che il servizio Ollama sia disponibile su {OLLAMA_SERVER_URL}...")
    while True:
        try:
            response = requests.head(OLLAMA_SERVER_URL, timeout=5)
            if response.status_code == 200:
                print("Ollama è disponibile.")
                break
        except requests.exceptions.ConnectionError:
            print("Ollama non è ancora disponibile, riprovo tra 5 secondi...")
        except requests.exceptions.Timeout:
            print("Timeout durante l'attesa di Ollama, riprovo tra 5 secondi...")
        except Exception as e:
            print(f"Errore inatteso durante l'attesa di Ollama: {e}, riprovo tra 5 secondi...")
        time.sleep(5)


def pull_ollama_model():
    """Scarica il modello Ollama specificato.

    Questa funzione configura la variabile d'ambiente `OLLAMA_HOST` per puntare al
    server Ollama e quindi esegue il comando `ollama pull` utilizzando `subprocess`
    per scaricare il modello identificato da `OLLAMA_MODEL_NAME`.
    Viene fornito un feedback sull'output del comando Ollama e vengono gestiti
    errori comuni come il fallimento del sottoprocesso o l'assenza del comando 'ollama'.

    Returns:
        None: La funzione non restituisce alcun valore; il suo scopo è l'esecuzione di un comando esterno.
    """
    print(f"Scaricando il modello '{OLLAMA_MODEL_NAME}' tramite il client Ollama nel container flask_app...")
    os.environ["OLLAMA_HOST"] = OLLAMA_SERVER_URL
    
    try:
        result = subprocess.run(['ollama', 'pull', OLLAMA_MODEL_NAME], check=True, capture_output=True, text=True)
        print(f"Output Ollama pull:\n{result.stdout}")
        if result.stderr:
            print(f"Errore/Avviso Ollama pull:\n{result.stderr}")
        print(f"Modello '{OLLAMA_MODEL_NAME}' gestito.")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante il download del modello '{OLLAMA_MODEL_NAME}':")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        print("Controlla i log di ollama_server o la connessione.")
    except FileNotFoundError:
        print("Errore: il comando 'ollama' non è stato trovato. Assicurati che il client Ollama sia installato nel Dockerfile.")
    except Exception as e:
        print(f"Si è verificato un errore inatteso durante il pull del modello Ollama: {e}")


def main():
    """Punto di ingresso principale dell'applicazione.

    Questa funzione orchestra il processo di avvio dell'applicazione Flask,
    gestendo la configurazione iniziale e la dipendenza da Ollama.
    Verifica la presenza del file `.env` e, se assente, lo crea.
    Successivamente, carica le variabili d'ambiente. Se le variabili
    `MODEL_NAME` e `LOCAL_BASE_URL` sono configurate (indicando l'uso di Ollama locale),
    attende che il servizio Ollama sia disponibile e scarica il modello specificato.
    Infine, avvia l'applicazione Flask sostituendo il processo corrente.

    Returns:
        None: Questa funzione non restituisce mai un valore direttamente, poiché
              sostituisce il processo corrente con `app.py` tramite `os.execv`.

    Raises:
        SystemExit: Chiamata indirettamente tramite `create_env_file()` se il file .env
                    non è presente e deve essere creato, terminando il programma.
        OSError: Potrebbe essere sollevata da `os.execv` se l'eseguibile Python o lo script
                 `app.py` non può essere trovato o eseguito.
    """
     
    if not os.path.exists(ENV_FILE):
        create_env_file()
 
    print("File .env trovato. Procedendo con l'avvio dell'applicazione Flask...")
    
    load_dotenv(dotenv_path=ENV_FILE)
    
    if os.getenv("MODEL_NAME") and os.getenv("LOCAL_BASE_URL"):
        os.environ["OLLAMA_HOST"] = str(os.getenv("LOCAL_BASE_URL"))
        wait_for_ollama()
        pull_ollama_model()
    else:
        print("Ollama non configurato nel .env, saltando attesa e pull del modello Ollama.")

    print("Avvio dell'applicazione Flask...")
    os.execv(sys.executable, ['python', 'app.py'])

if __name__ == "__main__":
    main()
