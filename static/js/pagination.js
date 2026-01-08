document.addEventListener('DOMContentLoaded', function () {
    const rowsPerPage = 8;
    const rows = Array.from(document.querySelectorAll('#table-body tr'));
    const paginationContainer = document.getElementById('pagination');

    function displayRows(startIndex) {
        rows.forEach((row, index) => {
            row.style.display = (index >= startIndex && index < startIndex + rowsPerPage) ? '' : 'none';
        });
    }

    function setupPagination() {
        const totalPages = Math.ceil(rows.length / rowsPerPage);
        paginationContainer.innerHTML = '';

        // Botón anterior
        const prevBtn = document.createElement('li');
        prevBtn.className = 'page-item';
        prevBtn.innerHTML = `<a class="page-link" href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a>`;
        paginationContainer.appendChild(prevBtn);

        // Botones de número
        for (let i = 0; i < totalPages; i++) {
            const pageBtn = document.createElement('li');
            pageBtn.className = 'page-item';
            pageBtn.innerHTML = `<a class="page-link" href="#">${i + 1}</a>`;
            pageBtn.addEventListener('click', function (e) {
                e.preventDefault();
                currentPage = i;
                displayRows(currentPage * rowsPerPage);
                setActivePage(currentPage);
            });
            paginationContainer.appendChild(pageBtn);
        }

        // Botón siguiente
        const nextBtn = document.createElement('li');
        nextBtn.className = 'page-item';
        nextBtn.innerHTML = `<a class="page-link" href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a>`;
        paginationContainer.appendChild(nextBtn);

        prevBtn.addEventListener('click', function (e) {
            e.preventDefault();
            if (currentPage > 0) {
                currentPage--;
                displayRows(currentPage * rowsPerPage);
                setActivePage(currentPage);
            }
        });

        nextBtn.addEventListener('click', function (e) {
            e.preventDefault();
            if (currentPage < totalPages - 1) {
                currentPage++;
                displayRows(currentPage * rowsPerPage);
                setActivePage(currentPage);
            }
        });
    }

    function setActivePage(index) {
        const pageItems = paginationContainer.querySelectorAll('li');
        pageItems.forEach(item => item.classList.remove('active'));
        if (pageItems[index + 1]) { // +1 por el botón "Anterior"
            pageItems[index + 1].classList.add('active');
        }
    }

    let currentPage = 0;
    displayRows(0);
    setupPagination();
    setActivePage(0);
});