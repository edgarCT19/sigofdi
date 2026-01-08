from bson import ObjectId

import secrets

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail

from system.decorators import login_required_custom
from system.models import Usuario, UnidadResponsable
from system.forms import UsuarioForm

# Vista de funciones CRUD de usuarios del sistema
@never_cache
@login_required_custom
def User_List(request):
    """Vista para listar usuarios activos del sistema.
     - Esta vista obtiene todos los usuarios activos y las unidades responsables
     - Renderiza la plantilla 'lista_usuarios.html' con los datos obtenidos
    """

    # Obtenemos los usuarios activos y las unidades responsables
    usuarios = Usuario.objects(is_active=True)
    unidad_responsable = UnidadResponsable.objects()
    return render(request, 'systemsigo/Usuarios/lista_usuarios.html', {
        'usuarios': usuarios,
        'unidad_responsable': unidad_responsable,
    })

@never_cache
@login_required_custom
def Add_User(request):
    """
    Vista para agregar un nuevo usuario al sistema.
     - Esta vista maneja tanto la visualización del formulario como el procesamiento de los datos enviados.
     - Verifica si el correo electrónico y la matrícula ya están registrados antes de crear un nuevo usuario.
     - Envía un correo electrónico al nuevo usuario con su contraseña generada.
     - Si el usuario es creado exitosamente, redirige a la lista de usuarios con un mensaje de éxito.
    """

    if request.method == "POST":
        email = request.POST.get('email')
        matricula = request.POST.get('matricula')
        
        # Verificamos si ya existen
        email_existente = Usuario.objects(email=email).first()
        matricula_existente = Usuario.objects(matricula=matricula).first()

        if email_existente and matricula_existente:
            messages.error(request, 'El correo y la matrícula ya están registrados.')
        elif email_existente:
            messages.error(request, 'El correo ya está registrado.')
        elif matricula and matricula_existente:
            messages.error(request, 'La matrícula ya está registrada.')
        else:
            try:
                raw_password = secrets.token_urlsafe(10)
                hashed_password = Usuario.hash_password(raw_password)

                rol = request.POST.get('rol')

                unidad_responsable = None
                if rol not in ['admin', 'admin_ambiental', 'admin_energia', 'admin_salud'] and request.POST.get('unidad_responsable'):
                    unidad_responsable = UnidadResponsable.objects.get(id=request.POST.get('unidad_responsable'))

                creado_por = Usuario.objects(id=request.session['user_id']).first() if 'user_id' in request.session else None

                usuario = Usuario(
                    matricula=matricula,
                    nombres=request.POST.get('nombres'),
                    apellidos=request.POST.get('apellidos'),
                    email=email,
                    telefono=request.POST.get('telefono'),
                    rol=request.POST.get('rol'),
                    unidad_responsable=unidad_responsable,
                    password=hashed_password,
                    creado_por=creado_por,
                )

                usuario.save()

                # Enviar correo con contraseña
                send_mail(
                    'Tu cuenta ha sido creada en el Sistema SIGO',
                    f'Hola {usuario.nombre_completo},\n\nTu cuenta ha sido creada exitosamente.\n\nUsuario: {usuario.email}\nContraseña: {raw_password}\n\nPor favor cambia tu contraseña una vez que inicies sesión.',
                    'tu_correo@gmail.com',
                    [usuario.email],
                    fail_silently=False,
                )

                messages.success(request, 'Usuario agregado exitosamente.')
                return redirect('usuarios')

            except Exception as e:
                messages.error(request, f"Ocurrió un error inesperado: {str(e)}")

    unidades = UnidadResponsable.objects()
    return render(request, "systemsigo/Usuarios/add_form.html", {"unidades": unidades})

