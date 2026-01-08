from django.shortcuts import render
from django.views.decorators.cache import never_cache

from system.decorators import login_required_custom

@never_cache
@login_required_custom
def Inicio_director (request):
    return render(request, 'systemsigo/index_direc.html') # Solo renderiza la vista(Frontend) sin pasarle contexto adicional