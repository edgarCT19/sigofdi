

(() => {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');

    menuToggle?.addEventListener('click', () => {
        sidebar?.classList.toggle('show');
    });

    const submenuParents = document.querySelectorAll('#sidebar .has-submenu > a');
    submenuParents.forEach(parent => {
        parent.addEventListener('click', (e) => {
            e.preventDefault();
            parent.parentElement.classList.toggle('open');
        });
    });

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const sidebarLinks = document.querySelectorAll('#sidebar a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function () {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
})();