import secrets

from mongoengine.errors import NotUniqueError

from django.views.decorators.cache import never_cache
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib import messages

from system.decorators import login_required_custom
from system.models import Subestacion, Usuario
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
    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
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
    if user.rol != 'encargado_ur':
        return redirect('inicio')

    if request.method == "POST":
        matricula = request.POST.get('matricula')
        email = request.POST.get('email')

        matricula_existe = Usuario.objects(matricula=matricula).first()
        email_existe = Usuario.objects(email=email).first()

        if matricula_existe and email_existe:
            messages.error(request, 'La matrícula y el correo electrónico ya están registrados.')
        elif matricula_existe:
            messages.error(request, 'La matrícula ya está registrada.')
        elif email_existe:
            messages.error(request, 'El correo electrónico ya está registrado.')
        else:
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
                    unidad_responsable=user.unidad_responsable,
                    password=hashed_password,
                    creado_por=user,
                )
                usuario.save()

                send_mail(
                    'Tu cuenta ha sido creada en el Sistema SIGO',
                    f'Hola {usuario.nombre_completo},\n\nUsuario: {usuario.email}\nContraseña: {raw_password}',
                    'al066230@uacam.mx',
                    [usuario.email],
                    fail_silently=False,
                )

                messages.success(request, 'Capturista agregado exitosamente.')
                return redirect('lista_capturistas')

            except (NotUniqueError, ValidationError):
                messages.error(request, 'Ocurrió un error al guardar el usuario. Verifica los datos.')

    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    return render(request, "Encargado_UR/Usuarios/add_userCap.html", {
        "unidad": user.unidad_responsable,
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
        return redirect('inicio')

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

    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
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