from django.http import JsonResponse
from django.views.decorators.http import require_GET

from system.decorators import login_required_custom
from system.models import Area, Edificio, UnidadResponsable

@require_GET
@login_required_custom
def ajax_edificios_por_ur_admin(request):
    ur_id = request.GET.get('ur_id')
    if not ur_id:
        return JsonResponse({"ok": False, "error": "Falta ur_id"}, status=400)
    ur = UnidadResponsable.objects(id=ur_id).first()
    if not ur:
        return JsonResponse({"ok": False, "error": "UR no encontrada"}, status=404)
    edificios = Edificio.objects(unidad_responsable=ur).only('id', 'nombre')
    data = [{"id": str(e.id), "nombre": e.nombre} for e in edificios]
    return JsonResponse({"ok": True, "data": data})

@require_GET
@login_required_custom
def ajax_areas_por_ur_admin(request):
    ur_id = request.GET.get('ur_id')
    if not ur_id:
        return JsonResponse({"ok": False, "error": "Falta ur_id"}, status=400)
    ur = UnidadResponsable.objects(id=ur_id).first()
    if not ur:
        return JsonResponse({"ok": False, "error": "UR no encontrada"}, status=404)
    areas = Area.objects(unidad_responsable=ur).only('id', 'nombre')
    data = [{"id": str(a.id), "nombre": a.nombre} for a in areas]
    return JsonResponse({"ok": True, "data": data})
