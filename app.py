import os
import requests


from dotenv import load_dotenv
from flask import Flask, request, render_template

load_dotenv() #carico le variabili d'ambiente dal file .env

app = Flask(__name__) #imposto la route dell'applicazione

API_KEY = os.getenv("API_KEY") #recupero la chiave api dal file .env

if not API_KEY:
    raise ValueError("Chiave API non trovata") #manfo un messaggio di errore nel caso in cui non fosse possibile recuperare la chiave

API_BASE_URL = os.getenv("API_BASE_URL") #recupero l'endpoint del modello in uso dalle variabili di sistema

#creo una funzione per interagire con il modello di intelligenza artificiale

def call_ai_model(prompt):
    
    headers = {
        "Content-Type": "application/json"
    }

    params = {
        "key": API_KEY
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

    try:
        response = requests.post(API_BASE_URL, headers=headers, params=params, json=payload)
        response.raise_for_status()
        response_data = response.json()

        if response_data and "candidates" in response_data and response_data["candidates"]:
            generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return generated_text
        else:
            return "Nessuna risposta valida dall'API."

    except requests.exceptions.HTTPError as err:
        print(f"Errore HTTP: {err}")
        print(f"Risposta API: {response.text}")
        return f"Errore dall'API: {err}. Dettagli: {response.text}"
    except requests.exceptions.ConnectionError as err:
        print(f"Errore di connessione: {err}")
        return "Errore di connessione all'API."
    except requests.exceptions.Timeout as err:
        print(f"Timeout della richiesta: {err}")
        return "La richiesta all'API è scaduta."
    except requests.exceptions.RequestException as err:
        print(f"Errore generico della richiesta: {err}")
        return "Si è verificato un errore durante la chiamata all'API."
    except KeyError as err:
        print(f"Errore nel parsing della risposta JSON: Chiave mancante {err}")
        print(f"Risposta completa: {response_data}")
        return "Errore nel parsing della risposta API."
    except Exception as e:
        print(f"Errore inaspettato: {e}")
        return "Si è verificato un errore inaspettato."
    

@app.route('/', methods = ["GET"])
def show_form():
    return render_template('index.html')


#devo inserire un endpoint per ricevere il codice e costruire il prompt

@app.route('/code_reviewer', methods = ["POST"])
def review_code():
    python_code = request.form.get("input_code")

    if not python_code:
        return render_template('index.html', error = "Inserisci il codice da revisionare")
    
    prompt = (
        "Correggi questo codice python, inserendo commenti per segnalre:\n"
        "1. Errori di sintassi \n"
        "2. Errori di logica \n"
        "3. Variabili non utilizzate\n"
        "4. Genera tutti i docstrings necessari \n"
        "Inoltre, inserisci, in fondo al codice, una nota che indichi dei suggerimenti di stile basati su PEP8.\n"
        "Il codice python da correggere è:\n\n"
        f"{python_code}"
        ""
        )
    
    reviewed_code = call_ai_model(prompt= prompt)

    return render_template('index.html', original_code = python_code, reviewed_code = reviewed_code)


    

if __name__ == '__main__':
    app.run(debug=True)




