document.addEventListener("DOMContentLoaded", function () {
  // Selecciona todos los inputs de texto y textareas
  const inputs = document.querySelectorAll('input[type="text"], textarea');

  inputs.forEach(input => {
    input.addEventListener("input", function () {
      this.value = this.value.toUpperCase();
    });
  });
});
