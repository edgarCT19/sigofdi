  // Para los selects, aseguramos que tengan valor inicial vacío para activar el label flotante
    document.querySelectorAll('select').forEach(select => {
        select.addEventListener('change', function () {
            if (this.value !== '') {
                this.setAttribute('value', this.value);
            } else {
                this.removeAttribute('value');
            }
        });
    });