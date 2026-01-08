from django import forms
from .models import Campus, UnidadResponsable, Usuario
from mongoengine.errors import ValidationError
from captcha.fields import CaptchaField

class TarifasForm(forms.Form):
    nombre = forms.CharField(max_length=255, required=True)
    descripcion = forms.CharField(widget=forms.Textarea, max_length=500, required=True)
    tarifa = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

class CampusForm(forms.Form):
    nomenclatura = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': ''}))
    ubicacion = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': ''}))
    metros_cuadrados = forms.DecimalField(required=True, widget=forms.NumberInput(attrs={'class': ''}))

class UnidadResponsableForm(forms.Form):
    nombre = forms.CharField(max_length=200)

    campus = forms.ChoiceField(choices=[])

    total_personas = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(UnidadResponsableForm, self).__init__(*args, **kwargs)
        self.fields['campus'].choices = [
            (str(c.id), f"{c.nomenclatura} - {c.ubicacion}") for c in Campus.objects.all()
        ]

class UsuarioForm(forms.Form):
    matricula = forms.CharField(max_length=100, required=False)
    nombres = forms.CharField(max_length=100, required=True)
    apellidos = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    telefono = forms.CharField( # Cambie la linea de codigo aquí para que el campo telefono acepte solo numeros
    max_length=20,
    required=False,
    widget=forms.TextInput(attrs={
        'type': 'number', 
        'placeholder': 'Ingrese su teléfono',
        'pattern': '[0-9+ ]*',  
        'inputmode': 'numeric', 
    })
)
    unidad_responsable = forms.ChoiceField(choices=[], required=False)
    rol = forms.ChoiceField(choices=[
        ('admin', 'Administrador'),
        ('admin_energia', 'Administrador Energía'),
        ('admin_ambiental', 'Administrador Ambiental'),
        #('admin_salud', 'Administrador Salud'),
        #('rector', 'Rector'),
        #('director', 'Director'),
        ('encargado_ur', 'Responsable de Unidad'),
        ('capturista', 'Capturista'),
        #('auditor', 'Auditor'),
    ])
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        # Se carga el listado de unidades responsables
        self.fields['unidad_responsable'].choices = [
            (str(ur.id), ur.nombre) for ur in UnidadResponsable.objects.all()
        ]

class FotoPerfilForm(forms.Form):
    foto = forms.ImageField(
        label="Selecciona una nueva foto de perfil",
        widget=forms.ClearableFileInput(attrs={
            'class': 'material-input',
            'accept': 'image/*'
        })
    )