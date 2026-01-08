from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
import requests
from .models import * 
from django.http import HttpResponse, JsonResponse
import secrets
from django.core.mail import send_mail
import time
from .decorators import login_required_custom
from django.views.decorators.cache import never_cache
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST

# ================================================ VISTAS DE FUNCIONES LOGIN =====================================================
# Vista principal de inicio de sesión
def Login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        usuario = Usuario.objects(email=email).first()

        if usuario and usuario.is_active and usuario.check_password(password):
            # Crear sesión
            request.session['user_id'] = str(usuario.id)
            request.session['rol'] = usuario.rol
            request.session['email'] = usuario.email
            request.session['nombres'] = usuario.nombres
            request.session['apellidos'] = usuario.apellidos

            if usuario.unidad_responsable:
                request.session['unidad_responsable_id'] = str(usuario.unidad_responsable.id)
                request.session['unidad_responsable_nombre'] = usuario.unidad_responsable.nombre
            else:
                request.session['unidad_responsable_id'] = None
                request.session['unidad_responsable_nombre'] = None

            # Redirección según rol
            destino = {
                'admin': 'inicio',
                'admin_energia': 'admin_energia_inicio',
                'admin_ambiental': 'admin_ambiental_inicio',
                'capturista': 'capturista',
                'encargado_ur': 'encargado_ur',
                'rector': 'rector',
                'director': 'director',
                'auditor': 'auditor'
            }.get(usuario.rol, 'inicio')

            return render(request, 'systemsigo/login.html', {
                'login_success': True,
                'redirect_url': destino
            })

        # Si no coincide correo o contraseña
        return render(request, 'systemsigo/login.html', {
            'error': 'Correo o contraseña incorrectos.'
        })

    # Si es GET, solo muestra el formulario
    return render(request, 'systemsigo/login.html')

def enviar_correo_bloqueo(usuario):
    asunto = "Cuenta suspendida temporalmente"
    mensaje = f"""
Hola {usuario.nombres},

Hemos detectado 3 intentos fallidos consecutivos al intentar acceder a tu cuenta asociada al correo {usuario.email}.

Por seguridad, tu cuenta ha sido suspendida temporalmente por 2 horas. 

Si no fuiste tú, por favor contacta con el administrador del sistema.

Atentamente,
Equipo de Soporte de SIG-Online
"""
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=False,
    )

def logout_view(request):
    # Elimina completamente la sesión
    request.session.flush()

    # Opcional: elimina otras cookies si fuera necesario
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


# Vistas para restauración de contraseñas modulo interno
@never_cache
@login_required_custom
def SolicitarCambioPassword(request):
    if request.method == 'POST':
        actual = request.POST.get('actual')
        usuario = Usuario.objects(id=request.session.get('user_id')).first()

        if not usuario or not usuario.check_password(actual):
            messages.error(request, 'Contraseña actual incorrecta.')
            return redirect('cambiar_password')

        # Generar código de verificación
        codigo = secrets.token_urlsafe(6)
        PasswordResetCode(
            usuario=usuario,
            codigo=codigo
        ).save()

        # Enviar código por correo
        send_mail(
            'Código para cambio de contraseña - Sistema SIGO',
            f'Hola {usuario.nombres},\n\nTu código para cambiar la contraseña es: {codigo}\nEste código es válido por 15 minutos.',
            'al066230@uacam.mx',
            [usuario.email],
            fail_silently=False
        )

        messages.success(request, 'Se ha enviado un código a tu correo. Ingresa el código para continuar.')
        return redirect('confirmar_cambio_password')

    return render(request, 'systemsigo/Resets_passwords/Interno/solicitar_cambio.html')

