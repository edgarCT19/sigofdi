from datetime import datetime

from django.shortcuts import render
from django.views.decorators.cache import never_cache

from system.decorators import login_required_custom
from system.models import PeriodoInventario, Subestacion
from system.views import get_user

@never_cache
@login_required_custom
def Inicio_encargado(request):
    user = get_user(request)

    # Buscar si hay un periodo activo actualmente
    hoy = datetime.now()
    periodo_activo = PeriodoInventario.objects(
        status="Activo",
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy,
        activo=True
    ).first()

    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    return render(request, 'systemsigo/index_encargado.html', {
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles,
        'periodo_alerta': periodo_activo  # Pasamos el periodo si existe
    })