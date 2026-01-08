from django.shortcuts import render
from django.views.decorators.cache import never_cache

from system.decorators import login_required_custom
from system.gestion_energetica.views_admin.periodos_inventarios import obtener_periodo_activo
from system.views import get_user

@never_cache
@login_required_custom
def Inicio_capturista (request):
    """Renderiza la vista de inicio para el capturista con el periodo activo."""
    
    user = get_user(request)
    periodo_activo = obtener_periodo_activo()
    return render(request, 'systemsigo/index_cap.html', {
        'periodo_activo': periodo_activo,
    })