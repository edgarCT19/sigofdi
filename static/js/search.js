  //Buscador dinámico
  document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("input-search");
    const clearBtn = document.getElementById("clear-search");
    const tableRows = document.querySelectorAll("table tbody tr");

    // Filtrado en tiempo real
    searchInput.addEventListener("input", function () {
      const query = this.value.trim().toLowerCase();

      // Mostrar/ocultar botón de limpiar
      if (query !== "") {
        clearBtn.classList.remove("d-none");
      } else {
        clearBtn.classList.add("d-none");
      }

      // Filtrar filas
      tableRows.forEach((row) => {
        const rowText = row.innerText.toLowerCase();
        row.style.display = rowText.includes(query) ? "" : "none";
      });
    });

    // Botón de limpiar búsqueda
    clearBtn.addEventListener("click", function () {
      searchInput.value = "";
      clearBtn.classList.add("d-none");

      // Mostrar todas las filas al limpiar
      tableRows.forEach((row) => {
        row.style.display = "";
      });
    });
  });