@never_cache
@login_required_custom
def ConfirmarCambioPassword(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        nueva = request.POST.get('nueva')
        confirmar = request.POST.get('confirmar')

        usuario = Usuario.objects(id=request.session.get('user_id')).first()

        codigo_db = PasswordResetCode.objects(
            usuario=usuario,
            codigo=codigo_ingresado,
            usado=False,
            expiracion__gte=datetime.utcnow()
        ).first()

        if not codigo_db:
            messages.error(request, 'Código inválido o expirado.')
            return redirect('confirmar_cambio_password')

        if nueva != confirmar:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('confirmar_cambio_password')

        usuario.password = Usuario.hash_password(nueva)
        usuario.save()

        codigo_db.usado = True
        codigo_db.save()

        messages.success(request, 'Contraseña actualizada con éxito.')
        return redirect('cambiar_password')  # Redirige donde prefieras

    return render(request, 'systemsigo/Resets_passwords/Interno/confirmar_cambio.html')


# Vistas para restauración de contraseñas modulo externo
def SolicitarRecuperacionPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        usuario = Usuario.objects(email=email).first()
        if not usuario:
            messages.error(request, 'El correo no está registrado en el sistema.')
            return redirect('solicitar_recuperacion')

        # Eliminar códigos anteriores (opcional pero recomendable)
        PasswordResetCode.objects(usuario=usuario, usado=False).delete()

        # Generar código de 6 dígitos
        codigo = str(secrets.randbelow(1000000)).zfill(6)
        expiracion = datetime.now() + timedelta(minutes=10)

        reset_code = PasswordResetCode(
            usuario=usuario,
            codigo=codigo,
            expiracion=expiracion
        )
        reset_code.save()

        # Enviar correo
        send_mail(
            'Código para recuperar tu contraseña - SIGO',
            f'Hola {usuario.nombre_completo},\n\nTu código de recuperación es: {codigo}\nEste código expirará en 10 minutos.',
            'al066230@uacam.mx',  # EMAIL_HOST_USER
            [usuario.email],
            fail_silently=False,
        )

        request.session['reset_user_id'] = str(usuario.id)  # Guardamos para el siguiente paso
        messages.success(request, 'Se ha enviado un código a tu correo.')
        return redirect('verificar_codigo')

    return render(request, 'systemsigo/Resets_passwords/Externo/solicitar_recuperacion.html')

def VerificarCodigoResetPassword(request):
    usuario_id = request.session.get('reset_user_id')
    if not usuario_id:
        messages.error(request, 'Sesión inválida. Solicita el código nuevamente.')
        return redirect('solicitar_recuperacion')

    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        usuario = Usuario.objects(id=usuario_id).first()

        if not usuario:
            messages.error(request, 'Usuario no válido.')
            return redirect('solicitar_recuperacion')

        codigo_valido = PasswordResetCode.objects(
            usuario=usuario,
            codigo=codigo,
            expiracion__gte=datetime.now(),
            usado=False
        ).first()

        if not codigo_valido:
            messages.error(request, 'Código inválido o expirado.')
            return redirect('verificar_codigo')

        # Marcar como usado
        codigo_valido.usado = True
        codigo_valido.save()

        request.session['codigo_verificado'] = True  # bandera para el siguiente paso
        return redirect('cambiar_password')

    return render(request, 'systemsigo/Resets_passwords/Externo/verificar_codigo.html')

def CambiarPasswordReset(request):
    usuario_id = request.session.get('reset_user_id')
    codigo_verificado = request.session.get('codigo_verificado', False)

    if not usuario_id or not codigo_verificado:
        messages.error(request, 'Sesión inválida. Inicia de nuevo el proceso.')
        return redirect('solicitar_recuperacion')

    usuario = Usuario.objects(id=usuario_id).first()
    if not usuario:
        messages.error(request, 'Usuario no válido.')
        return redirect('solicitar_recuperacion')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('cambiar_password')

        if len(password1) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return redirect('cambiar_password')

        usuario.password = Usuario.hash_password(password1)
        usuario.save()

        # Limpiar la sesión
        request.session.flush()

        messages.success(request, 'Contraseña actualizada con éxito.')
        return redirect('login')  # O el nombre de tu vista de login

    return render(request, 'systemsigo/Resets_passwords/Externo/cambiar_contrasena.html')


# Función para obtener el usuario actual desde la sesión
def get_user(request):
    user_id = request.session.get('user_id')
    return Usuario.objects(id=user_id).first()


# ================================ VISTAS DE PERFIL DE USUARIO =====================================================

# Vista de perfil de usuarios
@never_cache
@login_required_custom
def perfil_usuario(request):
    usuario = get_user(request)  # O donde tengas almacenado el usuario logueado
    subestaciones = Subestacion.objects(unidad_responsable=usuario.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)
    return render(request, 'systemsigo/Perfil/perfil.html', 
                  {'usuario': usuario,'MEDIA_URL': settings.MEDIA_URL, 'subestaciones': subestaciones,
                  'tarifas_disponibles': tarifas_disponibles})

@never_cache
@login_required_custom
def cambiar_foto_perfil(request):
    usuario = get_user(request)

    if request.method == 'POST' and 'foto' in request.FILES:
        imagen = request.FILES['foto']
        nombre_archivo = f'perfil/{usuario.id}_{imagen.name}'
        ruta_guardada = default_storage.save(nombre_archivo, ContentFile(imagen.read()))
        usuario.foto_perfil = ruta_guardada
        usuario.save()
        messages.success(request, 'Foto de perfil actualizada correctamente.')
        return redirect('perfil_usuario')

    return render(request, 'systemsigo/Perfil/cambiar_foto.html', {
        'usuario': usuario,
        'MEDIA_URL': settings.MEDIA_URL
    })


# ================================ VISTAS DE ERRORES =====================================================
def error_404_view(request, exception):
    return render(request, 'Errores/error_404.html', status=404)

def error_408_view(request, exception):
    return render(request, 'Errores/error_408.html', status=408)

def error_500_view(request):
    return render(request, 'Errores/error_500.html', status=500)

def error_503_view(request):
    return render(request, 'Errores/error_503.html')

def error_504_view(request, exception):
    return render(request, 'Errores/error_504.html', status=504)