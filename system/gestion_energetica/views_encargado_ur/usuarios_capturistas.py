import secrets

from mongoengine.errors import NotUniqueError

from django.views.decorators.cache import never_cache
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib import messages

from system.decorators import login_required_custom
from system.models import Subestacion, Usuario, UnidadResponsable
from system.views import get_user


@never_cache
@login_required_custom
def listar_capturistas(request):
    """ 
    Listar capturistas de la unidad responsable del usuario logueado.

    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el usuario logueado y su unidad responsable.
    - Filtra los capturistas que pertenecen a la misma unidad responsable.

    - Obtiene las subestaciones y tarifas disponibles para la unidad responsable.
    - Renderiza la plantilla con la lista de capturistas y datos adicionales.
    """

    user = get_user(request)
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Sesión expirada. Inicia sesión nuevamente.")
        return redirect('login')

    usuario_logueado = Usuario.objects(id=user_id).first()

    if not usuario_logueado:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    # Capturistas que tienen la misma unidad responsable
    urs = usuario_logueado.unidad_responsable if usuario_logueado.unidad_responsable else []
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)
    capturistas = Usuario.objects(
    unidad_responsable=usuario_logueado.unidad_responsable,
    rol="capturista",
    is_active=True
)

    context = {
        'usuarios': capturistas,
        'titulo': "Lista de Capturistas Activos",
    }

    return render(request, 'Encargado_UR/Usuarios/listar_userCap.html', {
        'usuarios': capturistas,
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles,
        'context': context,
    })

@never_cache
@login_required_custom
def Add_Capturistas(request):
    """ 
    Agregar un nuevo capturista.

    - Verifica que el usuario esté logueado y tenga el rol de encargado de unidad responsable.
    - Valida que la matrícula y el correo electrónico no estén ya registrados.
    - Crea un nuevo usuario capturista con una contraseña generada aleatoriamente.
    - Envía un correo electrónico al nuevo capturista con sus credenciales.
    - Redirige a la lista de capturistas con un mensaje de éxito o error.
    """

    user = Usuario.objects(id=request.session['user_id']).first()

    if not user or user.rol != 'encargado_ur':
        return redirect('encargado_ur')

    urs = user.unidad_responsable if user.unidad_responsable else []

    if request.method == "POST":

        matricula = request.POST.get('matricula')
        email = request.POST.get('email')
        ur_id = request.POST.get('unidad_responsable')

        # -------- VALIDACIONES --------

        if not ur_id:
            messages.error(request, "Debes seleccionar una Unidad Responsable.")
            return redirect('add_capturista')

        ur = UnidadResponsable.objects(id=ur_id).first()

        if not ur or ur not in urs:
            messages.error(request, "UR inválida.")
            return redirect('add_capturista')

        matricula_existe = Usuario.objects(matricula=matricula).first()
        email_existe = Usuario.objects(email=email).first()

        if matricula_existe and email_existe:
            messages.error(request, 'La matrícula y el correo electrónico ya están registrados.')
            return redirect('add_capturista')

        if matricula_existe:
            messages.error(request, 'La matrícula ya está registrada.')
            return redirect('add_capturista')

        if email_existe:
            messages.error(request, 'El correo electrónico ya está registrado.')
            return redirect('add_capturista')

        # -------- CREACIÓN --------

        try:
            raw_password = secrets.token_urlsafe(10)
            hashed_password = Usuario.hash_password(raw_password)

            usuario = Usuario(
                matricula=matricula,
                nombres=request.POST.get('nombres'),
                apellidos=request.POST.get('apellidos'),
                email=email,
                telefono=request.POST.get('telefono'),
                rol='capturista',
                unidad_responsable=[ur],   # SOLO UNA UR
                password=hashed_password,
                creado_por=user,
            )

            usuario.save()

            send_mail(
                'Tu cuenta ha sido creada en el Sistema SIGO',
                f'''Hola {usuario.nombre_completo},

                    Usuario: {usuario.email}
                    Contraseña: {raw_password}
                    ''',
                'sigo-50001@uacam.mx',
                [usuario.email],
                fail_silently=False,
            )

            messages.success(request, 'Capturista agregado exitosamente.')
            return redirect('lista_capturistas')

        except (NotUniqueError, ValidationError):
            messages.error(request, 'Error al guardar el usuario.')
            return redirect('add_capturista')

    # -------- DATOS PARA TEMPLATE --------

    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    return render(request, "Encargado_UR/Usuarios/add_userCap.html", {
        "urs": urs,   # Ahora mandamos lista de URs
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles
    })

@never_cache
@login_required_custom
def Edit_Capturistas(request, id):
    """ 
    Editar un capturista existente.

    - Verifica que el usuario esté logueado y tenga el rol de encargado de unidad responsable.
    - Obtiene el usuario capturista a editar.
    - Actualiza los datos del capturista con los valores del formulario.
    - Redirige a la lista de capturistas con un mensaje de éxito.
    """

    user = Usuario.objects(id=request.session['user_id']).first()
    if user.rol != 'encargado_ur':
        return redirect('encargado_ur')

    usuario = Usuario.objects(id=id, creado_por=user).first()
    if not usuario:
        return redirect('error')

    if request.method == "POST":
        usuario.matricula = request.POST.get('matricula')
        usuario.nombres = request.POST.get('nombres')
        usuario.apellidos = request.POST.get('apellidos')
        usuario.email = request.POST.get('email')
        usuario.telefono = request.POST.get('telefono')
        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('lista_capturistas')

    urs = user.unidad_responsable if user.unidad_responsable else []
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)
    return render(request, "Encargado_UR/Usuarios/edit_userCap.html", {"usuario": usuario, 'subestaciones': subestaciones, 'tarifas_disponibles':tarifas_disponibles})

@never_cache
@login_required_custom
def Delete_Capturista(request, id):
    """ 
    Eliminar un capturista existente.

    - Verifica que el usuario esté logueado y tenga el rol de encargado de unidad responsable.
    - Obtiene el usuario capturista a eliminar.
    - Elimina el usuario capturista y redirige a la lista de capturistas con un mensaje de éxito.
    """

    user = Usuario.objects(id=request.session['user_id']).first()
    if user.rol != 'encargado_ur':
        return redirect('lista_capturistas')

    usuario = Usuario.objects(id=id, creado_por=user).first()
    if usuario:
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
    return redirect('lista_capturistas')