import os

directory_destinazione = ""
prefisso_file = "Input"

numero_di_file = 100

for i in range(numero_di_file):
  
  nome_file = f"{prefisso_file}{i}.py"
  percorso_completo = os.path.join(directory_destinazione, nome_file)
print(f"Creati con successo {numero_di_file} file nella directory corrente.")