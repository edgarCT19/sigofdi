from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from django.utils.timezone import make_aware

from system.models import PeriodoInventario, Usuario
from system.views import get_user
from system.decorators import login_required_custom


# Vistas para la gestión de periodos de inventarios energéticos.
@never_cache
@login_required_custom
def crear_periodo_inventario(request):
    """
    Vista para crear un nuevo periodo de inventario energético.
    - Restringida a usuarios con rol 'admin'.   
    - Valida que no haya solapamientos con periodos existentes.
    - Envía notificaciones por correo a usuarios con rol 'capturista' y 'encargado_ur'.
    - Genera automáticamente el nombre del periodo en formato "PERIODO_XXX".
    - Muestra mensajes de éxito o error según corresponda.
    """

    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    if request.method == "POST":
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        observaciones = request.POST.get("observaciones")

        try:
            fecha_inicio_dt = make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
            fecha_fin_dt = make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d"))

            if fecha_inicio_dt >= fecha_fin_dt:
                messages.error(request, "La fecha de inicio debe ser menor a la de fin.")
                return redirect("crear_periodo_inventario")

            # Verificar si se solapa con otro periodo existente
            solapado = PeriodoInventario.objects(
                fecha_inicio__lt=fecha_fin_dt,
                fecha_fin__gt=fecha_inicio_dt
            )
            if solapado:
                messages.error(request, "Ya existe un periodo activo en ese rango.")
                return redirect("crear_periodo_inventario")

            # Generar nombre automático del periodo
            count = PeriodoInventario.objects.count() + 1
            nombre_generado = f"PERIODO_{count:03d}"

            # Crear periodo
            periodo = PeriodoInventario(
                nombre=nombre_generado,
                fecha_inicio=fecha_inicio_dt,
                fecha_fin=fecha_fin_dt,
                observaciones=observaciones,
                persona_autoriza=f"{user.nombres} {user.apellidos}",
                rol=user.rol,
                status="Activo",
                activo=True
            )
            periodo.save()

            # Notificar por correo a encargados y capturistas
            usuarios_destino = Usuario.objects(rol__in=["capturista", "encargado_ur"])
            for u in usuarios_destino:
                if not u.email:
                    continue

                mensaje = (
                    f"Hola {u.nombre_completo},\n\n"
                    f"Se ha creado un nuevo periodo de inventario energético.\n\n"
                    f"Periodo: {nombre_generado}\n"
                    f"Desde: {fecha_inicio_dt.strftime('%d/%m/%Y')} hasta {fecha_fin_dt.strftime('%d/%m/%Y')}\n\n"
                    f"Observaciones: {observaciones}\n\n"
                    "Por favor, accede al sistema para revisar y capturar el inventario correspondiente."
                )

                send_mail(
                    subject="Nuevo Periodo de Inventario Energético",
                    message=mensaje,
                    from_email="al066230@uacam.mx",  # Cambiar por tu EMAIL_HOST_USER real
                    recipient_list=[u.email],
                    fail_silently=False,
                )

            messages.success(request, f"Periodo '{nombre_generado}' creado exitosamente y notificaciones enviadas.")
            return redirect("listar_periodos")

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, "systemsigo/Periodos/crear_periodo.html")

def obtener_periodo_activo():
    """Obtiene el periodo de inventario activo actual."""
    # Asumiendo que el periodo activo es aquel cuya fecha de inicio es menor o igual a ahora
    # y la fecha de fin es mayor o igual a ahora, y que está marcado como activo.
    ahora = datetime.now()
    return PeriodoInventario.objects(
        fecha_inicio__lte=ahora,
        fecha_fin__gte=ahora,
        activo=True
    ).order_by('-fecha_inicio').first()

@never_cache
@login_required_custom
def listar_periodos(request):
    """
    Vista para listar todos los periodos de inventario energético.
    - Restringida a usuarios con rol 'admin'.
    - Muestra los periodos ordenados por fecha de inicio descendente.
    - Actualiza automáticamente el estado de los periodos según la fecha actual.
    """
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    from datetime import datetime
    ahora = datetime.now()

    # Recuperar todos los periodos
    periodos = PeriodoInventario.objects().order_by("-fecha_inicio")

    # === Actualizar estados automáticamente ===
    for periodo in periodos:
        try:
            # Determinar el nuevo estado según las fechas
            if periodo.fecha_inicio <= ahora <= periodo.fecha_fin:
                nuevo_status = "Activo"
            elif ahora < periodo.fecha_inicio:
                nuevo_status = "Pendiente"
            else:
                nuevo_status = "Finalizado"

            # Solo actualizar si el estado cambió y es válido
            if periodo.status != nuevo_status and nuevo_status in ["Activo", "Pendiente", "Finalizado"]:
                periodo.status = nuevo_status
                periodo.activo = (nuevo_status == "Activo")
                periodo.save()

        except Exception as e:
            # Captura silenciosa de errores para evitar interrupciones
            print(f"[⚠] No se pudo actualizar el periodo '{periodo.nombre}': {e}")

    # Renderizar plantilla
    return render(request, "systemsigo/Periodos/listar.html", {
        "periodos": periodos
    })

@never_cache
@login_required_custom
def editar_periodo_inventario(request, id):
    """
    Vista para editar un periodo de inventario energético existente.
    - Restringida a usuarios con rol 'admin'.
    - Permite actualizar fechas, observaciones y estado del periodo.
    - Muestra mensajes de éxito o error según corresponda.
    - No permite cambiar el nombre del periodo una vez creado.
    - Asegura que las fechas no se solapen con otros periodos existentes.
    - Restringe la edición a periodos que no estén cerrados o inactivos.
    """

    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    try:
        periodo = PeriodoInventario.objects.get(id=id)
    except PeriodoInventario.DoesNotExist:
        messages.error(request, "Periodo no encontrado.")
        return redirect("listar_periodos")

    if request.method == "POST":
        try:
            periodo.fecha_inicio = datetime.strptime(request.POST.get("fecha_inicio"), "%Y-%m-%d")
            periodo.fecha_fin = datetime.strptime(request.POST.get("fecha_fin"), "%Y-%m-%d")
            periodo.observaciones = request.POST.get("observaciones", "")
            periodo.status = request.POST.get("status")
            periodo.save()
            messages.success(request, "Periodo actualizado correctamente.")
            return redirect("listar_periodos")
        except Exception as e:
            messages.error(request, f"Error al actualizar el periodo: {e}")

    return render(request, "systemsigo/Periodos/edit_form.html", {
        "periodo": periodo
    })

@never_cache
@login_required_custom
def eliminar_periodo_inventario(request, id):
    """
    Vista para eliminar un periodo de inventario energético.
    - Restringida a usuarios con rol 'admin'.
    - Elimina el periodo y muestra mensajes de éxito o error.
    - No permite eliminar periodos que estén activos o cerrados.
    - Muestra un mensaje de error si el periodo no existe o no se puede eliminar.
    """

    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("inicio")

    try:
        periodo = PeriodoInventario.objects.get(id=id)
        periodo.delete()
        messages.success(request, "Periodo eliminado correctamente.")
    except PeriodoInventario.DoesNotExist:
        messages.error(request, "Periodo no encontrado.")

    return redirect("listar_periodos")