const darkModeToggle = document.getElementById('darkModeToggle');
const logoImg = document.getElementById('logo');
const icon = darkModeToggle?.querySelector('i');

function updateDarkModeUI(isDark, showTooltip = false) {
    let title = '';

    if (isDark) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
        icon?.classList.replace('bi-moon', 'bi-sun');
        logoImg.src = logoImg.dataset.logoDark;  // Usa data-logo-dark
        title = 'Cambiar a modo claro';
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
        icon?.classList.replace('bi-sun', 'bi-moon');
        logoImg.src = logoImg.dataset.logoLight;  // Usa data-logo-light
        title = 'Cambiar a modo oscuro';
    }

    darkModeToggle?.setAttribute('title', title);

    const oldTooltip = bootstrap.Tooltip.getInstance(darkModeToggle);
    if (oldTooltip) oldTooltip.dispose();

    const newTooltip = new bootstrap.Tooltip(darkModeToggle, {
        title: title
    });

    if (showTooltip && darkModeToggle?.matches(':hover')) {
        newTooltip.show();
    }
}

// Inicializar Dark Mode desde localStorage
window.addEventListener('DOMContentLoaded', () => {
    const isDark = localStorage.getItem('darkMode') === 'enabled';
    updateDarkModeUI(isDark);
});

// Toggle Dark Mode en clic
darkModeToggle?.addEventListener('click', () => {
    const isDarkNow = !document.body.classList.contains('dark-mode');
    updateDarkModeUI(isDarkNow, true);
});