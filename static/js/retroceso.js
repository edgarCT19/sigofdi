function volverAtras(e) {
    e.preventDefault();

    if (document.referrer) {
        window.history.back();
    } else {
        window.location.href = "{% url 'listar_facturas_admin' %}";
    }
}