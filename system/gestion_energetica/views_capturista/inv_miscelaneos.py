from datetime import datetime

from decimal import Decimal, ROUND_HALF_UP

from mongoengine.errors import DoesNotExist

from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect

from system.models import NIVELES, Area, Edificio, InventarioMiscelaneos, PeriodoInventario
from system.decorators import login_required_custom
from system.views import get_user

# Vistas de funciones de inventario energetico de misceláneos
@never_cache
@login_required_custom
def registrar_inventario_miscelaneos(request):
    """ 
    Registrar un nuevo inventario de misceláneos.

    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene los edificios y niveles disponibles para la unidad responsable.
    - Filtra las áreas según el edificio seleccionado.
    - Procesa el formulario de registro de inventario.
    - Calcula potencia total y consumo mensual.
    - Guarda el inventario y redirige a la lista de inventarios.
    """

    user = get_user(request)
    if not user or user.rol != "capturista":
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    # 1) Obtener periodo activo
    periodo_activo = PeriodoInventario.objects(status="Activo").first()
    if not periodo_activo:
        messages.error(request, "No hay un periodo de inventario activo.")
        return redirect("listar_inventario_miscelaneos")

    # 2) Datos iniciales
    edificios = Edificio.objects(unidad_responsable=user.unidad_responsable)
    niveles   = NIVELES
    eid       = request.GET.get("edificio") or request.session.get("edificio_misc")
    nsel      = request.GET.get("nivel")   or request.session.get("nivel_misc")
    request.session["edificio_misc"] = eid
    request.session["nivel_misc"]    = nsel

    areas_filtradas = Area.objects(edificio=eid) if eid else []

    if request.method == "POST":
        try:
            edificio    = Edificio.objects.get(id=request.POST["edificio"])
            area        = Area.objects.get(id=request.POST["area"])
            nivel       = request.POST["nivel"]
            marca       = request.POST["marca"]
            miscelaneos = request.POST["miscelaneos"]
            modelo      = request.POST["modelo"]

            voltaje       = Decimal(request.POST["voltaje"])
            amperaje      = Decimal(request.POST["amperaje"])
            potencia      = voltaje * amperaje
            potencia_total= potencia / 1000
            horas_mes     = Decimal(request.POST["horas_mes"])
            consumo_mensual = (potencia_total * horas_mes).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            InventarioMiscelaneos(
                unidad_responsable = user.unidad_responsable,
                periodo            = periodo_activo,           # <-- aquí
                edificio           = edificio,
                nivel              = nivel,
                area               = area,
                marca              = marca,
                miscelaneos        = miscelaneos,
                modelo             = modelo,
                voltaje            = voltaje,
                amperaje           = amperaje,
                potencia           = potencia,
                potencia_total     = potencia_total,
                horas_mes          = horas_mes,
                consumo_mensual    = consumo_mensual,
                creado_por         = user
            ).save()

            messages.success(request, "Inventario registrado correctamente.")
            return redirect("listar_inventario_miscelaneos")

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(
        request,
        "Capturistas/Inventarios/Miscelaneos/add_form.html",
        {
            "edificios"            : edificios,
            "niveles"              : niveles,
            "areas_filtradas"      : areas_filtradas,
            "edificio_seleccionado": eid,
            "nivel_seleccionado"   : nsel,
        },
    )

