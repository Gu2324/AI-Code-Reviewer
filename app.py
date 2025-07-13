# app.py
from flask import Flask, request, render_template # Rimosso jsonify
from llm_service import LLMService

app = Flask(__name__)

@app.route('/', methods=["GET"])
def show_form():
    '''
        mostra la pagina principale dell'applicazione
    '''
    return render_template('index.html', input_code="", selected_review_type="bug_detection")

@app.route('/code_reviewer', methods=["POST"])
def review_code():
    '''
        recupera il codice python che viene fornito dall'utente e lo invia ad un llm per la revisione,
        in base alla modalità selezionata nell'interfaccia.
    '''

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
