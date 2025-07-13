import os
import requests
import ollama


from typing import Optional
from config import Config

class LLMService:

    api_key: Optional[str]
    api_base_url: Optional[str]
    model_name: Optional[str]
    local_base_url: Optional[str]
    llm_choice: str


    def __init__(self) -> None: 
        
        
        self.api_key = Config.API_KEY
        self.api_base_url = Config.API_BASE_URL

        
        self.model_name = Config.MODEL_NAME
        self.local_base_url = Config.LOCAL_BASE_URL

        # Logica per determinare automaticamente quale LLM usare
        not_local_configured = self.api_key and self.api_base_url
        ollama_configured = self.model_name and self.local_base_url

        if not_local_configured  and ollama_configured:
            # Se entrambi sono configurati, solleva un errore o scegli una priorità
            raise ValueError("Sono configurati sia Gemini che Ollama. Si prega di configurarne solo uno nel file .env.")
        elif not_local_configured:
            self.llm_choice = "not local API"
        elif ollama_configured:
            self.llm_choice = "ollama"
            # Imposta OLLAMA_HOST solo se local_base_url è definito e Ollama è l'LLM scelto
            os.environ["OLLAMA_HOST"] = str(self.local_base_url)
        else:
            raise ValueError("Nessun LLM è stato configurato nel file .env. Si prega di configurarne almeno uno.")

    def call_llm_api(self, prompt: str) -> str:
        '''
            Funzione privata per interagire con le API di Gemini.
        '''

        if not self.api_key or not self.api_base_url:
            return "Errore: API Key o Base URL per il modello selezionati non configurati."

        headers = {
            "Content-Type": "application/json"
        }
        
        params = { # type: ignore
            "key": self.api_key 
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
        }

        try:
            response = requests.post(self.api_base_url, headers=headers, params=params, json=payload, timeout=60)
            response.raise_for_status()
            
            response_json = response.json()

            if 'candidates' in response_json and response_json['candidates']:
                generated_text = response_json['candidates'][0]['content']['parts'][0]['text']
                return generated_text
            else:
                return "Nessuna revisione generata da Gemini."

        except requests.exceptions.HTTPError as e:
            print(f"Errore HTTP durante la chiamata a Gemini: {e}")
            return f"Errore HTTP dall'API di Gemini: {e}"
        except requests.exceptions.ConnectionError as e:
            print(f"Errore di connessione durante la chiamata a Gemini: {e}")
            return f"Errore di connessione a Gemini: {e}"
        except requests.exceptions.Timeout as e:
            print(f"Timeout durante la chiamata a Gemini: {e}")
            return "Timeout della chiamata a Gemini."
        except requests.exceptions.RequestException as e:
            print(f"Errore generico durante la chiamata a Gemini: {e}")
            return f"Si è verificato un errore durante la chiamata a Gemini: {e}"
        except ValueError as e: # Per errori di parsing JSON
            print(f"Errore di parsing JSON dalla risposta di Gemini: {e}")
            return f"Errore di parsing dalla risposta di Gemini: {e}"
        except Exception as e:
            print(f"Errore inaspettato durante la chiamata a Gemini: {e}")
            return f"Si è verificato un errore inaspettato: {e}"

    def call_local_llm(self, prompt: str) -> str:
        '''
            Funzione privata per interagire con i modelli Ollama locali.
        '''
        if not self.model_name:
            return "Errore: Nome del modello Ollama non configurato."

        try:
            response = ollama.chat(model=self.model_name, messages=[{'role': 'user', 'content': prompt}]) # type: ignore
    

            if 'message' in response and 'content' in response['message']:
                generated_text = response['message']['content']
                return generated_text
            else:
                return "Nessuna risposta valida da Ollama."

        except ollama.ResponseError as e:
            # Cattura errori specifici dalla libreria Ollama
            print(f"Errore dalla risposta di Ollama (ad es. modello non trovato): {e}")
            return f"Errore dall'API di Ollama: {e}"
        except Exception as e:
            # Cattura altri errori generici che potrebbero verificarsi durante la chiamata
            print(f"Errore inaspettato durante la chiamata a Ollama: {e}")
            return f"Si è verificato un errore inaspettato: {e}"
        
    def _generate_review_prompt(self, code_snippet: str = "", review_type: str = "bug_detection") -> str:
        prompt = ""
        if review_type == "bug_detection":
            prompt = ( '''
                Sei un esperto analista di codice Python specializzato nella rilevazione di bug e problemi logici.

                ISTRUZIONI:
                - Analizza il codice fornito per identificare potenziali bug, errori logici e problemi di runtime
                - Restituisci il codice originale IDENTICO con commenti aggiunti per evidenziare i problemi
                - Concentrati su: errori di logica, gestione delle eccezioni, problemi di tipo, condizioni di race, memory leaks, accesso a indici fuori range, divisioni per zero, null pointer exceptions
                - Valuta la robustezza del codice e i casi edge non gestiti
                - Identifica pattern anti-pattern comuni

                FORMATO OUTPUT:
                Restituisci il codice originale esattamente com'è, aggiungendo commenti in linea nel formato:
                - `# BUG: [SEVERITÀ] - [descrizione problema]` per problemi sulla stessa linea
                - `# POTENTIAL_BUG: [SEVERITÀ] - [descrizione]` per problemi potenziali
                - `# MISSING_HANDLING: [caso non gestito]` per gestioni mancanti
                - Per CIASCUN BUG INSERISCI UN SOLO COMMENTO
                SEVERITÀ: CRITICA/ALTA/MEDIA/BASSA

                Se non rilevi problemi, restituisci il codice originale senza commenti aggiuntivi.
                Il codice originale è:\n
                '''
                f"{code_snippet}"
            )

        elif review_type == "syntax_revision":
            prompt = (
                '''
                    Sei un esperto di sintassi Python specializzato nell'identificazione di errori sintattici e violazioni delle regole del linguaggio.

                    ISTRUZIONI:
                    - Analizza il codice fornito per identificare errori di sintassi, problemi di parsing e violazioni delle regole Python
                    - Restituisci il coadice originale IDENTICO con commenti aggiunti per evidenziare gli errori sintattici
                    - Concentrati su: errori di indentazione, parentesi/bracket non bilanciate, keywords usate incorrettamente, nomi di variabili/funzioni non validi, import errati, strutture sintattiche malformate
                    - Verifica la compatibilità con le versioni Python standard
                    - Identifica utilizzi deprecati o sintassi obsoleta

                    FORMATO OUTPUT:
                    Restituisci il codice originale esattamente com'è, aggiungendo commenti in linea nel formato:
                    - `# SYNTAX_ERROR: [descrizione errore]` per errori di sintassi
                    - `# DEPRECATED: [elemento deprecato] - usa [alternativa]` per sintassi obsoleta
                    - `# INVALID: [spiegazione]` per costrutti non validi
                    - PER CIASCUN ERRORE DI SINTASSI INSERISCI UN SOLO COMMENTO

                    Se la sintassi è corretta, restituisci il codice originale senza commenti aggiuntivi.\n
                    Il codice da revisionare è:
                '''
                f"{code_snippet}"
            )
        
        elif review_type == "style_suggestions":
            prompt = (
                '''
                    Sei un esperto di stile Python specializzato nell'applicazione delle linee guida PEP8 e best practices.

                    ISTRUZIONI:
                    - Analizza il codice fornito per identificare violazioni del PEP8 e problemi di stile
                    - Restituisci il codice originale IDENTICO con commenti aggiunti per evidenziare le violazioni di stile
                    - Concentrati su: naming conventions, lunghezza delle linee, spaziatura, indentazione, organizzazione degli import, struttura del codice, commenti inline
                    - Valuta la leggibilità e la manutenibilità del codice
                    - Identifica pattern che possono essere migliorati stilisticamente

                    FORMATO OUTPUT:
                    Restituisci il codice originale esattamente com'è, aggiungendo commenti in linea nel formato:
                    - `# PEP8: [codice regola] - [suggerimento]` per violazioni PEP8
                    - `# STYLE: [suggerimento di miglioramento]` per problemi di stile generali
                    - `# NAMING: [suggerimento]` per problemi di naming convention

                    Se lo stile è conforme, restituisci il codice originale senza commenti aggiuntivi.
                    Il codice da revisionare è:\n
                '''
                f"{code_snippet}"
            )

        elif review_type == "doc_strings_add":
            prompt = (
                '''
                    Sei un esperto di documentazione Python specializzato nella generazione di docstring e commenti di documentazione.

                    ISTRUZIONI:
                    - Analizza il codice fornito per identificare funzioni, classi e metodi che necessitano di documentazione
                    - Restituisci il codice originale IDENTICO con docstring e commenti aggiunti dove necessario
                    - Concentrati su: docstring mancanti, docstring incomplete, documentazione dei parametri, valori di ritorno, eccezioni, esempi d'uso
                    - Segui gli standard Google/NumPy/Sphinx per le docstring
                    - Identifica codice complesso che necessita di commenti esplicativi

                    FORMATO OUTPUT:
                    Restituisci il codice originale esattamente com'è, aggiungendo:
                    - Docstring complete per funzioni/classi/metodi che ne sono privi
                    - Commenti esplicativi per logica complessa nel formato `# EXPLAIN: [spiegazione]`
                    - Usa lo stile Google per le docstring:
                    """Breve descrizione.
                        Descrizione più dettagliata se necessaria.
                        Args:
                        param1 (type): Descrizione parametro.
                        param2 (type): Descrizione parametro.
                        Returns:
                        type: Descrizione del valore restituito.
                        Raises:
                        ExceptionType: Descrizione dell'eccezione.
                    """
                    
                    Il codice da revisionare è: \n
                '''
                f"{code_snippet}"
            )

        return prompt
    
    def generate_code_review(self, code_snippet: str, review_type: str = "bug_detection") -> str:
        if self.llm_choice == "not local API":
            return self.call_llm_api(self._generate_review_prompt(code_snippet=code_snippet, review_type=review_type))
        elif self.llm_choice == "ollama":
            return self.call_local_llm(self._generate_review_prompt(code_snippet=code_snippet, review_type=review_type))
        else:
            raise ValueError(f"Scelta LLM '{self.llm_choice}' non supportata per la generazione della revisione.")
