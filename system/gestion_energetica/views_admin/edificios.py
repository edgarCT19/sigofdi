from django.shortcuts import render
from django.views.decorators.cache import never_cache

from system.models import Edificio, UnidadResponsable
from system.decorators import login_required_custom

@never_cache
@login_required_custom
def listar_edificios_admin(request):
    """
    Vista para listar todos los edificios registrados en el sistema.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    """

    unidad_id = request.GET.get('unidad_id')

    unidades = UnidadResponsable.objects.all().order_by('nombre')

    if unidad_id:
        edificios = Edificio.objects(unidad_responsable=unidad_id)
    else:
        edificios = Edificio.objects.all()

    return render(request, 'systemsigo/Edificios/edificios.html', {
        'edificios': edificios,
        'unidades': unidades,
        'unidad_id': unidad_id,
    })