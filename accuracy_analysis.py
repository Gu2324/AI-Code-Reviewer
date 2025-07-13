import matplotlib.pyplot as plt

class llm_model:
    
    def __init__(self, name: str = "", prompt : str = "", bug_accuracy: int = 0, syntax_accuracy: int = 0, style_accuracy: int = 0, docstrings_accuracy: int = 0, time : int = 0):
    
        self.time = time #Intero riportato in millisecondi
        self.name = name
        self.prompt = prompt
        self.bug_accuracy = bug_accuracy
        self.syntax_accuracy = syntax_accuracy
        self.style_accuracy = style_accuracy
        self.docstring_accuracy = docstrings_accuracy

    def generate_grphic(self):
        categories = ["bug_accuracy", "syntax_accuracy", "style_accuracy", "docstring_accuracy", "execution_time"]

        values = [self.bug_accuracy, self.syntax_accuracy, self.style_accuracy, self.docstring_accuracy, self.time]

        plt.bar(categories, values)

        plt.title(self.name)

        plt.xlabel("categories")

        plt.ylabel("score")

        plt.show()







    
if __name__ == "__main__":
    
    ollama = llm_model("codegemma", "prova di prompt", 60, 50, 35, 35, 70) #I voti verrano espressi in centesimi e il tempo in minuti
    ollama.generate_grphic()


