  // Inicializa tooltips Bootstrap
  document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
  });

  function toggleClearButton(input) {
    const clearBtn = document.getElementById('clear-search');
    clearBtn.classList.toggle('d-none', input.value.trim() === '');
  }

  function clearSearch() {
    const input = document.getElementById('input-search');
    input.value = '';
    toggleClearButton(input);
    input.focus();
  }