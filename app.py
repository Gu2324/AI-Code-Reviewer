from flask import Flask, request, render_template

from llm_service import LLMService

app = Flask(__name__)


@app.route('/', methods=["GET"])
def show_form():
    """Rendering della Pagina Principale dell'Applicazione

        Questa funzione è incaricata di visualizzare la pagina principale dell'applicazione.

        Gestisce le richieste GET all'URL radice ('/') e visualizza il template index.html. 
        Inizializza il campo del codice di input come vuoto e imposta il tipo di revisione selezionato di default su 'bug_detection'.
        
        Valori di Ritorno (Returns)
            str: Il template index.html renderizzato con i valori predefiniti per il codice di input e il tipo di revisione.
    """
    return render_template('index.html', input_code="", selected_review_type="bug_detection")


@app.route('/code_reviewer', methods=["POST"])
def review_code():
    """Gestisce le Richieste di Code Review

        Questa funzione è responsabile dell'elaborazione delle richieste di revisione del codice Python inviate dagli utenti.

        Riceve uno snippet di codice Python e il tipo di revisione desiderato tramite una richiesta POST. 
        Esegue una validazione iniziale dell'input, poi inizializza un LLMService per generare una revisione del codice in base al tipo selezionato. 
        Il risultato di questa revisione, o qualsiasi messaggio di errore riscontrato durante il processo, viene poi mostrato all'utente tramite il template index.html.

        Argomenti (Args)

            input_code (str): Lo snippet di codice Python che l'utente ha inviato per la revisione. Questo valore viene recuperato da request.form.get("input_code").

            review_type (str, optional): Il tipo di revisione del codice richiesto (ad esempio, "bug_detection").
            Se non specificato, il valore predefinito è "bug_detection". Anche questo viene recuperato da request.form.get("review_type").

        Valori di Ritorno (Returns)

            str: Il template index.html renderizzato, che include il codice revisionato, il codice originale inviato, il tipo di revisione scelto o un messaggio di errore.

        Eccezioni Sollevate (Raises)

            ValueError: Questa eccezione viene sollevata se la configurazione del servizio LLM non è valida durante l'inizializzazione
            (ad esempio, mancano le chiavi API necessarie) o se il metodo generate_code_review incontra un errore specifico dell'applicazione
            (come un problema nell'interpretare il prompt o nel generare la risposta).

            Exception: Viene sollevata per qualsiasi altro errore imprevisto che si possa verificare durante l'inizializzazione del servizio LLM o 
            durante il processo di generazione della revisione del codice (ad esempio, problemi di rete o eccezioni non gestite dal servizio LLM).
    """
    python_code = request.form.get("input_code")
    review_type = request.form.get("review_type", "bug_detection")

    if not python_code:
        return render_template('index.html', error="Inserisci il codice da revisionare", original_code=python_code, selected_review_type=review_type)
    
    try:
        llm_service = LLMService() 
    except ValueError as e:
        return render_template('index.html', error=f"Errore di configurazione del servizio LLM: {e}", original_code=python_code, selected_review_type=review_type)
    except Exception as e:
        return render_template('index.html', error=f"Errore inaspettato durante l'inizializzazione del servizio: {e}", original_code=python_code, selected_review_type=review_type)

    try:
        reviewed_code = llm_service.generate_code_review(code_snippet=python_code, review_type=review_type)
        return render_template('index.html', reviewed_code=reviewed_code, original_code=python_code, selected_review_type=review_type)
    except ValueError as e:
        return render_template('index.html', original_code=python_code, error=str(e), selected_review_type=review_type)
    except Exception as e:
        return render_template('index.html', original_code=python_code, error=f"Si è verificato un errore durante la revisione: {e}", selected_review_type=review_type)
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
