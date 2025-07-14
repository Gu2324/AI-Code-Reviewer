import os
import time

from llm_service import LLMService


def run_code_review_batch():
    """Elabora in batch snippet di codice per la revisione basata su LLM e salva i risultati.

Questa funzione automatizza il processo di revisione del codice iterando attraverso
specifici file `InputX.py` all'interno della directory 'tests/'. Legge il contenuto
di ogni file, lo invia a un `LLMService` per vari tipi di analisi del codice
(ad esempio, rilevamento di bug, revisione sintattica, aggiunta di docstring,
suggerimenti di stile) e compila i risultati. Lo snippet originale e la revisione
generata dall'LLM vengono quindi salvati in un unico file di output.

La funzione categorizza ciascuna revisione in base al numero del file di input
(ad esempio, i file 1-25 per il rilevamento dei bug).

Args:
    None: Questa funzione utilizza percorsi di directory e intervalli di file hardcoded.

Returns:
    None: La funzione scrive i suoi risultati direttamente in un file chiamato
    "llm_code_review_results.txt" e stampa messaggi di stato sulla console.

Raises:
    FileNotFoundError: Se la directory 'tests/' non esiste o se un file
        `InputX.py` specifico, previsto dal ciclo di elaborazione, non viene trovato.
    Exception: Cattura eccezioni generiche che possono verificarsi durante le
        operazioni di lettura dei file, stampando un avviso e saltando il file problematico.

Examples:
    Per eseguire la revisione in batch:
    # Assicurati che la directory 'tests/' esista e contenga i file InputX.py
    # in base all'intervallo configurato nella funzione.
    run_code_review_batch()
    # Questo creerà 'llm_code_review_results.txt' con gli output della revisione.
"""

    output_filename = "llm_code_review_results.txt"
    tests_dir = "tests/"
    
    if not os.path.exists(tests_dir):
        print(f"Errore: La cartella '{tests_dir}' non esiste. Creala e aggiungi i file di test.")
        return

    llm_service = LLMService() 

    results = {
        "bug_detection": [],
        "syntax_revision": [],
        "doc_strings_add": [],
        "style_suggestions": []
        
    }

    start_time = time.time()

    for i in range(45, 48):
        file_path = os.path.join(tests_dir, f"Input{i}.py")
        code_snippet = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_snippet = f.read()
        except FileNotFoundError:
            print(f"Avviso: File {file_path} non trovato. Saltando.")
            continue
        except Exception as e:
            print(f"Errore nella lettura del file {file_path}: {e}")
            continue

        review_type = ""
        if 1 <= i <= 25:
            review_type = "bug_detection"
        elif 26 <= i <= 50:
            review_type = "syntax_revision"
        elif 51 <= i <= 75:
            review_type = "doc_strings_add"
        elif 76 <= i <= 100:
            review_type = "style_suggestions"
        
        print(f"Elaborando Input{i}.py per la categoria: {review_type}")

        prompt_used = ""
        
        generated_review = llm_service.generate_code_review(code_snippet=code_snippet, review_type=review_type)
        
        results[review_type].append({
            "test_number": i,
            "code_snippet": code_snippet,
            "prompt_used": prompt_used,
            "generated_review": generated_review
        })
        
    end_time = time.time()
    total_time = end_time - start_time

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(f"--- Risultati della Code Review LLM ---\n")
        outfile.write(f"Tempo totale impiegato: {total_time:.2f} secondi\n\n")

        for category, items in results.items():
            if items:
                outfile.write(f"=== Categoria: {category.replace('_', ' ').title()} ===\n\n")
                
                if items[0]["prompt_used"]:
                    outfile.write(f"--- Prompt utilizzato per '{category.replace('_', ' ').title()}' ---\n")
                    outfile.write(items[0]["prompt_used"].splitlines()[1].strip() + '\n')
                    outfile.write("...\n")
                    outfile.write("---\n\n")

                for item in items:
                    outfile.write(f"--- Input {item['test_number']} ---\n")
                    outfile.write(item['code_snippet'].strip() + "\n\n")
                    outfile.write(f"--- Output {item['test_number']} (Revisione) ---\n")
                    outfile.write(item['generated_review'].strip() + "\n\n")
                outfile.write("\n")

    print(f"\nRevisione completata. I risultati sono stati salvati in '{output_filename}'.")
    print(f"Tempo totale impiegato: {total_time:.2f} secondi.")

if __name__ == "__main__":

    if not os.path.exists("tests"):
        os.makedirs("tests")
    for i in range(1, 2):
        with open(f"tests/Input{i}.py", "w") as f:
            f.write(f"# Contenuto di Input{i}.py per {i}\n")
            f.write("def example_function():\n")
            f.write("    pass\n")

    run_code_review_batch()