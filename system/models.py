from datetime import datetime, timedelta
import secrets
import bcrypt
from mongoengine import (
    Document, StringField, EmailField, BooleanField, DateTimeField,
    ReferenceField, IntField, DecimalField, DictField,
    FileField, ObjectIdField
)
from mongoengine import DENY, ValidationError
from datetime import date

######################################################################################
######################################################################################
######################################################################################

# ==================== MODELOS DE GESTIÓN ENERGÉTICA ====================

class Campus(Document):
    nomenclatura = StringField(required=True)
    ubicacion = StringField()
    metros_cuadrados = DecimalField(precision=2, force_string=True)
    fecha_registro = DateTimeField(default=datetime.now)

    meta = {
        'indexes': ['nomenclatura']
    }

    def __str__(self):
        return self.nomenclatura

class UnidadResponsable(Document):
    nombre = StringField(required=True)
    total_personas = IntField()
    campus = ReferenceField(Campus, reverse_delete_rule=DENY)
    diagrama_unifilar = FileField(required=True)#Implementación en futura actualización

    meta = {
        'indexes': ['nombre', 'campus']
    }

class Usuario(Document):
    matricula = StringField(unique=True, required=False, default=None)
    nombres = StringField(required=True)
    apellidos = StringField(required=True)
    email = EmailField(required=True, unique=True)
    telefono = StringField(max_length=20, required=False, default=None)
    unidad_responsable = ReferenceField(UnidadResponsable, required=False, default=None, reverse_delete_rule=DENY)
    rol = StringField(required=True, choices=('admin', 'admin_energia', 'admin_ambiental', 'admin_salud',
                                              'rector', 'director', 'encargado_ur', 'capturista', 'auditor'))
    is_active = BooleanField(default=True)
    fecha_alta = DateTimeField(default=datetime.now)
    fecha_baja = DateTimeField(required=False, default=None)
    password = StringField(required=True)
    creado_por = ReferenceField('Usuario', required=False, default=None, reverse_delete_rule=DENY) # Autorreferencia
    foto_perfil = StringField()

    meta = {
        'collection': 'usuarios',
        'ordering': ['-fecha_alta'],
        'indexes': ['email', 'unidad_responsable', 'rol']
    }

    def deactivate(self):
        self.is_active = False
        self.fecha_baja = datetime.now()
        self.save()
    
    @classmethod
    def hash_password(cls, plain):
        return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def generate_password(self):
        random_password = secrets.token_urlsafe(10)
        self.password = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.save()
        # Aquí se puede agregar lógica de envío de correo
        return random_password

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.email})"
    
    @property
    def es_admin(self):
        return self.rol in ['admin', 'admin_ambiental', 'admin_energia', 'admin_salud']
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    intentos_fallidos = IntField(default=0)
    bloqueado_hasta = DateTimeField(required=False, default=None)

    def esta_bloqueado(self):
        if self.bloqueado_hasta:
            return datetime.now() < self.bloqueado_hasta
        return False

    def registrar_fallo_login(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 3:
            self.bloqueado_hasta = datetime.now() + timedelta(hours=2)
            self.save()
            from .views import enviar_correo_bloqueo  # importa la función donde esté
            enviar_correo_bloqueo(self)
        else:
            self.save()

    def resetear_intentos(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save()

class PasswordResetCode(Document):
    usuario = ReferenceField(Usuario, required=True)
    codigo = StringField(required=True)
    creado_en = DateTimeField(default=datetime.utcnow)
    expiracion = DateTimeField(default=lambda: datetime.utcnow() + timedelta(minutes=15))
    usado = BooleanField(default=False)

    meta = {'collection': 'password_reset_codes'}

class Edificio(Document):
    nombre = StringField(required=True)
    responsable_alta = StringField()
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    fecha_registro = DateTimeField(default=datetime.now)

    meta = {
        'indexes': ['nombre', 'unidad_responsable']
    }

class Area(Document):
    nombre = StringField(required=True)
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    edificio = ReferenceField(Edificio)
    fecha_registro = DateTimeField(default=datetime.now)
    responsable = StringField()
    telefono = StringField()
    cargo = StringField()
    grado_estudio = StringField()

    meta = {
        'indexes': ['nombre', 'unidad_responsable']
    }

class Subestacion(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    no_servicio = IntField()
    no_medidor = StringField()
    tarifa = StringField(required=True)
    multiplicador = DecimalField(precision=2, force_string=True)

    meta = {
        'indexes': ['unidad_responsable']
    }

NIVELES = (
    "1", "2", "3", "4",
    "Planta baja", "Planta alta", "Sin planta"
)

class PeriodoInventario(Document):
    nombre = StringField(required=True, unique=True)  # Asegura que no se repita el nombre
    fecha_inicio = DateTimeField(required=True)
    fecha_fin = DateTimeField(required=True)
    status = StringField(choices=["Activo", "Pendiente", "Finalizado"], default="Activo")
    observaciones = StringField()
    persona_autoriza = StringField()
    rol = StringField()
    activo = BooleanField(default=True)

    meta = {
        'indexes': [
            'fecha_inicio', 
            'fecha_fin',
            {'fields': ['fecha_inicio', 'fecha_fin'], 'unique': False}
        ]
    }

    def clean(self):
        super().clean()

        # Validar que la fecha de inicio sea menor a la de fin
        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError("La fecha de inicio no puede ser mayor o igual a la fecha de fin.")

        # Validar solapamientos (solo si es nuevo o se modificó)
        query = PeriodoInventario.objects(
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        )
        if self.pk:  # Si se está editando, excluirse a sí mismo
            query = query.filter(id__ne=self.pk)

        if query:
            raise ValidationError("El periodo de inventario se solapa con otro existente.")
        
    @property
    def status_actual(self):
        """
        Devuelve el estado actual del periodo en función de las fechas.
        - 'Pendiente' si aún no comienza.
        - 'Activo' si está dentro del rango.
        - 'Finalizado' si ya terminó.
        """
        hoy = date.today()
        fecha_inicio = self.fecha_inicio.date() if hasattr(self.fecha_inicio, 'date') else self.fecha_inicio
        fecha_fin = self.fecha_fin.date() if hasattr(self.fecha_fin, 'date') else self.fecha_fin

        if hoy < fecha_inicio:
            return "Pendiente"
        elif fecha_inicio <= hoy <= fecha_fin:
            return "Activo"
        else:
            return "Finalizado"

class HistorialInventario(Document):
    periodo = ReferenceField(PeriodoInventario, reverse_delete_rule=DENY)
    inventario_id = ObjectIdField(required=True)
    tipo = StringField(choices=["Climatización", "Luminarias", "Misceláneos"], required=True)
    datos = DictField()
    fecha_registro = DateTimeField(default=datetime.utcnow)

class InventarioClimatizacion(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    edificio = ReferenceField(Edificio, reverse_delete_rule=DENY)
    nivel = StringField(choices=NIVELES)
    area = ReferenceField(Area, reverse_delete_rule=DENY)
    tipo_clima = StringField()
    marca = StringField()
    modelo = StringField()
    capacidad = IntField()
    voltaje = DecimalField(precision=2, force_string=True)
    amperaje = DecimalField(precision=2, force_string=True)
    potencia = DecimalField(precision=2, force_string=True)
    potencia_total = DecimalField(precision=5, force_string=True)
    horas_mes = DecimalField(precision=2, force_string=True)
    consumo_mensual = DecimalField(precision=2, force_string=True)
    fecha_registro = DateTimeField(default=datetime.now)
    periodo = ReferenceField(PeriodoInventario, reverse_delete_rule=DENY)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    ultima_actualizacion = DateTimeField()
    activo = BooleanField(default=True) 
    fecha_baja = DateTimeField(null=True)
    fecha_reactivacion = DateTimeField(null=True)
    dado_baja_por = ReferenceField(Usuario, required=False, null=True)
    reactivado_por = ReferenceField(Usuario, required=False, null=True)

class InventarioLuminarias(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    edificio = ReferenceField(Edificio, reverse_delete_rule=DENY)
    nivel = StringField(choices=NIVELES)
    area = ReferenceField(Area, reverse_delete_rule=DENY)
    tipo_lampara = StringField()
    num_luminarias = IntField()
    lamp_luminarias = IntField()
    potencia_lamp = DecimalField(precision=2, force_string=True)
    potencia_total_lum = DecimalField(precision=5, force_string=True)
    consumo_mensual_horas = IntField()
    consumo_mensual = DecimalField(precision=2, force_string=True)
    fecha_registro = DateTimeField(default=datetime.now)
    periodo = ReferenceField(PeriodoInventario, reverse_delete_rule=DENY)
    creado_por = ReferenceField(Usuario, required=False, default=None)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    activo = BooleanField(default=True) 
    fecha_baja = DateTimeField(null=True)
    fecha_reactivacion = DateTimeField(null=True)
    dado_baja_por = ReferenceField(Usuario, required=False, null=True)
    reactivado_por = ReferenceField(Usuario, required=False, null=True)

class InventarioMiscelaneos(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    edificio = ReferenceField(Edificio, reverse_delete_rule=DENY)
    nivel = StringField(choices=NIVELES)
    area = ReferenceField(Area, reverse_delete_rule=DENY)
    marca = StringField()
    miscelaneos = StringField()
    modelo = StringField()
    voltaje = DecimalField(precision=2, force_string=True)
    amperaje = DecimalField(precision=2, force_string=True)
    potencia = DecimalField(precision=2, force_string=True)
    potencia_total = DecimalField(precision=5, force_string=True)
    horas_mes = DecimalField(precision=2, force_string=True)
    consumo_mensual = DecimalField(precision=2, force_string=True)
    fecha_registro = DateTimeField(default=datetime.now)
    periodo = ReferenceField(PeriodoInventario, reverse_delete_rule=DENY)
    creado_por = ReferenceField(Usuario, required=False, default=None)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    activo = BooleanField(default=True)  
    fecha_baja = DateTimeField(null=True)
    fecha_reactivacion = DateTimeField(null=True)
    dado_baja_por = ReferenceField(Usuario, required=False, null=True)
    reactivado_por = ReferenceField(Usuario, required=False, null=True)

class Tarifas(Document):
    nombre = StringField(required=True, max_length=255)
    descripcion = StringField(required=True, max_length=500)
    tarifa = DecimalField(required=True, force_string=True)

    def __str__(self):
        return f"{self.nombre} - {self.tarifa}"

class FacturaEnergeticaTriple(Document):
    tipo_tarifa = StringField(choices=["GDMTH", "GDMTO", "GDBT"])
    subestacion = ReferenceField(Subestacion, reverse_delete_rule=DENY)
    dias_periodo = IntField() 
    periodo = StringField()
    consumo = DecimalField(precision=2, force_string=True)
    demanda_maxima = IntField()
    factor_potencia = DecimalField(precision=2, force_string=True)
    factor_carga = IntField()
    cargo_energia = DecimalField(precision=2, force_string=True)
    importe_demanda_maxima = DecimalField(precision=2, force_string=True)
    importe_bt = DecimalField(precision=2, force_string=True)
    importe_fp = DecimalField(precision=2, force_string=True)
    dap = DecimalField(precision=2, force_string=True)
    iva = DecimalField(precision=2, force_string=True)
    total_a_pagar = DecimalField(precision=2, force_string=True)
    archivo_pdf = FileField(required=True)
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    fecha_vencimiento = DateTimeField()
    status = StringField(choices=["Pagada", "No pagada"], default="No pagada")
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()

    meta = {
        'indexes': ['subestacion', 'status', 'tipo_tarifa', 'creado_por']
    }

class FacturaPdbt(Document):
    tipo_tarifa = StringField(choices=["PDBT"], default="PDBT")
    subestacion = ReferenceField(Subestacion, reverse_delete_rule=DENY)
    dias_periodo = IntField() 
    periodo = StringField()
    consumo = DecimalField(precision=2, force_string=True)
    cargo_energia = DecimalField(precision=2, force_string=True)
    importe_demanda_maxima = DecimalField(precision=2, force_string=True)
    dap = DecimalField(precision=2, force_string=True)
    iva = DecimalField(precision=2)
    total_a_pagar = DecimalField(precision=2)
    archivo_pdf = FileField(required=True)
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    status = StringField(choices=["Pagada", "No pagada"], default="Pagada")
    fecha_vencimiento = DateTimeField()
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()

    meta = {
        'indexes': ['subestacion', 'status', 'tipo_tarifa', 'creado_por']
    }

class Medidores(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    no_medidor = StringField()
    capacidad_transformador = DecimalField(precision=2, force_string=True)
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True)

    meta = {
        'indexes': [
            # Índice no único para consultas rápidas por unidad_responsable
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }


######################################################################################
######################################################################################
######################################################################################

# ==================== MODELOS DE GESTIÓN AMBIENTAL ====================

class BitacoraMensual(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    laboratorio = StringField()
    tipo_residuo = StringField()
    cantidad = DecimalField(precision=2, force_string=True)
    estado_fisico = StringField()
    creti = StringField()
    tipo_envase = StringField() 
    capacidad_medida = StringField()
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True)

    meta = {
        'indexes': [
            # Índice no único para consultas rápidas por unidad_responsable
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }

class AlmacenamientoTemporal(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    centro_acopio = StringField()
    tipo_residuo = StringField()
    cantidad = DecimalField(precision=2, force_string=True)
    estado_fisico = StringField()
    creti = StringField()
    tipo_envase = StringField() 
    capacidad_medida = StringField()
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True)

    meta = {
        'indexes': [
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }

class BitacoraGeneracionRPBI(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    area_dependencia = StringField()
    cultivos_cepas = StringField()
    punzocortantes = StringField()
    patologicos = StringField()
    no_anatomicos = StringField()
    sangre = StringField()
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None) 
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True)

    meta = {
        'indexes': [
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }

class BitacoraRecoleccionRPBI(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    area_dependencia = StringField()
    cultivos_cepas = StringField()
    punzocortantes = StringField()
    patologicos = StringField()
    no_anatomicos = StringField()
    sangre = StringField()
    bolsas_rojas = IntField()
    bolsas_amarillas = IntField()
    contenedores_punzocortantes = IntField()
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None) 
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True)

    meta = {
        'indexes': [
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }

class CentroAcopioRME(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    centro_acopio = StringField()
    tipo_residuo = StringField()
    cantidad = DecimalField(precision=2, force_string=True)
    estado_fisico = StringField()
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True)

    meta = {
        'indexes': [
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }

class VertederoMunicipal(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    dependencia = StringField()
    tipo_desecho = StringField()
    capacidad = DecimalField(precision=2, force_string=True)
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True) 

    meta = {
        'indexes': [
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }

class CentroAcopioRRR(Document):
    unidad_responsable = ReferenceField(UnidadResponsable, reverse_delete_rule=DENY)
    centro_acopio = StringField()
    dependencia = StringField()
    pet = StringField()
    papel = StringField()
    carton = StringField()
    metales = StringField()
    fecha_registro = DateTimeField(default=datetime.now)
    creado_por = ReferenceField(Usuario, required=False, default=None, reverse_delete_rule=DENY)
    actualizado_por = ReferenceField(Usuario, required=False, default=None)
    ultima_actualizacion = DateTimeField()
    status = BooleanField(default=True) 

    meta = {
        'indexes': [
            {'fields': ['unidad_responsable'], 'unique': False}
        ]
    }