document.addEventListener("DOMContentLoaded", function () {
  // --- Funzione di Auto-ridimensionamento riutilizzabile per entrambe le textarea ---
  function autoResizeTextarea(textareaElement) {
    textareaElement.style.height = "auto"; // Resetta l'altezza per ricalcolare
    // Imposta l'altezza in base al contenuto, ma considera anche lo spazio del bottone se presente
    textareaElement.style.height = textareaElement.scrollHeight + "px";

    // Assicurati che anche il parent .textarea-container si adatti all'altezza del textarea + bottone
    const parentContainer = textareaElement.closest(".textarea-container");
    if (parentContainer) {
      const button = parentContainer.querySelector("button");
      if (button) {
        // Altezza minima del container = altezza textarea + altezza bottone + bottom padding del bottone
        const buttonHeight = button.offsetHeight;
        const buttonBottomPadding = parseFloat(
          window.getComputedStyle(button).bottom
        );
        const requiredHeight =
          textareaElement.scrollHeight +
          buttonHeight +
          buttonBottomPadding +
          10; // Aggiungi un po' di spazio
        parentContainer.style.minHeight = requiredHeight + "px";
      } else {
        parentContainer.style.minHeight = textareaElement.scrollHeight + "px";
      }
    }
  }

  // --- Gestione della Textarea di INPUT ---
  const inputCodeTextarea = document.querySelector(".input_code");
  if (inputCodeTextarea) {
    // Applica auto-ridimensionamento all'avvio e ad ogni input
    autoResizeTextarea(inputCodeTextarea);
    inputCodeTextarea.addEventListener("input", () =>
      autoResizeTextarea(inputCodeTextarea)
    );
  }

  // --- Gestione della Textarea di OUTPUT con Animazione di Digitazione ---
  const reviewedCodeOutputTextarea = document.querySelector(
    ".reviewed_code_output"
  );
  if (reviewedCodeOutputTextarea) {
    const originalText = reviewedCodeOutputTextarea.value;
    reviewedCodeOutputTextarea.value = ""; // Svuota per l'animazione

    let charIndex = 0;
    function typeReviewedCode() {
      if (charIndex < originalText.length) {
        reviewedCodeOutputTextarea.value += originalText.charAt(charIndex);
        charIndex++;
        reviewedCodeOutputTextarea.scrollTop =
          reviewedCodeOutputTextarea.scrollHeight; // Scorrimento automatico
        autoResizeTextarea(reviewedCodeOutputTextarea); // Ridimensiona ad ogni carattere
        setTimeout(typeReviewedCode, 12); // Velocità di digitazione
      } else {
        // Quando l'animazione è completa, assicurati che l'altezza sia finale e corretta
        autoResizeTextarea(reviewedCodeOutputTextarea);
      }
    }

    // Inizia l'animazione se c'è testo
    if (originalText.length > 0) {
      typeReviewedCode();
    } else {
      // Se non c'è testo, assicurati che la textarea sia comunque correttamente dimensionata
      autoResizeTextarea(reviewedCodeOutputTextarea);
    }
  }
});

// --- Funzione per copiare il testo della textarea di output ---
function copyFunction() {
  const reviewedCodeOutputTextarea = document.querySelector(
    ".reviewed_code_output"
  );
  if (reviewedCodeOutputTextarea) {
    // Seleziona il testo all'interno della textarea
    reviewedCodeOutputTextarea.select();
    // Per supportare i dispositivi mobili e garantire che tutto il testo sia selezionato
    reviewedCodeOutputTextarea.setSelectionRange(0, 99999);

    // Utilizza l'API Clipboard per copiare il testo
    navigator.clipboard
      .writeText(reviewedCodeOutputTextarea.value)
      .then(() => {
        // Successo nella copia
        console.log("Testo copiato con successo!");
        const copyButton = document.querySelector(
          'form.reviewed_code_form button[onclick="copyFunction()"]'
        );
        if (copyButton) {
          const originalButtonText = copyButton.textContent;
          copyButton.textContent = "Copiato!"; // Feedback visivo
          setTimeout(() => {
            copyButton.textContent = originalButtonText; // Torna al testo originale
          }, 2000); // Dopo 2 secondi
        }
      })
      .catch((err) => {
        // Gestione degli errori (ad esempio, permessi negati dal browser)
        console.error("Errore durante la copia del testo: ", err);
        alert(
          "Impossibile copiare il testo. Si prega di selezionare e copiare manualmente."
        );
      });
  }
}
