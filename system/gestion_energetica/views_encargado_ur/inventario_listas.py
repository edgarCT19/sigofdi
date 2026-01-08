from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.contrib import messages

from system.decorators import login_required_custom
from system.models import InventarioClimatizacion, InventarioLuminarias, InventarioMiscelaneos, Subestacion, PeriodoInventario
from system.views import get_user

# Función auxiliar para filtrar por periodo
def filtrar_por_periodo(queryset, request):
    periodo_id = request.GET.get("periodo")

    if periodo_id:
        try:
            queryset = queryset.filter(periodo=periodo_id)
        except:
            pass

    return queryset, periodo_id

# Vista de listados de inventarios energeticos
@never_cache
@login_required_custom
def listar_climatizacion_encargado(request):
    """
    Vista para listar los inventarios de climatización del encargado de unidad responsable (UR).

    - Esta vista obtiene todos los registros de inventarios de climatización asociados a la unidad responsable del usuario    
    y calcula los totales de potencia, horas y consumo mensual. También obtiene las tarifas disponibles de las subestaciones asociadas a la UR.
    - Si el usuario no es un encargado de UR, se redirige a la página de inicio con un mensaje de error.
    - Los registros se pasan al contexto para ser renderizados en la plantilla correspondiente.
    """

    user = get_user(request)
    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    # Obtener todos los periodos (para el filtro)
    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')

    registros = InventarioClimatizacion.objects(unidad_responsable=user.unidad_responsable)

    registros, periodo_id = filtrar_por_periodo(registros, request)

    total_potencia = sum([i.potencia_total for i in registros])
    total_horas = sum([i.horas_mes for i in registros])
    total_consumo = sum([i.consumo_mensual for i in registros])

    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    context = {
        "registros": registros,
        "periodos": periodos,
        "periodo_seleccionado": periodo_id,
        "titulo": "Inventario de Climatización",
        'total_potencia': total_potencia,
        'total_horas': total_horas,
        'total_consumo': total_consumo,
        "tarifas_disponibles": tarifas_disponibles
    }

    return render(request, "Encargado_UR/Inventarios/Climatizacion/climatizacion_list.html", context)

@never_cache
@login_required_custom
def listar_luminarias_encargado(request):
    """ 
    Vista para listar los inventarios de luminarias del encargado de unidad responsable (UR).

    - Esta vista obtiene todos los registros de inventarios de luminarias asociados a la unidad responsable del usuario 
    y calcula los totales de potencia, horas y consumo mensual. También obtiene las tarifas disponibles de las subestaciones asociadas a la UR.
    - Si el usuario no es un encargado de UR, se redirige a la página de inicio con un mensaje de error.
    - Los registros se pasan al contexto para ser renderizados en la plantilla correspondiente.
    """

    user = get_user(request)
    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')

    registros = InventarioLuminarias.objects(unidad_responsable=user.unidad_responsable)

    registros, periodo_id = filtrar_por_periodo(registros, request)

    total_potencia = sum([i.potencia_total_lum for i in registros])
    total_horas = sum([i.consumo_mensual_horas for i in registros])
    total_consumo = sum([i.consumo_mensual for i in registros])

    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    context = {
        "registros": registros,
        "periodos": periodos,
        "periodo_seleccionado": periodo_id,
        "titulo": "Inventario de Luminarias",
        'total_potencia': total_potencia,
        'total_horas': total_horas,
        'total_consumo': total_consumo,
        "tarifas_disponibles": tarifas_disponibles
    }

    return render(request, "Encargado_UR/Inventarios/Luminarias/luminarias_list.html", context)

@never_cache
@login_required_custom
def listar_miscelaneos_encargado(request):
    """
    Vista para listar los inventarios de misceláneos del encargado de unidad responsable (UR).  
    
    - Esta vista obtiene todos los registros de inventarios de misceláneos asociados a la unidad responsable del usuario    
    y calcula los totales de potencia, horas y consumo mensual. También obtiene las tarifas disponibles de las subestaciones asociadas a la UR.
    - Si el usuario no es un encargado de UR, se redirige a la página de inicio con un mensaje de error.
    - Los registros se pasan al contexto para ser renderizados en la plantilla correspondiente.
    """

    user = get_user(request)
    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')

    registros = InventarioMiscelaneos.objects(unidad_responsable=user.unidad_responsable)

    registros, periodo_id = filtrar_por_periodo(registros, request)

    total_potencia = sum([i.potencia_total for i in registros])
    total_horas = sum([i.horas_mes for i in registros])
    total_consumo = sum([i.consumo_mensual for i in registros])

    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    context = {
        "registros": registros,
        "periodos": periodos,
        "periodo_seleccionado": periodo_id,
        "titulo": "Inventario de Misceláneos",
        'total_potencia': total_potencia,
        'total_horas': total_horas,
        'total_consumo': total_consumo,
        "tarifas_disponibles": tarifas_disponibles
    }

    return render(request, "Encargado_UR/Inventarios/Miscelaneos/miscelaneos_list.html", context)