@never_cache
@login_required_custom
def listar_inventario_miscelaneos(request):
    """
    Listar todos los registros de inventario de misceláneos. 

    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene los registros de inventario de misceláneos para la unidad responsable.
    - Verifica si hay un periodo activo de inventario.
    - Renderiza la plantilla con los registros y el periodo activo.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect("login")
    
    now = datetime.now()

    periodo_activo = PeriodoInventario.objects(
        fecha_inicio__lte=now,
        fecha_fin__gte=now,
        status="Activo",
        activo=True
    ).first()

    if not periodo_activo:
        return render(request, 'Capturistas/Inventarios/Miscelaneos/inventario_lista.html', {
            'registros': [],
            'periodo_activo': None
        })

    registros = InventarioMiscelaneos.objects(
        unidad_responsable=user.unidad_responsable,
        creado_por=user,
        periodo=periodo_activo 
    ).order_by('-fecha_registro')

    return render(
        request,
        "Capturistas/Inventarios/Miscelaneos/inventario_lista.html",
        {"registros": registros,
         "periodo_activo": periodo_activo},
    )

@never_cache
@login_required_custom
def obtener_areas_por_edificio_miscelaneos(request):
    """
    Obtener áreas filtradas por edificio para el inventario de misceláneos.
    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el ID del edificio desde la solicitud GET.
    - Filtra las áreas según el edificio seleccionado.
    - Devuelve un JSON con las áreas disponibles.
    """

    edificio_id = request.GET.get("edificio_id")
    if not edificio_id:
        return JsonResponse([], safe=False)

    try:
        areas = Area.objects(edificio=edificio_id).only("id", "nombre")
        data = [{"id": str(area.id), "nombre": area.nombre} for area in areas]
        return JsonResponse(data, safe=False)
    except Exception:
        return JsonResponse([], safe=False)

@never_cache
@login_required_custom
def editar_inventario_miscelaneos(request, id):
    """
    Editar un registro de inventario de misceláneos.

    - Verifica que el usuario esté logueado y tenga una sesión activa.  
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene el registro de inventario a editar.
    - Filtra los edificios y áreas según el registro.
    - Procesa el formulario de edición.
    - Actualiza los datos del inventario y redirige a la lista de inventarios.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    try:
        inventario = InventarioMiscelaneos.objects.get(id=id)
    except DoesNotExist:
        messages.error(request, "Registro no encontrado.")
        return redirect('listar_inventario_miscelaneos')

    if inventario.unidad_responsable != user.unidad_responsable:
        messages.error(request, "No tienes permiso para editar este registro.")
        return redirect('listar_inventario_miscelaneos')

    edificios = Edificio.objects(unidad_responsable=user.unidad_responsable)
    niveles = NIVELES
    areas_filtradas = Area.objects(edificio=inventario.edificio)

    if request.method == 'POST':
        try:
            inventario.edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            inventario.nivel = request.POST.get('nivel')
            inventario.area = Area.objects.get(id=request.POST.get('area'))
            inventario.marca = request.POST.get('marca')
            inventario.miscelaneos = request.POST.get('miscelaneos')
            inventario.modelo = request.POST.get('modelo')
            inventario.voltaje = Decimal(request.POST.get('voltaje'))
            inventario.amperaje = Decimal(request.POST.get('amperaje'))
            inventario.potencia = inventario.voltaje * inventario.amperaje
            inventario.potencia_total = inventario.potencia / 1000
            inventario.horas_mes = Decimal(request.POST.get('horas_mes'))
            inventario.consumo_mensual = inventario.potencia_total * inventario.horas_mes
            inventario.actualizado_por = user
            inventario.ultima_actualizacion = datetime.now()
            inventario.save()

            messages.success(request, "Registro actualizado correctamente.")
            return redirect('listar_inventario_miscelaneos')
        except Exception as e:
            messages.error(request, f"Error al actualizar: {e}")

    return render(request, 'Capturistas/Inventarios/Miscelaneos/edit_form.html', {
        'inventario': inventario,
        'edificios': edificios,
        'niveles': niveles,
        'areas_filtradas': areas_filtradas,
    })

@never_cache
@login_required_custom
def eliminar_inventario_miscelaneos(request, id):
    """
    Eliminar un registro de inventario de misceláneos. 
     
    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene el registro de inventario a eliminar.
    - Elimina el registro y redirige a la lista de inventarios con un mensaje de éxito.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    try:
        inventario = InventarioMiscelaneos.objects.get(id=id)
        if inventario.unidad_responsable != user.unidad_responsable:
            messages.error(request, "No tienes permiso para eliminar este registro.")
        else:
            inventario.delete()
            messages.success(request, "Registro eliminado correctamente.")
    except DoesNotExist:
        messages.error(request, "Registro no encontrado.")

    return redirect('listar_inventario_miscelaneos')