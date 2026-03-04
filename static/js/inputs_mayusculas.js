document.addEventListener("DOMContentLoaded", function () {

  // Selecciona todos los inputs de texto y textareas
  // excepto los que tengan la clase .no-mayus
  const inputs = document.querySelectorAll(
    'input[type="text"]:not(.no-mayus), textarea:not(.no-mayus)'
  );

  inputs.forEach(input => {
    input.addEventListener("input", function () {
      this.value = this.value.toUpperCase();
    });
  });

});