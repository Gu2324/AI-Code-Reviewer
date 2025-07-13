import os
import time
from llm_service import LLMService

def run_code_review_batch():
    """
    Recupera i code snippet dalla cartella 'tests/',
    li invia all'LLMService per la revisione e genera un file di output.
    """
    output_filename = "llm_code_review_results.txt"
    tests_dir = "tests/"
    
    # Assicurati che la cartella tests/ esista
    if not os.path.exists(tests_dir):
        print(f"Errore: La cartella '{tests_dir}' non esiste. Creala e aggiungi i file di test.")
        return

    llm_service = LLMService() # Inizializza il servizio LLM

    results = {
        "bug_detection": [],
        "syntax_revision": [],
        "doc_strings_add": [],
        "style_suggestions": []
        
    }

    start_time = time.time()

    for i in range(34, 49): # Per i 100 test da 1 a 100
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

        # Genera il prompt specifico per la categoria
        prompt_used = ""
        
        # Chiama l'LLM e ottieni la revisione
        generated_review = llm_service.generate_code_review(code_snippet=code_snippet, review_type=review_type)
        
        results[review_type].append({
            "test_number": i,
            "code_snippet": code_snippet,
            "prompt_used": prompt_used,
            "generated_review": generated_review
        })
        
    end_time = time.time()
    total_time = end_time - start_time

    # Scrivi i risultati nel file di output
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(f"--- Risultati della Code Review LLM ---\n")
        outfile.write(f"Tempo totale impiegato: {total_time:.2f} secondi\n\n")

        for category, items in results.items():
            if items: # Scrivi solo se ci sono elementi per la categoria
                outfile.write(f"=== Categoria: {category.replace('_', ' ').title()} ===\n\n")
                
                # Riporta il prompt usato per questa categoria (è lo stesso per tutti gli item di una categoria)
                # Prendiamo il prompt dal primo elemento se esiste
                if items[0]["prompt_used"]:
                    outfile.write(f"--- Prompt utilizzato per '{category.replace('_', ' ').title()}' ---\n")
                    outfile.write(items[0]["prompt_used"].splitlines()[1].strip() + '\n') # Solo la prima riga del prompt
                    outfile.write("...\n") # Per indicare che il prompt è più lungo
                    outfile.write("---\n\n")

                for item in items:
                    outfile.write(f"--- Input {item['test_number']} ---\n")
                    outfile.write(item['code_snippet'].strip() + "\n\n")
                    outfile.write(f"--- Output {item['test_number']} (Revisione) ---\n")
                    outfile.write(item['generated_review'].strip() + "\n\n")
                outfile.write("\n") # Linea vuota tra le categorie

    print(f"\nRevisione completata. I risultati sono stati salvati in '{output_filename}'.")
    print(f"Tempo totale impiegato: {total_time:.2f} secondi.")

if __name__ == "__main__":
    # Esempio di creazione di file di test (solo per dimostrazione)
    # Rimuovi/commenta questo blocco se hai già i tuoi 100 test
    if not os.path.exists("tests"):
        os.makedirs("tests")
    for i in range(1, 2):
        with open(f"tests/Input{i}.py", "w") as f:
            f.write(f"# Contenuto di Input{i}.py per {i}\n")
            f.write("def example_function():\n")
            f.write("    pass\n")

    # Esegui la batch di revisione
    run_code_review_batch()