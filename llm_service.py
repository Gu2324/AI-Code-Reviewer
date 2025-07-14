import os
from typing import Optional
import ollama
import requests

from config import Config

class LLMService:
    """Classe di servizio per interagire con vari Large Language Model (LLM).

        Questa classe fornisce un'interfaccia unificata per interagire sia con un
        LLM basato su cloud (come Gemini di Google tramite API) sia con un LLM locale
        (come Ollama). Gestisce la configurazione, la selezione e l'invocazione
        dell'LLM appropriato in base alle impostazioni dell'ambiente.

        Attributes:
            api_key (Optional[str]): Chiave API per l'LLM basato su cloud (es. Gemini).
            api_base_url (Optional[str]): URL di base per l'API dell'LLM basato su cloud.
            model_name (Optional[str]): Nome del modello LLM locale (es. 'llama2').
            local_base_url (Optional[str]): URL di base per l'istanza locale di Ollama.
            llm_choice (str): Memorizza l'LLM scelto ("not local API" o "ollama")
                            dopo l'inizializzazione.
    """
    gemini_api_key: Optional[str]
    gemini_api_base_url: Optional[str]
    model_name: Optional[str]
    local_base_url: Optional[str]
    llm_choice: str


    def __init__(self) -> None:
        """Inizializza il servizio LLMService e determina quale LLM utilizzare.

            Legge la configurazione dall'oggetto `Config` e verifica che
            sia configurato esattamente un solo LLM (o l'API cloud/Gemini o Ollama/locale).
            Configura l'LLM scelto per le chiamate successive.

            Raises:
                ValueError: Se sono configurati sia Gemini/API cloud che Ollama,
                            o se nessun LLM è configurato nel file .env.

            Examples:
                # Supponendo che Config.API_KEY e Config.API_BASE_URL siano impostati
                # e che Config.MODEL_NAME e Config.LOCAL_BASE_URL NON siano impostati.
                service = LLMService()
                print(service.llm_choice)
                not local API

                # Supponendo che Config.MODEL_NAME e Config.LOCAL_BASE_URL siano impostati
                # e che Config.API_KEY e Config.API_BASE_URL NON siano impostati.
                service = LLMService()
                print(service.llm_choice)
                ollama

                # Esempio di sollevamento di ValueError se entrambi sono configurati:
                # class Config: API_KEY='abc'; API_BASE_URL='http://api'; MODEL_NAME='llama2'; LOCAL_BASE_URL='http://ollama'
                # try: service = LLMService()
                # except ValueError as e: print(e)
                # Sono configurati sia Gemini che Ollama. Si prega di configurarne solo uno nel file .env.
        """

        self.gemini_api_key = Config.GEMINI_API_KEY
        self.gemini_api_base_url = Config.GEMINI_API_BASE_URL
        self.model_name = Config.MODEL_NAME
        self.local_base_url = Config.LOCAL_BASE_URL
        # 2 modelli usati contemporaneamente non fanno distinguere quale chiamare
        gemini_configured = self.gemini_api_key and self.gemini_api_base_url
        ollama_configured = self.model_name and self.local_base_url

        if gemini_configured and ollama_configured:
            # Se entrambi sono configurati, solleva un errore o scegli una priorità
            raise ValueError("Sono configurati sia Gemini che Ollama. "
            "Si prega di configurarne solo uno nel file .env.")
        elif gemini_configured:
            self.llm_choice = "gemini"
        elif ollama_configured:
            self.llm_choice = "ollama"
            # OLLAMA richiede che nelle variabili di ambiente sia configurato HOLLAMA_HOST
            os.environ["OLLAMA_HOST"] = str(self.local_base_url)
        else:
            raise ValueError("Nessun LLM è stato configurato nel file .env. "
            "Si prega di configurarne almeno uno.")


    def __call_gemini(self, prompt: str) -> str:
        """Interagisce con un'API GEMINI.

            Questo metodo privato costruisce un payload di richiesta e lo invia all'endpoint
            API configurato. Gestisce vari errori HTTP e di connessione che potrebbero
            verificarsi durante la chiamata API.

            Args:
                prompt (str): Il prompt testuale da inviare all'LLM.

            Returns:
                str: La risposta testuale generata dall'LLM, o un messaggio di errore
                    se la chiamata API fallisce o non viene ricevuta una risposta valida.

            Raises:
                requests.exceptions.HTTPError: Per errori HTTP (ad esempio, risposte 4xx, 5xx).
                requests.exceptions.ConnectionError: Per errori relativi alla rete.
                requests.exceptions.Timeout: Se la richiesta scade dopo 300 secondi.
                requests.exceptions.RequestException: Per qualsiasi altro errore generale relativo a `requests`.
                ValueError: Se il parsing JSON fallisce a causa di un formato di risposta non valido dall'API.
                Exception: Per qualsiasi altro errore imprevisto durante il processo.

            Examples:
                # Questo è un metodo privato e non dovrebbe essere chiamato direttamente.
                # Esempio di utilizzo interno (supponendo che self.llm_choice sia "not local API" e la configurazione sia valida):
                # service = LLMService()
                # response = service._LLMService__call_llm_api("Raccontami una breve storia su un prode cavaliere.")
                # print(response)
        """
        if not self.gemini_api_key or not self.gemini_api_base_url:
            return "Errore: API Key o Base URL per il modello selezionati non configurati."

        headers = {
            "Content-Type": "application/json"
        }
        
        params = { # type: ignore
            "key": self.gemini_api_key
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
            response = requests.post(self.gemini_api_base_url, headers=headers, 
                                     params=params, json=payload, timeout=300)
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
        """Interagisce con un LLM locale tramite Ollama.

            Questo metodo invia un prompt di chat all'istanza locale di Ollama configurata
            e recupera la risposta generata.

            Args:
                prompt (str): Il prompt testuale da inviare all'LLM locale.

            Returns:
                str: La risposta testuale generata da Ollama, o un messaggio di errore
                    se la chiamata fallisce o non viene ricevuta una risposta valida.

            Raises:
                ollama.ResponseError: Per errori specifici dell'API di Ollama,
                        ad esempio, modello non trovato o problemi del server.
            Exception: Per qualsiasi altro errore imprevisto durante il processo.

            Examples:
                # Questo è un metodo interno, tipicamente chiamato da `generate_code_review`.
                # Esempio di utilizzo interno (supponendo che self.llm_choice sia "ollama" e la configurazione sia valida):
                # service = LLMService()
                # response = service.call_local_llm("Riassumi il GIL di Python.")
                # print(response)
        """
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
        """Genera un prompt specifico per l'LLM basato sul tipo di revisione desiderato.

            Questo metodo privato costruisce un set dettagliato di istruzioni per l'LLM,
            guidandolo a eseguire un particolare tipo di revisione del codice (ad esempio,
            rilevamento di bug, revisione sintattica, suggerimenti di stile o aggiunta di docstring).

            Args:
                code_snippet (str, optional): Lo snippet di codice da revisionare.
                                  Il valore predefinito è una stringa vuota.
                review_type (str, optional): Il tipo di revisione del codice da eseguire.
                                 I tipi supportati sono: "bug_detection",
                                 "syntax_revision", "style_suggestions",
                                 "doc_strings_add". Il valore predefinito è "bug_detection".

            Returns:
                str: La stringa del prompt formattato, pronta per essere inviata all'LLM.

            Examples:
                # Questo è un metodo privato e non dovrebbe essere chiamato direttamente.
                # Esempio di utilizzo interno:
                # service = LLMService()
                # bug_prompt = service._generate_review_prompt("def f(): pass", "bug_detection")
                # print(bug_prompt.startswith("Sei un esperto analista di codice Python"))
                # True
                # style_prompt = service._generate_review_prompt("x=1", "style_suggestions")
                # print(style_prompt.startswith("Sei un esperto di stile Python"))
                # True
        """
        prompt = ""
        if review_type == "bug_detection":
            prompt = ( '''
               Sei un esperto analista di codice Python specializzato nella rilevazione di bug e problemi logici.

                ISTRUZIONI:
                - Analizza il codice Python fornito per identificare potenziali bug, errori logici e problemi di runtime.
                - Restituisci il codice originale IDENTICO con commenti aggiunti per evidenziare i problemi.
                - Concentrati su: errori di logica, gestione delle eccezioni, problemi di tipo, condizioni di race, memory leaks, accesso a indici fuori range, divisioni per zero, null pointer exceptions, e gestione impropria delle risorse.
                - Valuta la robustezza del codice e i casi edge non gestiti.
                - Identifica anti-pattern comuni e suggerisci miglioramenti impliciti attraverso i commenti.

                FORMATO OUTPUT:
                Restituisci il codice originale esattamente com'è, aggiungendo commenti in linea nel formato:
                - `# BUG: [SEVERITÀ] - [descrizione problema]` per problemi sulla stessa linea.
                - `# POTENTIAL_BUG: [SEVERITÀ] - [descrizione]` per problemi potenziali o difficili da riprodurre.
                - `# MISSING_HANDLING: [caso non gestito]` per gestioni mancanti di casi o eccezioni.
                - **Per OGNI problema o caso non gestito, inserisci ESATTAMENTE UN SOLO COMMENTO, specifico e conciso.**
                SEVERITÀ: CRITICA/ALTA/MEDIA/BASSA (scala fissa e sempre da usare).

                Se non rilevi problemi, restituisci il codice originale senza commenti aggiuntivi.
                Il codice originale è:
                '''
                f"{code_snippet}" )


        elif review_type == "syntax_revision":
            prompt = ( '''
                    Sei un esperto di sintassi Python specializzato nell'identificazione di errori sintattici e violazioni delle regole del linguaggio.

                    ISTRUZIONI:
                    - Analizza il codice Python fornito per identificare errori di sintassi, problemi di parsing e violazioni delle regole intrinseche di Python.
                    - Restituisci il codice originale IDENTICO con commenti aggiunti per evidenziare gli errori sintattici.
                    - Concentrati su: errori di indentazione, parentesi/graffe/quadre non bilanciate, keyword usate incorrettamente, nomi di variabili/funzioni non validi, import errati o incompleti, e strutture sintattiche malformate.
                    - Verifica la compatibilità della sintassi con le versioni Python standard (es. Python 3.x).
                    - Identifica utilizzi deprecati o sintassi obsoleta, indicando la versione da cui sono deprecati se possibile.

                    FORMATO OUTPUT:
                    Restituisci il codice originale esattamente com'è, aggiungendo commenti in linea nel formato:
                    - `# SYNTAX_ERROR: [descrizione errore]` per errori di sintassi evidenti.
                    - `# DEPRECATED: [elemento deprecato] - usa [alternativa suggerita]` per sintassi obsoleta.
                    - `# INVALID: [spiegazione del costrutto non valido]` per costrutti Python non validi.
                    - **Per OGNI errore o violazione di sintassi, inserisci ESATTAMENTE UN SOLO COMMENTO, specifico e pertinente.**

                    Se la sintassi è corretta, restituisci il codice originale senza commenti aggiuntivi.
                    Il codice da revisionare è:\n
                    '''
            f"{code_snippet}" )
                
        
        elif review_type == "style_suggestions":
            prompt = ( '''
                    Sei un esperto di stile Python specializzato nell'applicazione delle linee guida PEP8 e delle best practice di programmazione.

                    ISTRUZIONI:
                    - Analizza il codice Python fornito per identificare violazioni dello standard PEP8 e problemi generali di stile.
                    - Restituisci il codice originale IDENTICO con commenti aggiunti per evidenziare le violazioni di stile.
                    - Concentrati su: naming conventions (Nomenclatura), lunghezza delle linee (max 79 caratteri), spaziatura (attorno operatori, dopo le virgole), indentazione (4 spazi), organizzazione degli import, struttura del codice (es. funzioni troppo lunghe), e chiarezza dei commenti inline.
                    - Valuta la leggibilità, la manutenibilità e la coerenza del codice.
                    - Identifica pattern che possono essere migliorati stilisticamente per aderire agli standard.

                    FORMATO OUTPUT:
                    Restituisci il codice originale esattamente com'è, aggiungendo commenti in linea nel formato:
                    - `# PEP8: [codice regola E.g. E501] - [suggerimento specifico]` per violazioni PEP8 dirette.
                    - `# STYLE: [suggerimento di miglioramento generale]` per problemi di stile non coperti direttamente da PEP8 ma che ne migliorano la leggibilità.
                    - `# NAMING: [suggerimento per la convenzione di denominazione]` per problemi relativi alle convenzioni di denominazione.
                    - **Per OGNI violazione di stile o suggerimento, inserisci ESATTAMENTE UN SOLO COMMENTO, conciso e puntuale.**

                    Se lo stile è completamente conforme, restituisci il codice originale senza commenti aggiuntivi.
                    Il codice da revisionare è:\n
                    '''
            f"{code_snippet}" )
                

        elif review_type == "doc_strings_add":
            prompt = ( '''
                    ISTRUZIONI:
                    - Analizza il codice Python fornito per identificare funzioni, classi e metodi che necessitano di documentazione adeguata.
                    - Restituisci il codice originale IDENTICO con docstring e commenti aggiunti dove necessario.
                    - Concentrati su: docstring mancanti, docstring incomplete (es. senza descrizione di parametri, ritorno, o eccezioni), necessità di documentazione dei parametri, valori di ritorno, eccezioni sollevate ed esempi d'uso.
                    - **Applica rigorosamente lo stile Google per le docstring, includendo sezioni per Args, Returns, Raises, ed Examples quando applicabile.**
                    - Identifica blocchi di codice complesso che necessitano di commenti esplicativi per chiarire la logica non ovvia.

                    FORMATO OUTPUT:
                    Restituisci il codice originale esattamente com'è, aggiungendo:
                    - Docstring complete e formattate in stile Google per funzioni, classi e metodi che ne sono privi o che li hanno incompleti.
                    - Commenti esplicativi per logica complessa nel formato `# EXPLAIN: [spiegazione concisa della logica]`.
                    - Le docstring devono seguire lo standard Google Style come nell'esempio:
                        ```python
                        """Breve riassunto della funzione/metodo/classe.

                        Descrizione più dettagliata se necessaria, spiegando il suo scopo e comportamento.

                        Args:
                            param1 (type): Descrizione del primo parametro.
                            param2 (type, optional): Descrizione del secondo parametro, con indicazione se opzionale e valore di default.

                        Returns:
                            type: Descrizione del valore restituito dalla funzione/metodo.

                        Raises:
                            ExceptionType: Descrizione quando e perché viene sollevata questa eccezione.
                            AnotherException: Descrizione di un'altra possibile eccezione.
                        """
                        ```

                    Il codice da revisionare è:\n
                    '''
                f"{code_snippet}" )
                

        return prompt
    

    def generate_code_review(self, code_snippet: str, review_type: str = "bug_detection") -> str:
        """Genera una revisione del codice per un dato snippet utilizzando l'LLM selezionato.

            Questo è il metodo pubblico principale per avviare una revisione del codice. Per prima cosa
            genera un prompt specifico basato sul `review_type` e poi invia
            questo prompt all'LLM configurato (basato su cloud o locale).

            Args:   
            code_snippet (str): Lo snippet di codice Python da revisionare.
            review_type (str, optional): Il tipo di revisione da eseguire.
                                 Deve essere uno dei tipi supportati da
                                 `_generate_review_prompt` ("bug_detection",
                                 "syntax_revision", "style_suggestions",
                                 "doc_strings_add").
                                 Il valore predefinito è "bug_detection".

            Returns:
            str: Il codice revisionato con commenti/suggerimenti generati dall'LLM,
            o un messaggio di errore se la chiamata all'LLM fallisce.

            Raises:
                ValueError: Se la `llm_choice` determinata durante l'inizializzazione
                    non è un'opzione supportata ("not local API" o "ollama").

            Examples:
            # Supponendo che sia configurata l'opzione 'not local API'
            # service = LLMService()
            # reviewed_code = service.generate_code_review("def add(a,b): return a + b", "bug_detection")
            # print(reviewed_code)
            # def add(a,b): return a + b

            # Supponendo che sia configurato 'ollama'
            # service = LLMService()
            # reviewed_code = service.generate_code_review("x=1", "style_suggestions")
            # print(reviewed_code)
            # x = 1 # PEP8: E225 - missing whitespace around operator
        """
        if self.llm_choice == "gemini":
            return self.__call_gemini(self._generate_review_prompt(code_snippet=code_snippet, review_type=review_type))
        elif self.llm_choice == "ollama":
            return self.call_local_llm(self._generate_review_prompt(code_snippet=code_snippet, review_type=review_type))
        else:
            raise ValueError(f"Scelta LLM '{self.llm_choice}' non supportata per la generazione della revisione.")
