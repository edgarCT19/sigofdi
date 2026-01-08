from django.shortcuts import render
from django.views.decorators.cache import never_cache

from system.models import Area, Edificio, UnidadResponsable
from system.decorators import login_required_custom


@never_cache
@login_required_custom
def listar_areas_admin(request):
    """
    Lista las áreas en el panel de administración.
    Filtra por unidad responsable y edificio si se especifican en la URL.
    """
    unidades = UnidadResponsable.objects()

    ur_id = request.GET.get('unidad_responsable')
    edificio_id = request.GET.get('edificio')

    edificios = []
    areas = []

    if ur_id:
        # Filtrar edificios por unidad responsable
        edificios = Edificio.objects(unidad_responsable=ur_id)

        if edificio_id:
            # Filtrar áreas por unidad responsable y edificio
            areas = Area.objects(unidad_responsable=ur_id, edificio=edificio_id)
        else:
            # Todas las áreas de la unidad responsable
            areas = Area.objects(unidad_responsable=ur_id)

    context = {
        'unidades': unidades,
        'edificios': edificios,
        'areas': areas,
        'ur_id': ur_id,
        'edificio_id': edificio_id,
    }

    return render(request, 'systemsigo/Areas/areas.html', context)