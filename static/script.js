document.addEventListener('DOMContentLoaded', function() {
    const reviewedCodeOutputElement = document.querySelector('.reviewed_code_output'); // Questo è il <code> element
    const copyButton = document.querySelector('.copy_button');
    
    // Non è più necessario 'originalText' se non usi il typewriter effect su reviewedCodeOutput
    // const originalText = reviewedCodeOutputElement.textContent.trim(); 

    // Rimuovi completamente la logica dell'effetto macchina da scrivere per reviewedCodeOutputElement
    // reviewedCodeOutputElement.textContent = ''; // Questa riga va rimossa o non avrà senso
    // function typewriterEffect(...) { ... }
    // if (originalText.length > 0) { typewriterEffect(...) }

    // Applica Highlight.js all'elemento <code>
    // Questo viene eseguito non appena il DOM è pronto e Jinja ha riempito l'elemento
    if (reviewedCodeOutputElement.textContent.trim().length > 0) {
        hljs.highlightElement(reviewedCodeOutputElement);
    }
    
    // Copia il contenuto dell'elemento <pre><code> negli appunti.
    function copyFunction() {
        const textToCopy = reviewedCodeOutputElement.textContent; // Ottieni il testo raw dall'elemento <code>

        try {
            navigator.clipboard.writeText(textToCopy);
            alert('Codice copiato negli appunti!');
        } catch (err) {
            console.error('Errore durante la copia del testo: ', err);
            alert('Impossibile copiare il codice. Si prega di copiare manualmente.');
        }
    }

    if (copyButton) {
        copyButton.addEventListener('click', copyFunction);
    }
});