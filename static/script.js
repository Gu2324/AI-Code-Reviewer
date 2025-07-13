document.addEventListener('DOMContentLoaded', function() {
    const reviewTypeSelect = document.getElementById('review_type_main'); // ID del select visibile
    const hiddenReviewTypeInput = document.getElementById('hidden_review_type'); // ID dell'input hidden
    const reviewedCodeOutputElement = document.querySelector('.reviewed_code_output');
    const copyButton = document.querySelector('.copy_button');

    // Inizializza l'input hidden con il valore corrente del select visibile
    if (reviewTypeSelect && hiddenReviewTypeInput) {
        hiddenReviewTypeInput.value = reviewTypeSelect.value;
    }

    // Aggiungi un event listener al select per aggiornare l'input hidden
    if (reviewTypeSelect) {
        reviewTypeSelect.addEventListener('change', function() {
            if (hiddenReviewTypeInput) {
                hiddenReviewTypeInput.value = this.value;
            }
        });
    }

    // Applica Highlight.js all'elemento <code> al caricamento iniziale
    // Questo è importante ora che la pagina si ricarica e Flask popola il contenuto
    if (reviewedCodeOutputElement.textContent.trim().length > 0 && reviewedCodeOutputElement.textContent.trim() !== 'Il codice revisionato apparirà qui.') {
        hljs.highlightElement(reviewedCodeOutputElement);
    }
    
    // Funzione per copiare il contenuto del codice revisionato (rimane invariata)
    function copyFunction() {
        const textToCopy = reviewedCodeOutputElement.textContent;

        try {
            const textarea = document.createElement('textarea');
            textarea.value = textToCopy;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            showTemporaryMessage('Codice copiato negli appunti!', 'success');
        } catch (err) {
            console.error('Errore durante la copia del testo: ', err);
            showTemporaryMessage('Impossibile copiare il codice. Si prega di copiare manualmente.', 'error');
        }
    }

    if (copyButton) {
        copyButton.addEventListener('click', copyFunction);
    }

    // Funzione per mostrare messaggi temporanei all'utente (successo/errore) - rimane invariata
    function showTemporaryMessage(message, type) {
        let messageBox = document.getElementById('tempMessageBox');
        if (!messageBox) {
            messageBox = document.createElement('div');
            messageBox.id = 'tempMessageBox';
            messageBox.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 1em;
                color: white;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.5s ease-in-out;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(messageBox);
        }

        messageBox.textContent = message;
        if (type === 'success') {
            messageBox.style.backgroundColor = '#4CAF50';
        } else if (type === 'error') {
            messageBox.style.backgroundColor = '#f44336';
        } else {
            messageBox.style.backgroundColor = '#333';
        }
        
        messageBox.style.opacity = 1;

        setTimeout(() => {
            messageBox.style.opacity = 0;
        }, 3000);
    }

    // Rimossa completamente la gestione della sottomissione del form tramite AJAX.
    // La sottomissione avverrà in modo tradizionale, causando un ricaricamento della pagina.
});

// Funzione globale per il toggle del menu delle impostazioni (rimane invariata)
function toggleSettingsMenu() {
    const reviewMenu = document.getElementById('review_mode_menu');
    if (reviewMenu.style.display === 'flex') {
        reviewMenu.style.display = 'none';
    } else {
        reviewMenu.style.display = 'flex';
    }
}
