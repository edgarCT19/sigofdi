from django.shortcuts import render
from django.views.decorators.cache import never_cache

from system.decorators import login_required_custom

# Vista de inicio para el rector
@never_cache
@login_required_custom
def Inicio_rector (request):
    return render(request, 'systemsigo/index_rect.html') # Renderiza la plantilla de inicio para el rector