@never_cache
@login_required_custom
def Edit_User(request, usuario_id):
    """
    Vista para editar un usuario existente.

     - Esta vista maneja tanto la visualización del formulario con los datos actuales del usuario como el procesamiento de los datos enviados.
     - Actualiza los campos del usuario y maneja la asociación con una unidad responsable si es necesario.
     - Si el usuario es actualizado exitosamente, redirige a la lista de usuarios con un mensaje de éxito.
    """

    try:
        usuario = Usuario.objects.get(id=ObjectId(usuario_id))
    except:
        raise Http404("Usuario no encontrado")

    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario.matricula = form.cleaned_data['matricula']
            usuario.nombres = form.cleaned_data['nombres']
            usuario.apellidos = form.cleaned_data['apellidos']
            usuario.email = form.cleaned_data['email']
            usuario.telefono = form.cleaned_data['telefono']
            usuario.rol = form.cleaned_data['rol']
            usuario.is_active = form.cleaned_data['is_active']

            # Asociar unidad responsable
            unidad_id = form.cleaned_data['unidad_responsable']
            if unidad_id:
                usuario.unidad_responsable = UnidadResponsable.objects.get(id=ObjectId(unidad_id))
            else:
                usuario.unidad_responsable = None

            if usuario.rol in ["admin", "admin_ambiental", "admin_energia", "admin_salud"]:
               usuario.unidad_responsable = None # Lineas agregadas

            usuario.save()

            # ✅ Mostrar mensaje de éxito
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuarios')
    else:
        form = UsuarioForm(initial={
            'matricula': usuario.matricula,
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'email': usuario.email,
            'telefono': usuario.telefono,
            'rol': usuario.rol,
            'is_active': usuario.is_active,
            'unidad_responsable': str(usuario.unidad_responsable.id) if usuario.unidad_responsable else '',
        })

    return render(request, 'systemsigo/Usuarios/edit_form.html', {
        'form': form,
        'usuario': usuario
    })

@never_cache
@login_required_custom
def Delete_User(request, usuario_id):
    """
    Vista para eliminar un usuario del sistema mediante AJAX.

     - Esta vista maneja la solicitud de eliminación de un usuario específico.
     - Si el usuario es encontrado, lo elimina y devuelve una respuesta JSON de éxito.
     - Si el usuario no es encontrado, devuelve una respuesta JSON de error.
     - Si el método de solicitud no es POST, devuelve un error 405.
    """

    if request.method == "POST":
        try:
            # Buscar el usuario por el ID de MongoDB
            usuario = Usuario.objects.get(id=ObjectId(usuario_id))
            usuario.deactivate()  # Deactivamos al usuario
            return JsonResponse({"success": True, "message": "La cuenta del usuario ha sido desactivada correctamente."})
        except Usuario.DoesNotExist:
            return JsonResponse({"success": False, "message": "Usuario no encontrado."}, status=404)

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)


# Vista de funciones crud de usuarios inactivos
@never_cache
@login_required_custom
def usuarios_inactivos(request):
    """
    Vista para listar usuarios inactivos del sistema.

     - Esta vista obtiene todos los usuarios que están inactivos y renderiza la plantilla 'lista_inactivos.html' con los datos obtenidos.
    """
    usuarios = Usuario.objects(is_active=False)
    return render(request, 'systemsigo/Usuarios/lista_inactivos.html', {
        'usuarios': usuarios
    })

@never_cache
@login_required_custom
def reactivar_usuario(request, usuario_id):
    """
    Vista para reactivar un usuario inactivo.

     - Esta vista busca un usuario por su ID y, si lo encuentra, lo reactiva estableciendo su estado a activo y limpiando la fecha de baja.
     - Si el usuario es reactivado exitosamente, redirige a la lista de usuarios inactivos con un mensaje de éxito.
     - Si el usuario no es encontrado, muestra un mensaje de error.
    """

    usuario = Usuario.objects(id=usuario_id).first()
    if usuario:
        usuario.is_active = True
        usuario.fecha_baja = None
        usuario.save()
        messages.success(request, f"El usuario {usuario.nombre_completo} ha sido reactivado.")
    else:
        messages.error(request, "Usuario no encontrado.")
    return redirect('usuarios_inactivos')  # o donde sea que se muestren

@never_cache
@login_required_custom
def eliminar_permanente(request, usuario_id):
    """
    Vista para eliminar permanentemente un usuario inactivo.
        - Esta vista busca un usuario por su ID y, si lo encuentra, lo elimina permanentemente de la base de datos.
        - Si el usuario es eliminado exitosamente, redirige a la lista de usuarios inactivos con un mensaje de éxito.
        - Si el usuario no es encontrado, muestra un mensaje de error.
    """

    usuario = Usuario.objects(id=usuario_id).first()
    if usuario:
        usuario.delete()
        messages.success(request, "Usuario eliminado permanentemente.")
    else:
        messages.error(request, "Usuario no encontrado.")
    return redirect('usuarios_inactivos')