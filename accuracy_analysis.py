import matplotlib.pyplot as plt


class LlmModel:
    """Rappresenta le Metriche di Performance di un Modello LLM

        Questa classe ha il compito di conservare le metriche di performance di un modello LLM.

        Questa classe memorizza vari punteggi di accuratezza (bug, sintassi, stile, docstring)
        e il tempo di esecuzione per uno specifico Large Language Model (LLM), insieme al suo nome e 
        al prompt utilizzato per la valutazione. 
        Offre inoltre la funzionalità per visualizzare queste metriche sotto forma di grafico a barre.

    """
    
    def __init__(self, name: str = "", prompt: str = "", bug_accuracy: int = 0, syntax_accuracy: int = 0, style_accuracy: int = 0, docstrings_accuracy: int = 0, time: int = 0):
            """Inizializza un'Istanza LlmModel con Metriche di Performance

                Questo costruttore inizializza un'istanza della classe LlmModel fornendo le metriche di performance di un modello LLM.

                Argomenti (Args)

                    name (str): Il nome del modello LLM (ad esempio, "codegemma", "gemini-2.5-flash"). Il valore predefinito è una stringa vuota.

                    prompt (str): Una descrizione del prompt utilizzato per valutare il modello 
                    (ad esempio, "prompt generico", "prompt migliorato"). Il valore predefinito è una stringa vuota.

                    bug_accuracy (int): Il punteggio di accuratezza relativo alla capacità del modello 
                    di correggere o identificare bug, tipicamente su una scala (ad esempio, 0-100). 
                    Il valore predefinito è 0.

                    syntax_accuracy (int): Il punteggio di accuratezza relativo alla capacità del modello 
                    di generare codice sintatticamente corretto, tipicamente su una scala (ad esempio, 0-100). 
                    Il valore predefinito è 0.

                    style_accuracy (int): Il punteggio di accuratezza relativo alla capacità del modello 
                    di aderire alle linee guida di stile del codice, tipicamente su una scala (ad esempio, 0-100). 
                    Il valore predefinito è 0.

                    docstrings_accuracy (int): Il punteggio di accuratezza relativo alla capacità del modello
                    di generare docstring complete e corrette, tipicamente su una scala (ad esempio, 0-100). 
                    
                    Il valore predefinito è 0.

                    time (int): Il tempo di esecuzione o una metrica di tempo delle performance per il modello, 
                    che rappresenta la velocità con cui esegue un'attività. Il valore predefinito è 0.
            """
            self.time = time 
            self.name = name
            self.prompt = prompt
            self.bug_accuracy = bug_accuracy
            self.syntax_accuracy = syntax_accuracy
            self.style_accuracy = style_accuracy
            self.docstrings_accuracy = docstrings_accuracy

    def generate_graphic(self):
        """Genera e Visualizza un Grafico a Barre delle Metriche di Performance dell'LLM

            Questo metodo serve a creare e mostrare un grafico a barre delle metriche di performance 
            di un modello LLM.

            Questo metodo utilizza la libreria matplotlib per creare un grafico a barre che visualizza 
            le metriche bug_accuracy, syntax_accuracy, style_accuracy, docstrings_accuracy e time del modello LLM. 
            Il titolo del grafico viene impostato usando il name del modello. 
            Il grafico viene poi mostrato tramite plt.show().

            Argomenti (Args)

                None: Questo metodo non accetta alcun argomento.

            Valori di Ritorno (Returns)

                None: Questo metodo visualizza direttamente un grafico e non restituisce alcun valore.

            Esempi (Examples)

            # EXPLAIN: Creazione di un'istanza LlmModel e generazione del grafico delle sue metriche.
            model = LlmModel(
                name="ExampleModel",
                prompt="sample prompt",
                bug_accuracy=80,
                syntax_accuracy=75,
                style_accuracy=70,
                docstrings_accuracy=85,
                time=10
            )
            model.generate_graphic() # Questo aprirà una finestra matplotlib con il grafico.

        """
         
        categories = ["bug_accuracy", "syntax_accuracy", "style_accuracy", "docstring_accuracy", "execution_time"]
        values = [self.bug_accuracy, self.syntax_accuracy, self.style_accuracy, self.docstrings_accuracy, self.time]

        plt.bar(categories, values)
        plt.title(self.name)
        plt.xlabel("categories")
        plt.ylabel("score")
        plt.show()

        
if __name__ == "__main__":
    ollama_gen = LlmModel("codegemma", "prompt generico", 60, 50, 35, 35, 70)
    ollama_emp = LlmModel("codegemma", "prompt migliorato", 70, 65, 45, 60, 70)
    gemini_gen = LlmModel("gemini-2.5-flash", "prompt generico", 85, 80, 75, 90, 7)
    gemini_emp = LlmModel("gemini-2.5-flash", "prompt migliorato", 95, 95, 90, 90, 7)
    ollama_gen.generate_graphic()
    ollama_emp.generate_graphic()
    gemini_gen.generate_graphic()
    gemini_emp.generate_graphic()


