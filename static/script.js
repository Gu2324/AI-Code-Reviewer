document.addEventListener('DOMContentLoaded', function() {
    const reviewedCodeOutput = document.querySelector('.reviewed_code_output');
    const copyButton = document.querySelector('.copy_button');
    const originalText = reviewedCodeOutput.textContent.trim(); 

    // Elimino il testo iniziale, così da poter iniziare la scrittura da zero
    reviewedCodeOutput.textContent = '';

    /**
     * Implementa un effetto di scrittura simile ad una macchina da scrivere
     * @param {HTMLTextAreaElement} element L'elemento textarea su cui applicare l'effetto.
     * @param {string} text Il testo da "scrivere" nella textarea.
     * @param {number} delay Il ritardo in millisecondi tra ogni carattere.
     */
    function typewriterEffect(element, text, delay = 25) {
        let i = 0;
        function typeChar() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeChar, delay);
            }
        }
        typeChar();
    }

    //Inizia l'effetto solo se c'è testo 
    if (originalText.length > 0) {
        typewriterEffect(reviewedCodeOutput, originalText);
    }

    // Copia il contenuto della textarea del codice revisionato negli appunti.
    function copyFunction() {
        // Seleziona il testo all'interno della textarea
        reviewedCodeOutput.select();
        reviewedCodeOutput.setSelectionRange(0, 99999); // For mobile devices

        try {
            // Copia il testo all'interno della textarea
            navigator.clipboard.writeText(reviewedCodeOutput.value);
            alert('Codice copiato negli appunti!'); //Fornisce un feedback all'utente
        } catch (err) {
            console.error('Errore durante la copia del testo: ', err);
            alert('Impossibile copiare il codice. Si prega di copiare manualmente.'); // Fallimento della copia 
        }
    }

    // Abbina la funzione di copia al click del pulsante
    if (copyButton) {
        copyButton.addEventListener('click', copyFunction);
    }
});