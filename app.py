import os
import requests



from dotenv import load_dotenv
from flask import Flask, request, render_template

load_dotenv() #carico le variabili d'ambiente dal file .env

app = Flask(__name__) #imposto la route dell'applicazione

OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME") #recupero la chiave api dal file .env

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL") #recupero l'endpoint del modello in uso dalle variabili di sistema

if OLLAMA_API_BASE_URL:
    os.environ["OLLAMA_HOST"] = OLLAMA_API_BASE_URL

import ollama #Sono stato costretto a spostare l'operazione di import del modulo perché importarlo prima settava OLLAMA_HOST in automatico e non leggeva la modifica


GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

GEMINI_API_BASE_URL=str(os.getenv("GEMINI_API_BASE_URL"))

if not GEMINI_API_KEY and not OLLAMA_MODEL_NAME: #controlla che sia disponibile almeno una chiave
    raise ValueError("Impossibile trovare una chiave API valida")




def call_gemini(prompt:str) -> str:
    '''
        Questa è la funzione per interagire con le API di Gemini.
        Riceve in input un prompt e fornisce in output il codice commentato, estraendo l'originale dalla textarea
    '''
    
    # Definizione dei parametri necessari per interagire con l'API di gemini

    headers = {
        "Content-Type": "application/json"
    }

    params = {
        "key": GEMINI_API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # Blocco per la generazione dell'output
    # L'istruzione try invia a gemini la richiesta e salva i risultati in resposnse in formato json, conver

    try:
        response = requests.post(GEMINI_API_BASE_URL, headers=headers, params=params, json=payload)
        response.raise_for_status()
        response_data = response.json()

        if response_data and "candidates" in response_data and response_data["candidates"]:
            generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return generated_text
        else:
            return "Nessuna risposta valida dall'API."

    except requests.exceptions.HTTPError as err: #Gestisce gli errori HTTP con codice >= 400
        print(f"Errore HTTP: {err}")
        print(f"Risposta API: {response.text}") # type: ignore
        return f"Errore dall'API: {err}. Dettagli: {response.text}" # type: ignore
    except requests.exceptions.ConnectionError as err: #Gestisce gli errori di connesione
        print(f"Errore di connessione: {err}")
        return "Errore di connessione all'API."
    except requests.exceptions.Timeout as err: #Gestisce gli errori causati da tempi di attesa troppo lunghi, che fanno scadere la richiesta all?'API
        print(f"Timeout della richiesta: {err}")
        return "La richiesta all'API è scaduta."
    except requests.exceptions.RequestException as err: #Gestisce erroi generici
        print(f"Errore generico della richiesta: {err}")
        return "Si è verificato un errore durante la chiamata all'API."
    except KeyError as err: #Gestisce gli errori dovuti ad un formato JSON non previsto, mostrando comunque il risultato ottenuto
        print(f"Errore nel parsing della risposta JSON: Chiave mancante {err}")
        print(f"Risposta completa: {response_data}") # type: ignore
        return "Errore nel parsing della risposta API."
    except Exception as e: #Cattura errori di logica, di runtime o altri errori dovuti a mancanze nel codice
        print(f"Errore inaspettato: {e}")
        return "Si è verificato un errore inaspettato."
    



def call_ollama(prompt: str, model_name: str) -> str:
    '''
        Questa è la funzione per interagire con Ollama (locale)
        Riceve in input un prompt e fornisce in output il codice commentato, estraendo l'originale dalla textarea
    '''    

    #In questo caso, a differenza dell'interazione con l'API di gemini, non serve la dichiarazione dei parametri headers, params e payload perché
    #gestita automatica dal modulo ollama
    
    try:
        response_data = ollama.generate(model=model_name, prompt=prompt, options={'temperature':0.1}) #Cattura la risposta del modello (che restituisce un dizionario python)


        if response_data and "response" in response_data: #Controlla che sia stato effettivamente ricevuta una risposta e che questa contenga la chiave "response"
            generated_text = response_data["response"] 
            return generated_text
        else:
            return "Nessuna risposta valida dall'API di Ollama."
        

        
    except ollama.ResponseError as e:
        # Questo errore viene sollevato dalla libreria ollama per risposte non 2xx dal server Ollama: in sostanza, che sia stata ricevuta correttamente la richiesta http
        print(f"Errore dalla risposta di Ollama (ad es. modello non trovato): {e}")
        return f"Errore dall'API di Ollama: {e}"
    except Exception as e:
        # Cattura altri errori generici che potrebbero verificarsi durante la chiamata
        print(f"Errore inaspettato durante la chiamata a Ollama: {e}")
        return f"Si è verificato un errore inaspettato: {e}"

#def clean_code(code: str) -> str:

    prompt = (
        "Sei un esperto di scrittura di codice python pulito e funzionale.\n"
        "Elimina le zone di markdown che delimitano il codice e riordina i commenti, riscrivendoli tutti nella forma # commento.\n"
        "Il codice da pulire è: \n\n"
        f"{code}\n\n"
        "NON MODIFICARE ALTRO."
    )

    cleaned_code = ""

    if OLLAMA_MODEL_NAME and not GEMINI_API_KEY:
        cleaned_code = call_ollama(prompt=prompt, model_name=OLLAMA_MODEL_NAME)

    else:
        cleaned_code = call_gemini(prompt=prompt)
    
    return cleaned_code

def get_ai_response(prompt: str) -> str | None :

    '''
        Funzione che chiama uno dei due modelli disponibili (o entrambi) e restituisce il testo generato
    '''

    if OLLAMA_MODEL_NAME and not GEMINI_API_KEY:
        return call_ollama(prompt=prompt, model_name=OLLAMA_MODEL_NAME)
    
    elif GEMINI_API_KEY and not OLLAMA_MODEL_NAME:
        return call_gemini(prompt=prompt)
        

    elif GEMINI_API_KEY and OLLAMA_MODEL_NAME:
        gemini_response = call_gemini(prompt=prompt)
        ollama_response = call_ollama(prompt=prompt, model_name=OLLAMA_MODEL_NAME)

        return "REVISIONE GEMINI:\n" + f"{gemini_response}\n" + "REVISIONE OLLAMA:\n" + f"{ollama_response}"

    else:
        return "Errore: Nessun modello API (Gemini o Ollama) configurato correttamente. Controllare le variabili d'ambiente."

    


@app.route('/', methods = ["GET"])
def show_form():
    return render_template('index.html', input_code="") #mostra la pagina html, impostanto il campo di input per il codice vuoto


@app.route('/code_reviewer', methods = ["POST"])
def review_code():

    python_code = request.form.get("input_code")

    if not python_code: #Se il campo viene lasciato vuole lancia un errore 
        return render_template('index.html', error = "Inserisci il codice da revisionare")

    prompt = ( #Costruzione del prompt generico per gli LLM
        "Sei un esperto in revisione di codice Python.\n"
        "Il tuo compito è fornire una revisione sintetica e focalizzata del codice Python fornito.\n"
        "La revisione deve includere:\n"
        "- Commenti direttamente nel codice (come commenti Python `#`):\n"
        "  - Segnalazioni di errori di sintassi.\n"
        "  - Segnalazione di errori di logica.\n"
        "  - Identificazione di variabili non utilizzate.\n"
        "  - Suggerimenti per imprecisioni stilistiche basate su PEP8.\n"
        "  - Aggiunta di docstrings (se mancanti) per le funzioni dichiarate dall'utente. Utilizza il formato `'''Docstring della funzione'''`.\n"
        "**Regole di output stringenti:**\n"
        "- NON MODIFICARE ASSOLUTAMENTE il codice Python originale fornito in alcun modo.\n"
        "- NON AGGIUNGERE NESSUN CODICE PYTHON NUOVO (es. nuove funzioni, classi, variabili, importazioni) che non sia presente nell'input originale.\n"
        "- NON COMMENTARE ELEMENTI CHE NON SONO PRESENTI NEL CODICE FORNITO.\n"
        "- Tutti i commenti devono essere nella forma '# commento'.\n"
        "- L'output deve contenere ESATTAMENTE il codice Python fornito dall'utente, con l'aggiunta dei soli commenti e docstrings.\n"
        "- NON includere testo introduttivo o conclusivo (es. 'Ecco la revisione:', 'Spero sia utile', ecc.).\n"
        "- NON racchiudere l'output in blocchi di codice Markdown (es. ```python o ```).\n"
        "- NON aggiungere funzioni o dichiarazioni: se nel codice non ci sono correzioni, non inventare altre funzioni per commentarne lo stile.\n"
        "Il codice da commentare è:\n"
        f"{python_code}"
    )
     
    reviewed_code = get_ai_response(prompt=prompt)
    
    #Debug per highlight.js
    print("REVIEWED_CODE RAW:")
    print(repr(reviewed_code))

    return render_template('index.html', original_code = python_code, reviewed_code = reviewed_code)


if __name__ == '__main__':
    app.run(debug=True)




