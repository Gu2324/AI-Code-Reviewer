import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Gestione delle Impostazioni di Configurazione dell'Applicazione

        Questa classe si occupa di gestire le impostazioni di configurazione dell'applicazione, 
        che vengono caricate dalle variabili d'ambiente.

        Questa classe offre un punto di accesso centralizzato per le diverse chiavi API, 
        URL di base e nomi di modelli richiesti dall'applicazione. 
        Recupera queste impostazioni dall'ambiente, che di solito include le variabili 
        caricate da un file .env tramite load_dotenv().

        Attributi (Attributes)

            API_KEY (str o None): La chiave API usata per l'autenticazione con i servizi esterni. 
            Viene recuperata dalla variabile d'ambiente 'API_KEY'. Sarà None se la variabile non è impostata.

            API_BASE_URL (str o None): L'URL di base per gli endpoint API esterni. 
            Viene recuperato dalla variabile d'ambiente 'API_BASE_URL'. Sarà None se la variabile non è impostata.

            MODEL_NAME (str o None): Il nome specifico del modello AI che l'applicazione utilizzerà. 
            Viene recuperato dalla variabile d'ambiente 'MODEL_NAME'. Sarà None se la variabile non è impostata.

            LOCAL_BASE_URL (str o None): L'URL di base per un servizio locale o un endpoint di sviluppo. 
            Viene recuperato dalla variabile d'ambiente 'LOCAL_BASE_URL'. Sarà None se la variabile non è impostata.

        Esempi (Examples)

        Per accedere a un'impostazione di configurazione da qualsiasi punto dell'applicazione:

        api_key = Config.API_KEY
        if api_key:
            print(f"API Key caricata: {api_key[:4]}...")
        else:
            print("La variabile d'ambiente API_KEY non è impostata.")

        Assicurati che il tuo file .env (o l'ambiente) contenga voci come:

        API_KEY="la_tua_chiave_api_segreta_12345"
        API_BASE_URL="https://api.example.com/v1"
        MODEL_NAME="gpt-4"
        LOCAL_BASE_URL="http://localhost:8000"
    """
    GEMINI_API_KEY = os.getenv("API_KEY")
    GEMINI_API_BASE_URL = os.getenv("API_BASE_URL")

    MODEL_NAME = os.getenv("MODEL_NAME")
    LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL")



