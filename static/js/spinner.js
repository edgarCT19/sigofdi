  const form = document.querySelector("form");
  const spinner = document.getElementById("loadingSpinner");

  form.addEventListener("submit", function () {
    // Mostrar el spinner en pantalla completa
    spinner.style.display = "flex";
    
    // Cambiar el texto del botón
    const submitButton = form.querySelector("button[type='submit']");
    submitButton.disabled = true;
    submitButton.innerText = "Cargando...";
  });